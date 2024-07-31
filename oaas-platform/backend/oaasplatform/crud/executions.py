from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
import requests

from oaasplatform.main import logger
from oaasplatform.config import settings
from oaasplatform.utils import algorithm_repository_wrapper as alg_repo
from oaasplatform.utils.docker import get_IP_container
from oaasplatform.schemas.status import Status
from oaasplatform.schemas.executions import ExecutionsOutSchema as OutSchema
from oaasplatform.schemas.executions import ExecutionsDatabaseSchema as DbSchema
from oaasplatform.schemas.instances import InstanceOutSchema
from oaasplatform.schemas.descriptors import ResourceDescriptorOutSchema
from oaasplatform.database.models import Executions, ResourceDescriptors, Instances, ExecutionType

def get_executions():
    return Executions.all().prefetch_related("instance", "resource", "instance__image")

async def get_execution(executionId):
    return await OutSchema.from_queryset_single(Executions.get(executionId=executionId))

async def create_execution(execution):
    # Validate that all id's exists
    try:
        resource_descriptor = await ResourceDescriptorOutSchema.from_queryset_single(ResourceDescriptors.get(resourceId=execution.resource_id))
        instance = await InstanceOutSchema.from_queryset_single(Instances.get(instanceId=execution.instance_id))
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Some of given IDs doesn't  exists."
        )

    if resource_descriptor.execution_type == ExecutionType.DIRECT:
        raise HTTPException(
            status_code=422,
            detail=f"Direct executions are not allowed. Access to the running instance and execute it directly. Port: {instance.docker['port']}"
        )

    try:
        execution_obj = await Executions.create(input_parameters=execution.input_parameters,
                                                         instance_id=execution.instance_id,
                                                         resource_id=execution.resource_id,)
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Sorry, that execution already exists"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=422,
            detail=f"Sorry, integrity error"
        )

    return await OutSchema.from_tortoise_orm(execution_obj)

async def launch_execution(executionId):
    try:
        execution = Executions.get(executionId=executionId)
        db_exec = await DbSchema.from_queryset_single(execution)
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Algorithm execution {executionId} not found."
        )

    # Call API
    try:
        if not settings.NETWORK_MODE_HOST:
            container_ip = get_IP_container(container_id=db_exec.instance.docker['backend_id'],
                                            network_id=db_exec.instance.docker['network_id'])
            container_port = settings.INTERNAL_PORT
        else:   # network_mode: host, broken on windows
            container_ip = "127.0.0.1"
            container_port = db_exec.instance.docker["port"]    
        
        output = alg_repo.launch_execution(executionId=db_exec.executionId,
                                            ip=container_ip,    
                                            port=container_port,
                                            local_algorithm_id=db_exec.resource.localId,
                                            input_parameters=db_exec.input_parameters)
    except requests.ConnectionError:
        raise HTTPException(
            status_code=422,
            detail=f"Unable to connect with instance {db_exec.instance.id}. Is it running?"
        )
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Connected with instance but an error ocurred."
        )
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(
            status_code=422,
            detail=f"Unable to launch execution."
        )

    # Update status entry
    await execution.update(status="0")      # Mark as queued

    return output

async def update_input_parameters(executionId: int, execution: dict) -> OutSchema:
    try:
        exec = Executions.get(executionId=executionId)
        db_exec = await DbSchema.from_queryset_single(exec)
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Algorithm execution {executionId} not found."
        )

    logger.info(f"Updating input parameters of execution {executionId} with: {execution}")
    await exec.update(input_parameters=execution)
    
    return await OutSchema.from_queryset_single(Executions.get(executionId=executionId))

async def delete_execution(executionId) -> Status:
    try:
        db_exec = await OutSchema.from_queryset_single(Executions.get(executionId=executionId))
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Algorithm execution {executionId} not found."
        )

    deleted_exec = await Executions.filter(executionId=executionId).delete()
    if not deleted_exec:
        raise HTTPException(
            status_code=422,
            detail=f"Algorithm execution {executionId} not found."
        )
    return Status(message=f"Deleted algorithm execution {executionId}")
