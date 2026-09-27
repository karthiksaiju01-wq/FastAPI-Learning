from sqlalchemy import Column,Integer,String,ForeignKey
from database import Base
from sqlalchemy.orm import relationship
from utils import hash_password, verify_password


class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    name=Column(String)
    email=Column(String)
    password = Column(String)
    products=relationship("Product",back_populates="user")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)


    user_id = Column(Integer, ForeignKey("users.id"))
    user=relationship("User", back_populates="products")
