## 📘 DOCUMENTACIÓN DE ENDPOINTS - SGAH

### 🔐 BASE DE DATOS DE PRUEBA
Usuarios predefinidos (contraseña: **Admin123**):
```
Email: admin@sgah.com           | Rol: ADMIN
Email: coordinador@sgah.com     | Rol: COORDINADOR_LOGISTICA
Email: operador@sgah.com        | Rol: OPERADOR_ENTREGAS
Email: registrador@sgah.com     | Rol: REGISTRADOR_DONACIONES
```

---

## 1️⃣ AUTENTICACIÓN (HU-02)

### 🔑 POST /auth/login
**Descripción:** Obtener token JWT

**Request:**
```json
{
  "correo": "admin@sgah.com",
  "password": "Admin123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id_usuario": 1,
    "nombre_completo": "Administrador Sistema",
    "correo": "admin@sgah.com",
    "rol": "ADMIN",
    "activo": true
  }
}
```

**Headers para Postman:**
```
Authorization: Bearer <token_aqui>
Content-Type: application/json
```

**Errores comunes:**
```json
// Credenciales inválidas (401)
{
  "detail": "Credenciales inválidas"
}

// Usuario inactivo (403)
{
  "detail": "Usuario inactivo. Contacte al administrador"
}
```

---

## 2️⃣ GESTIÓN DE USUARIOS (HU-01)

### ✅ POST /users/
**Descripción:** Crear nuevo usuario
**Permisos:** ADMIN, COORDINADOR_LOGISTICA
**Headers:** Authorization: Bearer {token}

**Request:**
```json
{
  "nombre_completo": "Juan Pérez López",
  "correo": "juan.perez@sgah.com",
  "rol": "CENSADOR",
  "password": "SecurePass123"
}
```

**Validaciones de password:**
- Mínimo 8 caracteres
- Mínimo 1 mayúscula
- Mínimo 1 número

**Response (201 Created):**
```json
{
  "id_usuario": 5,
  "nombre_completo": "Juan Pérez López",
  "correo": "juan.perez@sgah.com",
  "rol": "CENSADOR",
  "activo": true,
  "fecha_creacion": "2026-05-11T15:30:00",
  "fecha_actualizacion": "2026-05-11T15:30:00"
}
```

**Errores:**
```json
// Email duplicado (400)
{
  "detail": "El correo ya está registrado"
}

// Sin permisos (403)
{
  "detail": "No tienes permisos para crear usuarios"
}

// Password inválido (422)
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "La contraseña debe contener al menos una mayúscula",
      "type": "value_error"
    }
  ]
}
```

---

### 📋 GET /users/
**Descripción:** Listar todos los usuarios
**Permisos:** Autenticado
**Headers:** Authorization: Bearer {token}
**Query params:** 
- `skip`: número de registros a saltar (default: 0)
- `limit`: máximo de registros (default: 100, máximo: 1000)

**Request URL:**
```
GET /users/?skip=0&limit=50
```

**Response (200 OK):**
```json
[
  {
    "id_usuario": 1,
    "nombre_completo": "Administrador Sistema",
    "correo": "admin@sgah.com",
    "rol": "ADMIN",
    "activo": true
  },
  {
    "id_usuario": 2,
    "nombre_completo": "Coordinador Logística",
    "correo": "coordinador@sgah.com",
    "rol": "COORDINADOR_LOGISTICA",
    "activo": true
  }
]
```

---

### 🔍 GET /users/{user_id}
**Descripción:** Obtener detalles de un usuario
**Permisos:** Autenticado
**Headers:** Authorization: Bearer {token}

**Request:**
```
GET /users/1
```

**Response (200 OK):**
```json
{
  "id_usuario": 1,
  "nombre_completo": "Administrador Sistema",
  "correo": "admin@sgah.com",
  "rol": "ADMIN",
  "activo": true,
  "fecha_creacion": "2026-05-11T12:00:00",
  "fecha_actualizacion": "2026-05-11T12:00:00"
}
```

**Errores:**
```json
// Usuario no existe (404)
{
  "detail": "Usuario no encontrado"
}
```

---

### ✏️ PUT /users/{user_id}
**Descripción:** Actualizar usuario
**Permisos:** ADMIN (cualquiera) o el usuario de sí mismo
**Headers:** Authorization: Bearer {token}

**Request:**
```json
{
  "nombre_completo": "Juan Carlos Pérez López",
  "rol": "OPERADOR_ENTREGAS",
  "activo": true
}
```

**Campos actualizables:**
- `nombre_completo` (opcional)
- `rol` (opcional): ADMIN, CENSADOR, OPERADOR_ENTREGAS, COORDINADOR_LOGISTICA, FUNCIONARIO_CONTROL, REGISTRADOR_DONACIONES
- `activo` (opcional): true (activo) o false (inactivo)

**Response (200 OK):**
```json
{
  "id_usuario": 5,
  "nombre_completo": "Juan Carlos Pérez López",
  "correo": "juan.perez@sgah.com",
  "rol": "OPERADOR_ENTREGAS",
  "activo": true,
  "fecha_creacion": "2026-05-11T15:30:00",
  "fecha_actualizacion": "2026-05-11T16:45:00"
}
```

**Errores:**
```json
// Sin permisos para actualizar otro usuario (403)
{
  "detail": "Solo puedes actualizar tu propio perfil"
}
```

---

### 🚫 DELETE /users/{user_id}
**Descripción:** Desactivar usuario (activo=false)
**Permisos:** ADMIN
**Headers:** Authorization: Bearer {token}

**Request:**
```
DELETE /users/5
```

**Response (204 No Content)**
Sin contenido en la respuesta

**Verificar desactivación:**
```
GET /users/5
```
Verás que `activo: false`

---

### ✅ POST /users/{user_id}/activate
**Descripción:** Activar un usuario (activo=true)
**Permisos:** ADMIN
**Headers:** Authorization: Bearer {token}

**Request:**
```
POST /users/5/activate
```

**Response (200 OK):**
```json
{
  "id_usuario": 5,
  "nombre_completo": "Juan Pérez López",
  "correo": "juan.perez@sgah.com",
  "rol": "CENSADOR",
  "activo": true,
  "fecha_creacion": "2026-05-11T15:30:00",
  "fecha_actualizacion": "2026-05-11T16:50:00"
}
```

---

## 🎯 FLUJOS DE PRUEBA RECOMENDADOS

### Flujo 1: Login y crear usuario
```bash
# 1. Login como admin
POST /auth/login
{
  "correo": "admin@sgah.com",
  "password": "Admin123"
}
# Copiar token del response

# 2. Crear nuevo usuario (incluir token en Authorization header)
POST /users/
Headers: Authorization: Bearer {token}
{
  "nombre_completo": "Ana García Martínez",
  "correo": "ana.garcia@sgah.com",
  "rol": "FUNCIONARIO_CONTROL",
  "password": "Control123"
}

# 3. Listar usuarios
GET /users/
Headers: Authorization: Bearer {token}
```

### Flujo 2: Actualizar perfil propio
```bash
# 1. Login con usuario no-admin
POST /auth/login
{
  "correo": "operador@sgah.com",
  "password": "Admin123"
}

# 2. Actualizar nombre (token en header)
PUT /users/3
Headers: Authorization: Bearer {token}
{
  "nombre_completo": "Operador de Entregas Actualizado"
}
```

### Flujo 3: Desactivar y activar usuario
```bash
# 1. Login como admin
POST /auth/login
{
  "correo": "admin@sgah.com",
  "password": "Admin123"
}

# 2. Desactivar usuario (activo = false)
DELETE /users/5
Headers: Authorization: Bearer {token}

# 3. Verificar desactivación
GET /users/5
Headers: Authorization: Bearer {token}
# Verá: "activo": false

# 4. Intentar login con usuario inactivo (fallará)
POST /auth/login
{
  "correo": "usuario@sgah.com",
  "password": "SuPassword"
}
# Response: 403 "Usuario inactivo. Contacte al administrador"

# 5. Activar usuario (activo = true)
POST /users/5/activate
Headers: Authorization: Bearer {token}

# 6. Intentar login de nuevo (funcionará)
POST /auth/login
{
  "correo": "usuario@sgah.com",
  "password": "SuPassword"
}
```

---

## 🔐 ROLES Y PERMISOS

| Rol | Crear Usuarios | Actualizar Otros | Desactivar |
|-----|---|---|---|
| ADMIN | ✅ | ✅ | ✅ |
| COORDINADOR_LOGISTICA | ✅ | ❌ | ❌ |
| OPERADOR_ENTREGAS | ❌ | ❌ | ❌ |
| CENSADOR | ❌ | ❌ | ❌ |
| FUNCIONARIO_CONTROL | ❌ | ❌ | ❌ |
| REGISTRADOR_DONACIONES | ❌ | ❌ | ❌ |

Todos pueden:
- Actualizar su propio perfil
- Ver usuarios (listar y obtener detalles)

---

## 📝 CONFIGURACIÓN DE POSTMAN

### 1. Crear variable de entorno
En Postman:
1. Click en "Environment" (arriba a la derecha)
2. Click en "+"
3. Nombre: `sgah`
4. Variables:
   - Nombre: `base_url` | Valor: `http://localhost:8000`
   - Nombre: `token` | Valor: `(dejar vacío)`

### 2. Usar variables en requests
```
POST {{base_url}}/auth/login
Headers: 
  Authorization: Bearer {{token}}
```

### 3. Script para guardar token automáticamente
En la sección "Tests" del endpoint login:
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("token", jsonData.access_token);
}
```

---

## 🚀 PRÓXIMOS PASOS (Futuros módulos)

El sistema está preparado para:
- Usar JWT con roles en nuevos módulos
- Extender UserService para nuevas funcionalidades
- Agregar nuevos roles sin cambiar código
- Implementar auditoría de cambios (fecha_actualizacion ya está lista)

---

## ⚠️ NOTAS IMPORTANTES

1. **Contraseñas**: Las contraseñas se hashean con bcrypt. Nunca guardes contraseñas en texto plano.
2. **Token JWT**: Expira después de 480 minutos (configurable en .env). Usa refresh-token para extender.
3. **Email único**: El correo es único a nivel de base de datos. Validación en API.
4. **Desactivación lógica**: No hay DELETE físico. Los datos se preservan.
5. **Fecha de actualización**: Se actualiza automáticamente en cada cambio.
6. **Campo único de estado**: Solo `activo` (booleano). Sin redundancia.
