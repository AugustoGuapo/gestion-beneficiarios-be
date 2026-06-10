import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.persona import Persona
from app.domain.models.familia import Familia
from app.domain.models.configuracion_puntaje import ConfiguracionPuntaje
from app.domain.models.zona import Zona
from datetime import datetime

logger = logging.getLogger(__name__)

# Mapeo de nivel de riesgo a factor numérico
_FACTOR_ZONA: dict[str, float] = {
    "bajo": 1.0,
    "medio": 1.5,
    "alto": 2.0,
    "crítico": 3.0,
}


async def obtener_config(db: AsyncSession) -> dict:
    """Obtiene todas las configuraciones de puntaje como dict."""
    result = await db.execute(select(ConfiguracionPuntaje))
    configs = result.scalars().all()
    return {c.clave: c.valor for c in configs}


async def _obtener_factor_zona(db: AsyncSession, familia: Familia) -> float:
    """
    Calcula el factor multiplicador de zona basado en el nivel de riesgo
    de la zona donde reside la familia.
    """
    if familia.id_zona is None:
        return 1.0  # Sin zona asignada, factor neutral

    try:
        result = await db.execute(select(Zona).where(Zona.id_zona == familia.id_zona))
        zona = result.scalar_one_or_none()
        if zona is None:
            return 1.0

        nivel = zona.nivel_riesgo_tipo
        if nivel is None:
            return 1.0

        # Normalizar a string por si viene como enum
        nivel_str = str(nivel.value) if hasattr(nivel, "value") else str(nivel)
        return _FACTOR_ZONA.get(nivel_str, 1.0)
    except Exception:
        logger.exception("Error obteniendo factor zona para familia %s", familia.id_familia)
        return 1.0


async def recalcular_puntaje_familia(db: AsyncSession, familia_id: int) -> float:
    """
    Calcula y guarda el puntaje de prioridad para una familia.

    Fórmula:
        puntaje_base = (peso_miembros * n)
                     + (peso_nino * n_ninos)
                     + (peso_anciano * n_ancianos)
                     + (peso_embarazada * n_embarazadas)
                     + (peso_discapacidad * n_discapacitados)
                     + (peso_enfermedad * n_enfermedades)
                     + peso_dias_sin_ayuda * min(dias_sin_ayuda, tope_dias)

        puntaje_final = puntaje_base * factor_zona
    """
    config = await obtener_config(db)

    # Obtener personas de la familia
    result = await db.execute(
        select(Persona).where(Persona.id_familia == familia_id)
    )
    personas = result.scalars().all()

    n_miembros = len(personas)
    n_ninos = sum(1 for p in personas if p.es_nino)
    n_ancianos = sum(1 for p in personas if p.es_anciano)
    n_embarazadas = sum(1 for p in personas if p.es_embarazada)
    n_discapacitados = sum(1 for p in personas if p.tiene_discapacidad)
    n_enfermedades = sum(1 for p in personas if p.tiene_enfermedad_cronica)

    puntaje = (
        config.get("peso_miembros", 1.0) * n_miembros
        + config.get("peso_nino", 2.0) * n_ninos
        + config.get("peso_anciano", 2.5) * n_ancianos
        + config.get("peso_embarazada", 3.0) * n_embarazadas
        + config.get("peso_discapacidad", 2.0) * n_discapacitados
        + config.get("peso_enfermedad", 1.5) * n_enfermedades
    )

    # Obtener la familia para calcular factor zona y días sin ayuda
    result = await db.execute(
        select(Familia).where(Familia.id_familia == familia_id)
    )
    familia = result.scalar_one_or_none()
    if familia is None:
        return 0.0

    # Factor zona: multiplicador por nivel de riesgo
    factor_zona = await _obtener_factor_zona(db, familia)
    peso_zona_config = config.get("peso_zona", 1.0)
    puntaje *= factor_zona * peso_zona_config

    # Días sin ayuda: desde fecha de registro
    if familia.fecha_registro:
        dias_desde_registro = (datetime.utcnow() - familia.fecha_registro).days
        tope = int(config.get("tope_dias", 30))
        dias_considerados = min(max(dias_desde_registro, 0), tope)
        puntaje += config.get("peso_dias_sin_ayuda", 0.5) * dias_considerados

    # Guardar puntaje en la familia
    familia.puntaje_prioridad = round(puntaje, 2)
    await db.commit()
    await db.refresh(familia)

    return familia.puntaje_prioridad
