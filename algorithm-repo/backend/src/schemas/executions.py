from pydantic import BaseModel
from typing import Union

class ExecutionsOut(BaseModel):
    id: int
    name: str
    task_id: str
    callback_id: Union[int, None]
    input_parameters: dict
    output: dict
    error: dict
    created: str
    finished: str

class CallbackMessage(BaseModel):
    type: str
    content: Union[dict, str]