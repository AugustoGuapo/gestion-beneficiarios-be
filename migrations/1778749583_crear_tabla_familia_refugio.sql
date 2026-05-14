-- =============================================
-- Migración: 1778749583_crear_tabla_familia_refugio.sql
-- Creada: 2026-05-14
-- Descripción (HU-24): Crea la tabla `familia_refugio` que registra el historial
--   de asignaciones de una familia a un refugio. La asignación activa es la fila
--   con `fecha_salida IS NULL`. Cuando se realiza un traslado, se cierra la
--   asignación activa actual (set `fecha_salida = NOW()`) y se inserta una nueva
--   para el refugio destino.
-- =============================================

CREATE TABLE IF NOT EXISTS familia_refugio (
    id_familia_refugio INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_familia INT NOT NULL,
    id_refugio INT NOT NULL,
    fecha_ingreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_salida TIMESTAMP NULL,

    CONSTRAINT fk_fr_familia
        FOREIGN KEY (id_familia)
        REFERENCES familia (id_familia)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_fr_refugio
        FOREIGN KEY (id_refugio)
        REFERENCES refugios (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT ck_familia_refugio_fechas
        CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso)
);

-- Solo una asignación ACTIVA por familia (donde fecha_salida IS NULL).
CREATE UNIQUE INDEX IF NOT EXISTS uq_familia_refugio_activo
ON familia_refugio (id_familia)
WHERE fecha_salida IS NULL;

CREATE INDEX IF NOT EXISTS idx_familia_refugio_refugio
ON familia_refugio (id_refugio);

CREATE INDEX IF NOT EXISTS idx_familia_refugio_familia_fecha
ON familia_refugio (id_familia, fecha_ingreso);

-- =============================================
-- ROLLBACK
-- =============================================
-- DROP INDEX IF EXISTS idx_familia_refugio_familia_fecha;
-- DROP INDEX IF EXISTS idx_familia_refugio_refugio;
-- DROP INDEX IF EXISTS uq_familia_refugio_activo;
-- DROP TABLE IF EXISTS familia_refugio;
