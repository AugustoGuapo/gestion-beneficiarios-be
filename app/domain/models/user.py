from sqlalchemy import Column, Integer, String
from app.infrastructure.db.base import Base

class User(Base):
    __tablename__ = "usuario"
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)