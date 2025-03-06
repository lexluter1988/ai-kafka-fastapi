from app.utils.consumers import KafkaTransportConsumer
from app.utils.dto import ChatResponseEvent


async def kafka_listener(active_connections: dict):
    consumer = KafkaTransportConsumer(
        event_class=ChatResponseEvent,
        topic='chat_responses',
    )
    await consumer.connect()

    try:
        async for msg in consumer.consume():
            if msg and isinstance(msg, ChatResponseEvent):
                chat_id = msg.chat_id
                response_text = msg.response

                if chat_id in active_connections:
                    websocket = active_connections[chat_id]
                    await websocket.send_text(response_text)
            else:
                print(f'Received invalid message: {msg}')
    except Exception as e:
        print(f'Error in chat consumer: {e}')
    finally:
        await consumer.close()
