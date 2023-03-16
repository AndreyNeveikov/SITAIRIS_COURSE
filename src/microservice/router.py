from fastapi import APIRouter, Request

from services import StatisticService


class StatisticsRouter:
    @property
    def router(self):
        api_router = APIRouter(prefix='/statistics', tags=['statistics'])

        @api_router.get('/')
        async def get_statistics(request: Request):
            user_uuid = request.state.user_uuid
            statistics = StatisticService.get_statistics(user_uuid)
            return statistics

        return api_router
