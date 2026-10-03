# entrenar_zancudo.py — uso: python entrenar_zancudo.py <configuracion> <semilla> <pasos> [ruido]
# Script del NB43: entrena PPO en Zancudo-v0 por tramos, examina cada tramo y guarda agente + estadísticas.
import sys, time, torch
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
import zancudo_env                                            # registra Zancudo-v0

torch.set_num_threads(1)
configuracion, semilla, total = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ruido = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
nombre = f"zancudo_{configuracion}_s{semilla}" + (f"_ruido{ruido}".replace(".", "p") if ruido > 0 else "")   # sin puntos: SB3 los confunde con la extensión

entornos = VecNormalize(make_vec_env("Zancudo-v0", n_envs=4, seed=semilla, env_kwargs=dict(ruido_obs=ruido)))
ajustes = dict(seed=semilla)
if configuracion == "afinado":
    ajustes.update(n_steps=512, batch_size=64, learning_rate=3e-4,
                   policy_kwargs=dict(log_std_init=-1, net_arch=dict(pi=[256, 256], vf=[256, 256])))
agente = PPO("MlpPolicy", entornos, **ajustes)

examen = VecNormalize(make_vec_env("Zancudo-v0", n_envs=1, seed=123, env_kwargs=dict(ruido_obs=ruido)),
                      training=False, norm_reward=False)
inicio = time.time()
mejor = -np.inf
while agente.num_timesteps < total:
    agente.learn(100_352, reset_num_timesteps=False)
    examen.obs_rms = entornos.obs_rms
    notas, distancias = [], []
    for episodio in range(5):
        obs = examen.reset()
        nota, hecho = 0.0, False
        while not hecho:
            accion, _ = agente.predict(obs, deterministic=True)
            obs, r, hecho, info = examen.step(accion)
            nota += r[0]
        notas.append(nota)
        distancias.append(info[0]["x"])
    nota_media = float(np.mean(notas))
    print(nombre, agente.num_timesteps, round(nota_media, 1), round(float(np.std(notas)), 1),
          round(float(np.mean(distancias)), 2), f"{time.time() - inicio:.0f}s", flush=True)
    agente.save(nombre)
    entornos.save(f"{nombre}_norm.pkl")
    if nota_media > mejor:                                    # guardamos también el MEJOR (lección del NB35)
        mejor = nota_media
        agente.save(f"{nombre}_mejor")
        entornos.save(f"{nombre}_mejor_norm.pkl")
