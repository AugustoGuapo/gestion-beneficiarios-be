"""Schemas Pydantic para HU-22: Registrar entrega individual."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class EstadoEntrega(str, Enum):
    """Estados validos para una entrega."""

    PENDIENTE = "PENDIENTE"
    ENTREGADA = "ENTREGADA"
    ANULADA = "ANULADA"


class DetalleEntregaItem(BaseModel):
    """Item del detalle de una entrega (request)."""

    id_recurso: int = Field(..., gt=0, description="ID del recurso a entregar")
    cantidad: int = Field(..., gt=0, description="Cantidad de unidades a entregar")


class EntregaCreate(BaseModel):
    """Payload para registrar una nueva entrega (HU-22)."""

    id_familia: int = Field(..., gt=0, description="Familia receptora de la entrega")
    fecha_efectiva: date | None = Field(
        default=None,
        description="Fecha real de la entrega. Si se omite, se usa la fecha actual.",
    )
    id_bodega: int | None = Field(
        default=None,
        gt=0,
        description=(
            "Bodega desde la cual descontar el inventario. "
            "Si se omite, el sistema selecciona la primera bodega con stock suficiente."
        ),
    )
    coordenadas: str | None = Field(default=None, max_length=100)
    firma_digital: str | None = Field(default=None)
    detalles: list[DetalleEntregaItem] = Field(
        ...,
        min_length=1,
        description="Lista de recursos a entregar (al menos uno).",
    )


class DetalleEntregaResponse(BaseModel):
    """Item del detalle de la entrega en la respuesta."""

    model_config = ConfigDict(from_attributes=True)

    id_detalle: int
    id_recurso: int
    nombre_recurso: str | None = None
    cantidad: int


class EntregaResponse(BaseModel):
    """Respuesta tras registrar (o consultar) una entrega."""

    model_config = ConfigDict(from_attributes=True)

    id_entrega: int
    codigo: str | None = None
    estado: EstadoEntrega
    fecha: datetime | None = None
    fecha_efectiva: date
    id_familia: int | None = None
    id_bodega: int | None = Field(
        default=None,
        description="Bodega utilizada para descontar inventario (calculada al registrar).",
    )
    coordenadas: str | None = None
    firma_digital: str | None = None
    detalles: list[DetalleEntregaResponse] = Field(default_factory=list)
