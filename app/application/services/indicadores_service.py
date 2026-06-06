from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.familia import Familia
from app.domain.models.foco_sanitario import FocoSanitario
from app.domain.models.inventario import Inventario
from app.domain.models.plan_distribucion import PlanDistribucion
from app.domain.models.recurso import Recurso
from app.schema.indicadores_schema import IndicadoresPanelResponse, RecursoDisponible


class IndicadoresService:
    """Servicio para el panel de indicadores clave — HU-27."""

    @staticmethod
    async def obtener_indicadores(db: AsyncSession) -> IndicadoresPanelResponse:

        # Total familias registradas
        total_familias = (
            await db.execute(select(func.count()).select_from(Familia))
        ).scalar_one()

        # Familias que tienen al menos un plan en estado 'entregada'
        familias_atendidas = (
            await db.execute(
                select(func.count(func.distinct(PlanDistribucion.id_familia))).where(
                    PlanDistribucion.estado == "entregada"
                )
            )
        ).scalar_one()

        familias_pendientes = total_familias - familias_atendidas

        # Planes por estado
        planes_programados = (
            await db.execute(
                select(func.count()).select_from(PlanDistribucion).where(
                    PlanDistribucion.estado == "programada"
                )
            )
        ).scalar_one()

        planes_entregados = (
            await db.execute(
                select(func.count()).select_from(PlanDistribucion).where(
                    PlanDistribucion.estado == "entregada"
                )
            )
        ).scalar_one()

        # Focos sanitarios por estado
        focos_activos = (
            await db.execute(
                select(func.count()).select_from(FocoSanitario).where(
                    FocoSanitario.estado == "ACTIVO"
                )
            )
        ).scalar_one()

        focos_en_atencion = (
            await db.execute(
                select(func.count()).select_from(FocoSanitario).where(
                    FocoSanitario.estado == "EN_ATENCION"
                )
            )
        ).scalar_one()

        # Recursos disponibles (join inventario + recurso)
        result = await db.execute(
            select(Recurso.nombre, Inventario.cantidad)
            .join(Inventario, Inventario.recurso_id == Recurso.id_recurso)
            .order_by(Recurso.nombre)
        )
        recursos = [
            RecursoDisponible(nombre=row.nombre, cantidad=row.cantidad)
            for row in result.all()
        ]

        return IndicadoresPanelResponse(
            total_familias=total_familias,
            familias_atendidas=familias_atendidas,
            familias_pendientes=familias_pendientes,
            planes_programados=planes_programados,
            planes_entregados=planes_entregados,
            focos_sanitarios_activos=focos_activos,
            focos_sanitarios_en_atencion=focos_en_atencion,
            recursos_disponibles=recursos,
        )
