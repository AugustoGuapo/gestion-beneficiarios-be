"""Servicio para trasladar familias entre refugios (HU-24).

Reglas de negocio:

- La familia debe tener una asignación ACTIVA (fila en `familia_refugio` con
  `fecha_salida IS NULL`).
- El refugio destino debe existir.
- El refugio destino debe ser distinto del refugio origen.
- El refugio destino debe tener capacidad suficiente:
    ocupacion_actual_destino + personas_familia <= capacidad_maxima_destino
- El número de personas de la familia se calcula como
  `COUNT(persona WHERE id_familia = X)`. Si no hay personas registradas se
  asume 1 (la propia familia).

Atomicidad:
- Todo el flujo (cerrar asignación previa, crear nueva, decrementar ocupación
  del origen, incrementar ocupación del destino) ocurre en una sola
  transacción. Si cualquier paso falla se hace rollback completo y la
  base de datos queda como estaba.
"""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.familia import Familia
from app.domain.models.familia_refugio import FamiliaRefugio
from app.domain.models.persona import Persona
from app.domain.models.refugio import Refugio
from app.schema.traslado_schema import (
    RefugioOcupacion,
    TrasladoCreate,
    TrasladoResponse,
)


class TrasladoService:
    """Lógica de negocio para los traslados entre refugios."""

    @staticmethod
    async def _contar_personas_familia(db: AsyncSession, id_familia: int) -> int:
        """Cuenta personas que pertenecen a la familia. Mínimo 1."""
        stmt = select(func.count(Persona.id_persona)).where(Persona.id_familia == id_familia)
        result = await db.execute(stmt)
        cantidad = int(result.scalar_one() or 0)
        return max(cantidad, 1)

    @staticmethod
    async def _obtener_asignacion_activa(
        db: AsyncSession, id_familia: int
    ) -> FamiliaRefugio | None:
        stmt = (
            select(FamiliaRefugio)
            .where(
                FamiliaRefugio.id_familia == id_familia,
                FamiliaRefugio.fecha_salida.is_(None),
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def trasladar_familia(
        db: AsyncSession,
        payload: TrasladoCreate,
    ) -> TrasladoResponse:
        familia = await db.get(Familia, payload.id_familia)
        if familia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Familia {payload.id_familia} no encontrada",
            )

        destino = await db.get(Refugio, payload.id_refugio_destino)
        if destino is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Refugio destino {payload.id_refugio_destino} no encontrado",
            )

        asignacion_activa = await TrasladoService._obtener_asignacion_activa(db, payload.id_familia)
        if asignacion_activa is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"La familia {payload.id_familia} no tiene un refugio asignado actualmente; "
                    "no es posible trasladar."
                ),
            )

        id_refugio_origen = int(asignacion_activa.id_refugio)
        if id_refugio_origen == payload.id_refugio_destino:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El refugio destino es el mismo que el actual; no hay traslado a realizar.",
            )

        origen = await db.get(Refugio, id_refugio_origen)
        if origen is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"El refugio origen ({id_refugio_origen}) ya no existe; estado inconsistente."
                ),
            )

        personas = await TrasladoService._contar_personas_familia(db, payload.id_familia)

        capacidad_destino = int(destino.capacidad_maxima_personas or 0)
        ocupacion_destino = int(destino.ocupacion_actual or 0)
        if ocupacion_destino + personas > capacidad_destino:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"El refugio destino {payload.id_refugio_destino} no tiene capacidad "
                    f"suficiente: ocupación actual {ocupacion_destino}, capacidad "
                    f"{capacidad_destino}, se intentan ingresar {personas} personas."
                ),
            )

        ahora = datetime.utcnow()

        try:
            asignacion_activa.fecha_salida = ahora
            db.add(asignacion_activa)

            nueva_asignacion = FamiliaRefugio(
                id_familia=payload.id_familia,
                id_refugio=payload.id_refugio_destino,
                fecha_ingreso=ahora,
                fecha_salida=None,
            )
            db.add(nueva_asignacion)

            origen.ocupacion_actual = max(0, int(origen.ocupacion_actual or 0) - personas)
            destino.ocupacion_actual = int(destino.ocupacion_actual or 0) + personas
            db.add(origen)
            db.add(destino)

            await db.commit()
            await db.refresh(nueva_asignacion)
            await db.refresh(origen)
            await db.refresh(destino)
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se pudo completar el traslado por conflicto de integridad: {exc.orig}",
            ) from exc

        return TrasladoResponse(
            id_familia=payload.id_familia,
            id_familia_refugio=int(nueva_asignacion.id_familia_refugio),
            id_refugio_origen=id_refugio_origen,
            id_refugio_destino=payload.id_refugio_destino,
            personas_trasladadas=personas,
            fecha_traslado=ahora,
            origen=RefugioOcupacion(
                id_refugio=int(origen.id),
                nombre=origen.nombre,
                capacidad_maxima=int(origen.capacidad_maxima_personas or 0),
                ocupacion_actual=int(origen.ocupacion_actual or 0),
            ),
            destino=RefugioOcupacion(
                id_refugio=int(destino.id),
                nombre=destino.nombre,
                capacidad_maxima=int(destino.capacidad_maxima_personas or 0),
                ocupacion_actual=int(destino.ocupacion_actual or 0),
            ),
        )
