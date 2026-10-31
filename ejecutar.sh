#!/usr/bin/env bash
# Ejecuta el proyecto en macOS / Linux. Uso:  bash ejecutar.sh [opciones de main.py]
set -e
cd "$(dirname "$0")"
PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
if [ ! -x ".venv/bin/python" ]; then
  echo "Creando entorno virtual..."
  "$PY" -m venv .venv
fi
.venv/bin/python -m pip install --quiet --disable-pip-version-check -r requirements.txt
.venv/bin/python -m unittest discover tests
.venv/bin/python main.py --detalle "$@"
echo
echo 'Resultados guardados en la carpeta "resultados".'
