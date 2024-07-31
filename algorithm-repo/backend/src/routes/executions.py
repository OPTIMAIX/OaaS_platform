from fastapi import APIRouter, Path, Request, Body
from typing import Union

from src.schemas.executions import ExecutionsOut
from src.utils.executions_wrapper import read_execution, start_execution, stop_execution

router = APIRouter(tags=["Executions"])

@router.post("/executions/{algorithm_id}",
             response_model=ExecutionsOut)
async def launch_algorithm(request: Request,
                            input_parameter: dict,
                            callback_id: Union[int, None] = None,
                            algorithm_id: int = Path(None, description="Identifier for an algorithm"),
                           ) -> ExecutionsOut:
    return start_execution(algorithm_id=algorithm_id, 
                           input_parameters=input_parameter, 
                           callback_id=callback_id,
                           ip_client=request.client.host)

@router.get("/executions/{execution_id}",
            response_model=ExecutionsOut)
async def get_execution(execution_id: int = Path(None, description="Identifier for an execution")) -> ExecutionsOut:
    return read_execution(execution_id=execution_id)

@router.delete("/executions/{execution_id}",
               response_model=ExecutionsOut)
async def end_execution(execution_id: int = Path(None, description="Identifier for an execution")) -> ExecutionsOut:
    return stop_execution(execution_id=execution_id)