-- =====================================================================
-- MIGRACION HU-08: Agregar id_zona a familia para factor de ubicacion
-- Permite que el puntaje de prioridad considere el nivel de riesgo
-- de la zona donde reside la familia.
-- =====================================================================

ALTER TABLE IF EXISTS familia
    ADD COLUMN IF NOT EXISTS id_zona INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'familia'
          AND constraint_name = 'fk_familia_zona'
    ) THEN
        ALTER TABLE familia
            ADD CONSTRAINT fk_familia_zona
            FOREIGN KEY (id_zona)
            REFERENCES zona(id_zona)
            ON DELETE SET NULL
            ON UPDATE CASCADE;
    END IF;
END $$;

COMMENT ON COLUMN familia.id_zona IS 'Zona de residencia de la familia, usada para calcular factor de riesgo en el puntaje de prioridad';

-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- ALTER TABLE familia DROP CONSTRAINT IF EXISTS fk_familia_zona;
-- ALTER TABLE familia DROP COLUMN IF EXISTS id_zona;
