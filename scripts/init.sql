-- =========================
-- SCRIPT DE INICIALIZACIÓN
-- =========================
-- Este script se ejecuta solo al crear una base de datos nueva
-- (volumen PostgreSQL vacío). Contiene el esquema final + datos semilla.
--
-- Las migraciones incrementales están en migrations/*.sql y se aplican
-- con `make migrate` sobre bases existentes.
--
-- IMPORTANTE: Este archivo NO debe contener ALTER TABLE para agregar
-- columnas. Eso es responsabilidad de las migraciones.
-- =========================

-- =========================
-- TIPO ENUM
-- =========================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'nivel_riesgo_tipo') THEN
        CREATE TYPE nivel_riesgo_tipo AS ENUM ('bajo', 'medio', 'alto', 'crítico');
    END IF;
END
$$;

-- =========================
-- TABLA PERSONA (versión final: HU-04/05)
-- =========================
CREATE TABLE IF NOT EXISTS persona (
    id_persona INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    edad INT,
    es_nino BOOLEAN DEFAULT FALSE,
    es_anciano BOOLEAN DEFAULT FALSE,
    es_embarazada BOOLEAN DEFAULT FALSE,
    id_familia INT,
    tipo_documento VARCHAR(20),
    numero_documento VARCHAR(20),
    tiene_discapacidad BOOLEAN DEFAULT FALSE,
    tiene_enfermedad_cronica BOOLEAN DEFAULT FALSE,
    es_cabeza_familia BOOLEAN DEFAULT FALSE,
    CHECK (edad >= 0)
);

-- =========================
-- TABLA FAMILIA (versión final: HU-04)
-- =========================
CREATE TABLE IF NOT EXISTS familia (
    id_familia INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_representante INT UNIQUE,
    codigo_familia VARCHAR(15) UNIQUE NOT NULL,
    acepta_privacidad BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    puntaje_prioridad FLOAT DEFAULT 0.0,

    CONSTRAINT fk_representante
    FOREIGN KEY (id_representante)
    REFERENCES persona(id_persona)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

-- FK de persona → familia (circular, se agrega después de crear ambas)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'persona'
          AND constraint_name = 'fk_persona_familia'
    ) THEN
        ALTER TABLE persona
            ADD CONSTRAINT fk_persona_familia
            FOREIGN KEY (id_familia) REFERENCES familia(id_familia)
            ON DELETE SET NULL ON UPDATE CASCADE;
    END IF;
END
$$;

-- =========================
-- TABLA ZONA (versión final)
-- =========================
CREATE TABLE IF NOT EXISTS zona (
    id_zona INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nivel_riesgo_tipo nivel_riesgo_tipo NOT NULL
);

-- =========================
-- TABLA UBICACION
-- =========================
CREATE TABLE IF NOT EXISTS ubicacion (
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
-- TABLA REFUGIOS (versión final: HU-10 + HU-24)
-- =========================
CREATE TABLE IF NOT EXISTS refugios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion TEXT NOT NULL,
    latitud DECIMAL(10, 8) NOT NULL,
    longitud DECIMAL(11, 8) NOT NULL,
    capacidad_maxima INTEGER NOT NULL CHECK (capacidad_maxima > 0),
    ocupacion_actual INTEGER NOT NULL DEFAULT 0 CHECK (ocupacion_actual >= 0),
    id_zona INTEGER NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_refugios_zona
    FOREIGN KEY (id_zona)
    REFERENCES zona(id_zona)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

    CONSTRAINT ck_refugios_ocupacion CHECK (ocupacion_actual <= capacidad_maxima)
);

CREATE INDEX IF NOT EXISTS idx_refugios_zona ON refugios(id_zona);

-- =========================
-- TABLA FAMILIA_REFUGIO (versión final: HU-24)
-- =========================
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

CREATE UNIQUE INDEX IF NOT EXISTS uq_familia_refugio_activo
    ON familia_refugio (id_familia)
    WHERE fecha_salida IS NULL;

CREATE INDEX IF NOT EXISTS idx_familia_refugio_refugio
    ON familia_refugio (id_refugio);

CREATE INDEX IF NOT EXISTS idx_familia_refugio_familia_fecha
    ON familia_refugio (id_familia, fecha_ingreso);

-- =========================
-- TABLA ORIGEN_RECURSO
-- =========================
CREATE TABLE IF NOT EXISTS origen_recurso (
    id_origen INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50),

    CHECK (tipo IN ('ALCALDIA', 'GOBERNACION', 'EMPRESA', 'CIUDADANO'))
);

-- =========================
-- TABLA RECURSO (versión final: categoría + unidad_medida + activo + umbral_alerta)
-- =========================
CREATE TABLE IF NOT EXISTS recurso (
    id_recurso INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    peso_unitario_kg DECIMAL(10,2),
    id_origen INT,
    categoria VARCHAR(50) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    umbral_alerta INTEGER,

    CHECK (peso_unitario_kg > 0),
    CHECK (categoria IN ('ALIMENTOS', 'COBIJA', 'COLCHONETA', 'ASEO', 'MEDICAMENTO')),
    CHECK (unidad_medida IN ('KG', 'UNIDAD', 'LITRO')),
    CHECK (umbral_alerta IS NULL OR umbral_alerta >= 1),

    CONSTRAINT fk_origen
    FOREIGN KEY (id_origen)
    REFERENCES origen_recurso(id_origen)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_recurso_nombre_categoria
    ON recurso (nombre, categoria);

-- =========================
-- TABLA BODEGA (versión final: HU-11/13)
-- =========================
CREATE TABLE IF NOT EXISTS bodega (
    id_bodega INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    latitud DECIMAL(10, 8) NOT NULL DEFAULT 8.75000000,
    longitud DECIMAL(11, 8) NOT NULL DEFAULT -75.88000000,
    capacidad_max_kg DECIMAL(10, 2) NOT NULL DEFAULT 20000.00,
    peso_actual_kg DECIMAL(10, 2) DEFAULT 0 CHECK (peso_actual_kg >= 0),
    zona_id INTEGER NOT NULL,

    CONSTRAINT fk_bodega_zona
    FOREIGN KEY (zona_id)
    REFERENCES zona(id_zona)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

    CHECK (capacidad_max_kg > 0)
);

CREATE INDEX IF NOT EXISTS idx_bodega_zona ON bodega(zona_id);

-- =========================
-- TABLA MOVIMIENTO_INVENTARIO
-- =========================
CREATE TABLE IF NOT EXISTS movimiento_inventario (
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
-- TABLA ENTREGA (versión final: HU-22 + HU-12)
-- =========================
CREATE TABLE IF NOT EXISTS entrega (
    id_entrega INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(20),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_efectiva DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'ENTREGADA',
    id_familia INT,
    id_bodega INT NOT NULL,
    coordenadas VARCHAR(100),
    firma_digital TEXT,

    CONSTRAINT fk_entrega_familia
    FOREIGN KEY (id_familia)
    REFERENCES familia(id_familia)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

    CONSTRAINT fk_entrega_bodega
    FOREIGN KEY (id_bodega)
    REFERENCES bodega(id_bodega)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

    CONSTRAINT ck_entrega_estado
    CHECK (estado IN ('PENDIENTE', 'ENTREGADA', 'ANULADA'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_entrega_codigo ON entrega(codigo);
CREATE INDEX IF NOT EXISTS idx_entrega_familia_fecha
    ON entrega(id_familia, fecha_efectiva);

-- =========================
-- TABLA DETALLE_ENTREGA
-- =========================
CREATE TABLE IF NOT EXISTS detalle_entrega (
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
-- TABLA USUARIO (versión final refactorizada: HU-01/02)
-- =========================
CREATE TABLE IF NOT EXISTS usuario (
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

CREATE INDEX IF NOT EXISTS idx_usuario_correo ON usuario(correo);
CREATE INDEX IF NOT EXISTS idx_usuario_activo ON usuario(activo);
CREATE INDEX IF NOT EXISTS idx_usuario_rol ON usuario(rol);

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

-- =========================
-- TABLA INVENTARIO
-- =========================
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

CREATE INDEX IF NOT EXISTS idx_inventario_recurso ON inventario (recurso_id);

-- =========================
-- TABLA DONACION
-- =========================
CREATE TABLE IF NOT EXISTS donacion (
    id_donacion INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    referencia VARCHAR(255),
    fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- TABLA DONACION_RECURSO
-- =========================
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

CREATE INDEX IF NOT EXISTS idx_donrec_donacion ON donacion_recurso (donacion_id);
CREATE INDEX IF NOT EXISTS idx_donrec_recurso ON donacion_recurso (recurso_id);

-- =========================
-- TABLA CONFIGURACION_PUNTAJE (HU-08)
-- =========================
CREATE TABLE IF NOT EXISTS configuracion_puntaje (
    id_config INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave VARCHAR(50) UNIQUE NOT NULL,
    valor FLOAT NOT NULL,
    descripcion VARCHAR(200)
);

-- =========================
-- TABLA PLAN_DISTRIBUCION (HU-21)
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

-- =========================
-- TABLA DETALLE_PLAN_DISTRIBUCION
-- =========================
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

-- =========================
-- TABLA FOCO_SANITARIO (HU-25)
-- =========================
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

-- ==========================================
-- INSERCIÓN DE DATOS DE PRUEBA
-- ==========================================

-- ZONAS
INSERT INTO zona (nombre, nivel_riesgo_tipo) VALUES
('Zona Norte', 'alto'),
('Zona Sur', 'medio'),
('Zona Centro', 'bajo'),
('Zona Rural Este', 'crítico'),
('Zona Rural Oeste', 'medio')
ON CONFLICT DO NOTHING;

-- UBICACIONES
INSERT INTO ubicacion (direccion, id_zona) VALUES
('Calle 10 # 5-20', 1),
('Carrera 3 # 8-15', 2),
('Avenida Central # 1-01', 3),
('Vereda El Roble', 4),
('Vereda La Palma', 5),
('Calle 22 # 7-40', 1),
('Barrio El Carmen', 2)
ON CONFLICT DO NOTHING;

-- REFUGIOS
INSERT INTO refugios (id, nombre, ubicacion, latitud, longitud, capacidad_maxima, ocupacion_actual, id_zona)
VALUES
    (1, 'Refugio Coliseo Norte', 'Calle 10 # 5-20', 8.75000000, -75.88000000, 200, 120, 1),
    (2, 'Refugio Escuela Sur', 'Carrera 3 # 8-15', 8.74000000, -75.89000000, 150, 90, 2),
    (3, 'Refugio Centro Vida', 'Avenida Central # 1-01', 8.76000000, -75.87000000, 100, 40, 3)
ON CONFLICT (id) DO NOTHING;

-- PERSONAS
INSERT INTO persona (
    nombre, edad, es_nino, es_anciano, es_embarazada
) VALUES
('Carlos Pérez',  35, FALSE, FALSE, FALSE),
('María López',   28, FALSE, FALSE, TRUE),
('José Martínez', 70, FALSE, TRUE,  FALSE),
('Ana Gómez',     8,  TRUE,  FALSE, FALSE),
('Luis Rodríguez',45, FALSE, FALSE, FALSE),
('Carmen Torres', 32, FALSE, FALSE, FALSE),
('Pedro Sánchez', 60, FALSE, FALSE, FALSE),
('Rosa Jiménez',  25, FALSE, FALSE, TRUE),
('Juan Castro',   50, FALSE, FALSE, FALSE),
('Elena Vargas',  5,  TRUE,  FALSE, FALSE),
('Roberto Silva', 40, FALSE, FALSE, FALSE),
('Lucía Morales', 72, FALSE, TRUE,  FALSE)
ON CONFLICT DO NOTHING;

-- FAMILIAS (requiere codigo_familia)
INSERT INTO familia (id_representante, codigo_familia) VALUES
(1,  'FAM-001'),
(2,  'FAM-002'),
(5,  'FAM-003'),
(6,  'FAM-004'),
(9,  'FAM-005'),
(11, 'FAM-006')
ON CONFLICT DO NOTHING;

-- ASIGNACIÓN FAMILIA → REFUGIO
INSERT INTO familia_refugio (id_familia, id_refugio, fecha_ingreso) VALUES
(1, 1, '2025-01-10'),
(2, 1, '2025-01-11'),
(3, 2, '2025-01-12'),
(4, 2, '2025-01-13')
ON CONFLICT DO NOTHING;

-- ORÍGENES DE RECURSOS
INSERT INTO origen_recurso (nombre, tipo) VALUES
('Alcaldía de Montería',   'ALCALDIA'),
('Gobernación de Córdoba', 'GOBERNACION'),
('Empresa Postobón',       'EMPRESA'),
('Ciudadanos voluntarios', 'CIUDADANO'),
('Grupo Nutresa',          'EMPRESA')
ON CONFLICT DO NOTHING;

-- RECURSOS
INSERT INTO recurso (nombre, peso_unitario_kg, id_origen, categoria, unidad_medida) VALUES
('Arroz x 5kg',       5.00, 1, 'ALIMENTOS', 'KG'),
('Aceite x 1L',       1.00, 1, 'ALIMENTOS', 'LITRO'),
('Lentejas x 1kg',    1.00, 2, 'ALIMENTOS', 'KG'),
('Colchoneta',        3.50, 2, 'COLCHONETA', 'UNIDAD'),
('Sábanas (par)',     1.20, 3, 'COBIJA', 'UNIDAD'),
('Agua potable x 5L', 5.00, 4, 'ALIMENTOS', 'LITRO'),
('Frijoles x 1kg',    1.00, 5, 'ALIMENTOS', 'KG'),
('Atún en lata',      0.18, 3, 'ALIMENTOS', 'UNIDAD'),
('Sal x 1kg',         1.00, 1, 'ALIMENTOS', 'KG'),
('Azúcar x 1kg',      1.00, 5, 'ALIMENTOS', 'KG')
ON CONFLICT DO NOTHING;

-- BODEGAS
INSERT INTO bodega (nombre, capacidad_max_kg, zona_id) VALUES
('Bodega Central Montería', 20000, 1),
('Bodega Auxiliar Norte',   8000, 2)
ON CONFLICT DO NOTHING;

-- MOVIMIENTOS INVENTARIO
INSERT INTO movimiento_inventario (tipo, cantidad, id_recurso, id_bodega) VALUES
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
('SALIDA', 20, 4, 1)
ON CONFLICT DO NOTHING;

-- ENTREGAS
INSERT INTO entrega (fecha_efectiva, id_familia, id_bodega, coordenadas, firma_digital) VALUES
('2025-01-15', 1, 1, '8.7479,-75.8814', 'FIRMA_FAM1_001'),
('2025-01-15', 2, 1, '8.7490,-75.8820', 'FIRMA_FAM2_001'),
('2025-01-16', 3, 1, '8.7510,-75.8800', 'FIRMA_FAM3_001'),
('2025-01-17', 1, 1, '8.7479,-75.8814', 'FIRMA_FAM1_002'),
('2025-01-18', 4, 1, '8.7530,-75.8790', 'FIRMA_FAM4_001'),
('2025-01-18', 5, 1, '8.7550,-75.8770', 'FIRMA_FAM5_001'),
('2025-01-19', 2, 1, '8.7490,-75.8820', 'FIRMA_FAM2_002'),
('2025-01-20', 6, 2, '8.7560,-75.8760', 'FIRMA_FAM6_001')
ON CONFLICT DO NOTHING;

-- DETALLE ENTREGAS
INSERT INTO detalle_entrega (id_entrega, id_recurso, cantidad) VALUES
(1, 1, 2), (1, 2, 1), (1, 6, 2), (1, 8, 4),
(2, 1, 2), (2, 3, 1), (2, 4, 1), (2, 5, 1),
(3, 1, 1), (3, 7, 2), (3, 9, 1), (3, 10, 1),
(4, 6, 3), (4, 8, 6), (4, 2, 1),
(5, 1, 2), (5, 4, 1), (5, 6, 2),
(6, 1, 2), (6, 2, 1), (6, 7, 2),
(7, 6, 2), (7, 8, 4), (7, 10, 1),
(8, 1, 1), (8, 3, 2), (8, 9, 1)
ON CONFLICT DO NOTHING;

-- CONFIGURACIÓN PUNTAJE (HU-08)
INSERT INTO configuracion_puntaje (clave, valor, descripcion) VALUES
('peso_miembros', 1.0, 'Puntos por cada miembro de la familia'),
('peso_nino', 2.0, 'Puntos por cada niño'),
('peso_anciano', 2.5, 'Puntos por cada anciano'),
('peso_embarazada', 3.0, 'Puntos por cada embarazada'),
('peso_discapacidad', 2.0, 'Puntos por persona con discapacidad'),
('peso_enfermedad', 1.5, 'Puntos por persona con enfermedad crónica'),
('peso_zona', 1.0, 'Factor multiplicador según zona'),
('peso_dias_sin_ayuda', 0.5, 'Puntos por día sin recibir ayuda'),
('tope_dias', 30, 'Máximo de días a considerar')
ON CONFLICT (clave) DO NOTHING;

-- USUARIOS DE PRUEBA
-- Contraseña: Admin123 (hasheada con bcrypt)
INSERT INTO usuario (nombre_completo, correo, password_hash, rol, activo) VALUES
('Administrador Sistema',    'admin@sgah.com',         '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq', 'ADMIN',                    TRUE),
('Coordinador Logística',    'coordinador@sgah.com',    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq', 'COORDINADOR_LOGISTICA',    TRUE),
('Operador de Entregas',     'operador@sgah.com',       '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq', 'OPERADOR_ENTREGAS',        TRUE),
('Registrador de Donaciones','registrador@sgah.com',    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq', 'REGISTRADOR_DONACIONES',   TRUE)
ON CONFLICT (correo) DO NOTHING;
