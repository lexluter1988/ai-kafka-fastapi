from __future__ import annotations

import json
from typing import Type

from aiokafka import AIOKafkaConsumer
from pydantic import BaseModel, ValidationError

from app.settings import get_kafka_settings

settings = get_kafka_settings()


class KafkaTransportConsumer:
    def __init__(self, topic: str, event_class: Type[BaseModel]):
        self.topic = topic
        self.event_class = event_class
        self.consumer = AIOKafkaConsumer(
            self.topic, **settings.dict(), value_deserializer=lambda v: self.deserialize_message(v)
        )

    def deserialize_message(self, value: bytes):
        try:
            data = json.loads(value)
            return self.event_class(**data)
        except (ValidationError, json.JSONDecodeError) as e:
            print(f'Failed to deserialize message: {e}')
            return None  # Можно настроить обработку некорректных сообщений

    async def connect(self):
        try:
            await self.consumer.start()
        except Exception as e:
            print(f'Failed to connect to Kafka: {e}')
            raise

    async def consume(self):
        if not self.consumer:
            raise RuntimeError('Consumer is not connected')
        try:
            async for msg in self.consumer:
                if msg.value:
                    print(f'Received event: {msg.value}')
                    yield msg.value
        except Exception as e:
            print(f'Error consuming messages: {e}')
            raise

    async def close(self):
        if self.consumer:
            await self.consumer.stop()
