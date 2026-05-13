-- =========================
-- V001: Agregar campos faltantes a tabla familia
-- HU-04: Registrar familia afectada
-- =========================

ALTER TABLE familia
    ADD COLUMN IF NOT EXISTS codigo_familia VARCHAR(15) UNIQUE NOT NULL,
    ADD COLUMN IF NOT EXISTS acepta_privacidad BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS puntaje_prioridad FLOAT DEFAULT 0.0;