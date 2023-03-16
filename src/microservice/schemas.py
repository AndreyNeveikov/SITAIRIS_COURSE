from typing import Optional

from pydantic import BaseModel, Field


class PageModel(BaseModel):
    page_id: str = Field(...)
    owner_id: str = Field(...)
    posts: Optional[int] = None
    likes: Optional[int] = None
    followers: Optional[int] = None
