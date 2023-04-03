from fastapi import FastAPI

from consumer import consume
from middleware import MyMiddleware
from router import StatisticsRouter

app = FastAPI()

app.add_middleware(MyMiddleware)
app.include_router(StatisticsRouter().router)


@app.on_event('startup')
async def startup_event():
    await consume()
