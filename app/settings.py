from __future__ import annotations

import functools

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_prefix = ''

    app_version: str = '0.0.1'
    jwt_lifetime_seconds: int = 3600
    jwt_secret: str = 'SECRET'
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
    sasl_mechanism: str = ''
    sasl_plain_username: str = ''
    sasl_plain_password: str = ''


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()


@functools.lru_cache
def get_kafka_settings() -> KafkaSettings:
    return KafkaSettings()
