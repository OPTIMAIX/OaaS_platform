from typing import Optional
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from oaasplatform.database.models import Instances

InstanceInSchema = pydantic_model_creator(
    Instances, 
    name="InstanceIn", 
    exclude_readonly=True,
    exclude=["docker",
            "status",
            "id",
            "created_at",
            "modified_at"]
)

InstanceOutSchema = pydantic_model_creator(
    Instances, name="InstanceOut", exclude=["created_at", 
                                            "modified_at",
                                            "docker",
                                            "executions",
                                            "image.created_at",
                                            "image.modified_at",
                                            "image.type",
                                            "image.resources"]
)

InstanceDatabaseSchema = pydantic_model_creator(
    Instances, name="InstanceDatabase"
)

class InstanceUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]