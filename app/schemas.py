from pydantic import BaseModel
from typing import Optional


class LoginSchema(BaseModel):
    email: str
    password: str


class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = ''