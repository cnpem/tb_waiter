from typing import Annotated

from fastapi import FastAPI, Depends, Body, HTTPException
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler


from .models import CreateTensorboardInstanceRequest, TensorboardInstance
from .dependencies import verify_token, config
from .tensorboard import start_tensorboard
from .tva import create_mobius


hostname = config.hostname
ttl = config.board_ttl
get, get_all, set, remove, contains, prune = create_mobius(ttl)


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        id="mobius.m.mobius", func=prune, trigger="interval", seconds=2 * ttl
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(root_path="/api", dependencies=[Depends(verify_token)], lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/tensorboard")
def get_tensorboard_instance(name: str):
    if contains(name):
        return get(name)
    raise HTTPException(status_code=404, detail="Instance not found")


@app.post("/tensorboard/start")
def start_tensorboard_instance(
    request: Annotated[CreateTensorboardInstanceRequest, Body]
):
    logdir = request.logdir
    name = request.name
    if contains(name):
        return get(name)

    try:
        p, port = start_tensorboard(logdir, name)
        url = f"http://{hostname}/{name}/{port}"
        instance = TensorboardInstance(url=url, logdir=logdir, name=name, pid=p.pid)
        set(name, instance)
        return instance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tensorboard/kill/{name}")
def kill_tensorboard_instance(name: str):
    if contains(name):
        remove(name)
        return {"message": "Instance killed"}
    raise HTTPException(status_code=404, detail="Instance not found")


@app.get("/tensorboard/instances")
def get_tensorboard_instances():
    return get_all()
