-- =========================
-- TABLA PERSONA
-- =========================
CREATE TABLE persona (
    id_persona INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    edad INT,
    es_nino BOOLEAN DEFAULT FALSE,
    es_anciano BOOLEAN DEFAULT FALSE,
    es_embarazada BOOLEAN DEFAULT FALSE,
    CHECK (edad >= 0)
);

-- =========================
-- TABLA FAMILIA
-- =========================
CREATE TABLE familia (
    id_familia INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_representante INT UNIQUE,

    CONSTRAINT fk_representante
    FOREIGN KEY (id_representante)
    REFERENCES persona(id_persona)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- =========================
-- TABLA ZONA
-- =========================
CREATE TYPE nivel_riesgo_tipo AS ENUM ('bajo', 'medio', 'alto', 'crítico');

CREATE TABLE zona (
    id_zona INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nivel_riesgo_tipo nivel_riesgo_tipo NOT NULL
);

-- =========================
-- TABLA UBICACION
-- =========================
CREATE TABLE ubicacion (
    id_ubicacion INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    direccion VARCHAR(200),
    id_zona INT,

    CONSTRAINT fk_zona
    FOREIGN KEY (id_zona)
    REFERENCES zona(id_zona)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- =========================
-- TABLA FAMILIA_REFUGIO
-- =========================
CREATE TABLE IF NOT EXISTS familia_refugio (
    id_familia INT,
    id_refugio INT,
    fecha_ingreso DATE,

    PRIMARY KEY (id_familia, id_refugio),

    CONSTRAINT fk_fr_familia
    FOREIGN KEY (id_familia)
    REFERENCES familia(id_familia)
    ON DELETE CASCADE
);

-- =========================
-- TABLA ORIGEN_RECURSO
-- =========================
CREATE TABLE origen_recurso (
    id_origen INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50),

    CHECK (tipo IN ('ALCALDIA', 'GOBERNACION', 'EMPRESA', 'CIUDADANO'))
);

-- =========================
-- TABLA RECURSO
-- =========================
CREATE TABLE recurso (
    id_recurso INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    peso_unitario_kg DECIMAL(10,2),
    id_origen INT,

    CHECK (peso_unitario_kg > 0),

    CONSTRAINT fk_origen
    FOREIGN KEY (id_origen)
    REFERENCES origen_recurso(id_origen)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

-- =========================
-- TABLA BODEGA (Adaptada para HU-11)
-- =========================
CREATE TABLE bodega (
    id_bodega INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    latitud DECIMAL(10, 8) NOT NULL DEFAULT 8.75000000,
    longitud DECIMAL(11, 8) NOT NULL DEFAULT -75.88000000,
    capacidad_max_kg DECIMAL(10, 2) NOT NULL DEFAULT 20000.00,
    peso_actual_kg DECIMAL(10, 2) DEFAULT 0 CHECK (peso_actual_kg >= 0),
    zona_id INTEGER NOT NULL REFERENCES zona(id_zona) ON DELETE RESTRICT ON UPDATE CASCADE,
    CHECK (capacidad_max_kg > 0)
);

-- Ajuste seguro para bases ya existentes
ALTER TABLE IF EXISTS bodega
    ADD COLUMN IF NOT EXISTS latitud DECIMAL(10, 8) NOT NULL DEFAULT 8.75000000,
    ADD COLUMN IF NOT EXISTS longitud DECIMAL(11, 8) NOT NULL DEFAULT -75.88000000,
    ADD COLUMN IF NOT EXISTS capacidad_max_kg DECIMAL(10, 2) NOT NULL DEFAULT 20000.00,
    ADD COLUMN IF NOT EXISTS peso_actual_kg DECIMAL(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS zona_id INTEGER;

UPDATE bodega
SET zona_id = COALESCE(zona_id, 1)
WHERE zona_id IS NULL;

ALTER TABLE IF EXISTS bodega
    ALTER COLUMN zona_id SET NOT NULL;

ALTER TABLE IF EXISTS bodega
    DROP COLUMN IF EXISTS fecha_registro;

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

-- =========================
-- TABLA MOVIMIENTO_INVENTARIO
-- =========================
CREATE TABLE movimiento_inventario (
    id_movimiento INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo VARCHAR(10),
    cantidad INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_recurso INT,
    id_bodega INT,

    CHECK (tipo IN ('ENTRADA', 'SALIDA')),
    CHECK (cantidad > 0),

    CONSTRAINT fk_recurso_mov
    FOREIGN KEY (id_recurso)
    REFERENCES recurso(id_recurso)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

    CONSTRAINT fk_bodega
    FOREIGN KEY (id_bodega)
    REFERENCES bodega(id_bodega)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- =========================
-- TABLA ENTREGA
-- =========================
CREATE TABLE entrega (
    id_entrega INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_efectiva DATE NOT NULL,
    id_familia INT,
    coordenadas VARCHAR(100),
    firma_digital TEXT,

    CONSTRAINT fk_familia
    FOREIGN KEY (id_familia)
    REFERENCES familia(id_familia)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- =========================
-- TABLA DETALLE_ENTREGA
-- =========================
CREATE TABLE detalle_entrega (
    id_detalle INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_entrega INT,
    id_recurso INT,
    cantidad INT,

    CHECK (cantidad > 0),

    CONSTRAINT fk_entrega
    FOREIGN KEY (id_entrega)
    REFERENCES entrega(id_entrega)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_recurso_detalle
    FOREIGN KEY (id_recurso)
    REFERENCES recurso(id_recurso)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

-- =========================
-- TABLA USUARIO
-- =========================
CREATE TABLE usuario (
    id_usuario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(50),

    CHECK (rol IN ('ADMIN', 'ONG', 'VOLUNTARIO'))
);

-- =========================
-- TABLA AUDIT_LOG
-- =========================
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

-- ==========================================
-- INSERCIÓN DE DATOS DE PRUEBA
-- ==========================================

-- ZONAS
INSERT INTO zona (nombre, nivel_riesgo_tipo) VALUES
('Zona Norte', 'alto'),
('Zona Sur', 'medio'),
('Zona Centro', 'bajo'),
('Zona Rural Este', 'crítico'),
('Zona Rural Oeste', 'medio');

-- UBICACIONES
INSERT INTO ubicacion (direccion, id_zona) VALUES
('Calle 10 # 5-20', 1),
('Carrera 3 # 8-15', 2),
('Avenida Central # 1-01', 3),
('Vereda El Roble', 4),
('Vereda La Palma', 5),
('Calle 22 # 7-40', 1),
('Barrio El Carmen', 2);

-- REFUGIOS
-- (se insertan al final, luego de crear la tabla refugios)

-- PERSONAS
INSERT INTO persona (
    nombre,
    edad,
    es_nino,
    es_anciano,
    es_embarazada
) VALUES
('Carlos Pérez',      35, FALSE, FALSE, FALSE),
('María López',       28, FALSE, FALSE, TRUE),
('José Martínez',     70, FALSE, TRUE,  FALSE),
('Ana Gómez',         8,  TRUE,  FALSE, FALSE),
('Luis Rodríguez',    45, FALSE, FALSE, FALSE),
('Carmen Torres',     32, FALSE, FALSE, FALSE),
('Pedro Sánchez',     60, FALSE, FALSE, FALSE),
('Rosa Jiménez',      25, FALSE, FALSE, TRUE),
('Juan Castro',       50, FALSE, FALSE, FALSE),
('Elena Vargas',      5,  TRUE,  FALSE, FALSE),
('Roberto Silva',     40, FALSE, FALSE, FALSE),
('Lucía Morales',     72, FALSE, TRUE,  FALSE);

-- FAMILIAS
INSERT INTO familia (id_representante) VALUES
(1),
(2),
(5),
(6),
(9),
(11);

-- ASIGNACIÓN A REFUGIOS
INSERT INTO familia_refugio (
    id_familia,
    id_refugio,
    fecha_ingreso
) VALUES
(1, 1, '2025-01-10'),
(2, 1, '2025-01-11'),
(3, 2, '2025-01-12'),
(4, 2, '2025-01-13');

-- ORÍGENES DE RECURSOS
INSERT INTO origen_recurso (nombre, tipo) VALUES
('Alcaldía de Montería',   'ALCALDIA'),
('Gobernación de Córdoba', 'GOBERNACION'),
('Empresa Postobón',       'EMPRESA'),
('Ciudadanos voluntarios', 'CIUDADANO'),
('Grupo Nutresa',          'EMPRESA');

-- RECURSOS
INSERT INTO recurso (
    nombre,
    peso_unitario_kg,
    id_origen
) VALUES
('Arroz x 5kg',       5.00, 1),
('Aceite x 1L',       1.00, 1),
('Lentejas x 1kg',    1.00, 2),
('Colchoneta',        3.50, 2),
('Sábanas (par)',     1.20, 3),
('Agua potable x 5L', 5.00, 4),
('Frijoles x 1kg',    1.00, 5),
('Atún en lata',      0.18, 3),
('Sal x 1kg',         1.00, 1),
('Azúcar x 1kg',      1.00, 5);

-- BODEGAS
INSERT INTO bodega (
    nombre,
    capacidad_max_kg,
    zona_id
) VALUES
('Bodega Central Montería', 20000, 1),
('Bodega Auxiliar Norte',   8000, 2);

-- MOVIMIENTOS INVENTARIO
INSERT INTO movimiento_inventario (
    tipo,
    cantidad,
    id_recurso,
    id_bodega
) VALUES
('ENTRADA', 500, 1, 1),
('ENTRADA', 300, 2, 1),
('ENTRADA', 400, 3, 1),
('ENTRADA', 150, 4, 1),
('ENTRADA', 200, 5, 1),
('ENTRADA', 600, 6, 2),
('ENTRADA', 350, 7, 1),
('ENTRADA', 800, 8, 2),
('ENTRADA', 450, 9, 1),
('ENTRADA', 400, 10, 1),
('SALIDA', 50, 1, 1),
('SALIDA', 30, 2, 1),
('SALIDA', 20, 4, 1);

-- ENTREGAS
INSERT INTO entrega (
    fecha_efectiva,
    id_familia,
    coordenadas,
    firma_digital
) VALUES
('2025-01-15', 1, '8.7479,-75.8814', 'FIRMA_FAM1_001'),
('2025-01-15', 2, '8.7490,-75.8820', 'FIRMA_FAM2_001'),
('2025-01-16', 3, '8.7510,-75.8800', 'FIRMA_FAM3_001'),
('2025-01-17', 1, '8.7479,-75.8814', 'FIRMA_FAM1_002'),
('2025-01-18', 4, '8.7530,-75.8790', 'FIRMA_FAM4_001'),
('2025-01-18', 5, '8.7550,-75.8770', 'FIRMA_FAM5_001'),
('2025-01-19', 2, '8.7490,-75.8820', 'FIRMA_FAM2_002'),
('2025-01-20', 6, '8.7560,-75.8760', 'FIRMA_FAM6_001');

-- DETALLE ENTREGAS
INSERT INTO detalle_entrega (
    id_entrega,
    id_recurso,
    cantidad
) VALUES
(1, 1, 2),
(1, 2, 1),
(1, 6, 2),
(1, 8, 4),

(2, 1, 2),
(2, 3, 1),
(2, 4, 1),
(2, 5, 1),

(3, 1, 1),
(3, 7, 2),
(3, 9, 1),
(3, 10, 1),

(4, 6, 3),
(4, 8, 6),
(4, 2, 1),

(5, 1, 2),
(5, 4, 1),
(5, 6, 2),

(6, 1, 2),
(6, 2, 1),
(6, 7, 2),

(7, 6, 2),
(7, 8, 4),
(7, 10, 1),

(8, 1, 1),
(8, 3, 2),
(8, 9, 1);

-- ==========================================
-- TABLA USUARIO (REFACTORIZADO - Sin redundancia)
-- ==========================================
-- Reemplazar tabla usuario anterior si existe
DROP TABLE IF EXISTS usuario CASCADE;

CREATE TABLE usuario (
    id_usuario INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    correo VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'REGISTRADOR_DONACIONES',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (rol IN ('ADMIN', 'CENSADOR', 'OPERADOR_ENTREGAS', 'COORDINADOR_LOGISTICA', 'FUNCIONARIO_CONTROL', 'REGISTRADOR_DONACIONES'))
);

-- Crear índices
CREATE INDEX idx_usuario_correo ON usuario(correo);
CREATE INDEX idx_usuario_activo ON usuario(activo);
CREATE INDEX idx_usuario_rol ON usuario(rol);

-- USUARIOS DE PRUEBA
-- Contraseña: Admin123 (hasheada con bcrypt)
INSERT INTO usuario (
    nombre_completo,
    correo,
    password_hash,
    rol,
    activo
) VALUES
(
    'Administrador Sistema',
    'admin@sgah.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq',
    'ADMIN',
    TRUE
),
(
    'Coordinador Logística',
    'coordinador@sgah.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq',
    'COORDINADOR_LOGISTICA',
    TRUE
),
(
    'Operador de Entregas',
    'operador@sgah.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq',
    'OPERADOR_ENTREGAS',
    TRUE
),
(
    'Registrador de Donaciones',
    'registrador@sgah.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq',
    'REGISTRADOR_DONACIONES',
    TRUE
);
-- =========================
-- TABLA REFUGIOS (HU-10)
-- =========================
CREATE TABLE IF NOT EXISTS refugios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion_textual TEXT,
    latitud DECIMAL(10, 8) NOT NULL,
    longitud DECIMAL(11, 8) NOT NULL,
    capacidad_maxima_personas INTEGER NOT NULL CHECK (capacidad_maxima_personas > 0),
    ocupacion_actual INTEGER DEFAULT 0 CHECK (ocupacion_actual >= 0),
    zona_id INTEGER REFERENCES zona(id_zona) ON DELETE SET NULL ON UPDATE CASCADE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índice si no existe
CREATE INDEX IF NOT EXISTS idx_refugios_zona ON refugios(zona_id);

INSERT INTO refugios (id, nombre, ubicacion_textual, latitud, longitud, capacidad_maxima_personas, ocupacion_actual, zona_id)
VALUES
    (1, 'Refugio Coliseo Norte', 'Calle 10 # 5-20', 8.75000000, -75.88000000, 200, 120, 1),
    (2, 'Refugio Escuela Sur', 'Carrera 3 # 8-15', 8.74000000, -75.89000000, 150, 90, 2),
    (3, 'Refugio Centro Vida', 'Avenida Central # 1-01', 8.76000000, -75.87000000, 100, 40, 3)
ON CONFLICT (id) DO NOTHING;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_fr_refugio'
    ) THEN
        ALTER TABLE familia_refugio
            ADD CONSTRAINT fk_fr_refugio
            FOREIGN KEY (id_refugio)
            REFERENCES refugios(id)
            ON DELETE CASCADE;
    END IF;
END $$;
