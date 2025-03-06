from __future__ import annotations

from pydantic import BaseModel


class ChatResponseEvent(BaseModel):
    chat_id: str
    response: str


class ChatRequestEvent(BaseModel):
    chat_id: str
    user_message: str
