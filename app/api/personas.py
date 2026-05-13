from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.domain.models.persona import Persona
from app.infrastructure.db.session import get_db
from app.schema.persona_schema import PersonaCreate, PersonaResponse

router = APIRouter(prefix="/personas", tags=["personas"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[PersonaResponse])
async def get_personas(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    get_current_user(token)
    result = await db.execute(select(Persona))
    personas = result.scalars().all()
    return personas


@router.post(
    "/",
    response_model=PersonaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_persona(
    persona_in: PersonaCreate,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    get_current_user(token)
    persona = Persona(
        nombre=persona_in.nombre,
        edad=persona_in.edad,
        es_nino=persona_in.es_nino,
        es_anciano=persona_in.es_anciano,
        es_embarazada=persona_in.es_embarazada,
    )
    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    get_current_user(token)
    result = await db.execute(select(Persona).where(Persona.id_persona == persona_id))
    persona = result.scalar_one_or_none()
    if persona is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada")
    return persona
