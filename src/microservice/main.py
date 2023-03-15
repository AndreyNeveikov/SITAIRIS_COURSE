import time

from fastapi import FastAPI

from router import StatisticsRouter
from services import LocalstackLambda

app = FastAPI()

app.include_router(StatisticsRouter().router)


@app.on_event('startup')
def startup():
    time.sleep(20)  # because rabbitmq loads with some timeout
    LocalstackLambda().create_lambda('handler')
    LocalstackLambda().invoke_function('handler')
