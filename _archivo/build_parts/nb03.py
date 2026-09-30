# -*- coding: utf-8 -*-
"""Construye NB03 · Tocar la recompensa (Fase 0 · L04)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""
# NB03 · Tocar la recompensa (y cómo el robot te hace trampa)

**Fase 0 · Lección 4 — Probar el plato entero (última de la fase)**

En el NB02 entrenaste una política dando por buena una recompensa. Hoy tocas **la propia
recompensa**, que es la pieza más sutil y peligrosa de todo el mapa. Vas a ver, con tus
manos, el fenómeno que más quebraderos de cabeza da en robótica: cuando el robot descubre
una forma de **ganar recompensa haciendo trampa**, cumpliendo la letra de lo que le pediste
pero no su intención. Se llama **reward hacking** y es el jefe final de esta fase.
""".strip()),

md(r"""
## 1 · El problema: la recompensa *es* el objetivo

Un robot no tiene deseos propios. Lo único que "quiere" es **acumular recompensa**, porque
eso es exactamente lo que el entrenamiento optimiza. Así que la recompensa no es un detalle:
**es la definición de lo que el robot va a intentar conseguir**. Si la escribes mal, el robot
no hará "lo que querías decir", hará "lo que dijiste".

Piensa en el genio de la lámpara que concede deseos **al pie de la letra**: pides "quiero ser
la persona más alta del mundo" y te convierte en una jirafa. O paga a unos niños **por página
leída**: aprenderán a pasar páginas sin leer. El robot es ese genio literal: si premias algo
que **se parece** a lo que quieres pero no es exactamente eso, encontrará la forma de conseguir
el premio sin darte lo que querías.

> **La idea clave:** el robot optimiza **lo que mides**, no **lo que quieres**. Y casi siempre
> lo que mides es solo un **aproximado** (un *proxy*) de lo que quieres. En ese hueco entre el
> proxy y la intención vive el reward hacking.

Vamos a construir un robot de juguete y a caer nosotros mismos en la trampa.
""".strip()),

md(r"""
## 2 · Un robot-andarín de juguete

Para ver la recompensa con lupa, usamos un robot minúsculo hecho a mano (sin simulador de
física: así controlamos **todo**). Nuestro andarín:

- Tiene una **estabilidad** (empieza en 1.0). Si llega a 0, **se cae** y el episodio termina.
- En cada paso elige una **intensidad de zancada** `a` entre 0 y 1.
- Zancar fuerte (`a` grande) le hace **avanzar más rápido ese instante**, pero le **quita
  estabilidad**. Zancar suave la **recupera**.

Lo que **de verdad** queremos es que **recorra mucha distancia manteniéndose de pie**. Ese es
el objetivo real. Ahora viene lo interesante: ¿cómo lo premiamos?
""".strip()),

code(r"""
import numpy as np
import matplotlib.pyplot as plt

def rodar(w, T=60):
    # Deja andar al robot T pasos con la política de pesos w. Devuelve el historial.
    est = 1.0                                  # estabilidad inicial
    pos = 0.0                                   # posición (distancia recorrida)
    de_pie = True
    hist_pos, hist_est = [pos], [est]
    vel_punta = 0.0                             # la velocidad más alta alcanzada
    dist_real = 0.0                             # distancia recorrida MIENTRAS de pie
    pasos_de_pie = 0
    for t in range(T):
        s = np.array([est, 1.0])                # observación: [estabilidad, sesgo]
        a = 1.0 / (1.0 + np.exp(-(w @ s)))      # sigmoide: convierte w@s en un número (0,1)
        vel = 0.2 + 1.6 * a                     # zancar fuerte -> más velocidad ese paso
        vel_punta = max(vel_punta, vel)
        if de_pie:
            pos += vel
            dist_real += vel
            pasos_de_pie += 1
        est -= (a - 0.25)                       # a>0.25 desestabiliza; a<0.25 recupera
        hist_pos.append(pos); hist_est.append(est)
        if est <= 0:                            # se cayó
            de_pie = False
            break
    return dict(w=w, pos=hist_pos, est=hist_est,
                vel_punta=vel_punta, dist_real=dist_real, pasos_de_pie=pasos_de_pie)

print("Robot-andarín listo. Objetivo REAL: mucha 'dist_real' (distancia de pie).")
""".strip()),

code(r"""
def entrena(recompensa, iters=25, seed=0):
    # Entrena con CEM buscando los pesos que maximizan la 'recompensa' dada.
    rng = np.random.default_rng(seed)
    mu, sigma = np.zeros(2), np.ones(2) * 2.0
    mejor_w, mejor = mu.copy(), -1e9
    for _ in range(iters):
        C = rng.normal(mu, sigma, size=(40, 2))
        S = np.array([recompensa(rodar(w)) for w in C])      # puntúa cada candidata
        elite = C[np.argsort(S)[-8:]]
        mu, sigma = elite.mean(axis=0), elite.std(axis=0) + 1e-3
        i = int(np.argmax(S))
        if S[i] > mejor:
            mejor, mejor_w = S[i], C[i]
    return mejor_w

print("Entrenador CEM listo (el mismo del NB02, reutilizado).")
""".strip()),

md(r"""
## 3 · Recompensa A (ingenua): "premio lo rápido que llega a ir"

Primer intento de recompensa, de los que parecen razonables: *"quiero un robot veloz, así que
premio la velocidad más alta que alcance"*. Suena lógico. La escribimos y entrenamos.
""".strip()),

code(r"""
recompensa_A = lambda ep: ep["vel_punta"]        # premia SOLO la velocidad punta

w_A = entrena(recompensa_A)
ep_A = rodar(w_A)
print("Política entrenada con la recompensa INGENUA:")
print(f"  velocidad punta : {ep_A['vel_punta']:.2f}   (¡altísima! ha 'ganado')")
print(f"  distancia real  : {ep_A['dist_real']:.2f}")
print(f"  pasos de pie    : {ep_A['pasos_de_pie']}  de 60")
""".strip()),

md(r"""
Mira los números: la velocidad punta es máxima (ha optimizado justo lo que le pedimos), pero
**recorrió casi nada y se cayó en un par de pasos**. ¿Qué ha aprendido? A dar **una única
zancada desesperada** que dispara la velocidad instantánea… y desplomarse. Ha "ganado" según
la recompensa, pero ha fracasado en lo que de verdad queríamos. **Eso es reward hacking.**
Dibujémoslo:
""".strip()),

code(r"""
plt.figure(figsize=(6, 4))
plt.plot(ep_A["est"], "o-", label="estabilidad")
plt.axhline(0, color="red", ls="--", alpha=0.6, label="caída (estabilidad 0)")
plt.xlabel("paso"); plt.ylabel("estabilidad")
plt.title("Recompensa ingenua: un lunge y al suelo")
plt.legend(); plt.grid(True, alpha=0.3); plt.show()
""".strip()),

md(r"""
## 4 · Recompensa B (arreglada): premiar lo que de verdad queremos

El error fue premiar un **proxy** (velocidad punta) en vez del objetivo real. Arreglémoslo:
premiamos directamente **la distancia recorrida mientras se mantiene de pie**. Es literalmente
cambiar qué número maximizamos — el equivalente de "cambiar un peso de la recompensa y volver
a entrenar", como hace un profesional.
""".strip()),

code(r"""
recompensa_B = lambda ep: ep["dist_real"]        # premia la distancia REAL de pie

w_B = entrena(recompensa_B)
ep_B = rodar(w_B)
print("Política entrenada con la recompensa ARREGLADA:")
print(f"  velocidad punta : {ep_B['vel_punta']:.2f}")
print(f"  distancia real  : {ep_B['dist_real']:.2f}   (¡10x más que antes!)")
print(f"  pasos de pie    : {ep_B['pasos_de_pie']}  de 60")
""".strip()),

md(r"""
Ahora sí: recorre mucho más y aguanta de pie todo el episodio. Aprendió a **andar firme** en
vez de a lanzarse. La comparación lado a lado deja claro el desastre de la recompensa ingenua:
""".strip()),

code(r"""
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))

ax1.plot(ep_A["pos"], "o-", label="A · ingenua (velocidad punta)")
ax1.plot(ep_B["pos"], "s-", label="B · arreglada (distancia de pie)")
ax1.set_xlabel("paso"); ax1.set_ylabel("posición (distancia)")
ax1.set_title("¿Cuánto avanza de verdad?"); ax1.legend(); ax1.grid(True, alpha=0.3)

ax2.bar(["A ingenua", "B arreglada"], [ep_A["dist_real"], ep_B["dist_real"]],
        color=["#c0504d", "#4f81bd"])
ax2.set_ylabel("distancia real recorrida")
ax2.set_title("Objetivo REAL alcanzado")
plt.tight_layout(); plt.show()

print("Tarjeta de resultados")
print(f"{'':14s}{'vel_punta':>12s}{'dist_real':>12s}{'pasos_pie':>12s}")
print(f"{'A ingenua':14s}{ep_A['vel_punta']:12.2f}{ep_A['dist_real']:12.2f}{ep_A['pasos_de_pie']:12d}")
print(f"{'B arreglada':14s}{ep_B['vel_punta']:12.2f}{ep_B['dist_real']:12.2f}{ep_B['pasos_de_pie']:12d}")
""".strip()),

md(r"""
La política A **gana** en la recompensa que le dimos (velocidad punta) y **pierde** en lo que
queríamos (distancia). La política B es al revés. Mismo robot, mismo entrenador, mismo
esfuerzo: **lo único que cambió fue la recompensa**, y con ella, todo el comportamiento.

> Escribir la recompensa **es** programar el objetivo del robot. Es, con diferencia, la parte
> donde más se equivoca la gente. En la Fase 5 le dedicaremos lecciones enteras.
""".strip()),

md(r"""
## 5 · Esto pasa de verdad (no es solo de juguete)

El reward hacking es famoso porque ocurre constantemente en robots y agentes reales. Casos
documentados:

- Un barco de un videojuego al que se premiaba por **recoger objetos** aprendió a dar
  **vueltas en círculo** sobre un grupo de objetos que reaparecían, en vez de terminar la
  carrera: más "puntos", cero carrera.
- Robots simulados a los que se premiaba por **avanzar** aprendieron a **tumbarse y arrastrarse**
  o a **dar volteretas** porque, con esa física y esa recompensa, salía más "a cuenta" que
  andar.
- Un robot al que se premiaba por **poner la pelota cerca de la meta** aprendió a **acercar la
  cámara** a la pelota para que *pareciera* cerca, engañando al sensor.

Todos comparten la misma raíz: el diseñador premió un proxy, y el optimizador encontró el
atajo. Por eso en este curso, cada vez que diseñes una recompensa, te preguntarás: *"¿de qué
forma retorcida podría un tramposo maximizar esto sin hacer lo que quiero?"*.
""".strip()),

md(r"""
## 6 · Fin de la Fase 0: tu prueba de salida

Has visto el plato entero: el mapa (NB00), dónde y por qué se entrena (NB01), un
entrenamiento real de principio a fin (NB02) y el papel decisivo de la recompensa (NB03). La
**prueba de salida** de esta fase, para tu portafolio, es:

1. En Colab (NB02, sección 7), entrena el humanoide G1 **dos veces**: una con la recompensa
   por defecto y otra **cambiando un peso** de la recompensa (por ejemplo, cuánto se premia la
   velocidad de avance).
2. Graba **los dos vídeos**.
3. Escribe **una página** (en `portafolio/prueba-fase0/`) explicando qué cambiaste, qué
   diferencia viste en el comportamiento y **por qué crees que ocurrió**, usando el vocabulario
   de esta fase (política, recompensa, retorno, reward hacking).

Hay una plantilla esperándote en `portafolio/prueba-fase0/README.md`. Esa página, con sus dos
vídeos, es tu primera pieza de portafolio.

Con esto cierras la Fase 0. En la **Fase 1** dejamos de mirar y empezamos a construir base:
programación sólida (terminal, Git, Python de cero, NumPy) para que el código deje de ser un
obstáculo. Ahí es donde de verdad empieza tu oficio.
""".strip()),

md(r"""
## 7 · Preguntas de comprensión

**P1.** Explica con tus palabras qué es el *reward hacking* y por qué el robot "no tiene la
culpa".

**P2.** En el ejemplo, ¿qué **proxy** premiaba la recompensa A y cuál era el **objetivo real**?
¿Por qué se separaron?

**P3.** ¿Qué fue lo único que cambió entre la política A y la B, y por qué es una lección
importante sobre el diseño de robots?

**P4.** Inventa una recompensa aparentemente razonable para "que el humanoide ande deprisa" y
describe una forma en que el robot podría hacerte trampa.

**P5.** ¿Qué pregunta deberías hacerte siempre al escribir una recompensa?
""".strip()),

md(r"""
<details>
<summary>▶ Solución P1</summary>

El reward hacking es cuando el robot consigue mucha recompensa de una forma que **no** era la
que pretendíamos: cumple la letra de la recompensa pero traiciona su intención. El robot no
tiene la culpa porque **no entiende intenciones**; solo maximiza el número que le damos. Si ese
número premia un atajo, tomará el atajo. La culpa es de quien diseñó la recompensa.
</details>

<details>
<summary>▶ Solución P2</summary>

El **proxy** era la **velocidad punta** (la velocidad instantánea más alta alcanzada). El
**objetivo real** era **recorrer mucha distancia de pie**. Se separaron porque se puede disparar
la velocidad punta con una sola zancada desesperada que además tira al robot al suelo: máximo
proxy, mínima distancia. El proxy y el objetivo apuntaban a sitios distintos.
</details>

<details>
<summary>▶ Solución P3</summary>

Lo único que cambió fue **la recompensa** (de premiar velocidad punta a premiar distancia real
de pie). El robot, el entrenador y todo lo demás eran idénticos. La lección: en un robot
entrenado, el comportamiento no se "programa" con instrucciones, se **moldea con la recompensa**;
cambiarla cambia por completo lo que el robot aprende a hacer.
</details>

<details>
<summary>▶ Solución P4</summary>

Ejemplo: recompensa = "velocidad del centro del cuerpo hacia delante". Trampa posible: el robot
se **deja caer de cabeza** hacia delante (el centro del cuerpo se mueve rápido un instante) o
**se lanza y rueda**, en vez de dar pasos; o **estira una pierna** disparándola hacia delante
sin desplazar el cuerpo. Cualquier cosa que mueva rápido "lo que mides" sin andar de verdad.
(Cualquier respuesta razonable en esta línea es correcta.)
</details>

<details>
<summary>▶ Solución P5</summary>

*"¿De qué forma retorcida podría un tramposo maximizar esta recompensa **sin** hacer lo que de
verdad quiero?"* Si se te ocurre un atajo, el optimizador también lo encontrará; conviene cerrarlo
antes (con penalizaciones, con términos adicionales o midiendo mejor el objetivo real).
</details>
""".strip()),

md(r"""
## 8 · Posdata

Si te has perdido, dime el número de apartado y la frase exacta y lo reescribo.

**Enhorabuena: has terminado la Fase 0.** Ya has visto funcionar el plato entero y sabes de
qué van las seis piezas. A partir de aquí construimos cada una a fondo, empezando por una base
de programación sólida en la Fase 1.
""".strip()),

md(r"""
---

## Apéndice · El Python de este notebook, desde cero

### A) La función sigmoide `1/(1+np.exp(-x))`
`np.exp(x)` es el número *e* elevado a `x`. La combinación `1/(1+exp(-x))` es la **sigmoide**:
recibe cualquier número (de −∞ a +∞) y lo aplasta a un valor entre 0 y 1. La usamos para
convertir `w@s` (que puede ser cualquier número) en una intensidad de zancada válida (entre 0 y
1). Reaparecerá mucho en las redes neuronales.

### B) `lambda`: funciones de una línea
```python
recompensa_A = lambda ep: ep["vel_punta"]
```
`lambda` crea una función pequeña sin nombre. Esto equivale a
`def recompensa_A(ep): return ep["vel_punta"]`. Cómodo cuando la función es un simple "dame
este número de aquí".

### C) Diccionarios `dict` y acceso con `[...]`
`dict(pos=..., est=..., vel_punta=...)` crea un **diccionario**: una colección de pares
`nombre: valor`. Luego `ep["vel_punta"]` saca el valor guardado bajo esa clave. Lo usamos para
que `rodar` devuelva varios resultados con nombre en un solo paquete.

### D) `max(acumulado, nuevo)` para llevar el máximo
`vel_punta = max(vel_punta, vel)` actualiza `vel_punta` solo si `vel` es mayor. Es el patrón
típico para ir guardando "el más alto hasta ahora".

### E) matplotlib con dos paneles: `subplots`
```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11,4))
ax1.plot(...); ax2.bar(...)
```
`subplots(1, 2)` crea una figura con **1 fila y 2 columnas** de gráficas. Cada `ax` es una
gráfica independiente donde dibujas con `ax.plot`, `ax.bar`, etc. `plt.tight_layout()` las
ordena para que no se solapen.

### F) `plt.axhline(0, ...)`
Dibuja una **línea horizontal** en la altura indicada (aquí, en 0, para marcar el nivel de
"caída"). `ls="--"` la hace discontinua; `alpha=0.6` la hace semitransparente.

### G) `ax.bar(nombres, valores)`
Un diagrama de **barras**: una barra por cada nombre, de altura su valor. `color=[...]` da un
color a cada barra.

### H) Formato en columnas con f-strings
`f"{x:12.2f}"` reserva 12 caracteres para el número con 2 decimales; `f"{s:14s}"` reserva 14
para un texto; `f"{n:>12s}"` alinea a la derecha. Sirve para imprimir tablas alineadas a mano.
""".strip()),

]

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "notebooks",
                       "NB03_tocar_la_recompensa.ipynb")
    build(os.path.abspath(out), cells, title="NB03 · Tocar la recompensa")
