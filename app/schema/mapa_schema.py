from typing import Literal

from pydantic import BaseModel, Field


class MapaFeatureProperties(BaseModel):
    id: int = Field(..., description="Identificador del punto")
    tipo: Literal["bodega", "refugio", "entrega"] = Field(..., description="Tipo de marcador")
    nombre: str | None = Field(default=None, description="Nombre del punto")
    estado: str = Field(..., description="Estado resumido para el mapa")
    porcentaje: float | None = Field(
        default=None,
        description="Porcentaje de llenado/ocupación cuando aplique",
    )
    tiene_alerta: bool = Field(default=False, description="Indica si el punto tiene alerta")
    color: str = Field(..., description="Color sugerido para renderizar el marcador")
    zona_id: int | None = Field(default=None, description="Zona asociada al punto")


class MapaGeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: list[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="GeoJSON [longitud, latitud]",
    )


class MapaGeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: MapaGeoJSONPoint
    properties: MapaFeatureProperties


class MapaGeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[MapaGeoJSONFeature]
