-- =============================================
-- Migración: 1778672105_agregar_categoria_unidad_y_activo_a_recurso.sql
-- Creada: 2026-05-13 06:35:05
-- Descripción: Agregar categoria unidad y activo a recurso
-- =============================================
-- Requisito: debe existir la tabla public.recurso (creada por scripts/init.sql al
-- primer arranque del contenedor Postgres con volumen vacío). Si no existe:
--   docker compose down -v
--   docker compose up -d
--   make migrate
-- =============================================

DO $$
BEGIN
    IF to_regclass('public.recurso') IS NULL THEN
        RAISE EXCEPTION
            'La tabla public.recurso no existe. El esquema base no se cargó (init.sql). '
            'Recrea el volumen de datos: docker compose down -v && docker compose up -d '
            'y vuelve a ejecutar make migrate.';
    END IF;
END
$$;

-- 1) Agregar columnas con defaults temporales
ALTER TABLE recurso
ADD COLUMN IF NOT EXISTS categoria VARCHAR(50) DEFAULT 'ALIMENTOS',
ADD COLUMN IF NOT EXISTS unidad_medida VARCHAR(20) DEFAULT 'KG',
ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;

-- 2) Backfill exacto con mapeo por nombre (incl. variantes con tilde; ILIKE no ignora acentos)
UPDATE recurso
SET
    categoria = CASE
        WHEN nombre ILIKE '%arroz%' THEN 'ALIMENTOS'
        WHEN nombre ILIKE '%aceite%' THEN 'ALIMENTOS'
        WHEN nombre ILIKE '%lentejas%' THEN 'ALIMENTOS'
        WHEN nombre ILIKE '%frijol%' OR nombre ILIKE '%frijoles%' THEN 'ALIMENTOS'
        WHEN nombre ILIKE '%atun%' OR nombre ILIKE '%atún%' THEN 'ALIMENTOS'
        WHEN nombre ILIKE '%sal%' THEN 'ALIMENTOS'
        WHEN nombre ILIKE '%azucar%' OR nombre ILIKE '%azúcar%' THEN 'ALIMENTOS'
        WHEN nombre ILIKE '%agua%' THEN 'ALIMENTOS'
        WHEN nombre ILIKE '%colchoneta%' THEN 'COLCHONETA'
        WHEN nombre ILIKE '%sabana%' OR nombre ILIKE '%sábana%' THEN 'COBIJA'
        ELSE categoria
    END,
    unidad_medida = CASE
        WHEN nombre ILIKE '%1l%' OR nombre ILIKE '%5l%' THEN 'LITRO'
        WHEN nombre ILIKE '%kg%' THEN 'KG'
        WHEN nombre ILIKE '%colchoneta%' THEN 'UNIDAD'
        WHEN nombre ILIKE '%sabana%' OR nombre ILIKE '%sábana%' THEN 'UNIDAD'
        WHEN nombre ILIKE '%atun%' OR nombre ILIKE '%atún%' THEN 'UNIDAD'
        ELSE unidad_medida
    END
WHERE
    categoria IS NULL
    OR unidad_medida IS NULL
    OR (categoria = 'ALIMENTOS' AND unidad_medida = 'KG');

-- 3) Forzar NOT NULL
ALTER TABLE recurso
ALTER COLUMN categoria SET NOT NULL,
ALTER COLUMN unidad_medida SET NOT NULL,
ALTER COLUMN activo SET NOT NULL;

-- 4) CHECKs (enum en DB). IF NOT EXISTS no aplica a CHECK de esta forma en PG 16;
-- se usa pg_constraint + ADD CONSTRAINT sin IF NOT EXISTS.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_recurso_categoria'
    ) THEN
        ALTER TABLE recurso
        ADD CONSTRAINT chk_recurso_categoria
        CHECK (categoria IN ('ALIMENTOS', 'COBIJA', 'COLCHONETA', 'ASEO', 'MEDICAMENTO'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_recurso_unidad'
    ) THEN
        ALTER TABLE recurso
        ADD CONSTRAINT chk_recurso_unidad
        CHECK (unidad_medida IN ('KG', 'UNIDAD', 'LITRO'));
    END IF;
END
$$;

-- 5) Unicidad nombre + categoria
CREATE UNIQUE INDEX IF NOT EXISTS uq_recurso_nombre_categoria
ON recurso (nombre, categoria);

-- =============================================
-- ROLLBACK (opcional - descomentar si aplica)
-- =============================================
-- DROP INDEX IF EXISTS uq_recurso_nombre_categoria;
-- ALTER TABLE recurso DROP CONSTRAINT IF EXISTS chk_recurso_unidad;
-- ALTER TABLE recurso DROP CONSTRAINT IF EXISTS chk_recurso_categoria;
-- ALTER TABLE recurso DROP COLUMN IF EXISTS activo;
-- ALTER TABLE recurso DROP COLUMN IF EXISTS unidad_medida;
-- ALTER TABLE recurso DROP COLUMN IF EXISTS categoria;
