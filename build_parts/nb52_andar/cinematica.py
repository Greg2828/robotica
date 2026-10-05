"""Cinemática inversa de Zancudo: la pierna, analítica; el centro de masas, por iteración."""
from __future__ import annotations

import logging
import math

import mujoco
import numpy as np
from numpy.typing import NDArray

MUSLO = PIERNA = 0.4
ALTURA_TORSO = 0.865       # altura de la cadera con las piernas estiradas (qpos[1] = 0)

logger = logging.getLogger(__name__)


def ik_pierna(cadera_x: float, cadera_z: float, tobillo_x: float, tobillo_z: float) -> tuple[float, float, float]:
    """Ángulos (cadera, rodilla, tobillo) que ponen el tobillo en su sitio con la planta horizontal."""
    dx, dz = tobillo_x - cadera_x, cadera_z - tobillo_z
    coseno = (dx ** 2 + dz ** 2 - MUSLO ** 2 - PIERNA ** 2) / (2 * MUSLO * PIERNA)
    rodilla = -math.acos(min(1.0, max(-1.0, coseno)))
    cadera = math.atan2(dx, dz) - rodilla / 2
    return cadera, rodilla, -(cadera + rodilla)


class Cinematica:
    """Calcula posturas completas de Zancudo (torso recto, a altura fija) con un CdM dado."""

    def __init__(self, modelo: mujoco.MjModel, altura_cadera: float = 0.767, tolerancia: float = 1e-7,
                 max_iter: int = 20):
        self.modelo = modelo
        self.datos = mujoco.MjData(modelo)          # unos datos propios: no tocamos los de la simulación
        self.altura_cadera = altura_cadera
        self.tolerancia, self.max_iter = tolerancia, max_iter

    def _postura_con_cadera(self, x: float, pie_d, pie_i) -> tuple[NDArray[np.float64], float]:
        """Postura con la cadera en x, y el CdM (x) que resulta."""
        q = np.zeros(self.modelo.nq)
        q[0], q[1] = x, self.altura_cadera - ALTURA_TORSO
        q[3:6] = ik_pierna(x, self.altura_cadera, *pie_d)
        q[6:9] = ik_pierna(x, self.altura_cadera, *pie_i)
        self.datos.qpos[:] = q
        mujoco.mj_kinematics(self.modelo, self.datos)
        mujoco.mj_comPos(self.modelo, self.datos)
        return q, self.datos.subtree_com[1][0]

    def postura(self, cdm_x: float, pie_d, pie_i, cadera_x: float | None = None) -> NDArray[np.float64]:
        """qpos con los tobillos en pie_d y pie_i (x, z) y el CdM en cdm_x (método de la secante)."""
        x_a = cdm_x if cadera_x is None else cadera_x
        q, cdm = self._postura_con_cadera(x_a, pie_d, pie_i)
        error_a = cdm_x - cdm
        x_b = x_a + error_a
        for _ in range(self.max_iter):
            q, cdm = self._postura_con_cadera(x_b, pie_d, pie_i)
            error_b = cdm_x - cdm
            if abs(error_b) < self.tolerancia or error_a == error_b:
                return q
            x_a, error_a, x_b = x_b, error_b, x_b + error_b * (x_b - x_a) / (error_a - error_b)
        logger.warning("la IK del CdM no converge: pedido %.4f m, error %.1e m (¿pierna casi estirada?)",
                       cdm_x, error_b)
        return q

    def trayectoria(self, cdm: NDArray[np.float64], pies: NDArray[np.float64]) -> NDArray[np.float64]:
        """Una postura por instante: cdm (n,), pies (n, 2, 2) → (n, nq)."""
        posturas = np.zeros((len(cdm), self.modelo.nq))
        cadera_x = None
        for k in range(len(cdm)):
            posturas[k] = self.postura(cdm[k], pies[k, 0], pies[k, 1], cadera_x)
            cadera_x = posturas[k, 0]
        return posturas
