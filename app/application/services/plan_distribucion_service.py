from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.familia import Familia
from app.domain.models.plan_distribucion import PlanDistribucion, DetallePlanDistribucion
from datetime import datetime


async def generar_plan(db: AsyncSession) -> dict:
    """
    Genera un plan de distribución priorizado.

    Algoritmo:
    1. Obtener familias elegibles (con puntaje > 0, sin plan activo)
    2. Ordenar por puntaje descendente
    3. Para cada familia, crear entrada en plan_distribucion
    4. Asignar recursos según stock disponible (placeholder)

    NOTA: La asignación de stock requiere coordinación con HU-19 (Dev 3).
    Por ahora se asigna una cantidad base fija.
    """
    # Familias con plan activo (programada o en_curso)
    subquery_planes_activos = (
        select(PlanDistribucion.id_familia)
        .where(PlanDistribucion.estado.in_(["programada", "en_curso"]))
    )
    result = await db.execute(subquery_planes_activos)
    familias_con_plan = {row[0] for row in result.fetchall()}

    # Familias elegibles: con puntaje > 0 y sin plan activo
    result = await db.execute(
        select(Familia)
        .where(Familia.puntaje_prioridad > 0)
        .order_by(Familia.puntaje_prioridad.desc())
    )
    familias_elegibles = result.scalars().all()

    # Filtrar las que ya tienen plan activo
    familias_elegibles = [
        f for f in familias_elegibles if f.id_familia not in familias_con_plan
    ]

    if not familias_elegibles:
        return {
            "mensaje": "No hay familias elegibles para generar un plan",
            "total_familias": 0,
        }

    planes_creados = 0
    for orden, familia in enumerate(familias_elegibles, start=1):
        plan = PlanDistribucion(
            fecha_generacion=datetime.utcnow(),
            estado="programada",
            id_familia=familia.id_familia,
            puntaje_al_generar=familia.puntaje_prioridad,
            prioridad_orden=orden,
        )
        db.add(plan)
        await db.flush()  # Obtener id_plan sin commit

        # Asignación de stock base (placeholder hasta integrar HU-19 de Dev 3)
        # TODO: Consultar stock disponible y asignar según disponibilidad
        recursos_base = [
            {"id_recurso": 1, "cantidad": 2},  # Arroz x 5kg
            {"id_recurso": 2, "cantidad": 1},  # Aceite x 1L
            {"id_recurso": 6, "cantidad": 2},  # Agua potable x 5L
        ]

        for recurso in recursos_base:
            detalle = DetallePlanDistribucion(
                id_plan=plan.id_plan,
                id_recurso=recurso["id_recurso"],
                cantidad_asignada=recurso["cantidad"],
                cantidad_entregada=0,
            )
            db.add(detalle)

        planes_creados += 1

    await db.commit()

    return {
        "mensaje": f"Plan generado exitosamente para {planes_creados} familias",
        "total_familias": planes_creados,
    }
