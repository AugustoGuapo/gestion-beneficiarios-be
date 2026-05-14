from pydantic import BaseModel, Field, field_validator
from decimal import Decimal


class BodegaCreate(BaseModel):
    """Schema for creating a new Bodega (Warehouse) - HU-11

    Campos obligatorios:
    - nombre, latitud, longitud, capacidad_max_kg, zona_id (para georreferenciación y RN-03)
    """
    nombre: str = Field(..., min_length=1, max_length=100)
    latitud: float = Field(..., ge=-90, le=90, description="Latitude (required for mapping)")
    longitud: float = Field(..., ge=-180, le=180, description="Longitude (required for mapping)")
    capacidad_max_kg: Decimal = Field(..., gt=0, decimal_places=2, description="Max capacity in kg")
    peso_actual_kg: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2, description="Current weight")
    zona_id: int = Field(..., gt=0, description="Foreign key to zona.id_zona")

    @field_validator("peso_actual_kg")
    @classmethod
    def validate_weight_not_exceeded(cls, v, info):
        """RN-03: Block if peso_actual_kg > capacidad_maxima_kg"""
        if "capacidad_max_kg" in info.data:
            if v > info.data["capacidad_max_kg"]:
                raise ValueError(
                    f"Peso actual ({v} kg) no puede exceder capacidad máxima ({info.data['capacidad_max_kg']} kg)"
                )
        return v


class BodegaResponse(BaseModel):
    """Schema for Bodega response with calculated weight alert"""
    id_bodega: int
    nombre: str
    latitud: float
    longitud: float
    capacidad_max_kg: Decimal
    peso_actual_kg: Decimal
    zona_id: int
    peso_porcentaje: float = Field(..., description="Weight percentage of capacity")
    has_alerta: bool = Field(..., description="Alert if weight >= 85%")

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        # Calculate weight percentage
        self.peso_porcentaje = (
            (float(self.peso_actual_kg) / float(self.capacidad_max_kg) * 100)
            if self.capacidad_max_kg and float(self.capacidad_max_kg) > 0
            else 0
        )
        # Alert if weight >= 85%
        self.has_alerta = self.peso_porcentaje >= 85
