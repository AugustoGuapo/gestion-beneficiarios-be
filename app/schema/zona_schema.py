from enum import Enum

from pydantic import BaseModel


class NivelRiesgoTipo(str, Enum):
    bajo = "bajo"
    medio = "medio"
    alto = "alto"
    critico = "crítico"


class ZonaResponse(BaseModel):
    id_zona: int
    nombre: str
    nivel_riesgo: str

    class Config:
        from_attributes = True


class ZonaCreate(BaseModel):
    nombre: str
    nivel_riesgo: NivelRiesgoTipo
