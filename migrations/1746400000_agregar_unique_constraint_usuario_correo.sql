-- MIGRACIÓN: Añadir constraint única en usuario(correo)
-- Este script: 
-- 1) Verifica si la constraint ya existe (no hace nada si ya está)
-- 2) Comprueba si hay correos duplicados y aborta si existen
-- 3) Añade la constraint UNIQUE sobre `correo`

DO $$
BEGIN
    -- Si la constraint ya existe, salir sin cambios
    IF EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_usuario_correo'
    ) THEN
        RAISE NOTICE 'Constraint uq_usuario_correo ya existe. No se realizan cambios.';
        RETURN;
    END IF;

    -- Verificar duplicados
    IF EXISTS (
        SELECT correo FROM usuario GROUP BY correo HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'Existen correos duplicados en la tabla usuario. Resuelva duplicados antes de aplicar esta migración.';
    END IF;

    -- Añadir constraint única
    ALTER TABLE usuario ADD CONSTRAINT uq_usuario_correo UNIQUE (correo);
    RAISE NOTICE 'Constraint uq_usuario_correo creada correctamente.';
END
$$;
