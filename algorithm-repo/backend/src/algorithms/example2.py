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
        print(f"CallbackID: {callback_id}")
        return self.output_algorithm