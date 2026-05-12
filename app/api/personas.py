from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.domain.models.persona import Persona
from app.domain.models.familia import Familia
from app.core.security import get_current_user
from app.schema.persona_schema import PersonaResponse, PersonaCreate
from app.application.services.puntaje_service import recalcular_puntaje_familia

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
    persona_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    get_current_user(token)
    result = await db.execute(
        select(Persona).where(Persona.id_persona == persona_id)
    )
    persona = result.scalar_one_or_none()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada"
        )
    return persona


@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(
    persona: PersonaCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    get_current_user(token)

    if persona.id_familia is not None:
        result = await db.execute(
            select(Familia).where(Familia.id_familia == persona.id_familia)
        )
        familia = result.scalar_one_or_none()
        if not familia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada",
            )

    new_persona = Persona(
        id_familia=persona.id_familia,
        nombre=persona.nombre,
        edad=persona.edad,
        es_nino=persona.es_nino,
        es_anciano=persona.es_anciano,
        es_embarazada=persona.es_embarazada,
        tipo_documento=persona.tipo_documento,
        numero_documento=persona.numero_documento,
        tiene_discapacidad=persona.tiene_discapacidad,
        tiene_enfermedad_cronica=persona.tiene_enfermedad_cronica,
        es_cabeza_familia=persona.es_cabeza_familia,
    )
    db.add(new_persona)
    await db.commit()
    await db.refresh(new_persona)

    if new_persona.id_familia is not None:
        await recalcular_puntaje_familia(db, new_persona.id_familia)

    return new_persona


# ─── Endpoints anidados en familias ─────────────────────────


@router.get(
    "/familias/{familia_id}/personas",
    response_model=list[PersonaResponse],
)
async def get_personas_by_familia(
    familia_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    get_current_user(token)

    result = await db.execute(
        select(Familia).where(Familia.id_familia == familia_id)
    )
    familia = result.scalar_one_or_none()
    if not familia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Familia no encontrada"
        )

    result = await db.execute(
        select(Persona).where(Persona.id_familia == familia_id)
    )
    personas = result.scalars().all()
    return personas


@router.post(
    "/familias/{familia_id}/personas",
    response_model=PersonaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_persona_in_familia(
    familia_id: int,
    persona: PersonaCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    get_current_user(token)

    result = await db.execute(
        select(Familia).where(Familia.id_familia == familia_id)
    )
    familia = result.scalar_one_or_none()
    if not familia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Familia no encontrada"
        )

    new_persona = Persona(
        id_familia=familia_id,
        nombre=persona.nombre,
        edad=persona.edad,
        es_nino=persona.es_nino,
        es_anciano=persona.es_anciano,
        es_embarazada=persona.es_embarazada,
        tipo_documento=persona.tipo_documento,
        numero_documento=persona.numero_documento,
        tiene_discapacidad=persona.tiene_discapacidad,
        tiene_enfermedad_cronica=persona.tiene_enfermedad_cronica,
        es_cabeza_familia=persona.es_cabeza_familia,
    )
    db.add(new_persona)
    await db.commit()
    await db.refresh(new_persona)

    await recalcular_puntaje_familia(db, familia_id)

    return new_persona
