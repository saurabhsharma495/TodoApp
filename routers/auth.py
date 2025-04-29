from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import List
from sqlalchemy.orm import Session
from functions import get_db, create_access_token
from models import UserModel
from routers.schemas import UserResponse, UserRequest
from passlib.context import CryptContext
from functions import authenticate_user
from datetime import timedelta
from dotenv import load_dotenv

import os

load_dotenv()

# secret key fetch using openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_TIME = os.getenv('ACCESS_TOKEN_TIME')

auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentications']
)

# hash password
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if username is None or user_id is None or role is None :
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')
        return {'Username': username, 'User_id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')


@auth_router.post('/token')
async def get_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # print(f"username: {form_data.username}, password: {form_data.password}")
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes= int(ACCESS_TOKEN_TIME)))
    return {'message': 'Successful Authentication', 'access_token': token, "token_type": 'bearer'}


@auth_router.post('/create-user/')
async def create_user(request: UserRequest, db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    """Request:
        {
            "username": "saurabhsharma",
            "email": "saurabhksharma@gmail.com",
            "first_name": "saurabh",
            "last_name": "sharma",
            "password": "admin@123",
            "role": "admin"
        }
        Response:
        {
            "message": "User has been successfully!",
            "user_data": {
                "id": 1,
                "username": "saurabhsharma",
                "email": "saurabhksharma@gmail.com",
                "first_name": "saurabh",
                "last_name": "sharma",
                "role": "admin",
                "is_active": true
            },
            "status_code": 201
        }
    """
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')
    # Check if the username already exists
    existing_user = db.query(UserModel).filter(UserModel.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{request.username}' is already taken."
        )
    user_data = UserModel(
        email=request.email,
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        hash_password=bcrypt_context.hash(request.password),
        role=request.role,
        is_active=True
    )
    try:
        db.add(user_data)
        db.commit()
        db.refresh(user_data)
    except Exception as e:
        db.rollback()  # Rollback the order in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the user: {str(e)} in {create_user.__name__}"
        )
    return {
        "message": "User has been successfully!",
        "user_data": UserResponse.from_orm(user_data),
        "status_code": status.HTTP_201_CREATED
    }


@auth_router.get('/user_list', response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    """
    Response:
    [
        {
            "id": 1,
            "username": "saurabhsharma",
            "email": "saurabhksharma@gmail.com",
            "first_name": "saurabh",
            "last_name": "sharma",
            "role": "admin",
            "is_active": true
        },
        {
            "id": 2,
            "username": "addy",
            "email": "addy@gmail.com",
            "first_name": "addy",
            "last_name": "sharma",
            "role": "user1",
            "is_active": true
        }
    ]
    """
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')

    users = db.query(UserModel).all()
    return users


@auth_router.get('/user_details/{user_id}')
async def get_user_details(user_id: int, db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')

    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid todo_id: {user_id}")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User details not found for todo_id: {user_id}")
    return {
        "message": f"User details of Id: {user_id}",
        "user_details": UserResponse.from_orm(user),
        "status_code": status.HTTP_200_OK
    }


@auth_router.put('/update-user/{user_id}')
async def update_user_details(user_id: int, request: UserRequest, db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    """

    :param user_auth:
    :param db: Session = Depends(get_db)
    :param user_id: 1
    :param request:
    {
        "username": "vandana",
        "email": "vandana@gmail.com",
        "first_name": "vandana",
        "last_name": "sharma",
        "role": "user1",
        "is_active": true,
        "password": "12345"
    }
    :return:
    {
        "message": "User has been updated!",
        "user_updated_data": {
            "id": 2,
            "username": "vandana",
            "email": "vandana@gmail.com",
            "first_name": "vandana",
            "last_name": "sharma",
            "role": "user1",
            "is_active": true
        },
        "status_code": 202
    }
    """
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')

    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid user_id: {user_id}. It must be a positive integer.")

    existing_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user details not found for user_id: {user_id}")

    # Check if the username already exists for a different user
    if request.username != existing_user.username:
        user_with_same_username = db.query(UserModel).filter(UserModel.username == request.username).first()
        if user_with_same_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{request.username}' is already taken."
            )

    existing_user.username = request.username
    existing_user.email = request.email
    existing_user.first_name = request.first_name
    existing_user.last_name = request.last_name
    existing_user.password = request.password
    existing_user.role = request.role
    try:
        db.add(existing_user)
        db.commit()
        db.refresh(existing_user)
    except Exception as e:
        db.rollback()  # Rollback the order in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the order: {str(e)} in {update_user_details.__name__}"
        )
    return {
        "message": "User has been updated!",
        "user_updated_data": UserResponse.from_orm(existing_user),
        "status_code": status.HTTP_202_ACCEPTED
    }


@auth_router.delete('/delete-user/{user_id}')
async def delete_user(user_id: int, db: Session = Depends(get_db), user_auth: dict = Depends(get_current_user)):
    """

    :param user_auth:
    :param user_id: 6
    :param db:  Session = Depends(get_db)
    :return:
    {
        "message": "User with ID 6 has been successfully deleted.",
        "deleted_todo": {
            "id": 6,
            "username": "dummy1",
            "email": "dummy@gmail.com",
            "first_name": "dummy",
            "last_name": "sharma",
            "role": "user3",
            "is_active": true
        },
        "status_code": 204
    }
    """
    if user_auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate the user')

    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid user_id: {user_id}. It must be a positive integer.")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user details not found for user_id: {user_id}")
    db.query(UserModel).filter(UserModel.id == user_id).delete()
    try:
        db.commit()  # Commit to apply the deletion
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the todo: {str(e)}"
        )
    return {
        "message": f"User with ID {user_id} has been successfully deleted.",
        "deleted_todo": UserResponse.from_orm(user),
        "status_code": status.HTTP_204_NO_CONTENT
    }
