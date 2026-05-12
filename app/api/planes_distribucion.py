from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.domain.models.plan_distribucion import PlanDistribucion, DetallePlanDistribucion
from app.core.security import get_current_user
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
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(
        select(PlanDistribucion).order_by(PlanDistribucion.fecha_generacion.desc())
    )
    planes = result.scalars().all()
    return planes


@router.get("/{plan_id}", response_model=PlanDistribucionDetailResponse)
async def get_plan(
    plan_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    get_current_user(token)

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

    return PlanDistribucionDetailResponse(
        id_plan=plan.id_plan,
        fecha_generacion=plan.fecha_generacion,
        estado=plan.estado,
        id_familia=plan.id_familia,
        puntaje_al_generar=plan.puntaje_al_generar,
        prioridad_orden=plan.prioridad_orden,
        detalles=[DetallePlanResponse.model_validate(d) for d in detalles],
    )


@router.post("/generar")
async def generar_nuevo_plan(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Genera un nuevo plan de distribución priorizado."""
    get_current_user(token)
    resultado = await generar_plan(db)
    return resultado