"""El robot: cargar Zancudo 3D (dato del paquete) y ajustarlo a la configuración."""
from __future__ import annotations

import logging
from importlib import resources

import mujoco
import numpy as np

from .config import Simulacion

logger = logging.getLogger(__name__)

ARCHIVO_ROBOT = "zancudo3d.xml"


def ruta_robot() -> str:
    """Ruta del MJCF que viaja DENTRO del paquete (funciona esté donde esté instalado)."""
    return str(resources.files("locomocion") / "robots" / ARCHIVO_ROBOT)


def cargar_modelo(sim: Simulacion) -> mujoco.MjModel:
    """Carga el MJCF y le aplica el paso de tiempo y la rigidez de los servos de la configuración."""
    modelo = mujoco.MjModel.from_xml_path(ruta_robot())
    modelo.opt.timestep = sim.paso
    # servos de posición (NB50): fuerza = kp·(ctrl − q) − kv·q̇  →  gainprm[0] = kp, biasprm[1:3] = (−kp, −kv)
    modelo.actuator_gainprm[:, 0] = sim.kp
    modelo.actuator_biasprm[:, 1] = -sim.kp
    modelo.actuator_biasprm[:, 2] = -sim.kv
    logger.debug("modelo cargado: nq=%d nv=%d nu=%d, paso %.4f s, kp=%.0f kv=%.1f",
                 modelo.nq, modelo.nv, modelo.nu, sim.paso, sim.kp, sim.kv)
    return modelo


class Indices:
    """Dónde está cada cosa del robot (se calcula UNA vez, no en cada paso)."""

    def __init__(self, modelo: mujoco.MjModel):
        self.torso = modelo.body("torso").id
        self.pies = np.array([modelo.body("pie_d").id, modelo.body("pie_i").id])
        self.tactos = [modelo.sensor("tacto_d").adr[0], modelo.sensor("tacto_i").adr[0]]
        self.postura_defecto = modelo.key("agachado").qpos[7:].copy()
        self.qpos_inicial = modelo.key("agachado").qpos.copy()
        self.limite_bajo = modelo.actuator_ctrlrange[:, 0].copy()
        self.limite_alto = modelo.actuator_ctrlrange[:, 1].copy()
