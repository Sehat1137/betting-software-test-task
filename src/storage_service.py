import base64
from typing import Optional, AsyncIterator

import aioredis

from src.dto.storage import BodyEntry


class StorageService:

    @staticmethod
    async def create_redis_connection(host: str, port: int, db: int) -> AsyncIterator[aioredis.Redis]:
        connection: aioredis.Redis = aioredis.from_url(f"redis://{host}:{port}/{db}", decode_responses=True)
        yield connection
        await connection.close()

    def __init__(self, connection: aioredis.Redis) -> None:
        self._connection: aioredis.Redis = connection

    async def add(self, body: dict) -> str:
        key = self._get_key_by_body(body)
        entry = await self._get_entry_or_none(key)
        if not entry:
            await self._connection.set(key, BodyEntry(body=body, duplicates=0).json())
        else:
            entry.duplicates += 1
            await self._connection.set(key, entry.json())
        return key

    async def get(self, key: str) -> Optional[BodyEntry]:
        return await self._get_entry_or_none(key)

    async def remove(self, key: str) -> None:
        await self._connection.delete(key)

    async def update(self, key: str, body: dict):
        await self.remove(key)
        return await self.add(body)

    async def get_statistic(self) -> float:
        all_keys: list[str] = await self._connection.keys()
        all_values: list[str] = await self._connection.mget(all_keys)
        total_value: int = len(all_values)
        for entry in all_values:
            total_value += BodyEntry.parse_raw(entry).duplicates
        return (total_value - len(all_values)) / (total_value / 100)

    async def _get_entry_or_none(self, key: str) -> Optional[BodyEntry]:
        result: Optional[str] = await self._connection.get(key)
        if result is None:
            return None
        return BodyEntry.parse_raw(result)

    def _get_key_by_body(self, body: dict):
        raw_key: bytes = "".join(map("{0[0]}{0[1]}".format, body.items())).encode()
        return base64.b64encode(raw_key).decode()
