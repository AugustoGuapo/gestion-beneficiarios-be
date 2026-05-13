-- =============================================
-- Migración: 1770000000_agregar_enum_nivel_riesgo_a_zona.sql
-- Creada: 2026-05-13 00:00:00
-- Descripción: Agregar el enum nivel_riesgo_tipo y la columna nivel_riesgo a zona
-- =============================================

DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1
		FROM pg_type
		WHERE typname = 'nivel_riesgo_tipo'
	) THEN
		CREATE TYPE nivel_riesgo_tipo AS ENUM ('bajo', 'medio', 'alto', 'crítico');
	END IF;
END
$$;

ALTER TABLE zona
ADD COLUMN IF NOT EXISTS nivel_riesgo nivel_riesgo_tipo;

UPDATE zona
SET nivel_riesgo = 'bajo'
WHERE nivel_riesgo IS NULL;

ALTER TABLE zona
ALTER COLUMN nivel_riesgo SET NOT NULL;

-- =============================================
-- ROLLBACK
-- =============================================
-- ALTER TABLE zona DROP COLUMN nivel_riesgo;
-- DROP TYPE nivel_riesgo_tipo;
