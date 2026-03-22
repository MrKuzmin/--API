from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/garage")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    apartment = Column(String(10), nullable=False)
    birth_date = Column(Date, nullable=False)
    has_license = Column(Boolean, default=False)
    phone = Column(String(20), unique=True, nullable=False)
    role = Column(String(20), default="resident")


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String(10), unique=True, nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    color = Column(String(30), nullable=False)
    status = Column(String(20), default="parked")  # parked / away
    owner_id = Column(Integer, ForeignKey("residents.id"), nullable=False)

    owner = relationship("Resident")


class ParkingLog(Base):
    __tablename__ = "parking_log"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("residents.id"), nullable=False)
    departure_time = Column(DateTime, default=datetime.now)
    return_time = Column(DateTime, nullable=True)

    car = relationship("Car")
    driver = relationship("Resident", foreign_keys=[driver_id])