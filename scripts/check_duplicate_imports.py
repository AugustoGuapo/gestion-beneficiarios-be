#!/usr/bin/env python3
"""
Script para detectar imports duplicados en archivos Python del proyecto.
Escanea recursivamente, detecta líneas de import idénticas dentro de cada archivo.
Uso: python scripts/check_duplicate_imports.py
"""

import os
import re
import sys
from collections import defaultdict

# Directorios a escanear (relativos al directorio raíz del proyecto)
SCAN_DIRS = ["app", "tests", "scripts"]

# Extensiones a revisar
EXTENSION = ".py"

# Directorios a ignorar
EXCLUDE_DIRS = {"__pycache__", "venv", ".venv", ".env", "env", "node_modules", ".mypy_cache", ".pytest_cache"}

def find_python_files(root_dir):
    """Encuentra todos los archivos .py en los directorios especificados."""
    py_files = []
    for scan_dir in SCAN_DIRS:
        scan_path = os.path.join(root_dir, scan_dir)
        if not os.path.isdir(scan_path):
            continue
        for dirpath, dirnames, filenames in os.walk(scan_path):
            # Excluir directorios no deseados
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for filename in filenames:
                if filename.endswith(EXTENSION):
                    py_files.append(os.path.join(dirpath, filename))
    return py_files


def normalize_import(line):
    """Normaliza una línea de import para detectar duplicados semánticos.
    Elimina espacios extra y normaliza comillas simples/duales (en caso de que las haya)."""
    # Eliminar espacios al inicio/final
    line = line.strip()
    # Colapsar múltiples espacios internos a uno solo
    line = re.sub(r'\s+', ' ', line)
    return line


def is_import_line(line):
    """Determina si una línea es una línea de import/from import."""
    stripped = line.strip()
    return stripped.startswith("import ") or stripped.startswith("from ")


def detect_duplicate_imports(filepath):
    """Analiza un archivo y devuelve una lista de imports duplicados encontrados.
    Cada elemento es un dict con: 'line_number', 'text', 'duplicates'.
    """
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # Mapa: import_normalizado -> lista de números de línea
    import_map = defaultdict(list)

    for i, line in enumerate(lines, start=1):
        if is_import_line(line):
            normalized = normalize_import(line)
            import_map[normalized].append(i)

    # Filtrar solo los que tienen duplicados
    duplicates = []
    for normalized, line_numbers in import_map.items():
        if len(line_numbers) > 1:
            duplicates.append({
                "text": normalized,
                "lines": line_numbers,
                "count": len(line_numbers),
            })

    return duplicates


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    py_files = find_python_files(root_dir)

    if not py_files:
        print("❌ No se encontraron archivos .py para escanear.")
        print(f"   Directorios buscados: {', '.join(SCAN_DIRS)}")
        sys.exit(1)

    print(f"🔍 Escaneando {len(py_files)} archivos Python en busca de imports duplicados...\n")

    total_duplicates = 0
    files_with_duplicates = 0

    for filepath in sorted(py_files):
        rel_path = os.path.relpath(filepath, root_dir)
        duplicates = detect_duplicate_imports(filepath)

        if duplicates:
            files_with_duplicates += 1
            print(f"📄 {rel_path}:")
            for dup in duplicates:
                total_duplicates += dup["count"]
                lines_str = ", ".join(map(str, dup["lines"]))
                print(f"   ⚠️  Líneas [{lines_str}] — {dup['count']} veces:")
                print(f"       {dup['text']}")
            print()

    if total_duplicates == 0:
        print("✅ No se encontraron imports duplicados. ¡Todo limpio!")
    else:
        print(f"📊 Resumen:")
        print(f"   - Archivos con duplicados: {files_with_duplicates}")
        # Cada duplicado reporta count>1, pero el número real de líneas redundantes es (count - 1) por grupo
        redundant = sum(d["count"] - 1 for filepath in py_files for d in detect_duplicate_imports(filepath))
        print(f"   - Líneas redundantes (que podrían eliminarse): {redundant}")
        print()
        print("💡 Revisa los archivos listados arriba y elimina las líneas de import duplicadas.")


if __name__ == "__main__":
    main()
