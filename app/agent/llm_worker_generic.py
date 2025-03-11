import asyncio

from openai import OpenAI

from app.logger import logger
from app.openai.dto import ChatCompletionRequest, CompletionRequest
from app.settings import get_settings
from app.utils.consumers import KafkaTransportConsumer
from app.utils.producers import KafkaTransportProducer

settings = get_settings()


async def llm_worker_generic():
    client = OpenAI(api_key=settings.openai_token, base_url=settings.openai_host)

    consumer = KafkaTransportConsumer(
        topic='chat_requests_generic',
    )
    await consumer.connect()
    logger.info('LLM request Kafka Generic Consumer Connected')

    producer = KafkaTransportProducer(topic='chat_responses_generic')

    await producer.connect()
    logger.info('LLM response Kafka Generic Producer Connected')
    try:
        async for msg, headers in consumer.consume():
            event_type = headers.get('event_type')
            logger.info(f'Received {event_type} request {msg}')
            if event_type == 'chat.completions.request':
                request = ChatCompletionRequest.parse_obj(msg)
                response = client.chat.completions.create(**request.dict())
                logger.info(f'Received response for {event_type} request {response}')
                headers['event_type'] = 'chat.completions.response'
            elif event_type == 'completions.request':
                request = CompletionRequest.parse_obj(msg)
                response = client.completions.create(**request.dict())
                logger.info(f'Received response for {event_type} request {response}')
                headers['event_type'] = 'completions.response'
            else:
                raise
            await producer.send(event=response, headers=headers)

    finally:
        await producer.close()
        await consumer.close()


if __name__ == '__main__':
    asyncio.run(llm_worker_generic())
