from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional


class RefugioCreate(BaseModel):
    """Schema for creating a new Refugio (Shelter)"""
    nombre: str = Field(..., min_length=1, max_length=100)
    ubicacion_textual: Optional[str] = Field(None, max_length=500)
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)
    capacidad_maxima_personas: int = Field(..., gt=0)
    ocupacion_actual: int = Field(default=0, ge=0)
    zona_id: Optional[int] = None


class RefugioResponse(BaseModel):
    """Schema for Refugio response with calculated occupancy alert"""
    id: int
    nombre: str
    ubicacion_textual: Optional[str]
    latitud: float
    longitud: float
    capacidad_maxima_personas: int
    ocupacion_actual: int
    zona_id: Optional[int]
    fecha_registro: datetime
    ocupacion_porcentaje: float = Field(0.0, description="Occupancy percentage")
    has_alerta: bool = Field(False, description="Alert if occupancy > 90%")

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def calcular_ocupacion(self) -> "RefugioResponse":
        capacidad = float(self.capacidad_maxima_personas)
        ocupacion = float(self.ocupacion_actual)
        self.ocupacion_porcentaje = (
            (ocupacion / capacidad * 100) if capacidad > 0 else 0.0
        )
        self.has_alerta = self.ocupacion_porcentaje > 90
        return self
