from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.security import check_role
from app.infrastructure.db.session import get_db
from app.schema.reporte_zona_schema import ZonaSinEntregasResponse

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get(
    "/zonas-sin-entregas",
    response_model=list[ZonaSinEntregasResponse],
)
async def get_zonas_sin_entregas(
    _current_user: dict = Depends(
        check_role(
            [
                UserRole.ADMIN,
                UserRole.FUNCIONARIO_CONTROL,
            ]
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    query = """
        SELECT
            z.id_zona,
            z.nombre,
            z.nivel_riesgo_tipo AS nivel_riesgo,
            COUNT(DISTINCT f.id_familia) AS familias_por_zona
        FROM zona z
        JOIN ubicacion u ON u.id_zona = z.id_zona
        JOIN refugios r ON r.zona_id = z.id_zona
        JOIN familia_refugio fr ON fr.id_refugio = r.id
        JOIN familia f ON f.id_familia = fr.id_familia
        LEFT JOIN entrega e ON e.id_familia = f.id_familia
        WHERE e.id_entrega IS NULL
        GROUP BY z.id_zona, z.nombre, z.nivel_riesgo_tipo
        ORDER BY z.nivel_riesgo_tipo DESC, z.nombre ASC
    """

    result = await db.execute(text(query))

    return result.mappings().all()
