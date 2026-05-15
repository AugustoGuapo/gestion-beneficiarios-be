"""Endpoints del módulo de traslados de familia entre refugios (HU-24)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.traslado_service import TrasladoService
from app.core.security import get_current_user
from app.infrastructure.db.session import get_db
from app.schema.traslado_schema import TrasladoCreate, TrasladoResponse

router = APIRouter(prefix="/traslados", tags=["traslados"])


@router.post(
    "/",
    response_model=TrasladoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trasladar una familia entre refugios (HU-24)",
)
async def trasladar_familia(
    payload: TrasladoCreate,
    _current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Traslada una familia de su refugio actual al refugio destino indicado.

    **Atomicidad:**
    En una sola transacción se cierra la asignación previa, se abre la nueva
    y se actualiza la `ocupacion_actual` de ambos refugios. Ante cualquier
    error se hace rollback completo.

    **Errores comunes:**
    - 400: el refugio destino es el mismo que el actual.
    - 404: familia o refugio destino no encontrados.
    - 409: la familia no tiene refugio asignado actualmente o el destino no
      tiene capacidad suficiente.
    """
    return await TrasladoService.trasladar_familia(db=db, payload=payload)
