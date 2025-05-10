from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    nivel: str = "principiante"
    posicion_preferida: str = "drive"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    nivel: Optional[str] = None
    posicion_preferida: Optional[str] = None

class UserInDB(UserBase):
    id: str
    fecha_registro: datetime
    ultimo_analisis: Optional[str] = None
    tipo_ultimo_analisis: Optional[str] = None
    fecha_ultimo_analisis: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 