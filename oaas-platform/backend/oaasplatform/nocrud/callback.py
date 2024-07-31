from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist
from datetime import datetime, timezone

from oaasplatform.main import logger
from oaasplatform.config import settings
from oaasplatform.schemas.executions import ExecutionsDatabaseSchema as DbSchema
from oaasplatform.schemas.status import Status
from oaasplatform.database.models import Executions

async def process_callback(executionId: int, content: dict):
    try:
        execution = Executions.get(executionId=executionId)
        db_exec = await DbSchema.from_queryset_single(execution)
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Algorithm execution {executionId} not found."
        )
    
    # Change status to 1
    logger.debug(f"Updated status for execution {executionId}")
    await execution.update(status="1")

    # Update output
    logger.debug(f"Updated output for execution {executionId}")
    await execution.update(output_success=content)

    # Update end execution time
    logger.debug(f"Update execution end date {executionId}")
    await execution.update(executionEnd=datetime.now(settings.TZ))

    logger.debug(f"Sending OK to Algorithm Repository!")
    return Status(message="Sucesfully registered output execution")
