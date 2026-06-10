from pydantic import BaseModel
from datetime import datetime


class DetallePlanResponse(BaseModel):
    id_detalle: int
    id_plan: int
    id_recurso: int
    cantidad_asignada: int
    cantidad_entregada: int

    class Config:
        from_attributes = True


class PlanDistribucionResponse(BaseModel):
    id_plan: int
    fecha_generacion: datetime
    estado: str
    id_familia: int
    puntaje_al_generar: float
    prioridad_orden: int

    class Config:
        from_attributes = True


class PlanDistribucionDetailResponse(PlanDistribucionResponse):
    detalles: list[DetallePlanResponse] = []