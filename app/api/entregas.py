"""Router de entregas (HU-22): Registrar entrega individual."""

from fastapi import APIRouter, Depends, status
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
    summary="Registrar entrega individual a una familia (HU-22)",
)
async def registrar_entrega(
    payload: EntregaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(check_role(_ROLES_PERMITIDOS)),
) -> EntregaResponse:
    """Registra una entrega individual a una familia.

    Reglas (HU-22):
    - La familia debe existir.
    - Todos los recursos solicitados deben existir y estar activos.
    - Debe haber stock suficiente del recurso en la bodega elegida (o en alguna
      bodega del sistema si no se especifica `id_bodega`).
    - La operacion es atomica: si algo falla, no se persiste nada.
    - Al concretar la entrega se registra un movimiento `SALIDA` por cada recurso
      y se actualiza el `peso_actual_kg` de la bodega usada.
    """
    return await EntregaService.registrar_entrega(db, payload)


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
