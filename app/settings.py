from __future__ import annotations

import functools

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_prefix = ''

    app_version: str = '0.0.1'
    jwt_lifetime_seconds: int = 525600
    jwt_secret: str = (
        '04b84d9b8b01a45fb05af4c6a97ec82e79a3e752a14325b471249b5cb696734bce1c2ad06ad9e0c054a2dc86'
        '020547ac1b20de63b0c163706ad6567a83837b9fcc2aba30421a11cce05459a86d6365ef74964ae1d54354ce'
        'c9dc4355e59557d700f6fea74174ad3cab8121693af64e2a7633d2f05795854fed2c22b354c80b4c2b45a744'
        'a6597904eb16fa51a76ba8572e68981181545ef49a43f6a6bade5371875fa4659405a0c422a83e633d60eb0b'
        'd8d52e8712b34b26f19fd5f98ca75174acace091433be21c225abdb9f0211fcec1c569bd69659ef2d2485d7b'
        '0a1cfb9b5ae3baac736794112225d2d63ef0780d012e1f6348e46499722a4451c62d13d4'
    )
    database_url: str = 'sqlite+aiosqlite:///./test_app.db'
    debug: bool = False
    log_level: str = 'DEBUG'
    log_format: str = 'json'
    openai_token: str = ''
    openai_host: str
    openai_model_name: str


class KafkaSettings(BaseSettings):
    class Config:
        env_file = '.kafka'
        env_file_encoding = 'utf-8'
        env_prefix = ''

    bootstrap_servers: str = 'localhost:9093'
    security_protocol: str = 'PLAINTEXT'
    group_id: str = None
    sasl_mechanism: str = ''
    sasl_plain_username: str = ''
    sasl_plain_password: str = ''


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()


@functools.lru_cache
def get_kafka_settings() -> KafkaSettings:
    return KafkaSettings()
