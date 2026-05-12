from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from datetime import datetime
from app.infrastructure.db.base import Base


class Familia(Base):
    __tablename__ = "familia"

    id_familia = Column(Integer, primary_key=True, index=True)
    codigo_familia = Column(String(15), unique=True, nullable=False)
    acepta_privacidad = Column(Boolean, nullable=False)
    id_representante = Column(
        Integer, ForeignKey("persona.id_persona"), unique=True, nullable=True
    )
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    puntaje_prioridad = Column(Float, default=0.0)