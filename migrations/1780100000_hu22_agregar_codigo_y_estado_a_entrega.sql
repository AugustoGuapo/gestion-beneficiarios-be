-- =====================================================================
-- MIGRACION HU-22: Registrar entrega individual
-- Agrega columnas codigo y estado a la tabla entrega + indices de apoyo
-- =====================================================================

-- 1) Columna codigo (identificador unico legible: ENT-AAAA-NNNNN)
ALTER TABLE IF EXISTS entrega
    ADD COLUMN IF NOT EXISTS codigo VARCHAR(20);

CREATE UNIQUE INDEX IF NOT EXISTS uq_entrega_codigo ON entrega(codigo);

-- 2) Columna estado: PENDIENTE, ENTREGADA, ANULADA
ALTER TABLE IF EXISTS entrega
    ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'ENTREGADA';

-- Backfill defensivo (filas creadas antes de la migracion)
UPDATE entrega SET estado = 'ENTREGADA' WHERE estado IS NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'entrega'
          AND constraint_name = 'ck_entrega_estado'
    ) THEN
        ALTER TABLE entrega
            ADD CONSTRAINT ck_entrega_estado
            CHECK (estado IN ('PENDIENTE', 'ENTREGADA', 'ANULADA'));
    END IF;
END $$;

-- 3) Indice para acelerar busquedas/validaciones (HU-23 lo usa para prevenir
--    entregas duplicadas por familia + fecha_efectiva)
CREATE INDEX IF NOT EXISTS idx_entrega_familia_fecha
    ON entrega(id_familia, fecha_efectiva);

-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- ALTER TABLE entrega DROP CONSTRAINT IF EXISTS ck_entrega_estado;
-- DROP INDEX IF EXISTS idx_entrega_familia_fecha;
-- DROP INDEX IF EXISTS uq_entrega_codigo;
-- ALTER TABLE entrega DROP COLUMN IF EXISTS estado;
-- ALTER TABLE entrega DROP COLUMN IF EXISTS codigo;
