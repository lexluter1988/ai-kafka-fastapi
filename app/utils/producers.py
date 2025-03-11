from __future__ import annotations

import json

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from app.logger import logger
from app.settings import get_kafka_settings

settings = get_kafka_settings()


class KafkaTransportProducer:
    def __init__(self, topic: str):
        self.topic = topic
        self.producer = None

    @staticmethod
    def get_headers(headers: dict | None = None):
        return [(key, value.encode('utf-8')) for key, value in headers.items()] if headers else []

    async def connect(self):
        try:
            self.producer = AIOKafkaProducer(**settings.dict(exclude={'group_id'}))
            await self.producer.start()
        except Exception as e:
            logger.error(f'Failed to connect to Kafka: {e}')
            raise

    async def send(self, event: BaseModel, headers: dict | None = None):
        if not self.producer:
            raise RuntimeError('Producer is not connected')
        try:
            message = json.dumps(event.dict()).encode('utf-8')
            headers = self.get_headers(headers=headers)
            await self.producer.send_and_wait(self.topic, value=message, headers=headers)
        except Exception as e:
            logger.error(f'Failed to send message: {e}')
            raise

    async def close(self):
        if self.producer:
            await self.producer.stop()
