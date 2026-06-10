from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


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
    peso_unitario_kg: float | None
    activo: bool
    id_origen: int | None = None
    umbral_alerta: int | None = Field(
        default=None,
        description="HU-16: cantidad mínima; alerta si el stock por bodega cae por debajo",
    )

    class Config:
        from_attributes = True


class RecursoUmbralAlertaUpdate(BaseModel):
    """Actualización parcial del umbral de alerta (HU-16)."""

    umbral_alerta: int | None = Field(
        ...,
        description="Entero >= 1 para activar alertas; null desactiva el umbral para el recurso",
    )

    @field_validator("umbral_alerta")
    @classmethod
    def umbral_positivo_o_nulo(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("umbral_alerta debe ser null o un entero >= 1")
        return v


class RecursoCreate(BaseModel):
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
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
        gt=0,
        description="Peso por unidad en kilogramos (referencia logística), mayor que 0",
    )
    id_origen: int | None = Field(
        default=None,
        description="FK opcional a origen_recurso",
    )
    umbral_alerta: int | None = Field(
        default=None,
        ge=1,
        description="HU-16: umbral opcional al crear el recurso",
    )
