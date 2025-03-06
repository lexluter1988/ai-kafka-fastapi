from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect
from starlette.responses import HTMLResponse

from app.auth.db import User
from app.auth.logic import current_active_user
from app.utils.dto import ChatRequestEvent
from app.utils.producers import KafkaTransportProducer

test_app_router = APIRouter(prefix='/test-app')


@test_app_router.get('/welcome')
async def welcome(user: User = Depends(current_active_user)):  # noqa: B008
    return {f'Wilkomen {user.email}!'}


@test_app_router.get('/', response_class=HTMLResponse)
async def serve_html():
    with open('frontend.html', 'r', encoding='utf-8') as f:
        return f.read()


@test_app_router.websocket('/ws/chat/{chat_id}')
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    from app.main import get_active_connections

    active_connections = get_active_connections()

    await websocket.accept()
    active_connections[chat_id] = websocket
    producer = KafkaTransportProducer(topic='chat_requests')

    await producer.connect()
    try:
        while True:
            data = await websocket.receive_text()
            await producer.send(
                event_name='user_input', event=ChatRequestEvent(chat_id=chat_id, user_message=data)
            )

    except WebSocketDisconnect:
        del active_connections[chat_id]
    finally:
        await producer.close()
