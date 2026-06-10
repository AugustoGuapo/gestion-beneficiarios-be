---
name: Pull Request
about: Crear un PR para revisión
title: "[HU-XXX] Breve descripción del cambio"
labels: ""
assignees: ""
---

## 📋 Descripción
<!-- Explica brevemente qué hace este PR y por qué es necesario -->

## 🔗 Issue relacionado
<!-- Si resuelve una Historia de Usuario o Issue, enlázalo aquí -->
Closes #[HU-XXX]

## 🧪 Cómo probar este PR

### Requisitos previos
- Docker Desktop instalado
- Puerto 5432 libre

### Pasos para probar

```bash
# 1. Clonar y checkout
git checkout feature/HU-XXX
cp .env.example .env

# 2. Limpiar cualquier estado anterior e iniciar servicios
docker compose down
docker compose up --build -d

# 3. Aplicar migraciones
make migrate

# 4. Probar endpoints
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "Admin Principal", "password": "password"}'
```

### Pruebas automatizadas
```bash
# Ejecutar linter
make lint

# Ejecutar tests
make test
```

## 📸 Capturas de pantalla / Evidencias
<!-- Opcional pero recomendado. Pueden ser logs, respuestas de API, etc. -->

## ✅ Checklist antes de solicitar revisión

- [ ] El código sigue el estilo del proyecto (corre `make lint`)
- [ ] Las migraciones tienen el formato `{EPOCH}_{nombre}.sql`
- [ ] Agregué/actualicé tests para los cambios realizados
- [ ] Todos los tests pasan localmente (`make test`)
- [ ] Actualicé la documentación en `README.md` si es necesario
- [ ] Probé manualmente los endpoints con Docker
- [ ] No hay modelos o schemas sin usar (cada archivo nuevo es necesario)
- [ ] Los archivos nuevos siguen el patrón del proyecto:
  - `app/api/<entidad>.py` — Router
  - `app/domain/models/<entidad>.py` — Modelo SQLAlchemy
  - `app/schema/<entidad>_schema.py` — Schema Pydantic

## 📝 Notas adicionales
<!-- Cualquier información extra que el reviewer deba conocer -->