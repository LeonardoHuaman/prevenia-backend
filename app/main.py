import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models, schemas, crud, auth
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API del Prevenia")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/pacientes", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


### ——— RUTAS PARA DOCTORES ——— ###

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API del Prevenia"}


@app.post("/register/doctor", response_model=schemas.DoctorOut, tags=["Doctors"])
def register_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo doctor.
    Verifica si ya existe un doctor con el mismo correo.
    """
    if crud.get_doctor_by_email(db, doctor.correo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un doctor con ese correo"
        )
    nuevo = crud.create_doctor(db, doctor)
    return nuevo


@app.post("/login/doctor", response_model=schemas.Token, tags=["Doctors"])
def login_doctor(form_data: schemas.DoctorLogin, db: Session = Depends(get_db)):
    """
    Autentica a un doctor (correo + contraseña).
    Si las credenciales son correctas, devuelve un token JWT.
    """
    db_doc = crud.get_doctor_by_email(db, form_data.correo)
    if not db_doc or not auth.verify_password(form_data.password, db_doc.hashed_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token({"sub": db_doc.correo})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/doctors/me", response_model=schemas.DoctorProfile, tags=["Doctors"])
def read_current_doctor(current_doc: models.Doctor = Depends(auth.get_current_doctor)):
    """
    Ruta protegida: devuelve { nombre, clinic_name } del doctor autenticado.
    """
    return current_doc


### ——— RUTAS PARA PACIENTES ——— ###

@app.post(
    "/register/paciente",
    response_model=schemas.PacienteOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Pacientes"]
)
def register_paciente(
    dni: str         = Form(..., description="DNI del paciente"),
    nombres: str     = Form(..., description="Nombres del paciente"),
    apellidos: str   = Form(..., description="Apellidos del paciente"),
    edad: int        = Form(..., description="Edad del paciente"),
    celular: str     = Form(..., description="Número de celular del paciente"),
    correo: str      = Form(..., description="Correo del paciente"),
    foto: UploadFile = File(..., description="Foto del paciente (JPEG/PNG)"),
    db: Session      = Depends(get_db),
    current_doc: models.Doctor = Depends(auth.get_current_doctor)
):
    """
    Crea un nuevo paciente para el doctor autenticado.
    - Recibe campos de texto (dni, nombres, apellidos, edad, celular, correo) vía Form.
    - Recibe la foto como UploadFile (File).
    - Verifica duplicados (DNI y correo).
    - Asigna doctor_id automáticamente usando current_doc.id.
    - Guarda la foto en disco y crea el registro en la base de datos.
    """
    # 1. Verificar duplicados por DNI y correo
    if crud.get_paciente_por_dni(db, dni):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un paciente con ese DNI"
        )
    if crud.get_paciente_por_correo(db, correo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un paciente con ese correo"
        )

    # 2. Construir el Pydantic schema con los datos de formulario + doctor_id
    paciente_data = schemas.PacienteCreate(
        dni=dni,
        nombres=nombres,
        apellidos=apellidos,
        edad=edad,
        celular=celular,
        correo=correo,
        doctor_id=current_doc.id
    )

    # 3. Crear el paciente (el CRUD se encarga de:
    #    - Guardar la foto en 'static/pacientes/'
    #    - Insertar el registro en la BD, incluyendo 'foto' y 'doctor_id')
    nuevo_paciente = crud.create_paciente(db, paciente_data, foto)
    return nuevo_paciente


@app.get(
    "/pacientes/{paciente_id}",
    response_model=schemas.PacienteOut,
    tags=["Pacientes"]
)
def get_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """
    Devuelve los datos de un paciente por su ID.
    Si no existe, lanza un 404.
    """
    paciente = crud.get_paciente_por_id(db, paciente_id)
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    return paciente


@app.get(
    "/pacientes",
    response_model=list[schemas.PacienteOut],
    tags=["Pacientes"]
)
def list_pacientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos los pacientes con paginación básica (skip/limit).
    """
    pacientes = crud.get_pacientes(db, skip=skip, limit=limit)
    return pacientes
