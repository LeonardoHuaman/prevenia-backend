# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, crud, auth
from database import SessionLocal, engine
from jose import JWTError

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Hospitalaria 🏥")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API del Prevenia "}


#================DOCTOR ROUTES================#

@app.post("/register/doctor", response_model=schemas.DoctorOut)
def register_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    if crud.get_doctor_by_email(db, doctor.correo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un doctor con ese correo"
        )
    nuevo = crud.create_doctor(db, doctor)
    return nuevo

@app.post("/login/doctor", response_model=schemas.Token)
def login_doctor(form_data: schemas.DoctorCreate, db: Session = Depends(get_db)):
    # Usamos correo + password del mismo schema para simplificar
    db_doc = crud.get_doctor_by_email(db, form_data.correo)
    if not db_doc or not auth.verify_password(form_data.password, db_doc.hashed_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token({"sub": db_doc.correo})
    return {"access_token": token, "token_type": "bearer"}
