from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.security import check_role, get_current_user
from app.domain.models.foco_sanitario import FocoSanitario
from app.infrastructure.db.session import get_db
from app.schema.foco_sanitario_schema import (
    FocoSanitarioCreate,
    FocoSanitarioResponse,
    FocoSanitarioUpdate,
)
from app.schema.geojson_schema import (
    FocoSanitarioProperties,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONPoint,
)

router = APIRouter(prefix="/focos-sanitarios", tags=["Salubridad"])

_ROLES_LECTURA = [
    UserRole.ADMIN,
    UserRole.COORDINADOR_LOGISTICA,
    UserRole.FUNCIONARIO_CONTROL,
]

_ROLES_ESCRITURA = [
    UserRole.ADMIN,
    UserRole.COORDINADOR_LOGISTICA,
]


@router.post(
    "/",
    response_model=FocoSanitarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un foco de riesgo sanitario",
)
async def crear_foco_sanitario(
    payload: FocoSanitarioCreate,
    current_user: dict = Depends(check_role(_ROLES_ESCRITURA)),
    db: AsyncSession = Depends(get_db),
) -> FocoSanitarioResponse:
    """
    HU-25 — Registra un nuevo foco de riesgo sanitario asociado a una zona o albergue.

    - **tipo_vector**: AGUA_CONTAMINADA | INSECTOS | ROEDORES | RESIDUOS | OTRO
    - **nivel_riesgo**: BAJO | MEDIO | ALTO | CRITICO
    - **estado** inicial: ACTIVO (automático)
    """
    foco = FocoSanitario(**payload.model_dump())
    db.add(foco)
    await db.commit()
    await db.refresh(foco)
    return foco


@router.get(
    "/mapa",
    response_model=GeoJSONFeatureCollection,
    summary="Obtener focos sanitarios en formato GeoJSON para el mapa",
)
async def focos_sanitarios_geojson(
    incluir_resueltos: bool = False,
    current_user: dict = Depends(check_role(_ROLES_LECTURA)),
    db: AsyncSession = Depends(get_db),
) -> GeoJSONFeatureCollection:
    """
    HU-26 — Retorna los focos sanitarios en formato GeoJSON FeatureCollection.

    - Por defecto devuelve solo focos en estado **ACTIVO** y **EN_ATENCION**.
    - Con `incluir_resueltos=true` incluye también los resueltos.
    - Solo incluye focos que tengan coordenadas registradas (latitud y longitud).
    - Compatible con D3, Leaflet y cualquier librería de mapas estándar.
    """
    query = select(FocoSanitario).where(
        FocoSanitario.latitud.is_not(None),
        FocoSanitario.longitud.is_not(None),
    )

    if not incluir_resueltos:
        query = query.where(FocoSanitario.estado.in_(["ACTIVO", "EN_ATENCION"]))

    result = await db.execute(query)
    focos = result.scalars().all()

    features = [
        GeoJSONFeature(
            geometry=GeoJSONPoint(
                coordinates=[float(foco.longitud), float(foco.latitud)]
            ),
            properties=FocoSanitarioProperties(
                id_foco=foco.id_foco,
                tipo_vector=foco.tipo_vector,
                nivel_riesgo=foco.nivel_riesgo,
                estado=foco.estado,
                acciones_tomadas=foco.acciones_tomadas,
                fecha_registro=foco.fecha_registro.isoformat(),
                id_zona=foco.id_zona,
                id_albergue=foco.id_albergue,
            ),
        )
        for foco in focos
    ]

    return GeoJSONFeatureCollection(features=features)


@router.get(
    "/",
    response_model=list[FocoSanitarioResponse],
    summary="Listar focos sanitarios",
)
async def listar_focos_sanitarios(
    estado: str | None = None,
    nivel_riesgo: str | None = None,
    id_zona: int | None = None,
    current_user: dict = Depends(check_role(_ROLES_LECTURA)),
    db: AsyncSession = Depends(get_db),
) -> list[FocoSanitarioResponse]:
    """
    Retorna todos los focos sanitarios. Filtrables por estado, nivel_riesgo e id_zona.
    Por defecto devuelve todos los estados; el frontend puede filtrar ACTIVO y EN_ATENCION para el mapa (HU-26).
    """
    query = select(FocoSanitario)
    if estado:
        query = query.where(FocoSanitario.estado == estado.upper())
    if nivel_riesgo:
        query = query.where(FocoSanitario.nivel_riesgo == nivel_riesgo.upper())
    if id_zona:
        query = query.where(FocoSanitario.id_zona == id_zona)

    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/{foco_id}",
    response_model=FocoSanitarioResponse,
    summary="Obtener un foco sanitario por ID",
)
async def obtener_foco_sanitario(
    foco_id: int,
    current_user: dict = Depends(check_role(_ROLES_LECTURA)),
    db: AsyncSession = Depends(get_db),
) -> FocoSanitarioResponse:
    result = await db.execute(select(FocoSanitario).where(FocoSanitario.id_foco == foco_id))
    foco = result.scalar_one_or_none()
    if foco is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foco sanitario no encontrado.")
    return foco


@router.patch(
    "/{foco_id}",
    response_model=FocoSanitarioResponse,
    summary="Actualizar estado y acciones de un foco sanitario",
)
async def actualizar_foco_sanitario(
    foco_id: int,
    payload: FocoSanitarioUpdate,
    current_user: dict = Depends(check_role(_ROLES_ESCRITURA)),
    db: AsyncSession = Depends(get_db),
) -> FocoSanitarioResponse:
    """
    HU-25 — Permite actualizar estado, acciones tomadas, nivel de riesgo, tipo de vector y coordenadas.
    Cada cambio queda trazado en fecha_actualizacion.
    """
    result = await db.execute(select(FocoSanitario).where(FocoSanitario.id_foco == foco_id))
    foco = result.scalar_one_or_none()
    if foco is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foco sanitario no encontrado.")

    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(foco, campo, valor)
    foco.fecha_actualizacion = datetime.utcnow()

    await db.commit()
    await db.refresh(foco)
    return foco
