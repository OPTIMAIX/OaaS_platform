from tortoise import fields, models
from enum import Enum

class ImageType(str, Enum):
    PYTHON = "python"
    FASTAPI_REDIS = "fastapi-redis"
    JAVA = "java"
    MATLAB = "matlab"
    
class ExecutionType(str, Enum):
    OAAS = "OaaS"       # Execute using the OAAS method    
    DIRECT = "direct"   # Execute directly in the repository, using the API of the repository, without using the OAAS method

class Images(models.Model):
    imageId = fields.IntField(pk=True)
    name = fields.CharField(max_length=40, unique=True)
    description = fields.CharField(max_length=260)
    imageUrl = fields.CharField(max_length=50)
    type = fields.CharEnumField(ImageType, max_length=20)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    # Relation with algorithm descriptors
    resources: fields.ForeignKeyRelation(model_name="models.ResourceDescriptors")

    # Relation with algorithm Instances
    instances: fields.ForeignKeyRelation(model_name="models.Instances")

class ResourceDescriptors(models.Model):
    resourceId = fields.IntField(pk=True)
    localId = fields.IntField()
    name = fields.CharField(max_length=40)
    version = fields.CharField(max_length=10)
    description = fields.CharField(max_length=260)
    execution_type = fields.CharEnumField(ExecutionType, max_length=20, default=ExecutionType.OAAS)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    
    # As JSON schema
    inputParametersTemplate = fields.JSONField(null=True)

    # As JSON schema
    outputParametersTemplateSuccess = fields.JSONField(null=True)

    # As JSON schema
    outputParametersTemplateFailure = fields.JSONField(null=True)

    # Relation with algorithm repositories
    images = fields.ForeignKeyField(model_name="models.Images", related_name="resources", to_field="imageId")

class Instances(models.Model):
    instanceId = fields.IntField(pk=True, unique=True)
    name = fields.CharField(max_length=40, unique=True)
    description = fields.CharField(max_length=260)
    status = fields.CharField(max_length=20, null=True)
    quotaInformation = fields.JSONField(default={
        "cpu": "1 core",
        "ram": "512MB",
        "diskSpace": "10GB",
        "networkBandwidth": "100Mbps"
    })
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    docker = fields.JSONField(null=True)

    # Relation with algorithm repositories
    image = fields.ForeignKeyField(model_name="models.Images", related_name="instances", to_field="imageId")

class Executions(models.Model):
    executionId = fields.IntField(pk=True, unique=True)
    status = fields.IntField(null=True)
    lastProgress = fields.CharField(max_length=30, null=True)
    lastProgressFraction = fields.FloatField(null=True)
    executionRequest = fields.DatetimeField(auto_now=True)
    executionStart = fields.DatetimeField(null=True)
    executionEnd = fields.DatetimeField(null=True)
    input_parameters = fields.JSONField(null=True)
    output_success = fields.JSONField(null=True)
    output_error = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    # Relation to algorithm instance 
    instance = fields.ForeignKeyField(model_name="models.Instances", related_name="executions")

    # Relation to algorithm descriptor
    resource = fields.ForeignKeyField(model_name="models.ResourceDescriptors", related_name="executions")
