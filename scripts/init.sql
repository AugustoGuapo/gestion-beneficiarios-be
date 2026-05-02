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
CREATE TABLE zona (
    id_zona INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
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
-- TABLA ALBERGUE
-- =========================
CREATE TABLE albergue (
    id_albergue INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    capacidad INT,
    id_ubicacion INT,

    CONSTRAINT fk_ubicacion_albergue
    FOREIGN KEY (id_ubicacion)
    REFERENCES ubicacion(id_ubicacion)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- =========================
-- TABLA FAMILIA_ALBERGUE
-- =========================
CREATE TABLE familia_albergue (
    id_familia INT,
    id_albergue INT,
    fecha_ingreso DATE,

    PRIMARY KEY (id_familia, id_albergue),

    CONSTRAINT fk_fa_familia
    FOREIGN KEY (id_familia)
    REFERENCES familia(id_familia)
    ON DELETE CASCADE,

    CONSTRAINT fk_fa_albergue
    FOREIGN KEY (id_albergue)
    REFERENCES albergue(id_albergue)
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
-- TABLA BODEGA
-- =========================
CREATE TABLE bodega (
    id_bodega INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100),
    capacidad_max_kg DECIMAL(10,2),

    CHECK (capacidad_max_kg <= 20000)
);

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

-- ==========================================
-- INSERCIÓN DE DATOS DE PRUEBA
-- ==========================================

-- ZONAS
INSERT INTO zona (nombre) VALUES
('Zona Norte'),
('Zona Sur'),
('Zona Centro'),
('Zona Rural Este'),
('Zona Rural Oeste');

-- UBICACIONES
INSERT INTO ubicacion (direccion, id_zona) VALUES
('Calle 10 # 5-20', 1),
('Carrera 3 # 8-15', 2),
('Avenida Central # 1-01', 3),
('Vereda El Roble', 4),
('Vereda La Palma', 5),
('Calle 22 # 7-40', 1),
('Barrio El Carmen', 2);

-- ALBERGUES
INSERT INTO albergue (nombre, capacidad, id_ubicacion) VALUES
('Albergue Coliseo Norte', 200, 1),
('Albergue Escuela Sur',   150, 2),
('Albergue Centro Vida',   100, 3);

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

-- ASIGNACIÓN A ALBERGUES
INSERT INTO familia_albergue (
    id_familia,
    id_albergue,
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
    capacidad_max_kg
) VALUES
('Bodega Central Montería', 20000),
('Bodega Auxiliar Norte',   8000);

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

-- USUARIOS
INSERT INTO usuario (
    nombre,
    rol
) VALUES
('Admin Principal', 'ADMIN'),
('ONG Cruz Roja', 'ONG'),
('Voluntario Juan', 'VOLUNTARIO'),
('Voluntario Ana', 'VOLUNTARIO');