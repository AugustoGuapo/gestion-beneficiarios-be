# 🚀 GUÍA DE INICIO - HU-01 y HU-02

## Requisitos Previos

- Python 3.10+
- PostgreSQL 16+
- pip o pip3
- Postman (opcional, para pruebas)

---

## ⚙️ INSTALACIÓN

### 1. Clonar el repositorio y navegar al proyecto

```bash
cd "c:\Users\Guillermo Castano\Desktop\back-end beneficiario\gestion-beneficiarios-be"
```

### 2. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Dependencias nuevas (ya incluidas en requirements.txt):**
- bcrypt==4.1.2
- passlib==1.7.4

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores
```

**Contenido mínimo de .env:**
```env
DB_USER=ejemplo
DB_PASSWORD=ejemplo
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gestion_beneficiarios
JWT_SECRET_KEY=mi-clave-super-secreta-minimo-32-caracteres-para-produccion
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=480
```

### 5. Inicializar la base de datos

#### Opción A: Con Docker Compose (Recomendado)

```bash
docker-compose up -d
```

Esto inicia PostgreSQL y ejecuta automáticamente el script `scripts/init.sql`

#### Opción B: Sin Docker

1. Crear base de datos PostgreSQL:
```sql
CREATE DATABASE gestion_beneficiarios;
```

2. Ejecutar script de inicialización:
```bash
psql -U postgres -d gestion_beneficiarios -f scripts/init.sql
```

### 6. Verificar conexión a BD

```bash
# Desde Python
python -c "from app.core.config import settings; print(settings.database_url)"
```

---

## 🏃 EJECUCIÓN

### Iniciar el servidor

```bash
uvicorn app.main:app --reload
```

O con FastAPI CLI:
```bash
fastapi run app/main.py
```

**Output esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Acceder a la documentación interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🧪 PRUEBAS INICIALES

### 1. Login (obtener token)

**Curl:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "correo": "admin@sgah.com",
    "password": "Admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id_usuario": 1,
    "nombre_completo": "Administrador Sistema",
    "correo": "admin@sgah.com",
    "rol": "ADMIN",
    "estado": "ACTIVO"
  }
}
```

### 2. Listar usuarios

```bash
curl -X GET "http://localhost:8000/users/" \
  -H "Authorization: Bearer {TOKEN_AQUI}"
```

### 3. Crear usuario

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN_AQUI}" \
  -d '{
    "nombre_completo": "Pedro García",
    "correo": "pedro@sgah.com",
    "rol": "CENSADOR",
    "password": "Secure123"
  }'
```

---

## 📮 IMPORTAR EN POSTMAN

### 1. Descargar colección

Archivo: `SGAH_Collection.postman_collection.json`

### 2. Importar en Postman

1. Abre Postman
2. Click en "Import" (arriba a la izquierda)
3. Selecciona el archivo `SGAH_Collection.postman_collection.json`
4. Click en "Import"

### 3. Configurar variables de entorno

1. Click en "Environments" (arriba a la derecha)
2. Click en "+"
3. Nombre: `sgah`
4. Variables:
   - Key: `base_url` | Value: `http://localhost:8000`
   - Key: `token` | Value: `` (dejar vacío)

### 4. Usar la colección

- Selecciona el environment `sgah`
- Prueba cualquier endpoint
- El token se guardará automáticamente después del login

---

## 🗄️ MIGRACIONES (Si hay usuarios existentes)

Si ya tenías datos en la tabla `usuario` antigua:

```bash
psql -U postgres -d gestion_beneficiarios -f scripts/migrate_usuario_hu01_hu02.sql
```

Este script:
1. Preserva datos existentes
2. Los migra a la nueva estructura
3. Genera emails automáticamente si no existen
4. Asigna contraseña por defecto hasheada

---

## 📋 VERIFICACIÓN POST-INSTALACIÓN

### Checklist

- [ ] Docker/PostgreSQL corriendo
- [ ] Archivo .env configurado
- [ ] `pip install -r requirements.txt` completado
- [ ] Servidor iniciado sin errores
- [ ] Swagger UI accesible en /docs
- [ ] Login exitoso con admin@sgah.com
- [ ] Puedo listar usuarios
- [ ] Puedo crear usuario nuevo
- [ ] Email único se valida (intenta crear con email duplicado)

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "No module named 'bcrypt'"

```bash
pip install bcrypt==4.1.2 passlib==1.7.4
```

### Error: "Connection refused" (BD)

1. Verifica que PostgreSQL está corriendo
2. Verifica credenciales en .env
3. Con Docker: `docker-compose ps`

### Error: "relation usuario does not exist"

1. Ejecuta el script de inicialización:
   ```bash
   psql -U postgres -d gestion_beneficiarios -f scripts/init.sql
   ```

### Error: "JWT_SECRET_KEY not found"

1. Verifica que .env existe
2. Verifica que tiene JWT_SECRET_KEY configurado
3. Reinicia el servidor

### Token inválido en Postman

1. Ejecuta el endpoint Login primero
2. Copia el `access_token` completo
3. Pégalo en la variable `{{token}}` del environment

---

## 📚 DOCUMENTACIÓN COMPLETA

- **POSTMAN_EXAMPLES.md** - Documentación detallada de todos los endpoints
- **IMPLEMENTATION_SUMMARY.md** - Resumen técnico de cambios
- **app/core/constants.py** - Enums de roles y estados
- **app/application/services/user_service.py** - Lógica de negocio

---

## 🔄 ESTRUCTURA MODULAR

El código está diseñado para ser escalable:

```
app/
├── core/
│   ├── config.py         # Configuración
│   ├── security.py       # Autenticación y permisos
│   └── constants.py      # Enums (roles, estados)
│
├── domain/
│   └── models/
│       └── user.py       # Modelo User
│
├── application/
│   └── services/
│       └── user_service.py  # Lógica de negocio
│
├── infrastructure/
│   └── db/
│       └── session.py    # Conexión BD
│
├── api/
│   ├── auth.py           # Endpoints auth
│   └── users.py          # Endpoints usuarios
│
└── schema/
    └── user_schema.py    # Validación Pydantic
```

Para agregar nuevos módulos:
1. Crea modelo en `domain/models/`
2. Crea servicio en `application/services/`
3. Crea schemas en `schema/`
4. Crea routes en `api/`
5. Registra router en `main.py`

---

## ⚡ PRÓXIMOS PASOS

Después de verificar HU-01 y HU-02:

1. **Crear nuevo módulo** (ej: Beneficiarios)
   - Seguir estructura modular
   - Reutilizar UserService para autorización
   - Usar decoradores de roles

2. **Agregar features**
   - Refresh token automático
   - Rate limiting
   - Auditoría de cambios
   - 2FA

3. **Mejoras de performance**
   - Cachés en roles
   - Índices de BD
   - Batch operations

---

## 📞 SOPORTE

Si algo no funciona:

1. Revisa los logs del servidor
2. Verifica la configuración .env
3. Revisa que PostgreSQL está corriendo
4. Consulta POSTMAN_EXAMPLES.md para ejemplos

---

**¡Listo para empezar! 🚀**
