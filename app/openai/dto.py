from __future__ import annotations

from pydantic import BaseModel, Field


class ModelData(BaseModel):
    id: str = Field(description='Имя модели', default='')
    object: str = Field(description='Тип объекта', default='model')


class Model(BaseModel):
    data: list[ModelData] = Field(description='Описание модели')


class CompletionRequest(BaseModel):
    model: str = Field(description='Имя модели', default='')
    prompt: str = Field(description='Текстовый запрос', default='')
    max_tokens: int = Field(description='Максимальное количество токенов', default=50)
    stream: bool = Field(description='Потоковый ли ответ', default=False)


class CompletionResponseChoices(BaseModel):
    index: int
    text: str = Field(description='Сообщение от ассистента')
    logprobs: str | None
    finish_reason: str | None = Field(description='Причина завершения')
    stop_reason: str | None = Field(description='Причина остановки')


class CompletionResponse(BaseModel):
    id: str = Field(description='Идентификатор объекта')
    object: str = Field(description='Тип объекта', default='text_completion')
    created: int = Field(description='Дата генерации')
    model: str = Field(description='Модель', default='Qwen/Qwen2.5-72B-Instruct-AWQ')
    choices: list[CompletionResponseChoices] = Field(description='Список вариантов ответа')
    usage: ChatCompletionResponseUsage | None = Field(description='Детали использования токенов')


class ChatCompletionRequestMessage(BaseModel):
    role: str = Field(description='Роль user или system', default='user')
    content: str = Field(description='Текст сообщения')


class ChatCompletionRequest(BaseModel):
    model: str = Field(description='Имя модели', default='')
    messages: list[ChatCompletionRequestMessage] = Field(description='Сообщения для модели')
    temperature: float = Field(description='Температура модели', default=0.7)
    stream: bool = Field(description='Потоковый ли ответ', default=False)


class ChatCompletionResponseMessage(BaseModel):
    role: str = Field(description='Роль', default='assistant')
    reasoning_content: str | None = Field()
    content: str = Field(description='Текст ответа')
    tool_calls: list[str] | None


class ChatCompletionResponseChoices(BaseModel):
    index: int
    message: ChatCompletionResponseMessage = Field(description='Сообщение от ассистента')
    logprobs: str | None
    finish_reason: str = Field(description='Причина завершения', default='stop')


class ChatCompletionResponseUsage(BaseModel):
    prompt_tokens: int
    total_tokens: int
    completion_tokens: int
    prompt_tokens_details: str | None


class ChatCompletionResponse(BaseModel):
    id: str = Field(description='Идентификатор объекта ответа в чат')
    object: str = Field(description='Тип объекта', default='chat.completion')
    created: int = Field(description='Дата генерации')
    model: str = Field(description='Модель', default='Qwen/Qwen2.5-72B-Instruct-AWQ')
    choices: list[ChatCompletionResponseChoices] = Field(description='Список вариантов ответа')
    usage: ChatCompletionResponseUsage | None = Field(description='Детали использования токенов')
    prompt_logprobs: str | None
