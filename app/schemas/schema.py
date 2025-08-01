from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class PostCreateSchema(BaseModel):
    title: str
    content: str
    published: bool = True
    class Config:
        from_attributes = True

class PostResponseSchema(PostCreateSchema):
    id: int
    created_at: datetime
    rating: int
    user_id: int
    image_url:  Optional[str]
    class Config:
        from_attributes = True



class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    class Config:
        from_attributes = True

class UserUpdateSchema(UserCreateSchema):
    email: EmailStr = Field(exclude=True)
    password: str
    class Config:
        from_attributes = True

class UserResponseSchema(UserCreateSchema):
    created_at: datetime
    id: int
    password: str = Field(exclude=True)
    class Config:
        from_attributes = True