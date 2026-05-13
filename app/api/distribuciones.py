"""Endpoints del módulo de distribución (HU-21)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.distribucion_service import DistribucionService
from app.core.security import get_current_user
from app.infrastructure.db.session import get_db
from app.schema.distribucion_schema import PlanResponse

router = APIRouter(prefix="/distribuciones", tags=["distribución"])


@router.get(
    "/plan",
    response_model=PlanResponse,
    summary="Generar plan de distribución priorizado (HU-21)",
)
async def generar_plan_distribucion(
    dias_cobertura: int = Query(
        default=3,
        ge=3,
        le=30,
        description="Días de cobertura por familia. Mínimo 3 según HU-21.",
    ),
    racion_kg_persona_dia: float = Query(
        default=0.5,
        gt=0,
        le=5,
        description="Kilogramos por persona por día (default 0.5).",
    ),
    personas_por_familia: int = Query(
        default=4,
        ge=1,
        le=20,
        description=(
            "Personas asumidas por familia mientras no exista relación persona ↔ familia en DB."
        ),
    ),
    _current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Genera el plan priorizado de distribución a partir del estado actual de la DB.

    **Reglas:**
    - Mínimo 3 días de cobertura por familia.
    - Priorización combinada: vulnerabilidad del representante + nivel_riesgo de la zona
      del albergue donde se encuentra la familia.
    - No persiste el plan; se calcula on-demand.

    **Permisos:** requiere estar autenticado.
    """
    return await DistribucionService.generar_plan(
        db=db,
        dias_cobertura=dias_cobertura,
        racion_kg_persona_dia=racion_kg_persona_dia,
        personas_por_familia=personas_por_familia,
    )
