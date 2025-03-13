# OpenAI compatible FastAPI server with Kafka

This is FastAPI application with LLM worked daemon running separately.

Services are communicating via Kafka messaging bus.


## Author

Author: Alexey Suponin <lexxsmith@gmail.com>

## Version

0.1.0

## License

License: MIT

## Quick start

```
python3.10 -m venv venv
source venv/bin/activate
pip install pip-tools
make deps

mv .env.example .env
```

Now write your base url, token, model into `.env`

#### Run full stack

Run `docker-compose up -d --build`


#### Local development

If you want to run FastAPI locally, comment the `main` service in `docker-compose.yml`

Run `docker-compose up -d --build`
Start dev server `uvicorn --host 0.0.0.0 --port 8000 --reload app.main:application`

## Kafka

UI is accessible on http://127.0.0.1:8080/


## SwaggerUI

Visit the http://127.0.0.1:8000/docs

You can call `/completions` and `/chat/completions` with sync or stream method.

## OpenAI compatibility

With running FastAPI server, you can set openai client and test it like ChatGPT

```python
from openai import OpenAI, AsyncOpenAI

base_url = 'http://127.0.0.1:8000/v1'

client = OpenAI(api_key='token', base_url=base_url)
async_client = AsyncOpenAI(api_key='token', base_url=base_url)

def test():
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

test()
```

There are more example in [test.py](test.py)
