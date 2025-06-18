from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str]

class ContactCreate(ContactBase): pass
class ContactUpdate(ContactBase): pass

class ContactResponse(ContactBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    avatar_url: Optional[str]
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    avatar_url: Optional[str]

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None