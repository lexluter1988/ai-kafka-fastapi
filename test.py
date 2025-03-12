import asyncio

from openai import AsyncOpenAI, OpenAI

base_url = 'http://127.0.0.1:8000/v1'

client = OpenAI(api_key='token', base_url=base_url)
async_client = AsyncOpenAI(api_key='token', base_url=base_url)


def test_chat_completion__sync():
    chat_request = {
        'model': 'Qwen/Qwen2.5-72B-Instruct-AWQ',
        'messages': [
            {'role': 'system', 'content': 'Ты помощник.'},
            {'role': 'user', 'content': 'Привет, как дела?'},
        ],
        'temperature': 0.7,
        'stream': False,
    }
    response = client.chat.completions.create(**chat_request)
    print(response)


def test_completion__sync():
    completion_request = {
        'model': 'Qwen/Qwen2.5-72B-Instruct-AWQ',
        'prompt': '<|im_start|>user\nTell me a short story about AI.<|im_end|>\n<|im_start|>assistant\n',  # noqa: E501
        'max_tokens': 100,
        'stream': False,
    }
    response = client.completions.create(**completion_request)
    print(response)


async def test_chat_completion__async():
    chat_request = {
        'model': 'Qwen/Qwen2.5-72B-Instruct-AWQ',
        'messages': [
            {'role': 'system', 'content': 'Ты помощник.'},
            {'role': 'user', 'content': 'Привет, как дела?'},
        ],
        'temperature': 0.7,
        'stream': True,
    }

    stream = await async_client.chat.completions.create(**chat_request)
    async for chunk in stream:
        print(chunk)


async def test_completion__async():
    completion_request = {
        'model': 'Qwen/Qwen2.5-72B-Instruct-AWQ',
        'prompt': '<|im_start|>user\nTell me a short story about AI.<|im_end|>\n<|im_start|>assistant\n',  # noqa: E501
        'max_tokens': 100,
        'stream': True,
    }
    stream = await async_client.completions.create(**completion_request)
    async for chunk in stream:
        print(chunk)


asyncio.run(test_completion__async())
