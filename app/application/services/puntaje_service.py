from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.domain.models.persona import Persona
from app.domain.models.familia import Familia
from app.domain.models.configuracion_puntaje import ConfiguracionPuntaje
from app.domain.models.zona import Zona
from datetime import datetime, timezone


async def obtener_config(db: Session) -> dict:
    """Obtiene todas las configuraciones de puntaje como dict."""
    result = await db.execute(select(ConfiguracionPuntaje))
    configs = result.scalars().all()
    return {c.clave: c.valor for c in configs}


async def recalcular_puntaje_familia(db: Session, familia_id: int) -> float:
    """
    Calcula y guarda el puntaje de prioridad para una familia.

    Fórmula:
        puntaje = (peso_miembros * n)
                + (peso_nino * n_ninos)
                + (peso_anciano * n_ancianos)
                + (peso_embarazada * n_embarazadas)
                + (peso_discapacidad * n_discapacitados)
                + (peso_enfermedad * n_enfermedades)
                + peso_zona * factor_zona
                + peso_dias_sin_ayuda * min(dias_sin_ayuda, tope_dias)
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

    # Factor zona (si la familia tiene representante con ubicación)
    # Por ahora usamos peso_zona directamente como multiplicador base
    puntaje += config.get("peso_zona", 1.0) * 0  # placeholder para integración con ubicación

    # Días sin ayuda: calculados desde la última entrega o fecha de registro
    result = await db.execute(
        select(Familia).where(Familia.id_familia == familia_id)
    )
    familia = result.scalar_one_or_none()
    if familia and familia.fecha_registro:
        dias_desde_registro = (datetime.now(timezone.utc) - familia.fecha_registro).days
        tope = config.get("tope_dias", 30)
        dias_considerados = min(dias_desde_registro, tope)
        puntaje += config.get("peso_dias_sin_ayuda", 0.5) * dias_considerados

    # Guardar puntaje en la familia
    familia.puntaje_prioridad = round(puntaje, 2)
    await db.commit()
    await db.refresh(familia)

    return familia.puntaje_prioridad