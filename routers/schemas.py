from typing import Optional
from pydantic import BaseModel


class TodoRequest(BaseModel):
    title: str
    description: str
    priority: int
    completed: bool


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: int
    completed: bool
    user_id: Optional[int]

    class Config:
        orm_mode = True


class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    # hash_password: str

    class Config:
        orm_mode = True




