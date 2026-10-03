# zancudo_moldeado.py — Zancudo con la recompensa MOLDEADA (NB44)
# Hereda todo de Zancudo (NB43) y solo cambia la recompensa (herencia, NB25).
import numpy as np
import gymnasium as gym
import mujoco

from zancudo_env import Zancudo


class ZancudoMoldeado(Zancudo):

    def __init__(self, velocidad_objetivo=1.0, pesos=None, **kwargs):
        super().__init__(**kwargs)
        self.velocidad_objetivo = velocidad_objetivo
        self.pesos = dict(velocidad=1.0, recto=0.3, vida=0.2, vuelo=0.5, pie_alto=2.0, suavidad=0.05)
        if pesos is not None:
            self.pesos.update(pesos)
        self.pies = [mujoco.mj_name2id(self.modelo, mujoco.mjtObj.mjOBJ_GEOM, n) for n in ("pie_d", "pie_i")]
        self.suelo = mujoco.mj_name2id(self.modelo, mujoco.mjtObj.mjOBJ_GEOM, "suelo")

    def reset(self, seed=None, options=None):
        self.accion_anterior = np.zeros(6)
        return super().reset(seed=seed, options=options)

    def pies_en_el_suelo(self):
        # ¿qué pies tocan el suelo? Miramos la lista de contactos (NB41)
        tocan = [False, False]
        for i in range(self.datos.ncon):
            c = self.datos.contact[i]
            for k, pie in enumerate(self.pies):
                if (c.geom1 == pie and c.geom2 == self.suelo) or (c.geom2 == pie and c.geom1 == self.suelo):
                    tocan[k] = True
        return tocan

    def step(self, accion):
        observacion, _, caido, truncado, info = super().step(accion)
        p = self.pesos
        accion = np.clip(accion, -1, 1)
        # 1. ir a la velocidad pedida: 1 si va justo a esa velocidad, menos cuanto más se aleje (campana, NB28)
        r_velocidad = np.exp(-((info["velocidad"] - self.velocidad_objetivo) ** 2) / 0.25)
        # 2. torso recto: 1 si está recto, menos cuanto más se incline
        r_recto = np.exp(-(self.datos.qpos[2] ** 2) / 0.05)
        # 3. andar, no correr: castigo si NINGÚN pie toca el suelo
        tocan = self.pies_en_el_suelo()
        en_el_aire = 0.0 if any(tocan) else 1.0
        # 4. no dar patadas: castigo si un pie sube más de 15 cm
        alturas = np.array([self.datos.geom_xpos[pie][2] for pie in self.pies])
        exceso = float(np.sum(np.clip(alturas - 0.15, 0, None)))
        # 5. movimientos suaves: castigo por cambiar mucho la acción de una decisión a la siguiente
        cambio = float(np.sum((accion - self.accion_anterior) ** 2))
        self.accion_anterior = accion
        recompensa = (p["velocidad"] * r_velocidad + p["recto"] * r_recto + p["vida"]
                      - p["vuelo"] * en_el_aire - p["pie_alto"] * exceso - p["suavidad"] * cambio)
        info.update(r_velocidad=r_velocidad, r_recto=r_recto, en_el_aire=en_el_aire, exceso=exceso, cambio=cambio)
        return observacion, recompensa, caido, truncado, info


gym.register(id="ZancudoMoldeado-v0", entry_point=ZancudoMoldeado)
