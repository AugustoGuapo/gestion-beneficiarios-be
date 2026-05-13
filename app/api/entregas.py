"""Endpoints del módulo de Entregas (HU-22 + HU-23)."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.entrega_service import EntregaService
from app.core.security import get_current_user
from app.infrastructure.db.session import get_db
from app.schema.entrega_schema import EntregaCreate, EntregaResponse

router = APIRouter(prefix="/entregas", tags=["entregas"])


@router.post(
    "/",
    response_model=EntregaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar entrega individual (HU-22 + HU-23)",
)
async def registrar_entrega(
    payload: EntregaCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Registra una entrega individual a una familia.

    **Comportamiento (transaccional):**
    1. Valida que exista la familia y los recursos.
    2. **HU-23** — Bloquea entregas duplicadas: si ya existe una entrega no anulada
       para la misma familia en la misma `fecha_efectiva`, retorna 409 con mensaje
       claro y registra el intento en `audit_log` (action='DUPLICATE_BLOCKED').
    3. Valida stock suficiente por recurso.
    4. Genera un código `ENT-AAAA-NNNNN` único y secuencial por año.
    5. Inserta la `entrega` con estado='ENTREGADA', sus líneas en `detalle_entrega`
       y los movimientos `SALIDA` en `movimiento_inventario`.

    **Errores comunes:**
    - 404: familia, recurso o bodega no encontrados.
    - 409: stock insuficiente, entrega duplicada (HU-23) o conflicto de integridad.
    """
    ip_address = request.client.host if request.client else None
    return await EntregaService.registrar_entrega(
        db=db,
        payload=payload,
        username=current_user.get("email"),
        ip_address=ip_address,
    )
