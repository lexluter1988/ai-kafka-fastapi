# fastwithkafka

FastAPI with fastapi-users
Plus with OpenAI integration via websockets and Kafka messaging bus

## Author

Author: Your Name

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

```
uvicorn --host 0.0.0.0 --port 8000 --reload app.main:application
```

Now visit the http://127.0.0.1:8000/test-app


## Kafka

UI is accessible on http://127.0.0.1:8080/
