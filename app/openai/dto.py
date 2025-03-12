from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ModelData(BaseModel):
    id: str = Field(description='Имя модели', default='')
    object: str = Field(description='Тип объекта', default='model')


class Model(BaseModel):
    data: list[ModelData] = Field(description='Описание модели')


class CompletionRequest(BaseModel):
    model: str = Field(description='Имя модели', default='Qwen/Qwen2.5-72B-Instruct-AWQ')
    prompt: str = Field(description='Текстовый запрос', default='Как дела?')
    max_tokens: int = Field(description='Максимальное количество токенов', default=50)
    stream: bool = Field(description='Потоковый ли ответ', default=False)


class ChatCompletionResponseUsage(BaseModel):
    prompt_tokens: int
    total_tokens: int
    completion_tokens: int
    prompt_tokens_details: dict | None = Field(default=dict())


class CompletionResponseChoices(BaseModel):
    index: int
    text: str = Field(description='Сообщение от ассистента')
    logprobs: str | None
    finish_reason: str | None = Field(description='Причина завершения')
    stop_reason: Optional[str] = Field(description='Причина остановки', default=None)


class CompletionResponse(BaseModel):
    id: str = Field(description='Идентификатор объекта')
    object: str = Field(description='Тип объекта', default='text_completion')
    created: int = Field(description='Дата генерации')
    model: str = Field(description='Модель')
    choices: list[CompletionResponseChoices] = Field(description='Список вариантов ответа')
    usage: ChatCompletionResponseUsage | None = Field(description='Детали использования токенов')


class ChatCompletionRequestMessage(BaseModel):
    role: str = Field(description='Роль user или system', default='user')
    content: str = Field(description='Текст сообщения', default='Как дела?')


class ChatCompletionRequest(BaseModel):
    model: str = Field(description='Имя модели', default='Qwen/Qwen2.5-72B-Instruct-AWQ')
    messages: list[ChatCompletionRequestMessage] = Field(description='Сообщения для модели')
    temperature: float = Field(description='Температура модели', default=0.7)
    stream: bool = Field(description='Потоковый ли ответ', default=False)


class ChatCompletionResponseMessage(BaseModel):
    role: Optional[str] = Field(description='Роль', default=None)
    refusal: Optional[str] = Field(default=None)
    reasoning_content: dict | None = Field(default=dict())
    content: str = Field(description='Текст ответа')
    tool_calls: list[str] | None


class ChatCompletionResponseChoices(BaseModel):
    index: int
    delta: Optional[ChatCompletionResponseMessage] = Field(
        description='Часть сообщения при потоке', default=None
    )
    message: Optional[ChatCompletionResponseMessage] = Field(
        description='Сообщение от ассистента', default=None
    )
    logprobs: str | None
    finish_reason: Optional[str] = Field(description='Причина завершения', default='stop')


class ChatCompletionResponse(BaseModel):
    id: str = Field(description='Идентификатор объекта ответа в чат')
    object: str = Field(description='Тип объекта', default='chat.completion')
    created: int = Field(description='Дата генерации')
    model: str = Field(description='Модель', default='Qwen/Qwen2.5-72B-Instruct-AWQ')
    choices: list[ChatCompletionResponseChoices] = Field(description='Список вариантов ответа')
    usage: ChatCompletionResponseUsage | None = Field(description='Детали использования токенов')
    prompt_logprobs: dict | None = Field(default=dict())
