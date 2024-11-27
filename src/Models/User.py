from pydantic import BaseModel,Field,EmailStr
from datetime import datetime


class User(BaseModel):
    username : str = Field(min_length=5)
    email: EmailStr
    password : str = Field(min_length=5)
    admin : bool = False

class Login(BaseModel):
    email: EmailStr
    password : str = Field(min_length=5)
    remember_me : bool = False

class Sessiondb(BaseModel):
    username: str
    email : EmailStr
    token: str
    expires_at: datetime | None=None