from pydantic import BaseModel

from app.schema.zona_schema import NivelRiesgoTipo


class ZonaSinEntregasResponse(BaseModel):
    id_zona: int
    nombre: str
    nivel_riesgo: NivelRiesgoTipo
    familias_por_zona: int
