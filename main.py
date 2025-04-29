from fastapi import FastAPI, status
from database import engine
from routers.todos import todo_router
from routers.auth import auth_router
import models
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


app.router.include_router(todo_router)
app.router.include_router(auth_router)

