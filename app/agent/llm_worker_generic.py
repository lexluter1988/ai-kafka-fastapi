from openai import OpenAI

from app.logger import logger
from app.openai.dto import ChatCompletionRequest
from app.settings import get_settings
from app.utils.consumers import KafkaTransportConsumer
from app.utils.producers import KafkaTransportProducer

settings = get_settings()


async def llm_worker_generic():
    client = OpenAI(api_key=settings.openai_token, base_url=settings.openai_host)

    consumer = KafkaTransportConsumer(
        event_class=ChatCompletionRequest,
        topic='chat_requests_generic',
    )
    await consumer.connect()
    logger.info('LLM request Kafka Generic Consumer Connected')

    producer = KafkaTransportProducer(topic='chat_responses_generic')

    await producer.connect()
    logger.info('LLM response Kafka Generic Producer Connected')
    try:
        async for msg, headers in consumer.consume():
            request = ChatCompletionRequest.parse_obj(msg)
            logger.info('dbg got message for LLM', request)
            response = client.chat.completions.create(**request.dict())
            logger.info('dbg, got response from LLM ', response)
            await producer.send(event_name='llm_response', event=response, headers=headers)

    finally:
        await consumer.close()
        await producer.close()
