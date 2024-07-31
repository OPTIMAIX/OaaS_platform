from fastapi import APIRouter, Path, Body
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate

import oaasplatform.crud.instances as crud
import oaasplatform.nocrud.direct_execution as direct_execution
from oaasplatform.schemas.status import Status
from oaasplatform.schemas.instances import InstanceInSchema as InSchema
from oaasplatform.schemas.instances import InstanceOutSchema as OutSchema
from oaasplatform.schemas.instances import InstanceUpdate

router = APIRouter(tags=["Instance Management module"])

@router.get("/instances",
            response_model=Page[OutSchema])
async def get_instances() -> Page[OutSchema]:
    queryset = crud.get_instances()
    paginated_query = await paginate(queryset)
    
    items = [OutSchema.from_orm(item) for item in paginated_query.items]
    paginated_query.items = items
    return paginated_query


@router.post("/instances",
             response_model=OutSchema)
async def create_instance(instance: InSchema) -> OutSchema:
    return await crud.create_instance(instance=instance)


@router.delete("/instances",
               response_model=Status)
async def stop_all_instances() -> Status:
    return await crud.stop_instances()


@router.get("/instances/{instanceId}",
            response_model=OutSchema)
async def get_instance(instanceId: int = Path(..., description="Unique identifier for a repository instance")) -> OutSchema:
    return await crud.get_instance(instanceId=instanceId)


@router.put("/instances/{instanceId}",
            response_model=OutSchema)
async def update_instance(instance: InstanceUpdate,
                          instanceId: int = Path(..., description="Unique identifier for a repository instance")) -> OutSchema:
    return await crud.update_instance(instanceId=instanceId, instance=instance)


@router.post("/instances/{instanceId}/start",
                response_model=Status)
async def start_instance(instanceId: int = Path(..., description="Unique identifier for a repository instance")) -> Status:
    return await crud.start_instance(instanceId=instanceId)

@router.delete("/instances/{instanceId}/stop",
                response_model=Status)
async def stop_instance(instanceId: int = Path(..., description="Unique identifier for a repository instance")) -> Status:
    return await crud.stop_instance(instanceId=instanceId)

@router.delete("/instances/{instanceId}/delete",
                response_model=Status)
async def delete_instance(instanceId: int = Path(..., description="Unique identifier for a repository instance")) -> Status:
    return await crud.delete_instance(instanceId=instanceId)

@router.get("/instances/{instanceId}/execute/{endpoint:path}")
async def execute_direct_get(instanceId: int = Path(..., description="Unique identifier for a repository instance"),
                             endpoint: str = Path(description="The API endpoint to execute")):
    return await direct_execution.direct_execution_get(instanceId=instanceId, endpoint=endpoint)

@router.post("/instances/{instanceId}/execute/{endpoint:path}")
async def execute_direct_post(instanceId: int = Path(..., description="Unique identifier for a repository instance"),
                              endpoint: str = Path(description="The API endpoint to execute"),
                              body = Body(..., description="The request body")):
    return await direct_execution.direct_execution_post(instanceId=instanceId, endpoint=endpoint, body=body)
