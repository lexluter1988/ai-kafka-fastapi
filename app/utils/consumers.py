from __future__ import annotations

import json

from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_fixed

from app.logger import logger
from app.openai.dto import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    CompletionRequest,
    CompletionResponse,
)
from app.settings import get_kafka_settings

settings = get_kafka_settings()


class KafkaTransportConsumer:
    def __init__(self, topic: str):
        self.topic = topic
        self.consumer = AIOKafkaConsumer(
            self.topic, **settings.dict(), value_deserializer=lambda v: self.deserialize_message(v)
        )
        self.serializers_map = {
            'completions.request': CompletionRequest,
            'completions.response': CompletionResponse,
            'chat.completions.request': ChatCompletionRequest,
            'chat.completions.response': ChatCompletionResponse,
        }

    def deserialize_message(self, value: bytes):
        try:
            return json.loads(value)
        except (ValidationError, json.JSONDecodeError) as e:
            logger.error(f'Failed to deserialize message: {e}')
            return None

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(10))
    async def connect(self):
        try:
            await self.consumer.start()
        except Exception as e:
            logger.error(f'Failed to connect to Kafka: {e}')
            raise

    async def consume(self):
        if not self.consumer:
            raise RuntimeError('Consumer is not connected')
        try:
            async for msg in self.consumer:
                if msg.value:
                    headers = {key: value.decode() for key, value in msg.headers}
                    event_type = headers.get('event_type')

                    if not event_type:
                        logger.warning('Missing event_type in headers, skipping message.')
                        continue

                    serializer_class = self.serializers_map.get(event_type)
                    if not serializer_class:
                        logger.warning(f"Unknown event_type '{event_type}', skipping message.")
                        continue

                    try:
                        event = serializer_class(**msg.value)
                        yield event, headers
                    except ValidationError as e:
                        logger.error(f"Failed to deserialize event '{event_type}': {e}")

                    logger.info(
                        f'Received event: {msg.value} of type: {event_type} and headers: {headers}'
                    )
        except Exception as e:
            logger.error(f'Error consuming messages: {e}')
            raise

    async def close(self):
        if self.consumer:
            await self.consumer.stop()
