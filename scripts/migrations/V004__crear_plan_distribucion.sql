-- =========================
-- V004: Crear tablas de plan de distribución
-- HU-21: Generar plan de distribución priorizado
-- =========================

CREATE TABLE IF NOT EXISTS plan_distribucion (
    id_plan INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'programada',
    id_familia INT NOT NULL,
    puntaje_al_generar FLOAT NOT NULL,
    prioridad_orden INT NOT NULL,

    CONSTRAINT fk_plan_familia
    FOREIGN KEY (id_familia) REFERENCES familia(id_familia)
    ON DELETE CASCADE ON UPDATE CASCADE,

    CHECK (estado IN ('programada', 'en_curso', 'completada'))
);

CREATE TABLE IF NOT EXISTS detalle_plan_distribucion (
    id_detalle INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_plan INT NOT NULL,
    id_recurso INT NOT NULL,
    cantidad_asignada INT NOT NULL,
    cantidad_entregada INT DEFAULT 0,

    CONSTRAINT fk_detalle_plan
    FOREIGN KEY (id_plan) REFERENCES plan_distribucion(id_plan)
    ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_detalle_recurso
    FOREIGN KEY (id_recurso) REFERENCES recurso(id_recurso)
    ON DELETE RESTRICT ON UPDATE CASCADE,

    CHECK (cantidad_asignada > 0),
    CHECK (cantidad_entregada >= 0)
);