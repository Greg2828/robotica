"""Construye NB44·P6 · Puente de Python (6): NumPy intermedio para robótica.

Pensar en formas: (T, n) trayectorias, (N, 3) nubes de puntos, (3, 3)
rotaciones, (N, 3, 3) lotes. Grabar una trayectoria de Zancudo en un array
reservado (np.empty) frente a lista + np.array. Porciones por columnas y
filas. Máscaras booleanas, np.flatnonzero, argmax del primer True, índices con
listas (copia). Reducciones por ejes; np.diff, np.gradient, cumsum.
Broadcasting: las tres reglas, normalizar columnas, distancias entre todos los
pares (N,1,3)-(1,M,3), rotar N puntos (pts @ R.T), lotes de matrices con @ y
einsum. Vectorizar: cinemática directa de una pierna para 100.000 posturas
(bucle frente a vectorizado). np.linalg: norm (axis), cross (par = r×F),
outer, solve frente a inv, det, RᵀR = I. Vistas y copias a fondo: base,
shares_memory, ravel/flatten, += frente a a = a + b, out=. Decimales: eps,
isclose/allclose (rtol/atol), el tiempo acumulado, float32 frente a float64,
NaN que se propaga, nanmean. Laboratorio de 12 retos.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB44·P6 · Puente de Python (6): NumPy intermedio para robótica

**Puente de Python — Lección 6 de 6 (última)**

> En el NB15 y el NB27 aprendiste NumPy: arrays, `shape`, operaciones elemento a elemento, `@`, ejes, broadcasting, máscaras, vistas. Después, NB45-NB50 lo usaron a fondo: jacobianos de 3×9, matrices de rotación, `np.linalg.pinv`, `svd`, lotes de estados de forma (8, 10.000, 19)... y la trampa de las vistas de MuJoCo. Hoy hacemos el puente: el NumPy que de verdad se usa en robótica, con datos de Zancudo.

La habilidad que vamos a entrenar tiene nombre: **pensar en formas**. Un programador de NumPy con experiencia, antes de escribir una operación, se pregunta: "¿qué forma tiene cada array, y qué forma tendrá el resultado?". Si contestas eso, el resto sale solo, y los errores de forma (los más comunes, P1) desaparecen.
"""),

code(r"""import os
os.environ["MUJOCO_GL"] = "egl"
import time
import numpy as np
import mujoco
import matplotlib.pyplot as plt
np.set_printoptions(precision=4, suppress=True, linewidth=120)

zancudo = mujoco.MjModel.from_xml_path("robots/zancudo.xml")"""),

md(r"""## 1 · Pensar en formas

### Las formas típicas de la robótica

Casi todo lo que manejarás encaja en unas pocas formas. Apréndelas como un vocabulario:

| Forma | Qué es | Ejemplo |
|---|---|---|
| `(n,)` | un **vector**: un estado, una acción | `qpos` de Zancudo: `(9,)` |
| `(T, n)` | una **trayectoria**: T instantes, n números en cada uno | 1.000 pasos de `qpos`: `(1000, 9)` |
| `(N, 3)` | una **nube de puntos**: N puntos en 3D | las posiciones de los 8 cuerpos: `(8, 3)` |
| `(3, 3)` | una **matriz de rotación** (NB46) | la orientación del torso |
| `(3, nv)` | un **jacobiano** (NB46) | el del pie: `(3, 9)` |
| `(N, 3, 3)` | un **lote** de N rotaciones | la orientación de cada cuerpo: `(8, 3, 3)` |
| `(E, T, n)` | E trayectorias (episodios, semillas...) | el `rollout` del NB49: `(8, 10000, 19)` |

La convención casi universal: **el tiempo (o el índice del lote) va primero**, y las coordenadas, al final. Así, `trayectoria[t]` es el estado en el instante t, y `trayectoria[:, j]` es la evolución de la coordenada j a lo largo del tiempo.

MuJoCo sigue la misma lógica: `datos.xpos` (posiciones de los cuerpos) es `(nbody, 3)`, `datos.xmat` (sus rotaciones) es `(nbody, 9)` (cada matriz de 3×3 **aplanada** en 9 números, por cómo la guarda C):
"""),

code(r"""d = mujoco.MjData(zancudo)
mujoco.mj_forward(zancudo, d)
print("qpos:", d.qpos.shape, "| xpos:", d.xpos.shape, "| xmat:", d.xmat.shape)
rotaciones = d.xmat.reshape(-1, 3, 3)           # de (8, 9) a (8, 3, 3): 8 matrices de 3×3
print("rotaciones:", rotaciones.shape)
print("la del torso (cuerpo 1):\n", rotaciones[1])"""),

md(r"""`reshape(-1, 3, 3)` (NB27): "reorganiza en bloques de 3×3; el `-1` significa 'calcula tú cuántos'". 72 números / 9 = 8 matrices. La del torso es la identidad: está derecho.

## 2 · Grabar una trayectoria

### Reservar frente a añadir

Para tener datos interesantes, simulemos 3 segundos de Zancudo con una orden de agacharse al segundo 1 y de estirarse al segundo 2, y grabemos `qpos` en cada paso. Hay dos formas de grabar:

1. **Añadir a una lista** y convertir al final: `lista.append(d.qpos.copy())` y luego `np.array(lista)`. Sencillo y flexible (no hace falta saber cuántos pasos habrá).
2. **Reservar** el array entero de antemano con `np.empty((T, n))` (o `np.zeros`) y **rellenar** cada fila. Un poco más rápido y sin memoria duplicada; requiere saber T.
"""),

code(r"""T = 1500                                         # 3 s a 0,002 s por paso
agachado = np.array([0.5, -1.0, 0.5] * 2)

def ordenes(t: float) -> np.ndarray:
    return agachado if 1.0 <= t < 2.0 else np.zeros(6)

d = mujoco.MjData(zancudo)
tray = np.empty((T, zancudo.nq))                 # reservado: (1500, 9), con basura dentro
tiempos = np.empty(T)
contactos = np.empty(T, dtype=int)
for paso in range(T):
    d.ctrl[:] = ordenes(d.time)
    mujoco.mj_step(zancudo, d)
    tray[paso] = d.qpos                          # copia los 9 números EN la fila (no guarda una vista)
    tiempos[paso] = d.time
    contactos[paso] = d.ncon

print("trayectoria:", tray.shape, tray.dtype, "| contactos:", contactos.shape, contactos.dtype)"""),

md(r"""Dos detalles importantes:

- **`np.empty`** reserva memoria **sin inicializarla**: lo que hay dentro es "basura" (lo que hubiera antes en esa memoria). Es un poco más rápido que `np.zeros`, pero si te olvidas de rellenar alguna fila, tendrás números absurdos sin aviso. Úsalo solo si vas a rellenarlo **entero**.
- **`tray[paso] = d.qpos`** **copia** los valores dentro de la fila del array (la asignación a una porción escribe **dentro**, NB27). No hay trampa de vistas aquí, a diferencia de `lista.append(d.qpos)` sin `.copy()`, que guardaría 1.500 veces la misma vista (NB45).

### Porciones: columnas y filas

Con la trayectoria como array, todo se reduce a **porciones**:
"""),

code(r"""altura = 0.865 + tray[:, 1]                       # columna 1 (raiz_z), TODOS los instantes: (1500,)
rodillas = tray[:, [4, 7]]                        # las dos rodillas: (1500, 2)
pierna_d = tray[:, 3:6]                           # cadera, rodilla y tobillo derechos: (1500, 3)
cada_100 = tray[::100]                            # una de cada 100 filas: (15, 9)
ultimo_segundo = tray[tiempos >= 2.0]             # las filas del último segundo (máscara, sección 3)
print(altura.shape, rodillas.shape, pierna_d.shape, cada_100.shape, ultimo_segundo.shape)

fig, ejes = plt.subplots(1, 2, figsize=(11, 3.2))
ejes[0].plot(tiempos, altura)
ejes[0].set(xlabel="tiempo (s)", ylabel="altura de la cadera (m)")
ejes[1].plot(tiempos, rodillas, label=["rodilla derecha", "rodilla izquierda"])
ejes[1].set(xlabel="tiempo (s)", ylabel="ángulo (rad)")
ejes[1].legend()
for eje in ejes:
    eje.axvspan(1, 2, color="orange", alpha=0.15)
    eje.grid(alpha=0.3)
plt.tight_layout()
plt.show()"""),

md(r"""Lee bien cada porción, porque este es el pan de cada día:

- **`tray[:, 1]`**: "todas las filas, columna 1". El `:` es "todo" en esa dimensión. El resultado es **un vector** de 1.500 números (la dimensión de la columna desaparece al pedir **un** número).
- **`tray[:, [4, 7]]`**: con una **lista** de columnas, se queda con esas dos: `(1500, 2)`. (Las rodillas son las coordenadas 4 y 7: `raiz_x, raiz_z, raiz_giro, cadera_d, rodilla_d, tobillo_d, cadera_i, rodilla_i, tobillo_i`.)
- **`tray[:, 3:6]`**: de la columna 3 a la 5: `(1500, 3)`.
- **`tray[::100]`**: filas de 100 en 100 (la segunda dimensión, sin escribir, es "todo").
- `plt.plot(tiempos, rodillas)` con una matriz de 2 columnas dibuja **una línea por columna**, y `label` acepta una lista.

En la gráfica se ve el agachado (zona naranja): la cadera baja de 0,86 a 0,75 m y las rodillas se doblan hasta −1,05 rad; al estirarse, vuelve.
"""),

md(r"""## 3 · Máscaras e índices avanzados

### Preguntas de sí o no, para todos a la vez

Una **máscara** es un array de booleanos con la misma forma que los datos (NB27): `True` donde se cumple una condición. Con ella se **filtra** (`datos[mascara]`), se **cuenta** (`mascara.sum()`, porque `True` vale 1) y se **localiza**:
"""),

code(r"""agachado_de_verdad = altura < 0.8                 # (1500,) de True/False
print("pasos con la cadera por debajo de 0,8 m:", agachado_de_verdad.sum(),
      f"= {agachado_de_verdad.sum() * 0.002:.2f} s")
print("¿alguna vez sin contactos?", (contactos == 0).any(), "| ¿siempre?", (contactos == 0).all())

indices = np.flatnonzero(agachado_de_verdad)      # las POSICIONES de los True
print("primer y último paso agachado:", indices[0], indices[-1],
      f"→ de {tiempos[indices[0]]:.3f} s a {tiempos[indices[-1]]:.3f} s")"""),

md(r"""- **`mascara.sum()`**: cuántos `True`. Multiplicado por el pasito, **cuánto tiempo** pasa algo.
- **`.any()`** / **`.all()`**: ¿alguno? / ¿todos? (los equivalentes de `any`/`all` de Python, NB21, pero vectorizados).
- **`np.flatnonzero(mascara)`**: las **posiciones** de los `True` (el mismo resultado que `np.where(mascara)[0]`, NB27, sin la tupla).

Combinar condiciones se hace con **`&`** (y), **`|`** (o) y **`~`** (no), **con paréntesis** alrededor de cada comparación, porque estos operadores tienen más prioridad que `<` o `==`:
"""),

code(r"""en_la_fase_de_agachado = (tiempos >= 1.0) & (tiempos < 2.0)
bajo_pero_fuera_de_fase = agachado_de_verdad & ~en_la_fase_de_agachado
print("pasos bajos fuera de la fase de agachado:", bajo_pero_fuera_de_fase.sum())
print("primer instante:", tiempos[bajo_pero_fuera_de_fase][0] if bajo_pero_fuera_de_fase.any() else None)"""),

md(r"""Hay pasos con la cadera baja **después** de que termine la fase de agachado: es lo que tarda en estirarse (la cadera no sube de golpe a los 2,0 s, sino que tarda unas décimas: los motores son muelles con amortiguador, NB40).

(Y la trampa clásica: escribir `tiempos >= 1.0 & tiempos < 2.0` **sin** paréntesis da un error extraño, porque Python calcula primero `1.0 & tiempos`. Y escribir `and` en vez de `&` da el `ValueError: The truth value of an array... is ambiguous` del P3: `and` solo sabe trabajar con **un** booleano, no con arrays.)

### El primer instante en que algo pasa

Un modismo muy útil: **`np.argmax(mascara)`** da la posición del **primer** `True` (porque `argmax` devuelve el primer máximo, y `True` > `False`). Lo usamos en NB49 y NB50 para medir "cuándo llega al 90 %". Pero cuidado con su trampa:
"""),

code(r"""print("primer paso bajo 0,8 m:", np.argmax(altura < 0.8))
print("primer paso bajo 0,1 m:", np.argmax(altura < 0.1), "← ¡ojo! nunca baja de 0,1 m...")
print("comprobación:", (altura < 0.1).any())"""),

md(r"""Si **ningún** elemento es `True`, `argmax` devuelve **0** (el primer máximo de un array todo `False`), que parece "ocurrió en el paso 0". Siempre hay que comprobar con `.any()` antes, o usar `np.flatnonzero` (que daría un array vacío).

### Índices con listas: siempre copias

Un último detalle, que conecta con las vistas (sección 7). Las **porciones** (`a[2:5]`, `a[:, 3]`) dan **vistas**; pero los **índices con listas o con máscaras** (`a[[4, 7]]`, `a[mascara]`) dan **copias**. Así que modificar el resultado no toca el original... y asignar **a través de** ellos sí que escribe en el original:
"""),

code(r"""a = np.arange(6.0)
seleccion = a[[1, 3]]          # copia
seleccion[:] = 99
print(a)                       # sin cambios
a[[1, 3]] = 99                 # asignación DIRECTA con índices: escribe en a
print(a)
a[a > 50] = 0                  # el modismo de "recortar" con una máscara
print(a)"""),

md(r"""## 4 · Reducciones por ejes y diferencias

### axis: a lo largo de qué dimensión

Las **reducciones** (`sum`, `mean`, `max`, `min`, `std`, `argmax`...) aceptan **`axis`** (NB27): la dimensión que se **colapsa**. La forma de pensarlo: `axis=0` recorre las **filas** (el tiempo) y deja una respuesta **por columna**; `axis=1` recorre las columnas y deja una respuesta **por fila**:
"""),

code(r"""articulaciones = tray[:, 3:]                                 # (1500, 6)
print("media de cada articulación en el tiempo (axis=0):", articulaciones.mean(axis=0).round(3), articulaciones.mean(axis=0).shape)
print("ángulo máximo (en valor absoluto) de cada una:    ", np.abs(articulaciones).max(axis=0).round(3))
print("suma de los 6 ángulos en cada instante (axis=1):  ", articulaciones.sum(axis=1).shape)
print("¿en qué paso alcanza cada una su mínimo?          ", articulaciones.argmin(axis=0))"""),

md(r"""Una regla mnemotécnica infalible: **la forma del resultado es la forma del original sin la dimensión del `axis`**. `(1500, 6)` con `axis=0` → `(6,)`; con `axis=1` → `(1500,)`. Y con `keepdims=True`, la dimensión se queda con tamaño 1: `(1, 6)`, útil para el broadcasting (sección 5).

### Diferencias: velocidades desde posiciones

En el P4 calculamos velocidades con `itertools.pairwise`, de dos en dos. En NumPy, **`np.diff`** hace lo mismo para todo el array a la vez: `np.diff(x)` = `[x[1] − x[0], x[2] − x[1], ...]` (un elemento **menos**):
"""),

code(r"""velocidad_cadera = np.diff(altura) / np.diff(tiempos)                # (1499,): ¡uno menos!
velocidad_central = np.gradient(altura, tiempos)                       # (1500,): misma longitud
print(velocidad_cadera.shape, velocidad_central.shape)
print(f"velocidad máxima de bajada: {velocidad_cadera.min():.3f} m/s;  de subida: {velocidad_cadera.max():.3f} m/s")

# comparación con la velocidad que calcula MuJoCo, al final de la simulación
print(f"último paso: diferencias {velocidad_cadera[-1]:.5f} | MuJoCo {d.qvel[1]:.5f}")"""),

md(r"""- **`np.diff`** da la diferencia entre vecinos: con `/ np.diff(tiempos)`, una velocidad (NB16: pendiente = cambio / tiempo). Tiene un elemento menos, así que para dibujarla contra el tiempo hay que usar `tiempos[1:]`.
- **`np.gradient(x, t)`** calcula la pendiente en **cada** punto (con diferencias "centradas" en el interior: la media de la de antes y la de después), y conserva la longitud. Más cómoda para dibujar.
- La diferencia de posiciones coincide (casi) con la velocidad que integra MuJoCo: con el integrador semiimplícito (NB49), la posición nueva se calcula **con** la velocidad nueva, así que `(q_nuevo − q_viejo) / dt` es justo esa velocidad.

Y la operación inversa, **`np.cumsum`** (suma acumulada), reconstruye una posición sumando velocidades × dt: es una integral "a mano" (NB16), lo mismo que `itertools.accumulate` del P4, pero vectorizada.
"""),

md(r"""## 5 · Broadcasting a fondo

### Las tres reglas

En el NB27 viste que NumPy sabe operar arrays de **formas distintas**, "estirando" los pequeños. Se llama **broadcasting** (difusión). Ahora, las **reglas exactas**, que son solo tres. Para operar dos arrays, NumPy compara sus formas **empezando por la derecha**:

1. Si un array tiene **menos** dimensiones, se le añaden dimensiones de tamaño 1 **por la izquierda**: `(3,)` se trata como `(1, 3)`.
2. Dos dimensiones son compatibles si son **iguales**, o si **una de ellas es 1** (que se "estira" hasta la otra).
3. Si alguna pareja no cumple la regla 2, error: `operands could not be broadcast together` (P1).

Ejemplos:

```
   (1500, 6)  -  (6,)      →  (1500, 6)  -  (1, 6)   →  (1500, 6)     ✓  restar a cada fila un vector
   (1500, 6)  -  (1500,)   →  (1500, 6)  -  (1, 1500) →  ¡6 ≠ 1500!   ✗  error
   (1500, 6)  -  (1500, 1) →                             (1500, 6)     ✓  restar a cada columna un vector
   (8, 1, 3)  -  (1, 5, 3) →                             (8, 5, 3)     ✓  ¡todas las parejas!
```

El segundo caso es **el** error típico: quieres restar a cada fila su media (`(1500,)`), y NumPy intenta alinearla con las **columnas**. Arreglo: darle forma de columna, `(1500, 1)`, con `keepdims=True` o con `[:, None]`:
"""),

code(r"""media_por_instante = articulaciones.mean(axis=1)                        # (1500,)
centradas = articulaciones - media_por_instante[:, None]                 # (1500, 6) - (1500, 1)
centradas_2 = articulaciones - articulaciones.mean(axis=1, keepdims=True)
print(centradas.shape, np.allclose(centradas, centradas_2))

# normalizar cada columna (media 0, desviación 1): lo que hace un "normalizador de observaciones" (NB27)
normalizadas = (articulaciones - articulaciones.mean(axis=0)) / (articulaciones.std(axis=0) + 1e-8)
print(normalizadas.mean(axis=0).round(6), normalizadas.std(axis=0).round(3))"""),

md(r"""**`[:, None]`** añade una dimensión de tamaño 1 en esa posición (`None` es un alias de `np.newaxis`): de `(1500,)` a `(1500, 1)`. Es el truco más usado para preparar un broadcasting. (Y el `+ 1e-8` evita dividir por cero si alguna columna fuera constante.)

### Distancias entre todos los pares

El cuarto ejemplo de la lista es el más potente: con una dimensión "de 1" en cada lado, el broadcasting calcula **todas las combinaciones**. Por ejemplo, la distancia de cada cuerpo de Zancudo a cada uno de los demás, de una vez:
"""),

code(r"""mujoco.mj_forward(zancudo, d)
puntos = d.xpos[1:]                                            # los 7 cuerpos del robot (sin el mundo): (7, 3)
diferencias = puntos[:, None, :] - puntos[None, :, :]          # (7, 1, 3) - (1, 7, 3) → (7, 7, 3)
distancias = np.linalg.norm(diferencias, axis=-1)              # (7, 7)
nombres = [zancudo.body(i).name for i in range(1, zancudo.nbody)]
print(diferencias.shape, distancias.shape)
print("del torso a cada cuerpo:", dict(zip(nombres, distancias[0].round(3).tolist())))"""),

md(r"""`diferencias[i, j]` es el vector que va del cuerpo j al cuerpo i, y su norma (sección 6), la distancia. Sin un solo bucle. Esta "matriz de distancias" es la base de muchos algoritmos (detección de colisiones, vecinos más cercanos...). (`axis=-1` = "la última dimensión", la de las 3 coordenadas: los índices negativos funcionan también en los ejes.)

### Rotar muchos puntos a la vez

Para rotar **un** punto `p` (forma `(3,)`) con una matriz `R`: `R @ p` (NB46). ¿Y para rotar **N** puntos guardados como filas de una matriz `(N, 3)`? `R @ puntos` no encaja: `(3, 3) @ (N, 3)` necesitaría que N fuera 3. El truco es **trasponer**:
"""),

code(r"""angulo = np.radians(30)
R = np.array([[np.cos(angulo), 0, np.sin(angulo)],              # giro de 30° alrededor del eje y (NB46)
              [0, 1, 0],
              [-np.sin(angulo), 0, np.cos(angulo)]])
nube = np.random.default_rng(0).normal(size=(1000, 3))          # 1.000 puntos al azar
rotada = nube @ R.T                                              # (1000, 3) @ (3, 3) → (1000, 3)
# comprobación con un punto suelto:
print(np.allclose(rotada[0], R @ nube[0]))"""),

md(r"""**`puntos @ R.T`** es la forma estándar de rotar una nube de puntos guardada **por filas**. ¿Por qué funciona? Porque cada fila del resultado es `fila @ R.T`, que es lo mismo que `R @ fila` (trasponer los dos lados de un producto invierte su orden: (R·p)ᵀ = pᵀ·Rᵀ). Apréndelo como un modismo: **filas → `@ R.T`**.

### Lotes de matrices

Y si tenemos un **lote** de rotaciones `(N, 3, 3)` y un lote de vectores `(N, 3)`, y queremos rotar cada vector con **su** matriz? El `@` de NumPy trata las dimensiones de la izquierda como **lote** (con broadcasting): `(N, 3, 3) @ (N, 3, 1)` → `(N, 3, 1)`. Y la alternativa más expresiva es **`np.einsum`**, que describe la operación con letras:
"""),

code(r"""mats = d.xmat.reshape(-1, 3, 3)                                # (8, 3, 3): la rotación de cada cuerpo
vectores = np.tile([0.0, 0.0, 1.0], (zancudo.nbody, 1))        # (8, 3): el eje z local de cada uno

con_matmul = (mats @ vectores[:, :, None])[:, :, 0]            # (8,3,3) @ (8,3,1) → (8,3,1) → (8,3)
con_einsum = np.einsum("nij,nj->ni", mats, vectores)           # "para cada n: suma sobre j de M[n,i,j]·v[n,j]"
print(np.allclose(con_matmul, con_einsum))
print("eje z de cada cuerpo en el mundo:\n", con_einsum.round(3))"""),

md(r"""`einsum("nij,nj->ni", ...)` se lee: "el primer array tiene índices n, i, j; el segundo, n, j; el resultado, n, i; y los índices que **desaparecen** (la j) se **suman**". Es exactamente el producto matriz-vector para cada n. Es muy potente (puede expresar casi cualquier producto de arrays), aunque al principio cuesta leerlo. No hace falta dominarlo: basta con reconocerlo cuando aparezca (en PyTorch es muy común).

El eje z de cada cuerpo apunta **casi** hacia arriba en el mundo: casi `[0, 0, 1]`, con una pequeña componente x (de −0,04 como mucho, unos 2°). Es porque `d` guarda el estado del **final** de la simulación de la sección 2, cuando Zancudo acaba de estirarse y aún se balancea un poco.
"""),

md(r"""## 6 · Vectorizar

### Por qué los bucles de Python son lentos

Un bucle de Python que hace una cuenta pequeña en cada vuelta paga, en **cada** vuelta, el coste del intérprete (averiguar el tipo de cada variable, buscar la operación, crear objetos nuevos...). NumPy hace la misma cuenta **en C**, sobre todo el array, pagando ese coste **una vez**. A **vectorizar** se le llama a convertir un bucle sobre elementos en operaciones sobre arrays enteros (NB27).

Pongámoslo a prueba con algo de verdad: la **cinemática directa** de la pierna de Zancudo (NB46), es decir, la posición del tobillo respecto a la cadera a partir de los ángulos de cadera y rodilla, para **100.000** posturas. Con los muslos y piernas de 0,4 m, y midiendo los ángulos como en Zancudo:

```
   x = L₁·sen(θ₁) + L₂·sen(θ₁ + θ₂)          z = −L₁·cos(θ₁) − L₂·cos(θ₁ + θ₂)
```
"""),

code(r"""L1 = L2 = 0.4
rng = np.random.default_rng(1)
caderas = rng.uniform(-1.0, 1.0, 100_000)
rodillas_q = rng.uniform(-2.0, 0.0, 100_000)

def tobillo_bucle(caderas, rodillas_q):
    resultado = np.empty((len(caderas), 2))
    for i in range(len(caderas)):
        t1, t2 = caderas[i], rodillas_q[i]
        resultado[i, 0] = L1 * np.sin(t1) + L2 * np.sin(t1 + t2)
        resultado[i, 1] = -L1 * np.cos(t1) - L2 * np.cos(t1 + t2)
    return resultado

def tobillo_vectorizado(caderas, rodillas_q):
    x = L1 * np.sin(caderas) + L2 * np.sin(caderas + rodillas_q)
    z = -L1 * np.cos(caderas) - L2 * np.cos(caderas + rodillas_q)
    return np.stack([x, z], axis=1)                         # dos (N,) → una (N, 2)

inicio = time.perf_counter(); r1 = tobillo_bucle(caderas, rodillas_q); t_bucle = time.perf_counter() - inicio
inicio = time.perf_counter(); r2 = tobillo_vectorizado(caderas, rodillas_q); t_vect = time.perf_counter() - inicio
print(f"bucle: {t_bucle * 1000:.0f} ms | vectorizado: {t_vect * 1000:.1f} ms | {t_bucle / t_vect:.0f} veces más rápido")
print("¿mismo resultado?", np.allclose(r1, r2), "| forma:", r2.shape)"""),

md(r"""El código vectorizado es **casi igual** que la fórmula (se lee mejor que el bucle) y, en esta Raspberry Pi, **unas 14 veces** más rápido (como el ×10-20 del NB27). La ventaja crece cuanto más sencilla es la cuenta de cada vuelta, porque entonces casi todo el tiempo del bucle es "coste del intérprete". En un entrenamiento que repite algo millones de veces, es la diferencia entre horas y minutos.

(`np.stack([x, z], axis=1)` apila dos vectores como **columnas** de una matriz; con `axis=0` serían filas. Es el compañero de `np.concatenate`, que **une** arrays a lo largo de una dimensión que ya existe, NB27.)

Regla práctica: si escribes `for i in range(len(array))` y dentro solo hay cuentas con `array[i]`, casi seguro que se puede vectorizar. Lo que **no** se puede vectorizar fácilmente son los bucles en los que cada paso **depende del anterior** (como `mj_step`: el estado siguiente necesita el actual). Para esos están las herramientas del NB49 (`rollout`) y del NB59 (JAX).
"""),

md(r"""## 7 · np.linalg: el álgebra lineal del día a día

En el NB46 usaste `pinv`, `lstsq`, `svd` y `cond` para la cinemática inversa. Aquí van las piezas más **básicas**, que aparecen por todas partes:
"""),

code(r"""v = np.array([3.0, 4.0, 0.0])
print("norma (longitud) de un vector:", np.linalg.norm(v))
print("norma de cada fila de una matriz (axis=1):", np.linalg.norm(nube[:3], axis=1).round(3))

r = np.array([0.0, 0.0, 0.4])       # brazo de palanca: de la articulación al punto donde se empuja
F = np.array([10.0, 0.0, 0.0])      # fuerza horizontal de 10 N
print("par = r × F:", np.cross(r, F), "N·m  (NB37: 0,4 m · 10 N = 4 N·m, alrededor del eje y)")
print("producto exterior (outer) de [1, 2] y [3, 4, 5]:\n", np.outer([1, 2], [3, 4, 5]))"""),

md(r"""- **`np.linalg.norm(v)`**: la longitud de un vector (NB12). Con `axis`, la de cada fila o columna.
- **`np.cross(r, F)`**: el **producto vectorial** (NB37), que da el **par** de una fuerza: perpendicular a los dos, con módulo |r|·|F|·sen(ángulo). Fíjate en el signo: +4 en y. Con `np.cross` se calculan pares, velocidades angulares (v = ω × r) y normales a superficies.
- **`np.outer(a, b)`**: la matriz de todos los productos `a[i]·b[j]`. Es lo mismo que `a[:, None] * b[None, :]` (¡broadcasting!).

### solve, no inv

Para resolver un sistema de ecuaciones **A·x = b** (lo que hace MuJoCo en cada paso con la ecuación del movimiento, M·q̈ = ..., NB45), la tentación es calcular la inversa: `x = inv(A) @ b`. **No lo hagas**: usa `np.linalg.solve(A, b)`, que es más rápido y, sobre todo, más **preciso**:
"""),

code(r"""mujoco.mj_forward(zancudo, d)
M = np.zeros((zancudo.nv, zancudo.nv))
mujoco.mj_fullM(zancudo, d, M)                                  # la matriz de masas (NB45): (9, 9)
fuerza = d.qfrc_actuator + d.qfrc_passive + d.qfrc_constraint - d.qfrc_bias   # lado derecho (NB45)

aceleracion_solve = np.linalg.solve(M, fuerza)
aceleracion_inv = np.linalg.inv(M) @ fuerza
print("solve ≈ inv:", np.allclose(aceleracion_solve, aceleracion_inv))
print("¿coincide con la qacc de MuJoCo?", np.allclose(aceleracion_solve, d.qacc, atol=1e-6))

# una matriz MAL condicionada (NB46): la de Hilbert, H[i, j] = 1 / (i + j + 1)
n = 10
H = 1.0 / (np.arange(n)[:, None] + np.arange(n)[None, :] + 1)    # ¡broadcasting! (sección 5)
x_verdad = np.ones(n)
b = H @ x_verdad                                                 # así sabemos la solución exacta
print(f"número de condición: {np.linalg.cond(H):.1e}")
for nombre, x in [("solve", np.linalg.solve(H, b)), ("inv  ", np.linalg.inv(H) @ b)]:
    print(f"{nombre}: error en x {np.abs(x - x_verdad).max():.1e} | residuo |H·x − b| {np.abs(H @ x - b).max():.1e}")"""),

md(r"""- Con la matriz de masas de Zancudo (bien condicionada), `solve` e `inv` dan lo mismo, y recuperan **exactamente** la aceleración que calcula MuJoCo: la ecuación del movimiento del NB45, resuelta por nosotros.
- Con una matriz **mal condicionada** (la de Hilbert de 10×10, un ejemplo clásico: su número de condición, NB46, es de 10¹³, así que los errores de redondeo se amplifican hasta 10¹³ veces), las dos se alejan de la solución exacta, pero `inv` lo hace **unas 14 veces peor** en x, y su **residuo** (cuánto falla al volver a meter la solución en la ecuación) es de 10⁻⁵ frente al 10⁻¹⁶ de `solve`: `solve` da una solución que cumple la ecuación hasta la última cifra; `inv`, no. Calcular la inversa entera y luego multiplicar acumula más errores que resolver directamente. Además, `solve` es más rápida, sobre todo con matrices grandes (no calcula la inversa entera, que no necesita).

Regla: **nunca `inv(A) @ b`; siempre `solve(A, b)`**. Y si la matriz puede ser singular o no cuadrada (como un jacobiano), `lstsq` o `pinv` (NB46).

### Comprobar propiedades con allclose

Y un uso constante de `np.allclose`: comprobar propiedades matemáticas. Por ejemplo, que una matriz de rotación cumple RᵀR = I y det(R) = 1 (NB46):
"""),

code(r"""print("RᵀR = I:", np.allclose(R.T @ R, np.eye(3)), "| det(R) = 1:", np.isclose(np.linalg.det(R), 1.0))
print("todas las de Zancudo:", np.allclose(mats.transpose(0, 2, 1) @ mats, np.eye(3)))"""),

md(r"""`mats.transpose(0, 2, 1)` traspone **cada** matriz del lote (intercambia las dos últimas dimensiones y deja la del lote en su sitio), y el `@` por lotes multiplica cada una por su traspuesta. `np.eye(3)` se difunde a las 8 a la vez. Una línea para comprobar 8 matrices.
"""),

md(r"""## 8 · Vistas y copias, a fondo

### La regla, completa

La trampa que más horas hace perder con NumPy y MuJoCo (NB27, NB45). Aquí está **completa**:

| Operación | ¿Vista o copia? |
|---|---|
| porción `a[2:5]`, `a[:, 3]`, `a[::2]` | **vista** |
| `a.T`, `a.reshape(...)` (casi siempre), `a.ravel()` (si puede) | **vista** |
| índices con listas `a[[1, 3]]` o máscaras `a[a > 0]` | **copia** |
| `a.copy()`, `a.flatten()`, `np.array(a)` | **copia** |
| operaciones `a + b`, `a * 2`, `np.sin(a)` | array **nuevo** |
| los arrays de `MjData` (`qpos`, `xpos`...) y de `MjModel` | **vistas** de la memoria de C |

Una **vista** es otro array que mira a la **misma memoria**: cambiar uno cambia el otro. Se puede preguntar con **`.base`** (el array al que mira, o `None` si es dueño de su memoria) y con **`np.shares_memory`**:
"""),

code(r"""a = np.arange(12.0).reshape(3, 4)
columna = a[:, 1]
filtrado = a[a > 5]
print("¿columna es vista?", columna.base is not None, np.shares_memory(a, columna))
print("¿filtrado es vista?", np.shares_memory(a, filtrado))
print("ravel:", np.shares_memory(a, a.ravel()), "| flatten:", np.shares_memory(a, a.flatten()))
columna[:] = -1
print(a)"""),

md(r"""Cambiar `columna` ha cambiado la columna 1 de `a`: es la misma memoria. (`ravel` y `flatten` hacen lo mismo, aplanar a 1D, pero `ravel` da una vista si puede, y `flatten` siempre una copia.)

### += frente a a = a + b

Otra sutileza, ahora con la asignación. Mira la diferencia:
"""),

code(r"""qpos = np.zeros(3)
vista = qpos                    # dos nombres para el mismo array

qpos += 1                       # operación "en el sitio": modifica el array existente
print("tras +=:      ", vista)

qpos = qpos + 1                 # crea un array NUEVO y le pone el nombre qpos
print("tras = ... + :", vista, "  ← vista ya no ve los cambios")
print("qpos:         ", qpos)"""),

md(r"""- **`qpos += 1`** modifica el array **existente** (operación *in place*): todos los nombres que apuntan a él ven el cambio.
- **`qpos = qpos + 1`** calcula un array **nuevo** y hace que el **nombre** `qpos` apunte a él. El array viejo sigue ahí, con los nombres que tuviera (`vista`), sin cambios.

¿Por qué importa en robótica? Porque con `datos.qpos` pasa exactamente esto. `datos.qpos += 0.1` **modifica** la simulación (escribe en la memoria de MuJoCo). Pero si haces `q = datos.qpos` y luego `q = q + 0.1`, solo has creado un array nuevo: la simulación **no** se entera. Y `datos.qpos = algo` directamente... MuJoCo lo permite y copia los valores dentro (es un atributo especial), pero `datos.qpos[:] = algo` deja clarísimo que escribes **dentro** del array. Es la costumbre más segura.

### out=: calcular sin crear arrays

Para bucles muy rápidos, muchas funciones de NumPy aceptan **`out=`**: escriben el resultado en un array que ya existe, sin crear uno nuevo en cada vuelta (como el estilo "rellena este array" de MuJoCo, NB45):
"""),

code(r"""destino = np.empty(3)
np.multiply(np.array([1.0, 2.0, 3.0]), 2.0, out=destino)
np.clip(np.array([5.0, -5.0, 0.5]), -1, 1, out=destino)
print(destino)"""),

md(r"""## 9 · Decimales: comparar sin caer en trampas

### La precisión de la máquina

Los decimales del ordenador (`float64`) tienen unas **16 cifras** de precisión (NB06). El número más pequeño que, sumado a 1, da algo distinto de 1, se llama **épsilon de la máquina**:
"""),

code(r"""print("épsilon de float64:", np.finfo(np.float64).eps)
print("épsilon de float32:", np.finfo(np.float32).eps)
print("1 + eps/2 == 1 ?", 1.0 + np.finfo(np.float64).eps / 2 == 1.0)"""),

md(r"""Para `float64`, 2,2·10⁻¹⁶ (unas 16 cifras); para `float32`, 1,2·10⁻⁷ (solo unas **7** cifras). Y esto importa más de lo que parece: **PyTorch usa `float32` por defecto** (NB31), y las GPU van mucho más rápido con él (NB59). Una política entrenada en `float32` recibe observaciones de MuJoCo en `float64`: conviene convertirlas (`.astype(np.float32)`, NB27) y saber que se pierden cifras.

### El tiempo acumulado

Ya lo viste en el NB49: `simular_zancudo(2.0)` devolvía un tiempo de `2.0000000000000013`. Sumar 0,002 mil veces acumula errores de redondeo:
"""),

code(r"""t = 0.0
for _ in range(1000):
    t += 0.002
print(t, "| ¿igual a 2.0?", t == 2.0, "| ¿cerca?", np.isclose(t, 2.0))
print("la forma robusta: contar PASOS (enteros) y multiplicar:", 1000 * 0.002)"""),

md(r"""Por eso, en los bucles del curso, siempre contamos **pasos** (`for paso in range(int(round(segundos / dt)))`, NB49) en vez de comparar tiempos (`while t < segundos`): los enteros son **exactos**. Y para decidir si dos decimales son "iguales", **nunca `==`**: siempre con tolerancia.

### isclose y allclose: dos tolerancias

`np.isclose(a, b)` (uno a uno) y `np.allclose(a, b)` (¿todos?) consideran iguales dos números si:

```
   |a − b|  ≤  atol  +  rtol · |b|
```

- **`rtol`** (tolerancia **relativa**, por defecto 10⁻⁵): un error **proporcional** al tamaño del número. Para números grandes.
- **`atol`** (tolerancia **absoluta**, por defecto 10⁻⁸): un error fijo. Imprescindible para comparar con **cero**, donde la relativa no sirve (el 10⁻⁵ de 0 es 0).
"""),

code(r"""print(np.isclose(1000.0, 1000.001))                       # True: error relativo de 10⁻⁶
print(np.isclose(1e-9, 0.0))                              # True: gracias a atol = 10⁻⁸
print(np.isclose(1e-6, 0.0))                              # False: 10⁻⁶ > atol
print(np.isclose(1e-6, 0.0, atol=1e-5))                   # True: con una atol a la medida
print(np.isclose(0.859, 0.86, rtol=0, atol=0.005))        # ¿a menos de 5 mm? True"""),

md(r"""Elige las tolerancias **pensando en las unidades**: para alturas en metros, `atol=1e-3` es "un milímetro"; para ángulos en radianes, `atol=1e-3` es unas 0,06°. Los valores por defecto están pensados para comprobaciones numéricas (como RᵀR = I), no para cosas físicas.

### NaN se contagia

Por último, el `NaN` (NB22, NB49): **cualquier** operación con un `NaN` da `NaN`, así que un solo `NaN` en un array **contagia** las sumas, las medias, los máximos...
"""),

code(r"""notas = np.array([412.0, 455.2, np.nan, 430.8])
print("media:", notas.mean(), "| máximo:", notas.max())
print("nanmean:", np.nanmean(notas).round(1), "| nanmax:", np.nanmax(notas))
print("¿dónde hay NaN?", np.isnan(notas), "→ posiciones", np.flatnonzero(np.isnan(notas)))
print("NaN == NaN ?", np.nan == np.nan)"""),

md(r"""- La media y el máximo se vuelven `NaN`. Las versiones **`np.nanmean`**, **`np.nanmax`**, **`np.nansum`**... **ignoran** los `NaN`.
- Para encontrarlos: **`np.isnan`** (y `np.isfinite`, que además detecta los infinitos, NB22).
- Y la rareza final: **`NaN == NaN` es `False`**. Un `NaN` no es igual a nada, ni a sí mismo. Por eso nunca se busca con `== np.nan`, siempre con `np.isnan`.

Pero ojo: ignorar los `NaN` con `nanmean` es **esconder** un problema. Un `NaN` en una nota de entrenamiento significa que algo explotó (P5). Primero averigua **por qué** apareció; solo después decide si ignorarlo.
"""),

md(r"""## 10 · Resumen (y cierre del puente)

1. **Pensar en formas**: `(n,)`, `(T, n)`, `(N, 3)`, `(3, 3)`, `(N, 3, 3)`, `(E, T, n)`; el tiempo o el lote, primero. `xmat.reshape(-1, 3, 3)`.
2. **Grabar**: `np.empty((T, n))` + `tray[paso] = d.qpos` (copia dentro de la fila). Porciones: `tray[:, j]`, `tray[:, [a, b]]`, `tray[:, a:b]`, `tray[::k]`.
3. **Máscaras**: `.sum()` (contar), `.any()`/`.all()`, `np.flatnonzero`, `&`/`|`/`~` con paréntesis. `argmax(mascara)` = primer `True`, **comprobando antes con `.any()`**. Índices con listas o máscaras = **copias**; asignar a través de ellos escribe en el original.
4. **Reducciones**: la forma del resultado es la original sin el `axis`; `keepdims`. **`np.diff`** (uno menos), **`np.gradient`** (misma longitud), `np.cumsum`.
5. **Broadcasting**: alinear por la derecha; iguales o 1. `[:, None]` para columnas. Todas las parejas con `(N,1,3) − (1,M,3)`. Rotar filas: **`puntos @ R.T`**. Lotes: `@` y `einsum`.
6. **Vectorizar**: un orden de magnitud más rápido (×14 aquí) y más legible; lo que no se vectoriza fácil, los bucles con dependencia paso a paso.
7. **`np.linalg`**: `norm` (axis), `cross` (pares), `outer`, **`solve` en vez de `inv`**, `det`; comprobar propiedades con `allclose`.
8. **Vistas y copias**: la tabla; `.base`, `np.shares_memory`; **`+=` modifica, `a = a + b` crea**; `datos.qpos[:] = ...`; `out=`.
9. **Decimales**: épsilon (float64 ≈ 16 cifras, float32 ≈ 7); contar pasos enteros; **`isclose`/`allclose`** con `atol` y `rtol` pensadas en unidades; `NaN` se contagia, `np.isnan`, `nan*`, `NaN != NaN`.

**El puente completo.** Con P1-P6 has subido, escalón a escalón, del Python de la Parte 3 al del Bloque A: leer código ajeno y documentación, funciones como piezas (callbacks, cierres, decoradores), clases que se comportan como las de Python, generadores y gestores de contexto, tipos y errores profesionales, y el NumPy de la robótica. Ahora, NB45-NB50 se leen de otra manera: te recomiendo **repasarlos** (aunque sea por encima) antes de seguir con el NB51.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Forma (*shape*)** | Las dimensiones de un array: `(T, n)`, `(N, 3, 3)`... |
| **Lote (*batch*)** | Muchos objetos iguales apilados en la primera dimensión. |
| **Reducción** | Operación que colapsa una dimensión (`sum`, `mean`, `max` con `axis`). |
| **Broadcasting (difusión)** | Operar arrays de formas distintas estirando las dimensiones de tamaño 1. |
| **`einsum`** | Notación con letras para describir productos y sumas de arrays. |
| **Vectorizar** | Sustituir bucles sobre elementos por operaciones sobre arrays enteros. |
| **Producto vectorial / exterior** | `cross` (perpendicular, pares) / `outer` (todos los productos `a[i]·b[j]`). |
| **Operación en el sitio (*in place*)** | Modifica el array existente (`+=`, `out=`) en vez de crear uno nuevo. |
| **Épsilon de la máquina** | La menor diferencia distinguible respecto a 1: mide la precisión de los decimales. |
| **Tolerancia absoluta / relativa** | Error fijo (`atol`) / proporcional al tamaño del número (`rtol`). |
"""),

md(r"""## 11 · Laboratorio

**R1.** Con la trayectoria `tray` de la sección 2, calcula el ángulo medio de cada una de las 6 articulaciones **solo durante la fase de agachado** (de 1 a 2 s), en una línea.

**R2.** ★ Predice la forma de cada resultado sin ejecutar: `np.zeros((5, 3)) + np.ones(3)`, `np.zeros((5, 3)) + np.ones((5, 1))`, `np.zeros((5, 3)).sum(axis=0, keepdims=True)`, `np.zeros((4, 1, 3)) - np.zeros((1, 6, 3))`. ¿Cuál de estas da error: `np.zeros((5, 3)) + np.ones(5)`?

**R3.** Encuentra con máscaras el **intervalo más largo** de pasos seguidos en que la cadera está por debajo de 0,8 m, sin bucles de Python. (Pista: `np.diff` sobre la máscara convertida a entero marca con +1 los comienzos y con −1 los finales.)

**R4.** Calcula la velocidad de cada articulación con `np.gradient(tray[:, 3:], tiempos, axis=0)` y compárala con la que da MuJoCo grabando también `qvel`. ¿Coinciden?

**R5.** ★ Escribe `distancias_a(puntos, objetivo)` que, dados `puntos` `(N, 3)` y un `objetivo` `(3,)`, devuelva la distancia de cada punto al objetivo, `(N,)`, y el índice del más cercano. Úsala para saber qué cuerpo de Zancudo está más cerca del punto `(0.1, 0, 0.1)`.

**R6.** Vectoriza esta función: `def energia(qd, I): total = 0; for i in range(len(qd)): total += 0.5 * I[i] * qd[i] ** 2; return total`.

**R7.** Comprueba con `np.cross` que el par de una fuerza **paralela** al brazo de palanca es cero, y que el par de una fuerza perpendicular tiene módulo |r|·|F|.

**R8.** ★ Construye una rotación de 90° alrededor de z, aplícala a una nube de 5 puntos guardada por filas, y comprueba que **las distancias entre todos los pares** de puntos no cambian (una rotación es un movimiento rígido).

**R9.** ★ Explica qué imprime y por qué: `a = np.arange(5.0); b = a[1:4]; b *= 10; c = a[[1, 2]]; c += 1; print(a)`.

**R10.** Explica por qué `datos.qpos = datos.qpos + 0.1` y `datos.qpos += 0.1` tienen el mismo efecto con MuJoCo, pero `q = datos.qpos; q = q + 0.1` no hace nada en la simulación. (Pista: P3, `datos.qpos` es una *propiedad* con setter.)

**R11.** Suma 0,1 diez veces en un bucle. ¿Da 1,0? Compáralo con `np.isclose` y con `math.fsum([0.1] * 10)`. ¿Qué hace `fsum`?

**R12.** ★ Convierte la trayectoria a `float32` y calcula la velocidad de la cadera con `np.diff` en las dos precisiones. ¿Cuál es la diferencia máxima entre ambas? ¿Por qué es mucho mayor que la diferencia de las posiciones?
"""),

md(r'''<details>
<summary>▶ Solución R1</summary>

```python
fase = (tiempos >= 1.0) & (tiempos < 2.0)
print(tray[fase, 3:].mean(axis=0).round(3))
```

`tray[fase, 3:]` combina una **máscara** en las filas con una **porción** en las columnas: las filas de la fase, columnas de la 3 en adelante. Sale algo cercano a `[0.5, -1.0, 0.5, 0.5, -1.0, 0.5]` (las órdenes del agachado), algo menos en valor absoluto por el tiempo que tarda en llegar al principio de la fase.
</details>

<details>
<summary>▶ Solución R2</summary>

- `(5, 3) + (3,)` → **`(5, 3)`** (suma a cada fila).
- `(5, 3) + (5, 1)` → **`(5, 3)`** (suma a cada columna).
- `sum(axis=0, keepdims=True)` → **`(1, 3)`**.
- `(4, 1, 3) - (1, 6, 3)` → **`(4, 6, 3)`** (todas las parejas).
- `(5, 3) + (5,)` → **error**: por la derecha se comparan 3 y 5, que no son iguales ni 1. Arreglo: `np.ones(5)[:, None]`.
</details>

<details>
<summary>▶ Solución R3</summary>

```python
bajo = (altura < 0.8).astype(int)
cambios = np.diff(np.concatenate([[0], bajo, [0]]))       # rodeamos de ceros para cerrar los tramos
comienzos = np.flatnonzero(cambios == 1)
finales = np.flatnonzero(cambios == -1)
duraciones = finales - comienzos
mas_largo = duraciones.argmax()
print(f"{duraciones[mas_largo]} pasos seguidos ({duraciones[mas_largo] * 0.002:.2f} s), "
      f"del paso {comienzos[mas_largo]} al {finales[mas_largo] - 1}")
```

Es el `groupby` del P4, vectorizado. `np.diff` de una secuencia de 0 y 1 vale +1 donde empieza un tramo de unos y −1 donde termina. Añadir un 0 al principio y al final garantiza que todos los tramos tengan comienzo y final.
</details>

<details>
<summary>▶ Solución R4</summary>

```python
d = mujoco.MjData(zancudo)
velocidades = np.empty((T, zancudo.nv))
for paso in range(T):
    d.ctrl[:] = ordenes(d.time)
    mujoco.mj_step(zancudo, d)
    velocidades[paso] = d.qvel

con_gradient = np.gradient(tray[:, 3:], tiempos, axis=0)
con_diff = np.diff(tray[:, 3:], axis=0) / 0.002
print(f"gradient: error medio {np.abs(con_gradient - velocidades[:, 3:]).mean():.3f} rad/s")
print(f"diff:     error medio {np.abs(con_diff - velocidades[1:, 3:]).mean():.1e} rad/s")
print(f"aceleración media de las articulaciones: {np.abs(np.diff(velocidades[:, 3:], axis=0)).mean() / 0.002:.0f} rad/s²")
```

¡Sorpresa! `np.gradient` se equivoca en más de **1 rad/s** de media (y hasta casi 10), mientras que `np.diff` coincide con MuJoCo **exactamente** (error de 10⁻¹⁵: solo redondeo). Dos razones, y las dos son lecciones:

1. **`np.diff` coincide exactamente por cómo integra MuJoCo** (NB49): el Euler semiimplícito calcula la posición nueva **con la velocidad nueva**, `q_nuevo = q_viejo + dt · v_nuevo`. Así que `(q_nuevo − q_viejo) / dt` **es** `v_nuevo`, por definición.
2. **`np.gradient` falla porque las articulaciones vibran**: las aceleraciones medias son de más de 1.000 rad/s² (los motores de posición, muelles duros con amortiguador, corrigen sin parar a escala de pocos pasos). La diferencia centrada **promedia** la pendiente de antes y la de después, y cuando la velocidad cambia 2 rad/s de un paso al siguiente, ese promedio se aleja de la velocidad del instante.

Moraleja: para derivar datos, **conoce cómo se generaron**. Con datos de un simulador, la fórmula que coincide con su integrador es exacta; con datos de un robot real (ruidosos, NB41), ninguna derivada numérica es exacta, y suele hacer falta **filtrar** antes (P2: filtro paso bajo). (Como la simulación es determinista, NB45, la nueva simulación repite exactamente la trayectoria de la sección 2.)
</details>

<details>
<summary>▶ Solución R5</summary>

```python
def distancias_a(puntos: np.ndarray, objetivo: np.ndarray) -> tuple[np.ndarray, int]:
    distancias = np.linalg.norm(puntos - objetivo, axis=1)       # (N, 3) - (3,) → (N, 3) → (N,)
    return distancias, int(distancias.argmin())

mujoco.mj_forward(zancudo, d)
dist, cercano = distancias_a(d.xpos[1:], np.array([0.1, 0.0, 0.1]))
print(dist.round(3), "→ el más cercano:", zancudo.body(cercano + 1).name)
```

El `+ 1` corrige el desplazamiento por haber quitado el cuerpo 0 (el mundo) con `xpos[1:]`. Son los pies, cerca del suelo y del punto. (Si `d` estaba en otra postura de las celdas anteriores, el resultado puede variar; con `mj_resetData` antes, es la postura inicial.)
</details>

<details>
<summary>▶ Solución R6</summary>

```python
def energia(qd: np.ndarray, I: np.ndarray) -> float:
    return float(0.5 * np.sum(I * qd ** 2))
```

`I * qd ** 2` es elemento a elemento, y `np.sum` suma. (Si `I` fuera la matriz de masas completa, la energía cinética sería `0.5 * qd @ M @ qd`, NB45.)
</details>

<details>
<summary>▶ Solución R7</summary>

```python
r = np.array([0.0, 0.0, 0.4])
print(np.cross(r, np.array([0.0, 0.0, 10.0])))                 # paralela: [0, 0, 0]
par = np.cross(r, np.array([10.0, 0.0, 0.0]))                  # perpendicular
print(np.linalg.norm(par), np.linalg.norm(r) * 10.0)           # 4.0 4.0
```

Empujar a lo largo del brazo (como tirar de una puerta hacia sus bisagras) no produce giro; empujar perpendicular, el máximo (NB37).
</details>

<details>
<summary>▶ Solución R8</summary>

```python
Rz = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
p = np.random.default_rng(2).normal(size=(5, 3))
p_rot = p @ Rz.T

def todas_las_distancias(pts):
    return np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)

print(np.allclose(todas_las_distancias(p), todas_las_distancias(p_rot)))     # True
```

Las rotaciones (y las traslaciones) conservan las distancias: son movimientos **rígidos**. Es una forma rápida de comprobar que una matriz que has construido es de verdad una rotación (además de RᵀR = I y det = 1).
</details>

<details>
<summary>▶ Solución R9</summary>

`[ 0. 10. 20. 30.  4.]`. `b = a[1:4]` es una **vista**: `b *= 10` modifica los elementos 1, 2 y 3 de `a`. En cambio, `c = a[[1, 2]]` es una **copia** (índice con lista): `c += 1` solo cambia `c`. Las dos líneas se parecen muchísimo, y una toca el original y la otra no: por eso hay que tener la tabla de la sección 8 en la cabeza.
</details>

<details>
<summary>▶ Solución R10</summary>

`datos.qpos` no es un atributo normal: es una **propiedad** (P3) del objeto de MuJoCo. Al **leerla**, devuelve una vista de la memoria de C. Al **asignarla** (`datos.qpos = valores`), su *setter* **copia** los valores dentro de esa memoria (no sustituye el array). Así que `datos.qpos = datos.qpos + 0.1` calcula un array nuevo y el setter lo copia dentro: la simulación cambia. `datos.qpos += 0.1` modifica la vista en el sitio: también cambia.

Pero `q = datos.qpos; q = q + 0.1` solo hace que el nombre `q` apunte a un array **nuevo** que no tiene nada que ver con MuJoCo: la simulación ni se entera. Con `q += 0.1` sí cambiaría (en el sitio, sobre la vista). Es la diferencia entre **modificar un objeto** y **cambiar a qué objeto apunta un nombre**, la idea más importante de todo el modelo de memoria de Python (NB21).
</details>

<details>
<summary>▶ Solución R11</summary>

```python
import math
total = 0.0
for _ in range(10):
    total += 0.1
print(total, total == 1.0, np.isclose(total, 1.0), math.fsum([0.1] * 10))
# 0.9999999999999999 False True 1.0
```

La suma ingenua da 0,9999999999999999. **`math.fsum`** suma llevando la cuenta de los errores de redondeo de cada suma parcial y compensándolos (un algoritmo de "suma compensada"), y da el resultado correctamente redondeado: 1,0. Útil cuando sumas muchísimos números pequeños.
</details>

<details>
<summary>▶ Solución R12</summary>

```python
alt64 = 0.865 + tray[:, 1]
alt32 = (np.float32(0.865) + tray[:, 1].astype(np.float32))
dt = 0.002
v64 = np.diff(alt64) / dt
v32 = np.diff(alt32) / np.float32(dt)
print(f"diferencia máxima de posición: {np.abs(alt64 - alt32).max():.2e} m")
print(f"diferencia máxima de velocidad: {np.abs(v64 - v32).max():.2e} m/s")
```

En posición, la diferencia es del orden de 10⁻⁸ m (las 7 cifras de `float32` sobre números de ~0,86). En velocidad, unas **mil veces mayor**: al restar dos números **casi iguales** (alturas consecutivas, que se diferencian en micras), las cifras iguales se cancelan y lo que queda son, sobre todo, los errores de redondeo; y después se divide por un número pequeño (0,002), que los amplifica 500 veces. Se llama **cancelación catastrófica**, y es la razón por la que derivar datos numéricamente (y más en `float32`) es delicado: el ruido se dispara.
</details>
'''),

md(r"""## 12 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Con este notebook termina el **puente de Python**. El siguiente paso del curso es el **NB51** (Bloque B: andar sin RL): el péndulo invertido lineal, el punto de captura con fórmulas exactas, el plan de pasos y las trayectorias del pie, con NumPy vectorizado (¡que ahora ya dominas!) y gráficas profesionales.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB44p6_puente_numpy_robotica.ipynb")
    build(out, cells, title="NB44·P6 · Puente de Python (6): NumPy intermedio para robótica")
