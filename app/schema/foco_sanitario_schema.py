from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, model_validator


TipoVector = Literal["AGUA_CONTAMINADA", "INSECTOS", "ROEDORES", "RESIDUOS", "OTRO"]
NivelRiesgo = Literal["BAJO", "MEDIO", "ALTO", "CRITICO"]
EstadoFoco = Literal["ACTIVO", "EN_ATENCION", "RESUELTO"]


class FocoSanitarioCreate(BaseModel):
    id_zona: Optional[int] = None
    id_albergue: Optional[int] = None
    tipo_vector: TipoVector
    nivel_riesgo: NivelRiesgo
    acciones_tomadas: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

    @model_validator(mode="after")
    def validar_zona_o_albergue(self) -> "FocoSanitarioCreate":
        if self.id_zona is None and self.id_albergue is None:
            raise ValueError("Debe especificar al menos una zona o un albergue afectado.")
        return self


class FocoSanitarioUpdate(BaseModel):
    tipo_vector: Optional[TipoVector] = None
    nivel_riesgo: Optional[NivelRiesgo] = None
    acciones_tomadas: Optional[str] = None
    estado: Optional[EstadoFoco] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class FocoSanitarioResponse(BaseModel):
    id_foco: int
    id_zona: Optional[int] = None
    id_albergue: Optional[int] = None
    tipo_vector: str
    nivel_riesgo: str
    acciones_tomadas: Optional[str] = None
    estado: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    fecha_registro: datetime
    fecha_actualizacion: datetime

    model_config = {"from_attributes": True}
