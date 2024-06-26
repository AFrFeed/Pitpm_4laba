
import datetime
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Date, UniqueConstraint, PrimaryKeyConstraint, ForeignKey,Float, DateTime
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import declarative_base

app = FastAPI()

# Настройка базы данных MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://isp_p_Frolov:12345@77.91.86.135/isp_p_Frolov"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Определение модели SQLAlchemy для диагностики
class Diagnostic(Base):
    __tablename__ = "diagnostic"
    id = Column(Integer, primary_key=True, index=True)
    code_diagnostic_id = Column(Integer, index=True)
    name = Column(String(30), unique=True, index=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='diagnostic_pk'),
        UniqueConstraint('code_diagnostic_id'),
    )


Base.metadata.create_all(bind=engine)


# Определение модели SQLAlchemy для доктора
class Doctor(Base):
    __tablename__ = "doctor"
    id = Column(Integer, primary_key=True, index=True)
    FIO = Column(String(30), unique=True, index=True)
    category = Column(Integer, unique=True, index=True)
    speciality = Column(String(30), unique=True, index=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='doctor_pk'),
        UniqueConstraint('category'),
    )


Base.metadata.create_all(bind=engine)


# Определение модели SQLAlchemy для пациента
class Patient(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, index=True)
    medical_card_number = Column(String(50), index=True)
    FIO = Column(String(100), unique=True, index=True)
    date_of_birth = Column(Date(), nullable=False)
    address = Column(String(100), unique=True, index=True)
    gender = Column(String(50), index=True)
    discount = Column(Float(2), index=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='patient_pk'),
        UniqueConstraint('medical_card_number'),
    )


Base.metadata.create_all(bind=engine)


# Определение модели SQLAlchemy для приема
class Reception(Base):
    __tablename__ = "reception"

    id = Column(Integer, primary_key=True, index=True)
    coupon_number = Column(Integer, index=True)
    visit_purpose = Column(DateTime, index=True)
    date_reception = Column(DateTime, nullable=False)
    price = Column(Float(2), index=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='reception_pk'),
        UniqueConstraint('coupon_number'),
    )


Base.metadata.create_all(bind=engine)
# Создание таблиц в базе данных



# Определение Pydantic моделей для валидации данных
class DiagnosticCreate(BaseModel):
    code_diagnostic_id: int
    name: str

class DiagnosticResponse(BaseModel):
    id: int
    code_diagnostic_id: int
    name: str

    class Config:
        orm_mode = True

class DiagnosticReception(BaseModel):
    code_diagnostic_id: int
    name: str

class DiagnosticReceptionResponse(BaseModel):
    id: int
    code_diagnostic_id: int
    name: str

    class Config:
        orm_mode = True

class DoctorCreate(BaseModel):
    FIO: str
    category: int
    speciality: str

class DoctorResponse(BaseModel):
    id: int
    FIO: str
    category: int
    speciality: str

    class Config:
        orm_mode = True
class PatientCreate(BaseModel):
    medical_card_number: str
    FIO: str
    date_of_birth: datetime.datetime
    address: str
    gender: str
    discount: int

class PatientResponse(BaseModel):
    id: int
    medical_card_number: str
    FIO: str
    date_of_birth: datetime.date
    address: str
    gender: str
    discount: float

    class Config:
        orm_mode = True

class ReceptionCreate(BaseModel):
    coupon_number: int
    visit_purpose: datetime.datetime
    date_reception: datetime.datetime
    price: int

class ReceptionResponse(BaseModel):
    id: int
    coupon_number: int
    visit_purpose: datetime.datetime
    date_reception: datetime.datetime
    price: float

    class Config:
        orm_mode = True

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Маршрут для создания нового диагноза
@app.post("/diagnostics/", response_model=DiagnosticResponse)
def create_diagnostic(code_diagnostic_id: int,name: str, db: Session = Depends(get_db)):
    new_diagnostic = Diagnostic(code_diagnostic_id=code_diagnostic_id,name=name)
    try:
        db.add(new_diagnostic)
        db.commit()
        db.refresh(new_diagnostic)
        return new_diagnostic
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Diagnostic already registered")


# Маршрут для создания нового доктора
@app.post("/doctors/", response_model=DoctorResponse)
def create_doctor(FIO: str, category: int, speciality: str, db: Session = Depends(get_db)):
    new_doctor = Doctor(FIO=FIO, category=category, speciality=speciality)
    try:
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)
        return new_doctor
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="doctor already registered")


# Маршрут для создания нового пациента
@app.post("/patients/", response_model=PatientResponse)
def create_patient( medical_card_number: str, FIO: str,date_of_birth: datetime.date, address: str, gender: str,discount: float, db: Session = Depends(get_db)):
    new_patient = Patient(FIO=FIO, medical_card_number=medical_card_number, date_of_birth=date_of_birth, address=address, gender=gender, discount=discount)
    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Patient already registered")


# Маршрут для создания нового приема
@app.post("/receptions/", response_model=ReceptionResponse)
def create_reception(coupon_number: int, visit_purpose: datetime.datetime, date_reception: datetime.datetime, price: float, db: Session = Depends(get_db)):
    new_reception = Reception(coupon_number=coupon_number, visit_purpose=visit_purpose, date_reception=date_reception, price=price)
    try:
        db.add(new_reception)
        db.commit()
        db.refresh(new_reception)
        return new_reception
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Reception already registered")


# Маршрут для получения диагноза по идентификатору
@app.get("/diagnostics/{diagnostic_id}", response_model=DiagnosticResponse)
def get_diagnostic(diagnostic_id: int, db: Session = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if diagnostic is None:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    return diagnostic

# Маршрут для обновления информации о диагнозе
@app.put("/diagnostics/{diagnostic_id}", response_model=DiagnosticResponse)
def update_diagnostic(diagnostic_id: int, diagnostic_data: DiagnosticReception, db: Session = Depends(get_db)):
    db_diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not db_diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    for key, value in diagnostic_data.dict().items():
        setattr(db_diagnostic, key, value)
    db.commit()
    db.refresh(db_diagnostic)
    return db_diagnostic

# Маршрут для удаления диагноза
@app.delete("/diagnostics/{diagnostic_id}")
def delete_diagnostic(diagnostic_id: int, db: Session = Depends(get_db)):
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    db.delete(diagnostic)
    db.commit()
    return {"message": "Diagnostic deleted successfully"}
@app.get("/doctors/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

# Маршрут для обновления информации о докторе
@app.put("/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int, doctor_data: DoctorCreate, db: Session = Depends(get_db)):
    db_doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for key, value in doctor_data.dict().items():
        setattr(db_doctor, key, value)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

# Маршрут для удаления доктора
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doctor)
    db.commit()
    return {"message": "Doctor deleted successfully"}

# Аналогичные GET, PUT и DELETE запросы для сущности "Patient"
# GET запрос для получения информации о пациенте по идентификатору
@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# PUT запрос для обновления информации о пациенте
@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, patient_data: PatientCreate, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in patient_data.dict().items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient

# DELETE запрос для удаления пациента
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}

# Аналогичные GET, PUT и DELETE запросы для сущности "Reception"
# GET запрос для получения информации о приеме по идентификатору
@app.get("/receptions/{reception_id}", response_model=ReceptionResponse)
def get_reception(reception_id: int, db: Session = Depends(get_db)):
    reception = db.query(Reception).filter(Reception.id == reception_id).first()
    if reception is None:
        raise HTTPException(status_code=404, detail="Reception not found")
    return reception

# PUT запрос для обновления информации о приеме
@app.put("/receptions/{reception_id}", response_model=ReceptionResponse)
def update_reception(reception_id: int, reception_data: ReceptionCreate, db: Session = Depends(get_db)):
    db_reception = db.query(Reception).filter(Reception.id == reception_id).first()
    if not db_reception:
        raise HTTPException(status_code=404, detail="Reception not found")
    for key, value in reception_data.dict().items():
        setattr(db_reception, key, value)
    db.commit()
    db.refresh(db_reception)
    return db_reception

# DELETE запрос для удаления приема
@app.delete("/receptions/{reception_id}")
def delete_reception(reception_id: int, db: Session = Depends(get_db)):
    reception = db.query(Reception).filter(Reception.id == reception_id).first()
    if not reception:
        raise HTTPException(status_code=404, detail="Reception not found")
    db.delete(reception)
    db.commit()
    return {"message": "Reception deleted successfully"}