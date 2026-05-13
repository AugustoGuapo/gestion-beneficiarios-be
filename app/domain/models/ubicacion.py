from sqlalchemy import Column, ForeignKey, Integer, String

from app.infrastructure.db.base import Base


class Ubicacion(Base):
    __tablename__ = "ubicacion"

    id_ubicacion = Column(Integer, primary_key=True, index=True)
    direccion = Column(String(200), nullable=True)
    id_zona = Column(
        Integer,
        ForeignKey("zona.id_zona", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
