-- =========================
-- MIGRACIÓN HU-10: REFUGIOS
-- =========================

ALTER TABLE IF EXISTS refugios
    ADD COLUMN IF NOT EXISTS ubicacion TEXT,
    ADD COLUMN IF NOT EXISTS latitud DECIMAL(10, 8) NOT NULL DEFAULT 0.00000000,
    ADD COLUMN IF NOT EXISTS longitud DECIMAL(11, 8) NOT NULL DEFAULT 0.00000000,
    ADD COLUMN IF NOT EXISTS capacidad_maxima INTEGER,
    ADD COLUMN IF NOT EXISTS ocupacion_actual INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS id_zona INTEGER,
    ADD COLUMN IF NOT EXISTS fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'refugios' AND column_name = 'ubicacion_textual'
    ) THEN
        ALTER TABLE refugios RENAME COLUMN ubicacion_textual TO ubicacion;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'refugios' AND column_name = 'capacidad_maxima_personas'
    ) THEN
        ALTER TABLE refugios RENAME COLUMN capacidad_maxima_personas TO capacidad_maxima;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'refugios' AND column_name = 'zona_id'
    ) THEN
        ALTER TABLE refugios RENAME COLUMN zona_id TO id_zona;
    END IF;
END $$;

UPDATE refugios
SET
    ubicacion = COALESCE(ubicacion, 'Sin especificar'),
    latitud = COALESCE(latitud, 0),
    longitud = COALESCE(longitud, 0),
    capacidad_maxima = COALESCE(capacidad_maxima, 1),
    ocupacion_actual = COALESCE(ocupacion_actual, 0),
    id_zona = COALESCE(id_zona, 1)
WHERE TRUE;

ALTER TABLE IF EXISTS refugios
    ALTER COLUMN ubicacion SET NOT NULL,
    ALTER COLUMN capacidad_maxima SET NOT NULL,
    ALTER COLUMN ocupacion_actual SET DEFAULT 0,
    ALTER COLUMN ocupacion_actual SET NOT NULL,
    ALTER COLUMN id_zona SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'refugios'
          AND constraint_name = 'ck_refugios_ocupacion'
    ) THEN
        ALTER TABLE refugios
            ADD CONSTRAINT ck_refugios_ocupacion
            CHECK (ocupacion_actual <= capacidad_maxima);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'refugios'
          AND constraint_name = 'ck_refugios_capacidad'
    ) THEN
        ALTER TABLE refugios
            ADD CONSTRAINT ck_refugios_capacidad
            CHECK (capacidad_maxima > 0);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'refugios'
          AND constraint_name = 'fk_refugios_zona'
    ) THEN
        ALTER TABLE refugios
            ADD CONSTRAINT fk_refugios_zona
            FOREIGN KEY (id_zona)
            REFERENCES zona(id_zona)
            ON DELETE RESTRICT
            ON UPDATE CASCADE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_refugios_zona ON refugios(id_zona);

-- AUDIT LOG ya existe por migración previa.
