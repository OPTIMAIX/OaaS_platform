from tortoise.contrib.pydantic import pydantic_model_creator

from oaasplatform.database.models import ResourceDescriptors

ResourceDescriptorInSchema = pydantic_model_creator(
    ResourceDescriptors, name="ResourcesIn", exclude_readonly=True, exclude=["created_at",
                                                                            "modified_at"]
)

ResourceDescriptorOutSchema = pydantic_model_creator(
    ResourceDescriptors, name="ResourcesOut", exclude=["created_at", 
                                                       "modified_at"]
)

ResourceDescriptorDatabaseSchema = pydantic_model_creator(
    ResourceDescriptors, name="ResourcesDatabase"
)

