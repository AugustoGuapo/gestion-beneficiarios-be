-- MIGRACIÓN: Refactorizar tabla usuario - Eliminar campo redundante 'estado'
-- Mantener únicamente 'activo' como booleano
-- Ejecutar este script si la tabla usuario existe con campos redundantes

BEGIN TRANSACTION;

-- Paso 1: Crear tabla temporal con estructura refactorizada
CREATE TABLE usuario_new (
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

-- Paso 2: Copiar datos existentes y convertir 'estado' a 'activo'
INSERT INTO usuario_new (id_usuario, nombre_completo, correo, password_hash, rol, activo, fecha_creacion, fecha_actualizacion)
SELECT
    id_usuario,
    nombre_completo,
    correo,
    password_hash,
    rol,
    CASE
        WHEN estado = 'ACTIVO' OR estado IS NULL THEN TRUE
        WHEN estado = 'INACTIVO' THEN FALSE
        ELSE activo
    END as activo,
    fecha_creacion,
    fecha_actualizacion
FROM usuario;

-- Paso 3: Eliminar tabla anterior y renombrar nueva
DROP TABLE usuario CASCADE;
ALTER TABLE usuario_new RENAME TO usuario;

-- Paso 4: Recrear índices
CREATE INDEX idx_usuario_correo ON usuario(correo);
CREATE INDEX idx_usuario_activo ON usuario(activo);
CREATE INDEX idx_usuario_rol ON usuario(rol);

COMMIT;

-- VERIFICACIÓN
SELECT
    COUNT(*) as total_usuarios,
    COUNT(CASE WHEN activo THEN 1 END) as usuarios_activos,
    COUNT(CASE WHEN NOT activo THEN 1 END) as usuarios_inactivos
FROM usuario;
