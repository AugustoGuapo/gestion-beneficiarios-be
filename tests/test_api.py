"""
Tests de integración para la API.

Estos tests asumen que la base de datos PostgreSQL está corriendo
y que el schema inicial (scripts/init.sql) ya fue aplicado.
"""

import pytest
from httpx import AsyncClient

from app.core.constants import UserRole
from app.core.security import create_access_token

# =============================================================================
# Auth
# =============================================================================


@pytest.mark.integration
class TestAuth:
    """Tests del endpoint de autenticación."""

    async def test_login_success(self, client: AsyncClient):
        """Debe retornar token para credenciales válidas."""
        response = await client.post(
            "/auth/login",
            json={"correo": "admin@sgah.com", "password": "Admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Debe retornar 401 para credenciales inválidas."""
        response = await client.post(
            "/auth/login",
            json={"correo": "noexiste@sgah.com", "password": "Admin123"},
        )
        assert response.status_code == 401

    async def test_login_missing_fields(self, client: AsyncClient):
        """Debe retornar 422 si faltan campos."""
        response = await client.post("/auth/login", json={})
        assert response.status_code == 422


# =============================================================================
# Health Check
# =============================================================================


class TestHealth:
    """Tests básicos de que la app responde."""

    async def test_docs_accessible(self, client: AsyncClient):
        """La documentación debe ser accesible."""
        response = await client.get("/docs")
        assert response.status_code == 200

    async def test_openapi_accessible(self, client: AsyncClient):
        """El schema OpenAPI debe ser accesible."""
        response = await client.get("/openapi.json")
        assert response.status_code == 200


# =============================================================================
# Personas
# =============================================================================


@pytest.mark.integration
class TestPersonas:
    """Tests del CRUD de personas."""

    async def test_list_personas(self, client_auth: AsyncClient):
        """Debe listar personas con autenticación."""
        response = await client_auth.get("/personas/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_list_personas_unauthorized(self, client: AsyncClient):
        """Debe rechazar sin token."""
        response = await client.get("/personas/")
        assert response.status_code == 401

    async def test_get_persona_by_id(self, client_auth: AsyncClient):
        """Debe retornar una persona por ID."""
        response = await client_auth.get("/personas/1")
        assert response.status_code == 200
        data = response.json()
        assert "nombre" in data
        assert "id_persona" in data

    async def test_get_persona_not_found(self, client_auth: AsyncClient):
        """Debe retornar 404 para ID inexistente."""
        response = await client_auth.get("/personas/99999")
        assert response.status_code == 404

    async def test_create_persona(self, client_auth: AsyncClient, sample_persona_data: dict):
        """Debe crear una persona."""
        response = await client_auth.post("/personas/", json=sample_persona_data)
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["nombre"] == sample_persona_data["nombre"]


# =============================================================================
# Zonas
# =============================================================================


@pytest.mark.integration
class TestZonas:
    """Tests del CRUD de zonas."""

    async def test_list_zonas(self, client_auth: AsyncClient):
        """Debe listar zonas con autenticación."""
        response = await client_auth.get("/zonas/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_list_zonas_unauthorized(self, client: AsyncClient):
        """Debe rechazar sin token."""
        response = await client.get("/zonas/")
        assert response.status_code == 401

    async def test_get_zona_by_id(self, client_auth: AsyncClient):
        """Debe retornar una zona por ID."""
        response = await client_auth.get("/zonas/1")
        assert response.status_code == 200
        data = response.json()
        assert "nombre" in data

    async def test_get_zona_not_found(self, client_auth: AsyncClient):
        """Debe retornar 404 para ID inexistente."""
        response = await client_auth.get("/zonas/99999")
        assert response.status_code == 404


# =============================================================================
# Inventario (HU-15)
# =============================================================================


@pytest.mark.integration
class TestInventario:
    """Stock por bodega desde movimiento_inventario."""

    async def test_inventario_sin_filtro(self, client_auth: AsyncClient):
        response = await client_auth.get("/inventario/")
        assert response.status_code == 200
        data = response.json()
        assert "bodegas" in data and "consolidado" in data
        assert len(data["bodegas"]) >= 2
        b1 = next(b for b in data["bodegas"] if b["id_bodega"] == 1)
        arroz = next(l for l in b1["lineas"] if l["id_recurso"] == 1)
        assert arroz["cantidad_disponible"] == 450
        assert arroz["alerta_activa"] is False
        assert arroz["umbral_alerta"] is None
        cons_arroz = next(c for c in data["consolidado"] if c["id_recurso"] == 1)
        assert cons_arroz["cantidad_total"] == 450

    async def test_inventario_filtrado_por_bodega(self, client_auth: AsyncClient):
        response = await client_auth.get("/inventario/", params={"id_bodega": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["bodegas"]) == 1
        assert data["bodegas"][0]["id_bodega"] == 2
        ids_recursos = {l["id_recurso"] for l in data["bodegas"][0]["lineas"]}
        assert ids_recursos == {6, 8}
        agua = next(l for l in data["bodegas"][0]["lineas"] if l["id_recurso"] == 6)
        assert agua["cantidad_disponible"] == 600

    async def test_inventario_bodega_inexistente(self, client_auth: AsyncClient):
        response = await client_auth.get("/inventario/", params={"id_bodega": 99999})
        assert response.status_code == 404

    async def test_inventario_sin_token(self, client: AsyncClient):
        response = await client.get("/inventario/")
        assert response.status_code == 401

    async def test_inventario_rol_no_autorizado(self, client: AsyncClient):
        token = create_access_token(1, "censador@test.com", UserRole.CENSADOR.value)
        response = await client.get(
            "/inventario/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_inventario_operador_entregas(self, client: AsyncClient):
        token = create_access_token(2, "op@test.com", UserRole.OPERADOR_ENTREGAS.value)
        response = await client.get(
            "/inventario/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


@pytest.mark.integration
class TestInventarioAlertasHu16:
    """HU-16 — umbral por recurso y listado de alertas."""

    async def test_alertas_vacio_sin_umbral(self, client_auth: AsyncClient):
        r = await client_auth.get("/inventario/alertas")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["alertas"] == []

    async def test_umbral_dispara_alerta_y_linea_inventario(self, client_auth: AsyncClient):
        patch = await client_auth.patch(
            "/recursos/1/umbral-alerta",
            json={"umbral_alerta": 451},
        )
        assert patch.status_code == 200
        assert patch.json()["umbral_alerta"] == 451

        inv = await client_auth.get("/inventario/")
        assert inv.status_code == 200
        b1 = next(b for b in inv.json()["bodegas"] if b["id_bodega"] == 1)
        arroz = next(l for l in b1["lineas"] if l["id_recurso"] == 1)
        assert arroz["cantidad_disponible"] == 450
        assert arroz["umbral_alerta"] == 451
        assert arroz["alerta_activa"] is True

        alert = await client_auth.get("/inventario/alertas")
        assert alert.status_code == 200
        body = alert.json()
        assert body["total"] >= 1
        a0 = next(a for a in body["alertas"] if a["id_recurso"] == 1 and a["id_bodega"] == 1)
        assert a0["cantidad_disponible"] == 450
        assert a0["umbral_alerta"] == 451

        clear = await client_auth.patch(
            "/recursos/1/umbral-alerta",
            json={"umbral_alerta": None},
        )
        assert clear.status_code == 200
        assert clear.json()["umbral_alerta"] is None

        alert2 = await client_auth.get("/inventario/alertas")
        assert alert2.json()["total"] == 0

    async def test_patch_umbral_recurso_inexistente(self, client_auth: AsyncClient):
        r = await client_auth.patch(
            "/recursos/99999/umbral-alerta",
            json={"umbral_alerta": 10},
        )
        assert r.status_code == 404

    async def test_patch_umbral_rol_no_autorizado(self, client: AsyncClient):
        token = create_access_token(1, "c@test.com", UserRole.CENSADOR.value)
        r = await client.patch(
            "/recursos/1/umbral-alerta",
            json={"umbral_alerta": 100},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 403

    async def test_alertas_bodega_inexistente(self, client_auth: AsyncClient):
        r = await client_auth.get("/inventario/alertas", params={"id_bodega": 99999})
        assert r.status_code == 404


@pytest.mark.integration
class TestUsuarios:
    """Tests del CRUD de usuarios."""

    async def test_list_usuarios(self, client_auth: AsyncClient):
        """Debe listar usuarios con autenticación."""
        response = await client_auth.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_usuario_by_id(self, client_auth: AsyncClient):
        """Debe retornar un usuario por ID."""
        response = await client_auth.get("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert "nombre_completo" in data


# =============================================================================
# Entregas (HU-12 / HU-22 / HU-23)
# =============================================================================


@pytest.mark.integration
class TestEntregas:
    """Tests del endpoint de entregas."""

    async def test_registrar_entrega_ok(self, client_auth: AsyncClient):
        """Debe registrar una entrega exitosamente."""
        response = await client_auth.post(
            "/entregas/",
            json={
                "id_familia": 1,
                "detalles": [{"id_recurso": 1, "cantidad": 2}],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["codigo"].startswith("ENT-")
        assert data["estado"] == "ENTREGADA"
        assert len(data["detalles"]) == 1
        assert data["detalles"][0]["id_recurso"] == 1

    async def test_registrar_entrega_familia_inexistente(self, client_auth: AsyncClient):
        """Debe retornar 404 para familia inexistente."""
        response = await client_auth.post(
            "/entregas/",
            json={
                "id_familia": 99999,
                "detalles": [{"id_recurso": 1, "cantidad": 1}],
            },
        )
        assert response.status_code == 404

    async def test_registrar_entrega_recurso_inexistente(self, client_auth: AsyncClient):
        """Debe retornar 404 para recurso inexistente."""
        response = await client_auth.post(
            "/entregas/",
            json={
                "id_familia": 1,
                "detalles": [{"id_recurso": 99999, "cantidad": 1}],
            },
        )
        assert response.status_code == 404

    async def test_registrar_entrega_recurso_duplicado(self, client_auth: AsyncClient):
        """Debe retornar 400 si se repite el mismo recurso."""
        response = await client_auth.post(
            "/entregas/",
            json={
                "id_familia": 1,
                "detalles": [
                    {"id_recurso": 1, "cantidad": 1},
                    {"id_recurso": 1, "cantidad": 2},
                ],
            },
        )
        assert response.status_code == 400

    async def test_registrar_entrega_unauthorized(self, client: AsyncClient):
        """Debe retornar 401 sin token."""
        response = await client.post(
            "/entregas/",
            json={
                "id_familia": 1,
                "detalles": [{"id_recurso": 1, "cantidad": 1}],
            },
        )
        assert response.status_code == 401


# =============================================================================
# Planes de distribución (HU-21)
# =============================================================================


@pytest.mark.integration
class TestPlanesDistribucion:
    """Tests del endpoint de planes de distribución."""

    async def test_generar_plan(self, client_auth: AsyncClient):
        """Debe generar un plan de distribución."""
        response = await client_auth.post("/planes-distribucion/generar")
        assert response.status_code == 200
        data = response.json()
        assert "mensaje" in data

    async def test_listar_planes(self, client_auth: AsyncClient):
        """Debe listar planes de distribución."""
        response = await client_auth.get("/planes-distribucion/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
