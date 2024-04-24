from typing import Annotated
import os

from fastapi import FastAPI, Depends, Body, HTTPException

from .models import CreateTensorboardInstanceRequest, TensorboardInstance
from .dependencies import verify_token, config
from .tensorboard import start_tensorboard


tb_instances: dict[str, TensorboardInstance] = {}
hostname = config.hostname


app = FastAPI(root_path="/api", dependencies=[Depends(verify_token)])


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/tensorboard")
def get_tensorboard_instance(name: str):
    tb_instance = tb_instances.get(name)
    if tb_instance:
        return tb_instance
    return {"message": "Instance not found"}


@app.post("/tensorboard/start")
def start_tensorboard_instance(
    request: Annotated[CreateTensorboardInstanceRequest, Body]
):
    logdir = request.logdir
    name = request.name
    if name in tb_instances:
        return {"message": "Instance already exists"}

    try:
        p, port = start_tensorboard(logdir, name)
        url = f"http://{hostname}/{name}/{port}"
        tb_instance = TensorboardInstance(url=url, logdir=logdir, name=name, pid=p.pid)
        tb_instances[name] = tb_instance
        return tb_instance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tensorboard/kill/{name}")
def kill_tensorboard_instance(name: str):
    tb_instance = tb_instances.get(name)
    if tb_instance:
        os.kill(tb_instance.pid, 9)
        del tb_instances[name]
        return {"message": "Instance killed"}
    return {"message": "Instance not found"}


@app.get("/tensorboard/instances")
def get_tensorboard_instances():
    return tb_instances


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
