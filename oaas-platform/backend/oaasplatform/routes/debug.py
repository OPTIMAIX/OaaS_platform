from fastapi import APIRouter

from oaasplatform.main import logger
from oaasplatform.utils.docker import create_client

router = APIRouter(tags=["Debug"])

@router.post("/debug/docker")
def debug_docker():
    client = create_client()
    logger.info(client.containers.list())
    return "OK"

from oaasplatform.utils import algorithm_repository_wrapper as alg
# debug client api
@router.get("/debug_algorithms")
async def debug_alg():
    algorithms_dict = alg.get_algorithms("127.0.0.1", 5500)
    logger.info (algorithms_dict)

    # Creating descriptors
    logger.info("Creating descriptors...")
    return await alg.create_algorithms_descriptors(algorithm_repo_id=4, algorithm_response=algorithms_dict)

@router.get("/debug/isUp")
async def debug_isup(instance_id: int):
    from oaasplatform.utils.docker import instance_isUp
    from oaasplatform.schemas.instances import InstanceDatabaseSchema as DbSchema
    from oaasplatform.database.models import Instances

    obj = await DbSchema.from_queryset_single(Instances.get(id=instance_id))

    instance_isUp(obj.docker)

    return ""
