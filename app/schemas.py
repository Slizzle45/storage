from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RenameRequest(BaseModel):
    new_name: str = Field(min_length=1)


class EntryInfo(BaseModel):
    name: str
    type: Literal["file", "folder"]
    size: int | None
    modified: datetime


class ListResponse(BaseModel):
    path: str
    entries: list[EntryInfo]
