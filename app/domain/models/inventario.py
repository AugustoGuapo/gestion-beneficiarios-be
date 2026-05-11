from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.db.base import Base


class Inventario(Base):
    __tablename__ = "inventario"
    id_inventario = Column(Integer, primary_key=True, index=True)
    recurso_id = Column(Integer, ForeignKey("recurso.id_recurso"), nullable=False)
    cantidad = Column(Float, nullable=False, default=0.0)

    recurso = relationship("Recurso")
