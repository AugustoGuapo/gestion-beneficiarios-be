from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class Entrega(Base):
    __tablename__ = "entrega"

    id_entrega = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=True, index=True)
    fecha = Column(DateTime(timezone=False), server_default=func.now())
    fecha_efectiva = Column(Date, nullable=False)
    id_familia = Column(
        Integer,
        ForeignKey("familia.id_familia", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    coordenadas = Column(String(100), nullable=True)
    firma_digital = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="ENTREGADA")

    familia = relationship("Familia")
    detalles = relationship(
        "DetalleEntrega",
        back_populates="entrega",
        cascade="all, delete-orphan",
    )
