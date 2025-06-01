from sqlalchemy.orm import Session
import models as models, schemas, auth as auth

def get_doctor_by_email(db: Session, correo: str):
    return db.query(models.Doctor).filter(models.Doctor.correo == correo).first()

def create_doctor(db: Session, doc: schemas.DoctorCreate):
    hashed = auth.hash_password(doc.password)
    db_doc = models.Doctor(
        nombre=doc.nombre,
        especialidad=doc.especialidad,
        correo=doc.correo,
        hashed_pw=hashed,
        clinic_name  = doc.clinic_name
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


