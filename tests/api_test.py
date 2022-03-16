import json

import pytest
from async_asgi_testclient import TestClient
from src.storage_service import StorageService


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "body",
    [
        {"a": 1},
        {"b": "2"},
        {"a": 1, "b": True},
    ]
)
async def test_add_body(storage_service: StorageService, client: TestClient, body: dict):
    for attempt in range(3):
        response = await client.post("/api/add", json=body)
        key = response.json()["key"]
        assert json.loads(await storage_service._connection.get(key)) == {"duplicates": attempt, "body": body}
        assert response.status_code == 201


@pytest.mark.parametrize(
    "body",
    [
        {"body": {"b": "2"}, "duplicates": 0},
        {"body": {"a": 1}, "duplicates": 0},
        {"body": {"a": 1, "b": True}, "duplicates": 0},
    ]
)
async def test_get_body(storage_service: StorageService, client: TestClient, body: dict):
    key = storage_service._get_key_by_body(body)
    await storage_service._connection.set(key, json.dumps(body))
    response = await client.get(f"/api/get?key={key}")
    assert response.status_code == 200
    assert response.json() == body


@pytest.mark.parametrize(
    "body",
    [
        {"body": {"b": "2"}, "duplicates": 0},
        {"body": {"a": 1}, "duplicates": 0},
        {"body": {"a": 1, "b": True}, "duplicates": 0},
    ]
)
async def test_delete_body(storage_service: StorageService, client: TestClient, body: dict):
    key = storage_service._get_key_by_body(body)
    await storage_service._connection.set(key, json.dumps(body))
    response = await client.delete(f"/api/remove", json={"key": key})
    assert response.status_code == 204
    assert await storage_service._connection.get(key) is None


@pytest.mark.parametrize(
    "body",
    [
        {"body": {"b": "2"}, "duplicates": 2},
        {"body": {"a": 1}, "duplicates": 1},
        {"body": {"a": 1, "b": True}, "duplicates": 0},
    ]
)
async def test_update_body(storage_service: StorageService, client: TestClient, body: dict):
    key = storage_service._get_key_by_body(body)
    await storage_service._connection.set(key, json.dumps(body))
    new_body = {"c": "qwe", "body": body["body"]}
    response = await client.put(f"/api/update", json={"key": key, "body": new_body})
    assert response.status_code == 200
    assert await storage_service._connection.get(key) is None
    key = response.json()["key"]
    assert json.loads(await storage_service._connection.get(key)) == {"body": new_body, "duplicates": 0}


@pytest.mark.parametrize(
    "body, stats",
    [
        ({"body": {"b": "2"}, "duplicates": 0}, 0),
        ({"body": {"b": "2"}, "duplicates": 4}, 80.0),
        ({"body": {"b": "2"}, "duplicates": 9}, 90.0),
    ]
)
async def test_get_stats(storage_service: StorageService, client: TestClient, body: dict, stats: str):
    key = storage_service._get_key_by_body(body)
    await storage_service._connection.set(key, json.dumps(body))
    response = await client.get(f"/api/statistic")
    assert response.status_code == 200
    assert response.json()["duplicates"] == stats
