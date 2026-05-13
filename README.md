# Gestión de Beneficiarios - Backend

API REST para la gestión de beneficiarios en situaciones de emergencia. Proyecto del diplomado institucional 2026-1 de la Universidad de Córdoba, Montería, Colombia.

## Stack Tecnológico

| Tecnología | Propósito |
|------------|----------|
| **FastAPI** | Framework web async (Python 3.12+) |
| **PostgreSQL 16** | Base de datos relacional |
| **SQLAlchemy 2.0** | ORM asíncrono |
| **python-jose** | Generación y verificación de JWT |
| **Docker + Compose** | Contenerización |
| **Pydantic v2** | Validación de datos y schemas |
| **Ruff** | Linter y formatter (reemplaza flake8/black/isort) |
| **pytest + httpx** | Tests de integración async |
| **pre-commit** | Hooks automáticos de calidad |
| **GitHub Actions** | CI: lint + test automatizados |

## Arquitectura del Proyecto

El proyecto sigue una arquitectura **Clean Architecture / Hexagonal** con separación clara de responsabilidades:

```
app/
├── main.py                 # Punto de entrada de la aplicación
├── api/                  # Capa de presentación (Routers/Controllers)
│   ├── auth.py          # Endpoints de autenticación
│   ├── users.py        # CRUD de usuarios
│   ├── personas.py     # CRUD de personas
│   └── zonas.py       # CRUD de zonas
├── domain/             # Capa de dominio (Modelos de negocio)
│   └── models/         # Modelos SQLAlchemy
│       ├── user.py
│       ├── persona.py
│       └── zona.py
├── schema/             # Schemas Pydantic (DTOs)
│   ├── user_schema.py
│   ├── persona_schema.py
│   └── zona_schema.py
├── core/              # Configuración centralizada
│   ├── config.py      # Settings (DB, JWT)
│   └── security.py   # Funciones JWT
└── infrastructure/    # Capa de infraestructura
    └── db/          # Conexión a PostgreSQL
        ├── session.py
        └── base.py
```

### Flujo de datos

```
Request → API (Router) → Schema (Validación) → Domain (Modelo) → Infrastructure (DB)
                           ↓
                      Security (JWT)
```

## Patrones Utilizados

### 1. Repository Pattern (implícito)
Los modelos en `domain/models/` actúan como repositories que se comunican directamente con la DB a través de SQLAlchemy.

### 2. DTO Pattern
Los schemas en `schema/` cumplen el rol de Data Transfer Objects para validar requests y formatear responses.

### 3. Dependency Injection
FastAPI maneja la inyección de dependencias:
- `Depends(get_db)` para la sesión de DB
- `Depends(oauth2_scheme)` para JWT

### 4. async/await
Toda la aplicación es asíncrona:
- Endpoints con `async def`
- Queries con `await db.execute()`
- SQLAlchemy AsyncSession

### 5. JWT Bearer Flow
- Endpoint `/auth/login` genera token
- Headers `Authorization: Bearer <token>` en requests
- Dependency `get_current_user()` verifica token

## Requisitos

- Python 3.12+
- Docker Desktop
- Docker Compose

## Installation

### 1. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con los valores deseados.

### 2. Iniciar servicios

```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:8000`

### 3. Verificar salud

```bash
curl http://localhost:8000/docs
```

## Documentación interactiva y colección Postman

La API expone documentación OpenAPI/Swagger automáticamente en `/docs` y `/redoc`.

- Uso recomendado: primero explorar y probar endpoints en **Swagger UI** (`/docs`).
- Si necesitas compartir o ejecutar escenarios de prueba, importa la colección Postman incluida: `SGAH_Collection.postman_collection.json`.

La colección ya contiene scripts para guardar el token y variables de entorno.


## Variables de Entorno

| Variable | Descripción | Default |
|----------|------------|---------|
| `DB_USER` | Usuario de PostgreSQL | root |
| `DB_PASSWORD` | Contraseña de PostgreSQL | root |
| `DB_HOST` | Host de la DB | db |
| `DB_PORT` | Puerto de la DB | 5432 |
| `DB_NAME` | Nombre de la base de datos | gestion_beneficiarios |
| `JWT_SECRET_KEY` | Clave secreta para JWT | (generar propia) |
| `JWT_ALGORITHM` | Algoritmo de firma | HS256 |
| `JWT_EXPIRATION_MINUTES` | Expiración del token | 60 |

## Endpoints

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/login` | Generar token JWT |

**Request:**
```json
{
  "correo": "admin@sgah.com",
  "password": "cualquiera"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Usuarios

| Método | Endpoint | Descripción | Auth |
|--------|----------|------------|------|
| GET | `/users/` | Listar todos los usuarios (solo ADMIN y COORDINADOR_LOGISTICA) | ✅ |
| GET | `/users/{id}` | Obtener usuario por ID | ✅ |
| POST | `/users/` | Crear nuevo usuario | ✅ |

### Personas

| Método | Endpoint | Descripción | Auth |
|--------|----------|------------|------|
| GET | `/personas/` | Listar todas las personas | ✅ |
| GET | `/personas/{id}` | Obtener persona por ID | ✅ |
| POST | `/personas/` | Crear nueva persona | ✅ |

### Zonas

| Método | Endpoint | Descripción | Auth |
|--------|----------|------------|------|
| GET | `/zonas/` | Listar todas las zonas | ✅ |
| GET | `/zonas/{id}` | Obtener zona por ID | ✅ |
| POST | `/zonas/` | Crear nueva zona | ✅ |

## Uso de la API

### 1. Obtener token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "Admin Principal", "password": "password"}'
```

### 2. Usar token

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl http://localhost:8000/zonas/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Documentación interactiva

Swagger UI disponible en: `http://localhost:8000/docs`

## Base de Datos

### ⚠️ Fuente de verdad: `scripts/init.sql`

> **`scripts/init.sql` es la fuente de verdad del esquema de base de datos.**
> Este script ya fue ejecutado en la base de datos compartida que usamos para desarrollo.
> **Si la tabla o columna que necesitas ya existe en `init.sql`, NO crees una migración.**
> Solo debes crear una migración cuando `init.sql` no tenga las capacidades que necesitas
> (ej: agregar una columna que no existe, crear una tabla nueva que no está contemplada).

### Esquema actual

El esquema se encuentra en `scripts/init.sql` e incluye las siguientes tablas **ya existentes en la base de datos compartida**:

- **persona**: Beneficiarios individuales
- **familia**: Grupos familiares
- **zona**: Zonas geográficas
- **ubicacion**: Direcciones
- **albergue**: Centros de alojamiento
- **familia_albergue**: Asignación familia-albergue
- **origen_recurso**: Fuentes de ayudas
- **recurso**: Tipos de ayudas
- **bodega**: Centros de almacenamiento
- **movimiento_inventario**: Entradas/salidas
- **entrega**: Entregas realizadas
- **detalle_entrega**: Detalle de entregas
- **usuario**: Usuarios del sistema

> 💡 **Antes de crear cualquier migración, revisa `scripts/init.sql` para confirmar que la tabla o columna no exista ya.**

### Datos de prueba

El script `init.sql` incluye datos de ejemplo para pruebas.

## Desarrollo

### Comandos útiles (Makefile)

El proyecto incluye un `Makefile` con los comandos más comunes:

```bash
make install       # Instala dependencias (prod + dev)
make format        # Formatea código automáticamente
make lint          # Verifica estilo y calidad
make test          # Ejecuta tests
make test-cov      # Ejecuta tests con cobertura
make run           # Ejecuta API localmente (uvicorn reload)
make docker-up     # Levanta servicios con Docker
make docker-down   # Detiene servicios
make docker-logs   # Muestra logs de Docker
make migration name="descripción"  # Crea nueva migración SQL
make migrate       # Aplica migraciones pendientes
make db-shell      # Abre consola PostgreSQL
make clean         # Limpia archivos temporales
```

### Estructura de archivos

Cada nueva entidad sigue el patrón:

```
app/
├── api/
│   └── nueva_entidad.py    # Router
├── domain/models/
│   └── nueva_entidad.py   # Modelo SQLAlchemy
└── schema/
    └── nueva_entidad_schema.py  # Schema Pydantic
```

### Agregar un nuevo endpoint

1. Crear migración en `migrations/`: `make migration name="Crear tabla x"`
2. Crear modelo en `app/domain/models/`
3. Crear schema en `app/schema/`
4. Crear router en `app/api/`
5. Registrar en `app/main.py`
6. Aplicar migración: `make migrate`

Ver ejemplos existentes en `app/api/users.py`, `app/domain/models/user.py`, `app/schema/user_schema.py`.

### Linter y Formatter

Usamos **Ruff** para mantener un estilo consistente:

```bash
# Verificar estilo
make lint

# Corregir automáticamente
make format
```

Para integrarlo en el editor, instalar la extensión [Ruff para VSCode](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

### Pre-commit hooks

```bash
# Una sola vez al clonar el repo
pip install pre-commit
pre-commit install
```

A partir de ese momento, antes de cada `git commit` se ejecutará Ruff automáticamente.

## Migraciones de Base de Datos

Toda modificación a la base de datos **debe** registrarse como migración.

### Crear una migración

```bash
make migration name="Agregar campo telefono a persona"
```

Esto genera: `migrations/1744567890_agregar_campo_telefono_a_persona.sql`

### Formato

```
migrations/{EPOCH}_{nombre_snake_case}.sql
```

### Aplicar migraciones

```bash
make migrate
```

### Buenas prácticas

- Una migración = un cambio atómico
- Nunca modificar una migración ya aplicada (crear una nueva)
- Incluir el `ROLLBACK` como comentario al final del archivo
- Usar `IF NOT EXISTS` / `IF EXISTS` cuando sea posible

## Tests

Los tests se encuentran en `tests/` y usan **pytest** + **httpx** (cliente async).

```bash
# Ejecutar todos los tests
make test

# Con cobertura
make test-cov
```

Estructura esperada:
```
tests/
├── __init__.py
├── conftest.py       # Fixtures compartidos (client, auth_headers, etc.)
└── test_api.py       # Tests de integración
```

### Fixtures disponibles

- `client` — Cliente HTTP async (httpx.AsyncClient) sin auth
- `auth_headers` — Headers con token JWT válido
- `client_auth` — Cliente HTTP con auth pre-configurada
- `sample_persona_data`, `sample_user_data`, `sample_zona_data` — Datos de ejemplo

## CI/CD

Cada Pull Request ejecuta automáticamente en GitHub Actions:
1. **Lint** — Ruff linter + format check
2. **Test** — pytest contra PostgreSQL 16 (servicio temporal)

Ver `.github/workflows/ci.yml`.

## Pull Requests

### Template

Todos los PRs deben usar el template en `.github/PULL_REQUEST_TEMPLATE.md`.

### Con GitHub CLI

```bash
gh pr create \
  --title "[HU-XXX] Descripción" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md \
  --base main
```

### Checklist antes del PR

- [ ] `make lint` pasa
- [ ] `make test` pasa (o tests existentes siguen pasando)
- [ ] Migraciones con formato correcto
- [ ] Archivos nuevos siguen el patrón del proyecto

## Guía de Contribución Completa

Ver [CONTRIBUTING.md](./CONTRIBUTING.md) para guía detallada sobre:
- Flujo de trabajo con Git
- Convenciones de código
- Migraciones de base de datos
- Cómo agregar una nueva entidad (ejemplo completo)
- Pull Requests con GitHub CLI
- Resolución de problemas comunes

## Licencia

AGPL-3.0 - Universidad de Córdoba 2026

<!-- AGENT_INSTRUCTIONS_START --><!--
## ⚠️ Instrucciones para Agentes de IA

**SECCIÓN OBLIGATORIA - LEER SIEMPRE ANTES DE TRABAJAR**

Este documento es la **fuente de verdad** del proyecto. Antes de iniciar cualquier tarea:

1. **LEER ESTE README completo** - Entender arquitectura, patrones y stack
2. **LEER [CONTRIBUTING.md](./CONTRIBUTING.md)** - Flujo de trabajo, convenciones y PRs
3. **Revisar el estado actual** - Ver qué archivos existen y su estructura
4. **Consultar `app/main.py`** - Ver qué routers están registrados
5. **Ver modelos existentes** - Entender el patrón de domain/models
6. **Ver migraciones existentes** en `migrations/` para entender el formato
7. **Ver tests existentes** en `tests/` para entender el patrón de testing

### Reglas estrictas

- **LEER `scripts/init.sql` primero** — ese archivo es la fuente de verdad del schema. Si la tabla/columna ya existe ahí, **NO crees migración**, úsala directamente.
- **TODAS** las modificaciones a la DB que NO estén en `init.sql` deben ser migraciones en `migrations/` con formato `{EPOCH}_{snake_case}.sql`
- **NUNCA** modificar el `scripts/init.sql` — ese archivo es solo para bootstrap inicial y ya fue ejecutado en la DB compartida
- **NUNCA** modificar migraciones ya aplicadas (crear una nueva en su lugar)
- **SIEMPRE** seguir el patrón: `api/<entidad>.py` → `domain/models/<entidad>.py` → `schema/<entidad>_schema.py`
- **SIEMPRE** ejecutar `make lint` y `make test` antes de entregar código
- **NO inventar patrones** — Seguir los existentes en el código base

### Flujo para decidir si crear migración
1. Abrir `scripts/init.sql`
2. Buscar si la tabla o columna necesaria ya existe
3. Si existe y tiene lo que se necesita → usarla directamente (sin migración)
4. Si existe pero le falta algo → migración ALTER TABLE
5. Si no existe → migración CREATE TABLE

### Flujo de trabajo para nuevas features

1. Leer README y CONTRIBUTING.md
2. Explorar código existente (modelos, schemas, routers)
3. Crear migración SQL con `make migration name="descripción"`
4. Implementar modelo SQLAlchemy en `app/domain/models/`
5. Implementar schema Pydantic en `app/schema/`
6. Implementar router en `app/api/`
7. Registrar router en `app/main.py`
8. Agregar tests en `tests/test_api.py`
9. Ejecutar `make format && make lint && make test`
10. Actualizar README si se agregaron endpoints, tablas o variables de entorno
11. Crear PR con `gh pr create`

**Al finalizar una feature SIEMPRE actualizar este README con:**
- Nuevos endpoints agregados (nombre, método, descripción, si requiere auth)
- Nuevas tablas/modelos creados
- Cambios en la base de datos
- Variables de entorno nuevas
