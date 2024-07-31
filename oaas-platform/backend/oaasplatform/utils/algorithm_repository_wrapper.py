import json, requests
from tortoise.exceptions import DoesNotExist

from oaasplatform.main import logger
from oaasplatform.database.models import ResourceDescriptors, ExecutionType

def get_algorithms(ip: str, port: int) -> dict:
    url = f"http://{ip}:{port}/algorithms"
    try:
        logger.info(f"Getting algorithms: {url}")
        response = requests.get(url, timeout=5)
    except ConnectionResetError as ex:
        logger.error(ex)
        raise Exception
    except Exception as ex:
        logger.error(ex)
        raise Exception
    logger.debug(response)

    if response.status_code == 200:
        logger.debug("Response OK")
        output = json.loads(response.content)
        logger.info(f"Output, algorithms: {output}")
        return output
    else:
        logger.error(f"Response got {response.status_code}")
        logger.error("Unable to connect that algorithm repository.")
        raise Exception

async def create_algorithms_descriptors(algorithm_repo_id: int, algorithm_response: dict):
    logger.info("Trying to create algorithm descriptors...")

    num_alg = 0
    for alg in algorithm_response:
        logger.debug(alg)
        try:
            alg["localId"] = alg.pop("id")
            alg["inputParametersTemplate"] = alg.pop("input_schema")
            alg["outputParametersTemplateSuccess"] = alg.pop("output_schema")
            alg["execution_type"] = ExecutionType.OAAS
            await ResourceDescriptors.create(**alg, images_id=algorithm_repo_id)
            num_alg = num_alg + 1
        except DoesNotExist:
            logger.error("Unable to create algorithm descriptors")
            raise Exception

    logger.info(f"Succesfully created {num_alg} algorithms descriptors")

async def create_manually_algorithm_descriptor_direct_execution(images_id: int, algorithm_in: dict):
    logger.info(f"Creating manually algorithm descriptor for {algorithm_in['name']}...")
    try:
        algorithm = {}
        algorithm["localId"] = algorithm_in.pop("localId")
        algorithm["name"] = algorithm_in.pop("name")
        algorithm["version"] = algorithm_in.pop("version")
        algorithm["description"] = algorithm_in.pop("description")
        algorithm["inputParametersTemplate"] = "{}"
        algorithm["outputParametersTemplateSuccess"] = "{}"
        algorithm["execution_type"] = ExecutionType.DIRECT
        await ResourceDescriptors.create(**algorithm, images_id=images_id)
    except DoesNotExist as ex:
        logger.error(f"Unable to create manually algorithm descriptor. Error: {ex}")
        return

def launch_execution(executionId: int, ip: str, port: int, local_algorithm_id: int, input_parameters: dict):
    url = f"http://{ip}:{port}/executions/{local_algorithm_id}"
    params = {"callback_id": executionId}

    logger.debug(f"Launching execution with URL: {url}")
    response_launch = requests.post(url=url, json=input_parameters, params=params)

    if response_launch.status_code == 200:
        logger.debug("Launch execution got response OK")
        output = json.loads(response_launch.content)
        return output
    else:
        logger.error(f"Response got: {response_launch.status_code}")
        logger.error(response_launch.content)
        raise ValueError