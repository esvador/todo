# Todo API

Бэкенд для списка задач на FastAPI с JWT-авторизацией. Каждый пользователь видит только свои задачи.

## Стек
FastAPI, SQLAlchemy 2, SQLite (меняется через `DATABASE_URL`), PyJWT, Argon2 (pwdlib), pytest.

## Запуск

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # и задайте SECRET_KEY
uvicorn app.main:app --reload
```

Документация (Swagger): http://127.0.0.1:8000/docs. Кнопка **Authorize** позволяет залогиниться прямо там.

Таблицы создаются автоматически при старте.

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
ruff check app tests
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
tests/
```
