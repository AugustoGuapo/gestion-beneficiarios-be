from sqlalchemy import Column, Integer, Numeric, String

from app.infrastructure.db.base import Base


class Bodega(Base):
    __tablename__ = "bodega"

    id_bodega = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=True)
    capacidad_max_kg = Column(Numeric(10, 2), nullable=True)
