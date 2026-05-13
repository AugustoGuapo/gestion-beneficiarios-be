# Guía de Contribución

Este documento establece los lineamientos para contribuir al proyecto **Gestión de Beneficiarios - Backend**. Léelo **completamente** antes de empezar a trabajar.

---

## 📋 Tabla de Contenido

1. [Flujo de Trabajo (Git)](#1-flujo-de-trabajo-git)
2. [Convenciones de Código](#2-convenciones-de-código)
3. [Migraciones de Base de Datos](#3-migraciones-de-base-de-datos)
4. [Estructura de Archivos](#4-estructura-de-archivos)
5. [Cómo Agregar una Nueva Entidad](#5-cómo-agregar-una-nueva-entidad)
6. [Antes de Crear un Pull Request](#6-antes-de-crear-un-pull-request)
7. [Pull Request con GitHub CLI](#7-pull-request-con-github-cli)
8. [Resolución de Problemas Comunes](#8-resolución-de-problemas-comunes)

---

## 1. Flujo de Trabajo (Git)

### Rama principal

- `main` — Rama de producción. Solo se hace merge desde PRs revisados.
- No existe rama `develop` permanente. Cada feature tiene su propia rama.

### Crear una rama de feature

```bash
# Partir siempre de main actualizado
git checkout main
git pull origin main

# Crear rama de feature con el número de HU
git checkout -b feature/HU-XXX
```

### Commits

Los commits deben ser atómicos y descriptivos. Preferir mensajes en español:

```bash
git commit -m "Agrega CRUD de familias con endpoints GET y POST"
```

Evitar commits como `"fix"`, `"cambios"`, `"avance"`.

### Mantener la rama actualizada

```bash
# Mientras trabajas en feature/HU-XXX
git fetch origin
git rebase origin/main   # NO usar merge
```

---

## 2. Convenciones de Código

### Estilo

- Usamos **Ruff** como linter y formatter (configurado en `pyproject.toml`)
- Límite de línea: **100 caracteres**
- Quotes dobles para strings (`"ejemplo"`)
- Nombres de variables/funciones en **snake_case**
- Nombres de clases en **PascalCase**
- Archivos en **snake_case**

### Antes de hacer commit

```bash
# Formatear y lintar
make format
make lint

# Ejecutar tests
make test
```

O configurar **pre-commit** (recomendado):

```bash
pip install pre-commit
pre-commit install
```

Esto ejecutará Ruff automáticamente antes de cada commit.

### Estructura de imports

1. Standard library
2. Terceros (FastAPI, SQLAlchemy, etc.)
3. Locales (`app.xxx`)

```python
import os
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import Column, Integer, String

from app.infrastructure.db.base import Base
from app.schema.user_schema import UserCreate, UserResponse
```

---

## 3. Migraciones de Base de Datos

### ⚠️ Regla #1: `scripts/init.sql` es la fuente de verdad

> **`scripts/init.sql` es el schema oficial de la base de datos.**
> Se ejecuta una sola vez al iniciar los contenedores Docker (`docker compose up`).
> **Si la tabla o columna que necesitas YA EXISTE en `init.sql`, NO crees una migración.**

**Flujo para decidir si necesitas una migración:**

```
1. ¿La tabla que necesito existe en scripts/init.sql?
   │
   ├── SÍ → ¿Tiene las columnas que necesito?
   │        ├── SÍ → ✅ Usa la tabla tal cual. NO crees migración.
   │        └── NO → 🆕 Crea migración ALTER TABLE para agregar columna
   │
   └── NO → ¿Es una tabla nueva que NO está en init.sql?
            └── SÍ → 🆕 Crea migración CREATE TABLE
```

> 💡 **Siempre revisa `scripts/init.sql` antes de crear una migración.** Si ya existe lo que buscas, no dupliques.

### Regla de oro

> **Todo cambio en la base de datos que no esté cubierto por `init.sql` debe registrarse como migración.**

Esto incluye: creación de tablas nuevas (no contempladas en init.sql), alteración de columnas, nuevos índices, seed data adicional, etc.

### Formato

```
migrations/{EPOCH}_{nombre_snake_case}.sql
```

Ejemplo:
```
migrations/1744567890_agregar_campo_telefono_a_persona.sql
```

### Crear una migración

```bash
make migration name="Descripción del cambio"
```

Esto crea un archivo con template. Completar el SQL:

```sql
-- =============================================
-- Migración: 1744567890_agregar_campo_telefono_a_persona.sql
-- Creada: 2026-11-05 21:30:00
-- Descripción: Agregar campo teléfono a persona
-- =============================================

ALTER TABLE persona ADD COLUMN telefono VARCHAR(20);

-- =============================================
-- ROLLBACK
-- =============================================
-- ALTER TABLE persona DROP COLUMN telefono;
```

### Aplicar migraciones

```bash
make migrate
```

O si no estás usando Docker para la DB:
```bash
DB_HOST=localhost bash scripts/apply_migrations.sh
```

### Buenas prácticas

1. **Una migración = un cambio atómico** — no mezcles cosas no relacionadas
2. **Sé descriptivo** en el nombre: `agregar_campo_telefono_a_persona` no `cambios_varios`
3. **Incluye el ROLLBACK** como comentario al final
4. **No modifiques migraciones ya aplicadas** — crea una nueva
5. Usa `IF NOT EXISTS` / `IF EXISTS` cuando sea posible

---

## 4. Estructura de Archivos

Cada nueva entidad sigue este patrón obligatorio:

```
app/
├── api/<entidad>.py              # Router con endpoints
├── application/services/         # Lógica de negocio (opcional)
│   └── <entidad>_service.py
├── domain/models/<entidad>.py    # Modelo SQLAlchemy
└── schema/<entidad>_schema.py    # Schema Pydantic (request/response)
```

NO inventar patrones nuevos. Seguir los existentes.

---

## 5. Cómo Agregar una Nueva Entidad

Ejemplo: agregar entidad `Categoria`:

### 5.1 Migración SQL

```bash
make migration name="Crear tabla categoria"
```

Completar `migrations/{EPOCH}_crear_tabla_categoria.sql`:

```sql
CREATE TABLE IF NOT EXISTS categoria (
    id_categoria INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);
```

### 5.2 Modelo SQLAlchemy

`app/domain/models/categoria.py`:

```python
from sqlalchemy import Column, Integer, String, Text
from app.infrastructure.db.base import Base


class Categoria(Base):
    __tablename__ = "categoria"
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
```

### 5.3 Schema Pydantic

`app/schema/categoria_schema.py`:

```python
from pydantic import BaseModel


class CategoriaResponse(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: str | None = None

    model_config = {"from_attributes": True}


class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: str | None = None
```

### 5.4 Router

`app/api/categorias.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("/")
async def list_categorias(db: AsyncSession = Depends(get_db)):
    # ... implementación
    pass
```

### 5.5 Registrar en main.py

```python
from app.api import categorias

app.include_router(categorias.router)
```

---

## 6. Antes de Crear un Pull Request

### Checklist

- [ ] `make lint` pasa sin errores
- [ ] `make test` pasa (o los tests existentes siguen pasando)
- [ ] Migraciones con formato `{EPOCH}_{nombre}.sql`
- [ ] Los archivos nuevos siguen el patrón del proyecto
- [ ] Probaste los endpoints manualmente con Docker
- [ ] Si hay endpoints nuevos, están documentados en Swagger `/docs`
- [ ] Actualizaste `README.md` si agregaste endpoints o variables de entorno

---

## 7. Pull Request con GitHub CLI

### Abrir PR desde la terminal

```bash
# Asegúrate de estar en tu rama de feature
git checkout feature/HU-XXX

# Asegúrate de tener los cambios commiteados
git add .
git commit -m "feat: descripción de lo que implementa HU-XXX"

# Push a GitHub
git push origin feature/HU-XXX

# Crear PR usando gh CLI con template
gh pr create \
  --title "[HU-XXX] Título descriptivo" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md \
  --base main \
  --label "needs-review"
```

### Verificar PR antes de crearlo

```bash
# Ver qué cambios incluye el PR
gh pr diff

# Ver el estado de los checks
gh pr checks
```

### Si necesitas hacer cambios después de abrir el PR

```bash
# Hacer cambios, commit y push
git add .
git commit -m "fix: corrige validación de edad"
git push origin feature/HU-XXX
# El PR se actualiza automáticamente
```

### Instrucciones de revisión en el PR

En el cuerpo del PR, incluye **instrucciones claras para que el reviewer pueda probar**:

```markdown
## 🧪 Cómo probar

1. `docker compose down && docker compose up --build -d`
2. Aplicar migraciones: `bash scripts/apply_migrations.sh`
3. Probar endpoint: `curl -X POST http://localhost:8000/categorias/ ...`
4. Tests: `make test`
```

---

## 8. Resolución de Problemas Comunes

### "El puerto 5432 ya está en uso"

```bash
# Detener cualquier Postgres local
sudo lsof -i :5432
sudo kill -9 <PID>

# O cambiar el puerto en docker-compose.yml
```

### "Error de migración - tabla ya existe"

Usar `IF NOT EXISTS` en las migraciones para hacerlas idempotentes.

### "El linter está fallando"

```bash
make format   # corrige automáticamente lo que pueda
make lint     # verifica qué queda por corregir
```

### "No puedo importar mi módulo"

Verifica que:
1. Existe el archivo `__init__.py` en el directorio
2. El nombre del archivo está en **snake_case**
3. La ruta del import es desde la raíz del proyecto (`app.domain.models...`)

---

## Recursos

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
