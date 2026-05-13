from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.domain.models.persona import Persona
from app.domain.models.familia import Familia
from app.core.security import get_current_user, check_role
from app.core.constants import UserRole
from app.schema.persona_schema import PersonaResponse, PersonaCreate, PersonaUpdate
from app.application.services.puntaje_service import recalcular_puntaje_familia

router = APIRouter(prefix="/personas", tags=["personas"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[PersonaResponse])
async def get_personas(
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.CENSADOR,
        UserRole.COORDINADOR_LOGISTICA,
        UserRole.FUNCIONARIO_CONTROL,
    ])),
    db: Session = Depends(get_db),
    ):
    result = await db.execute(select(Persona))
    personas = result.scalars().all()
    return personas


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: int,
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.CENSADOR,
        UserRole.COORDINADOR_LOGISTICA,
        UserRole.FUNCIONARIO_CONTROL,
    ])),
    db: Session = Depends(get_db),
):
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
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.CENSADOR,
    ])),
    db: Session = Depends(get_db),
):
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


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: int,
    persona_data: PersonaUpdate,
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.CENSADOR,
    ])),
    db: Session = Depends(get_db),
):
    result = await db.execute(
        select(Persona).where(Persona.id_persona == persona_id)
    )
    persona = result.scalar_one_or_none()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada"
        )

    # Guardar id_familia anterior para recálculo si cambia de familia
    familia_anterior = persona.id_familia

    # Actualizar solo los campos enviados (no None)
    update_data = persona_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(persona, key, value)

    # Si se asignó a una nueva familia, verificar que exista
    if persona_data.id_familia is not None and persona_data.id_familia != familia_anterior:
        result = await db.execute(
            select(Familia).where(Familia.id_familia == persona_data.id_familia)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Familia no encontrada",
            )

    await db.commit()
    await db.refresh(persona)

    # Recalcular puntaje de la familia nueva y la anterior (si cambiaron)
    if persona.id_familia is not None:
        await recalcular_puntaje_familia(db, persona.id_familia)
    if familia_anterior is not None and familia_anterior != persona.id_familia:
        await recalcular_puntaje_familia(db, familia_anterior)

    return persona


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(
    persona_id: int,
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.CENSADOR,
    ])),
    db: Session = Depends(get_db),
):
    result = await db.execute(
        select(Persona).where(Persona.id_persona == persona_id)
    )
    persona = result.scalar_one_or_none()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada"
        )

    familia_id = persona.id_familia
    await db.delete(persona)
    await db.commit()

    # Recalcular puntaje de la familia a la que pertenecía
    if familia_id is not None:
        await recalcular_puntaje_familia(db, familia_id)

    return None


# ─── Endpoints anidados en familias ─────────────────────────


@router.get(
    "/familias/{familia_id}/personas",
    response_model=list[PersonaResponse],
)
async def get_personas_by_familia(
    familia_id: int,
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.CENSADOR,
        UserRole.COORDINADOR_LOGISTICA,
        UserRole.FUNCIONARIO_CONTROL,
    ])),
    db: Session = Depends(get_db),
):
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
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.CENSADOR,
    ])),
    db: Session = Depends(get_db),
):
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
