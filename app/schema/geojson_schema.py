from typing import Any, Literal, Optional

from pydantic import BaseModel


class FocoSanitarioProperties(BaseModel):
    """Propiedades de cada foco sanitario en el mapa."""

    id_foco: int
    tipo_vector: str
    nivel_riesgo: str
    estado: str
    acciones_tomadas: Optional[str] = None
    fecha_registro: str
    id_zona: Optional[int] = None
    id_albergue: Optional[int] = None

    model_config = {"from_attributes": True}


class GeoJSONPoint(BaseModel):
    """Geometría de punto GeoJSON."""

    type: Literal["Point"] = "Point"
    coordinates: list[float]  # [longitud, latitud] — orden estándar GeoJSON


class GeoJSONFeature(BaseModel):
    """Feature individual GeoJSON."""

    type: Literal["Feature"] = "Feature"
    geometry: GeoJSONPoint
    properties: FocoSanitarioProperties


class GeoJSONFeatureCollection(BaseModel):
    """FeatureCollection GeoJSON — formato estándar para mapas (compatible con D3, Leaflet, etc.)."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoJSONFeature]
