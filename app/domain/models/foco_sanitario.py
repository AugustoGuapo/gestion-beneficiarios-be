from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String, Text

from app.infrastructure.db.base import Base


class FocoSanitario(Base):
    __tablename__ = "foco_sanitario"

    id_foco = Column(Integer, primary_key=True, index=True)
    id_zona = Column(Integer, ForeignKey("zona.id_zona", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    id_refugio = Column(Integer, ForeignKey("refugios.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    tipo_vector = Column(String(50), nullable=False)
    nivel_riesgo = Column(String(20), nullable=False)
    acciones_tomadas = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="ACTIVO")
    latitud = Column(Numeric(10, 7), nullable=True)
    longitud = Column(Numeric(10, 7), nullable=True)
    fecha_registro = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "tipo_vector IN ('AGUA_CONTAMINADA', 'INSECTOS', 'ROEDORES', 'RESIDUOS', 'OTRO')",
            name="ck_foco_tipo_vector",
        ),
        CheckConstraint(
            "nivel_riesgo IN ('BAJO', 'MEDIO', 'ALTO', 'CRITICO')",
            name="ck_foco_nivel_riesgo",
        ),
        CheckConstraint(
            "estado IN ('ACTIVO', 'EN_ATENCION', 'RESUELTO')",
            name="ck_foco_estado",
        ),
        CheckConstraint(
            "id_zona IS NOT NULL OR id_refugio IS NOT NULL",
            name="ck_foco_zona_o_refugio",
        ),
    )

    def __repr__(self) -> str:
        return f"<FocoSanitario(id={self.id_foco}, tipo={self.tipo_vector}, estado={self.estado})>"
