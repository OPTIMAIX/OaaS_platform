from pydantic import BaseModel

class DesignsIn(BaseModel):
    name: str
    description: str
    designJson: dict

class DesignsOut(BaseModel):
    designId: str
    name: str
    description: str
    ownerInfo: str
    designJson: dict
    
class DesignsUpdate(BaseModel):
    name: str
    description: str
    designJson: dict