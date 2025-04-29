from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch database credentials from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


# print(f"DB_NAME: {DB_NAME}, DB_USER: {DB_USER}, DB_PASSWORD: {DB_PASSWORD},  DB_HOST: {DB_HOST}, DB_PORT: {DB_PORT}")
# PostgresSQL connection URL for SQLAlchemy
password = DB_PASSWORD.replace('@', '%40', 1)
DATABASE_URL = f"postgresql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

