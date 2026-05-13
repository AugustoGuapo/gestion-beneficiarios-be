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

### Zonas

| Método | Endpoint | Descripción | Auth |
|--------|----------|------------|------|
| GET | `/zonas/` | Listar todas las zonas | ✅ |
| GET | `/zonas/{id}` | Obtener zona por ID | ✅ |

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

### Esquema

El esquema se encuentra en `scripts/init.sql` e incluye:

- **persona**: Beneficiarios individuales
- **familia**: Grupos familiares
- **zona**: Zonas geográficas
- **ubicacion**: Direcciones
- **albergue**: Centros de alojamiento
- **familia_albergue**: Asignación famila-albergue
- **origen_recurso**: Fuentes de ayudas
- **recurso**: Tipos de ayudas
- **bodega**: Centros de almacenamiento
- **movimiento_inventario**: Entradas/salidas
- **entrega**: Entregas realizadas
- **detalle_entrega**: Detalle de entregas
- **usuario**: Usuarios del sistema

### Datos de prueba

El script `init.sql` incluye datos de ejemplo para pruebas.

## Desarrollo

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

1. Crear modelo en `app/domain/models/`
2. Crear schema en `app/schema/`
3. Crear router en `app/api/`
4. Registrar en `app/main.py`

Ver ejemplos existentes en `app/api/users.py`, `app/domain/models/user.py`, `app/schema/user_schema.py`.

## Contributing

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-caracteristica`
3. Commit cambios: `git commit -m 'Agrega nueva característica'`
4. Push a GitHub: `git push origin feature/nueva-caracteristica`
5. Crear Pull Request

## Licencia

AGPL-3.0 - Universidad de Córdoba 2026

<!-- AGENT_INSTRUCTIONS_START --><!--
## ⚠️ Instrucciones para Agentes de IA

**SECCIÓN OBLIGATORIA - LEER SIEMPRE ANTES DE TRABAJAR**

Este documento es la **fuente de verdad** del proyecto. Antes de iniciar cualquier tarea:

1. **LEER ESTE README completo** - Entender arquitectura, patrones y stack
2. **Revisar el estado actual** - Ver qué archivos existen y su estructura
3. **Consultar `app/main.py`** - Ver qué routers están registrados
4. **Ver modelos existentes** - Entender el patrón de domain/models

**Al finalizar una feature SIEMPRE actualizar este README con:**
- Nuevos endpoints agregados
- Nuevas tablas/modelos creados
- Cambios en la base de datos
- Variables de entorno nuevas

**Pattern obligatorio para nuevos endpoints:**
```
app/api/<entidad>.py          # Router con auth
app/domain/models/<entidad>.py  # Modelo SQLAlchemy
app/schema/<entidad>_schema.py # Schema Pydantic
```

**No inventar patrones** - Seguir los existentes en el código base.
--><!-- AGENT_INSTRUCTIONS_END -->
