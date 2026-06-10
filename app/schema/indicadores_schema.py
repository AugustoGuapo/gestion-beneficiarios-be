from pydantic import BaseModel


class RecursoDisponible(BaseModel):
    nombre: str
    cantidad: float


class IndicadoresPanelResponse(BaseModel):
    total_familias: int
    familias_atendidas: int
    familias_pendientes: int
    planes_programados: int
    planes_entregados: int
    focos_sanitarios_activos: int
    focos_sanitarios_en_atencion: int
    recursos_disponibles: list[RecursoDisponible]
