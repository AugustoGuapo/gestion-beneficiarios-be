from sqlalchemy import Column, Enum as SAEnum, Integer, String
from app.infrastructure.db.base import Base


class Zona(Base):
    __tablename__ = "zona"
    id_zona = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    nivel_riesgo = Column(
        SAEnum(
            "bajo",
            "medio",
            "alto",
            "crítico",
            name="nivel_riesgo_tipo",
            native_enum=True,
        ),
        nullable=False,
    )
