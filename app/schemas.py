from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class MemeBase(BaseModel):
    title: str
    description: str

class MemeCreate(MemeBase):
    image_data: str = Field(..., alias="image_data")

class MemeUpdate(MemeBase):
    image_data: str

class Meme(MemeBase):
    id: int
    file_name: Optional[str]

    class Config:
        orm_mode = True
