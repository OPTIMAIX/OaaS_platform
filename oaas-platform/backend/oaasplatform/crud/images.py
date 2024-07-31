from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist, IntegrityError
import time

from oaasplatform.main import logger
from oaasplatform.utils import docker
from oaasplatform.utils import algorithm_repository_wrapper as alg_repo
from oaasplatform.config import settings
from oaasplatform.schemas.status import Status
from oaasplatform.schemas.images import ImagesOutSchema as OutSchema
from oaasplatform.database.models import Images, Instances, ImageType

def get_images():
    return Images.all().prefetch_related('resources', 'instances')

async def get_image(imageId) -> OutSchema:
    return await OutSchema.from_queryset_single(Images.get(imageId=imageId))

async def create_image(image):
    logger.info(image.dict(exclude_unset=True))
    
    try:
        image_obj = await Images.create(**image.dict(exclude_unset=True))
    except IntegrityError:
        raise HTTPException(
            status_code=422,
            detail=f"Sorry, that image already exists"
        )

    print("Image URL: ", image.imageUrl)

    # Instance database to retrieve the algorithms inside.
    try:
        docker_dict = docker.deploy_instance(docker_image=image.imageUrl, 
                                             instance_id=0, 
                                             host_port=settings.DISCOVERY_PORT,
                                             type=image.type)
        logger.debug(f"Docker Dict: {docker_dict}")
    except Exception as e:
        print(e)
        await image_obj.delete()
        raise HTTPException(
            status_code=422,
            detail=f"Internal error. Unable to start instance"
        )

    # Get Algorithms of image & Update Descriptors
    try:
        time.sleep(5) # Some delay to give time to startup the container
        if settings.NETWORK_MODE_HOST:
            container_ip = "127.0.0.1"
            algorithm_port = settings.DISCOVERY_PORT
        else:
            container_ip = docker.get_IP_container(container_id=docker_dict['backend_id'],
                                                   network_id=docker_dict['network_id'])
            algorithm_port = settings.INTERNAL_PORT
        algorithms = alg_repo.get_algorithms(ip=container_ip, 
                                             port=algorithm_port)
    except:
        algorithms = {}
        logger.error("Unable to obtain resources from image")
        if image_obj.type == ImageType.MATLAB:
            # Manually create the algorithm descriptor for MATLAB Runtime
            name = image.imageUrl
            algorithm = {
                "localId": 0,
                "name": name,
                "version": "1.0",
                "description": f"MATLAB Runtime for algorithm " + name,
            }
            await alg_repo.create_manually_algorithm_descriptor_direct_execution(algorithm_in=algorithm,
                                                                                images_id=image_obj.imageId)
        elif image_obj.type == ImageType.PYTHON or image_obj.type == ImageType.JAVA:
            name = image.imageUrl
            algorithm = {
                "localId": 0,
                "name": name,
                "version": "1.0",
                "description": f"Direct Algorithm " + name,
            }
            await alg_repo.create_manually_algorithm_descriptor_direct_execution(algorithm_in=algorithm,
                                                                                images_id=image_obj.imageId)
        else:
            logger.error("Unable to create resource")
            
    # Remove instance
    try:
        docker.delete_instance(instance_id=0, type=image.type, docker_dict=docker_dict)
    except:
        raise HTTPException(
            status_code=422,
            detail=f"Internal error. Unable to delete instance"
        )

    try:
        if algorithms == {}:
            logger.info("No resources found in repository. Continue...")
        else:
            logger.debug("Creating resource...")
            await alg_repo.create_algorithms_descriptors(algorithm_repo_id=image_obj.imageId, 
                                                         algorithm_response=algorithms)
    except:
        await image_obj.delete()     # Delete entry from database
        raise HTTPException(
            status_code=422,
            detail=f"Internal error. Unable to create resource"
        )

    return await OutSchema.from_tortoise_orm(image_obj)

async def update_image(imageId, image) -> OutSchema:
    try:
        db_repo = await OutSchema.from_queryset_single(Images.get(imageId=imageId))
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Image {imageId} not found."
        )

    # Here if we want to insert permissions
    await Images.filter(imageId=imageId).update(**image.dict(exclude_unset=True))
    return await OutSchema.from_queryset_single(Images.get(imageId=imageId))

async def delete_image(imageId) -> Status:
    try:
        db_image = await OutSchema.from_queryset_single(Images.get(imageId=imageId))
    except DoesNotExist:
        raise HTTPException(
            status_code=422,
            detail=f"Image {imageId} not found."
        )

    # Check if instance is up
    instances = await Instances.filter(image_id=db_image.imageId)
    for instance in instances:
        if docker.instance_isUp(docker_dict=instance.docker):
            raise HTTPException(
                    status_code=422,
                    detail=f"Some instances are using this image. Must delete that instances before, in order to delete this image."
                )

    # Here if we want to insert permissions
    deleted_repo = await Images.filter(imageId=imageId).delete()
    if not deleted_repo:
        raise HTTPException(
            status_code=422,
            detail=f"Image {imageId} not found."
        )
    return Status(message=f"Deleted image {imageId}")
    