# models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Doctor(Base):
    __tablename__ = "doctor"
    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String, nullable=False)
    especialidad= Column(String, nullable=False)
    correo      = Column(String, unique=True, index=True, nullable=False)
    hashed_pw   = Column(String, nullable=False)
    creado_el   = Column(DateTime, default=datetime.utcnow)
