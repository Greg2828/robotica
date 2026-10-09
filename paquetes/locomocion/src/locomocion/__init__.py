"""locomocion: entorno de Gymnasium para que Zancudo 3D aprenda a seguir órdenes de velocidad (NB54)."""
import logging

__version__ = "0.1.0"

from .config import ConfigEntorno, Simulacion, Comandos, Recompensa, Episodio, cargar_config, guardar_config
from .entorno import ZancudoLocomocion
from .recompensas import TERMINOS, termino

__all__ = [
    "ConfigEntorno", "Simulacion", "Comandos", "Recompensa", "Episodio", "cargar_config", "guardar_config",
    "ZancudoLocomocion", "TERMINOS", "termino",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())

import gymnasium as _gym

if "Zancudo3D-v0" not in _gym.registry:
    _gym.register(id="Zancudo3D-v0", entry_point="locomocion.entorno:ZancudoLocomocion")
