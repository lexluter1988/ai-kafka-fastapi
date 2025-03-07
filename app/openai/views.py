from fastapi import APIRouter

from app.openai.dto import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    CompletionRequest,
    CompletionResponse,
    Model,
    ModelData,
)
from app.openai.examples import (
    OPENAI_COMPLETION_RESPONSE_EXAMPLE,
)
from app.settings import get_settings
from app.utils.consumers import KafkaTransportConsumer
from app.utils.producers import KafkaTransportProducer

openai_router = APIRouter(prefix='/v1')

settings = get_settings()


@openai_router.get('/models')
async def get_models() -> Model:
    return Model(data=[ModelData(id=settings.openai_model_name)])


@openai_router.post('/completions')
async def completions(request: CompletionRequest) -> CompletionResponse:
    return CompletionResponse.parse_obj(OPENAI_COMPLETION_RESPONSE_EXAMPLE)


@openai_router.post('/chat/completions')
async def chat_completions(request: ChatCompletionRequest) -> ChatCompletionResponse:
    producer = KafkaTransportProducer(
        topic='chat_requests_generic'
    )
    print('LLM request Kafka Generic Producer Connected')
    await producer.connect()

    consumer = KafkaTransportConsumer(
        event_class=ChatCompletionResponse,
        topic='chat_responses_generic',
    )

    await consumer.connect()
    print('LLM response Kafka Generic Consumer Connected')

    await producer.send(
        event_name='user_input', event=request
    )

    try:
        async for msg in consumer.consume():
            response = ChatCompletionResponse.parse_obj(msg)
            return response
    finally:
        await consumer.close()
        await producer.close()
