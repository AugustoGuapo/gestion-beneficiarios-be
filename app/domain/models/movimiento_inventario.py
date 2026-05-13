from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.infrastructure.db.base import Base


class MovimientoInventario(Base):
    """Movimientos de inventario (ENTRADA / SALIDA) por recurso y bodega.

    Define el stock disponible de un recurso como:
        stock = SUM(cantidad WHERE tipo='ENTRADA') - SUM(cantidad WHERE tipo='SALIDA')
    """

    __tablename__ = "movimiento_inventario"

    id_movimiento = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(10), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    id_recurso = Column(
        Integer,
        ForeignKey("recurso.id_recurso", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    )
    id_bodega = Column(
        Integer,
        ForeignKey("bodega.id_bodega", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
