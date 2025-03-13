import asyncio

from openai import AsyncOpenAI, OpenAI

from app.logger import logger
from app.openai.dto import ChatCompletionRequest, CompletionRequest
from app.settings import get_settings
from app.utils.consumers import KafkaTransportConsumer
from app.utils.producers import KafkaTransportProducer

settings = get_settings()


async def llm_worker_generic():
    client = OpenAI(api_key=settings.openai_token, base_url=settings.openai_host)
    async_client = AsyncOpenAI(api_key=settings.openai_token, base_url=settings.openai_host)

    consumer = KafkaTransportConsumer(
        topic='chat_requests_generic',
    )
    await consumer.connect()
    logger.info('LLM request Kafka Generic Consumer Connected')

    producer = KafkaTransportProducer(topic='chat_responses_generic')

    await producer.connect()
    logger.info('LLM response Kafka Generic Producer Connected')

    handlers = {
        'chat.completions.request': handle_chat_completion,
        'completions.request': handle_completion,
    }

    try:
        async for msg, headers in consumer.consume():
            event_type = headers.get('event_type')
            logger.info(f'Received {event_type} request {msg}')

            handler = handlers.get(event_type)
            if handler:
                await handler(client, async_client, producer, msg, headers)
            else:
                raise ValueError(f'Unknown event type: {event_type}')

    finally:
        await producer.close()
        await consumer.close()


async def handle_chat_completion(
    client: OpenAI,
    async_client: AsyncOpenAI,
    producer: KafkaTransportProducer,
    msg: dict,
    headers: dict,
):
    request = ChatCompletionRequest.parse_obj(msg)
    if request.stream:
        await chat_completions_streaming(
            client=async_client, producer=producer, request=request, headers=headers
        )
    else:
        try:
            response = client.chat.completions.create(**request.dict())
        except Exception as e:
            logger.error(f'Chat completion request exception {e}')
            return
        logger.info(f'Received response for chat.completions.request {response}')
        headers['event_type'] = 'chat.completions.response'
        await producer.send(event=response, headers=headers)


async def handle_completion(
    client: OpenAI,
    async_client: AsyncOpenAI,
    producer: KafkaTransportProducer,
    msg: dict,
    headers: dict,
):
    request = CompletionRequest.parse_obj(msg)
    if request.stream:
        await completions_streaming(
            client=async_client, producer=producer, request=request, headers=headers
        )
    else:
        try:
            response = client.completions.create(**request.dict())
        except Exception as e:
            logger.error(f'Completion request exception {e}')
            return
        logger.info(f'Received response for completions.request {response}')
        headers['event_type'] = 'completions.response'
        await producer.send(event=response, headers=headers)


async def chat_completions_streaming(
    *,
    client: AsyncOpenAI,
    producer: KafkaTransportProducer,
    request: ChatCompletionRequest,
    headers,
):
    try:
        stream = await client.chat.completions.create(**request.dict())
    except Exception as e:
        logger.error(f'Chat completion streaming request exception {e}')
        return
    headers['event_type'] = 'chat.completions.response'
    async for chunk in stream:
        await producer.send(event=chunk, headers=headers)


async def completions_streaming(
    *, client: AsyncOpenAI, producer: KafkaTransportProducer, request: CompletionRequest, headers
):
    try:
        stream = await client.completions.create(**request.dict())
    except Exception as e:
        logger.error(f'Completion streaming request exception {e}')
        return
    headers['event_type'] = 'completions.response'
    async for chunk in stream:
        await producer.send(event=chunk, headers=headers)


if __name__ == '__main__':
    asyncio.run(llm_worker_generic())
