from fastapi import APIRouter, Path

from oaasplatform.main import logger
from oaasplatform.nocrud import callback

router = APIRouter(tags=["Internal Callback"])

@router.post("/callback/{executionId}")
async def get_info_callback(content: dict,
                            executionId: int = Path(..., description="Unique identifier for an execution")):
    logger.debug(f"Callback received for execution {executionId}")
    logger.debug(f"Callback content: {content}")
    return await callback.process_callback(executionId=executionId, content=content)