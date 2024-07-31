# Algorithm Repository - Python (FastAPI)

This Algorithm Repository will be used by OaaS Node in order to execute algorithms.

* Programing Language: Python
* Framework: FastAPI

# Custom Algorithms
* New algorithms must be added as a file (`.py`) in folder: `backend/src/algorithms`
* New algorithms must follow the algorithm schema, view `example1.py` or `example2.py`
* If we need more python packages (example `pandas`), add to `backend/requirements.txt`
* New algorithms files we will auto-detected by the algorithm repository. 

Base Schema for Algorithms:
```python
from src.models.algorithms import BaseAlgorithm

import time

class TestAlgorithm(BaseAlgorithm):
    def __init__(self, input_parameters):
        self.description = "Example Algorithm 2"
        self.version = "0.2"
        self.example_input = {
            "name": "example",
            "ip_address": [1,2,3],
            "version": 5.0
        }
        self.example_output = {
            "success": True,
            "output": {
                "name": "example",
                "ip_address": [1,2,3],
                "version": 5.0
            }
        }
        self.input_parameters = input_parameters
        super().__init__()

    def run(self, callback_id, ip_client):
        print("Running algorithm...")
        print(f"Input parameter: {self.input_parameters}")
        print("This is TestAlgorithm")
        time.sleep(10)

        self.output_algorithm = {
            "success": True,
            "output": self.input_parameters
        }
        self.onFinish(callback_id=callback_id, ip_client=ip_client)
        return self.output_algorithm
```

# Docker 
## Deployment for local/debug
* `sudo docker-compose up`
* Go to: [localhost:55955](http://localhost:55955/)

## Publish Algorithm Repository Image
### If Docker Hub
* `sudo docker login`
### If Private Registry
* `sudo docker login <URL Registry>`

### Publish to Docker Hub
* `sudo docker build -t <docker_hub_username>/<app_name>:latest .`
* `sudo docker push <docker_hub_username>/<app_name>:latest`

OR

* `sudo docker build -t <app_name> .`
* `sudo docker tag <app_name> <docker_hub_username>/<app_name>:latest`
* `sudo docker push <docker_hub_username>/<app_name>:latest`

### Publish to Private Registry
* `sudo docker build -t <registry_username>/<app_name>:latest .`
* `sudo docker push <URL Registry>/<registry_username>/<app_name>:latest`