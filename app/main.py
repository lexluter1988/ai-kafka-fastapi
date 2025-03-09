from __future__ import annotations

import asyncio

from fastapi import FastAPI

from app.agent.demon import consume_responses
from app.agent.llm_worker_generic import llm_worker_generic
from app.auth.db import create_db_and_tables
from app.auth.logic import auth_backend, fastapi_users
from app.auth.schemas import UserCreate, UserRead, UserUpdate
from app.logger import setup_logging
from app.openai.views import openai_router
from app.settings import get_settings
from app.test_app.views import test_app_router

settings = get_settings()


async def start_demons():
    # asyncio.create_task(llm_worker())
    asyncio.create_task(llm_worker_generic())
    # asyncio.create_task(kafka_listener(active_connections=active_connections))
    asyncio.create_task(consume_responses())


def get_application() -> FastAPI:
    setup_logging(settings=settings)

    app = FastAPI(
        debug=settings.debug,
        version=settings.app_version or '0.1.0',
        title='Starter FastApi with FastApi users',
    )

    app.include_router(
        fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=['auth']
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix='/auth',
        tags=['auth'],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix='/auth',
        tags=['auth'],
    )
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix='/auth',
        tags=['auth'],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix='/users',
        tags=['users'],
    )
    app.include_router(test_app_router)
    app.include_router(openai_router)

    app.add_event_handler('startup', create_db_and_tables)
    app.add_event_handler('startup', start_demons)

    return app


application = get_application()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(application, host='0.0.0.0', port=8000)
