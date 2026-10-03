# zancudo_env.py — el entorno de Gymnasium de Zancudo (NB43)
# Zancudo es el bípedo plano del NB42 (robots/zancudo.xml).
import os
from pathlib import Path

import numpy as np
import gymnasium as gym
from gymnasium import spaces
import mujoco

FICHERO = Path(__file__).parent / "robots" / "zancudo.xml"


class Zancudo(gym.Env):
    metadata = {"render_modes": ["rgb_array"], "render_fps": 50}

    def __init__(self, render_mode=None, peso_avance=1.0, peso_vida=1.0, peso_control=0.01,
                 ruido_obs=0.0, max_pasos=1000):
        self.modelo = mujoco.MjModel.from_xml_path(str(FICHERO))
        self.datos = mujoco.MjData(self.modelo)
        self.submuestreo = 10                       # 10 pasitos de 0,002 s = la política decide 50 veces por segundo
        self.dt = self.modelo.opt.timestep * self.submuestreo
        self.peso_avance, self.peso_vida, self.peso_control = peso_avance, peso_vida, peso_control
        self.ruido_obs = ruido_obs
        self.max_pasos = max_pasos
        self.render_mode = render_mode
        self.renderer = None
        # postura de partida (de pie, un poco agachado) y cuánto puede apartarse de ella cada articulación
        self.postura_base = np.array([0.3, -0.6, 0.3, 0.3, -0.6, 0.3])
        self.amplitud = np.array([1.0, 1.0, 0.6, 1.0, 1.0, 0.6])
        self.action_space = spaces.Box(-1.0, 1.0, shape=(6,), dtype=np.float32)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(18,), dtype=np.float64)

    # --- lo que "mide" el robot: nada de posición x ni de altura exacta del torso ---
    def _observacion(self):
        d = self.datos
        angulos = d.qpos[3:9]                       # codificadores: los 6 ángulos de las articulaciones
        velocidades = d.qvel[3:9]                   # sus velocidades de giro
        inclinacion = d.qpos[2]                     # la inclinación del torso (la daría la IMU con su filtro, NB41)
        giro = d.qvel[2]                            # la velocidad de giro del torso (el giróscopo)
        vel_torso = d.qvel[0:2]                     # velocidad hacia delante y hacia arriba del torso (estimada)
        fase = 2 * np.pi * self.pasos * self.dt / 0.8      # un reloj que da una vuelta cada 0,8 s (NB36)
        obs = np.concatenate([angulos, velocidades * 0.1, [inclinacion, giro * 0.1],
                              vel_torso, [np.sin(fase), np.cos(fase)]])
        if self.ruido_obs > 0:
            obs = obs + self.np_random.normal(0, self.ruido_obs, obs.shape)
        return obs

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.modelo, self.datos)
        # partimos de la postura base, con un poquito de azar (NB25)
        self.datos.qpos[3:9] = self.postura_base + self.np_random.uniform(-0.05, 0.05, 6)
        self.datos.qpos[1] = -0.8 * (1 - np.cos(0.3))   # bajamos el torso lo que baja al agacharse (NB36), para que los pies toquen el suelo
        self.datos.ctrl[:] = self.postura_base
        mujoco.mj_forward(self.modelo, self.datos)
        self.pasos = 0
        return self._observacion(), {}

    def step(self, accion):
        accion = np.clip(accion, -1, 1)
        objetivo = self.postura_base + self.amplitud * accion           # la acción = ángulos objetivo (NB40)
        self.datos.ctrl[:] = np.clip(objetivo, self.modelo.actuator_ctrlrange[:, 0], self.modelo.actuator_ctrlrange[:, 1])
        x_antes = self.datos.qpos[0]
        for _ in range(self.submuestreo):
            mujoco.mj_step(self.modelo, self.datos)
        self.pasos += 1
        velocidad = (self.datos.qpos[0] - x_antes) / self.dt
        altura = 0.865 + self.datos.qpos[1]          # altura de la cadera sobre el suelo
        inclinacion = self.datos.qpos[2]
        caido = altura < 0.55 or abs(inclinacion) > 0.8
        recompensa = (self.peso_avance * velocidad + self.peso_vida
                      - self.peso_control * float(np.sum(accion ** 2)))
        truncado = self.pasos >= self.max_pasos
        info = {"x": self.datos.qpos[0], "velocidad": velocidad}
        return self._observacion(), recompensa, caido, truncado, info

    def render(self):
        if self.renderer is None:
            self.renderer = mujoco.Renderer(self.modelo, height=300, width=400)
        self.renderer.update_scene(self.datos, camera="lado")
        return self.renderer.render()

    def close(self):
        if self.renderer is not None:
            self.renderer.close()
            self.renderer = None


gym.register(id="Zancudo-v0", entry_point=Zancudo)
