-- =========================
-- MIGRACIÓN: AÑADIR CAMPOS A BODEGA Y CREAR AUDIT_LOG
-- =========================

-- BODEGA: compatibilidad con HU-11 y HU-13
ALTER TABLE IF EXISTS bodega
    ADD COLUMN IF NOT EXISTS latitud DECIMAL(10, 8) NOT NULL DEFAULT 8.75000000,
    ADD COLUMN IF NOT EXISTS longitud DECIMAL(11, 8) NOT NULL DEFAULT -75.88000000,
    ADD COLUMN IF NOT EXISTS capacidad_max_kg DECIMAL(10, 2) NOT NULL DEFAULT 20000.00,
    ADD COLUMN IF NOT EXISTS peso_actual_kg DECIMAL(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS zona_id INTEGER;

ALTER TABLE IF EXISTS bodega
    DROP COLUMN IF EXISTS fecha_registro;

UPDATE bodega
SET zona_id = COALESCE(zona_id, 1)
WHERE zona_id IS NULL;

ALTER TABLE IF EXISTS bodega
    ALTER COLUMN zona_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_bodega_zona ON bodega(zona_id);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'bodega'
          AND constraint_name = 'fk_bodega_zona'
    ) THEN
        ALTER TABLE bodega
            ADD CONSTRAINT fk_bodega_zona
            FOREIGN KEY (zona_id)
            REFERENCES zona(id_zona)
            ON DELETE RESTRICT
            ON UPDATE CASCADE;
    END IF;
END $$;

-- AUDIT LOG: requerido por el middleware
-- Ya fue creada en init.sql o migración previa; aquí solo se omite
-- para evitar conflictos de tipo de columna (SERIAL vs GENERATED AS IDENTITY).
-- Si no existe, la crea.
CREATE TABLE IF NOT EXISTS audit_log (
    id_audit_log INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(255),
    method VARCHAR(20) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    status_code INTEGER NOT NULL,
    ip_address VARCHAR(100),
    payload JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ROLLBACK
-- No se define rollback automático para columnas agregadas con IF NOT EXISTS.
-- En caso necesario, retirar manualmente la migración aplicada.
