import docker

from oaasplatform.database.models import Instances

#
#   Standalone methods for 'on_events' by FastAPI (startup & shutdown)
#   Just a copy of methods inside docker.py to avoid circular imports
#

def create_client() -> docker.DockerClient:
    try:
        client = docker.from_env()
        return client
    except docker.errors.DockerException:
        raise Exception

def start_instance(docker_dict: dict):
    client = create_client()

    try:
        container_to_start = []
        # Backend is always present!
        backend = client.containers.get(docker_dict["backend_id"])
        container_to_start.append(backend)
        
        if ("worker_id" in docker_dict):
            worker = client.containers.get(docker_dict["worker_id"])
            container_to_start.append(worker)
        if ("redis_id" in docker_dict):
            redis = client.containers.get(docker_dict["redis_id"])
            container_to_start.append(redis)

        # Starting containers
        for container in container_to_start:
            container.start()
    except docker.errors.APIError as ex:
        print("Unable to start an instance")
        print(ex)
        raise Exception

def stop_instance(docker_dict: dict):
    client = create_client()

    try:
        container_to_stop = []
        # Backend is always present!
        backend = client.containers.get(docker_dict["backend_id"])
        container_to_stop.append(backend)
        
        if ("worker_id" in docker_dict):
            worker = client.containers.get(docker_dict["worker_id"])
            container_to_stop.append(worker)
        if ("redis_id" in docker_dict):
            redis = client.containers.get(docker_dict["redis_id"])
            container_to_stop.append(redis)

        # Stopping containers
        for container in container_to_stop:
            container.stop()
    except docker.errors.APIError as ex:
        print("Unable to stop an instance")
        print(ex)
        raise Exception

def register_start_instances(app) -> None:
    @app.on_event('startup')
    async def start_instances():
        # Get all instances
        try:
            instances = await Instances.all()
        except Exception:
            raise Exception("Database not ready. Verify if database is already -> init-db...")
        if instances != []:
            # Start each instance
            for instance in instances:
                try:
                    start_instance(docker_dict=instance.docker)
                    instance.status = "running"
                    await instance.save()
                except:
                    print("Unable to start instances")


def register_stop_instances(app) -> None:
    @app.on_event('shutdown')
    async def shutdown_instances():
        # Get all instances
        instances = await Instances.all()
        if instances != []:
            # Shutdown each instance
            for instance in instances:
                try:
                    stop_instance(docker_dict=instance.docker)
                    instance.status = "exited"
                    await instance.save()
                except:
                    print("Unable to stop instances")

