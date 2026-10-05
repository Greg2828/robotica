"""Ejecutar posturas con los servos de Zancudo, y recuperarse de empujones con un paso de captura."""
from __future__ import annotations

import logging
import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto

import mujoco
import numpy as np
from numpy.typing import NDArray

from .cinematica import Cinematica, ik_pierna, ALTURA_TORSO
from .plan import G, CENTRO_PIE, ALTURA_TOBILLO

logger = logging.getLogger(__name__)

TALON, PUNTA = -0.06, 0.14     # la planta, respecto al tobillo


def configurar_servos(modelo: mujoco.MjModel, kp: float, kv: float) -> None:
    """Cambia la rigidez (kp) y la amortiguación (kv) de todos los servos de posición."""
    modelo.actuator_gainprm[:, 0] = kp
    modelo.actuator_biasprm[:, 1] = -kp
    modelo.actuator_biasprm[:, 2] = -kv


def se_ha_caido(datos: mujoco.MjData) -> bool:
    return abs(datos.qpos[2]) > 0.6 or datos.qpos[1] < -0.35


@dataclass
class Registro:
    t: NDArray[np.float64]
    cdm: NDArray[np.float64]
    tobillos: NDArray[np.float64]       # (n, 2): x de los tobillos derecho e izquierdo
    error_q: NDArray[np.float64]        # error máximo de las articulaciones en cada instante
    cae_en: float | None = None


def ejecutar(modelo: mujoco.MjModel, posturas: NDArray[np.float64], dt: float, prealimentar: bool = True,
             empujon: tuple[float, float] | None = None,
             al_paso: Callable[[mujoco.MjData], None] | None = None) -> Registro:
    """Sigue las posturas con los servos. empujon = (fuerza en N, instante en s), durante 0,1 s.

    Si se da `al_paso`, se le llama con los datos tras cada instante (para grabar, medir...).
    """
    datos = mujoco.MjData(modelo)
    datos.qpos[:] = posturas[0]
    datos.ctrl[:] = posturas[0, 3:]
    mujoco.mj_forward(modelo, datos)
    velocidades = np.gradient(posturas, dt, axis=0)
    kv_kp = -modelo.actuator_biasprm[0, 2] / modelo.actuator_gainprm[0, 0]
    subpasos = round(dt / modelo.opt.timestep)
    torso = modelo.body("torso").id
    pies = [modelo.body("pie_d").id, modelo.body("pie_i").id]
    n = len(posturas)
    reg = Registro(np.arange(n) * dt, np.full(n, np.nan), np.full((n, 2), np.nan), np.full(n, np.nan))
    for k in range(n):
        datos.ctrl[:] = posturas[k, 3:] + (kv_kp * velocidades[k, 3:] if prealimentar else 0.0)
        if empujon is not None:
            fuerza, instante = empujon
            datos.xfrc_applied[torso, 0] = fuerza if instante <= k * dt < instante + 0.1 else 0.0
        for _ in range(subpasos):
            mujoco.mj_step(modelo, datos)
        reg.cdm[k] = datos.subtree_com[1][0]
        reg.tobillos[k] = [datos.xpos[p][0] for p in pies]
        reg.error_q[k] = np.abs(datos.qpos[3:] - posturas[k, 3:]).max()
        if al_paso is not None:
            al_paso(datos)
        if se_ha_caido(datos):
            reg.cae_en = k * dt
            logger.info("se ha caído a los %.2f s", reg.cae_en)
            break
    return reg


class Estado(Enum):
    DE_PIE = auto()
    PASO = auto()


class PasoDeCaptura:
    """Zancudo de pie que, si su DCM sale de los pies, da pasos al punto de captura (NB51)."""

    def __init__(self, modelo: mujoco.MjModel, z0: float = 0.71, t_paso: float = 0.25, alcance: float = 0.35,
                 altura_paso: float = 0.04, margen: float = 0.0, max_pasos: int = 1, dt: float = 0.01):
        self.modelo, self.dt = modelo, dt
        self.omega = math.sqrt(G / z0)
        self.t_paso, self.alcance, self.altura_paso = t_paso, alcance, altura_paso
        self.margen, self.max_pasos = margen, max_pasos
        self.cinematica = Cinematica(modelo)

    def _dentro(self, pies: list[float]) -> tuple[float, float]:
        return min(pies) + TALON + self.margen, max(pies) + PUNTA - self.margen

    def probar(self, fuerza: float, instante: float = 0.5, duracion: float = 5.0,
               al_paso: Callable[[mujoco.MjData], None] | None = None) -> tuple[bool, int]:
        """Empuja (fuerza N durante 0,1 s) y devuelve (sigue de pie, pasos dados)."""
        m, w, dt = self.modelo, self.omega, self.dt
        d = mujoco.MjData(m)
        pies = [0.0, 0.0]
        q = self.cinematica.postura(CENTRO_PIE, (0.0, ALTURA_TOBILLO), (0.0, ALTURA_TOBILLO))
        d.qpos[:] = q
        mujoco.mj_forward(m, d)
        kv_kp = -m.actuator_biasprm[0, 2] / m.actuator_gainprm[0, 0]
        subpasos = round(dt / m.opt.timestep)
        torso = m.body("torso").id
        estado, reloj, pasos = Estado.DE_PIE, 0.0, 0
        x0 = xi0 = CENTRO_PIE
        anterior = q.copy()
        for k in range(round(duracion / dt)):
            t = k * dt
            mujoco.mj_subtreeVel(m, d)
            x, v = d.subtree_com[1][0], d.subtree_linvel[1][0]
            xi = x + v / w
            tobillos = [(pies[0], ALTURA_TOBILLO), (pies[1], ALTURA_TOBILLO)]
            if estado is Estado.DE_PIE:
                bajo, alto = self._dentro(pies)
                if not bajo <= xi <= alto and pasos < self.max_pasos:
                    estado, reloj, pasos = Estado.PASO, 0.0, pasos + 1
                    vuela = int(np.argmax([abs(xi - p - CENTRO_PIE) for p in pies]))
                    apoya, despegue = 1 - vuela, pies[vuela]
                    logger.info("t = %.2f s: DCM en %.3f, fuera de [%.3f, %.3f] → paso %d", t, xi, bajo, alto, pasos)
                else:
                    objetivo = min(max(xi0, bajo), alto)
                    cdm = objetivo + (x0 - objetivo) * math.exp(-w * reloj)
                    q = self.cinematica.postura(cdm, *tobillos, anterior[0])
                    reloj += dt
            if estado is Estado.PASO:
                s = min(reloj / self.t_paso, 1.0)
                p = pies[apoya] + CENTRO_PIE
                if s < 0.7:                              # a partir del 70 % ya no se cambia el destino
                    xi_final = p + (xi - p) * math.exp(w * (self.t_paso - reloj))
                    destino = min(max(xi_final - CENTRO_PIE, pies[apoya] - self.alcance), pies[apoya] + self.alcance)
                avance = 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5
                tobillos[vuela] = (despegue + (destino - despegue) * avance,
                                   ALTURA_TOBILLO + self.altura_paso * 64 * s ** 3 * (1 - s) ** 3)
                q = np.zeros(m.nq)
                q[0] = d.qpos[0]                         # la cadera de apoyo, libre: donde esté
                q[1] = self.cinematica.altura_cadera - ALTURA_TORSO
                q[3:6] = ik_pierna(q[0], self.cinematica.altura_cadera, *tobillos[0])
                q[6:9] = ik_pierna(q[0], self.cinematica.altura_cadera, *tobillos[1])
                reloj += dt
                if reloj >= self.t_paso - 1e-9:
                    pies[vuela] = destino
                    estado, reloj, x0, xi0 = Estado.DE_PIE, 0.0, x, xi
                    logger.debug("pie %s apoyado en %.3f m (DCM %.3f)", "derecho" if vuela == 0 else "izquierdo",
                                 destino, xi)
            d.ctrl[:] = q[3:] + kv_kp * (q[3:] - anterior[3:]) / dt
            anterior = q
            d.xfrc_applied[torso, 0] = fuerza if instante <= t < instante + 0.1 else 0.0
            for _ in range(subpasos):
                mujoco.mj_step(m, d)
            if al_paso is not None:
                al_paso(d)
            if se_ha_caido(d):
                logger.info("se ha caído a los %.2f s, tras %d pasos", t, pasos)
                return False, pasos
        return True, pasos
