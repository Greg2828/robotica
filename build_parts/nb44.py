"""Construye NB44 · Moldear la recompensa: andar bonito (Parte 6 · Lección 1).

Abre la Parte 6 (bípedos de verdad). El Zancudo del NB43 corre a lo bruto (más
de 4 m/s, patadas de 0,9 m, la mitad del tiempo en el aire): cumple la
recompensa, no lo que queríamos. Moldear la recompensa: términos y pesos, y sus
peligros (cada término es una trampa nueva, Goodhart). El núcleo exponencial
(campana) para SEGUIR un objetivo en vez de maximizar. Los cinco términos de
ZancudoMoldeado (velocidad objetivo 1 m/s, torso recto, no volar, no dar
patadas, suavidad), leídos con inspect; contactos pie-suelo. Cuentas: quieto
vs andar. Estudio de ablación con 4 entrenamientos (completa, sin_vuelo,
sin_pie_alto, lento): velocidad, tiempo en el aire, altura de los pies,
suavidad, GIFs. Lecciones: lo que se mide se consigue; ablación; pesos.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB44 · Moldear la recompensa: andar bonito

**Parte 6 · Bípedos de verdad — Lección 1**

> En el **NB43** Zancudo aprendió a moverse hacia delante... a su manera. Su recompensa decía "avanza todo lo que puedas sin caerte", y eso hizo: **corre** a más de 4 m/s, a grandes zancadas, con patadas en las que el pie sube casi un metro y pasando más de la mitad del tiempo **en el aire**.

Empieza la **Parte 6 · Bípedos de verdad**, y empieza por el problema que destapó el NB43: el agente hace **lo que le pagas**, no lo que quieres (NB04, NB35). Si queremos un robot que **ande** (que no corra), a una velocidad **razonable**, con el torso **recto**, sin **patadas** y con movimientos **suaves** (para no romper sus motores, NB40), hay que **decírselo** en la recompensa.

A eso se le llama **moldear la recompensa** (*reward shaping*), y es, probablemente, la parte del trabajo de un ingeniero de locomoción que más horas se come. Hoy vamos a moldear la de Zancudo con cinco términos, a entrenarla, y a hacer un **estudio de ablación** (quitar los términos uno a uno) para ver qué hace cada pieza.
"""),

md(r"""## 1 · Por qué corría

Recuerda la recompensa del NB43:

```
   recompensa  =  velocidad hacia delante  +  1  −  0,01 × acciones²
```

Cada metro por segundo de más es un punto más **en cada paso**. No hay ningún límite: a 4 m/s se cobran 5 puntos por paso, a 2 m/s solo 3. Así que PPO buscó la forma de ir **lo más rápido posible**, y la encontró: correr a saltos. Nada en la recompensa dice "no corras", ni "no levantes el pie un metro", ni "no vayas a tirones".

Es el **reward hacking** del NB04 en estado puro, aunque esta vez el "hackeo" sea casi admirable: un robot plano de 23 kg que corre a 15 km/h. Pero un robot **real** que corriera así se rompería: los aterrizajes de cada salto golpean los motores (NB40), las patadas gastan muchísima energía (y calientan los motores, NB40), y depender de pasar media vida en el aire hace que cualquier diferencia entre la simulación y la realidad lo tire al suelo (el reality gap, NB02).
"""),

md(r"""## 2 · Moldear: añadir términos, con cuidado

Moldear la recompensa es **añadir términos** que premian lo que queremos y castigan lo que no, cada uno con su **peso** (cuánto importa):

```
   recompensa  =  peso₁ × término₁  +  peso₂ × término₂  +  ...  −  pesoₖ × castigoₖ  −  ...
```

Suena fácil, pero tiene tres peligros, y los tres los vas a ver hoy:

1. **Cada término nuevo es una trampa nueva** (la ley de **Goodhart** del NB04: "cuando una medida se convierte en objetivo, deja de ser una buena medida"). Si castigas "levantar el pie más de 15 cm", quizá aprenda a arrastrar los pies. Si castigas "estar en el aire", quizá aprenda a dar pasitos ridículos.
2. **Los pesos importan muchísimo.** Un castigo demasiado fuerte y el robot prefiere no moverse; demasiado débil, y lo ignora. Encontrar los pesos es, a menudo, prueba y error.
3. **La trampa de sobrevivir** (NB35) sigue ahí: si quedarse quieto paga más que intentar andar con todos los castigos, se quedará quieto.

Por eso, después de moldear hay que **mirar** (los GIF, no solo la nota) y **medir** cada cosa que queríamos conseguir.
"""),

md(r"""## 3 · Seguir un objetivo: la campana

La primera idea es la más importante: no queremos "la velocidad **máxima**", sino "**1 m/s**". El término de velocidad del NB43 (cobrar la velocidad tal cual) premia ir siempre más rápido. Necesitamos un término que valga **lo máximo justo en 1 m/s** y **menos** cuanto más nos alejemos, por arriba o por abajo.

La herramienta que usa todo el mundo es la **campana** del NB28, en forma de **núcleo exponencial**:

```
   término de velocidad  =  e^( −(velocidad − objetivo)² / 0,25 )
```

- Si la velocidad es **justo** el objetivo, la diferencia es 0, y e⁰ = **1**: el máximo.
- Si se aleja, la diferencia al cuadrado crece, el exponente se hace muy negativo, y el término cae hacia **0**.
- El 0,25 (el "ancho" de la campana) decide **cuánto** se tolera: aquí, alejarse medio metro por segundo ya baja el premio a e⁻¹ ≈ 0,37.

Dibujémoslo, junto al término del NB43:
"""),

code(r"""import os
os.environ["MUJOCO_GL"] = "egl"
import numpy as np
import matplotlib.pyplot as plt

velocidades = np.linspace(-1, 4, 200)
plt.figure(figsize=(7, 3.5))
plt.plot(velocidades, velocidades, label="NB43: la velocidad tal cual (sin techo)")
plt.plot(velocidades, np.exp(-(velocidades - 1.0) ** 2 / 0.25), lw=2, label="NB44: campana alrededor de 1 m/s")
plt.axvline(1.0, color="gray", ls="--", lw=1)
plt.ylim(-1, 4)
plt.xlabel("velocidad (m/s)")
plt.ylabel("premio por paso")
plt.legend()
plt.grid(alpha=0.3)
plt.show()"""),

md(r"""Con la campana, correr a 4 m/s ya no paga **nada** (e^(−9 / 0,25) ≈ 0), y quedarse quieto tampoco (e^(−1 / 0,25) ≈ 0,02). Lo que más paga es ir **justo** a 1 m/s. Este truco (premiar con una campana la cercanía a un objetivo) es el que usan casi todos los entornos de robots con patas modernos para que **sigan órdenes** de velocidad, como veremos en el NB46. Y vale para cualquier cosa que queramos **mantener cerca** de un valor: una altura, una inclinación, un ángulo...
"""),

md(r"""## 4 · Los cinco términos de Zancudo

El entorno con la recompensa moldeada está en `zancudo_moldeado.py`. Es una **subclase** de `Zancudo` (la herencia del NB25): lo hereda **todo** (el robot, la observación, la acción, las caídas) y solo cambia la recompensa. Leamos su `step` con `inspect` (NB43):
"""),

code(r"""import inspect
import gymnasium as gym
import zancudo_moldeado
from zancudo_moldeado import ZancudoMoldeado

print(inspect.getsource(ZancudoMoldeado.step))"""),

md(r"""Primero llama al `step` de su madre con `super().step(accion)` (NB25): así el robot se mueve exactamente igual que en el NB43, y nos quedamos con su observación, sus caídas y su `info`, pero **tiramos** su recompensa (el `_`). Después calcula cinco términos:

| Término | Qué mide | Tipo | Peso |
|---|---|---|---|
| **velocidad** | cercanía a 1 m/s (campana) | premio, de 0 a 1 | 1,0 |
| **recto** | cercanía del torso a la vertical (campana) | premio, de 0 a 1 | 0,3 |
| **vida** | seguir vivo | premio fijo | 0,2 |
| **vuelo** | 1 si **ningún** pie toca el suelo | castigo | 0,5 |
| **pie_alto** | cuánto pasan los pies de 15 cm de altura | castigo | 2,0 |
| **suavidad** | cuánto cambia la acción respecto de la anterior (al cuadrado) | castigo | 0,05 |

Algunos detalles:

- **Vuelo**: queremos **andar**, y andar es, por definición, tener siempre al menos un pie en el suelo (correr es justo lo contrario: hay fases en el aire, NB35). Para saber qué pie toca el suelo, mira la lista de **contactos** de MuJoCo, como en el NB41:
"""),

code(r"""print(inspect.getsource(ZancudoMoldeado.pies_en_el_suelo))"""),

md(r"""- **Pie alto**: los pies pueden subir hasta 15 cm sin castigo (lo necesario para no tropezar). Lo que pase de ahí, se castiga: adiós a las patadas de 90 cm.
- **Suavidad**: compara la acción de ahora con la de la decisión anterior. Un robot que cambia de golpe sus ángulos objetivo a cada decisión pega **tirones** a sus motores (y en el mundo real, eso hace vibrar la estructura y calienta los motores, NB40). Este término es uno de los más usados en robots reales.
- La **vida** ahora vale 0,2 (antes, 1): ya no queremos que sobrevivir sea lo principal.

¿Le sale a cuenta quedarse quieto? Hagamos las cuentas por paso (sin castigos, en el mejor de los casos):

- **Quieto y recto**: velocidad ≈ 0,02 + recto 0,3 + vida 0,2 ≈ **0,52** por paso → unos **520** puntos en los 1.000 pasos.
- **Andando a 1 m/s, recto**: 1 + 0,3 + 0,2 = **1,5** por paso → **1.500** puntos.

Andar paga el triple. La trampa de sobrevivir está desactivada... sobre el papel. Comprobemos las políticas de referencia:
"""),

code(r"""from gymnasium.utils.env_checker import check_env
check_env(ZancudoMoldeado())

moldeado = gym.make("ZancudoMoldeado-v0")

def jugar_episodios(entorno, politica, n=5):
    retornos, duraciones, distancias = [], [], []
    for semilla in range(n):
        observacion, info = entorno.reset(seed=semilla)
        retorno, pasos = 0.0, 0
        while True:
            observacion, recompensa, terminado, truncado, info = entorno.step(politica(observacion))
            retorno += recompensa
            pasos += 1
            if terminado or truncado:
                break
        retornos.append(retorno)
        duraciones.append(pasos)
        distancias.append(info["x"])
    return np.mean(retornos), np.mean(duraciones), np.mean(distancias)

for nombre, politica in [("quieto", lambda obs: np.zeros(6)), ("azar", lambda obs: moldeado.action_space.sample())]:
    r, d, x = jugar_episodios(moldeado, politica)
    print(f"{nombre:>6}: retorno {r:6.1f} | dura {d:6.1f} pasos | acaba en x = {x:+.2f} m")"""),

md(r"""RESULTADO_REFERENCIAS_44
"""),

md(r"""## 5 · El estudio de ablación

¿Hace falta cada uno de los términos? La forma científica de saberlo es un **estudio de ablación** ("ablación" viene de quitar, extirpar): entrenar con **todos** los términos, y después repetir **quitando** uno (o un grupo) cada vez. Si al quitar un término el robot empeora justo en lo que ese término vigilaba, es que hacía falta. Es lo que se hace en cualquier artículo de investigación serio, y lo que te van a preguntar en una entrevista de trabajo: "¿y cómo sabes que ese término sirve para algo?".

Entrené cuatro variantes con el script `entrenar_moldeado.py` (junto a este notebook), PPO con los ajustes por defecto y `VecNormalize`, cuatro a la vez en la Pi, como en el NB43:

| Variante | Qué cambia |
|---|---|
| `completa` | los cinco términos, objetivo 1 m/s |
| `sin_vuelo` | sin el castigo por tener los dos pies en el aire |
| `sin_pie_alto` | sin los castigos de pie alto ni de suavidad |
| `lento` | completa, pero pidiendo **0,5 m/s** |

Sus registros (pasos, nota, desviación, distancia en los 20 s, duración media del episodio en pasos):
"""),

code(r"""REGISTRO_44"""),

md(r"""ANALISIS_44
"""),

md(r"""## 6 · Midiendo el "bonito"

La nota no basta: cada variante cobra con una recompensa distinta, así que sus notas no se pueden comparar. Lo que hay que comparar es **lo que queríamos conseguir**. Una función que juega un episodio con un agente y mide cinco cosas: la **velocidad** media, el **porcentaje del tiempo en el aire** (los dos pies sin tocar el suelo), la **altura máxima** de los pies, la **inclinación** media del torso (en valor absoluto) y el **cambio** medio de la acción entre decisiones (la suavidad):
"""),

code(r"""from pathlib import Path
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize
import mujoco

MODELOS = Path("modelos")

def cargar(nombre, entorno_id="ZancudoMoldeado-v0", **kwargs):
    agente = PPO.load(MODELOS / nombre)
    normalizador = VecNormalize.load(MODELOS / f"{nombre}_norm.pkl", make_vec_env(entorno_id, n_envs=1, env_kwargs=kwargs))
    normalizador.training = False
    return lambda obs: agente.predict(normalizador.normalize_obs(obs), deterministic=True)[0]

def medir_forma(politica, semilla=0, pasos=500):
    entorno = ZancudoMoldeado()                          # lo usamos solo para medir: no importa su recompensa
    observacion, info = entorno.reset(seed=semilla)
    aire, alturas, inclinaciones, cambios, anterior = [], [], [], [], np.zeros(6)
    x0 = entorno.datos.qpos[0]
    for paso in range(pasos):
        accion = politica(observacion)
        observacion, recompensa, terminado, truncado, info = entorno.step(accion)
        aire.append(not any(entorno.pies_en_el_suelo()))
        alturas.append(max(entorno.datos.geom_xpos[pie][2] for pie in entorno.pies))
        inclinaciones.append(abs(entorno.datos.qpos[2]))
        cambios.append(np.sum((np.clip(accion, -1, 1) - anterior) ** 2))
        anterior = np.clip(accion, -1, 1)
        if terminado:
            break
    t = (paso + 1) * 0.02
    return dict(velocidad=(entorno.datos.qpos[0] - x0) / t, aire=100 * np.mean(aire), pie_max=max(alturas),
                inclinacion=np.mean(inclinaciones), cambio=np.mean(cambios), segundos=t)"""),

code(r"""import zancudo_env

agentes = {
    "NB43 (sin moldear)": cargar("MEJOR_NB43", "Zancudo-v0"),
    "completa": cargar("moldeado_completa_mejor"),
    "sin_vuelo": cargar("moldeado_sin_vuelo_mejor"),
    "sin_pie_alto": cargar("moldeado_sin_pie_alto_mejor"),
    "lento": cargar("moldeado_lento_mejor", velocidad_objetivo=0.5),
}
print(f"{'agente':>20} | {'vel. (m/s)':>10} | {'% en el aire':>12} | {'pie más alto (m)':>16} | {'inclinación':>11} | {'tirones':>7} | {'dura (s)':>8}")
for nombre, politica in agentes.items():
    m = medir_forma(politica)
    print(f"{nombre:>20} | {m['velocidad']:10.2f} | {m['aire']:12.1f} | {m['pie_max']:16.2f} | {m['inclinacion']:11.3f} | {m['cambio']:7.2f} | {m['segundos']:8.1f}")"""),

md(r"""ANALISIS_FORMA
"""),

md(r"""## 7 · Verlo

Los números dicen mucho, pero en locomoción **hay que mirar**. Grabamos un GIF de cada uno, con la misma función del NB43:"""),

code(r"""import imageio
from IPython.display import Image, display

def grabar(politica, ruta, pasos=250, cada=2, semilla=0):
    camara = ZancudoMoldeado(render_mode="rgb_array")
    observacion, info = camara.reset(seed=semilla)
    fotos = []
    for paso in range(pasos):
        observacion, recompensa, terminado, truncado, info = camara.step(politica(observacion))
        if paso % cada == 0:
            fotos.append(camara.render())
        if terminado or truncado:
            break
    camara.close()
    imageio.mimsave(ruta, fotos, fps=round(1 / (0.02 * cada)), loop=0)

os.makedirs("assets", exist_ok=True)
grabar(agentes["completa"], "assets/nb44_completa.gif")
display(Image(filename="assets/nb44_completa.gif"))"""),

md(r"""GIF_COMPLETA
"""),

code(r"""grabar(agentes["sin_vuelo"], "assets/nb44_sin_vuelo.gif")
display(Image(filename="assets/nb44_sin_vuelo.gif"))"""),

md(r"""GIF_SIN_VUELO
"""),

md(r"""## 8 · Lo que nos llevamos

LECCIONES_44
"""),

md(r"""## 9 · Resumen de la lección

RESUMEN_44

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Moldear la recompensa (*reward shaping*)** | Añadir términos y pesos a la recompensa para conseguir un comportamiento concreto. |
| **Término / peso** | Cada pieza de la recompensa / cuánto cuenta. |
| **Núcleo exponencial (campana)** | e^(−diferencia² / ancho): vale 1 en el objetivo y cae al alejarse. |
| **Seguir (*tracking*) un objetivo** | Premiar la cercanía a un valor pedido, no el máximo. |
| **Castigo por tirones (*action rate*)** | Castigar el cambio de la acción entre decisiones seguidas. |
| **Estudio de ablación** | Quitar piezas una a una para ver qué aporta cada una. |
| **Andar / correr** | Siempre al menos un pie en el suelo / con fases en el aire. |
"""),

md(r"""## 10 · Ejercicios

EJERCICIOS_44
"""),

md(r"""## 11 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Zancudo ya anda a la velocidad que le pedimos. Pero en el NB41 vimos lo frágiles que son las políticas entrenadas en un mundo perfecto, y en el NB43, cómo sufrían con los empujones. En el **NB45** lo haremos **robusto**: lo entrenaremos en mundos que cambian (masas distintas, suelos más o menos resbaladizos, motores más flojos, sensores con ruido y retraso) y recibiendo **empujones** mientras aprende. Es la **aleatorización de dominio** (NB02), la técnica que más ha hecho por llevar robots de la simulación a la realidad.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB44_moldear_la_recompensa.ipynb")
    build(out, cells, title="NB44 · Moldear la recompensa: andar bonito")
