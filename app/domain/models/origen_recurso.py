from sqlalchemy import Column, Integer, String

from app.infrastructure.db.base import Base


class OrigenRecurso(Base):
    """Catálogo de procedencias de ayuda (tabla origen_recurso en BD)."""

    __tablename__ = "origen_recurso"

    id_origen = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=True)
