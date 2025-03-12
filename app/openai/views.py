import asyncio
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter
from starlette.responses import StreamingResponse

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

    if request.stream:
        return StreamingResponse(
            completions_stream_generator(correlation_id), media_type='text/event-stream'
        )
    try:
        response = await asyncio.wait_for(future, timeout=20)
        return CompletionResponse.parse_obj(response)
    except asyncio.TimeoutError:
        raise


@openai_router.post('/chat/completions')
async def chat_completions(request: ChatCompletionRequest) -> ChatCompletionResponse:
    producer = KafkaTransportProducer(topic='chat_requests_generic')
    logger.info('LLM request Kafka Generic Producer Connected')
    await producer.connect()

    correlation_id = str(uuid.uuid4())
    headers = {
        'correlation_id': correlation_id,
        'event_type': 'chat.completions.request',
    }

    loop = asyncio.get_event_loop()
    future = loop.create_future()
    response_futures[correlation_id] = future

    await producer.send(event=request, headers=headers)

    if request.stream:
        return StreamingResponse(
            chat_completions_stream_generator(correlation_id), media_type='text/event-stream'
        )

    try:
        response = await asyncio.wait_for(future, timeout=20)
        return ChatCompletionResponse.parse_obj(response)
    except asyncio.TimeoutError:
        raise


async def chat_completions_stream_generator(correlation_id: str) -> AsyncGenerator[str, None]:
    """
    Асинхронный генератор для передачи частичных ответов
    от chat.completions в FastAPI StreamingResponse
    """
    while True:
        if correlation_id not in response_futures:
            response_futures[correlation_id] = asyncio.Future()

        future = response_futures[correlation_id]

        try:
            chunk = await asyncio.wait_for(future, timeout=5)
            if chunk is None:
                break
            json_chunk = chunk.model_dump_json()
            yield f'data: {json_chunk}\n\n'  # for OpenAI compatibility

            response_futures[correlation_id] = asyncio.Future()
        except asyncio.TimeoutError:
            break
        except asyncio.CancelledError:
            logger.error(f'Streaming cancelled for {correlation_id}')


async def completions_stream_generator(correlation_id: str) -> AsyncGenerator[str, None]:
    """
    Асинхронный генератор для передачи частичных ответов
    от completions в FastAPI StreamingResponse
    """
    while True:
        if correlation_id not in response_futures:
            response_futures[correlation_id] = asyncio.Future()

        future = response_futures[correlation_id]

        try:
            chunk = await asyncio.wait_for(future, timeout=5)
            if chunk is None:
                break

            json_chunk = chunk.model_dump_json()
            yield f'data: {json_chunk}\n\n'  # for OpenAI compatibility

            response_futures[correlation_id] = asyncio.Future()
        except asyncio.TimeoutError:
            break
        except asyncio.CancelledError:
            logger.error(f'Streaming cancelled for {correlation_id}')
