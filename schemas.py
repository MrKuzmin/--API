from pydantic import BaseModel, Field
from typing import Optional

# ==================== СХЕМЫ ДЛЯ АВТОМОБИЛЕЙ ====================

class CarBase(BaseModel):
    """
    Базовая схема автомобиля.
    Содержит все поля, кроме ID (который генерируется базой).
    """
    brand: str = Field(..., description="Марка автомобиля (например: Toyota, BMW, Lada)", min_length=1, max_length=100)
    year: int = Field(..., description="Год выпуска (от 1950 до 2100)", ge=1950, le=2100)
    status: str = Field(..., description="Статус автомобиля: free - свободна, busy - занята, broken - сломана", 
                        pattern="^(free|busy|broken)$")
    license_category: str = Field(..., description="Необходимая категория прав: B, C или D", 
                                  pattern="^(B|C|D)$")
    image_url: Optional[str] = Field(None, description="Ссылка на фото автомобиля (необязательно)")
    color: Optional[str] = Field(None, description="Цвет автомобиля (необязательно, например: красный, синий, чёрный)")

class CarCreate(CarBase):
    """Схема для создания автомобиля (совпадает с базовой)"""
    pass

class Car(CarBase):
    """Схема для ответа с автомобилем (включает ID)"""
    id: int = Field(..., description="Уникальный идентификатор автомобиля")
    
    class Config:
        from_attributes = True


# ==================== СХЕМЫ ДЛЯ ВОДИТЕЛЕЙ ====================

class DriverBase(BaseModel):
    """Базовая схема водителя"""
    first_name: str = Field(..., description="Имя водителя", min_length=2, max_length=50)
    last_name: str = Field(..., description="Фамилия водителя", min_length=2, max_length=50)
    middle_name: Optional[str] = Field(None, description="Отчество водителя (необязательно)", max_length=50)
    age: int = Field(..., description="Возраст водителя (от 18 до 100)", ge=18, le=100)
    car_id: Optional[int] = Field(None, description="ID автомобиля, на котором ездит водитель (null если не за рулём)")
    license_id: Optional[int] = Field(None, description="ID водительских прав (null если нет прав)")

class DriverCreate(DriverBase):
    """Схема для создания водителя"""
    pass

class Driver(DriverBase):
    """Схема для ответа с водителем"""
    id: int = Field(..., description="Уникальный идентификатор водителя")
    
    class Config:
        from_attributes = True


# ==================== СХЕМЫ ДЛЯ ПРАВ ====================

class LicenseBase(BaseModel):
    """Базовая схема водительских прав"""
    has_b: bool = Field(False, description="Наличие категории B")
    has_c: bool = Field(False, description="Наличие категории C")
    has_d: bool = Field(False, description="Наличие категории D")

class LicenseCreate(LicenseBase):
    """Схема для создания прав"""
    pass

class DriverLicense(LicenseBase):
    """Схема для ответа с правами"""
    id: int = Field(..., description="Уникальный номер водительского удостоверения")
    
    class Config:
        from_attributes = True