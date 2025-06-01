# schemas.py

from datetime import datetime
from pydantic import BaseModel, EmailStr

# Esquema para crear un doctor (ya lo tenías):
class DoctorCreate(BaseModel):
    nombre: str
    especialidad: str
    correo: EmailStr
    password: str
    clinic_name: str

# Esquema para serializar la respuesta después de crear un doctor:
class DoctorOut(BaseModel):
    id: int
    nombre: str
    especialidad: str
    correo: EmailStr
    creado_el: datetime
    clinic_name: str

    class Config:
        from_attributes = True  # mapea directamente atributos del modelo SQLAlchemy

# Esquema para el token:
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    correo: EmailStr | None = None

class DoctorLogin(BaseModel):
    correo: EmailStr
    password: str

class DoctorProfile(BaseModel):
    nombre: str
    clinic_name: str

    class Config:
        from_attributes = True
