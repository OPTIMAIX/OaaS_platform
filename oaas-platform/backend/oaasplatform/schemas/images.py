from typing import Optional
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from oaasplatform.database.models import Images

ImagesInSchema = pydantic_model_creator(
    Images, 
    name="ImagesIn", 
    exclude_readonly=True,
    exclude=["id", 
             "created_at", 
             "modified_at", 
             "resources", 
             "instances"]
)

ImagesOutSchema = pydantic_model_creator(
    Images, name="ImagesOut", exclude=["created_at", 
                                        "modified_at",
                                        "resources.created_at",
                                        "resources.modified_at",
                                        "resources.executions",
                                        "instances.created_at",
                                        "instances.modified_at",
                                        "instances.docker",
                                        "instances.executions"]
)

ImagesDatabaseSchema = pydantic_model_creator(
    Images, name="ImagesDatabase"
)

class ImagesUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
