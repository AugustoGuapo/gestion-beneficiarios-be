from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.mapa_service import MapaService
from app.infrastructure.db.session import get_db
from app.schema.mapa_schema import MapaGeoJSONFeatureCollection

router = APIRouter(prefix="/mapa", tags=["mapa"])


@router.get(
    "/resumen",
    response_model=MapaGeoJSONFeatureCollection,
    summary="Resumen geográfico unificado para HU-13",
)
async def get_resumen_mapa(
    id_zona: int | None = Query(default=None, description="Filtra puntos por zona"),
    limite_entregas: int = Query(
        default=20,
        ge=1,
        le=200,
        description="Cantidad máxima de entregas recientes a incluir",
    ),
    db: AsyncSession = Depends(get_db),
) -> MapaGeoJSONFeatureCollection:
    return await MapaService.obtener_resumen(
        db=db,
        id_zona=id_zona,
        limite_entregas=limite_entregas,
    )
