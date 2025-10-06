import os
from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String(100), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(50), nullable=False)
    phone = Column(String(50))
    email = Column(String(100))
    address = Column(Text)
    blood_type = Column(String(10))
    allergies = Column(Text)
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(50))
    medical_history = Column(Text)
    current_medications = Column(Text)
    created_date = Column(DateTime, default=datetime.now)

    health_metrics = relationship("HealthMetric", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="patient", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "blood_type": self.blood_type,
            "allergies": self.allergies,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "medical_history": self.medical_history,
            "current_medications": self.current_medications,
            "created_date": self.created_date,
        }


class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String(100), ForeignKey("patients.patient_id"), nullable=False, index=True)
    metric_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    date = Column(DateTime, nullable=False)
    notes = Column(Text)
    category = Column(String(100))

    patient = relationship("Patient", back_populates="health_metrics")

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "metric_type": self.metric_type,
            "value": self.value,
            "unit": self.unit,
            "date": self.date,
            "notes": self.notes,
            "category": self.category,
        }


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String(100), ForeignKey("patients.patient_id"), nullable=False, index=True)
    record_type = Column(String(100), nullable=False)
    description = Column(Text)
    doctor_name = Column(String(100))
    facility_name = Column(String(200))
    record_date = Column(Date, nullable=False)
    file_path = Column(String(500))
    file_name = Column(String(200))
    file_type = Column(String(100))
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.now)

    patient = relationship("Patient", back_populates="medical_records")

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "record_type": self.record_type,
            "description": self.description,
            "doctor_name": self.doctor_name,
            "facility_name": self.facility_name,
            "record_date": self.record_date,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "upload_date": self.upload_date,
        }


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String(100), ForeignKey("patients.patient_id"), index=True)
    patient_name = Column(String(200))
    activity_type = Column(String(100), nullable=False)
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.now, index=True)

    patient = relationship("Patient", back_populates="activities")

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "patient_name": self.patient_name,
            "type": self.activity_type,
            "description": self.description,
            "timestamp": self.timestamp,
            "date": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


def get_engine():
    """Get database engine using DATABASE_URL from environment."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return create_engine(database_url, pool_pre_ping=True)


def get_session():
    """Create and return a new database session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_database():
    """Initialize database tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
