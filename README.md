# Todo API

Бэкенд для списка задач на FastAPI с JWT-авторизацией. Каждый пользователь видит только свои задачи.

## Стек
FastAPI, SQLAlchemy 2, Alembic, SQLite (меняется через `DATABASE_URL`), PyJWT, Argon2 (pwdlib), pytest, ruff.

## Запуск

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-dev.txt   # для продакшена достаточно requirements.txt
copy .env.example .env                # и задайте SECRET_KEY
alembic upgrade head                  # создать/обновить таблицы
uvicorn app.main:app --reload
```

Документация (Swagger): http://127.0.0.1:8000/docs. Кнопка **Authorize** позволяет залогиниться прямо там.

## Миграции

Схема БД управляется через Alembic. После изменения моделей в `app/models.py`:

```powershell
alembic revision --autogenerate -m "add priority to todos"   # создать миграцию
# проверить сгенерированный файл в alembic/versions/
alembic upgrade head                                          # применить
alembic downgrade -1                                          # откатить последнюю
```

Тест `tests/test_migrations.py` падает, если модели изменили, а миграцию забыли создать.

## Эндпоинты

| Метод | Путь | Авторизация | Описание |
|---|---|---|---|
| GET | `/health` | — | проверка работоспособности |
| POST | `/auth/register` | — | регистрация (`{"username", "password"}`) |
| POST | `/auth/login` | — | логин (form-data `username`, `password`) → `access_token` |
| GET | `/auth/me` | ✔ | текущий пользователь |
| POST | `/todos` | ✔ | создать задачу |
| GET | `/todos` | ✔ | список: `?is_done=`, `?q=` (поиск), `?limit=`, `?offset=` |
| GET | `/todos/{id}` | ✔ | получить задачу |
| PATCH | `/todos/{id}` | ✔ | частичное обновление |
| DELETE | `/todos/{id}` | ✔ | удалить |

Авторизация: заголовок `Authorization: Bearer <token>`.

## Пример

```bash
curl -X POST localhost:8000/auth/register -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'
TOKEN=$(curl -s -X POST localhost:8000/auth/login -d "username=alice&password=secret123" | jq -r .access_token)
curl -X POST localhost:8000/todos -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"title":"Купить молоко"}'
curl localhost:8000/todos -H "Authorization: Bearer $TOKEN"
```

## Тесты и линтер

```powershell
pytest
ruff check .
ruff format .
```

## Структура

```
app/
  main.py        приложение, CORS, роутеры
  config.py      настройки из env / .env
  database.py    engine, сессия
  models.py      User, Todo
  schemas.py     Pydantic-схемы
  security.py    хеширование паролей, JWT
  deps.py        зависимости (сессия БД, текущий пользователь)
  routers/       auth.py, todos.py
alembic/         миграции БД (versions/ — файлы миграций)
tests/
```
