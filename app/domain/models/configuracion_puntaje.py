from sqlalchemy import Column, Integer, String, Float
from app.infrastructure.db.base import Base


class ConfiguracionPuntaje(Base):
    __tablename__ = "configuracion_puntaje"

    id_config = Column(Integer, primary_key=True, index=True)
    clave = Column(String(50), unique=True, nullable=False)
    valor = Column(Float, nullable=False)
    descripcion = Column(String(200), nullable=True)