from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class DetalleEntrega(Base):
    __tablename__ = "detalle_entrega"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_entrega = Column(
        Integer,
        ForeignKey("entrega.id_entrega", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    id_recurso = Column(
        Integer,
        ForeignKey("recurso.id_recurso", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    cantidad = Column(Integer, nullable=False)

    entrega = relationship("Entrega", back_populates="detalles")
    recurso = relationship("Recurso")
