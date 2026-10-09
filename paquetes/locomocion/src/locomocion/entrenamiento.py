"""Entrenar (PPO de Stable-Baselines3) y evaluar políticas de locomoción."""
from __future__ import annotations

import csv
import json
import logging
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

from .config import ConfigEntorno, guardar_config, cargar_config
from .entorno import ZancudoLocomocion

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AjustesPPO:
    """Los hiperparámetros del algoritmo (aparte de los del entorno)."""
    n_entornos: int = 16
    n_pasos: int = 256               # pasos por entorno antes de cada actualización (16 × 256 = 4096)
    lote: int = 1024
    epocas: int = 5
    tasa_aprendizaje: float = 3e-4
    gamma: float = 0.99
    lambda_gae: float = 0.95
    entropia: float = 0.0
    log_std_inicial: float = -1.0
    red: tuple[int, ...] = (256, 128)
    hilos_torch: int = 2


def _fabrica(config: ConfigEntorno):
    def crear():
        return ZancudoLocomocion(config)
    return crear


def crear_entornos(config: ConfigEntorno, n: int, semilla: int, procesos: bool = True):
    """n copias del entorno (en procesos aparte si procesos=True), cada una con su semilla."""
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
    clase = SubprocVecEnv if procesos and n > 1 else DummyVecEnv
    return make_vec_env(_fabrica(config), n_envs=n, seed=semilla, vec_env_cls=clase)


def _registro_callback(carpeta: Path, cada_actualizacion: int = 10):
    """Retrollamada de SB3: en cada actualización apunta en progreso.csv la media de cada término por episodio
    (y la cuenta en el registro: con nivel INFO una de cada `cada_actualizacion`, el resto con DEBUG)."""
    from stable_baselines3.common.callbacks import BaseCallback

    class RegistroTerminos(BaseCallback):
        def __init__(self):
            super().__init__()
            self.episodios: list[dict] = []
            self.fichero = carpeta / "progreso.csv"
            self.columnas: list[str] | None = None
            if self.fichero.exists():                    # al reanudar, se sigue escribiendo en el mismo fichero
                with self.fichero.open() as f:
                    self.columnas = next(csv.reader(f))
            self.inicio = time.time()
            self.actualizaciones = 0

        def _on_step(self) -> bool:
            for info in self.locals["infos"]:
                if "episodio_terminos" in info and "episode" in info:
                    fila = dict(info["episodio_terminos"])
                    fila["recompensa"] = info["episode"]["r"]
                    fila["duracion"] = info["episode"]["l"]
                    self.episodios.append(fila)
            return True

        def _on_rollout_end(self) -> None:
            if not self.episodios:
                return
            claves = sorted({k for e in self.episodios for k in e})
            medias = {k: float(np.mean([e.get(k, 0.0) for e in self.episodios])) for k in claves}
            fila = {"pasos": self.num_timesteps, "segundos": round(time.time() - self.inicio, 1),
                    "episodios": len(self.episodios), **medias}
            if self.columnas is None:
                self.columnas = list(fila)
                with self.fichero.open("w", newline="") as f:
                    csv.DictWriter(f, self.columnas).writeheader()
            with self.fichero.open("a", newline="") as f:
                csv.DictWriter(f, self.columnas, extrasaction="ignore").writerow(fila)
            self.actualizaciones += 1
            nivel = logging.INFO if self.actualizaciones % cada_actualizacion == 0 else logging.DEBUG
            logger.log(nivel, "pasos %d | recompensa %.2f | duración %.0f | seguir_velocidad %.3f | %.0f pasos/s",
                       self.num_timesteps, medias["recompensa"], medias["duracion"],
                       medias.get("seguir_velocidad", float("nan")),
                       self.num_timesteps / max(time.time() - self.inicio, 1e-9))
            self.episodios = []

    return RegistroTerminos()


def entrenar(config: ConfigEntorno, pasos: int, carpeta: str | Path, semilla: int = 0,
             ajustes: AjustesPPO = AjustesPPO(), guardar_cada: int = 200_000, procesos: bool = True,
             seguir: bool = False) -> Path:
    """Entrena PPO y guarda en `carpeta`: config.yaml, ajustes.json, progreso.csv, modelo.zip, normalizacion.pkl."""
    import torch
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import VecNormalize

    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(ajustes.hilos_torch)
    if seguir:                                            # se sigue con la configuración guardada
        config = cargar_config(carpeta / "config.yaml")
    crudos = crear_entornos(config, ajustes.n_entornos, semilla, procesos)
    if seguir:
        entornos = VecNormalize.load(str(carpeta / "normalizacion.pkl"), crudos)
        agente = PPO.load(carpeta / "modelo.zip", env=entornos)
        logger.info("se reanuda desde %s (%d pasos ya hechos)", carpeta, agente.num_timesteps)
    else:
        (carpeta / "progreso.csv").unlink(missing_ok=True)
        guardar_config(config, carpeta / "config.yaml")
        (carpeta / "ajustes.json").write_text(json.dumps({**asdict(ajustes), "semilla": semilla}, indent=2))
        entornos = VecNormalize(crudos, gamma=ajustes.gamma)
        agente = PPO("MlpPolicy", entornos, seed=semilla, n_steps=ajustes.n_pasos, batch_size=ajustes.lote,
                     n_epochs=ajustes.epocas, learning_rate=ajustes.tasa_aprendizaje, gamma=ajustes.gamma,
                     gae_lambda=ajustes.lambda_gae, ent_coef=ajustes.entropia,
                     policy_kwargs=dict(log_std_init=ajustes.log_std_inicial, activation_fn=torch.nn.ELU,
                                        net_arch=dict(pi=list(ajustes.red), vf=list(ajustes.red))))
    callback = _registro_callback(carpeta)
    logger.info("entrenando %d pasos con %d entornos (semilla %d) → %s", pasos, ajustes.n_entornos, semilla, carpeta)
    objetivo = agente.num_timesteps + pasos if seguir else pasos
    try:
        while agente.num_timesteps < objetivo:
            tramo = min(guardar_cada, objetivo - agente.num_timesteps)
            agente.learn(tramo, reset_num_timesteps=False, callback=callback)
            agente.save(carpeta / "modelo.zip")
            entornos.save(str(carpeta / "normalizacion.pkl"))
            logger.info("guardado en %s (%d pasos)", carpeta, agente.num_timesteps)
    finally:
        entornos.close()
    return carpeta


class Politica:
    """Una política entrenada, lista para usar fuera de SB3: obs (sin normalizar) → acción."""

    def __init__(self, carpeta: str | Path):
        from stable_baselines3 import PPO
        from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
        self.carpeta = Path(carpeta)
        self.config = cargar_config(self.carpeta / "config.yaml")
        self.agente = PPO.load(self.carpeta / "modelo.zip", device="cpu")
        falso = DummyVecEnv([_fabrica(self.config)])
        self.normalizacion = VecNormalize.load(str(self.carpeta / "normalizacion.pkl"), falso)
        self.normalizacion.training = False

    def __call__(self, obs: np.ndarray) -> np.ndarray:
        accion, _ = self.agente.predict(self.normalizacion.normalize_obs(obs), deterministic=True)
        return accion


def evaluar(politica: Politica, comando, episodios: int = 3, semilla: int = 1000,
            config: ConfigEntorno | None = None) -> dict[str, float]:
    """Corre episodios con un comando fijo y mide cómo lo sigue el robot."""
    entorno = ZancudoLocomocion(config or politica.config)
    duraciones, velocidades, giros, recompensas_ = [], [], [], []
    for k in range(episodios):
        obs, _ = entorno.reset(seed=semilla + k, options={"comando": comando})
        total, registro_v, registro_w, hecho = 0.0, [], [], False
        while not hecho:
            obs, r, terminado, truncado, info = entorno.step(politica(obs))
            total += r
            if entorno.pasos * entorno.dt > 1.0:         # el primer segundo es arrancar
                registro_v.append(info["vel_lineal"][:2])
                registro_w.append(info["vel_angular"][2])
            hecho = terminado or truncado
        duraciones.append(entorno.pasos * entorno.dt)
        recompensas_.append(total)
        if registro_v:
            velocidades.append(np.mean(registro_v, axis=0))
            giros.append(np.mean(registro_w))
    entorno.close()
    v = np.mean(velocidades, axis=0) if velocidades else np.full(2, np.nan)
    return {"duracion": float(np.mean(duraciones)), "recompensa": float(np.mean(recompensas_)),
            "vx": float(v[0]), "vy": float(v[1]), "giro": float(np.mean(giros)) if giros else float("nan")}
