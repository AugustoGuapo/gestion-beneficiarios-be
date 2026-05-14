from collections import defaultdict
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.bodega import Bodega
from app.domain.models.movimiento_inventario import MovimientoInventario
from app.domain.models.recurso import Recurso
from app.schema.inventario_schema import (
    InventarioConsolidadoLinea,
    InventarioConsultaResponse,
    InventarioLineaRecurso,
    InventarioPorBodega,
)
from app.schema.recurso_schema import CategoriaRecurso, UnidadMedida


def _suma_entrada_menos_salida():
    return func.sum(
        case(
            (MovimientoInventario.tipo == "ENTRADA", MovimientoInventario.cantidad),
            (MovimientoInventario.tipo == "SALIDA", -MovimientoInventario.cantidad),
            else_=0,
        )
    )


def _filtros_movimiento_validos():
    return (
        MovimientoInventario.id_bodega.isnot(None),
        MovimientoInventario.id_recurso.isnot(None),
        MovimientoInventario.tipo.in_(("ENTRADA", "SALIDA")),
        MovimientoInventario.cantidad.isnot(None),
    )


class InventarioService:
    """Cálculo de stock a partir de movimientos (sin duplicar reglas en routers)."""

    @staticmethod
    async def _bodega_existe(db: AsyncSession, id_bodega: int) -> bool:
        res = await db.execute(select(Bodega.id_bodega).where(Bodega.id_bodega == id_bodega))
        return res.scalar_one_or_none() is not None

    @staticmethod
    async def _stock_rows(
        db: AsyncSession,
        id_bodega: int | None,
    ) -> Sequence[tuple[int, str, int, str, str, str, int]]:
        suma = _suma_entrada_menos_salida()
        where_clauses = list(_filtros_movimiento_validos())
        if id_bodega is not None:
            where_clauses.append(MovimientoInventario.id_bodega == id_bodega)

        inner = (
            select(
                MovimientoInventario.id_bodega,
                MovimientoInventario.id_recurso,
                suma.label("cantidad_disponible"),
            )
            .where(*where_clauses)
            .group_by(MovimientoInventario.id_bodega, MovimientoInventario.id_recurso)
            .having(suma > 0)
        )

        sub = inner.subquery()
        stmt = (
            select(
                sub.c.id_bodega,
                Bodega.nombre,
                sub.c.id_recurso,
                Recurso.nombre,
                Recurso.categoria,
                Recurso.unidad_medida,
                sub.c.cantidad_disponible,
            )
            .select_from(sub)
            .join(Bodega, Bodega.id_bodega == sub.c.id_bodega)
            .join(Recurso, Recurso.id_recurso == sub.c.id_recurso)
        )
        result = await db.execute(stmt)
        return result.all()

    @staticmethod
    def _consolidado_desde_filas(
        filas: Sequence[tuple[int, str, int, str, str, str, int]],
    ) -> list[InventarioConsolidadoLinea]:
        totales: dict[int, tuple[str, CategoriaRecurso, UnidadMedida, int]] = {}
        for _bid, _bnom, rid, rnom, cat, um, qty in filas:
            rid_i = int(rid)
            qty_i = int(qty)
            if rid_i not in totales:
                totales[rid_i] = (
                    str(rnom),
                    CategoriaRecurso(str(cat)),
                    UnidadMedida(str(um)),
                    qty_i,
                )
            else:
                nom, c, u, prev = totales[rid_i]
                totales[rid_i] = (nom, c, u, prev + qty_i)
        return [
            InventarioConsolidadoLinea(
                id_recurso=rid,
                nombre=nom,
                categoria=cat,
                unidad_medida=um,
                cantidad_total=total,
            )
            for rid, (nom, cat, um, total) in sorted(totales.items(), key=lambda x: x[0])
        ]

    @staticmethod
    async def consultar(db: AsyncSession, id_bodega: int | None) -> InventarioConsultaResponse:
        if id_bodega is not None:
            if not await InventarioService._bodega_existe(db, id_bodega):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Bodega no encontrada",
                )

        filas = await InventarioService._stock_rows(db, id_bodega)
        lineas_por_bodega: dict[int, list[InventarioLineaRecurso]] = defaultdict(list)

        for bid, _bnom, rid, rnom, cat, um, qty in filas:
            lineas_por_bodega[int(bid)].append(
                InventarioLineaRecurso(
                    id_recurso=int(rid),
                    nombre=str(rnom),
                    categoria=CategoriaRecurso(str(cat)),
                    unidad_medida=UnidadMedida(str(um)),
                    cantidad_disponible=int(qty),
                )
            )

        if id_bodega is not None:
            res_bodega = await db.execute(select(Bodega).where(Bodega.id_bodega == id_bodega))
            bodega = res_bodega.scalar_one()
            bodegas_out = [
                InventarioPorBodega(
                    id_bodega=int(bodega.id_bodega),
                    nombre=str(bodega.nombre),
                    lineas=sorted(
                        lineas_por_bodega.get(int(bodega.id_bodega), []),
                        key=lambda l: l.id_recurso,
                    ),
                )
            ]
        else:
            res_todas = await db.execute(select(Bodega).order_by(Bodega.id_bodega))
            todas = res_todas.scalars().all()
            bodegas_out = [
                InventarioPorBodega(
                    id_bodega=int(b.id_bodega),
                    nombre=str(b.nombre),
                    lineas=sorted(
                        lineas_por_bodega.get(int(b.id_bodega), []),
                        key=lambda l: l.id_recurso,
                    ),
                )
                for b in todas
            ]

        consolidado = InventarioService._consolidado_desde_filas(filas)
        return InventarioConsultaResponse(bodegas=bodegas_out, consolidado=consolidado)
