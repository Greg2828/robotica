# Robótica: entrenar robots bípedos y humanoides — de cero a profesional

> Ruta de aprendizaje autodidacta, en castellano, para llegar a **entrenar políticas de
> control de robots bípedos y humanoides** (aprendizaje por refuerzo, simulación y paso de
> la simulación al robot real) a nivel de portafolio profesional, sin título de ingeniería.

Cada tema es un **notebook** (`.ipynb`) que se lee como un libro: primero el problema real
de robótica, luego la idea con un objeto cotidiano, después la notación y el código
comentado, un ejemplo que **sale mal** a propósito, y ejercicios resueltos. Las matemáticas
que hacen falta (vectores, derivadas, probabilidad, rotaciones…) se explican **desde cero**
dentro del propio material: no necesitas nada externo.

## Cómo está organizado

El temario sigue 8 fases, de lo más simple a lo más avanzado:

| Fase | Título | Idea en una línea |
|---|---|---|
| 0 | Probar el plato entero | Ver todo el proceso funcionando antes de estudiar las piezas. |
| 1 | Programación sólida | Que programar deje de ser un obstáculo (terminal, Git, Python, NumPy). |
| 2 | Redes neuronales | Cómo aprende una red, porque una política **es** una red. |
| 3 | Aprendizaje por refuerzo | La técnica con la que se entrenan los humanoides (hasta PPO propio). |
| 4 | El cuerpo del robot | La física que la política tiene que dominar (cinemática, dinámica, control PD). |
| 5 | Entrenar bípedos en simulación | El corazón: moldear el comportamiento de un humanoide (MuJoCo Playground). |
| 6 | Comportamientos avanzados | Imitación de movimiento, VLA, reproducir un artículo. |
| 7 | Hardware real | Cruzar la brecha simulación → robot físico (ROS 2, Raspberry Pi). |

Los notebooks están en `notebooks/`, numerados de forma continua (`NB00`, `NB01`, …), con
un prefijo de fase. Cada fase termina con una **prueba de salida** cuyo resultado se guarda
en `portafolio/`.

## Dónde se ejecuta cada cosa

- **Raspberry Pi 5 / portátil sin GPU (CPU):** fundamentos, MuJoCo en CPU, PyTorch en CPU,
  RL pequeño y control. Todos estos notebooks están **verificados** (se ejecutan de principio
  a fin sin error) en una Raspberry Pi 5 aarch64.
- **Google Colab (GPU gratuita):** entrenamiento pesado (miles de robots en paralelo con
  MJX/JAX, Isaac Lab). Esos notebooks llevan en la primera celda la instalación de sus
  dependencias y se abren directamente desde GitHub.

## Puesta en marcha (CPU, local)

```bash
cd robotica
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/fase0.txt
python -m jupyter notebook   # o abre los .ipynb en tu editor
```

## Estado

Consulta `PROGRESO.md` para ver por dónde va la ruta y cuál es el siguiente paso.

---

*Material de aprendizaje personal. El código de ejemplo es didáctico: prioriza la claridad
sobre el rendimiento.*
