# entrenar_moldeado.py — uso: python entrenar_moldeado.py <variante> <pasos>
# Script del NB44: entrena PPO (ajustes por defecto + VecNormalize) en ZancudoMoldeado-v0 con distintas variantes.
import sys, time, torch
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
import zancudo_moldeado                                       # registra ZancudoMoldeado-v0

VARIANTES = {
    "completa":     dict(),                                   # los cinco términos
    "sin_vuelo":    dict(pesos=dict(vuelo=0.0)),              # quitamos el castigo por volar
    "sin_pie_alto": dict(pesos=dict(pie_alto=0.0, suavidad=0.0)),   # quitamos patadas y suavidad
    "lento":        dict(velocidad_objetivo=0.5),             # pedimos medio metro por segundo
}

torch.set_num_threads(1)
variante, total = sys.argv[1], int(sys.argv[2])
kwargs = VARIANTES[variante]
nombre = f"moldeado_{variante}"
entornos = VecNormalize(make_vec_env("ZancudoMoldeado-v0", n_envs=4, seed=0, env_kwargs=kwargs))
agente = PPO("MlpPolicy", entornos, seed=0)
examen = VecNormalize(make_vec_env("ZancudoMoldeado-v0", n_envs=1, seed=123, env_kwargs=kwargs),
                      training=False, norm_reward=False)
inicio, mejor = time.time(), -np.inf
while agente.num_timesteps < total:
    agente.learn(100_352, reset_num_timesteps=False)
    examen.obs_rms = entornos.obs_rms
    notas, distancias, duraciones = [], [], []
    for episodio in range(5):
        obs = examen.reset()
        nota, pasos, hecho = 0.0, 0, False
        while not hecho:
            accion, _ = agente.predict(obs, deterministic=True)
            obs, r, hecho, info = examen.step(accion)
            nota += r[0]
            pasos += 1
        notas.append(nota)
        distancias.append(info[0]["x"])
        duraciones.append(pasos)
    nota_media = float(np.mean(notas))
    print(nombre, agente.num_timesteps, round(nota_media, 1), round(float(np.std(notas)), 1),
          round(float(np.mean(distancias)), 2), round(float(np.mean(duraciones)), 1), f"{time.time() - inicio:.0f}s", flush=True)
    agente.save(nombre)
    entornos.save(f"{nombre}_norm.pkl")
    if nota_media > mejor:
        mejor = nota_media
        agente.save(f"{nombre}_mejor")
        entornos.save(f"{nombre}_mejor_norm.pkl")
