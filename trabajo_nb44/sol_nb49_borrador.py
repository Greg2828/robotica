import json, functools
nb=json.load(open('NB49_integradores_y_rendimiento.ipynb')); ns={}
keep=('def aceleracion','PENDULO =','def angulo_final','MUELLE =','def zancudo_de_pie','import functools','class Cronometro','from contextlib','import timeit','import cProfile','from mujoco import rollout','import os')
for c in nb['cells']:
    if c['cell_type']!='code': continue
    src=''.join(c['source'])
    if any(src.lstrip().startswith(k) or k in src.split('\n')[0] for k in keep): exec(src, ns)
exec(r'''
import time, timeit, numpy as np, mujoco
res={}
for nombre, integ, dtmax in [("Euler",0,0.002),("implicitfast",3,0.02),("RK4",1,0.005)]:
    m=mujoco.MjModel.from_xml_path("robots/zancudo.xml"); m.opt.integrator=integ; m.opt.timestep=dtmax; d=mujoco.MjData(m)
    s=min(timeit.repeat(lambda: mujoco.mj_step(m,d), number=3000, repeat=3)); pps=3000/s
    print("E1",nombre, round(pps), "seg simulados por seg", round(pps*dtmax,1))
lo,hi=0.0005,0.05
for _ in range(25):
    mid=(lo+hi)/2
    if probar("Euler", dt=mid, k=1000)[0] < 1: lo=mid
    else: hi=mid
print("E2", lo, "2/omega", 2/np.sqrt(1000/(0.4**2/3)))
for g in [1.62, 9.81, 24.8]:
    z=mujoco.MjModel.from_xml_path("robots/zancudo.xml")
    with opciones(z, gravity=np.array([0,0,-g])):
        d=mujoco.MjData(z)
        for k in range(500): mujoco.mj_step(z,d)
        mujoco.mj_forward(z,d); mujoco.mj_rnePostConstraint(z,d)
        f=d.body("pie_d").cfrc_ext[5]+d.body("pie_i").cfrc_ext[5]
        print("E4", g, round(f,2), "peso", round(23.6*g,2), "altura", round(0.865+d.qpos[1],3))
z=mujoco.MjModel.from_xml_path("robots/zancudo.xml"); rng=np.random.default_rng(0)
ordenes=rng.uniform(-0.5,0.5,(1000,z.nu))
S=mujoco.mjtState.mjSTATE_FULLPHYSICS; d=mujoco.MjData(z); ini=np.zeros(mujoco.mj_stateSize(z,S)); mujoco.mj_getState(z,d,ini,S)
for k in range(1000): d.ctrl[:]=ordenes[k]; mujoco.mj_step(z,d)
fin=np.zeros_like(ini); mujoco.mj_getState(z,d,fin,S)
est,_=rollout.rollout(z,[mujoco.MjData(z)],ini[None,:],ordenes[None,:,:])
print("E5", np.array_equal(est[0,-1],fin), np.abs(est[0,-1]-fin).max())
''', ns)
import mujoco, numpy as np, time
from concurrent.futures import ProcessPoolExecutor
def cae(fuerza, segundos=3.0):
    m=mujoco.MjModel.from_xml_path("robots/zancudo.xml"); d=mujoco.MjData(m); t=m.body("torso").id
    for k in range(int(segundos/m.opt.timestep)):
        d.xfrc_applied[t,0]=fuerza; mujoco.mj_step(m,d)
    return 0.865+d.qpos[1] < 0.8
fs=list(range(10,21))
t=time.perf_counter(); r1=[cae(f) for f in fs]; t1=time.perf_counter()-t
t=time.perf_counter()
with ProcessPoolExecutor(4) as ex: r4=list(ex.map(cae, fs))
t4=time.perf_counter()-t
print("E6", r1==r4, list(zip(fs,r4)), round(t1,2), round(t4,2))
