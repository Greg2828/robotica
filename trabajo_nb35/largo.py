import sys, time, numpy as np, torch
torch.set_num_threads(1)
import gymnasium as gym
from torch import nn
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
from stable_baselines3.common.evaluation import evaluate_policy
nombre, cfg, total = sys.argv[1], sys.argv[2], int(sys.argv[3])
venv = VecNormalize(make_vec_env(nombre, n_envs=4, seed=0))
kw = dict(seed=0)
if cfg == "afinado":
    kw.update(n_steps=512, batch_size=64, learning_rate=3e-4, policy_kwargs=dict(log_std_init=-1, net_arch=dict(pi=[256,256], vf=[256,256])))
m = PPO("MlpPolicy", venv, **kw)
ev = VecNormalize(make_vec_env(nombre, n_envs=1, seed=123), training=False, norm_reward=False)
t=time.time(); bloque=100_352
while m.num_timesteps < total:
    m.learn(bloque, reset_num_timesteps=False)
    ev.obs_rms = venv.obs_rms
    r,s = evaluate_policy(m, ev, n_eval_episodes=5, deterministic=True)
    print(nombre,cfg,m.num_timesteps, round(r,1), round(s,1), f"{time.time()-t:.0f}s", flush=True)
    m.save(f"{nombre}_{cfg}"); venv.save(f"{nombre}_{cfg}_norm.pkl")
