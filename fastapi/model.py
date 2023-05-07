from pydantic import BaseModel
from typing import List, Union


class UrlItem(BaseModel):
    url: str


class TextItem(BaseModel):
    text: str


class CommentItem(BaseModel):
    userName: str
    contents: str
    sympathyCount: int
    antipathyCount: int


class CommentList(BaseModel):
    comments: List[CommentItem]