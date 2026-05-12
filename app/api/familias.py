from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.domain.models.familia import Familia
from app.core.security import get_current_user
from app.schema.familia_schema import FamiliaCreate, FamiliaResponse
from datetime import datetime

router = APIRouter(prefix="/familias", tags=["familias"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def generar_codigo_familia(db: Session) -> str:
    """Genera un código único con formato FAM-{año}-{NNNNN}."""
    year = datetime.utcnow().year
    result = await db.execute(func.max(Familia.id_familia))
    max_id = result.scalar()
    next_num = (max_id or 0) + 1
    return f"FAM-{year}-{next_num:05d}"


@router.get("/", response_model=list[FamiliaResponse])
async def get_familias(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(Familia).order_by(Familia.fecha_registro.desc()))
    familias = result.scalars().all()
    return familias


@router.get("/{familia_id}", response_model=FamiliaResponse)
async def get_familia(
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
    return familia


@router.post("/", response_model=FamiliaResponse, status_code=status.HTTP_201_CREATED)
async def create_familia(
    familia: FamiliaCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    get_current_user(token)

    if not familia.acepta_privacidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe aceptar la política de privacidad para registrar la familia",
        )

    codigo = await generar_codigo_familia(db)
    new_familia = Familia(
        codigo_familia=codigo,
        acepta_privacidad=familia.acepta_privacidad,
        fecha_registro=datetime.utcnow(),
        puntaje_prioridad=0.0,
    )
    db.add(new_familia)
    await db.commit()
    await db.refresh(new_familia)
    return new_familia