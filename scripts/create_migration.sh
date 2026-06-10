#!/bin/bash
set -euo pipefail

# ===============================================
# create_migration.sh
# ===============================================
# Uso: bash scripts/create_migration.sh "descripcion_del_cambio"
#
# Crea un archivo de migración con el formato:
#   {EPOCH}_{snake_case_description}.sql
#
# Ejemplo:
#   bash scripts/create_migration.sh "Agregar campo telefono a tabla persona"
#   -> migrations/1744567890_agregar_campo_telefono_a_tabla_persona.sql
# ===============================================

MIGRATIONS_DIR="migrations"

if [ $# -lt 1 ]; then
    echo "❌ Error: Proporciona un nombre descriptivo para la migración."
    echo ""
    echo "Uso: bash scripts/create_migration.sh \"descripcion_del_cambio\""
    echo ""
    echo "Ejemplos:"
    echo "  bash scripts/create_migration.sh \"Crear tabla refugios\""
    echo "  bash scripts/create_migration.sh \"Agregar columna email a usuario\""
    exit 1
fi

NAME="$*"

# Convertir a snake_case
SNAKE_NAME=$(echo "$NAME" \
    | tr '[:upper:]' '[:lower:]' \
    | sed 's/ñ/n/g' \
    | sed 's/[^a-z0-9] /_/g' \
    | sed 's/[^a-z0-9]/_/g' \
    | sed 's/__*/_/g' \
    | sed 's/^_//;s/_$//')

EPOCH=$(date +%s)
FILENAME="${EPOCH}_${SNAKE_NAME}.sql"
FILEPATH="${MIGRATIONS_DIR}/${FILENAME}"

# Crear directorio si no existe
mkdir -p "$MIGRATIONS_DIR"

# Crear archivo con template
cat > "$FILEPATH" <<- EOF
-- =============================================
-- Migración: ${FILENAME}
-- Creada: $(date '+%Y-%m-%d %H:%M:%S')
-- Descripción: ${NAME}
-- =============================================

-- ⚠️  Completar con SQL de la migración
-- Ejemplo:
--   ALTER TABLE persona ADD COLUMN telefono VARCHAR(20);

-- =============================================
-- ROLLBACK (opcional - descomentar si aplica)
-- =============================================
-- ALTER TABLE persona DROP COLUMN telefono;
EOF

echo "✅ Migración creada: ${FILEPATH}"
echo ""
echo "📝 Edita el archivo y completa el SQL de la migración."
echo "📖 Para aplicar: make migrate"
echo "    O: bash scripts/apply_migrations.sh"
