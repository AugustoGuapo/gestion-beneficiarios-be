from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.infrastructure.db.base import Base


class Refugio(Base):
    """
    ORM model for Refugios (Temporary Shelters) - HU-10

    Attributes:
        id: Primary key for the shelter record
        nombre: Name/identifier of the shelter
        ubicacion_textual: Text description of the shelter's location
        latitud: Latitude coordinate (DECIMAL 10,8)
        longitud: Longitude coordinate (DECIMAL 11,8)
        capacidad_maxima_personas: Maximum number of people that can be housed
        ocupacion_actual: Current number of people in the shelter
        zona_id: Foreign key to zona table
        fecha_registro: Timestamp of record creation
    """

    __tablename__ = "refugios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    ubicacion_textual = Column(String, nullable=True)
    latitud = Column(Numeric(10, 8), nullable=False)
    longitud = Column(Numeric(11, 8), nullable=False)
    capacidad_maxima_personas = Column(Integer, nullable=False)
    ocupacion_actual = Column(Integer, default=0)
    zona_id = Column(Integer, ForeignKey("zona.id_zona"), nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
