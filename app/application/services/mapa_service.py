from __future__ import annotations

from decimal import Decimal

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.bodega import Bodega
from app.domain.models.entrega import Entrega
from app.domain.models.refugio import Refugio
from app.schema.mapa_schema import (
    MapaFeatureProperties,
    MapaGeoJSONFeature,
    MapaGeoJSONFeatureCollection,
    MapaGeoJSONPoint,
)


class MapaService:
    """Construye los puntos geográficos requeridos por HU-13."""

    @staticmethod
    def _decimal_to_float(value: Decimal | float | int | None) -> float:
        if value is None:
            return 0.0
        return float(value)

    @staticmethod
    def _parse_coordenadas(coordenadas: str | None) -> tuple[float, float] | None:
        if not coordenadas:
            return None
        partes = [parte.strip() for parte in coordenadas.split(",", 1)]
        if len(partes) != 2:
            return None
        try:
            lat = float(partes[0])
            lng = float(partes[1])
        except ValueError:
            return None
        return lat, lng

    @staticmethod
    def _color_por_alerta(tiene_alerta: bool) -> str:
        return "red" if tiene_alerta else "green"

    @staticmethod
    def _color_entrega() -> str:
        return "blue"

    @staticmethod
    def _feature(
        *,
        id: int,
        tipo: str,
        nombre: str | None,
        lat: float,
        lng: float,
        estado: str,
        porcentaje: float | None,
        tiene_alerta: bool,
        color: str,
        zona_id: int | None,
    ) -> MapaGeoJSONFeature:
        return MapaGeoJSONFeature(
            geometry=MapaGeoJSONPoint(coordinates=[lng, lat]),
            properties=MapaFeatureProperties(
                id=id,
                tipo=tipo,  # type: ignore[arg-type]
                nombre=nombre,
                estado=estado,
                porcentaje=porcentaje,
                tiene_alerta=tiene_alerta,
                color=color,
                zona_id=zona_id,
            ),
        )

    @classmethod
    async def obtener_resumen(
        cls,
        db: AsyncSession,
        id_zona: int | None = None,
        limite_entregas: int = 20,
    ) -> MapaGeoJSONFeatureCollection:
        features: list[MapaGeoJSONFeature] = []

        features.extend(await cls._obtener_bodegas(db, id_zona=id_zona))
        features.extend(await cls._obtener_refugios(db, id_zona=id_zona))
        features.extend(
            await cls._obtener_entregas_recientes(
                db,
                id_zona=id_zona,
                limite_entregas=limite_entregas,
            )
        )
        return MapaGeoJSONFeatureCollection(features=features)

    @classmethod
    async def _obtener_bodegas(
        cls,
        db: AsyncSession,
        id_zona: int | None = None,
    ) -> list[MapaGeoJSONFeature]:
        query = select(Bodega)
        if id_zona is not None:
            query = query.where(Bodega.zona_id == id_zona)

        result = await db.execute(query.order_by(Bodega.id_bodega.asc()))
        bodegas = result.scalars().all()

        puntos: list[MapaGeoJSONFeature] = []
        for bodega in bodegas:
            bodega_id = int(getattr(bodega, "id_bodega"))
            nombre = getattr(bodega, "nombre", None)
            latitud = getattr(bodega, "latitud", None)
            longitud = getattr(bodega, "longitud", None)
            zona_id = getattr(bodega, "zona_id", None)
            capacidad = cls._decimal_to_float(getattr(bodega, "capacidad_max_kg", 0))
            peso_actual = cls._decimal_to_float(getattr(bodega, "peso_actual_kg", 0))
            porcentaje = (peso_actual / capacidad * 100) if capacidad > 0 else 0.0
            tiene_alerta = porcentaje >= 85
            puntos.append(
                cls._feature(
                    id=bodega_id,
                    tipo="bodega",
                    nombre=nombre,
                    lat=cls._decimal_to_float(latitud),
                    lng=cls._decimal_to_float(longitud),
                    estado="ALERTA" if tiene_alerta else "OK",
                    porcentaje=porcentaje,
                    tiene_alerta=tiene_alerta,
                    color=cls._color_por_alerta(tiene_alerta),
                    zona_id=int(zona_id) if zona_id is not None else None,
                )
            )
        return puntos

    @classmethod
    async def _obtener_refugios(
        cls,
        db: AsyncSession,
        id_zona: int | None = None,
    ) -> list[MapaGeoJSONFeature]:
        query = select(Refugio)
        if id_zona is not None:
            query = query.where(Refugio.zona_id == id_zona)

        result = await db.execute(query.order_by(Refugio.id.asc()))
        refugios = result.scalars().all()

        puntos: list[MapaGeoJSONFeature] = []
        for refugio in refugios:
            refugio_id = int(getattr(refugio, "id"))
            nombre = getattr(refugio, "nombre", None)
            latitud = getattr(refugio, "latitud", None)
            longitud = getattr(refugio, "longitud", None)
            zona_id = getattr(refugio, "zona_id", None)
            capacidad = cls._decimal_to_float(getattr(refugio, "capacidad_maxima_personas", 0))
            ocupacion = cls._decimal_to_float(getattr(refugio, "ocupacion_actual", 0))
            porcentaje = (ocupacion / capacidad * 100) if capacidad > 0 else 0.0
            tiene_alerta = porcentaje > 90
            puntos.append(
                cls._feature(
                    id=refugio_id,
                    tipo="refugio",
                    nombre=nombre,
                    lat=cls._decimal_to_float(latitud),
                    lng=cls._decimal_to_float(longitud),
                    estado="ALERTA" if tiene_alerta else "OK",
                    porcentaje=porcentaje,
                    tiene_alerta=tiene_alerta,
                    color=cls._color_por_alerta(tiene_alerta),
                    zona_id=int(zona_id) if zona_id is not None else None,
                )
            )
        return puntos

    @classmethod
    async def _obtener_entregas_recientes(
        cls,
        db: AsyncSession,
        id_zona: int | None = None,
        limite_entregas: int = 20,
    ) -> list[MapaGeoJSONFeature]:
        query = select(Entrega, Bodega).join(Bodega, Entrega.id_bodega == Bodega.id_bodega)
        if id_zona is not None:
            query = query.where(Bodega.zona_id == id_zona)

        query = query.order_by(desc(Entrega.fecha_efectiva), desc(Entrega.fecha)).limit(
            max(1, limite_entregas)
        )

        result = await db.execute(query)
        filas = result.all()

        puntos: list[MapaGeoJSONFeature] = []
        for entrega, bodega in filas:
            coordenadas = cls._parse_coordenadas(getattr(entrega, "coordenadas", None))
            if coordenadas is None:
                continue
            lat, lng = coordenadas
            puntos.append(
                cls._feature(
                    id=int(getattr(entrega, "id_entrega")),
                    tipo="entrega",
                    nombre=getattr(entrega, "codigo", None) or f"Entrega {getattr(entrega, 'id_entrega')}",
                    lat=lat,
                    lng=lng,
                    estado=getattr(entrega, "estado", None) or "ENTREGADA",
                    porcentaje=None,
                    tiene_alerta=False,
                    color=cls._color_entrega(),
                    zona_id=int(getattr(bodega, "zona_id")) if getattr(bodega, "zona_id", None) is not None else None,
                )
            )
        return puntos
