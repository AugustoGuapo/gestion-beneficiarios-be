-- =============================================
-- Migración: 1778784170_agregar_umbral_alerta_a_recurso.sql
-- Creada: 2026-05-14 13:42:50
-- Descripción: Agregar umbral alerta a recurso
-- =============================================

ALTER TABLE recurso
ADD COLUMN IF NOT EXISTS umbral_alerta INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'recurso_umbral_alerta_check'
    ) THEN
        ALTER TABLE recurso
        ADD CONSTRAINT recurso_umbral_alerta_check
        CHECK (umbral_alerta IS NULL OR umbral_alerta >= 1);
    END IF;
END
$$;

-- =============================================
-- ROLLBACK
-- =============================================
-- ALTER TABLE recurso DROP CONSTRAINT IF EXISTS recurso_umbral_alerta_check;
-- ALTER TABLE recurso DROP COLUMN IF EXISTS umbral_alerta;
