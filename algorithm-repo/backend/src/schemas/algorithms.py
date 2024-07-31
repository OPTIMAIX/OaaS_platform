from pydantic import BaseModel

class AlgorithmsOut(BaseModel):
    id: int
    name: str
    version: str
    description: str
    module: str
    input_schema: dict
    output_schema: dict
