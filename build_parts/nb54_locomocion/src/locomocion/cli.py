"""Línea de órdenes: python -m locomocion {info,entrenar,evaluar} ..."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .config import cargar_config, a_dict

logger = logging.getLogger("locomocion.cli")


def _configurar_logging(verbosidad: int, fichero: Path | None = None) -> None:
    nivel = {0: logging.WARNING, 1: logging.INFO}.get(verbosidad, logging.DEBUG)
    manejadores: list[logging.Handler] = [logging.StreamHandler()]
    if fichero is not None:
        fichero.parent.mkdir(parents=True, exist_ok=True)
        manejadores.append(logging.FileHandler(fichero, encoding="utf-8"))
    logging.basicConfig(level=nivel, handlers=manejadores, force=True,
                        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s", datefmt="%H:%M:%S")


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="locomocion", description="Entorno de locomoción de Zancudo 3D (NB54).")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="más detalle (-v: INFO, -vv: DEBUG)")
    sub = parser.add_subparsers(dest="orden", required=True)

    comun = argparse.ArgumentParser(add_help=False)          # opciones que comparten varias órdenes
    comun.add_argument("--config", type=Path, help="fichero YAML con cambios sobre la configuración por defecto")
    comun.add_argument("--set", dest="cambios", action="append", default=[], metavar="CLAVE=VALOR",
                       help="cambiar un valor, p. ej. --set simulacion.kp=200 (se puede repetir)")

    sub.add_parser("info", parents=[comun], help="muestra la configuración resultante y comprueba el entorno")

    e = sub.add_parser("entrenar", parents=[comun], help="entrena una política con PPO")
    e.add_argument("--pasos", type=int, default=1_000_000, help="pasos de entorno (por defecto: %(default)s)")
    e.add_argument("--salida", type=Path, required=True, help="carpeta donde guardar el modelo y los registros")
    e.add_argument("--semilla", type=int, default=0)
    e.add_argument("--entornos", type=int, default=16, help="entornos en paralelo (por defecto: %(default)s)")
    e.add_argument("--guardar-cada", type=int, default=200_000)
    e.add_argument("--seguir", action="store_true", help="reanudar el entrenamiento guardado en --salida")

    v = sub.add_parser("evaluar", help="evalúa una política guardada con una orden fija")
    v.add_argument("carpeta", type=Path, help="carpeta de un entrenamiento")
    v.add_argument("--comando", type=float, nargs=3, default=[0.4, 0.0, 0.0], metavar=("VX", "VY", "GIRO"))
    v.add_argument("--episodios", type=int, default=3)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = crear_parser().parse_args(argv)
    fichero_log = args.salida / "entrenamiento.log" if args.orden == "entrenar" else None
    _configurar_logging(args.verbose, fichero_log)

    if args.orden == "info":
        import yaml
        from .entorno import ZancudoLocomocion
        config = cargar_config(args.config, args.cambios)
        print(yaml.safe_dump(a_dict(config), sort_keys=False, allow_unicode=True))
        entorno = ZancudoLocomocion(config)
        obs, _ = entorno.reset(seed=0)
        print(f"observación: {obs.shape}, acción: {entorno.action_space.shape}, dt de la política: {entorno.dt} s")
        return 0

    if args.orden == "entrenar":
        from .entrenamiento import AjustesPPO, entrenar
        config = cargar_config(args.config, args.cambios)
        entrenar(config, args.pasos, args.salida, semilla=args.semilla, ajustes=AjustesPPO(n_entornos=args.entornos),
                 guardar_cada=args.guardar_cada, seguir=args.seguir)
        return 0

    if args.orden == "evaluar":
        from .entrenamiento import Politica, evaluar
        resultado = evaluar(Politica(args.carpeta), args.comando, episodios=args.episodios)
        print(f"orden {args.comando} → " + ", ".join(f"{k} {v:.3f}" for k, v in resultado.items()))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
