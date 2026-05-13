"""
Fixtures compartidos para tests.

Provee:
- Cliente HTTP async para testear la API
- Sesión de base de datos de prueba
- Token JWT pre-generado para endpoints protegidos
"""
import os
import sys
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Asegurar que el proyecto está en el path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.core.security import create_access_token


@pytest.fixture(scope="session")
def anyio_backend():
    """Configuración de backend async para toda la sesión."""
    return "asyncio"


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Cliente HTTP async preparado para testear la API.
    Usa ASGITransport para comunicación directa sin red.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        timeout=30,
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers() -> dict:
    """
    Genera headers de autenticación con un token JWT válido.
    El token expira en 60 minutos (configuración por defecto).
    """
    token = create_access_token("Admin Principal")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def client_auth(client: AsyncClient, auth_headers: dict) -> AsyncClient:
    """
    Cliente HTTP con autenticación pre-configurada.
    Útil para tests de endpoints protegidos.
    """
    client.headers.update(auth_headers)
    return client


@pytest.fixture
def sample_persona_data() -> dict:
    """Datos de ejemplo para crear una persona."""
    return {
        "nombre": "Test Persona",
        "edad": 30,
        "es_nino": False,
        "es_anciano": False,
        "es_embarazada": False,
    }


@pytest.fixture
def sample_user_data() -> dict:
    """Datos de ejemplo para crear un usuario."""
    return {
        "nombre": "Usuario Test",
        "rol": "VOLUNTARIO",
    }


@pytest.fixture
def sample_zona_data() -> dict:
    """Datos de ejemplo para crear una zona."""
    return {"nombre": "Zona Test", "nivel_riesgo": "medio"}
