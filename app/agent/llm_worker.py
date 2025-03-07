from openai import AsyncOpenAI

from app.settings import get_settings
from app.utils.consumers import KafkaTransportConsumer
from app.utils.dto import ChatRequestEvent, ChatResponseEvent
from app.utils.producers import KafkaTransportProducer

settings = get_settings()


async def llm_worker():
    client = AsyncOpenAI(api_key=settings.openai_token, base_url=settings.openai_host)

    consumer = KafkaTransportConsumer(
        event_class=ChatRequestEvent,
        topic='chat_requests',
    )
    await consumer.connect()
    print('LLM request Kafka Consumer Connected')

    producer = KafkaTransportProducer(topic='chat_responses')

    await producer.connect()
    print('LLM response Kafka Producer Connected')
    try:
        async for msg in consumer.consume():
            chat_id = msg.chat_id
            user_message = msg.user_message
            stream = await client.chat.completions.create(
                model=settings.openai_model_name,
                messages=[{'role': 'user', 'content': user_message}],
                stream=True,
            )

            async for chunk in stream:
                text = chunk.choices[0].delta.content or ''.strip()
                await producer.send(
                    event_name='llm_response',
                    event=ChatResponseEvent(chat_id=chat_id, response=text),
                )

    finally:
        await consumer.close()
        await producer.close()
