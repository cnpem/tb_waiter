from pydantic import BaseModel


class TensorboardInstance(BaseModel):
    url: str
    logdir: str
    name: str
    pid: int


class CreateTensorboardInstanceRequest(BaseModel):
    logdir: str
    name: str