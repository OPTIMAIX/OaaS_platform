from pydantic import BaseModel

class ComputationResources(BaseModel):
    cpu: str
    ram: str

class InfoOut(BaseModel):
    ip_address: str
    ip_port: int
    name: str
    description: str
    owner_info: str
    computation_resources: ComputationResources

class InfoIn(BaseModel):
    name: str
    description: str
    owner_info: str
