from sqlalchemy import Column, Enum as SAEnum, Integer, String

from app.schema.zona_schema import NivelRiesgoTipo
from app.infrastructure.db.base import Base


class Zona(Base):
    __tablename__ = "zona"
    id_zona = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    nivel_riesgo_tipo = Column(
        SAEnum(NivelRiesgoTipo, name="nivel_riesgo", native_enum=True),
        nullable=False,
        default=NivelRiesgoTipo.bajo,
    )
