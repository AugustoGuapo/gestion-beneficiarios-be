import uuid

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token


def make_auth_header(rol: str) -> dict:
    token = create_access_token(1, "test@sgah.com", rol)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
class TestRecursos:
    async def test_create_recurso_ok(self, client: AsyncClient):
        headers = make_auth_header("REGISTRADOR_DONACIONES")
        # Unicidad nombre+categoría en DB: nombre fijo hace 409 al repetir make test.
        nombre = f"Arroz Premium test-{uuid.uuid4().hex[:12]}"
        payload = {
            "nombre": nombre,
            "categoria": "ALIMENTOS",
            "unidad_medida": "KG",
            "peso_unitario_kg": 1.0,
            "id_origen": 1,
        }
        resp = await client.post("/recursos/", json=payload, headers=headers)
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["nombre"] == payload["nombre"]
        assert data["categoria"] == payload["categoria"]

    async def test_create_recurso_duplicate(self, client: AsyncClient):
        headers = make_auth_header("REGISTRADOR_DONACIONES")
        nombre = f"Aceite Premium test-{uuid.uuid4().hex[:12]}"
        payload = {
            "nombre": nombre,
            "categoria": "ALIMENTOS",
            "unidad_medida": "LITRO",
            "peso_unitario_kg": 1.0,
        }
        await client.post("/recursos/", json=payload, headers=headers)
        resp = await client.post("/recursos/", json=payload, headers=headers)
        assert resp.status_code == 409

    async def test_create_recurso_unauthorized(self, client: AsyncClient):
        payload = {
            "nombre": "Colchoneta",
            "categoria": "COLCHONETA",
            "unidad_medida": "UNIDAD",
            "peso_unitario_kg": 3.5,
        }
        resp = await client.post("/recursos/", json=payload)
        assert resp.status_code == 401

    async def test_create_recurso_forbidden(self, client: AsyncClient):
        headers = make_auth_header("CENSADOR")
        payload = {
            "nombre": "Sabanas",
            "categoria": "COBIJA",
            "unidad_medida": "UNIDAD",
            "peso_unitario_kg": 1.2,
        }
        resp = await client.post("/recursos/", json=payload, headers=headers)
        assert resp.status_code == 403

    async def test_list_recursos(self, client: AsyncClient):
        headers = make_auth_header("COORDINADOR_LOGISTICA")
        resp = await client.get("/recursos/", headers=headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
