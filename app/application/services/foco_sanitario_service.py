from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.foco_sanitario import FocoSanitario
from app.schema.foco_sanitario_schema import FocoSanitarioCreate, FocoSanitarioUpdate
from app.schema.geojson_schema import (
    FocoSanitarioProperties,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONPoint,
)


class FocoSanitarioService:
    """Servicio de lógica de negocio para focos de riesgo sanitario."""

    @staticmethod
    async def crear_foco(db: AsyncSession, payload: FocoSanitarioCreate) -> FocoSanitario:
        """HU-25 — Registra un nuevo foco de riesgo sanitario."""
        foco = FocoSanitario(**payload.model_dump())
        db.add(foco)
        await db.commit()
        await db.refresh(foco)
        return foco

    @staticmethod
    async def listar_focos(
        db: AsyncSession,
        estado: str | None = None,
        nivel_riesgo: str | None = None,
        id_zona: int | None = None,
    ) -> list[FocoSanitario]:
        """Retorna focos sanitarios con filtros opcionales."""
        query = select(FocoSanitario)
        if estado:
            query = query.where(FocoSanitario.estado == estado.upper())
        if nivel_riesgo:
            query = query.where(FocoSanitario.nivel_riesgo == nivel_riesgo.upper())
        if id_zona:
            query = query.where(FocoSanitario.id_zona == id_zona)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def obtener_foco(db: AsyncSession, foco_id: int) -> FocoSanitario:
        """Obtiene un foco por ID o lanza 404."""
        result = await db.execute(
            select(FocoSanitario).where(FocoSanitario.id_foco == foco_id)
        )
        foco = result.scalar_one_or_none()
        if foco is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foco sanitario no encontrado.",
            )
        return foco

    @staticmethod
    async def actualizar_foco(
        db: AsyncSession, foco_id: int, payload: FocoSanitarioUpdate
    ) -> FocoSanitario:
        """HU-25 — Actualiza estado, acciones y otros campos de un foco."""
        foco = await FocoSanitarioService.obtener_foco(db, foco_id)
        for campo, valor in payload.model_dump(exclude_unset=True).items():
            setattr(foco, campo, valor)
        foco.fecha_actualizacion = datetime.utcnow()
        await db.commit()
        await db.refresh(foco)
        return foco

    @staticmethod
    async def obtener_geojson(
        db: AsyncSession, incluir_resueltos: bool = False
    ) -> GeoJSONFeatureCollection:
        """HU-26 — Retorna focos con coordenadas en formato GeoJSON para el mapa."""
        query = select(FocoSanitario).where(
            FocoSanitario.latitud.is_not(None),
            FocoSanitario.longitud.is_not(None),
        )
        if not incluir_resueltos:
            query = query.where(FocoSanitario.estado.in_(["ACTIVO", "EN_ATENCION"]))

        result = await db.execute(query)
        focos = result.scalars().all()

        features = [
            GeoJSONFeature(
                geometry=GeoJSONPoint(
                    coordinates=[float(foco.longitud), float(foco.latitud)]
                ),
                properties=FocoSanitarioProperties(
                    id_foco=foco.id_foco,
                    tipo_vector=foco.tipo_vector,
                    nivel_riesgo=foco.nivel_riesgo,
                    estado=foco.estado,
                    acciones_tomadas=foco.acciones_tomadas,
                    fecha_registro=foco.fecha_registro.isoformat(),
                    id_zona=foco.id_zona,
                    id_refugio=foco.id_refugio,
                ),
            )
            for foco in focos
        ]
        return GeoJSONFeatureCollection(features=features)
