"""Schemas Pydantic para el módulo de Entregas (HU-22)."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class EstadoEntrega(str, Enum):
    PENDIENTE = "PENDIENTE"
    ENTREGADA = "ENTREGADA"
    ANULADA = "ANULADA"


class DetalleEntregaItem(BaseModel):
    """Una línea del detalle de la entrega."""

    id_recurso: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    id_bodega: int | None = Field(
        default=None,
        gt=0,
        description=(
            "Bodega desde la cual se descuenta el inventario. "
            "Si no se envía, se usa la bodega por defecto que tenga stock suficiente."
        ),
    )


class EntregaCreate(BaseModel):
    id_familia: int = Field(..., gt=0)
    fecha_efectiva: date = Field(..., description="Fecha real de la entrega")
    coordenadas: str | None = Field(default=None, max_length=100)
    firma_digital: str | None = None
    items: list[DetalleEntregaItem] = Field(..., min_length=1)


class DetalleEntregaResponse(BaseModel):
    id_detalle: int
    id_recurso: int
    cantidad: int

    class Config:
        from_attributes = True


class EntregaResponse(BaseModel):
    id_entrega: int
    codigo: str | None
    fecha: datetime | None = None
    fecha_efectiva: date
    id_familia: int | None
    coordenadas: str | None
    firma_digital: str | None
    estado: EstadoEntrega
    detalles: list[DetalleEntregaResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
