from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.infrastructure.db.base import Base


class PlanDistribucion(Base):
    __tablename__ = "plan_distribucion"

    id_plan = Column(Integer, primary_key=True, index=True)
    fecha_generacion = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(20), nullable=False, default="programada")
    id_familia = Column(
        Integer, ForeignKey("familia.id_familia"), nullable=False
    )
    puntaje_al_generar = Column(Float, nullable=False)
    prioridad_orden = Column(Integer, nullable=False)


class DetallePlanDistribucion(Base):
    __tablename__ = "detalle_plan_distribucion"

    id_detalle = Column(Integer, primary_key=True, index=True)
    id_plan = Column(
        Integer, ForeignKey("plan_distribucion.id_plan"), nullable=False
    )
    id_recurso = Column(
        Integer, ForeignKey("recurso.id_recurso"), nullable=False
    )
    cantidad_asignada = Column(Integer, nullable=False)
    cantidad_entregada = Column(Integer, default=0)