from pydantic import BaseModel, Field

from app.schema.recurso_schema import CategoriaRecurso, UnidadMedida


class InventarioLineaRecurso(BaseModel):
    """Stock disponible de un tipo de recurso en una bodega."""

    id_recurso: int
    nombre: str
    categoria: CategoriaRecurso
    unidad_medida: UnidadMedida
    cantidad_disponible: int = Field(..., ge=0, description="Unidades disponibles (entradas − salidas)")


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
