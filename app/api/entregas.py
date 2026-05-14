"""Router de entregas (HU-22 + HU-23)."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.entrega_service import EntregaService
from app.core.constants import UserRole
from app.core.security import check_role
from app.infrastructure.db.session import get_db
from app.schema.entrega_schema import EntregaCreate, EntregaResponse

router = APIRouter(prefix="/entregas", tags=["entregas"])

_ROLES_PERMITIDOS = [
    UserRole.ADMIN,
    UserRole.OPERADOR_ENTREGAS,
    UserRole.COORDINADOR_LOGISTICA,
]


@router.post(
    "/",
    response_model=EntregaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar entrega individual a una familia (HU-22 + HU-23)",
)
async def registrar_entrega(
    payload: EntregaCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_role(_ROLES_PERMITIDOS)),
) -> EntregaResponse:
    """Registra una entrega individual a una familia.

    Reglas:
    - **HU-22**: la familia debe existir, los recursos deben existir y estar
      activos, y debe haber stock suficiente en la bodega elegida (o en alguna
      del sistema si no se especifica `id_bodega`). La operacion es atomica.
    - **HU-23**: si ya existe una entrega no anulada para la misma familia en
      la misma `fecha_efectiva`, se rechaza con `409 Conflict` y se registra
      el intento en `audit_log` (action = `ENTREGA_DUPLICADA_BLOQUEADA`).
    """
    username = current_user.get("email") if isinstance(current_user, dict) else None
    ip_address = request.client.host if request.client else None
    return await EntregaService.registrar_entrega(
        db, payload, username=username, ip_address=ip_address
    )


@router.get(
    "/{id_entrega}",
    response_model=EntregaResponse,
    summary="Obtener detalle de una entrega",
)
async def obtener_entrega(
    id_entrega: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_role(_ROLES_PERMITIDOS)),
) -> EntregaResponse:
    return await EntregaService.obtener_entrega(db, id_entrega)
