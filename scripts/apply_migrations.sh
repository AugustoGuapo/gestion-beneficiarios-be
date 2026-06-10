#!/bin/bash
set -euo pipefail

# ===============================================
# apply_migrations.sh
# ===============================================
# Aplica migraciones SQL en orden cronológico
# contra la base de datos PostgreSQL.
#
# Requiere: psql instalado o Docker funcionando
#
# Uso:
#   bash scripts/apply_migrations.sh              # aplica pendientes
#   bash scripts/apply_migrations.sh --dry-run    # muestra qué ejecutará
#   bash scripts/apply_migrations.sh --status     # muestra estado actual
# ===============================================

MIGRATIONS_DIR="migrations"
TRACKING_TABLE="_migrations"
APP_NAME="gestion-beneficiarios-be"

# Configuración de conexión (desde .env o defaults)
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-root}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-gestion_beneficiarios}"

# Comando para ejecutar SQL (usa Docker si está disponible)
PSQL_CMD="docker compose exec -T db psql -U ${DB_USER} -d ${DB_NAME}"

# Verificar que existan migraciones
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "❌ Directorio de migraciones no encontrado: $MIGRATIONS_DIR"
    exit 1
fi

# Obtener lista de archivos SQL ordenados por nombre
MIGRATION_FILES=$(ls "$MIGRATIONS_DIR"/*.sql 2>/dev/null | sort || true)

if [ -z "$MIGRATION_FILES" ]; then
    echo "ℹ️  No hay archivos de migración en $MIGRATIONS_DIR/"
    exit 0
fi

# ---- dry-run mode ----
if [ "${1:-}" = "--dry-run" ]; then
    echo "📋 Migraciones pendientes (dry-run):"
    echo ""
    for f in $MIGRATION_FILES; do
        APPLIED=$($PSQL_CMD -t -A -c "SELECT COUNT(*) FROM ${TRACKING_TABLE} WHERE filename = '$(basename "$f")';" 2>/dev/null || echo "0")
        if [ "$APPLIED" = "0" ] || [ -z "$APPLIED" ]; then
            echo "   ⏳ $(basename "$f")"
        else
            echo "   ✅ $(basename "$f") (ya aplicada)"
        fi
    done
    exit 0
fi

# ---- status mode ----
if [ "${1:-}" = "--status" ]; then
    echo "📊 Estado de migraciones:"
    echo ""
    
    # Verificar si la tabla de tracking existe
    TABLE_EXISTS=$($PSQL_CMD -t -A -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '${TRACKING_TABLE}');" 2>/dev/null || echo "false")
    
    if [ "$TABLE_EXISTS" != "true" ]; then
        echo "   ⚠️  Tabla de control '${TRACKING_TABLE}' no existe aún."
        echo "   Ninguna migración ha sido aplicada."
        exit 0
    fi
    
    for f in $MIGRATION_FILES; do
        APPLIED=$($PSQL_CMD -t -A -c "SELECT COUNT(*) FROM ${TRACKING_TABLE} WHERE filename = '$(basename "$f")';" 2>/dev/null || echo "0")
        if [ "$APPLIED" = "0" ] || [ -z "$APPLIED" ]; then
            echo "   ⏳ $(basename "$f") — pendiente"
        else
            APPLIED_AT=$($PSQL_CMD -t -A -c "SELECT applied_at FROM ${TRACKING_TABLE} WHERE filename = '$(basename "$f")';")
            echo "   ✅ $(basename "$f") — aplicada el $APPLIED_AT"
        fi
    done
    exit 0
fi

echo "🚀 Aplicando migraciones a ${DB_NAME}..."

# Asegurar que la tabla de tracking existe
$PSQL_CMD -c "
CREATE TABLE IF NOT EXISTS ${TRACKING_TABLE} (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64)
);
" > /dev/null 2>&1

APPLIED_COUNT=0

for f in $MIGRATION_FILES; do
    FILENAME=$(basename "$f")
    
    # Verificar si ya fue aplicada
    APPLIED=$($PSQL_CMD -t -A -c "SELECT COUNT(*) FROM ${TRACKING_TABLE} WHERE filename = '${FILENAME}';" 2>/dev/null || echo "0")
    
    if [ "$APPLIED" != "0" ]; then
        echo "   ✅ ${FILENAME} — ya aplicada, saltando"
        continue
    fi
    
    echo "   ⏳ ${FILENAME} — aplicando..."
    
    # Calcular checksum del archivo
    CHECKSUM=$(sha256sum "$f" | cut -d' ' -f1)
    
    # Ejecutar migración dentro de una transacción
    if $PSQL_CMD -v ON_ERROR_STOP=1 -f "$f" > /dev/null 2>&1; then
        # Registrar migración
        $PSQL_CMD -c "INSERT INTO ${TRACKING_TABLE} (filename, checksum) VALUES ('${FILENAME}', '${CHECKSUM}');" > /dev/null 2>&1
        echo "   ✅ ${FILENAME} — aplicada exitosamente"
        APPLIED_COUNT=$((APPLIED_COUNT + 1))
    else
        echo "   ❌ ${FILENAME} — ERROR al aplicar. Revise el archivo."
        exit 1
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$APPLIED_COUNT" -eq 0 ]; then
    echo "📦 No hay migraciones nuevas para aplicar."
else
    echo "📦 ${APPLIED_COUNT} migración(es) aplicada(s) correctamente."
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"