"""Schemas Pydantic para el traslado de familia entre refugios (HU-24)."""

from datetime import datetime

from pydantic import BaseModel, Field


class TrasladoCreate(BaseModel):
    """Solicitud de traslado."""

    id_familia: int = Field(..., gt=0, description="Familia que se traslada")
    id_refugio_destino: int = Field(..., gt=0, description="Refugio destino del traslado")


class RefugioOcupacion(BaseModel):
    """Estado de un refugio tras el traslado."""

    id_refugio: int
    nombre: str | None = None
    capacidad_maxima: int
    ocupacion_actual: int


class TrasladoResponse(BaseModel):
    """Respuesta del traslado: incluye el estado actualizado de ambos refugios."""

    id_familia: int
    id_familia_refugio: int = Field(..., description="ID del nuevo registro de asignación activa")
    id_refugio_origen: int
    id_refugio_destino: int
    personas_trasladadas: int = Field(
        ..., description="Cantidad de personas movidas (size de la familia)"
    )
    fecha_traslado: datetime
    origen: RefugioOcupacion
    destino: RefugioOcupacion
