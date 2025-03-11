from app.logger import logger
from app.state import response_futures
from app.utils.consumers import KafkaTransportConsumer


async def kafka_listener(active_connections: dict):
    consumer = KafkaTransportConsumer(
        topic='chat_responses_generic',
    )
    await consumer.connect()
    logger.info('LLM response Kafka Consumer Connected')

    try:
        async for msg, headers in consumer.consume():
            correlation_id = headers.get('correlation_id')
            if correlation_id in active_connections:
                websocket = active_connections[correlation_id]
                if msg and hasattr(msg, 'choices') and len(msg.choices) > 0:
                    response_text = msg.choices[0].delta.content or msg.choices[0].message.content
                    if response_text:
                        await websocket.send_text(response_text)
            else:
                logger.info(f'Received invalid message: {msg}')
    except Exception as e:
        logger.error(f'Error in chat consumer: {e}')
    finally:
        await consumer.close()


async def consume_responses():
    consumer = KafkaTransportConsumer(
        topic='chat_responses_generic',
    )
    await consumer.connect()
    try:
        async for msg, headers in consumer.consume():
            correlation_id = headers.get('correlation_id')

            if correlation_id in response_futures:
                future = response_futures.pop(correlation_id)
                future.set_result(msg)
    finally:
        await consumer.close()
