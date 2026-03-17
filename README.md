# 🚗 Garage API

API для управления автопарком. Учебный проект для демонстрации навыков тестирования API, работы с базами данных и Docker.

## 📋 О проекте

Проект моделирует работу небольшого гаража:
- **Автомобили** — добавление, хранение, изменение статуса
- **Водители** — регистрация, привязка к автомобилям
- **Права** — категории (B, C, D) для водителей

Все сущности связаны между собой, что позволяет тестировать сложные сценарии.

## 🛠 Технологии

- **Python 3.14** + **FastAPI** — само API
- **PostgreSQL 17** — база данных
- **SQLAlchemy** — ORM для работы с БД
- **Docker** + **Docker Compose** — контейнеризация
- **pgAdmin** — управление базой (опционально)

## 🚀 Запуск одной командой (Docker)

Самый простой способ запустить проект:

```bash
docker-compose up --build
После запуска:

API доступно по адресу http://localhost:8000

Документация Swagger: http://localhost:8000/docs

База данных PostgreSQL на порту 5432 (логин: postgres, пароль: postgres)

Остановить:

bash
docker-compose down
Если нужно полностью пересоздать базу:

bash
docker-compose down -v
docker-compose up --build
🔧 Запуск вручную (без Docker)
Если хочешь запустить без контейнеров:

Подними PostgreSQL (любым способом)

Создай виртуальное окружение:

bash
python -m venv venv
venv\Scripts\activate  # для Windows
Установи зависимости:

bash
pip install -r requirements.txt
Запусти сервер:

bash
uvicorn main:app --reload
Открой http://127.0.0.1:8000/docs

📚 Эндпоинты
Автомобили (/cars)
Метод	Эндпоинт	Описание
POST	/cars/	Создать машину
GET	/cars/	Список всех машин
GET	/cars/{id}	Получить машину по ID
PUT	/cars/{id}	Обновить машину
DELETE	/cars/{id}	Удалить машину
Водители (/drivers)
Метод	Эндпоинт	Описание
POST	/drivers/	Создать водителя
GET	/drivers/	Список всех водителей
GET	/drivers/{id}	Получить водителя по ID
PUT	/drivers/{id}	Обновить водителя
DELETE	/drivers/{id}	Удалить водителя
Права (/licenses)
Метод	Эндпоинт	Описание
POST	/licenses/	Создать запись о правах
GET	/licenses/	Список всех прав
GET	/licenses/{id}	Получить права по ID
PUT	/licenses/{id}	Обновить права
DELETE	/licenses/{id}	Удалить права
🗄 Структура базы данных
sql
cars: id, brand, year, status, license_category, image_url, color
drivers: id, first_name, last_name, middle_name, age, car_id, license_id
driver_licenses: id, has_b, has_c, has_d
Связи:

drivers.car_id → cars.id (водитель может быть привязан к машине)

drivers.license_id → driver_licenses.id (водитель имеет права)

📝 Примеры запросов
Создать машину
json
POST /cars/
{
  "brand": "Toyota Camry",
  "year": 2020,
  "status": "free",
  "license_category": "B",
  "color": "black"
}
Создать водителя
json
POST /drivers/
{
  "first_name": "Иван",
  "last_name": "Петров",
  "age": 35,
  "license_id": 1
}
Создать права
json
POST /licenses/
{
  "has_b": true,
  "has_c": false,
  "has_d": false
}
👨‍💻 Автор
Владимир

Email: vladimir_k_a@bk.ru

Telegram: @Kuzmich0

GitHub: MrKuzmin

📄 Лицензия
Проект создан в учебных целях. Свободно для использования и модификации.