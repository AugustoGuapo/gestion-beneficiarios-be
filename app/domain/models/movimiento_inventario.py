from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.infrastructure.db.base import Base


class MovimientoInventario(Base):
    """ORM model para la tabla `movimiento_inventario`.

    HU-22 lo usa para registrar SALIDAS al concretar una entrega.
    HU-08/HU-11 ya manejan ENTRADAS por el lado de donaciones / bodegas.
    """
    """Movimiento de inventario (entrada/salida) — fuente de verdad para stock por bodega (HU-15)."""

    __tablename__ = "movimiento_inventario"

    id_movimiento = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, server_default=func.current_timestamp())
    id_recurso = Column(
        Integer,
        ForeignKey("recurso.id_recurso", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    id_bodega = Column(
        Integer,
        ForeignKey("bodega.id_bodega", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
