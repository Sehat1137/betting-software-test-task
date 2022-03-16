from typing import Union

import aioredis
from dependency_injector import containers, providers

from config import Config
from src.storage_service import StorageService


class Container(containers.DeclarativeContainer):

    config: Union[Config, providers.Configuration[Config]] = providers.Configuration()

    redis_connection: providers.Resource[aioredis.Redis] = providers.Resource(
        StorageService.create_redis_connection,
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
    )

    storage_service: providers.Resource[StorageService] = providers.Factory(
        StorageService,
        connection=redis_connection
    )
