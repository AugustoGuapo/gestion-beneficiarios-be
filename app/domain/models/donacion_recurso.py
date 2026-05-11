from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class DonacionRecurso(Base):
    __tablename__ = "donacion_recurso"
    id = Column(Integer, primary_key=True, index=True)
    donacion_id = Column(Integer, ForeignKey("donacion.id_donacion"), nullable=False)
    recurso_id = Column(Integer, ForeignKey("recurso.id_recurso"), nullable=False)
    cantidad = Column(Float, nullable=False)

    recurso = relationship("Recurso")
