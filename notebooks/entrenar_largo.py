# entrenar_largo.py  —  uso: python entrenar_largo.py Hopper-v5 defecto 1000000
# Script del NB35: entrena PPO con VecNormalize por tramos, examina cada tramo y guarda agente + estadísticas.
import sys, time, torch
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3.common.evaluation import evaluate_policy

torch.set_num_threads(1)
nombre, configuracion, total = sys.argv[1], sys.argv[2], int(sys.argv[3])
entornos = VecNormalize(make_vec_env(nombre, n_envs=4, seed=0))
ajustes = dict(seed=0)
if configuracion == "afinado":
    ajustes.update(n_steps=512, batch_size=64, learning_rate=3e-4,
                   policy_kwargs=dict(log_std_init=-1, net_arch=dict(pi=[256, 256], vf=[256, 256])))
agente = PPO("MlpPolicy", entornos, **ajustes)

examen = VecNormalize(make_vec_env(nombre, n_envs=1, seed=123), training=False, norm_reward=False)
inicio = time.time()
while agente.num_timesteps < total:
    agente.learn(100_352, reset_num_timesteps=False)          # un tramo
    examen.obs_rms = entornos.obs_rms
    nota, desviacion = evaluate_policy(agente, examen, n_eval_episodes=5, deterministic=True)
    print(nombre, configuracion, agente.num_timesteps, round(nota, 1), round(desviacion, 1), f"{time.time() - inicio:.0f}s")
    agente.save(f"{nombre}_{configuracion}")                   # el agente...
    entornos.save(f"{nombre}_{configuracion}_norm.pkl")        # ...y sus estadísticas: ¡las dos cosas!
