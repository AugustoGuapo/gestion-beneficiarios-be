from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.domain.models.persona import Persona
from app.core.security import get_current_user
from app.schema.persona_schema import PersonaResponse

router = APIRouter(prefix="/personas", tags=["personas"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[PersonaResponse])
async def get_personas(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(Persona))
    personas = result.scalars().all()
    return personas


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(Persona).where(Persona.id_persona == persona_id))
    persona = result.scalar_one_or_none()
    return persona
