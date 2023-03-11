from typing import Optional

from pydantic import BaseModel, Field


class PageModel(BaseModel):
    page_id: str = Field(...)
    owner_id: str = Field(...)
    posts: Optional[int] = None
    likes: Optional[int] = None
    followers: Optional[int] = None


# class StatisticsDomain:
#     def __init__(self, repository):
#         self.__repository = repository
#
#     def get_all(self):
#         return self.__repository.get_all()
#
#     def get_item(self, page_id: str):
#         return self.__repository.get_item(page_id)
#
#     def put_item(self, page_id: dict):
#         return self.__repository.put_item(page_id)
#
#     def update_item(self, page_id: str):
#         return self.__repository.update_item(page_id)
#
#     def delete_item(self, page_id: str):
#         return self.__repository.delete_item(page_id)
