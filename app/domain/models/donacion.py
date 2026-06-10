from sqlalchemy import Column, DateTime, Integer, String, func

from app.infrastructure.db.base import Base


class Donacion(Base):
    __tablename__ = "donacion"
    id_donacion = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=True)
    referencia = Column(String(255), nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
