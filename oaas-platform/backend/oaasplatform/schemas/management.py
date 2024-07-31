from pydantic import BaseModel

from oaasplatform.schemas.info import ComputationResources

class OaaSNodeOut(BaseModel):
    ipAddressOrDns: str
    ipPort: int
    name: str
    description: str
    ownerInfo: str
    computationResources: ComputationResources
    
class OaaSNodeUpdate(BaseModel):
    name: str
    description: str
    ownerInfo: str
    computationResources: dict