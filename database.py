from sqlalchemy import create_engine
from urllib.parse import quote_plus
from sqlalchemy.orm import declarative_base,sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

password = "karthik@2003"
encoded_password = quote_plus(password)

DATABASE_URL = f"postgresql+psycopg2://postgres:{encoded_password}@localhost:5432/fastapi_db"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Database connection successful!")
except Exception as e:
    print("Database connection failed:", e)

from sqlalchemy.orm import declarative_base
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()