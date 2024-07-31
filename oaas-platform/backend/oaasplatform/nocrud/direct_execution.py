from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist
import requests

from oaasplatform.main import logger
from oaasplatform.schemas.instances import InstanceDatabaseSchema as DbSchema
from oaasplatform.database.models import Instances

async def direct_execution_get(instanceId: int, endpoint: str):
    logger.info(f"Executing endpoint {endpoint} on instance {instanceId}")
    
    try:
        db_instance = await DbSchema.from_queryset_single(Instances.get(instanceId=instanceId))
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Algorithm instance {instanceId} not found."
        )

    # Check if instance is running
    if db_instance.status != "running":
        raise HTTPException(
            status_code=422,
            detail=f"Algorithm instance {instanceId} is not running."
        )
        
    if endpoint == "/":
        endpoint = ""
        
    # Create base URL for instance
    instance_docker = db_instance.docker
    url = f"http://localhost:{instance_docker['port']}/{endpoint}"
    logger.info(f"URL for instance {instanceId}: {url}")
    
    # Execute the GET request
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Error executing GET request on instance {instanceId}. {response.text}")
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error executing GET request on instance {instanceId}. {response.reason}"
        )
    else:
        logger.info(f"GET request on instance {instanceId} executed successfully.")
        try:
            return response.json()
        except:
            return response.text    
        
async def direct_execution_post(instanceId: int, endpoint: str, body: dict):
    logger.info(f"Executing endpoint {endpoint} on instance {instanceId}")
    
    try:
        db_instance = await DbSchema.from_queryset_single(Instances.get(instanceId=instanceId))
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Algorithm instance {instanceId} not found."
        )

    # Check if instance is running
    if db_instance.status != "running":
        raise HTTPException(
            status_code=422,
            detail=f"Algorithm instance {instanceId} is not running."
        )
        
    if endpoint == "/":
        endpoint = ""
    
    # Create base URL for instance
    instance_docker = db_instance.docker
    url = f"http://localhost:{instance_docker['port']}/{endpoint}"
    logger.info(f"URL for instance {instanceId}: {url}")
    
    # Execute the POST request
    response = requests.post(url, json=body)
    if response.status_code != 200:
        logger.error(f"Error executing POST request on instance {instanceId}. {response.text}")
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error executing POST request on instance {instanceId}. {response.reason}"
        )
    else:
        logger.info(f"POST request on instance {instanceId} executed successfully.")
        try:
            return response.json()
        except:
            return response.text
