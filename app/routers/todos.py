from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import select

from app.deps import CurrentUser, DbSession
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


def get_own_todo(db: DbSession, user: CurrentUser, todo_id: int) -> Todo:
    todo = db.get(Todo, todo_id)
    # Чужие задачи отдаём как 404, чтобы не раскрывать их существование
    if todo is None or todo.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found")
    return todo


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, db: DbSession, user: CurrentUser) -> Todo:
    todo = Todo(**data.model_dump(), owner_id=user.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.get("", response_model=list[TodoRead])
def list_todos(
    db: DbSession,
    user: CurrentUser,
    is_done: bool | None = None,
    q: Annotated[str | None, Query(max_length=100, description="Поиск по названию")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Todo]:
    stmt = select(Todo).where(Todo.owner_id == user.id)
    if is_done is not None:
        stmt = stmt.where(Todo.is_done == is_done)
    if q:
        stmt = stmt.where(Todo.title.icontains(q, autoescape=True))
    stmt = stmt.order_by(Todo.created_at.desc(), Todo.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt))


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int, db: DbSession, user: CurrentUser) -> Todo:
    return get_own_todo(db, user, todo_id)


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, data: TodoUpdate, db: DbSession, user: CurrentUser) -> Todo:
    todo = get_own_todo(db, user, todo_id)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("title", ...) is None or changes.get("is_done", ...) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "title/is_done cannot be null")
    for field, value in changes.items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: DbSession, user: CurrentUser) -> Response:
    todo = get_own_todo(db, user, todo_id)
    db.delete(todo)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
