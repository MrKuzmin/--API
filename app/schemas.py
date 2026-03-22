from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional
import re


class ResidentBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    apartment: str = Field(..., min_length=1, max_length=10)
    birth_date: date
    has_license: bool = False
    phone: str = Field(..., min_length=11, max_length=20)

    @field_validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^\+\d{11,15}$", v):
            raise ValueError("Номер телефона должен начинаться с + и содержать только цифры")
        return v


class ResidentCreate(ResidentBase):
    pass


class Resident(ResidentBase):
    id: int
    role: str

    class Config:
        from_attributes = True


class CarBase(BaseModel):
    plate: str = Field(..., min_length=5, max_length=10)
    brand: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    color: str = Field(..., min_length=1, max_length=30)
    owner_id: int


class CarCreate(CarBase):
    pass


class Car(CarBase):
    id: int
    status: str

    class Config:
        from_attributes = True


class ParkingLogBase(BaseModel):
    car_id: int
    driver_id: int


class ParkingLogCreate(ParkingLogBase):
    pass


class ParkingLog(ParkingLogBase):
    id: int
    departure_time: datetime
    return_time: Optional[datetime] = None

    class Config:
        from_attributes = True