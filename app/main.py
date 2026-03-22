from fastapi import FastAPI, Request, HTTPException, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
import re

from . import database
from . import schemas

# ==================== НАСТРОЙКА ПРИЛОЖЕНИЯ ====================

app = FastAPI(
    title="Garage (Парковка МКД)",
    version="1.0.0",
    contact={
        "name": "Владимир",
        "email": "vladimir_k_a@bk.ru",
        "url": "https://t.me/Kuzmich0"
    }
)

app.add_middleware(SessionMiddleware, secret_key="your-secret-key-here")

# Подключаем шаблоны
templates = Jinja2Templates(directory="templates")

# Подключаем статику (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==================== ЗАВИСИМОСТИ ====================

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== СТРАНИЦЫ ====================

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    residents = db.query(database.Resident).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "residents": residents
    })


@app.get("/admin-login")
def admin_login_form(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.get("/resident/{resident_id}")
def resident_dashboard(
    request: Request,
    resident_id: int,
    db: Session = Depends(get_db)
):
    if request.session.get("resident_id") != resident_id:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    
    resident = db.query(database.Resident).filter(database.Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Жилец не найден")
    
    cars = db.query(database.Car).filter(database.Car.owner_id == resident_id).all()
    trips = db.query(database.ParkingLog).filter(database.ParkingLog.driver_id == resident_id).order_by(database.ParkingLog.departure_time.desc()).all()
    parked_count = db.query(database.Car).filter(database.Car.status == "parked").count()
    free_spots = 100 - parked_count
    
    return templates.TemplateResponse("resident_dashboard.html", {
        "request": request,
        "resident": resident,
        "cars": cars,
        "trips": trips,
        "free_spots": free_spots
    })


@app.get("/admin-dashboard")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    cars = db.query(database.Car).all()
    residents = db.query(database.Resident).all()
    parked_count = db.query(database.Car).filter(database.Car.status == "parked").count()
    free_spots = 100 - parked_count
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "cars": cars,
        "residents": residents,
        "free_spots": free_spots
    })


# ==================== АВТОРИЗАЦИЯ ====================

@app.post("/auth/resident")
async def auth_resident(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        phone = data.get("phone", "")
    except:
        form = await request.form()
        phone = form.get("phone", "")
    
    print(f"=== ПОЛУЧЕН ТЕЛЕФОН: '{phone}'")
    
    if not phone or phone.strip() == "":
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Введите номер телефона"
        })
    
    if not re.match(r"^\+\d{11,15}$", phone):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Неверный формат номера. Пример: +79001234567"
        })
    
    resident = db.query(database.Resident).filter(database.Resident.phone == phone).first()
    if resident:
        request.session["resident_id"] = resident.id
        request.session["role"] = resident.role
        return RedirectResponse(url=f"/resident/{resident.id}", status_code=303)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "error": "Жилец с таким номером не найден"
    })


@app.post("/auth/admin")
async def auth_admin(request: Request):
    try:
        data = await request.json()
        login = data.get("login", "")
        password = data.get("password", "")
    except:
        form = await request.form()
        login = form.get("login", "")
        password = form.get("password", "")
    
    print(f"=== ВХОД АДМИНА: login='{login}', password='{password}'")
    
    if not login or not password:
        return templates.TemplateResponse("admin_login.html", {
            "request": request,
            "error": "Введите логин и пароль"
        })
    
    if login == "admin" and password == "admin":
        request.session["role"] = "admin"
        return RedirectResponse(url="/admin-dashboard", status_code=303)
    
    return templates.TemplateResponse("admin_login.html", {
        "request": request,
        "error": "Неверный логин или пароль"
    })


# ==================== УПРАВЛЕНИЕ МАШИНАМИ ====================

@app.get("/admin/car/add")
def add_car_form(request: Request, db: Session = Depends(get_db)):
    residents = db.query(database.Resident).all()
    return templates.TemplateResponse("car_form.html", {
        "request": request,
        "residents": residents,
        "title": "Добавить машину",
        "action": "/cars"
    })


@app.post("/cars")
def create_car(
    request: Request,
    plate: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    color: str = Form(...),
    owner_id: int = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(database.Car).filter(database.Car.plate == plate).first()
    if existing:
        raise HTTPException(status_code=400, detail="Машина с таким номером уже существует")
    
    parked_count = db.query(database.Car).filter(database.Car.status == "parked").count()
    status = "parked" if parked_count < 100 else "away"
    
    car = database.Car(
        plate=plate,
        brand=brand,
        model=model,
        color=color,
        owner_id=owner_id,
        status=status
    )
    db.add(car)
    db.commit()
    db.refresh(car)
    
    return RedirectResponse(url="/admin-dashboard", status_code=303)


@app.post("/cars/{car_id}")
def update_car(
    request: Request,
    car_id: int,
    plate: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    color: str = Form(...),
    owner_id: int = Form(...),
    db: Session = Depends(get_db)
):
    car = db.query(database.Car).filter(database.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    
    if car.plate != plate:
        existing = db.query(database.Car).filter(database.Car.plate == plate).first()
        if existing:
            raise HTTPException(status_code=400, detail="Машина с таким номером уже существует")
    
    car.plate = plate
    car.brand = brand
    car.model = model
    car.color = color
    car.owner_id = owner_id
    db.commit()
    
    return RedirectResponse(url="/admin-dashboard", status_code=303)


@app.post("/admin/car/delete/{car_id}")
def delete_car(
    request: Request,
    car_id: int,
    db: Session = Depends(get_db)
):
    car = db.query(database.Car).filter(database.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    
    if car.status == "away":
        raise HTTPException(status_code=400, detail="Нельзя удалить машину, которая в поездке")
    
    db.delete(car)
    db.commit()
    
    return RedirectResponse(url="/admin-dashboard", status_code=303)


# ==================== УПРАВЛЕНИЕ ЖИЛЬЦАМИ ====================

@app.get("/admin/resident/add")
def add_resident_form(request: Request):
    return templates.TemplateResponse("resident_form.html", {
        "request": request,
        "title": "Добавить жильца",
        "action": "/residents"
    })


@app.post("/residents")
def create_resident(
    request: Request,
    full_name: str = Form(...),
    apartment: str = Form(...),
    birth_date: str = Form(...),
    has_license: bool = Form(False),
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(database.Resident).filter(database.Resident.phone == phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Жилец с таким номером уже существует")
    
    resident = database.Resident(
        full_name=full_name,
        apartment=apartment,
        birth_date=birth_date,
        has_license=has_license,
        phone=phone
    )
    db.add(resident)
    db.commit()
    db.refresh(resident)
    
    return RedirectResponse(url="/admin-dashboard", status_code=303)


@app.post("/residents/{resident_id}")
def update_resident(
    request: Request,
    resident_id: int,
    full_name: str = Form(...),
    apartment: str = Form(...),
    birth_date: str = Form(...),
    has_license: bool = Form(False),
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    resident = db.query(database.Resident).filter(database.Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Жилец не найден")
    
    if resident.phone != phone:
        existing = db.query(database.Resident).filter(database.Resident.phone == phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="Жилец с таким номером уже существует")
    
    resident.full_name = full_name
    resident.apartment = apartment
    resident.birth_date = birth_date
    resident.has_license = has_license
    resident.phone = phone
    db.commit()
    
    return RedirectResponse(url="/admin-dashboard", status_code=303)


@app.post("/admin/resident/delete/{resident_id}")
def delete_resident(
    request: Request,
    resident_id: int,
    db: Session = Depends(get_db)
):
    resident = db.query(database.Resident).filter(database.Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Жилец не найден")
    
    cars = db.query(database.Car).filter(database.Car.owner_id == resident_id).count()
    if cars > 0:
        raise HTTPException(status_code=400, detail="Нельзя удалить жильца, у которого есть машины")
    
    db.delete(resident)
    db.commit()
    
    return RedirectResponse(url="/admin-dashboard", status_code=303)


# ==================== ВЫЕЗД / ВЪЕЗД ====================

@app.post("/exit")
def exit_car(
    request: Request,
    car_id: int = Form(...),
    driver_id: int = Form(...),
    db: Session = Depends(get_db)
):
    car = db.query(database.Car).filter(database.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    
    if car.status != "parked":
        raise HTTPException(status_code=400, detail="Машина уже в поездке")
    
    driver = db.query(database.Resident).filter(database.Resident.id == driver_id).first()
    if not driver or not driver.has_license:
        raise HTTPException(status_code=400, detail="У водителя нет прав")
    
    age = datetime.now().year - driver.birth_date.year
    if age < 18:
        raise HTTPException(status_code=400, detail="Водитель младше 18 лет")
    
    active_trip = db.query(database.ParkingLog).filter(
        database.ParkingLog.driver_id == driver_id,
        database.ParkingLog.return_time.is_(None)
    ).first()
    if active_trip:
        raise HTTPException(status_code=400, detail="Водитель уже в поездке")
    
    trip = database.ParkingLog(
        car_id=car.id,
        driver_id=driver_id,
        departure_time=datetime.now()
    )
    db.add(trip)
    car.status = "away"
    db.commit()
    
    return RedirectResponse(url="/admin-dashboard", status_code=303)

@app.get("/admin/resident/edit/{resident_id}")
def edit_resident_form(
    request: Request,
    resident_id: int,
    db: Session = Depends(get_db)
):
    resident = db.query(database.Resident).filter(database.Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Жилец не найден")
    
    return templates.TemplateResponse("resident_form.html", {
        "request": request,
        "resident": resident,
        "title": "Редактировать жильца",
        "action": f"/residents/{resident_id}"
    })

@app.get("/admin/car/edit/{car_id}")
def edit_car_form(
    request: Request,
    car_id: int,
    db: Session = Depends(get_db)
):
    car = db.query(database.Car).filter(database.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    
    residents = db.query(database.Resident).all()
    return templates.TemplateResponse("car_form.html", {
        "request": request,
        "car": car,
        "residents": residents,
        "title": "Редактировать машину",
        "action": f"/cars/{car_id}"
    })

@app.post("/entry")
def entry_car(
    request: Request,
    car_id: int = Form(...),
    db: Session = Depends(get_db)
):
    car = db.query(database.Car).filter(database.Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    
    if car.status != "away":
        raise HTTPException(status_code=400, detail="Машина не в поездке")
    
    parked_count = db.query(database.Car).filter(database.Car.status == "parked").count()
    if parked_count >= 100:
        raise HTTPException(status_code=400, detail="Нет свободных мест")
    
    trip = db.query(database.ParkingLog).filter(
        database.ParkingLog.car_id == car_id,
        database.ParkingLog.return_time.is_(None)
    ).order_by(database.ParkingLog.departure_time.desc()).first()
    
    if not trip:
        raise HTTPException(status_code=400, detail="Нет открытой поездки для этой машины")
    
    trip.return_time = datetime.now()
    car.status = "parked"
    db.commit()
    
    return RedirectResponse(url="/admin-dashboard", status_code=303)