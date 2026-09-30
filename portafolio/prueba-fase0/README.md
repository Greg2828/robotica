# Prueba de salida · Fase 0 — Probar el plato entero

> Plantilla. Rellénala tú tras entrenar el humanoide G1 en Colab (ver NB02 · sección 7).
> Cuando la termines, esta carpeta —con los dos vídeos— es tu primera pieza de portafolio.

## Qué hice

Entrené el humanoide **G1JoystickFlatTerrain** en MuJoCo Playground (Colab, GPU) **dos
veces**, cambiando un único aspecto de la recompensa entre una y otra.

- **Vídeo A (recompensa por defecto):** `video_A.mp4` (o `.gif`)
- **Vídeo B (recompensa modificada):** `video_B.mp4`

## Qué cambié en la recompensa

*(Escribe aquí el peso que tocaste y a qué valor. Ej.: "subí ×3 el premio a la velocidad de
avance".)*

## Qué diferencia vi en el comportamiento

*(Describe con tus palabras cómo andaba en A y en B: más rápido pero inestable, más cauto,
se caía, hacía algo raro…)*

## Por qué creo que ocurrió

*(Usa el vocabulario de la fase: política, recompensa, retorno, proxy, reward hacking. ¿El
robot encontró algún atajo? ¿La recompensa premiaba algo que no era exactamente lo que
querías?)*

---

## Summary (English, for employers)

I trained the Unitree **G1** humanoid locomotion policy in MuJoCo Playground (PPO on a Colab
GPU) twice, changing one reward term between runs, and compared the resulting gaits. This
folder contains both videos and my analysis of how the reward change reshaped the learned
behavior — including whether the agent found a reward-hacking shortcut.

**Skills shown:** the full RL-for-robotics pipeline (environment, policy, reward, training,
evaluation), reward design and its failure modes, reproducible experiments with fixed seeds.
