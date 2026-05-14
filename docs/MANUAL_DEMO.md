# 🎬 Manual de Demo — SGAH (Sistema de Gestión de Ayuda Humanitaria)

**Duración estimada:** 20-25 minutos
**Prerrequisitos:** Docker corriendo, API accesible en `http://localhost:8000`
**Herramienta recomendada:** [Insomnia](https://insomnia.rest/) o [Bruno](https://www.usebruno.com/) (o simplemente curl desde terminal)

---

## 📋 Preparación inicial (2 min)

### 1. Verificar que todo está corriendo

```bash
docker compose ps
make migrate --status   # Todas deben aparecer como aplicadas
```

### 2. Obtener token de administrador (se usará en todos los flujos)

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo": "admin@sgah.com", "password": "Admin123"}' | jq .
```

Guardar el `access_token` que retorna. Lo usaremos como variable `$TOKEN` en los ejemplos.

```bash
export TOKEN="eyJhbGciOiJIUzI1NiIs..."  # pegar el token real
```

---

## 🔐 Flujo 1: Autenticación y control de acceso por roles (4 min)

**HU-01/02** — Demuestra seguridad JWT + roles granulares + auditoría.

### Paso 1.1: Acceder a recurso protegido con token válido

```bash
curl -s http://localhost:8000/personas/ \
  -H "Authorization: Bearer $TOKEN" | jq '. | length'
```

✅ Debe retornar la lista de personas (12 registros del seed).

### Paso 1.2: Intentar acceso sin token

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/personas/
```

✅ Debe retornar `401`.

### Paso 1.3: Intentar acción no autorizada según el rol

```bash
# Login como OPERADOR_ENTREGAS (sin permisos para crear personas)
TOKEN_OPERADOR=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo": "operador@sgah.com", "password": "Admin123"}' | jq -r '.access_token')

curl -s -X POST http://localhost:8000/personas/ \
  -H "Authorization: Bearer $TOKEN_OPERADOR" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Test"}' | jq .
```

✅ Debe retornar `403` con mensaje de roles requeridos.

### Paso 1.4: Verificar que quedó registrado en auditoría

```bash
# Login como admin para ver logs
curl -s http://localhost:8000/audit_logs/ \
  -H "Authorization: Bearer $TOKEN" | jq '.[0:3]'
```

✅ Debe mostrar los intentos de acceso con método, endpoint, status_code y payload.

---

## 👨‍👩‍👧‍👦 Flujo 2: Registro de familia censal + cálculo de puntaje (6 min)

**HU-04/05/08** — Corazón del sistema: censar población vulnerable y calcular prioridad.

### Paso 2.1: Crear una nueva familia

```bash
curl -s -X POST http://localhost:8000/familias/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"acepta_privacidad": true}' | jq .
```

✅ Respuesta esperada (similar a):
```json
{
  "id_familia": 7,
  "codigo_familia": "FAM-2026-00007",
  "acepta_privacidad": true,
  "puntaje_prioridad": 0.0
}
```

### Paso 2.2: Agregar miembros vulnerables a la familia

Agregar 2 niños y 1 anciano:

```bash
# Niño 1
curl -s -X POST http://localhost:8000/personas/familias/7/personas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Luisito Pérez", "edad": 6, "es_nino": true}' | jq .

# Niño 2
curl -s -X POST http://localhost:8000/personas/familias/7/personas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Anita Pérez", "edad": 4, "es_nino": true}' | jq .

# Anciano
curl -s -X POST http://localhost:8000/personas/familias/7/personas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Doña María", "edad": 75, "es_anciano": true}' | jq .
```

### Paso 2.3: Verificar el puntaje calculado automáticamente

```bash
curl -s http://localhost:8000/familias/7 \
  -H "Authorization: Bearer $TOKEN" | jq '.puntaje_prioridad'
```

✅ El puntaje debe ser **7.5** (3 miembros × 1.0 + 2 niños × 2.0 + 1 anciano × 2.5).

### Paso 2.4: Modificar la configuración de puntaje en caliente

```bash
# Subir el peso del anciano de 2.5 a 4.0
curl -s -X PUT http://localhost:8000/configuracion-puntaje/peso_anciano \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"valor": 4.0}' | jq .

# Recalcular manualmente
curl -s -X POST http://localhost:8000/configuracion-puntaje/familias/7/calcular-puntaje \
  -H "Authorization: Bearer $TOKEN" | jq .
```

✅ El puntaje ahora debe ser **9.0** (3 × 1.0 + 2 × 2.0 + 1 × 4.0).

### Paso 2.5: Revertir configuración

```bash
curl -s -X PUT http://localhost:8000/configuracion-puntaje/peso_anciano \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"valor": 2.5}' | jq .
```

**💡 Punto para destacar al profesor:** El puntaje es parametrizable sin cambiar código. Un coordinador puede ajustar los pesos según la crisis sin necesidad de desarrollador.

---

## 📊 Flujo 3: Generación de plan de distribución priorizado (4 min)

**HU-08/21** — Muestra cómo los datos censales se convierten en un plan operativo.

### Paso 3.1: Ver familias existentes con sus puntajes

```bash
curl -s http://localhost:8000/familias/ \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {id: .id_familia, codigo: .codigo_familia, puntaje: .puntaje_prioridad}'
```

✅ Debe mostrar varias familias con puntajes distintos (la familia 7 debe tener el más alto).

### Paso 3.2: Generar el plan de distribución

```bash
curl -s -X POST http://localhost:8000/planes-distribucion/generar \
  -H "Authorization: Bearer $TOKEN" | jq .
```

✅ Respuesta esperada:
```json
{
  "mensaje": "Plan generado exitosamente para N familias",
  "total_familias": N
}
```

### Paso 3.3: Listar planes generados (ordenados por prioridad)

```bash
curl -s http://localhost:8000/planes-distribucion/ \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {id: .id_plan, familia: .id_familia, puntaje: .puntaje_al_generar, prioridad: .prioridad_orden}'
```

✅ Deben aparecer ordenados por `prioridad_orden`, con la familia de mayor puntaje primero.

### Paso 3.4: Ver detalle de un plan con recursos asignados

```bash
curl -s http://localhost:8000/planes-distribucion/1 \
  -H "Authorization: Bearer $TOKEN" | jq '.detalles'
```

✅ Cada plan debe tener recursos asignados (Arroz x 5kg, Aceite x 1L, Agua potable x 5L).

**💡 Punto para destacar al profesor:** El sistema excluye automáticamente familias que ya tienen un plan activo (programada o en curso), evitando duplicados.

---

## 📦 Flujo 4: Registro de entrega con regla RN-02 (cobertura 3 días) (6 min)

**HU-12/22/23** — El flujo más complejo. Demuestra transacciones atómicas, reglas de negocio y auditoría.

### Paso 4.1: Consultar inventario disponible en bodegas

```bash
# Ver bodegas
curl -s http://localhost:8000/bodegas/ \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {id: .id_bodega, nombre: .nombre, peso_actual: .peso_actual_kg}'
```

### Paso 4.2: Registrar una entrega a una familia

```bash
curl -s -X POST http://localhost:8000/entregas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_familia": 1,
    "fecha_efectiva": "2026-05-14",
    "detalles": [
      {"id_recurso": 1, "cantidad": 2},
      {"id_recurso": 2, "cantidad": 1}
    ]
  }' | jq .
```

✅ Respuesta esperada (similar a):
```json
{
  "id_entrega": 9,
  "codigo": "ENT-2026-00001",
  "estado": "ENTREGADA",
  "fecha_efectiva": "2026-05-14",
  "id_familia": 1,
  "id_bodega": 1,
  "detalles": [
    {"id_recurso": 1, "nombre_recurso": "Arroz x 5kg", "cantidad": 2},
    {"id_recurso": 2, "nombre_recurso": "Aceite x 1L", "cantidad": 1}
  ]
}
```

**💡 Punto para destacar:** Observe que:
- Se generó un código secuencial `ENT-2026-00001`
- El sistema resolvió automáticamente la bodega (id_bodega: 1)
- Se descontó el stock y el peso de la bodega en una sola transacción

### Paso 4.3: Intentar violar la regla de cobertura de 3 días (RN-02)

```bash
# Misma familia, misma fecha (o dentro de 3 días)
curl -s -X POST http://localhost:8000/entregas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_familia": 1,
    "fecha_efectiva": "2026-05-15",
    "detalles": [
      {"id_recurso": 1, "cantidad": 1}
    ]
  }' | jq .
```

✅ Debe retornar `400 Bad Request` con:
```json
{
  "detail": {
    "code": "COBERTURA_NO_CUMPLIDA",
    "message": "La familia 1 ya recibió ayuda en los últimos 3 días...",
    "ultima_fecha": "2026-05-14",
    "dias_transcurridos": 1
  }
}
```

### Paso 4.4: Verificar que el intento bloqueado quedó auditado

```bash
curl -s http://localhost:8000/audit_logs/ \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | select(.action == "ENTREGA_BLOQUEADA_COBERTURA_3_DIAS") | {accion: .action, payload: .payload}'
```

✅ Debe mostrar el intento bloqueado con el detalle de la familia y fechas.

**💡 Punto clave para destacar al profesor:** La auditoría del bloqueo se persiste en una sesión independiente de BD, por lo que sobrevive aunque la transacción principal haga rollback. Esto es trazabilidad real.

---

## 🏁 Resumen para la presentación

| Flujo | Lo que demuestra | Peso en nota |
|-------|-----------------|-------------|
| 1. Autenticación | JWT, bcrypt, roles, auditoría | 20% |
| 2. Familia + puntaje | Lógica de negocio, reglas parametrizables, recálculo automático | 30% |
| 3. Plan distribución | Priorización algorítmica, exclusión de duplicados | 20% |
| 4. Entrega + RN-02 | Transacciones atómicas, regla de dominio, trazabilidad | 30% |

### 📌 Frase final sugerida:

> *"SGAH es un sistema con arquitectura en capas, seguridad JWT, reglas de negocio como la priorización por vulnerabilidad y la cobertura de 3 días, todo sobre PostgreSQL con 17 migraciones progresivas. Próximos pasos: frontend web y mayor cobertura de tests automatizados."*

---
*Documento generado el 14 de mayo de 2026 — Revisar credenciales y endpoints antes de la demo.*
