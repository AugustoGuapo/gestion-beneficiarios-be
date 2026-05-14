from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.db.base import Base


class Entrega(Base):
    """ORM model para la tabla `entrega` (HU-22).

    Las columnas `codigo` y `estado` se agregan via migracion
    1780100000_hu22_agregar_codigo_y_estado_a_entrega.sql
    """

    __tablename__ = "entrega"

    id_entrega = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=True, index=True)
    estado = Column(String(20), nullable=False, default="ENTREGADA")
    fecha = Column(DateTime, server_default=func.current_timestamp())
    fecha_efectiva = Column(Date, nullable=False)
    id_familia = Column(
        Integer,
        ForeignKey("familia.id_familia", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    coordenadas = Column(String(100), nullable=True)
    firma_digital = Column(Text, nullable=True)

    detalles = relationship(
        "DetalleEntrega",
        back_populates="entrega",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
