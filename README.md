# Simulador de Scheduling en la Nube (Python)

Prototipo del laboratorio **"Scheduling y asignación eficiente de recursos en la nube"** (curso Servicios Cloud).
Simula cómo un *scheduler* reparte trabajos entre máquinas virtuales (VM) y compara algoritmos con métricas
reales: **makespan, tiempo de espera, retorno, throughput, utilización, balance de carga y costo**.

```
Jobs  ──►  Scheduler (algoritmo)  ──►  Recursos cloud (VM)  ──►  Simulador  ──►  Métricas  ──►  CSV + gráficos
```

Algoritmos incluidos: **FCFS/FIFO, Round Robin, SJF, Min-Min, Max-Min, balanceo por carga/capacidad (LPT),
algoritmo genético (GA)** y **óptimo por búsqueda exhaustiva** (solo instancias pequeñas), más una opción
**manual** para probar tu propia asignación.

---

## 1. Requisitos

* **Python 3.9 o superior** (probado con 3.12). Comprueba con `python --version` (Windows: `py --version`).
  Si no lo tienes: <https://www.python.org/downloads/> → durante la instalación marca **"Add python.exe to PATH"**.
* Conexión a Internet **solo la primera vez** (para instalar `matplotlib`).
* No requiere GPU, Docker ni cuentas cloud.

## 2. Ejecución rápida (recomendada)

| Sistema | Qué hacer |
|---|---|
| **Windows** | Descomprime la carpeta y haz **doble clic en `ejecutar_windows.bat`** |
| **macOS / Linux** | En la terminal, dentro de la carpeta: `bash ejecutar.sh` |

El script crea un entorno virtual (`.venv`), instala las dependencias, corre las pruebas automáticas y
ejecuta **todos los escenarios**. Los resultados quedan en la carpeta `resultados/`.

## 3. Ejecución manual paso a paso

Abre una terminal **dentro de la carpeta del proyecto** (en Windows: clic derecho → *Abrir en Terminal*).

### Windows (PowerShell o CMD)
```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```
> Se usa `.venv\Scripts\python` directamente, así **no necesitas activar** el entorno (evita el error de
> "ejecución de scripts deshabilitada" de PowerShell).

### macOS / Linux
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

## 4. Comandos útiles

(En Windows reemplaza `python` por `.venv\Scripts\python`; en macOS/Linux por `.venv/bin/python`.)

```bash
python main.py                                  # los 3 escenarios
python main.py -e evaluacion --detalle          # caso de la guía de evaluación, con tabla por VM
python main.py -e hetero                        # Pregunta 3: VM1=8 vCPU, VM2=VM3=2 vCPU
python main.py -e laboratorio                   # 50 tareas, 5 VM heterogéneas (FCFS vs Min-Min, etc.)
python main.py -e laboratorio -a fcfs minmin    # solo algunos algoritmos
python main.py -e laboratorio --semilla 7 --num-tareas 80 --num-vms 6
python main.py --archivo-trabajos data/trabajos_ejemplo.csv --archivo-vms data/vms_ejemplo.csv
python main.py --sin-graficos                   # solo tablas y CSV
python main.py --mostrar                        # además abre las gráficas en ventanas
python main.py --listar                         # lista algoritmos y escenarios
python -m unittest discover tests -v            # pruebas automáticas
```

Claves de algoritmos: `fcfs`, `rr`, `sjf`, `minmin`, `maxmin`, `balanceado`, `genetico`, `optimo`, `manual`.
(`manual` y `optimo` solo aplican a los escenarios con 8 trabajos.)

## 5. Qué se genera en `resultados/`

| Archivo | Contenido |
|---|---|
| `resumen_<escenario>.csv` | Métricas de cada algoritmo (se abre en Excel) |
| `asignaciones_<escenario>.csv` | Trabajo, VM, inicio, fin y espera de cada tarea por algoritmo |
| `gantt_<escenario>_<alg>.png` | Diagrama de Gantt por algoritmo |
| `comparacion_<escenario>.png` | Makespan, espera media y utilización (mejor en verde) |
| `utilizacion_<escenario>.png` | Utilización de cada VM por algoritmo |
| `convergencia_laboratorio.png` | Curva de convergencia del algoritmo genético |

## 6. Resultados esperados (para verificar que todo funciona)

Escenario `evaluacion` (8 trabajos, 3 VM de 4 vCPU), tiempos en minutos:

| Estrategia | Carga VM1 / VM2 / VM3 | Makespan |
|---|---|---|
| Round Robin | 17 / 21 / 14 | **21** |
| SJF (VM que se libera primero) | 18 / 22 / 12 | **22** |
| Propuesta optimizada | 18 / 17 / 17 | **18** |
| Óptimo (exhaustivo) | 18 / 17 / 17 | **18** (= cota inferior ⌈52/3⌉) |

En `laboratorio` (semilla 42) deberías ver, entre otros: FCFS = 156 min, Min-Min = 129.5 min y GA = 118.5 min.

## 7. Arquitectura del código

```
cloud_scheduling_lab/
├── main.py                     # interfaz de línea de comandos
├── ejecutar_windows.bat        # ejecución con doble clic (Windows)
├── ejecutar.sh                 # ejecución en macOS/Linux
├── requirements.txt            # matplotlib
├── data/                       # CSV de ejemplo (trabajos y VM)
├── tests/test_scheduling.py    # pruebas que reproducen la guía de evaluación
└── cloudsched/
    ├── models.py               # Job, VM, Entry, Schedule
    ├── scenarios.py            # evaluacion, hetero, laboratorio, personalizado (CSV)
    ├── schedulers/             # UN archivo por algoritmo (fcfs, round_robin, sjf, min_min, ...)
    ├── simulator.py            # convierte el plan de cada VM en línea de tiempo (valida el plan)
    ├── metrics.py              # makespan, espera, retorno, throughput, utilización, CV, costo
    ├── runner.py               # ejecuta escenario × algoritmos
    ├── reporting.py            # tablas por consola y CSV
    └── plots.py                # Gantt, comparación, utilización, convergencia
```

**Supuestos del modelo** (los de la guía): todos los trabajos llegan en t = 0; cada VM ejecuta un trabajo a la vez;
sin costo de cambio de contexto; sin interrupciones. Velocidad de una VM = vCPU / 4 (escalado lineal respecto a una
VM de 4 vCPU). Costo referencial = VM encendidas (0.05 USD por vCPU-hora) hasta que termina el lote.
Round Robin se implementa como **reparto cíclico entre VM**, tal como lo plantea la guía de evaluación.

## 8. Agregar tu propio algoritmo

1. Crea `cloudsched/schedulers/mi_algoritmo.py` con una clase que herede de `Scheduler` e implemente
   `schedule(jobs, vms)` devolviendo `{id_vm: [trabajos en orden]}`.
2. Regístrala en la tupla de `cloudsched/schedulers/__init__.py`.
3. Ejecuta `python main.py -a mi_clave`.

## 9. Solución de problemas

| Problema | Solución |
|---|---|
| `python` no se reconoce (Windows) | Usa `py` en lugar de `python`, o reinstala Python marcando *Add to PATH*. |
| PowerShell: "la ejecución de scripts está deshabilitada" | No actives el entorno; usa `.venv\Scripts\python ...` como en la sección 3. |
| `No module named matplotlib` | Falta instalar: `.venv\Scripts\python -m pip install -r requirements.txt`. |
| Error de `pip` por red/proxy | Verifica tu conexión; en redes institucionales prueba con datos móviles. |
| `venv` falla en Linux (Ubuntu/Debian) | `sudo apt install python3-venv` |
| No se ven acentos en consola | Usa Windows Terminal o abre los CSV con Excel (ya van en UTF-8 con BOM). |
| Quiero empezar de cero | Borra las carpetas `.venv` y `resultados` y vuelve a ejecutar. |
