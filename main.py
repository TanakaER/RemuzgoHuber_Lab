"""Punto de entrada: simulador de scheduling cloud.

Ejemplos:
    python main.py                              # todos los escenarios
    python main.py -e evaluacion --detalle      # caso de la guía de evaluación, con tablas por VM
    python main.py -e laboratorio -a fcfs minmin genetico
    python main.py --archivo-trabajos data/trabajos_ejemplo.csv --archivo-vms data/vms_ejemplo.csv
"""
from __future__ import annotations

import argparse
import sys

from cloudsched import schedulers, scenarios
from cloudsched.reporting import (export_csv, print_details, print_scenario_header, print_summary)
from cloudsched.runner import run_scenario

ESCENARIOS = ["evaluacion", "hetero", "laboratorio", "todos"]


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Simulador de scheduling y asignación de recursos en la nube.")
    p.add_argument("-e", "--escenario", choices=ESCENARIOS, default="todos", help="escenario (por defecto: todos)")
    p.add_argument("-a", "--algoritmos", nargs="+", metavar="ALG",
                   help=f"algoritmos a comparar: {', '.join(schedulers.available())}")
    p.add_argument("--semilla", type=int, default=42, help="semilla del dataset del laboratorio y del GA")
    p.add_argument("--num-tareas", type=int, default=50, help="tareas del laboratorio (por defecto 50)")
    p.add_argument("--num-vms", type=int, default=5, help="VM del laboratorio (por defecto 5)")
    p.add_argument("--archivo-trabajos", help="CSV propio de trabajos (columnas: id,duracion)")
    p.add_argument("--archivo-vms", help="CSV propio de VM (columnas: id,vcpu,ram_gb[,velocidad][,costo_hora])")
    p.add_argument("-o", "--salida", default="resultados", help="carpeta de salida (por defecto: resultados)")
    p.add_argument("--detalle", action="store_true", help="muestra la asignación por VM de cada algoritmo")
    p.add_argument("--sin-graficos", action="store_true", help="no genera imágenes PNG")
    p.add_argument("--mostrar", action="store_true", help="abre además las gráficas en ventanas")
    p.add_argument("--listar", action="store_true", help="lista algoritmos y escenarios y termina")
    return p.parse_args(argv)


def build_scenarios(args):
    if args.archivo_trabajos or args.archivo_vms:
        if not (args.archivo_trabajos and args.archivo_vms):
            raise ValueError("Para datos propios indique --archivo-trabajos y --archivo-vms.")
        return [scenarios.personalizado(args.archivo_trabajos, args.archivo_vms)]
    chosen = ["evaluacion", "hetero", "laboratorio"] if args.escenario == "todos" else [args.escenario]
    built = []
    for key in chosen:
        if key == "evaluacion":
            built.append(scenarios.evaluacion())
        elif key == "hetero":
            built.append(scenarios.hetero())
        else:
            built.append(scenarios.laboratorio(args.semilla, args.num_tareas, args.num_vms))
    return built


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):  # evita errores de acentos en consolas Windows
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    args = parse_args(argv)
    if args.listar:
        print("Algoritmos:")
        for key, cls in schedulers.REGISTRY.items():
            print(f"  {key:11s} {cls.name}")
        print("Escenarios:", ", ".join(ESCENARIOS[:-1]), "(o 'todos')")
        return 0
    try:
        plots = None
        if not args.sin_graficos:
            from cloudsched import plots
            plots.use_backend(args.mostrar)
        generated = []
        for sc in build_scenarios(args):
            algos = args.algoritmos
            if algos and sc.key != "evaluacion":
                algos = [a for a in algos if a.lower() != "manual"]  # 'manual' solo existe en 'evaluacion'
            if algos and sc.key == "laboratorio":
                algos = [a for a in algos if a.lower() != "optimo"]  # 50 tareas: búsqueda exhaustiva inviable
            results = run_scenario(sc, algos, seed=args.semilla)
            print_scenario_header(sc)
            print_summary(sc, results)
            if args.detalle:
                print_details(sc, results)
            generated += export_csv(sc, results, args.salida)
            if plots:
                generated += plots.make_all(sc, results, args.salida, args.mostrar)
    except ValueError as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 2
    print(f"\nListo. Se generaron {len(generated)} archivos en la carpeta '{args.salida}/' (CSV y PNG).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
