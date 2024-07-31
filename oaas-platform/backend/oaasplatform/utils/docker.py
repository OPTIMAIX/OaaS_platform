import docker

from oaasplatform.main import logger
from oaasplatform.config import settings
from oaasplatform.database.models import ImageType

def create_client() -> docker.DockerClient:
    try:
        client = docker.from_env()
        logger.debug("Docker client created")
        return client
    except docker.errors.DockerException:
        logger.error("Unable to find Docker socket. Check if Docker is started.")


def selftest_docker() -> bool:
    try:
        client = docker.from_env()
        client.ping()
        return True
    except docker.errors.DockerException:
        return False

def loggin_registry(client: docker.DockerClient, user: str, password: str, registry: str) -> docker.DockerClient:
    try:
        client.login(registry=registry, username=user, password=password)
        return client
    except Exception as ex:
        logger.error(ex)
        logger.error("Unable to authenticate with registry")
        raise Exception

def create_containers_fastapi_redis(docker_dict: dict, client: docker.DockerClient, docker_image: str, instance_id: int, network_id: str, volume_id: str, host_port: int):
    output_backend = client.containers.run(image=docker_image,
                                                name=f"algRepo_backend_{instance_id}",
                                                network=network_id,
                                                environment={
                                                    "CELERY_BROKER_URL": "redis://redis:6379/0",
                                                    "CELERY_RESULT_BACKEND": "redis://redis:6379/0"
                                                },
                                                ports={'55955/tcp': host_port},
                                                working_dir='/app',
                                                volumes=[f'{volume_id}:/app'],
                                                detach=True)
    logger.debug(f"Backend container: {output_backend}")

    output_celery = client.containers.run(image=docker_image,
                                                name=f"algRepo_worker_{instance_id}",
                                                command="celery --app=src.worker.celery worker --loglevel=INFO",
                                                network=network_id,
                                                environment={
                                                    "CELERY_BROKER_URL": "redis://redis:6379/0",
                                                    "CELERY_RESULT_BACKEND": "redis://redis:6379/0"
                                                },
                                                working_dir='/app',
                                                volumes=[f'{volume_id}:/app'],
                                                detach=True)
    logger.debug(f"Worker container: {output_celery}")

    output_redis = client.containers.run(image="redis:7-alpine",
                                                hostname="redis",
                                                name=f"algRepo_redis_{instance_id}",
                                                network=network_id,
                                                detach=True)
    logger.debug(f"Redis container: {output_redis}")
    
    docker_dict["backend_id"] = output_backend.short_id
    docker_dict["worker_id"] = output_celery.short_id
    docker_dict["redis_id"] = output_redis.short_id
    return

def create_single_container(container_port: str, docker_dict: dict, client: docker.DockerClient, docker_image: str, instance_id: int, network_id: str, volume_id: str, host_port: int):
    output_backend = client.containers.run(image=docker_image,
                                                name=f"algRepo_backend_{instance_id}",
                                                network=network_id,
                                                ports={container_port: host_port},
                                                working_dir='/app',
                                                volumes=[f'{volume_id}:/app'],
                                                detach=True)
    logger.debug(f"Backend container: {output_backend}")
    docker_dict["backend_id"] = output_backend.short_id
    return

def deploy_instance(type: ImageType, instance_id: int, docker_image: str, host_port: int):
    client = create_client()

    if settings.REGISTRY_URL:
        logger.debug(f"Using registry: {settings.REGISTRY_URL}")
        docker_image = f"{settings.REGISTRY_URL}/{docker_image}"
        logger.debug(f"Image: {docker_image}")

        # Logging to Registry
        client = loggin_registry(client=client, user=settings.REGISTRY_USER,
                                                password=settings.REGISTRY_PASSWORD,
                                                registry=settings.REGISTRY_URL)

    # Create network & volumes
    try:
        network = client.networks.create(name=f"algorithm_repo_stack_{instance_id}")
        volume = client.volumes.create(name=f"algorithm_volume_stack_{instance_id}")
    except:
        logger.error("Unable to create networks or volumes on Docker.")
        logger.error("Check if network/volume already exists...")
        raise Exception

    # Create new containers for instance
    docker_dict = {}
    try:
        docker_dict["image"] = docker_image
        docker_dict["port"] = host_port
        docker_dict["network_id"] = network.short_id
        docker_dict["volume_id"] = volume.id
        logger.debug(f"Docker dict content before create: {docker_dict}")
        logger.info(f"Creating containers for instance {instance_id}")
        
        if (type == ImageType.FASTAPI_REDIS):
            create_containers_fastapi_redis(instance_id=instance_id,
                                            docker_dict=docker_dict,
                                            client=client, 
                                            docker_image=docker_image,
                                            network_id=network.short_id,
                                            volume_id=volume.id,
                                            host_port=host_port)
        elif (type == ImageType.PYTHON):
            create_single_container(container_port='55955/tcp',
                                    docker_dict=docker_dict,
                                    client=client,
                                    docker_image=docker_image,
                                    instance_id=instance_id,
                                    network_id=network.short_id,
                                    volume_id=volume.id,
                                    host_port=host_port)
        elif (type == ImageType.JAVA):
            create_single_container(container_port='55955/tcp',
                                    docker_dict=docker_dict,
                                    client=client,
                                    docker_image=docker_image,
                                    instance_id=instance_id,
                                    network_id=network.short_id,
                                    volume_id=volume.id,
                                    host_port=host_port)
        elif (type == ImageType.MATLAB):
            create_single_container(container_port='9910/tcp',
                                    docker_dict=docker_dict,
                                    client=client,
                                    docker_image=docker_image,
                                    instance_id=instance_id,
                                    network_id=network.short_id,
                                    volume_id=volume.id,
                                    host_port=host_port)
        else:
            logger.error("Unknown repository type")
            raise Exception
        
        if not settings.NETWORK_MODE_HOST:
            logger.debug(f"Connecting root container to network: {network.short_id}")
            try:
                # Connect root container to instance
                connect_container_to_network(container_name=settings.OAAS_NODE_CONTAINER_NAME,
                                             network_id=network.id)
            except Exception as ex:
                logger.error(ex)
                logger.error("Unable to connect root container to instance")
                pass
            
    except docker.errors.ContainerError:
        logger.error("Container exits with non-zero")
    except docker.errors.ImageNotFound:
        logger.error("Image not found")
    except docker.errors.APIError as err:
        logger.error(err)
        logger.error("Server returns an error")

    logger.info("Containers sucesfully created.")
    return docker_dict      # Return JSON with containers ID

def start_instance(type: ImageType, instance_id: int, docker_dict: dict):
    client = create_client()

    try:
        logger.info(f"Starting instance {instance_id}")
        
        container_to_start = []
        if type == ImageType.FASTAPI_REDIS:
            backend = client.containers.get(docker_dict["backend_id"])
            container_to_start.append(backend)
            worker = client.containers.get(docker_dict["worker_id"])
            container_to_start.append(worker)
            redis = client.containers.get(docker_dict["redis_id"])
            container_to_start.append(redis)
        else:
            backend = client.containers.get(docker_dict["backend_id"])
            container_to_start.append(backend)

        # Starting containers
        for container in container_to_start:
            if container.status != "running":
                container.start()
    except:
        logger.error("Unable to start an instance")
        raise Exception

def stop_instance(type: ImageType, instance_id: int, docker_dict: dict):
    client = create_client()

    try:
        logger.info(f"Stopping instance {instance_id}")
        
        container_to_stop = []
        if type == ImageType.FASTAPI_REDIS:
            backend = client.containers.get(docker_dict["backend_id"])
            container_to_stop.append(backend)
            worker = client.containers.get(docker_dict["worker_id"])
            container_to_stop.append(worker)
            redis = client.containers.get(docker_dict["redis_id"])
            container_to_stop.append(redis)
        else:
            backend = client.containers.get(docker_dict["backend_id"])
            container_to_stop.append(backend)
        
        for container in container_to_stop:
            if container.status == "running":
                container.stop()
    except:
        logger.error("Unable to stop containers")
        raise Exception

def delete_instance(type: ImageType, instance_id: int, docker_dict: dict):
    client = create_client()

    try:
        logger.info(f"Stopping and delete instance {instance_id}")
        
        container_to_delete = []
        if type == ImageType.FASTAPI_REDIS:
            backend = client.containers.get(docker_dict["backend_id"])
            container_to_delete.append(backend)
            worker = client.containers.get(docker_dict["worker_id"])
            container_to_delete.append(worker)
            redis = client.containers.get(docker_dict["redis_id"])
            container_to_delete.append(redis)
        else:
            backend = client.containers.get(docker_dict["backend_id"])
            container_to_delete.append(backend)
    
        if not settings.NETWORK_MODE_HOST:
            # Disconnect root container to instance
            try:
                disconnect_container_to_network(container_name=settings.OAAS_NODE_CONTAINER_NAME,
                                                network_id=docker_dict["network_id"])
            except:
                pass
    
        # Stopping containers
        for container in container_to_delete:
            if container.status == "running":
                container.kill()
        
        # Remove containers
        for container in container_to_delete:
            container.remove()

        logger.info("Deleting network and volume...")

        # Get network & volume
        network = client.networks.get(docker_dict["network_id"])
        volume = client.volumes.get(docker_dict["volume_id"])

        # Remove network & volume
        network.remove()
        volume.remove()
    except docker.errors.APIError as ex:
        logger.error("Docker error. Unable to delete containers")
        logger.error(ex)
        raise Exception
    except Exception as ex:
        logger.error(ex)
        logger.error("General error. Unable to delete container")
        raise Exception

def connect_container_to_network(network_id: str, container_name: str):
    client = create_client()

    try:
        # Get Network and Container
        network = client.networks.get(network_id)
        container = client.containers.get(container_name)

        # Connecting
        network.connect(container)      # Throws and error: TypeError: NetworkError, this is cause for the change on the network adapter
    except:
        logger.error("Unable to connect containers")
        raise Exception

def disconnect_container_to_network(network_id: str, container_name: str):
    client = create_client()

    try:
        # Get Network and Container
        network = client.networks.get(network_id)
        container = client.containers.get(container_name)

        # Connecting
        network.disconnect(container)
    except:
        logger.error("Unable to disconnect containers")
        raise Exception

def instance_isUp(docker_dict: dict):
    client = create_client()

    try:
        backend = client.containers.get(docker_dict["backend_id"])
        status = backend.status
        if status == "running":
            return True
        elif status == "exited":
            return False
    except:
        logger.error("Unable to connect to container")
        
def get_IP_container(container_id, network_id):
    client = create_client()
    try:
        container = client.containers.get(container_id)
        network = client.networks.get(network_id)
        ip_add = container.attrs["NetworkSettings"]["Networks"][network.name]["IPAddress"]
        return ip_add
    except Exception as ex:
        logger.error(ex)
        logger.error("Unable to get IP Address of backend")
