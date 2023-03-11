import asyncio

from fastapi import FastAPI

from consume import consume
from router import StatisticsRouter
# from schemas import StatisticsDomain
from services import StatisticsRepository

app = FastAPI()

# statistics_repository = StatisticsRepository()
# statistics_domain = StatisticsDomain(statistics_repository)
# statistics_router = StatisticsRouter(statistics_domain)

app.include_router(StatisticsRouter().router)


#
# @app.get("/api/v1/statistics/{page_id}")
# def get_statistics():
#     return {"Hello": "World"}
#
# @app.on_event('startup')
# async def startup():
#     await consume()

#
@app.on_event('startup')
async def startup():
    await consume()
