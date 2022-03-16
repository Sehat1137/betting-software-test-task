import asyncio

import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI

from config import Config
from src.storage_service import StorageService
from src.container import Container
from src.views import get_api_router


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    ev_loop = asyncio.get_event_loop()
    yield ev_loop
    ev_loop.close()


@pytest.fixture(scope="function")
def config() -> Config:
    config = Config()
    config.redis_db = 1
    return config


@pytest.fixture(scope="function", autouse=True)
def container(config: Config) -> Container:
    container = Container()
    container.config.from_pydantic(config)
    container.init_resources()
    container.wire(modules=["src.views", ])
    yield container
    container.unwire()


@pytest.fixture(scope="function", autouse=True)
async def storage_service(config: Config, container: Container) -> StorageService:
    connection = await container.redis_connection()
    storage_service = StorageService(connection)
    all_keys: list[str] = await connection.keys()
    if all_keys:
        await connection.delete(*all_keys)
    with container.storage_service.override(storage_service):
        yield storage_service
    all_keys: list[str] = await connection.keys()
    if all_keys:
        await connection.delete(*all_keys)


@pytest.fixture(scope='session')
def app() -> FastAPI:
    application = FastAPI()
    application.include_router(get_api_router())
    return application


@pytest.fixture(scope="session")
async def client(app: FastAPI) -> TestClient:
    async with TestClient(app, headers={"Content-Type": "application/json"}) as client:
        yield client
