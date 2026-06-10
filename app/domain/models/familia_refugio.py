from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class FamiliaRefugio(Base):
    """Historial de asignaciones familia <-> refugio (HU-24).

    Una fila por cada estadía. La asignación ACTIVA es aquella con
    `fecha_salida IS NULL`. Cuando se realiza un traslado se cierra la
    asignación activa (set `fecha_salida = now()`) y se crea una nueva
    para el refugio destino.
    """

    __tablename__ = "familia_refugio"

    id_familia_refugio = Column(Integer, primary_key=True, index=True)
    id_familia = Column(
        Integer,
        ForeignKey("familia.id_familia", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    id_refugio = Column(
        Integer,
        ForeignKey("refugios.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    fecha_ingreso = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_salida = Column(DateTime, nullable=True)

    familia = relationship("Familia")
    refugio = relationship("Refugio")
