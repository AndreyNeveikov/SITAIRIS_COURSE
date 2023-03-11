from fastapi import APIRouter

from services import StatisticService
from schemas import PageModel


# class StatisticsRouter:
#     def __init__(self, statistics_domain: StatisticsDomain):
#         self.__statistics_domain = statistics_domain
#
#     @property
#     def router(self):
#         api_router = APIRouter(prefix='/statistics', tags=['statistics'])
#
#         @api_router.get('/get/{page_id}')
#         def get_page_statistic(page_id: str):
#             return self.__statistics_domain.get_item(page_id)
#
#         @api_router.post('/create/')
#         def create_page_statistic(page_model: PageModel):
#             return self.__statistics_domain.put_item(dict(page_model))
#
#         return api_router


class StatisticsRouter:
    @property
    def router(self):
        api_router = APIRouter(prefix='/statistics', tags=['statistics'])

        @api_router.get('/{page_id}')
        async def get_statistics(page_id):
            return StatisticService.get_statistics(page_id)

        @api_router.post('/')
        async def create_statistics(page_model: PageModel):
            return StatisticService.create_statistics(dict(page_model))

        return api_router
