from openai import AsyncOpenAI, OpenAI

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
    print('LLM request Kafka Generic Consumer Connected')

    producer = KafkaTransportProducer(
        topic='chat_responses_generic'
    )

    await producer.connect()
    print('LLM response Kafka Generic Producer Connected')
    try:
        async for msg in consumer.consume():
            request = ChatCompletionRequest.parse_obj(msg)
            print('dbg got message for LLM', request)
            response = client.chat.completions.create(
                **request.dict()
            )
            print('dbg, got response from LLM ', response)

            await producer.send(
                event_name='llm_response',
                event=response,
            )

    finally:
        await consumer.close()
        await producer.close()
