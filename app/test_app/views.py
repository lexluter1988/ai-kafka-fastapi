from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect
from starlette.responses import HTMLResponse

from app.logger import logger
from app.openai.dto import ChatCompletionRequest
from app.settings import get_settings
from app.state import active_connections
from app.utils.producers import KafkaTransportProducer

test_app_router = APIRouter(prefix='/test-app')

settings = get_settings()


@test_app_router.get('/', response_class=HTMLResponse)
async def serve_html():
    with open('frontend.html', 'r', encoding='utf-8') as f:
        return f.read()


@test_app_router.websocket('/ws/chat/{chat_id}')
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    await websocket.accept()
    active_connections[chat_id] = websocket
    producer = KafkaTransportProducer(topic='chat_requests_generic')

    await producer.connect()
    logger.info('LLM request Kafka Producer Connected')
    try:
        while True:
            data = await websocket.receive_text()
            await producer.send(
                event=ChatCompletionRequest(
                    model=settings.openai_model_name,
                    messages=[{'role': 'user', 'content': data}],
                    stream=True,
                ),
                headers={'event_type': 'chat.completions.request', 'correlation_id': chat_id},
            )

    except WebSocketDisconnect:
        del active_connections[chat_id]
    finally:
        await producer.close()
