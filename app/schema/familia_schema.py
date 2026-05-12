from pydantic import BaseModel
from datetime import datetime


class FamiliaCreate(BaseModel):
    acepta_privacidad: bool


class FamiliaResponse(BaseModel):
    id_familia: int
    codigo_familia: str
    acepta_privacidad: bool
    id_representante: int | None
    fecha_registro: datetime
    puntaje_prioridad: float

    class Config:
        from_attributes = True