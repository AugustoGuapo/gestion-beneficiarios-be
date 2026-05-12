from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.domain.models.configuracion_puntaje import ConfiguracionPuntaje
from app.domain.models.familia import Familia
from app.core.security import get_current_user
from app.schema.configuracion_puntaje_schema import (
    ConfiguracionPuntajeResponse,
    ConfiguracionPuntajeUpdate,
)
from app.application.services.puntaje_service import recalcular_puntaje_familia

router = APIRouter(prefix="/configuracion-puntaje", tags=["configuracion-puntaje"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[ConfiguracionPuntajeResponse])
async def get_configuraciones(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(ConfiguracionPuntaje))
    configs = result.scalars().all()
    return configs


@router.put("/{clave}", response_model=ConfiguracionPuntajeResponse)
async def update_configuracion(
    clave: str,
    update: ConfiguracionPuntajeUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    get_current_user(token)

    result = await db.execute(
        select(ConfiguracionPuntaje).where(ConfiguracionPuntaje.clave == clave)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración '{clave}' no encontrada",
        )

    config.valor = update.valor
    await db.commit()
    await db.refresh(config)
    return config


@router.post("/familias/{familia_id}/calcular-puntaje")
async def calcular_puntaje(
    familia_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Calcula y guarda el puntaje de prioridad para una familia."""
    get_current_user(token)

    result = await db.execute(
        select(Familia).where(Familia.id_familia == familia_id)
    )
    familia = result.scalar_one_or_none()
    if not familia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Familia no encontrada"
        )

    puntaje = await recalcular_puntaje_familia(db, familia_id)
    return {
        "id_familia": familia_id,
        "puntaje_prioridad": puntaje,
        "mensaje": "Puntaje calculado exitosamente",
    }