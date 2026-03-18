from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "postgresql://postgres:postgres@db:5432/garage"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Car(Base):
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    license_category = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    color = Column(String, nullable=True)
    
    driver = relationship("Driver", back_populates="car", uselist=False)
    
    __table_args__ = (
        CheckConstraint('year >= 1950 AND year <= 2100', name='check_year_range'),
        CheckConstraint("status IN ('free', 'busy', 'broken')", name='check_status'),
        CheckConstraint("license_category IN ('B', 'C', 'D')", name='check_license_category'),
    )

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    age = Column(Integer, nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=True)
    license_id = Column(Integer, ForeignKey("driver_licenses.id"), nullable=True, unique=True)
    
    car = relationship("Car", back_populates="driver")
    license = relationship("DriverLicense", back_populates="driver", uselist=False)

class DriverLicense(Base):
    __tablename__ = "driver_licenses"
    
    id = Column(Integer, primary_key=True, index=True)
    has_b = Column(Boolean, nullable=False, default=False)
    has_c = Column(Boolean, nullable=False, default=False)
    has_d = Column(Boolean, nullable=False, default=False)
    
    driver = relationship("Driver", back_populates="license", uselist=False)