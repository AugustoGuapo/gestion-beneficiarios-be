from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.inventario_service import InventarioService
from app.core.constants import UserRole
from app.core.security import check_role
from app.infrastructure.db.session import get_db
from app.schema.inventario_schema import InventarioConsultaResponse

router = APIRouter(prefix="/inventario", tags=["inventario"])

_INVENTARIO_ROLES = [
    UserRole.ADMIN,
    UserRole.COORDINADOR_LOGISTICA,
    UserRole.OPERADOR_ENTREGAS,
]


@router.get(
    "/",
    response_model=InventarioConsultaResponse,
    summary="Consultar inventario por bodega (HU-15)",
)
async def get_inventario(
    _current_user: Annotated[dict, Depends(check_role(_INVENTARIO_ROLES))],
    db: Annotated[AsyncSession, Depends(get_db)],
    id_bodega: Annotated[
        int | None,
        Query(description="Filtrar por bodega; omitir para todas las bodegas"),
    ] = None,
):
    """
    Devuelve líneas de stock por bodega (solo movimientos con saldo > 0) y un consolidado
    en el alcance de la consulta. Los totales reflejan el estado actual de la base de datos.
    """
    return await InventarioService.consultar(db, id_bodega)
