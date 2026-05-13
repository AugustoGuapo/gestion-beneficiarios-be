"""Servicio para generar el plan de distribución priorizado (HU-21).

Reglas de negocio:

- Días de cobertura mínimos: 3 (configurable, no se permite menor).
- Ración: kg fijos por persona/día (default 0.5), configurable vía query.
- Score de priorización combinado:
    score = (vulnerabilidad_representante * peso_vulnerabilidad)
          + (nivel_riesgo_zona * peso_riesgo)
  donde:
    - vulnerabilidad_representante: 3 si embarazada, 2 si niño o anciano, 0 en otro caso.
    - nivel_riesgo_zona: crítico=4, alto=3, medio=2, bajo=1, sin albergue=0.
- El plan NO se persiste; se calcula on-demand y se retorna ordenado de mayor a menor score.

Nota: la base actual (`scripts/init.sql`) no relaciona personas con familias salvo a
través de `familia.id_representante`. Por eso se asume un número fijo de personas por
familia (`personas_por_familia`, default 4). Cuando exista la relación persona ↔ familia,
este servicio debe pasar a contar miembros reales.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domain.models.albergue import Albergue
from app.domain.models.familia import Familia
from app.domain.models.familia_albergue import FamiliaAlbergue
from app.domain.models.persona import Persona
from app.domain.models.ubicacion import Ubicacion
from app.domain.models.zona import Zona
from app.schema.distribucion_schema import PlanItem, PlanResponse
from app.schema.zona_schema import NivelRiesgoTipo

PESO_VULNERABILIDAD = 3.0
PESO_RIESGO_ZONA = 2.0

RIESGO_VALOR = {
    NivelRiesgoTipo.critico: 4,
    NivelRiesgoTipo.alto: 3,
    NivelRiesgoTipo.medio: 2,
    NivelRiesgoTipo.bajo: 1,
}


def _vulnerabilidad_representante(persona: Persona | None) -> int:
    if persona is None:
        return 0
    if persona.es_embarazada:
        return 3
    if persona.es_nino or persona.es_anciano:
        return 2
    return 0


def _valor_riesgo(nivel: NivelRiesgoTipo | None) -> int:
    if nivel is None:
        return 0
    return RIESGO_VALOR.get(nivel, 0)


class DistribucionService:
    """Lógica para construir el plan priorizado."""

    @staticmethod
    async def generar_plan(
        db: AsyncSession,
        dias_cobertura: int = 3,
        racion_kg_persona_dia: float = 0.5,
        personas_por_familia: int = 4,
    ) -> PlanResponse:
        rep = aliased(Persona)

        # Trae familia + representante + (opcionalmente) albergue/zona vía LEFT JOINs.
        stmt = (
            select(Familia, rep, Albergue, Zona)
            .outerjoin(rep, Familia.id_representante == rep.id_persona)
            .outerjoin(FamiliaAlbergue, FamiliaAlbergue.id_familia == Familia.id_familia)
            .outerjoin(Albergue, Albergue.id_albergue == FamiliaAlbergue.id_albergue)
            .outerjoin(Ubicacion, Ubicacion.id_ubicacion == Albergue.id_ubicacion)
            .outerjoin(Zona, Zona.id_zona == Ubicacion.id_zona)
        )

        result = await db.execute(stmt)
        rows = result.all()

        items: list[PlanItem] = []
        total_kg = 0.0
        for familia, representante, albergue, zona in rows:
            nivel_riesgo = (
                zona.nivel_riesgo_tipo if zona is not None and zona.nivel_riesgo_tipo else None
            )

            vulnerabilidad = _vulnerabilidad_representante(representante)
            valor_riesgo = _valor_riesgo(nivel_riesgo)

            score = (vulnerabilidad * PESO_VULNERABILIDAD) + (valor_riesgo * PESO_RIESGO_ZONA)
            racion_kg = round(
                personas_por_familia * dias_cobertura * racion_kg_persona_dia,
                2,
            )
            total_kg += racion_kg

            items.append(
                PlanItem(
                    id_familia=familia.id_familia,
                    representante=representante.nombre if representante else None,
                    id_albergue=albergue.id_albergue if albergue else None,
                    nombre_albergue=albergue.nombre if albergue else None,
                    id_zona=zona.id_zona if zona else None,
                    nombre_zona=zona.nombre if zona else None,
                    nivel_riesgo=nivel_riesgo,
                    personas_estimadas=personas_por_familia,
                    vulnerables=1 if vulnerabilidad > 0 else 0,
                    racion_kg=racion_kg,
                    dias_cobertura=dias_cobertura,
                    score=score,
                )
            )

        items.sort(key=lambda x: x.score, reverse=True)

        return PlanResponse(
            parametros={
                "dias_cobertura": dias_cobertura,
                "racion_kg_persona_dia": racion_kg_persona_dia,
                "personas_por_familia": personas_por_familia,
                "peso_vulnerabilidad": PESO_VULNERABILIDAD,
                "peso_riesgo_zona": PESO_RIESGO_ZONA,
            },
            total_familias=len(items),
            total_kg_requeridos=round(total_kg, 2),
            items=items,
        )
