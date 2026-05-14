from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.recurso import Recurso
from app.schema.recurso_schema import RecursoCreate


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
