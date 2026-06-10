-- =============================================
-- Migración: 1778749583_crear_tabla_familia_refugio.sql
-- Creada: 2026-05-14
-- Descripción (HU-24): Crea la tabla `familia_refugio` que registra el historial
--   de asignaciones de una familia a un refugio.
-- =============================================

DO $$
DECLARE
    v_pk_name TEXT;
    v_has_identity BOOLEAN;
BEGIN
    IF to_regclass('public.familia_refugio') IS NULL THEN
        -- Tabla no existe → Crear desde cero con estructura final
        CREATE TABLE familia_refugio (
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
        RAISE NOTICE 'Tabla familia_refugio creada desde cero.';
        RETURN;
    END IF;

    -- Tabla existe. Verificar si ya tiene identity (estructura moderna).
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'familia_refugio'
          AND column_name = 'id_familia_refugio'
          AND is_identity = 'YES'
    ) INTO v_has_identity;

    IF v_has_identity THEN
        RAISE NOTICE 'familia_refugio ya tiene estructura final (identity). Saltando migración.';
        RETURN;
    END IF;

    -- Migrar tabla legacy a estructura moderna
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'familia_refugio'
          AND column_name = 'id_familia_refugio'
    ) THEN
        ALTER TABLE familia_refugio ADD COLUMN id_familia_refugio INT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'familia_refugio'
          AND column_name = 'fecha_ingreso'
    ) THEN
        ALTER TABLE familia_refugio ADD COLUMN fecha_ingreso TIMESTAMP;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'familia_refugio'
          AND column_name = 'fecha_salida'
    ) THEN
        ALTER TABLE familia_refugio ADD COLUMN fecha_salida TIMESTAMP NULL;
    END IF;

    UPDATE familia_refugio SET fecha_ingreso = CURRENT_TIMESTAMP WHERE fecha_ingreso IS NULL;

    ALTER TABLE familia_refugio
        ALTER COLUMN fecha_ingreso SET DEFAULT CURRENT_TIMESTAMP,
        ALTER COLUMN fecha_ingreso SET NOT NULL;

    CREATE SEQUENCE IF NOT EXISTS familia_refugio_id_familia_refugio_seq;
    ALTER TABLE familia_refugio
        ALTER COLUMN id_familia_refugio SET DEFAULT nextval('familia_refugio_id_familia_refugio_seq');

    UPDATE familia_refugio
    SET id_familia_refugio = nextval('familia_refugio_id_familia_refugio_seq')
    WHERE id_familia_refugio IS NULL;

    ALTER TABLE familia_refugio ALTER COLUMN id_familia_refugio SET NOT NULL;

    -- Reemplazar PK si es necesario
    SELECT tc.constraint_name INTO v_pk_name
    FROM information_schema.table_constraints tc
    WHERE tc.table_schema = 'public'
      AND tc.table_name = 'familia_refugio'
      AND tc.constraint_type = 'PRIMARY KEY';

    IF v_pk_name IS NOT NULL AND v_pk_name <> 'familia_refugio_pkey' THEN
        EXECUTE format('ALTER TABLE familia_refugio DROP CONSTRAINT %I', v_pk_name);
    END IF;

    IF v_pk_name IS NULL OR v_pk_name <> 'familia_refugio_pkey' THEN
        ALTER TABLE familia_refugio ADD CONSTRAINT familia_refugio_pkey PRIMARY KEY (id_familia_refugio);
    END IF;

    -- Reemplazar FKs y CHECK
    ALTER TABLE familia_refugio
        DROP CONSTRAINT IF EXISTS fk_fr_familia,
        DROP CONSTRAINT IF EXISTS fk_fr_refugio,
        DROP CONSTRAINT IF EXISTS ck_familia_refugio_fechas;

    ALTER TABLE familia_refugio
        ADD CONSTRAINT fk_fr_familia
            FOREIGN KEY (id_familia) REFERENCES familia (id_familia)
            ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT fk_fr_refugio
            FOREIGN KEY (id_refugio) REFERENCES refugios (id)
            ON DELETE RESTRICT ON UPDATE CASCADE,
        ADD CONSTRAINT ck_familia_refugio_fechas
            CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso);
END $$;

-- Índices
CREATE UNIQUE INDEX IF NOT EXISTS uq_familia_refugio_activo
    ON familia_refugio (id_familia) WHERE fecha_salida IS NULL;

CREATE INDEX IF NOT EXISTS idx_familia_refugio_refugio ON familia_refugio (id_refugio);
CREATE INDEX IF NOT EXISTS idx_familia_refugio_familia_fecha ON familia_refugio (id_familia, fecha_ingreso);

-- =============================================
-- ROLLBACK
-- =============================================
-- DROP INDEX IF EXISTS idx_familia_refugio_familia_fecha;
-- DROP INDEX IF EXISTS idx_familia_refugio_refugio;
-- DROP INDEX IF EXISTS uq_familia_refugio_activo;
-- DROP TABLE IF EXISTS familia_refugio;
