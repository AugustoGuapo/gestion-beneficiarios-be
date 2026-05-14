-- =====================================================================
-- MIGRACION HU-12: relacion entrega-bodega y cobertura de 3 dias
-- - Asegura estado en entrega
-- - Agrega id_bodega a entrega
-- - Backfill de entregas historicas
-- - Crea indice para validar cobertura por familia
-- - Crea inventario si no existe
-- =====================================================================

ALTER TABLE IF EXISTS entrega
    ADD COLUMN IF NOT EXISTS estado VARCHAR(20) DEFAULT 'ENTREGADA';

ALTER TABLE IF EXISTS entrega
    ADD COLUMN IF NOT EXISTS id_bodega INTEGER;

UPDATE entrega
SET id_bodega = COALESCE(
    id_bodega,
    (SELECT id_bodega FROM bodega ORDER BY id_bodega LIMIT 1)
)
WHERE id_bodega IS NULL;

ALTER TABLE IF EXISTS entrega
    ALTER COLUMN id_bodega SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'entrega'
          AND constraint_name = 'fk_entrega_bodega'
    ) THEN
        ALTER TABLE entrega
            ADD CONSTRAINT fk_entrega_bodega
            FOREIGN KEY (id_bodega)
            REFERENCES bodega(id_bodega)
            ON DELETE RESTRICT
            ON UPDATE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_entrega_familia_fecha_efectiva
    ON entrega(id_familia, fecha_efectiva DESC);

CREATE TABLE IF NOT EXISTS inventario (
    id_inventario SERIAL PRIMARY KEY,
    id_bodega INTEGER REFERENCES bodega(id_bodega),
    id_recurso INTEGER REFERENCES recurso(id_recurso),
    stock_actual DECIMAL(10, 2) DEFAULT 0
);

-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- DROP INDEX IF EXISTS idx_entrega_familia_fecha_efectiva;
-- ALTER TABLE entrega DROP CONSTRAINT IF EXISTS fk_entrega_bodega;
-- ALTER TABLE entrega DROP COLUMN IF EXISTS id_bodega;
-- ALTER TABLE entrega DROP COLUMN IF EXISTS estado;
-- DROP TABLE IF EXISTS inventario;
