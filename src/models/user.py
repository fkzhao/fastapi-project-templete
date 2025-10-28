from sqlalchemy import Column, Integer, String
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    nick_name = Column(String)
