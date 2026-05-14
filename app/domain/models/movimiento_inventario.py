from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.infrastructure.db.base import Base


class MovimientoInventario(Base):
    """Movimiento de inventario (entrada/salida) — fuente de verdad para stock por bodega (HU-15)."""

    __tablename__ = "movimiento_inventario"

    id_movimiento = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10), nullable=True)
    cantidad = Column(Integer, nullable=True)
    fecha = Column(DateTime, nullable=True)
    id_recurso = Column(Integer, ForeignKey("recurso.id_recurso"), nullable=True)
    id_bodega = Column(Integer, ForeignKey("bodega.id_bodega"), nullable=True)
