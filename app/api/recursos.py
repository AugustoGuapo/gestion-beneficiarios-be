from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.recurso_service import RecursoService
from app.core.constants import UserRole
from app.core.security import check_role
from app.infrastructure.db.session import get_db
from app.schema.recurso_schema import RecursoCreate, RecursoResponse, RecursoUmbralAlertaUpdate

router = APIRouter(prefix="/recursos", tags=["recursos"])

_RECURSO_EDITOR_ROLES = [UserRole.REGISTRADOR_DONACIONES, UserRole.COORDINADOR_LOGISTICA]

_UMBRAL_ALERTA_ROLES = [
    UserRole.ADMIN,
    UserRole.COORDINADOR_LOGISTICA,
    UserRole.REGISTRADOR_DONACIONES,
]


@router.post(
    "/",
    response_model=RecursoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar tipo de recurso",
    response_description="Recurso creado",
)
async def create_recurso(
    recurso_create: RecursoCreate,
    _current_user: Annotated[dict, Depends(check_role(_RECURSO_EDITOR_ROLES))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Alta en el catálogo base (HU-14).

    Roles: **REGISTRADOR_DONACIONES** o **COORDINADOR_LOGISTICA**.
    Unicidad lógica por combinación ``nombre`` + ``categoria`` (HTTP 409 si existe).
    """
    return await RecursoService.create_recurso(db, recurso_create)


@router.get(
    "/",
    response_model=list[RecursoResponse],
    summary="Listar tipos de recurso",
)
async def list_recursos(
    _current_user: Annotated[dict, Depends(check_role(_RECURSO_EDITOR_ROLES))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Catálogo de recursos. Mismos roles que POST."""
    return await RecursoService.list_recursos(db)


@router.patch(
    "/{id_recurso}/umbral-alerta",
    response_model=RecursoResponse,
    summary="Configurar umbral de alerta de inventario (HU-16)",
)
async def patch_umbral_alerta(
    id_recurso: Annotated[int, Path(description="ID del tipo de recurso", ge=1)],
    payload: RecursoUmbralAlertaUpdate,
    _current_user: Annotated[dict, Depends(check_role(_UMBRAL_ALERTA_ROLES))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Establece o limpia (null) el umbral por recurso. No afecta movimientos ni donaciones.
    """
    return await RecursoService.update_umbral_alerta(db, id_recurso, payload)
