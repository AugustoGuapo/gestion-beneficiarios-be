from pydantic import BaseModel, Field
from datetime import datetime


class FamiliaCreate(BaseModel):
    acepta_privacidad: bool
    id_zona: int | None = Field(
        default=None,
        description="Zona de residencia de la familia, usada para el factor de riesgo en el puntaje de prioridad",
    )


class FamiliaResponse(BaseModel):
    id_familia: int
    codigo_familia: str
    acepta_privacidad: bool
    id_representante: int | None
    fecha_registro: datetime
    puntaje_prioridad: float
    id_zona: int | None = None

    class Config:
        from_attributes = True
