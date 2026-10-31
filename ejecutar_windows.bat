@echo off
REM Ejecuta el proyecto con un doble clic (Windows). Crea el entorno virtual la primera vez.
cd /d "%~dp0"
set "PYCMD="
py -3 --version >nul 2>nul
if not errorlevel 1 set "PYCMD=py -3"
if not defined PYCMD (
  python --version >nul 2>nul
  if not errorlevel 1 set "PYCMD=python"
)
if not defined PYCMD (
  echo No se encontro Python. Instalelo desde https://www.python.org/downloads/ marcando "Add python.exe to PATH".
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno virtual...
  %PYCMD% -m venv .venv
  if errorlevel 1 ( echo Error creando el entorno virtual. & pause & exit /b 1 )
)
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 ( echo Error instalando dependencias. Revise su conexion a Internet. & pause & exit /b 1 )
".venv\Scripts\python.exe" -m unittest discover tests
".venv\Scripts\python.exe" main.py --detalle %*
echo.
echo Resultados guardados en la carpeta "resultados".
pause
