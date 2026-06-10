from pydantic import BaseModel, Field

from app.schema.recurso_schema import CategoriaRecurso, UnidadMedida


class InventarioLineaRecurso(BaseModel):
    """Stock disponible de un tipo de recurso en una bodega."""

    id_recurso: int
    nombre: str
    categoria: CategoriaRecurso
    unidad_medida: UnidadMedida
    cantidad_disponible: int = Field(..., ge=0, description="Unidades disponibles (entradas − salidas)")
    umbral_alerta: int | None = Field(
        default=None,
        description="HU-16: umbral del catálogo recurso; null si no está configurado",
    )
    alerta_activa: bool = Field(
        default=False,
        description="HU-16: true si hay umbral y el stock es estrictamente menor",
    )


class InventarioPorBodega(BaseModel):
    """Inventario desglosado por centro de almacenamiento."""

    id_bodega: int
    nombre: str
    lineas: list[InventarioLineaRecurso]


class InventarioConsolidadoLinea(BaseModel):
    """Totales por recurso en el alcance de la consulta (una bodega o todas)."""

    id_recurso: int
    nombre: str
    categoria: CategoriaRecurso
    unidad_medida: UnidadMedida
    cantidad_total: int = Field(..., ge=0)


class InventarioConsultaResponse(BaseModel):
    """Respuesta HU-15: detalle por bodega y consolidado."""

    bodegas: list[InventarioPorBodega]
    consolidado: list[InventarioConsolidadoLinea]


class InventarioAlertaActiva(BaseModel):
    """Alerta de stock bajo umbral en una bodega (HU-16)."""

    id_bodega: int
    nombre_bodega: str
    id_recurso: int
    nombre_recurso: str
    categoria: CategoriaRecurso
    unidad_medida: UnidadMedida
    cantidad_disponible: int = Field(..., ge=0)
    umbral_alerta: int = Field(..., ge=1)


class InventarioAlertasResponse(BaseModel):
    """Listado para panel principal e indicadores (RF39 / HU-27)."""

    alertas: list[InventarioAlertaActiva]
    total: int = Field(..., ge=0)
