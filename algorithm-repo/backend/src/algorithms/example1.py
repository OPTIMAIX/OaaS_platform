from src.models.algorithms import BaseAlgorithm

import time

class ExampleAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.description = "Example Algorithm"
        self.version = "0.1"
        super().__init__()

    def run(self, callback_id, ip_client):
        print("Running algorithm...")
        print("This is ExampleAlgorithm")
        time.sleep(10)

        # Finished algorithm
        self.output_algorithm = {"end": True}
        print(f"CallbackID: {callback_id}")
        self.onFinish(callback_id=callback_id, ip_client=ip_client)
        return self.output_algorithm