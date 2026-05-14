from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_db

from app.domain.models.donante import Donante

from app.schema.donante_schema import (
    DonanteCreate,
    DonanteResponse,
)

router = APIRouter(
    prefix="/donantes",
    tags=["Donantes"],
)


@router.post(
    "/",
    response_model=DonanteResponse,
)
async def registrar_donante(
    donante: DonanteCreate,
    db: AsyncSession = Depends(get_db),
):

    query = select(Donante).where(
        Donante.nombre == donante.nombre,
        Donante.tipo_donante == donante.tipo_donante,
    )

    result = await db.execute(query)

    donante_existente = result.scalar_one_or_none()

    if donante_existente:

        raise HTTPException(
            status_code=409,
            detail="Ya existe un donante con ese nombre y tipo",
        )

    nuevo_donante = Donante(
        nombre=donante.nombre,
        tipo_donante=donante.tipo_donante,
    )

    db.add(nuevo_donante)

    await db.commit()

    await db.refresh(nuevo_donante)

    return nuevo_donante