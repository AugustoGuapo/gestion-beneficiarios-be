from sqlalchemy import Boolean, Column, Integer, String

from app.infrastructure.db.base import Base


class Persona(Base):
    __tablename__ = "persona"
    id_persona = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    edad = Column(Integer, nullable=True)
    es_nino = Column(Boolean, default=False)
    es_anciano = Column(Boolean, default=False)
    es_embarazada = Column(Boolean, default=False)
