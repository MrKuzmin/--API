from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import database
import schemas

# Создаём таблицы в базе данных (если их ещё нет)
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Garage API",
    description="Базовое API для управления автопарком. Только CRUD операции.",
    version="1.0.0",
    contact={
        "name": "Владимир",
        "email": "vladimir_k_a@bk.ru",
        "url": "https://t.me/Kuzmich0"
    }
)

# Зависимость для получения сессии базы данных
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== АВТОМОБИЛИ ====================

@app.post("/cars/", response_model=schemas.Car, status_code=201)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    """Создать новую машину"""
    db_car = database.Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


@app.get("/cars/", response_model=List[schemas.Car])
def read_cars(db: Session = Depends(get_db)):
    """Получить список всех машин"""
    return db.query(database.Car).all()


@app.get("/cars/{car_id}", response_model=schemas.Car)
def read_car(car_id: int, db: Session = Depends(get_db)):
    """Получить машину по ID"""
    car = db.query(database.Car).filter(database.Car.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    return car


@app.put("/cars/{car_id}", response_model=schemas.Car)
def update_car(car_id: int, car: schemas.CarCreate, db: Session = Depends(get_db)):
    """Обновить машину"""
    db_car = db.query(database.Car).filter(database.Car.id == car_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    
    for key, value in car.dict().items():
        setattr(db_car, key, value)
    
    db.commit()
    db.refresh(db_car)
    return db_car


@app.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    """Удалить машину"""
    db_car = db.query(database.Car).filter(database.Car.id == car_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    
    db.delete(db_car)
    db.commit()
    return None


# ==================== ВОДИТЕЛИ ====================

@app.post("/drivers/", response_model=schemas.Driver, status_code=201)
def create_driver(driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    """Создать нового водителя"""
    db_driver = database.Driver(**driver.dict())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver


@app.get("/drivers/", response_model=List[schemas.Driver])
def read_drivers(db: Session = Depends(get_db)):
    """Получить список всех водителей"""
    return db.query(database.Driver).all()


@app.get("/drivers/{driver_id}", response_model=schemas.Driver)
def read_driver(driver_id: int, db: Session = Depends(get_db)):
    """Получить водителя по ID"""
    driver = db.query(database.Driver).filter(database.Driver.id == driver_id).first()
    if driver is None:
        raise HTTPException(status_code=404, detail="Водитель не найдена")
    return driver


@app.put("/drivers/{driver_id}", response_model=schemas.Driver)
def update_driver(driver_id: int, driver: schemas.DriverCreate, db: Session = Depends(get_db)):
    """Обновить данные водителя"""
    db_driver = db.query(database.Driver).filter(database.Driver.id == driver_id).first()
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Водитель не найдена")
    
    for key, value in driver.dict().items():
        setattr(db_driver, key, value)
    
    db.commit()
    db.refresh(db_driver)
    return db_driver


@app.delete("/drivers/{driver_id}", status_code=204)
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    """Удалить водителя"""
    db_driver = db.query(database.Driver).filter(database.Driver.id == driver_id).first()
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Водитель не найдена")
    
    db.delete(db_driver)
    db.commit()
    return None


# ==================== ПРАВА ====================

@app.post("/licenses/", response_model=schemas.DriverLicense, status_code=201)
def create_license(license: schemas.LicenseCreate, db: Session = Depends(get_db)):
    """Создать запись о правах"""
    db_license = database.DriverLicense(**license.dict())
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license


@app.get("/licenses/", response_model=List[schemas.DriverLicense])
def read_licenses(db: Session = Depends(get_db)):
    """Получить список всех прав"""
    return db.query(database.DriverLicense).all()


@app.get("/licenses/{license_id}", response_model=schemas.DriverLicense)
def read_license(license_id: int, db: Session = Depends(get_db)):
    """Получить права по ID"""
    license = db.query(database.DriverLicense).filter(database.DriverLicense.id == license_id).first()
    if license is None:
        raise HTTPException(status_code=404, detail="Права не найдены")
    return license


@app.put("/licenses/{license_id}", response_model=schemas.DriverLicense)
def update_license(license_id: int, license: schemas.LicenseCreate, db: Session = Depends(get_db)):
    """Обновить данные о правах"""
    db_license = db.query(database.DriverLicense).filter(database.DriverLicense.id == license_id).first()
    if db_license is None:
        raise HTTPException(status_code=404, detail="Права не найдены")
    
    for key, value in license.dict().items():
        setattr(db_license, key, value)
    
    db.commit()
    db.refresh(db_license)
    return db_license


@app.delete("/licenses/{license_id}", status_code=204)
def delete_license(license_id: int, db: Session = Depends(get_db)):
    """Удалить запись о правах"""
    db_license = db.query(database.DriverLicense).filter(database.DriverLicense.id == license_id).first()
    if db_license is None:
        raise HTTPException(status_code=404, detail="Права не найдены")
    
    db.delete(db_license)
    db.commit()
    return None