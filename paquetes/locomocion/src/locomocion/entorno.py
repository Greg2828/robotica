"""El entorno de Gymnasium: Zancudo 3D tiene que seguir órdenes de velocidad (vx, vy, giro)."""
from __future__ import annotations

import logging

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces

from . import recompensas
from .config import ConfigEntorno
from .modelo import Indices, cargar_modelo

logger = logging.getLogger(__name__)

# escalas de la observación: que todos los números anden por ±1 (como legged_gym)
ESCALA_VEL_LINEAL = 2.0
ESCALA_VEL_ANGULAR = 0.25
ESCALA_VEL_ARTICULAR = 0.05
UMBRAL_CONTACTO = 1.0          # N: con más fuerza en la planta, el pie «está en el suelo»
DIM_OBS = 3 + 3 + 3 + 3 + 12 + 12 + 12 + 2


class ZancudoLocomocion(gym.Env):
    """Zancudo 3D con órdenes de velocidad.

    Observación (50 números, todo en el marco del torso, nada de posición absoluta):
      gravedad proyectada (3) · velocidad angular (3) · velocidad lineal (3) · órdenes (3)
      · ángulos − postura por defecto (12) · velocidades articulares (12) · última acción (12)
      · reloj de fase (sen, cos) (2)
    Acción (12 números en ±1): objetivo de los servos = postura por defecto + escala · acción.
    """

    metadata = {"render_modes": ["rgb_array"], "render_fps": 50}

    def __init__(self, config: ConfigEntorno | None = None, render_mode: str | None = None):
        self.config = config or ConfigEntorno()
        recompensas.comprobar_pesos(self.config.recompensa.pesos)
        self.modelo = cargar_modelo(self.config.simulacion)
        self.datos = mujoco.MjData(self.modelo)
        self.ind = Indices(self.modelo)
        self.dt = self.config.simulacion.dt
        self.max_pasos = round(self.config.episodio.duracion / self.dt)
        self.metadata = {**self.metadata, "render_fps": round(1 / self.dt)}
        self.render_mode = render_mode
        self._camara = None

        self.action_space = spaces.Box(-1.0, 1.0, shape=(self.modelo.nu,), dtype=np.float32)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(DIM_OBS,), dtype=np.float32)

        self.comando = np.zeros(3)
        self.accion = np.zeros(self.modelo.nu)
        self.accion_anterior = np.zeros(self.modelo.nu)
        self.tiempo_aire = np.zeros(2)
        self.contacto_anterior = np.ones(2, dtype=bool)
        self.pasos = 0
        self.terminos_episodio: dict[str, float] = {}

    # --- lo que «siente» el robot -----------------------------------------------------------
    def _rotacion(self) -> np.ndarray:
        return self.datos.xmat[self.ind.torso].reshape(3, 3)

    def _medir(self) -> dict[str, np.ndarray]:
        d, R = self.datos, self._rotacion()
        return {
            "gravedad": R.T @ np.array([0.0, 0.0, -1.0]),         # del mundo al marco del torso (NB53, E1)
            "vel_angular": d.qvel[3:6].copy(),                     # ya está en el marco local (NB53)
            "vel_lineal": R.T @ d.qvel[0:3],                       # la lineal está en el mundo: la giramos
            "articulaciones": d.qpos[7:] - self.ind.postura_defecto,
            "vel_articulares": d.qvel[6:].copy(),
            "contacto": d.sensordata[self.ind.tactos] > UMBRAL_CONTACTO,
        }

    def _fase(self) -> float:
        return (self.pasos * self.dt / self.config.recompensa.periodo_paso) % 1.0

    def _observacion(self, medida: dict[str, np.ndarray]) -> np.ndarray:
        fase = 2 * np.pi * self._fase()
        obs = np.concatenate([
            medida["gravedad"],
            medida["vel_angular"] * ESCALA_VEL_ANGULAR,
            medida["vel_lineal"] * ESCALA_VEL_LINEAL,
            self.comando * np.array([ESCALA_VEL_LINEAL, ESCALA_VEL_LINEAL, ESCALA_VEL_ANGULAR]),
            medida["articulaciones"],
            medida["vel_articulares"] * ESCALA_VEL_ARTICULAR,
            self.accion,
            [np.sin(fase), np.cos(fase)],
        ])
        return obs.astype(np.float32)

    # --- órdenes ----------------------------------------------------------------------------
    def muestrear_comando(self) -> np.ndarray:
        c = self.config.comandos
        if self.np_random.random() < c.prob_quieto:
            return np.zeros(3)
        return np.array([self.np_random.uniform(*c.vx), self.np_random.uniform(*c.vy), self.np_random.uniform(*c.giro)])

    # --- la API de Gymnasium ------------------------------------------------------------------
    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)                       # siembra self.np_random (NB25, NB28)
        ep, d = self.config.episodio, self.datos
        mujoco.mj_resetData(self.modelo, d)
        d.qpos[:] = self.ind.qpos_inicial
        d.qpos[7:] += self.np_random.uniform(-ep.ruido_articulaciones, ep.ruido_articulaciones, self.modelo.nu)
        d.qvel[:] = self.np_random.uniform(-ep.ruido_velocidades, ep.ruido_velocidades, self.modelo.nv)
        d.ctrl[:] = self.ind.postura_defecto
        mujoco.mj_forward(self.modelo, d)

        opciones = options or {}
        self.comando = np.asarray(opciones["comando"], dtype=float) if "comando" in opciones else self.muestrear_comando()
        self.accion[:] = 0.0
        self.accion_anterior[:] = 0.0
        self.tiempo_aire[:] = 0.0
        self.contacto_anterior[:] = True
        self.pasos = 0
        self.terminos_episodio = {}
        return self._observacion(self._medir()), {"comando": self.comando.copy()}

    def step(self, accion):
        sim, ep = self.config.simulacion, self.config.episodio
        self.accion_anterior = self.accion
        self.accion = np.clip(np.asarray(accion, dtype=float), -1.0, 1.0)
        objetivo = self.ind.postura_defecto + sim.escala_accion * self.accion
        self.datos.ctrl[:] = np.clip(objetivo, self.ind.limite_bajo, self.ind.limite_alto)
        for _ in range(sim.decimacion):                # decimación: varios pasos de física por decisión
            mujoco.mj_step(self.modelo, self.datos)
        self.pasos += 1

        medida = self._medir()
        contacto = medida["contacto"]
        primer_contacto = contacto & ~self.contacto_anterior
        self.tiempo_aire += self.dt
        tiempo_aire_al_aterrizar = self.tiempo_aire * primer_contacto
        self.tiempo_aire[contacto] = 0.0
        self.contacto_anterior = contacto

        altura = float(self.datos.qpos[2])
        m = recompensas.Medidas(
            comando=self.comando, vel_lineal=medida["vel_lineal"], vel_angular=medida["vel_angular"],
            gravedad=medida["gravedad"], altura=altura, pares=self.datos.actuator_force.copy(),
            accion=self.accion, accion_anterior=self.accion_anterior, articulaciones=medida["articulaciones"],
            contacto=contacto, primer_contacto=primer_contacto, tiempo_aire=tiempo_aire_al_aterrizar,
            fase=self._fase(),
        )
        recompensa, partes = recompensas.calcular(m, self.config.recompensa, self.dt)
        for nombre, valor in partes.items():
            self.terminos_episodio[nombre] = self.terminos_episodio.get(nombre, 0.0) + valor

        inclinacion = float(np.arccos(np.clip(-medida["gravedad"][2], -1.0, 1.0)))
        caido = altura < ep.altura_minima or inclinacion > ep.inclinacion_maxima
        sin_numeros = not np.all(np.isfinite(self.datos.qpos))
        terminado = bool(caido or sin_numeros)
        truncado = self.pasos >= self.max_pasos
        if sin_numeros:
            logger.warning("la simulación ha dado NaN en el paso %d: se termina el episodio", self.pasos)

        info = {"terminos": partes, "vel_lineal": medida["vel_lineal"], "vel_angular": medida["vel_angular"],
                "comando": self.comando.copy(), "contacto": contacto}
        if terminado or truncado:
            info["episodio_terminos"] = dict(self.terminos_episodio)
        return self._observacion(medida), float(recompensa), terminado, truncado, info

    def render(self):
        if self._camara is None:
            self._camara = mujoco.Renderer(self.modelo, height=240, width=320)
        self._camara.update_scene(self.datos, camera="lado")
        return self._camara.render()

    def close(self):
        if self._camara is not None:
            self._camara.close()
            self._camara = None
