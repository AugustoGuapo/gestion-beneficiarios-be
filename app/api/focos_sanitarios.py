from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.foco_sanitario_service import FocoSanitarioService
from app.core.constants import UserRole
from app.core.security import check_role
from app.infrastructure.db.session import get_db
from app.schema.foco_sanitario_schema import (
    FocoSanitarioCreate,
    FocoSanitarioResponse,
    FocoSanitarioUpdate,
)
from app.schema.geojson_schema import GeoJSONFeatureCollection

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


@router.post("/", response_model=FocoSanitarioResponse, status_code=status.HTTP_201_CREATED, summary="Registrar un foco de riesgo sanitario")
async def crear_foco_sanitario(payload: FocoSanitarioCreate, current_user: dict = Depends(check_role(_ROLES_ESCRITURA)), db: AsyncSession = Depends(get_db)) -> FocoSanitarioResponse:
    """HU-25 — Registra un nuevo foco de riesgo sanitario asociado a una zona o refugio."""
    return await FocoSanitarioService.crear_foco(db, payload)


@router.get("/mapa", response_model=GeoJSONFeatureCollection, summary="Obtener focos sanitarios en formato GeoJSON para el mapa")
async def focos_sanitarios_geojson(incluir_resueltos: bool = False, current_user: dict = Depends(check_role(_ROLES_LECTURA)), db: AsyncSession = Depends(get_db)) -> GeoJSONFeatureCollection:
    """HU-26 — Retorna focos en formato GeoJSON. Por defecto solo ACTIVO y EN_ATENCION."""
    return await FocoSanitarioService.obtener_geojson(db, incluir_resueltos)


@router.get("/", response_model=list[FocoSanitarioResponse], summary="Listar focos sanitarios")
async def listar_focos_sanitarios(estado: str | None = None, nivel_riesgo: str | None = None, id_zona: int | None = None, current_user: dict = Depends(check_role(_ROLES_LECTURA)), db: AsyncSession = Depends(get_db)) -> list[FocoSanitarioResponse]:
    """Retorna todos los focos sanitarios. Filtrables por estado, nivel_riesgo e id_zona."""
    return await FocoSanitarioService.listar_focos(db, estado, nivel_riesgo, id_zona)


@router.get("/{foco_id}", response_model=FocoSanitarioResponse, summary="Obtener un foco sanitario por ID")
async def obtener_foco_sanitario(foco_id: int, current_user: dict = Depends(check_role(_ROLES_LECTURA)), db: AsyncSession = Depends(get_db)) -> FocoSanitarioResponse:
    """Obtiene un foco sanitario por su ID."""
    return await FocoSanitarioService.obtener_foco(db, foco_id)


@router.patch("/{foco_id}", response_model=FocoSanitarioResponse, summary="Actualizar estado y acciones de un foco sanitario")
async def actualizar_foco_sanitario(foco_id: int, payload: FocoSanitarioUpdate, current_user: dict = Depends(check_role(_ROLES_ESCRITURA)), db: AsyncSession = Depends(get_db)) -> FocoSanitarioResponse:
    """HU-25 — Actualiza estado, acciones tomadas, nivel de riesgo y coordenadas."""
    return await FocoSanitarioService.actualizar_foco(db, foco_id, payload)
