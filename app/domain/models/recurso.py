from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.infrastructure.db.base import Base


class Recurso(Base):
    __tablename__ = "recurso"
    id_recurso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    peso_unitario_kg = Column(Numeric(10, 2), nullable=False)
    id_origen = Column(Integer, ForeignKey("origen_recurso.id_origen"), nullable=True)
