-- ==================================================
-- MIGRACIÓN 001
-- Agrega inventario, donacion y donacion_recurso
-- sobre el esquema base existente.
-- ==================================================

CREATE TABLE IF NOT EXISTS inventario (
    id_inventario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recurso_id INT NOT NULL UNIQUE,
    cantidad DOUBLE PRECISION NOT NULL DEFAULT 0,

    CONSTRAINT fk_inventario_recurso
    FOREIGN KEY (recurso_id)
    REFERENCES recurso(id_recurso)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS donacion (
    id_donacion INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    referencia VARCHAR(255),
    fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS donacion_recurso (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    donacion_id INT NOT NULL,
    recurso_id INT NOT NULL,
    cantidad DOUBLE PRECISION NOT NULL,

    CONSTRAINT fk_donacion_recurso_donacion
    FOREIGN KEY (donacion_id)
    REFERENCES donacion(id_donacion)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_donacion_recurso_recurso
    FOREIGN KEY (recurso_id)
    REFERENCES recurso(id_recurso)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_inventario_recurso ON inventario (recurso_id);
CREATE INDEX IF NOT EXISTS idx_donrec_donacion ON donacion_recurso (donacion_id);
CREATE INDEX IF NOT EXISTS idx_donrec_recurso ON donacion_recurso (recurso_id);