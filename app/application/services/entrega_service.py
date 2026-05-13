"""Servicio del módulo de Entregas (HU-22).

Responsabilidades:
- Validar existencia de familia y recursos.
- Validar stock suficiente por recurso (calculado desde `movimiento_inventario`).
- Generar código `ENT-AAAA-NNNNN` secuencial por año.
- Ejecutar el registro de entrega en una sola transacción:
    1) INSERT en `entrega` con estado='ENTREGADA' y codigo generado.
    2) INSERT en `detalle_entrega` por cada item.
    3) INSERT en `movimiento_inventario` (tipo='SALIDA') por cada item, contra la bodega
       indicada o la primera bodega con stock suficiente.
"""

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.audit_log import AuditLog
from app.domain.models.bodega import Bodega
from app.domain.models.detalle_entrega import DetalleEntrega
from app.domain.models.entrega import Entrega
from app.domain.models.familia import Familia
from app.domain.models.movimiento_inventario import MovimientoInventario
from app.domain.models.recurso import Recurso
from app.infrastructure.db.session import SessionLocal
from app.schema.entrega_schema import DetalleEntregaItem, EntregaCreate

CODIGO_PREFIJO = "ENT"
CODIGO_PADDING = 5


def _formatear_codigo(anio: int, secuencial: int) -> str:
    return f"{CODIGO_PREFIJO}-{anio:04d}-{secuencial:0{CODIGO_PADDING}d}"


class EntregaService:
    """Lógica de negocio para registrar entregas individuales (HU-22)."""

    @staticmethod
    async def _stock_por_recurso(
        db: AsyncSession,
        id_recurso: int,
        id_bodega: int | None,
    ) -> int:
        """Calcula stock disponible = SUM(ENTRADA) - SUM(SALIDA) para un recurso.

        Si `id_bodega` se provee, filtra solo movimientos de esa bodega.
        """
        stmt = select(
            func.coalesce(
                func.sum(
                    case(
                        (MovimientoInventario.tipo == "ENTRADA", MovimientoInventario.cantidad),
                        else_=-MovimientoInventario.cantidad,
                    )
                ),
                0,
            )
        ).where(MovimientoInventario.id_recurso == id_recurso)

        if id_bodega is not None:
            stmt = stmt.where(MovimientoInventario.id_bodega == id_bodega)

        result = await db.execute(stmt)
        stock = result.scalar_one()
        return int(stock or 0)

    @staticmethod
    async def _resolver_bodega_para_descontar(
        db: AsyncSession,
        id_recurso: int,
        cantidad: int,
    ) -> int | None:
        """Devuelve la primera bodega con stock suficiente para descontar `cantidad`.

        Si no se encuentra una bodega con stock suficiente, devuelve None.
        """
        stmt = (
            select(
                MovimientoInventario.id_bodega,
                func.sum(
                    case(
                        (MovimientoInventario.tipo == "ENTRADA", MovimientoInventario.cantidad),
                        else_=-MovimientoInventario.cantidad,
                    )
                ).label("stock"),
            )
            .where(MovimientoInventario.id_recurso == id_recurso)
            .group_by(MovimientoInventario.id_bodega)
            .order_by(MovimientoInventario.id_bodega.asc())
        )

        result = await db.execute(stmt)
        for id_bodega, stock in result.all():
            if id_bodega is not None and int(stock or 0) >= cantidad:
                return int(id_bodega)
        return None

    @staticmethod
    async def _siguiente_codigo(db: AsyncSession, anio: int) -> str:
        """Calcula el próximo código secuencial ENT-AAAA-NNNNN.

        Toma el MAX(codigo) que empiece con el prefijo del año y suma 1.
        Para concurrencia real, en Postgres se recomienda usar una secuencia dedicada
        o un advisory lock; aquí confiamos en el UNIQUE INDEX sobre `entrega.codigo`
        para detectar colisiones (la transacción reintenta o falla 409).
        """
        prefijo = f"{CODIGO_PREFIJO}-{anio:04d}-"
        stmt = select(func.max(Entrega.codigo)).where(Entrega.codigo.like(f"{prefijo}%"))
        result = await db.execute(stmt)
        max_codigo: str | None = result.scalar_one()

        siguiente = 1
        if max_codigo:
            try:
                siguiente = int(max_codigo.rsplit("-", 1)[-1]) + 1
            except ValueError:
                siguiente = 1

        return _formatear_codigo(anio, siguiente)

    @staticmethod
    async def _validar_familia(db: AsyncSession, id_familia: int) -> None:
        familia = await db.get(Familia, id_familia)
        if familia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Familia {id_familia} no encontrada",
            )

    @staticmethod
    async def _registrar_auditoria_duplicado(
        username: str | None,
        ip_address: str | None,
        payload: EntregaCreate,
        id_entrega_existente: int,
        codigo_existente: str | None,
    ) -> None:
        """Registra en `audit_log` el intento bloqueado por entrega duplicada (HU-23).

        Usa una sesión independiente (`SessionLocal`) para que el registro de
        auditoría persista incluso si la transacción principal fue revertida.
        """
        try:
            async with SessionLocal() as audit_db:
                audit_db.add(
                    AuditLog(
                        username=username,
                        method="POST",
                        endpoint="/entregas/",
                        action="DUPLICATE_BLOCKED",
                        status_code=status.HTTP_409_CONFLICT,
                        ip_address=ip_address,
                        payload={
                            "motivo": "entrega duplicada (misma familia y misma fecha)",
                            "id_familia": payload.id_familia,
                            "fecha_efectiva": payload.fecha_efectiva.isoformat(),
                            "entrega_existente_id": id_entrega_existente,
                            "entrega_existente_codigo": codigo_existente,
                        },
                    )
                )
                await audit_db.commit()
        except Exception:
            # Auditoría es best-effort: nunca debe tumbar el flujo principal.
            pass

    @staticmethod
    async def _validar_no_duplicada(
        db: AsyncSession,
        payload: EntregaCreate,
        username: str | None,
        ip_address: str | None,
    ) -> None:
        """HU-23: bloquea entregas duplicadas (misma familia + misma fecha_efectiva).

        Las entregas con estado='ANULADA' no se consideran (se permite re-entregar
        si una previa fue anulada).
        """
        stmt = (
            select(Entrega.id_entrega, Entrega.codigo)
            .where(
                Entrega.id_familia == payload.id_familia,
                Entrega.fecha_efectiva == payload.fecha_efectiva,
                Entrega.estado != "ANULADA",
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        row = result.first()

        if row is None:
            return

        id_existente, codigo_existente = row
        await EntregaService._registrar_auditoria_duplicado(
            username=username,
            ip_address=ip_address,
            payload=payload,
            id_entrega_existente=id_existente,
            codigo_existente=codigo_existente,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Entrega duplicada: la familia {payload.id_familia} ya tiene una entrega "
                f"registrada para la fecha {payload.fecha_efectiva.isoformat()} "
                f"(entrega existente: {codigo_existente or id_existente})."
            ),
        )

    @staticmethod
    async def _validar_y_resolver_items(
        db: AsyncSession,
        items: list[DetalleEntregaItem],
    ) -> list[tuple[DetalleEntregaItem, int]]:
        """Valida que los recursos existan y que haya stock suficiente.

        Devuelve la lista de (item, id_bodega_a_descontar). Si el cliente no envió
        bodega, se resuelve automáticamente.
        Lanza HTTPException 404 si un recurso no existe y 409 si no hay stock.
        """
        resueltos: list[tuple[DetalleEntregaItem, int]] = []

        for item in items:
            recurso = await db.get(Recurso, item.id_recurso)
            if recurso is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Recurso {item.id_recurso} no encontrado",
                )

            if item.id_bodega is not None:
                bodega = await db.get(Bodega, item.id_bodega)
                if bodega is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Bodega {item.id_bodega} no encontrada",
                    )
                stock = await EntregaService._stock_por_recurso(db, item.id_recurso, item.id_bodega)
                if stock < item.cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            f"Stock insuficiente para recurso {item.id_recurso} "
                            f"en bodega {item.id_bodega}: hay {stock}, se requieren "
                            f"{item.cantidad}"
                        ),
                    )
                resueltos.append((item, item.id_bodega))
                continue

            id_bodega = await EntregaService._resolver_bodega_para_descontar(
                db, item.id_recurso, item.cantidad
            )
            if id_bodega is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"No hay bodega con stock suficiente para recurso "
                        f"{item.id_recurso} (cantidad requerida: {item.cantidad})"
                    ),
                )
            resueltos.append((item, id_bodega))

        return resueltos

    @staticmethod
    async def registrar_entrega(
        db: AsyncSession,
        payload: EntregaCreate,
        username: str | None = None,
        ip_address: str | None = None,
    ) -> Entrega:
        await EntregaService._validar_familia(db, payload.id_familia)
        await EntregaService._validar_no_duplicada(
            db=db,
            payload=payload,
            username=username,
            ip_address=ip_address,
        )
        items_resueltos = await EntregaService._validar_y_resolver_items(db, payload.items)

        anio = (payload.fecha_efectiva or date.today()).year
        codigo = await EntregaService._siguiente_codigo(db, anio)

        try:
            entrega = Entrega(
                codigo=codigo,
                fecha_efectiva=payload.fecha_efectiva,
                id_familia=payload.id_familia,
                coordenadas=payload.coordenadas,
                firma_digital=payload.firma_digital,
                estado="ENTREGADA",
            )
            db.add(entrega)
            await db.flush()

            for item, id_bodega in items_resueltos:
                db.add(
                    DetalleEntrega(
                        id_entrega=entrega.id_entrega,
                        id_recurso=item.id_recurso,
                        cantidad=item.cantidad,
                    )
                )
                db.add(
                    MovimientoInventario(
                        tipo="SALIDA",
                        cantidad=item.cantidad,
                        id_recurso=item.id_recurso,
                        id_bodega=id_bodega,
                    )
                )

            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se pudo registrar la entrega por conflicto de integridad: {e.orig}",
            ) from e

        result = await db.execute(
            select(Entrega)
            .options(selectinload(Entrega.detalles))
            .where(Entrega.id_entrega == entrega.id_entrega)
        )
        return result.scalar_one()
