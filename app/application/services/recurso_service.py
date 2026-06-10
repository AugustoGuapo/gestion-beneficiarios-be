from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.recurso import Recurso
from app.schema.recurso_schema import RecursoCreate, RecursoUmbralAlertaUpdate


class RecursoService:
    @staticmethod
    async def create_recurso(db: AsyncSession, recurso_create: RecursoCreate) -> Recurso:
        recurso = Recurso(**recurso_create.model_dump())
        db.add(recurso)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un recurso con el mismo nombre y categoria",
            ) from None
        await db.refresh(recurso)
        return recurso

    @staticmethod
    async def list_recursos(db: AsyncSession) -> list[Recurso]:
        result = await db.execute(select(Recurso))
        return result.scalars().all()

    @staticmethod
    async def update_umbral_alerta(
        db: AsyncSession,
        id_recurso: int,
        payload: RecursoUmbralAlertaUpdate,
    ) -> Recurso:
        result = await db.execute(select(Recurso).where(Recurso.id_recurso == id_recurso))
        recurso = result.scalar_one_or_none()
        if recurso is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurso no encontrado",
            )
        recurso.umbral_alerta = payload.umbral_alerta
        await db.commit()
        await db.refresh(recurso)
        return recurso
