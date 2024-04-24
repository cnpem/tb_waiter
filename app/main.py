from typing import Annotated

import os
import subprocess
import socket
from fastapi import FastAPI, Body

from pydantic import BaseModel


class TensorboardInstance(BaseModel):
    url: str
    logdir: str
    name: str
    pid: int


class CreateTensorboardInstanceRequest(BaseModel):
    logdir: str
    name: str


tb_instances: dict[str, TensorboardInstance] = {}
hostname = "localhost"
# docker_hostname = "api"


def get_available_port():
    initial_port = 6006
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = initial_port
    while port < 65535:
        try:
            s.bind((hostname, port))
            s.close()
            return port
        except OSError:
            port += 1
    return None


def start_tensorboard(logdir: str, name: str):
    port = get_available_port()
    p = subprocess.Popen(
        [
            "tensorboard",
            "--logdir",
            logdir,
            "--port",
            str(port),
            "--bind_all",
            "--path_prefix",
            f"/{name}/{port}",
        ]
    )

    return p, port


app = FastAPI(root_path="/api")


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
    p, port = start_tensorboard(logdir, name)
    url = f"http://{hostname}:{port}/{name}/{port}"
    tb_instance = TensorboardInstance(url=url, logdir=logdir, name=name, pid=p.pid)
    tb_instances[name] = tb_instance
    return tb_instance


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
