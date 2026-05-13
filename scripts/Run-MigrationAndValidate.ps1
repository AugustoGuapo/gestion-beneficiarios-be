# ========================================================================
# Script de ejecución de migración y validación (PowerShell)
# ========================================================================
# Este script ejecuta la migración y luego valida que todo funcionó

param(
    [string]$DB_HOST = "localhost",
    [string]$DB_PORT = "5432",
    [string]$DB_USER = "root",
    [string]$DB_PASSWORD = "root",
    [string]$DB_NAME = "gestion_beneficiarios"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================`n" -ForegroundColor Cyan
Write-Host "EJECUTANDO MIGRACIÓN SQL" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# Variables de entorno
$env:PGPASSWORD = $DB_PASSWORD

# Obtener ruta del directorio actual
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "⏳ Ejecutando migrate_usuario_hu01_hu02.sql..." -ForegroundColor Yellow
try {
    & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$scriptDir\migrate_usuario_hu01_hu02.sql"
    Write-Host "`n✅ Migración ejecutada exitosamente`n" -ForegroundColor Green
} catch {
    Write-Host "`n❌ Error durante la migración: $_`n" -ForegroundColor Red
    exit 1
}

Write-Host "==========================================`n" -ForegroundColor Cyan
Write-Host "VALIDANDO RESULTADOS" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

Write-Host "⏳ Ejecutando validación..." -ForegroundColor Yellow
try {
    & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$scriptDir\test_migration_validation.sql"
    Write-Host "`n✅ Validación completada exitosamente`n" -ForegroundColor Green
} catch {
    Write-Host "`n❌ Error durante la validación: $_`n" -ForegroundColor Red
    exit 1
}

Write-Host "==========================================`n" -ForegroundColor Cyan
Write-Host "PROCESO COMPLETADO" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# Mostrar resumen rápido
Write-Host "📊 RESUMEN RÁPIDO:" -ForegroundColor Yellow
$env:PGPASSWORD = $DB_PASSWORD
& psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) as total_usuarios, MAX(id_usuario) as max_id, COUNT(CASE WHEN activo THEN 1 END) as activos FROM usuario;" -t
