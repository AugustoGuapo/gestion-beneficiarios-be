import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.familia import Familia
from app.application.services.inventario_service import InventarioService
from app.domain.models.plan_distribucion import PlanDistribucion, DetallePlanDistribucion
from app.domain.models.recurso import Recurso
from datetime import datetime

logger = logging.getLogger(__name__)


async def _obtener_recursos_disponibles(db: AsyncSession) -> list[dict]:
    """
    Consulta recursos con stock disponible desde MovimientoInventario.
    Retorna lista de {id_recurso, cantidad} ordenada por mayor stock primero.
    """
    consulta = await InventarioService.consultar(db, id_bodega=None)
    recursos = [
        {"id_recurso": linea.id_recurso, "cantidad": linea.cantidad_total}
        for linea in consulta.consolidado
        if linea.cantidad_total > 0
    ]
    recursos.sort(key=lambda r: r["cantidad"], reverse=True)
    return recursos


async def _asignar_recursos_por_familia(
    db: AsyncSession,
    plan_id: int,
    recursos_disponibles: list[dict],
    orden: int,
    total_familias: int,
) -> None:
    """
    Asigna recursos a una familia basado en el stock disponible.
    Distribuye equitativamente: a cada familia se le asigna 1 unidad de cada
    recurso prioritario (alimentos básicos, agua) que tenga stock suficiente.
    """
    # Recursos prioritarios: aquellos con categoría ALIMENTOS y stock >= 2
    for recurso in recursos_disponibles:
        if recurso["cantidad"] < 2:
            continue  # No hay suficiente stock

        # Verificar que el recurso sea de tipo ALIMENTOS (prioritario)
        result = await db.execute(
            select(Recurso).where(Recurso.id_recurso == recurso["id_recurso"])
        )
        rec = result.scalar_one_or_none()
        if rec is None or rec.categoria != "ALIMENTOS":
            continue

        detalle = DetallePlanDistribucion(
            id_plan=plan_id,
            id_recurso=recurso["id_recurso"],
            cantidad_asignada=1,
            cantidad_entregada=0,
        )
        db.add(detalle)

        # Descontar del stock disponible para la siguiente familia
        recurso["cantidad"] -= 1


async def generar_plan(db: AsyncSession) -> dict:
    """
    Genera un plan de distribución priorizado.

    Algoritmo:
    1. Obtener recursos disponibles con stock en inventario
    2. Obtener familias elegibles (con puntaje > 0, sin plan activo)
    3. Ordenar por puntaje descendente
    4. Para cada familia, crear entrada en plan_distribucion
    5. Asignar recursos según stock disponible (distribución equitativa)
    """
    recursos_disponibles = await _obtener_recursos_disponibles(db)

    if not recursos_disponibles:
        return {
            "mensaje": "No hay stock disponible para generar un plan de distribución",
            "total_familias": 0,
        }

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
    total_familias = len(familias_elegibles)

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

        # Asignar recursos según stock disponible
        await _asignar_recursos_por_familia(
            db, plan.id_plan, recursos_disponibles, orden, total_familias
        )

        planes_creados += 1

    await db.commit()

    return {
        "mensaje": f"Plan generado exitosamente para {planes_creados} familias",
        "total_familias": planes_creados,
    }
