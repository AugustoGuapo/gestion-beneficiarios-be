"""Servicio de entregas (HU-22 + HU-23).

Implementa la logica de registrar una entrega individual de forma atomica:
- Valida familia y recursos.
- HU-23: bloquea duplicados por (id_familia, fecha_efectiva) y deja
  trazabilidad explicita en `audit_log`.
- Resuelve la bodega de la cual descontar (parametro del usuario o autoseleccion).
- Verifica stock suficiente por (recurso, bodega) usando movimiento_inventario.
- Genera un codigo legible secuencial por anio (ENT-AAAA-NNNNN).
- Crea la entrega + detalles + movimientos SALIDA en una sola transaccion.
- Actualiza el peso_actual_kg de la bodega para mantener consistencia con HU-11.
"""

import logging
from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.audit_log import AuditLog
from app.domain.models.bodega import Bodega
from app.domain.models.detalle_entrega import DetalleEntrega
from app.domain.models.entrega import Entrega
from app.domain.models.familia import Familia
from app.domain.models.movimiento_inventario import MovimientoInventario
from app.domain.models.recurso import Recurso
from app.infrastructure.db.session import SessionLocal
from app.schema.entrega_schema import (
    DetalleEntregaItem,
    DetalleEntregaResponse,
    EntregaCreate,
    EntregaResponse,
    EstadoEntrega,
)

logger = logging.getLogger(__name__)


class EntregaService:
    """Servicio que orquesta el registro de entregas (HU-22)."""

    @staticmethod
    async def _validar_familia(db: AsyncSession, id_familia: int) -> Familia:
        result = await db.execute(select(Familia).where(Familia.id_familia == id_familia))
        familia = result.scalar_one_or_none()
        if familia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Familia con id {id_familia} no existe",
            )
        return familia

    @staticmethod
    async def _validar_recursos(
        db: AsyncSession, items: list[DetalleEntregaItem]
    ) -> dict[int, Recurso]:
        """Carga los recursos referenciados y verifica que existan (y esten activos)."""
        ids = {it.id_recurso for it in items}
        if len(ids) != len(items):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se permite repetir el mismo recurso en los detalles",
            )

        result = await db.execute(select(Recurso).where(Recurso.id_recurso.in_(ids)))
        recursos = {r.id_recurso: r for r in result.scalars().all()}

        faltantes = ids - set(recursos.keys())
        if faltantes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recursos no encontrados: {sorted(faltantes)}",
            )

        inactivos = [rid for rid, rec in recursos.items() if getattr(rec, "activo", True) is False]
        if inactivos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Recursos inactivos no se pueden entregar: {sorted(inactivos)}",
            )

        return recursos

    @staticmethod
    async def _stock_recurso_en_bodega(db: AsyncSession, id_recurso: int, id_bodega: int) -> int:
        """Stock disponible = SUM(ENTRADA) - SUM(SALIDA) del recurso en la bodega."""
        entradas = await db.execute(
            select(func.coalesce(func.sum(MovimientoInventario.cantidad), 0)).where(
                MovimientoInventario.id_recurso == id_recurso,
                MovimientoInventario.id_bodega == id_bodega,
                MovimientoInventario.tipo == "ENTRADA",
            )
        )
        salidas = await db.execute(
            select(func.coalesce(func.sum(MovimientoInventario.cantidad), 0)).where(
                MovimientoInventario.id_recurso == id_recurso,
                MovimientoInventario.id_bodega == id_bodega,
                MovimientoInventario.tipo == "SALIDA",
            )
        )
        return int(entradas.scalar_one() or 0) - int(salidas.scalar_one() or 0)

    @staticmethod
    async def _resolver_bodega(
        db: AsyncSession,
        items: list[DetalleEntregaItem],
        id_bodega_preferida: int | None,
    ) -> Bodega:
        """Valida la bodega pedida o selecciona automaticamente una con stock suficiente.

        Si el cliente pasa `id_bodega`, se valida que exista y que cubra TODOS los items.
        Si no lo pasa, se recorren las bodegas en orden y se devuelve la primera que tenga
        stock suficiente para TODOS los items.
        """
        if id_bodega_preferida is not None:
            result = await db.execute(select(Bodega).where(Bodega.id_bodega == id_bodega_preferida))
            bodega = result.scalar_one_or_none()
            if bodega is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Bodega con id {id_bodega_preferida} no existe",
                )
            for it in items:
                stock = await EntregaService._stock_recurso_en_bodega(
                    db, it.id_recurso, bodega.id_bodega
                )
                if stock < it.cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Stock insuficiente en bodega {bodega.id_bodega} "
                            f"para recurso {it.id_recurso}: disponible {stock}, "
                            f"solicitado {it.cantidad}"
                        ),
                    )
            return bodega

        result = await db.execute(select(Bodega).order_by(Bodega.id_bodega))
        bodegas = list(result.scalars().all())
        if not bodegas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay bodegas registradas en el sistema",
            )

        for bodega in bodegas:
            cubre_todo = True
            for it in items:
                stock = await EntregaService._stock_recurso_en_bodega(
                    db, it.id_recurso, bodega.id_bodega
                )
                if stock < it.cantidad:
                    cubre_todo = False
                    break
            if cubre_todo:
                return bodega

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Ninguna bodega tiene stock suficiente para cubrir todos los recursos "
                "de la entrega. Considere dividir la entrega o especificar id_bodega."
            ),
        )

    @staticmethod
    async def _registrar_auditoria_duplicado(
        username: str | None,
        ip_address: str | None,
        id_familia: int,
        fecha_efectiva: date,
        entrega_existente: Entrega,
    ) -> None:
        """Persiste un registro explicito de intento bloqueado (HU-23).

        Usa una sesion independiente para asegurar que el log sobreviva al
        rollback de la transaccion principal de la entrega.
        """
        try:
            async with SessionLocal() as session:
                log = AuditLog(
                    username=username,
                    method="POST",
                    endpoint="/entregas/",
                    action="ENTREGA_DUPLICADA_BLOQUEADA",
                    status_code=status.HTTP_409_CONFLICT,
                    ip_address=ip_address,
                    payload={
                        "id_familia": id_familia,
                        "fecha_efectiva": str(fecha_efectiva),
                        "entrega_existente": {
                            "id_entrega": entrega_existente.id_entrega,
                            "codigo": entrega_existente.codigo,
                            "estado": entrega_existente.estado,
                        },
                    },
                )
                session.add(log)
                await session.commit()
        except Exception:
            logger.exception("Error registrando auditoria de entrega duplicada")

    @staticmethod
    async def _validar_no_duplicada(
        db: AsyncSession,
        id_familia: int,
        fecha_efectiva: date,
        username: str | None,
        ip_address: str | None,
    ) -> None:
        """HU-23: rechaza registrar otra entrega para la misma familia en el mismo dia.

        Reglas:
        - Se ignoran entregas con estado `ANULADA` (no cuentan como duplicado).
        - Se devuelve `409 Conflict` con datos de la entrega existente.
        - Se registra el intento bloqueado en `audit_log` con accion explicita.
        """
        result = await db.execute(
            select(Entrega).where(
                Entrega.id_familia == id_familia,
                Entrega.fecha_efectiva == fecha_efectiva,
                Entrega.estado != EstadoEntrega.ANULADA.value,
            )
        )
        duplicada = result.scalars().first()
        if duplicada is None:
            return

        await EntregaService._registrar_auditoria_duplicado(
            username=username,
            ip_address=ip_address,
            id_familia=id_familia,
            fecha_efectiva=fecha_efectiva,
            entrega_existente=duplicada,
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "ENTREGA_DUPLICADA",
                "message": (
                    f"Ya existe una entrega registrada para la familia {id_familia} "
                    f"en la fecha {fecha_efectiva}. No se permite duplicar."
                ),
                "entrega_existente": {
                    "id_entrega": duplicada.id_entrega,
                    "codigo": duplicada.codigo,
                    "estado": duplicada.estado,
                },
            },
        )

    @staticmethod
    async def _siguiente_codigo(db: AsyncSession) -> str:
        """Genera codigo secuencial por anio: ENT-AAAA-NNNNN."""
        anio = datetime.utcnow().year
        prefijo = f"ENT-{anio}-"
        result = await db.execute(
            select(func.count(Entrega.id_entrega)).where(Entrega.codigo.like(f"{prefijo}%"))
        )
        count = int(result.scalar_one() or 0)
        siguiente = count + 1
        return f"{prefijo}{siguiente:05d}"

    @staticmethod
    async def registrar_entrega(
        db: AsyncSession,
        payload: EntregaCreate,
        username: str | None = None,
        ip_address: str | None = None,
    ) -> EntregaResponse:
        """Registra una entrega individual de forma atomica (HU-22 + HU-23).

        Validaciones (en orden):
        1. Familia existe.
        2. HU-23: no existe otra entrega no anulada para la misma familia en
           la misma `fecha_efectiva`. Si existe, se aborta con 409 y se
           registra el intento en `audit_log`.
        3. Recursos existen, estan activos y sin duplicados.
        4. Bodega especificada existe (o hay una con stock suficiente para todo).
        5. Stock suficiente por recurso.

        Efectos (en la misma transaccion):
        - INSERT entrega (estado='ENTREGADA', codigo generado).
        - INSERT detalle_entrega por cada item.
        - INSERT movimiento_inventario tipo='SALIDA' por cada item.
        - UPDATE bodega.peso_actual_kg restando peso total entregado.
        """
        await EntregaService._validar_familia(db, payload.id_familia)

        fecha_efectiva = payload.fecha_efectiva or date.today()
        await EntregaService._validar_no_duplicada(
            db=db,
            id_familia=payload.id_familia,
            fecha_efectiva=fecha_efectiva,
            username=username,
            ip_address=ip_address,
        )

        recursos = await EntregaService._validar_recursos(db, payload.detalles)
        bodega = await EntregaService._resolver_bodega(db, payload.detalles, payload.id_bodega)

        codigo = await EntregaService._siguiente_codigo(db)

        try:
            entrega = Entrega(
                codigo=codigo,
                estado=EstadoEntrega.ENTREGADA.value,
                fecha_efectiva=fecha_efectiva,
                id_familia=payload.id_familia,
                coordenadas=payload.coordenadas,
                firma_digital=payload.firma_digital,
            )
            db.add(entrega)
            await db.flush()

            peso_total = Decimal("0")
            for item in payload.detalles:
                recurso = recursos[item.id_recurso]

                detalle = DetalleEntrega(
                    id_entrega=entrega.id_entrega,
                    id_recurso=item.id_recurso,
                    cantidad=item.cantidad,
                )
                db.add(detalle)

                movimiento = MovimientoInventario(
                    tipo="SALIDA",
                    cantidad=item.cantidad,
                    id_recurso=item.id_recurso,
                    id_bodega=bodega.id_bodega,
                )
                db.add(movimiento)

                peso_unitario = Decimal(str(recurso.peso_unitario_kg or 0))
                peso_total += peso_unitario * Decimal(item.cantidad)

            peso_actual = Decimal(str(bodega.peso_actual_kg or 0))
            nuevo_peso = peso_actual - peso_total
            if nuevo_peso < 0:
                nuevo_peso = Decimal("0")
            bodega.peso_actual_kg = nuevo_peso

            await db.commit()
        except HTTPException:
            await db.rollback()
            raise
        except Exception as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error registrando entrega: {exc}",
            ) from exc

        await db.refresh(entrega)

        detalles_resp = [
            DetalleEntregaResponse(
                id_detalle=d.id_detalle,
                id_recurso=d.id_recurso,
                nombre_recurso=recursos[d.id_recurso].nombre,
                cantidad=d.cantidad,
            )
            for d in entrega.detalles
        ]

        return EntregaResponse(
            id_entrega=entrega.id_entrega,
            codigo=entrega.codigo,
            estado=EstadoEntrega(entrega.estado),
            fecha=entrega.fecha,
            fecha_efectiva=entrega.fecha_efectiva,
            id_familia=entrega.id_familia,
            id_bodega=bodega.id_bodega,
            coordenadas=entrega.coordenadas,
            firma_digital=entrega.firma_digital,
            detalles=detalles_resp,
        )

    @staticmethod
    async def obtener_entrega(db: AsyncSession, id_entrega: int) -> EntregaResponse:
        result = await db.execute(select(Entrega).where(Entrega.id_entrega == id_entrega))
        entrega = result.scalar_one_or_none()
        if entrega is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entrega con id {id_entrega} no existe",
            )

        recursos_ids = {d.id_recurso for d in entrega.detalles}
        recursos_map: dict[int, Recurso] = {}
        if recursos_ids:
            res = await db.execute(select(Recurso).where(Recurso.id_recurso.in_(recursos_ids)))
            recursos_map = {r.id_recurso: r for r in res.scalars().all()}

        detalles_resp = [
            DetalleEntregaResponse(
                id_detalle=d.id_detalle,
                id_recurso=d.id_recurso,
                nombre_recurso=(
                    recursos_map[d.id_recurso].nombre if d.id_recurso in recursos_map else None
                ),
                cantidad=d.cantidad,
            )
            for d in entrega.detalles
        ]

        return EntregaResponse(
            id_entrega=entrega.id_entrega,
            codigo=entrega.codigo,
            estado=EstadoEntrega(entrega.estado),
            fecha=entrega.fecha,
            fecha_efectiva=entrega.fecha_efectiva,
            id_familia=entrega.id_familia,
            coordenadas=entrega.coordenadas,
            firma_digital=entrega.firma_digital,
            detalles=detalles_resp,
        )
