from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
)

from app.domain.models.origen_recurso import OrigenRecurso  # noqa: F401 — registra tabla para FK
from app.infrastructure.db.base import Base


class Recurso(Base):
    __tablename__ = "recurso"
    id_recurso = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    categoria = Column(String(50), nullable=False)
    unidad_medida = Column(String(20), nullable=False, server_default="KG")
    peso_unitario_kg = Column(Numeric(10, 2), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default='true')
    id_origen = Column(Integer, ForeignKey("origen_recurso.id_origen"), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "categoria IN ('ALIMENTOS','COBIJA','COLCHONETA','ASEO','MEDICAMENTO')",
            name="chk_recurso_categoria",
        ),
        CheckConstraint(
            "unidad_medida IN ('KG','UNIDAD','LITRO')",
            name="chk_recurso_unidad",
        ),
        CheckConstraint(
            "(peso_unitario_kg > 0) OR (peso_unitario_kg IS NULL)",
            name="recurso_peso_unitario_kg_check",
        ),
    )
