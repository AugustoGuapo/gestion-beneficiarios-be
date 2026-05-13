from sqlalchemy import Column, ForeignKey, Integer, String

from app.infrastructure.db.base import Base


class Albergue(Base):
    __tablename__ = "albergue"

    id_albergue = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    capacidad = Column(Integer, nullable=True)
    id_ubicacion = Column(
        Integer,
        ForeignKey("ubicacion.id_ubicacion", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
