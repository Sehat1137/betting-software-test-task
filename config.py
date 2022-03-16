from pydantic import BaseSettings


class Config(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db: int
