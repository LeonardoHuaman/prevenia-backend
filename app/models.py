from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Doctor(Base):
    __tablename__ = "doctor"
    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String, index=True)
    correo      = Column(String, unique=True, index=True)
    hashed_pw   = Column(String)
    clinic_name = Column(String)

    # Un doctor puede tener muchos pacientes:
    pacientes = relationship("Paciente", back_populates="doctor")


class Paciente(Base):
    __tablename__ = "paciente"
    id        = Column(Integer, primary_key=True, index=True)
    dni       = Column(String, unique=True, index=True)
    nombres   = Column(String, index=True)
    apellidos = Column(String, index=True)
    edad      = Column(Integer)
    celular   = Column(String)
    correo    = Column(String, unique=True, index=True)
    foto      = Column(String, nullable=True)  # ruta o filename de la foto

    # Clave foránea hacia Doctor:
    doctor_id = Column(Integer, ForeignKey("doctor.id"), nullable=False)

    # Cada paciente pertenece a un doctor:
    doctor = relationship("Doctor", back_populates="pacientes")
