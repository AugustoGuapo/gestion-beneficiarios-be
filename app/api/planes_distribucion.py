from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.domain.models.plan_distribucion import PlanDistribucion, DetallePlanDistribucion
from app.core.security import get_current_user, check_role
from app.core.constants import UserRole
from app.schema.plan_distribucion_schema import (
    PlanDistribucionResponse,
    PlanDistribucionDetailResponse,
    DetallePlanResponse,
)
from app.application.services.plan_distribucion_service import generar_plan

router = APIRouter(prefix="/planes-distribucion", tags=["planes-distribucion"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[PlanDistribucionResponse])
async def get_planes(
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.COORDINADOR_LOGISTICA,
        UserRole.FUNCIONARIO_CONTROL,
        UserRole.OPERADOR_ENTREGAS,
    ])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlanDistribucion).order_by(PlanDistribucion.fecha_generacion.desc())
    )
    planes = result.scalars().all()
    return planes


@router.get("/{plan_id}", response_model=PlanDistribucionDetailResponse)
async def get_plan(
    plan_id: int,
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.COORDINADOR_LOGISTICA,
        UserRole.FUNCIONARIO_CONTROL,
        UserRole.OPERADOR_ENTREGAS,
    ])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlanDistribucion).where(PlanDistribucion.id_plan == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado"
        )

    result = await db.execute(
        select(DetallePlanDistribucion).where(
            DetallePlanDistribucion.id_plan == plan_id
        )
    )
    detalles = result.scalars().all()

    return PlanDistribucionDetailResponse.model_validate(
        {
            "id_plan": plan.id_plan,
            "fecha_generacion": plan.fecha_generacion,
            "estado": plan.estado,
            "id_familia": plan.id_familia,
            "puntaje_al_generar": plan.puntaje_al_generar,
            "prioridad_orden": plan.prioridad_orden,
            "detalles": [DetallePlanResponse.model_validate(d) for d in detalles],
        }
    )


@router.post("/generar")
async def generar_nuevo_plan(
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.COORDINADOR_LOGISTICA,
    ])),
    db: AsyncSession = Depends(get_db),
):
    """Genera un nuevo plan de distribución priorizado."""
    resultado = await generar_plan(db)
    return resultado
