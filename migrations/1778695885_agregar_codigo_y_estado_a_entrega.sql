-- =============================================
-- Migración: 1778695885_agregar_codigo_y_estado_a_entrega.sql
-- Creada: 2026-05-13
-- Descripción (HU-22): Añadir columnas `codigo` y `estado` a la tabla `entrega`
--   - codigo: identificador único con formato ENT-AAAA-NNNNN (secuencial por año)
--   - estado: ciclo de vida de la entrega (PENDIENTE / ENTREGADA / ANULADA)
-- =============================================

ALTER TABLE entrega
ADD COLUMN IF NOT EXISTS codigo VARCHAR(50);

CREATE UNIQUE INDEX IF NOT EXISTS idx_entrega_codigo
ON entrega (codigo);

ALTER TABLE entrega
ADD COLUMN IF NOT EXISTS estado VARCHAR(20) NOT NULL DEFAULT 'ENTREGADA';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.constraint_column_usage
        WHERE table_name = 'entrega'
          AND constraint_name = 'entrega_estado_check'
    ) THEN
        ALTER TABLE entrega
        ADD CONSTRAINT entrega_estado_check
        CHECK (estado IN ('PENDIENTE', 'ENTREGADA', 'ANULADA'));
    END IF;
END
$$;

-- Índice útil para detectar entregas duplicadas (HU-23): misma familia + mismo día.
CREATE INDEX IF NOT EXISTS idx_entrega_familia_fecha
ON entrega (id_familia, fecha_efectiva);

-- =============================================
-- ROLLBACK
-- =============================================
-- DROP INDEX IF EXISTS idx_entrega_familia_fecha;
-- ALTER TABLE entrega DROP CONSTRAINT IF EXISTS entrega_estado_check;
-- ALTER TABLE entrega DROP COLUMN IF EXISTS estado;
-- DROP INDEX IF EXISTS idx_entrega_codigo;
-- ALTER TABLE entrega DROP COLUMN IF EXISTS codigo;
