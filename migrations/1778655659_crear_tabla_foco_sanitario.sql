-- HU-25: Registrar foco de riesgo sanitario
-- Migración: Crear tabla foco_sanitario

CREATE TABLE IF NOT EXISTS foco_sanitario (
    id_foco          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_zona          INT,
    id_refugio       INT,
    tipo_vector      VARCHAR(50)  NOT NULL,
    nivel_riesgo     VARCHAR(20)  NOT NULL,
    acciones_tomadas TEXT,
    estado           VARCHAR(20)  NOT NULL DEFAULT 'ACTIVO',
    latitud          DECIMAL(10, 7),
    longitud         DECIMAL(10, 7),
    fecha_registro   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (tipo_vector  IN ('AGUA_CONTAMINADA', 'INSECTOS', 'ROEDORES', 'RESIDUOS', 'OTRO')),
    CHECK (nivel_riesgo IN ('BAJO', 'MEDIO', 'ALTO', 'CRITICO')),
    CHECK (estado       IN ('ACTIVO', 'EN_ATENCION', 'RESUELTO')),
    CHECK (id_zona IS NOT NULL OR id_refugio IS NOT NULL),

    CONSTRAINT fk_foco_zona
        FOREIGN KEY (id_zona)
        REFERENCES zona(id_zona)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT fk_foco_refugio
        FOREIGN KEY (id_refugio)
        REFERENCES refugios(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_foco_sanitario_estado      ON foco_sanitario(estado);
CREATE INDEX IF NOT EXISTS idx_foco_sanitario_nivel_riesgo ON foco_sanitario(nivel_riesgo);
CREATE INDEX IF NOT EXISTS idx_foco_sanitario_zona        ON foco_sanitario(id_zona);
