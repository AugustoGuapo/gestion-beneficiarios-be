from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from app.infrastructure.db.base import Base


class Persona(Base):
    __tablename__ = "persona"

    id_persona = Column(Integer, primary_key=True, index=True)
    id_familia = Column(Integer, ForeignKey("familia.id_familia"), nullable=True)
    nombre = Column(String(100), nullable=False)
    edad = Column(Integer, nullable=True)
    es_nino = Column(Boolean, default=False)
    es_anciano = Column(Boolean, default=False)
    es_embarazada = Column(Boolean, default=False)
    tipo_documento = Column(String(20), nullable=True)
    numero_documento = Column(String(20), nullable=True)
    tiene_discapacidad = Column(Boolean, default=False)
    tiene_enfermedad_cronica = Column(Boolean, default=False)
    es_cabeza_familia = Column(Boolean, default=False)
