from typing import Union
import os
import time

from celery import Celery
from src.utils.algorithms_lookups import lookup_algorithm
from src.utils.executions_worker import update_executions_file

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")

@celery.task(name="debug_task")
def debug_task():
    time.sleep(10)
    return True

@celery.task(name="execute_algorithm", bind=True)
def execute_algorithm(self, name: str, input_parameters: dict, callback_id: Union[int, None], ip_client: str):
    algorithm = lookup_algorithm(name, input_parameters)
    output = algorithm.run(callback_id=callback_id, ip_client=ip_client)
    update_executions_file(task_id=self.request.id, output=output, error=algorithm.error)
    return True