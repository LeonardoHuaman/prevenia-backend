from datetime import datetime
from pydantic import BaseModel, EmailStr

class DoctorCreate(BaseModel):
    nombre: str
    especialidad: str
    correo: EmailStr
    password: str

class DoctorOut(BaseModel):
    id: int
    nombre: str
    especialidad: str
    correo: EmailStr
    creado_el: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    correo: EmailStr | None = None
