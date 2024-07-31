from fastapi import APIRouter, Path
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate

import oaasplatform.crud.executions as crud
from oaasplatform.schemas.status import Status
from oaasplatform.schemas.executions import InExecutionSchema
from oaasplatform.schemas.executions import ExecutionsOutSchema as OutSchema

router = APIRouter(tags=["Execution Management module"])

@router.get("/executions",
            response_model=Page[OutSchema])
async def get_executions() -> Page[OutSchema]:
    queryset = crud.get_executions()
    paginated_query = await paginate(queryset)
    
    items = [OutSchema.from_orm(item) for item in paginated_query.items]
    paginated_query.items = items
    return paginated_query


@router.post("/executions",
             response_model=OutSchema)
async def create_executions(execution: InExecutionSchema) -> OutSchema:
    return await crud.create_execution(execution=execution)


@router.get("/executions/{executionId}",
            response_model=OutSchema)
async def get_execution(executionId: int = Path(..., description="Unique identifier for an execution")) -> OutSchema:
    return await crud.get_execution(executionId=executionId)


@router.put("/resourceExecutions/{executionId}",
            response_model=OutSchema)
async def update_input_parameters(execution: dict,
                                  executionId: int = Path(..., description="Unique identifier for an execution")) -> OutSchema:
    return await crud.update_input_parameters(executionId=executionId, execution=execution)                               


@router.post("/executions/{executionId}")
async def launch_execution(executionId: int = Path(..., description="Unique identifier for an execution")):
    return await crud.launch_execution(executionId=executionId) 


@router.delete("/resourceExecutions/{executionId}/stop",
               response_model=Status)
async def stop_execution(executionId: int = Path(..., description="Unique identifier for an execution")) -> Status:
    return Status(message="Method not implemented")

@router.delete("/resourceExecutions/{executionId}/delete",
               response_model=Status)
async def delete_execution(executionId: int = Path(..., description="Unique identifier for an execution")) -> Status:
    return await crud.delete_execution(executionId=executionId)