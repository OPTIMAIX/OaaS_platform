from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist
from time import sleep

from oaasplatform.main import logger
from oaasplatform.config import settings
from oaasplatform.utils import docker
from oaasplatform.schemas.status import Status
from oaasplatform.schemas.images import ImagesOutSchema
from oaasplatform.schemas.instances import InstanceOutSchema as OutSchema
from oaasplatform.schemas.instances import InstanceDatabaseSchema as DbSchema
from oaasplatform.database.models import Instances, Images

def get_instances():
    return Instances.all().prefetch_related('image')

async def get_instance(instanceId):
    return await OutSchema.from_queryset_single(Instances.get(instanceId=instanceId))

async def stop_instances() -> Status:
    instances = await Instances.all().prefetch_related('image')
    if instances != []:
        # Shutdown each instance
        for instance in instances:
            try:
                docker.stop_instance(instance_id=instance.instanceId, type=instance.image.type, docker_dict=instance.docker)
                instance.status = "exited"
                await instance.save()
            except:
                raise HTTPException(
                    status_code=422,
                    detail=f"Unable to stop instances."
                )
        return Status(message="Sucesfully stopped all instances.")
    raise HTTPException(
        status_code=422,
        detail=f"No instances found."
    )

async def create_instance(instance) -> OutSchema:
    try:
        instance_obj = await Instances.create(**instance.dict(exclude_unset=True))
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(
            status_code=422,
            detail=f"Sorry, that instance already exists"
        )

    # Up an instance given an ID
    try:
        image_obj = await ImagesOutSchema.from_queryset_single(Images.get(imageId=instance.image_id))
    except:
        raise HTTPException(
            status_code=422,
            detail=f"Unable to found repository"
        )

    try:
        docker_dict = docker.deploy_instance(docker_image=image_obj.imageUrl,
                                             instance_id=instance_obj.instanceId,
                                             type=image_obj.type,
                                             host_port=(instance_obj.instanceId + settings.INIT_PORT))
        logger.debug(f"Docker dict: {docker_dict}")
    except:
        raise HTTPException(
            status_code=422,
            detail=f"Internal error. Unable to start instance"
        )

    # Add docker_dict to instance_obj
    instance_obj.docker = docker_dict
    instance_obj.status = "running"
    await instance_obj.save()

    return await OutSchema.from_tortoise_orm(instance_obj)

async def update_instance(instanceId, instance) -> OutSchema:
    try:
        db_instance = await OutSchema.from_queryset_single(Instances.get(instanceId=instanceId))
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Instance {instanceId} not found"
        )

    await Instances.filter(instanceId=instanceId).update(**instance.dict(exclude_unset=True))
    return await OutSchema.from_queryset_single(Instances.get(instanceId=instanceId))

async def delete_instance(instanceId) -> Status:
    try:
        db_instance = await DbSchema.from_queryset_single(Instances.get(instanceId=instanceId))
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Instance {instanceId} not found."
        )

    instance_id = db_instance.instanceId
    instance_type = db_instance.image.type
    instance_docker = db_instance.docker

    try:
        docker.delete_instance(instance_id=instance_id, type=instance_type, docker_dict=instance_docker)
    except:
        logger.debug(f"Instance {instance_id} isnt running.")

        await start_instance(instanceId=instance_id)
        sleep(1)

        try:
            docker.delete_instance(instance_id=instance_id, type=instance_type, docker_dict=instance_docker)
        except:
            raise HTTPException(
                status_code=422,
                detail=f"Internal error. Unable to delete instance {instance_id}"
            )

    deleted_instance = await Instances.filter(instanceId=instanceId).delete()
    if not deleted_instance:
        raise HTTPException(
            status_code=422,
            detail=f"Instance {instanceId} not found."
        )

    return Status(message=f"Deleted instance {instanceId}")

async def start_instance(instanceId: int) -> Status:
    try:
        instance = Instances.get(instanceId=instanceId).prefetch_related('image')
        db_instance = await DbSchema.from_queryset_single(instance)
    except:
        raise HTTPException(
            status_code=422,
            detail=f"Instance {instanceId} not found"
        )


    if docker.instance_isUp(db_instance.docker) == False:
        try:
            docker.start_instance(instance_id=db_instance.instanceId, type= db_instance.image.type, docker_dict=db_instance.docker)
            await instance.update(status="running")
        except Exception as ex:
            logger.error(ex)
            raise HTTPException(
                status_code=422,
                detail=f"Internal error. Unable to start instance {instanceId}"
            )
        return Status(message=f"Started instance {instanceId}")
    else:
        raise HTTPException(
            status_code=422,
            detail=f"Instance {instanceId} is already started"
        )
    

async def stop_instance(instanceId: int) -> Status:
    try:
        instance = Instances.get(instanceId=instanceId).prefetch_related('image')
        db_instance = await DbSchema.from_queryset_single(instance)
    except Exception as ex:
        logger.error(ex)
        raise HTTPException(
            status_code=422,
            detail=f"Instance {instanceId} not found"
        )


    if docker.instance_isUp(db_instance.docker) == True:
        try:
            docker.stop_instance(instance_id=db_instance.instanceId, type= db_instance.image.type, docker_dict=db_instance.docker)
            await instance.update(status="exited")
        except Exception as ex:
            logger.error(ex)
            raise HTTPException(
                status_code=422,
                detail=f"Internal error. Unable to stop instance {instanceId}"
            )
        return Status(message=f"Stopped instance {instanceId}")
    else:
        raise HTTPException(
            status_code=422,
            detail=f"Instance {instanceId} is already stopped"
        )
