from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, JSON
from sqlalchemy.orm import DeclarativeBase
from ..config import Base

class LuxBase(DeclarativeBase):

  __abstract__ = True  # <-- nie używaj declared_attr tutaj!

  @declared_attr
  def data(cls):
      return Column(JSON, default=dict)

  def to_dict(self):
      return {
          k: getattr(self, k)
          for k in self.__mapper__.c.keys()
      } | {"data": self.data}

  def get_data(self, key: str, default=None):
      return self.data.get(key, default) if self.data else default

  def set_data(self, key: str, value):
      if self.data is None:
          self.data = {}
      self.data[key] = value

  def update_data(self, updates: dict):
      if self.data is None:
          self.data = {}
      self.data.update(updates)

  def remove_data(self, key: str):
      if self.data and key in self.data:
          del self.data[key]