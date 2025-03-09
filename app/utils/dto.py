from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel


class GenericEvent(BaseModel):
    """Общий обработчик для неизвестных событий."""

    data: Dict[str, Any]


class ChatResponseEvent(BaseModel):
    chat_id: str
    response: str


class ChatRequestEvent(BaseModel):
    chat_id: str
    user_message: str
