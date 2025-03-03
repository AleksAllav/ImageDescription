from typing import Any

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RequestHistory(Base):
    __tablename__ = "request_history"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    image_description = Column(String)

    def __init__(self, image_description, **kw: Any):
        super().__init__(**kw)
        self.image_description = image_description
