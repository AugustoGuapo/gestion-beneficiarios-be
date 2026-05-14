from enum import StrEnum

from pydantic import BaseModel, Field


class CategoriaRecurso(StrEnum):
    ALIMENTOS = "ALIMENTOS"
    COBIJA = "COBIJA"
    COLCHONETA = "COLCHONETA"
    ASEO = "ASEO"
    MEDICAMENTO = "MEDICAMENTO"


class UnidadMedida(StrEnum):
    KG = "KG"
    UNIDAD = "UNIDAD"
    LITRO = "LITRO"


class RecursoResponse(BaseModel):
    id_recurso: int
    nombre: str
    categoria: CategoriaRecurso
    unidad_medida: UnidadMedida
    peso_unitario_kg: float
    activo: bool
    id_origen: int | None = None

    class Config:
        from_attributes = True


class RecursoCreate(BaseModel):
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Nombre del ítem en el catálogo",
    )
    categoria: CategoriaRecurso = Field(
        description="Categoría (ALIMENTOS, COBIJA, COLCHONETA, ASEO, MEDICAMENTO)",
    )
    unidad_medida: UnidadMedida = Field(
        description="Unidad de medida (KG, UNIDAD, LITRO)",
    )
    peso_unitario_kg: float = Field(
        ...,
        description="Peso por unidad en kilogramos (referencia logística)",
    )
    id_origen: int | None = Field(
        default=None,
        description="FK opcional a origen_recurso",
    )
