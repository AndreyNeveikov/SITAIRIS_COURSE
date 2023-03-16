from fastapi import APIRouter, Request

from services import StatisticService


class StatisticsRouter:
    @property
    def router(self):
        api_router = APIRouter(prefix='/statistics', tags=['statistics'])

        @api_router.get('/{page_id}')
        async def get_statistics(request: Request, page_id):
            print(request.state.user_uuid)
            return StatisticService.get_statistics(page_id)

        return api_router
