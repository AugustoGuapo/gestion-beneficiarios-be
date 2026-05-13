from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String

from app.domain.models.origen_recurso import OrigenRecurso  # noqa: F401 — registra tabla para FK
from app.infrastructure.db.base import Base


class Recurso(Base):
    __tablename__ = "recurso"
    id_recurso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    categoria = Column(String(50), nullable=False)
    unidad_medida = Column(String(20), nullable=False)
    peso_unitario_kg = Column(Numeric(10, 2), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    id_origen = Column(Integer, ForeignKey("origen_recurso.id_origen"), nullable=True)
