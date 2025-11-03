from sqlalchemy import Column, DateTime, func

from core.database import EngineBase

class BaseModel(EngineBase):
    __abstract__ = True
    # Common fields will be defined in subclasses, followed by timestamp fields
    create_time = Column(DateTime, default=func.now(), nullable=False)
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

