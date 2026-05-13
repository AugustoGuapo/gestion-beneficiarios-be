#!/bin/bash
# ========================================================================
# Script de ejecución de migración y validación
# ========================================================================
# Este script ejecuta la migración y luego valida que todo funcionó

DB_USER="root"
DB_PASSWORD="root"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="gestion_beneficiarios"

# Variables de entorno
export PGPASSWORD=$DB_PASSWORD

echo "=========================================="
echo "EJECUTANDO MIGRACIÓN SQL"
echo "=========================================="
echo ""

# Ejecutar migración
echo "⏳ Ejecutando migrate_usuario_hu01_hu02.sql..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f ./scripts/migrate_usuario_hu01_hu02.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migración ejecutada exitosamente"
else
    echo ""
    echo "❌ Error durante la migración"
    exit 1
fi

echo ""
echo "=========================================="
echo "VALIDANDO RESULTADOS"
echo "=========================================="
echo ""

# Ejecutar validación
echo "⏳ Ejecutando validación..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f ./scripts/test_migration_validation.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Validación completada exitosamente"
else
    echo ""
    echo "❌ Error durante la validación"
    exit 1
fi

echo ""
echo "=========================================="
echo "PROCESO COMPLETADO"
echo "=========================================="
