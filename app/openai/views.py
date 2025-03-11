import asyncio
import uuid

from fastapi import APIRouter

from app.logger import logger
from app.openai.dto import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    CompletionRequest,
    CompletionResponse,
    Model,
    ModelData,
)
from app.settings import get_settings
from app.state import response_futures
from app.utils.producers import KafkaTransportProducer

openai_router = APIRouter(prefix='/v1')

settings = get_settings()


@openai_router.get('/models')
async def get_models() -> Model:
    return Model(data=[ModelData(id=settings.openai_model_name)])


@openai_router.post('/completions')
async def completions(request: CompletionRequest) -> CompletionResponse:
    producer = KafkaTransportProducer(topic='chat_requests_generic')
    logger.info('LLM request Kafka Generic Producer Connected')
    await producer.connect()

    correlation_id = str(uuid.uuid4())
    headers = {'correlation_id': correlation_id, 'event_type': 'completions.request'}

    loop = asyncio.get_event_loop()
    future = loop.create_future()
    response_futures[correlation_id] = future

    await producer.send(event=request, headers=headers)

    try:
        response = await asyncio.wait_for(future, timeout=10)
        return CompletionResponse.parse_obj(response)
    except asyncio.TimeoutError:
        raise


@openai_router.post('/chat/completions')
async def chat_completions(request: ChatCompletionRequest) -> ChatCompletionResponse:
    producer = KafkaTransportProducer(topic='chat_requests_generic')
    logger.info('LLM request Kafka Generic Producer Connected')
    await producer.connect()

    correlation_id = str(uuid.uuid4())
    headers = {'correlation_id': correlation_id, 'event_type': 'chat.completions.request'}

    loop = asyncio.get_event_loop()
    future = loop.create_future()
    response_futures[correlation_id] = future

    await producer.send(event=request, headers=headers)

    try:
        response = await asyncio.wait_for(future, timeout=10)
        return ChatCompletionResponse.parse_obj(response)
    except asyncio.TimeoutError:
        raise
