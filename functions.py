from database import SessionLocal
from models import UserModel
from passlib.context import CryptContext
from jose import jwt
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

# secret key fetch using openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


# hash password
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username: str, password: str, db):
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hash_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)



