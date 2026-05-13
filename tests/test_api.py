"""
Tests de integración para la API.

Estos tests asumen que la base de datos PostgreSQL está corriendo
y que el schema inicial (scripts/init.sql) ya fue aplicado.
"""

import pytest
from httpx import AsyncClient


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
            json={"username": "Admin Principal", "password": "password"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Debe retornar 401 para credenciales inválidas."""
        response = await client.post(
            "/auth/login",
            json={"username": "usuario_inexistente", "password": "wrong"},
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
# Usuarios
# =============================================================================


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
        assert "nombre" in data