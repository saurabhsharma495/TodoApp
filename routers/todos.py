from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from functions import get_db
from models import TodoModel
from routers.schemas import TodoRequest, TodoResponse
from routers.auth import get_current_user

todo_router = APIRouter(
    prefix='/todo',
    tags=['Todo']
)


@todo_router.post('/create-todo/')
async def create_todo(request: TodoRequest, db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')

    todo_data = TodoModel(**request.dict(), user_id=user_auth.get('User_id'))
    try:
        db.add(todo_data)
        db.commit()
        db.refresh(todo_data)
    except Exception as e:
        db.rollback()  # Rollback the order in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the order: {str(e)}"
        )
    return {
        "message": "todo has been successfully!",
        "todo_data": TodoResponse.from_orm(todo_data),
        "status_code": status.HTTP_201_CREATED
    }


@todo_router.get('/get_all_todo', response_model=List[TodoResponse])
async def get_todos(db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')

    todos = db.query(TodoModel).filter(TodoModel.user_id == user_auth.get('User_id')).all()
    return todos


@todo_router.get('/todos_details/{todo_id}')
async def get_todos_details(todo_id: int, db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')

    if todo_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid todo_id: {todo_id}")

    todos = db.query(TodoModel).filter(TodoModel.id == todo_id).filter(TodoModel.user_id == user_auth.get('User_id')).first()
    if not todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"todos details not found for todo_id: {todo_id}")
    return {
        "message": f"todo details of Id: {todo_id}",
        "todos_details": TodoResponse.from_orm(todos),
        "status_code": status.HTTP_200_OK
    }


@todo_router.put('/update-todo/{todo_id}')
async def update_todo(todo_id: int, request: TodoRequest, db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')

    if todo_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid todo_id: {todo_id}. It must be a positive integer.")
    todos = db.query(TodoModel).filter(TodoModel.id == todo_id).filter(TodoModel.user_id == user_auth.get('User_id')).first()
    if not todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"todos details not found for todo_id: {todo_id}")
    todos.title = request.title
    todos.description = request.description
    todos.priority = request.priority
    todos.completed = request.completed
    try:
        db.add(todos)
        db.commit()
        db.refresh(todos)
    except Exception as e:
        db.rollback()  # Rollback the order in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the order: {str(e)}"
        )
    return {
        "message": "todo has been updated!",
        "todo_data": TodoResponse.from_orm(todos),
        "status_code": status.HTTP_202_ACCEPTED
    }


@todo_router.delete('/delete-todo/{todo_id}')
async def delete_todo(todo_id: int, db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')

    if todo_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid todo_id: {todo_id}")

    todos = db.query(TodoModel).filter(TodoModel.id == todo_id).filter(TodoModel.user_id == user_auth.get('User_id')).first()
    if not todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"todos details not found for todo_id: {todo_id}")
    db.query(TodoModel).filter(TodoModel.id == todo_id).delete()
    try:
        db.commit()  # Commit to apply the deletion
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the todo: {str(e)}"
        )
    return {
        "message": f"Todo with ID {todo_id} has been successfully deleted.",
        "deleted_todo": TodoResponse.from_orm(todos),
        "status_code": status.HTTP_204_NO_CONTENT
    }









