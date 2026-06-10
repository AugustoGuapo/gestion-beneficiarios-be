from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class DonacionRecurso(Base):
    __tablename__ = "donacion_recurso"
    id = Column(Integer, primary_key=True, index=True)
    donacion_id = Column(
        Integer,
        ForeignKey("donacion.id_donacion", ondelete="CASCADE"),
        nullable=False,
    )
    recurso_id = Column(
        Integer,
        ForeignKey("recurso.id_recurso", ondelete="RESTRICT"),
        nullable=False,
    )
    cantidad = Column(Float, nullable=False)

    donacion = relationship("Donacion")
    recurso = relationship("Recurso")
