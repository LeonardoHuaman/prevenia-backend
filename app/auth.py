# auth.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional

# FastAPI / SQLAlchemy para la dependencia
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import crud, models
from database import SessionLocal

# ----------------------------------------------------------------
# CONFIGURACIÓN BÁSICA DE JWT Y BCRYPT
# ----------------------------------------------------------------

SECRET_KEY = "super_secreto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_pw: str, hashed_pw: str) -> bool:
    return pwd_context.verify(plain_pw, hashed_pw)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """
    Decodifica el JWT y devuelve el payload si es válido.
    Lanza JWTError en caso de token inválido o expirado.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ----------------------------------------------------------------
# OAuth2PasswordBearer: toma el token del header "Authorization"
# ----------------------------------------------------------------

# tokenUrl debe coincidir con tu ruta de login: "/login/doctor"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/doctor")


# ----------------------------------------------------------------
# DEPENDENCIA QUE PROPORCIONA UNA SESIÓN DE DB
# ----------------------------------------------------------------

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------------
# Función que valida el token y extrae el correo ("sub")
# ----------------------------------------------------------------

def verify_access_token(token: str) -> str:
    """
    - Decodifica y valida el JWT.
    - Extrae "sub" (correo) del payload.
    - Lanza HTTPException(401) si falla la validación.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
        return correo
    except JWTError:
        raise credentials_exception


# ----------------------------------------------------------------
# Dependencia que devuelve el modelo Doctor correspondiente al token
# ----------------------------------------------------------------

def get_current_doctor(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Doctor:
    """
    1. Toma el token JWT del header (OAuth2PasswordBearer).
    2. Lo valida en verify_access_token → retorna el correo.
    3. Busca en BD el doctor con dicho correo.
    4. Si no existe, lanza 401; si existe, lo devuelve.
    """
    correo = verify_access_token(token)
    doctor = crud.get_doctor_by_email(db, correo)
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return doctor
