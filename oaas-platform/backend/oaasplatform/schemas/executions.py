from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

from oaasplatform.database.models import Executions

ExecutionsInSchema = pydantic_model_creator(
    Executions, name="ExecutionsIn", exclude_readonly=True,
                                                      exclude=["output_success",
                                                               "output_error",
                                                               "executionStart",
                                                               "executionEnd",
                                                               "lastProgressFraction",
                                                               "lastProgress",
                                                               "status",
                                                               "created_at",
                                                               "modified_at",]
)

ExecutionsOutSchema = pydantic_model_creator(
    Executions, name="ExecutionsOut", exclude=["created_at", 
                                                "modified_at",
                                                "image",
                                                "image_id",
                                                "instance.created_at",
                                                "instance.modified_at",
                                                "instance.docker",
                                                "instance.image.created_at",
                                                "instance.image.modified_at",
                                                "instance.image.resources",
                                                "resource.created_at",
                                                "resource.modified_at",
                                                "resource.images"]
)

ExecutionsDatabaseSchema = pydantic_model_creator(
    Executions, name="ExecutionsDatabase"
)

class InExecutionSchema(BaseModel):
    input_parameters: dict
    resource_id: int
    instance_id: int
