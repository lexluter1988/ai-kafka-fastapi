from app.logger import logger
from app.openai.dto import ChatCompletionResponse
from app.state import response_futures
from app.utils.consumers import KafkaTransportConsumer
from app.utils.dto import ChatResponseEvent


async def kafka_listener(active_connections: dict):
    consumer = KafkaTransportConsumer(
        event_class=ChatResponseEvent,
        topic='chat_responses',
    )
    await consumer.connect()
    logger.info('LLM response Kafka Consumer Connected')

    try:
        async for msg, headers in consumer.consume():
            if msg and isinstance(msg, ChatResponseEvent):
                chat_id = msg.chat_id
                response_text = msg.response

                if chat_id in active_connections:
                    websocket = active_connections[chat_id]
                    await websocket.send_text(response_text)
            else:
                logger.info(f'Received invalid message: {msg}')
    except Exception as e:
        logger.error(f'Error in chat consumer: {e}')
    finally:
        await consumer.close()


async def consume_responses():
    consumer = KafkaTransportConsumer(
        event_class=ChatCompletionResponse,
        topic='chat_responses_generic',
    )
    await consumer.connect()
    try:
        async for msg, headers in consumer.consume():
            logger.info('dbg got message for LLM', msg)
            correlation_id = headers.get('correlation_id')

            if correlation_id in response_futures:
                future = response_futures.pop(correlation_id)
                future.set_result(msg)
    finally:
        await consumer.close()
