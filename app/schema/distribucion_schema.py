"""Schemas Pydantic para el plan de distribución priorizado (HU-21)."""

from pydantic import BaseModel, Field

from app.schema.zona_schema import NivelRiesgoTipo


class PlanItem(BaseModel):
    """Una familia dentro del plan de distribución."""

    id_familia: int
    representante: str | None = Field(
        default=None, description="Nombre del representante de la familia"
    )
    id_albergue: int | None = Field(
        default=None, description="Albergue actual de la familia (si tiene asignación)"
    )
    nombre_albergue: str | None = None
    id_zona: int | None = None
    nombre_zona: str | None = None
    nivel_riesgo: NivelRiesgoTipo | None = None

    personas_estimadas: int = Field(
        ..., description="Personas asumidas en la familia (default configurable)"
    )
    vulnerables: int = Field(
        default=0,
        description="Cantidad de miembros vulnerables conocidos (niño + anciano + embarazada)",
    )

    racion_kg: float = Field(
        ..., description="Kilogramos totales requeridos = personas × dias × ración/persona/día"
    )
    dias_cobertura: int = Field(..., ge=3, description="Días de cobertura calculados")

    score: float = Field(
        ...,
        description="Score de priorización (a mayor valor, mayor prioridad)",
    )


class PlanResponse(BaseModel):
    """Respuesta completa del plan."""

    parametros: dict = Field(
        ...,
        description="Parámetros usados para generar el plan (días, ración, etc.)",
    )
    total_familias: int
    total_kg_requeridos: float
    items: list[PlanItem]
