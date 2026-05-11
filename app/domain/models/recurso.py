from sqlalchemy import Column, Integer, String, Float
from app.infrastructure.db.base import Base


class Recurso(Base):
    __tablename__ = "recurso"
    id_recurso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    categoria = Column(String(100), nullable=False)
    unidad = Column(String(50), nullable=False)
    peso_unitario = Column(Float, nullable=False)
