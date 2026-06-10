from sqlalchemy import Column, Integer, String

from app.infrastructure.db.base import Base


class Zona(Base):
    __tablename__ = "zona"
    id_zona = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    nivel_riesgo_tipo = Column(String(20), nullable=False, default="bajo")
