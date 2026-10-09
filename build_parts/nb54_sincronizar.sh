#!/bin/sh
# Solo para desarrollo: copia la fuente del paquete (build_parts/nb54_locomocion) a paquetes/locomocion.
# El notebook NB54 hace lo mismo con %%writefile; este atajo sirve para lanzar entrenamientos sin ejecutarlo.
cd "$(dirname "$0")/.." || exit 1
mkdir -p paquetes/locomocion/src/locomocion/robots paquetes/locomocion/tests
cp build_parts/nb54_locomocion/pyproject.toml paquetes/locomocion/
cp build_parts/nb54_locomocion/src/locomocion/*.py paquetes/locomocion/src/locomocion/
cp build_parts/nb54_locomocion/tests/*.py paquetes/locomocion/tests/
cp notebooks/robots/zancudo3d.xml paquetes/locomocion/src/locomocion/robots/
