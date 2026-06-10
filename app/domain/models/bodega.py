from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.infrastructure.db.base import Base


class Bodega(Base):
    """
    ORM model for Bodega (Storage Warehouse) - HU-11

    Business Rules:
    - RN-03: peso_actual_kg cannot exceed capacidad_max_kg
    - Alerta: Alert if peso_actual_kg >= 85% of capacidad_max_kg
    - Coordenadas (lat/long) are mandatory for mapping (HU-13)

    Attributes:
        id_bodega: Primary key for the warehouse record
        nombre: Name/identifier of the warehouse
        latitud: Latitude coordinate (DECIMAL 10,8)
        longitud: Longitude coordinate (DECIMAL 11,8)
        capacidad_max_kg: Maximum storage capacity in kilograms
        peso_actual_kg: Current weight stored in kilograms
        zona_id: Foreign key to zona table
    """

    __tablename__ = "bodega"

    id_bodega = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    latitud = Column(Numeric(10, 8), nullable=False)
    longitud = Column(Numeric(11, 8), nullable=False)
    capacidad_max_kg = Column(Numeric(10, 2), nullable=False)
    peso_actual_kg = Column(Numeric(10, 2), default=0)
    zona_id = Column(Integer, ForeignKey("zona.id_zona"), nullable=False)
