# Migraciones de Base de Datos

Este directorio contiene todas las migraciones de base de datos del proyecto.

## Formato de nombre

Cada archivo de migración sigue el formato:

```
{EPOCH}_{migration_name_snake_case}.sql
```

Ejemplo:
```
1744567890_agregar_campo_telefono_a_persona.sql
```

## Cómo crear una migración

```bash
make migration name="Descripción del cambio"
# o directamente:
bash scripts/create_migration.sh "Descripción del cambio"
```

## Cómo aplicar migraciones

```bash
make migrate
# o directamente:
bash scripts/apply_migrations.sh
```

## Convenciones

1. **SIEMPRE** crear migraciones con el script (`create_migration.sh`)
2. **NUNCA** modificar una migración que ya fue aplicada a la base de datos compartida
3. Las migraciones deben ser **idempotentes** cuando sea posible (usar `IF NOT EXISTS`, etc.)
4. Incluir el **ROLLBACK** como comentario al final del archivo
5. Una migración = un cambio atómico (no mezclar cambios no relacionados)