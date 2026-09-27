from fastapi import FastAPI, Depends, HTTPException,Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils import hash_password, verify_password
import os
from datetime import datetime,timedelta,timezone
import jwt
from dotenv import load_dotenv
from routers.products import router as product_router
from fastapi.responses import JSONResponse


from database import get_db
from models import Product as ProductModel,User as UserModel

from routers.users import router as user_router
from routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
@app.get("/")
def root():
     return{"message":"Hello FastAPI"}
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        }
    )

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(product_router)
app.include_router(user_router)
app.include_router(auth_router)


class UserCreate(BaseModel):
    name:str
    email:str
    password:str
class UserResponse(BaseModel):
        id: int
        name: str
        email: str
class TokenResponse(BaseModel):
     access_token:str
     token_type :str

class Config:
        from_attributes = True
load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set in .env")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,JWT_SECRET_KEY,  algorithm=JWT_ALGORITHM
    )

    return token
 


