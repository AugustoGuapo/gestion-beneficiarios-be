from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.indicadores_service import IndicadoresService
from app.core.constants import UserRole
from app.core.security import check_role
from app.infrastructure.db.session import get_db
from app.schema.indicadores_schema import IndicadoresPanelResponse

router = APIRouter(prefix="/indicadores", tags=["Reportes"])

_ROLES_PERMITIDOS = [
    UserRole.ADMIN,
    UserRole.COORDINADOR_LOGISTICA,
    UserRole.FUNCIONARIO_CONTROL,
]


@router.get(
    "/",
    response_model=IndicadoresPanelResponse,
    summary="Panel de indicadores clave del sistema",
)
async def obtener_indicadores(
    current_user: dict = Depends(check_role(_ROLES_PERMITIDOS)),
    db: AsyncSession = Depends(get_db),
) -> IndicadoresPanelResponse:
    """
    HU-27 — Retorna los indicadores clave de la operación:

    - Total de familias registradas, atendidas y pendientes
    - Planes de distribución programados y entregados
    - Focos sanitarios activos y en atención
    - Recursos disponibles por tipo en inventario
    """
    return await IndicadoresService.obtener_indicadores(db)
