-- =========================
-- V002: Agregar id_familia y nuevos campos a tabla persona
-- HU-05: Registrar personas dentro de familia
-- =========================

ALTER TABLE persona
    ADD COLUMN IF NOT EXISTS id_familia INT,
    ADD COLUMN IF NOT EXISTS tipo_documento VARCHAR(20),
    ADD COLUMN IF NOT EXISTS numero_documento VARCHAR(20),
    ADD COLUMN IF NOT EXISTS tiene_discapacidad BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS tiene_enfermedad_cronica BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS es_cabeza_familia BOOLEAN DEFAULT FALSE;

ALTER TABLE persona
    ADD CONSTRAINT fk_persona_familia
    FOREIGN KEY (id_familia) REFERENCES familia(id_familia)
    ON DELETE SET NULL ON UPDATE CASCADE;