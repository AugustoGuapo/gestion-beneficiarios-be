-- =========================
-- V003: Crear tabla de configuración de puntaje
-- HU-08: Calcular puntaje de prioridad
-- =========================

CREATE TABLE IF NOT EXISTS configuracion_puntaje (
    id_config INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    clave VARCHAR(50) UNIQUE NOT NULL,
    valor FLOAT NOT NULL,
    descripcion VARCHAR(200)
);

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
