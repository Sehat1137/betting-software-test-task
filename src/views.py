from dependency_injector.wiring import Provide, inject
from fastapi import Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRouter

from src.container import Container
from src.dto.requests import AddBodyParams, GetBodyParams, RemoveKeyParams, UpdateBodyParams
from src.dto.responses import AddBodyResponse, UpdateBodyResponse, GetStatsResponse, GetBodyResponse
from src.storage_service import StorageService


@inject
async def add_body(
        params: AddBodyParams,
        storage: StorageService = Depends(Provide[Container.storage_service])
) -> JSONResponse:
    key = await storage.add(params.__root__)
    return JSONResponse(AddBodyResponse(key=key).dict(), status_code=status.HTTP_201_CREATED)


@inject
async def get_body_by_key(
        params: GetBodyParams = Depends(),
        storage: StorageService = Depends(Provide[Container.storage_service])
) -> JSONResponse:
    entry = await storage.get(params.key)
    if not entry:
        return JSONResponse(
            {"detail": f"body for key: {params.key} not found"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    return JSONResponse(entry.dict())


@inject
async def delete_body_by_key(
        params: RemoveKeyParams,
        storage: StorageService = Depends(Provide[Container.storage_service])
) -> Response:
    await storage.remove(params.key)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@inject
async def update_body_by_key(
        params: UpdateBodyParams,
        storage: StorageService = Depends(Provide[Container.storage_service])
) -> JSONResponse:
    key = await storage.update(params.key, params.body)
    return JSONResponse(UpdateBodyResponse(key=key).dict())


@inject
async def get_stats(storage: StorageService = Depends(Provide[Container.storage_service])) -> JSONResponse:
    return JSONResponse(GetStatsResponse(duplicates=await storage.get_statistic()).dict())


def get_api_router() -> APIRouter:
    router = APIRouter(prefix="/api")
    router.add_api_route(
        "/add", add_body, methods=["POST", ], response_model=AddBodyResponse, status_code=status.HTTP_201_CREATED
    )
    router.add_api_route("/get", get_body_by_key, methods=["GET", ], response_model=GetBodyResponse)
    router.add_api_route("/remove", delete_body_by_key, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT)
    router.add_api_route("/update", update_body_by_key, methods=["PUT", ], response_model=UpdateBodyResponse)
    router.add_api_route("/statistic", get_stats, methods=["GET", ], response_model=GetStatsResponse)
    return router
