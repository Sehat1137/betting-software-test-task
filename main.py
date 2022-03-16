from fastapi import FastAPI

from config import Config
from src.container import Container
from src.views import get_api_router


def get_app() -> FastAPI:
    container = Container()
    container.config.from_pydantic(Config())
    container.wire(modules=["src.views"])
    container.init_resources()
    app = FastAPI()
    app.include_router(get_api_router())
    return app
