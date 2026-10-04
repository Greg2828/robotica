"""Construye NB15 · NumPy: números a toda velocidad (Parte 2 · Lección 4).

Biblioteca = módulo grande; import numpy as np; np.array, ndarray, shape
(tupla); operaciones elemento a elemento sin bucles (y la trampa: con listas
+ concatena y 2*lista repite); sum/sqrt/linalg.norm; producto escalar con @;
ValueError de tamaños; matrices 2D (P[1, 2]), P @ obs (Segway del NB14 en una
línea); generador con semilla (default_rng), uniform size=(17,45), zeros,
clip; velocidad bucle vs @ (time.perf_counter; en la Pi ~50-100×). GRAN FINAL:
el humanoide REAL (gymnasium Humanoid-v5): reset/step ≅ reiniciar/paso del
NB11; obs (348,) con obs[0] = altura 1,39; recompensa del primer paso ≈ 5;
política lineal np.clip(W @ obs + b, ±0,4); W = 0 → 198,6 (= muñeco de trapo
del NB04); W al azar → ~58; búsqueda aleatoria de 20 matrices: mejor 141,7 <
198,6 → hace falta otra forma de aprender (pendientes).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB15 · NumPy: números a toda velocidad (y el humanoide de verdad)

**Parte 2 · Matemáticas y herramientas para robots — Lección 4**

> En el **NB14** viste que la política de un robot es una **matriz de pesos** multiplicada por la observación, y contaste
> cientos de ruedecillas. También notaste un problema: nuestras funciones con bucles funcionan, pero un entrenamiento
> tiene que hacer esas cuentas **millones** de veces. Necesitamos velocidad.

Hoy conocerás **NumPy**, la herramienta que usa **todo** el mundo que trabaja con números en Python: científicos,
ingenieros de robótica, investigadores de inteligencia artificial. Con ella, todo lo que hiciste con bucles en el NB12,
NB13 y NB14 se escribe en **una línea**, y va **decenas de veces más rápido**.

Y luego viene el momento que llevamos esperando desde el NB00: vamos a abrir, por primera vez, **el simulador de verdad**
del humanoide. Verás que su observación **es** un vector de NumPy, le aplicarás **tu propia** política lineal, y medirás
sus puntos con la recompensa real del NB04. Todo lo aprendido hasta ahora, encajando de golpe.

Una idea nueva por celda, como siempre.
"""),

md(r"""## 1 · Qué es una biblioteca

En el NB11 importaste `random` y en el NB12 `matplotlib`: cajas de herramientas (módulos). Algunas cajas son tan grandes y
tan útiles que tienen nombre propio: se llaman **bibliotecas** (o **librerías**), y las escriben y mantienen equipos de
personas de todo el mundo, durante años, gratis, para que cualquiera las use.

**NumPy** (se pronuncia "nam-pai", de *Numerical Python*, "Python numérico") es la biblioteca para trabajar con **montones de
números a la vez**: vectores, matrices y mucho más. Por dentro está escrita en otro lenguaje mucho más rápido que Python (el
lenguaje C), pero tú la manejas desde Python, con toda su comodidad. Lo mejor de los dos mundos.

Se importa así, con un apodo que usa absolutamente todo el mundo:
"""),

code(r"""import numpy as np"""),

md(r"""A partir de aquí, `np.algo` es una herramienta de NumPy. (Como `plt` para matplotlib: si ves `np.` en cualquier libro o web
de robótica o de inteligencia artificial, es NumPy.)
"""),

md(r"""## 2 · El array: la lista de NumPy

La pieza básica de NumPy es el **array** (en inglés, "formación" u "ordenación"): una lista de números con superpoderes. Se
fabrica a partir de una lista normal con `np.array(...)`:
"""),

code(r"""v = np.array([3, 4])
print(v)"""),

md(r"""Se muestra **sin comas** entre los números: así reconocerás un array de NumPy a simple vista (una lista normal se mostraría
`[3, 4]`).

Los arrays tienen un dato muy útil, su **forma** (en inglés, *shape*), que dice **cuánto mide en cada dirección**:
"""),

code(r"""print(v.shape)"""),

md(r"""`(2,)`: un array de **una dimensión** con **2** números (una flecha de 2 componentes). Esa coma suelta y los paréntesis son
la forma que tiene Python de escribir una **tupla** de un solo elemento; una tupla es como una lista que no se puede cambiar,
escrita con paréntesis. No te preocupes por ella: solo léela como "mide 2". Para una matriz de 17 × 45, la forma sería
`(17, 45)`. **Mirar la forma** es lo primero que hace un profesional cuando algo falla (recuerda la regla de los tamaños del
NB14).
"""),

md(r"""## 3 · Operaciones sin bucles

Aquí está la primera magia de NumPy. En el NB12 escribimos funciones con bucles para sumar flechas y multiplicarlas por un
número. Con arrays, **basta con los símbolos de siempre**: NumPy hace la operación **componente a componente**, él solo.

Sumar dos flechas (NB12):
"""),

code(r"""w = np.array([1.5, 2])
print(v + w)"""),

md(r"""**[4.5 6.]**: 3 + 1,5 y 4 + 2. Sin bucle, sin función `sumar`. (El `6.` es un 6 decimal; NumPy pone todos los números del
array del mismo tipo, y como 1,5 era decimal, todos pasan a serlo.)

Multiplicar por un número (NB12):
"""),

code(r"""print(2 * v)"""),

md(r"""**[6 8]**: el doble de la flecha. Y elevar al cuadrado cada componente:"""),

code(r"""print(v ** 2)"""),

md(r"""**[9 16]**. Todas las operaciones que conoces (`+`, `-`, `*`, `/`, `**`) funcionan así: **elemento a elemento**.
"""),

md(r"""### ¡Cuidado! Con listas normales no funciona igual

Esta trampa es importantísima, y engaña a muchísima gente. Mira lo que hacen los **mismos símbolos** con **listas normales** de
Python (las del NB09):
"""),

code(r"""print([3, 4] + [1, 2])
print(2 * [3, 4])"""),

md(r"""¡Nada que ver! Con listas:

- `+` **pega** una lista detrás de otra: `[3, 4, 1, 2]` (se llama **concatenar**).
- `2 *` **repite** la lista dos veces: `[3, 4, 3, 4]`.

Con arrays de NumPy:

- `+` **suma** componente a componente: `[4 6]`.
- `2 *` **multiplica** cada componente: `[6 8]`.

> **Regla:** para hacer matemáticas con vectores y matrices, usa **arrays de NumPy**, nunca listas normales. Las listas son para
> **guardar** cosas; los arrays, para **calcular**.

Y lo peor es que con las listas **no sale ningún error**: el programa sigue adelante con un resultado absurdo. Como la coma
decimal del NB05. Si alguna vez una suma de vectores te da algo con el doble de elementos, ya sabes qué ha pasado.
"""),

md(r"""## 4 · Longitud y producto escalar en una línea

¿Recuerdas la **longitud** de una flecha (NB12): los cuadrados, sumados, y la raíz? Con NumPy: `np.sum` suma todos los
elementos de un array, y `np.sqrt` (de *square root*, "raíz cuadrada") hace la raíz:
"""),

code(r"""print(np.sqrt(np.sum(v ** 2)))"""),

md(r"""**5.0**: la longitud de (3, 4), Pitágoras en una línea. Es tan común que NumPy la trae hecha, con el nombre de **norma** (que
vimos en el NB12): `np.linalg.norm` (*linalg* es de *linear algebra*, "álgebra lineal", la parte de las matemáticas que estudia
vectores y matrices: lo que estás aprendiendo en esta Parte 2).
"""),

code(r"""print(np.linalg.norm(v))"""),

md(r"""Y el **producto escalar** (NB13), la operación de las neuronas, tiene su propio símbolo en Python: la **arroba `@`**. Probemos
con el ejemplo del NB13, (2, 3) · (4, 1) = 11:
"""),

code(r"""a = np.array([2, 3])
b = np.array([4, 1])
print(a @ b)"""),

md(r"""**11**. Un símbolo en lugar de nuestra función `producto_escalar` con su bucle. (También existe `np.dot(a, b)`, que hace lo
mismo; verás las dos formas en el código de otras personas.)

Ojo, no confundas `@` con `*`: `a * b` multiplica **por parejas** y **no suma** (da otro vector, `[8 3]`); `a @ b` multiplica por
parejas **y suma** (da un número, 11). El producto escalar es `@`.
"""),

md(r"""### Y si los tamaños no encajan...

¿Qué pasa si sumamos dos arrays de tamaños distintos?"""),

code_err(r"""print(np.array([1, 2, 3]) + np.array([1, 2]))"""),

md(r"""`ValueError: operands could not be broadcast together with shapes (3,) (2,)`: "**error de valor**: no se pueden combinar
operandos de formas (3,) y (2,)". NumPy te dice exactamente las dos **formas** que no encajan. (*Broadcast* es un mecanismo de
NumPy para combinar arrays de tamaños distintos cuando tiene sentido; aquí no lo tiene.) Un nuevo tipo de error para la tabla:

| Tipo de error | Qué suele significar |
|---|---|
| `NameError`, `SyntaxError`, `IndentationError`, `IndexError`, `TypeError` | (los de siempre) |
| `ValueError` (con *shapes*) | Los **tamaños** de los arrays no encajan |
"""),

md(r"""## 5 · Matrices con NumPy

Una matriz se fabrica igual que en el NB14, con una lista de listas, pero metida en `np.array`. Recuperemos la matriz del robot de
dos ruedas del NB14:
"""),

code(r"""P = np.array([
    [-30, -8, -5],     # rueda izquierda
    [-30, -8,  5],     # rueda derecha
])
print(P)
print("Forma:", P.shape)"""),

md(r"""Se muestra como una tabla de verdad, y su forma es `(2, 3)`: 2 filas, 3 columnas. Para sacar un elemento, NumPy permite poner
fila y columna **dentro de los mismos corchetes**, separadas por una coma: `P[1, 2]` (en vez de `P[1][2]`, que también funciona):
"""),

code(r"""print(P[1, 2])"""),

md(r"""**5**, el peso del giro en la rueda derecha. Y ahora, la operación estrella del NB14, **matriz por vector**, con el **mismo
símbolo `@`**:
"""),

code(r"""observacion = np.array([2, 5, 1])
print(P @ observacion)"""),

md(r"""**[−105 −95]**: exactamente las dos acciones del NB14. Lo que allí necesitó dos funciones (`producto_escalar` y
`matriz_por_vector`, con un bucle cada una), aquí es **un símbolo**. Y la regla de los tamaños es la misma: (2, 3) @ (3,) da (2,).
"""),

md(r"""## 6 · Fabricar matrices grandes

Para la política del humanoide necesitamos matrices de 17 × 45 (o de 17 × 348). NumPy trae herramientas para fabricarlas de golpe,
sin bucles anidados.

**Números al azar.** NumPy tiene su propio generador de azar, que se crea con una **semilla** (como `random.seed` del NB11: misma
semilla, mismo azar). Luego se le pide una matriz entera de números al azar, diciendo su **forma** con `size`:
"""),

code(r"""generador = np.random.default_rng(0)
W = generador.uniform(-0.1, 0.1, size=(17, 45))
print("Forma:", W.shape, "| número total de pesos:", W.size)"""),

md(r"""Una matriz 17 × 45 de pesos al azar entre −0,1 y 0,1, en una línea. `W.size` cuenta **todos** sus números: 17 × 45 = **765**
(el bucle anidado del NB14, en una palabra).

**Ceros.** `np.zeros(...)` fabrica un array lleno de ceros de la forma que le digas. Por ejemplo, los 17 sesgos de la política,
empezando en cero:
"""),

code(r"""sesgos = np.zeros(17)
print(sesgos)"""),

md(r"""**Recortar.** Y la función `recortar` del NB14, para todos los números a la vez: `np.clip(array, mínimo, máximo)`. Mira cómo deja
cada número dentro de ±0,4:
"""),

code(r"""print(np.clip(np.array([-0.7, 0.1, 0.55]), -0.4, 0.4))"""),

md(r"""El −0,7 pasa a −0,4; el 0,1 se queda; el 0,55 pasa a 0,4. (*Clip* significa "recortar", como recortar con unas tijeras lo que
sobresale.)

Con estas tres herramientas, **la política lineal completa del humanoide** (NB14) se escribe en **una línea**:

```python
acciones = np.clip(W @ observacion + sesgos, -0.4, 0.4)
```

Matriz por observación, más sesgos, recortado. Enseguida la usaremos con el robot de verdad.
"""),

md(r"""## 7 · ¿Cuánto más rápido?

Hemos dicho que NumPy es "mucho más rápido". Un ingeniero no se lo cree: **lo mide** (como hiciste con los pasos del simulador en el
NB07). Vamos a calcular un producto escalar de dos vectores de **un millón** de números, primero con un bucle de Python y luego con
NumPy, y a cronometrar las dos cosas.

Para cronometrar usamos el módulo **`time`** ("tiempo"): `time.perf_counter()` da la hora exacta del reloj del ordenador, con mucha
precisión. Se mira el reloj antes y después, y se resta (NB06). Primero, los dos vectores (los fabricamos con NumPy, que es más
rápido, y los copiamos también como listas normales con `.tolist()`):
"""),

code(r"""import time

generador = np.random.default_rng(1)
a_numpy = generador.uniform(-1, 1, size=1_000_000)
b_numpy = generador.uniform(-1, 1, size=1_000_000)

a_lista = a_numpy.tolist()
b_lista = b_numpy.tolist()
print("Dos vectores de", len(a_lista), "números")"""),

md(r"""(Fíjate en `1_000_000`: Python permite poner **guiones bajos** dentro de un número para que se lea mejor, como los puntos de los
miles en castellano. `1_000_000` es un millón. Recuerda que el **punto** no se puede usar, porque es el decimal: NB05.)

Y ahora, la carrera:
"""),

code(r"""inicio = time.perf_counter()
total = 0
for i in range(len(a_lista)):
    total = total + a_lista[i] * b_lista[i]
tiempo_bucle = time.perf_counter() - inicio

inicio = time.perf_counter()
total_numpy = a_numpy @ b_numpy
tiempo_numpy = time.perf_counter() - inicio

print("Bucle de Python:", round(tiempo_bucle, 4), "segundos")
print("NumPy:          ", round(tiempo_numpy, 4), "segundos")
print("NumPy ha sido", round(tiempo_bucle / tiempo_numpy), "veces más rápido")
print("¿Mismo resultado?", round(total, 6) == round(total_numpy, 6))"""),

md(r"""**El mismo resultado, decenas de veces más rápido.** (Los tiempos exactos cambian cada vez que se ejecuta, y de un ordenador a
otro; en la Raspberry Pi en la que se preparó el curso, NumPy suele salir entre **50 y 120 veces** más rápido. Lo que importa es el
orden de magnitud.)

Piensa lo que eso significa para entrenar un robot: un entrenamiento que con bucles de Python tardara **un mes**, con NumPy podría
tardar **unas horas**. Y las herramientas profesionales de entrenamiento (que veremos más adelante) van todavía más allá: usan la
**tarjeta gráfica** del ordenador, que hace miles de estas cuentas **a la vez**. Por eso el entrenamiento pesado del curso irá a
ordenadores con tarjeta gráfica, como los de Google Colab.
"""),

md(r"""## 8 · El gran momento: el humanoide de verdad

Llevamos quince lecciones hablando de él. Lo viste desplomarse en un GIF (NB00), desmontaste su cuerpo (NB01), conociste su simulador
(NB02), su observación y su acción (NB03), su recompensa (NB04). Hoy, por fin, **lo vas a manejar tú**.

El humanoide vive en una biblioteca llamada **Gymnasium** (del inglés: "gimnasio", un sitio para **entrenar**). Gymnasium es el
estándar para entornos de aprendizaje por refuerzo: contiene muchos mundos (el humanoide, un robot de cuatro patas, el carro con
péndulo que inspiró nuestro palo de escoba, NB11...) y todos se manejan **igual**. Por dentro, el humanoide usa **MuJoCo** (NB02) para
la física.

Se importa con su apodo habitual, `gym`, y se **crea** el entorno por su nombre:
"""),

code(r"""import gymnasium as gym

entorno = gym.make("Humanoid-v5")"""),

md(r"""No sale nada, pero acabas de crear un mundo de mentira con un humanoide dentro. ("v5" es la versión 5 de este entorno; lo van
mejorando con los años.)

Ahora, lo primero de todo episodio: **reiniciar** (como la función `reiniciar` de tu palo de escoba). En Gymnasium se llama **`reset`**
("reiniciar"), y se le puede dar una semilla para que el robot aparezca siempre igual. Devuelve **dos** cosas: la observación inicial y
un paquete de información extra (que no usaremos):
"""),

code(r"""observacion, info = entorno.reset(seed=0)

print("Tipo:", type(observacion))
print("Forma:", observacion.shape)"""),

md(r"""**Es un array de NumPy**, con forma **(348,)**: la observación **completa** del humanoide que mencionamos en el NB03 (los 45 números
básicos más todos los extra). Una flecha de 348 dimensiones, tal y como dijimos en el NB12.

Mira sus **primeros cinco números**:
"""),

code(r"""print(np.round(observacion[:5], 3))"""),

md(r"""(`observacion[:5]` es una porción, NB09: de la posición 0 hasta antes de la 5. Si no se pone el inicio, se entiende que es 0.
`np.round` redondea todo el array de golpe.)

¿Ves el **1,391** del principio? Es la **altura del torso**, en metros. ¡El robot aparece de pie con el torso a unos 1,4 metros, justo
el número que usamos en el NB08 para simular la caída! Y los cuatro siguientes (0,99; 0,006; 0,008; 0,002) son los "**4 números** que
describen hacia dónde está inclinado y girado el torso" del NB03. Ese casi-1 seguido de casi-ceros significa: **derecho, sin inclinar**.

¿Y la acción? El entorno nos dice su forma:
"""),

code(r"""print("Forma de la acción:", entorno.action_space.shape)"""),

md(r"""**(17,)**: los 17 motores del NB01. Todo cuadra con lo que sabías.
"""),

md(r"""## 9 · Un paso del humanoide

Para dar un paso, se le pasa una acción a **`step`** ("paso"), exactamente como la función `paso` de tu palo de escoba. Probemos con
los 17 motores **a cero** (el "muñeco de trapo" del NB04):
"""),

code(r"""accion = np.zeros(17)
observacion, recompensa, terminado, truncado, info = entorno.step(accion)

print("Recompensa del paso:", round(recompensa, 3))
print("¿Terminado?", terminado, "| ¿Truncado?", truncado)
print("Altura del torso ahora:", round(observacion[0], 3))"""),

md(r"""`step` devuelve **cinco** cosas. Compáralas con tu función `paso` del NB11, que devolvía cuatro:

| Tu palo de escoba (NB11) | El humanoide (Gymnasium) |
|---|---|
| `reiniciar()` | `entorno.reset(seed=...)` |
| `paso(inclinacion, velocidad, empuje)` | `entorno.step(accion)` |
| devuelve inclinación y velocidad (la observación) | devuelve `observacion` (348 números) |
| devuelve `recompensa` | devuelve `recompensa` |
| devuelve `terminado` (¿se cayó?) | devuelve `terminado` (¿el torso bajó de 1 m? NB03) |
| (el truncado lo hacía el bucle de 500 pasos) | devuelve `truncado` (¿llegó a 1.000 pasos?) |
| | devuelve `info` (información extra) |

**Es el mismo diseño que construiste tú.** Has estado aprendiendo, sin saberlo, exactamente cómo funcionan los entornos
profesionales. (Una diferencia: aquí el entorno **recuerda** su estado por dentro, así que a `step` solo hay que pasarle la acción.)

¿Y la recompensa, **5,002**? Es el **+5 por seguir de pie** del NB04, más un poquito por el movimiento del centro de masas, menos casi nada
de esfuerzo (los motores están a cero). La recompensa real, funcionando tal y como la desmontamos a mano.
"""),

md(r"""## 10 · Tu política lineal, contra el humanoide

Vamos a jugar episodios enteros. Una función como el `episodio` del NB11, pero con el humanoide de verdad y con **tu política lineal**
de una línea (apartado 6). Recibe la matriz de pesos `W`, los sesgos `b` y una semilla, y devuelve el retorno y los pasos aguantados:
"""),

code(r"""def episodio(W, b, semilla):
    observacion, info = entorno.reset(seed=semilla)
    retorno = 0
    pasos = 0
    for n in range(1000):
        accion = np.clip(W @ observacion + b, -0.4, 0.4)       # TU POLÍTICA
        observacion, recompensa, terminado, truncado, info = entorno.step(accion)
        retorno = retorno + recompensa
        pasos = pasos + 1
        if terminado or truncado:
            break
    return retorno, pasos

def evaluar(W, b):
    retornos = []
    for semilla in range(5):
        retorno, pasos = episodio(W, b, semilla)
        retornos.append(retorno)
    return np.mean(retornos)        # la media, con NumPy"""),

md(r"""**Primera política: todos los pesos a cero.** Con `W` y `b` a cero, la acción siempre es cero: el muñeco de trapo. La matriz tiene
que medir 17 × **348** (17 motores, 348 números de observación):
"""),

code(r"""W_ceros = np.zeros((17, 348))
b_ceros = np.zeros(17)

retorno, pasos = episodio(W_ceros, b_ceros, 0)
print("Un episodio:", round(retorno, 1), "puntos en", pasos, "pasos")
print("Media de 5 episodios:", round(evaluar(W_ceros, b_ceros), 1))"""),

md(r"""**198,6 puntos de media, aguantando 40 pasos.** ¡Es **exactamente** el "muñeco de trapo" que medimos en el NB04 (~198 puntos, ~40
pasos)! Pero esta vez no te lo he contado yo: lo acabas de medir **tú**, con tu propio código, contra el simulador de verdad.

**Segunda política: pesos al azar.** Un robot recién nacido, con sus 5.933 ruedecillas (NB14) en posiciones cualesquiera:
"""),

code(r"""generador = np.random.default_rng(0)
W_azar = generador.uniform(-0.1, 0.1, size=(17, 348))

print("Media de 5 episodios:", round(evaluar(W_azar, b_ceros), 1))
retorno, pasos = episodio(W_azar, b_ceros, 0)
print("Un episodio:", round(retorno, 1), "puntos en", pasos, "pasos")"""),

md(r"""Unos **58 puntos**, y se cae en unos **13 pasos**. **Peor que no hacer nada**, igual que el robot al azar del NB04 y la política al
azar del palo de escoba (NB11). Una política con ruedecillas al azar **sacude** al robot y lo tira antes.
"""),

md(r"""## 11 · ¿Y si probamos al azar, como con el palo de escoba?

En el NB11, la búsqueda aleatoria encontró una política casi perfecta en dos intentos. Hagamos lo mismo con el humanoide: **20
matrices al azar**, cada una evaluada en 5 episodios, quedándonos con la mejor:
"""),

code(r"""generador = np.random.default_rng(42)
mejor = -1
for intento in range(20):
    W = generador.uniform(-0.05, 0.05, size=(17, 348))
    puntos = evaluar(W, b_ceros)
    if puntos > mejor:
        mejor = puntos
    print("intento", intento, "->", round(puntos, 1))

print()
print("La mejor de 20 políticas al azar:", round(mejor, 1))
print("No hacer nada:                    ", round(evaluar(W_ceros, b_ceros), 1))"""),

md(r"""La mejor de las 20 saca unos **142 puntos**. **Ni siquiera supera a no hacer nada** (198,6). Y desde luego, ninguna anda: todas se
caen en menos de un segundo.

Es la **maldición de la dimensionalidad** (NB03, NB14) vista con tus propios ojos, en el robot de verdad. Con **2** ruedecillas, probar
al azar funcionaba. Con **5.933**, no hay suerte que valga.

Antes de cerrar, una buena costumbre: cuando terminas de usar un entorno, se **cierra**, para liberar la memoria que usaba el simulador:
"""),

code(r"""entorno.close()"""),

md(r"""## 12 · Dónde estamos

Recapitulemos lo que has conseguido en esta lección:

- Sabes usar **NumPy**: arrays, operaciones sin bucles, `@` para productos escalares y matrices, y has **medido** que es decenas de veces
  más rápido.
- Has abierto **el simulador de verdad**: Gymnasium + MuJoCo, con `reset` y `step`, y has comprobado que su diseño es **el mismo** que el
  de tu palo de escoba.
- Has visto la **observación real** (348 números; el primero, la altura del torso), la **acción real** (17 números) y la **recompensa
  real** (el +5 del NB04, funcionando).
- Has aplicado **tu política lineal** al humanoide y has medido: ceros → 198,6 (el muñeco de trapo del NB04, reproducido); al azar → ~58;
  la mejor de 20 al azar → ~142.

Y has llegado a la pregunta central de todo el curso, con datos en la mano: **¿cómo se ajustan miles de ruedecillas a la vez, si probar al
azar no sirve ni para igualar a no hacer nada?**

La respuesta es la idea más importante de la inteligencia artificial moderna, y empieza en el **NB16**: las **pendientes**. En vez de girar
las ruedecillas a ciegas, para cada una nos preguntaremos: **"si la giro un poquito, ¿la cosa mejora o empeora?"**. Y la giraremos hacia
donde mejora. Paso a paso, cuesta arriba, hacia la cima de la montaña del NB04.
"""),

md(r"""## 13 · Resumen de la lección

1. **NumPy** (`import numpy as np`) es la biblioteca de los números rápidos. Su pieza básica es el **array** (`np.array`), con su **forma**
   (`.shape`). Con arrays, `+ - * / **` actúan **elemento a elemento**; con **listas normales**, `+` **concatena** y `2 *` **repite**.
2. `np.sum`, `np.sqrt`, `np.linalg.norm` (longitud), y **`@`** para el producto escalar y para **matriz por vector**. Si las formas no
   encajan: `ValueError`.
3. Para fabricar: `np.random.default_rng(semilla).uniform(..., size=(filas, columnas))`, `np.zeros(...)`, y `np.clip` para recortar. La
   política lineal del humanoide: `np.clip(W @ observacion + b, -0.4, 0.4)`.
4. NumPy es **decenas de veces más rápido** que un bucle de Python (medido con `time.perf_counter`).
5. **Gymnasium** (`gym.make("Humanoid-v5")`): `reset` → observación (array de 348; `[0]` = altura del torso); `step(accion)` → observación,
   recompensa, terminado, truncado, info. Pesos a cero: **198,6** (el muñeco de trapo); al azar: **~58**; la mejor de 20 al azar: **~142**.
   Hace falta una forma más lista de aprender.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Biblioteca / librería** | Un módulo grande, mantenido por mucha gente, como NumPy o matplotlib. |
| **NumPy (`np`)** | La biblioteca de Python para calcular con montones de números a la vez. |
| **Array** | La "lista con superpoderes" de NumPy, para calcular. |
| **Forma (`shape`)** | Cuánto mide un array en cada dirección: `(2,)`, `(17, 45)`. |
| **Tupla** | Una lista que no se puede cambiar, escrita con paréntesis. |
| **Elemento a elemento** | Una operación que se hace con cada componente por separado. |
| **Concatenar** | Pegar una lista detrás de otra (lo que hace `+` con listas normales). |
| **`@`** | El producto escalar / matriz por vector. |
| **`ValueError`** | Error por un valor que no encaja (en NumPy, a menudo, formas distintas). |
| **`np.clip`** | Recorta todos los números de un array a un rango. |
| **`time.perf_counter`** | El reloj de precisión para cronometrar código. |
| **Gymnasium (`gym`)** | La biblioteca estándar de entornos de aprendizaje por refuerzo. |
| **`reset` / `step`** | Reiniciar el entorno / dar un paso con una acción. |
"""),

md(r"""## 14 · Ejercicios

**E1.** Predice qué muestra cada línea y luego compruébalo: `print([1, 2] + [3, 4])` y `print(np.array([1, 2]) + np.array([3, 4]))`.

**E2.** Con NumPy, calcula la longitud de la flecha (6, 8) en una línea. ¿Coincide con el E3 del NB12?

**E3.** ¿Qué forma tiene `np.zeros((3, 5))`? ¿Cuántos números tiene en total (`.size`)? ¿Qué forma tendría el resultado de multiplicarla
(`@`) por un vector de 5 números?

**E4.** Reescribe el detector de caídas del NB13 con NumPy: la salida de la neurona es `pesos @ entradas + sesgo`. Comprueba que con pesos
`np.array([1, 0.3])`, sesgo −10 y entradas `np.array([5, 30])` sale 4.

**E5.** Con el humanoide: ¿qué pasa si **todos** los motores empujan siempre a tope, `np.full(17, 0.4)` (un array de 17 números, todos
0,4)? ¿Y a tope hacia el otro lado, `np.full(17, -0.4)`? Mide el retorno medio de las dos políticas. Pista: puedes hacer `W = 0` y poner
la acción en los sesgos: `b = np.full(17, 0.4)`. (Recuerda crear el entorno otra vez, porque lo cerramos.)

**E6.** **Reto.** Repite el cronometraje del apartado 7 con vectores de **10 millones** de números. ¿Cuánto tarda cada uno? ¿La proporción
se mantiene? (Ojo: el bucle de Python puede tardar unos segundos.)
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

- `[1, 2] + [3, 4]` → **`[1, 2, 3, 4]`**: con listas, `+` **concatena** (pega una detrás de otra).
- `np.array([1, 2]) + np.array([3, 4])` → **`[4 6]`**: con arrays, `+` **suma** componente a componente.
</details>

<details>
<summary>▶ Solución E2</summary>

```python
print(np.linalg.norm(np.array([6, 8])))
```

Salida: **10.0**, igual que el E3 del NB12 (el triángulo 6-8-10).
</details>

<details>
<summary>▶ Solución E3</summary>

`np.zeros((3, 5))` tiene forma **(3, 5)**: 3 filas y 5 columnas, **15** números en total. Multiplicada por un vector de 5 números (que
encaja con sus 5 columnas), da un vector de forma **(3,)**: un número por fila.
</details>

<details>
<summary>▶ Solución E4</summary>

```python
pesos = np.array([1, 0.3])
entradas = np.array([5, 30])
sesgo = -10
print(pesos @ entradas + sesgo)
```

Salida: **4.0** (1 × 5 + 0,3 × 30 − 10 = 5 + 9 − 10). Positivo: ¡salta la alarma!, como en el NB13.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
entorno = gym.make("Humanoid-v5")
print("Todo a +0,4:", round(evaluar(W_ceros, np.full(17, 0.4)), 1))
print("Todo a -0,4:", round(evaluar(W_ceros, np.full(17, -0.4)), 1))
entorno.close()
```

Con **todo a +0,4** sale unos **237** puntos (aguanta unos 47 pasos): ¡**más** que el muñeco de trapo! Con **todo a −0,4**, unos **45**
(se cae en 12 pasos). Una política que no mira **nada** (siempre la misma acción) ya cambia cuánto aguanta el robot: según hacia dónde
tensa los músculos, cae antes o después. ¿Recuerdas la tabla del NB00? "Un poco [de práctica]: ha descubierto que tensar las piernas
ayuda; se queda rígido y cae algo más tarde". ¡Es esto! Ninguna de las dos anda, claro: los 237 puntos son casi todos el +5 por seguir
de pie, unos pasos más.
</details>

<details>
<summary>▶ Solución E6</summary>

Cambia `size=1_000_000` por `size=10_000_000` en las dos líneas. Los dos tiempos se multiplican aproximadamente por **10** (diez veces
más números, diez veces más trabajo), así que la proporción entre ellos se mantiene parecida: NumPy sigue siendo decenas de veces más
rápido. En la Raspberry Pi, el bucle de Python tardará del orden de un par de segundos; NumPy, unas centésimas. (Si un día trabajas con
cien millones de números, el bucle tardaría ya medio minuto o más... y en un entrenamiento hay que hacer cuentas así una y otra vez.)
</details>
"""),

md(r"""## 15 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy ha sido un día grande: has manejado **el humanoide de verdad** con tu propio código, y has comprobado con datos reales casi todo lo que
la Parte 0 te contó con palabras. Y has llegado al muro: miles de ruedecillas que no se pueden ajustar probando al azar.

Antes, el **NB15b** te dará unas cuantas herramientas de matemáticas que usaremos muy pronto (mover funciones, la exponencial, el logaritmo). Y en el **NB16** empezamos a derribarlo. Volveremos a la montaña con niebla del NB04, y aprenderemos a hacer la pregunta clave: **¿hacia
dónde sube el terreno?**. Es la idea de **pendiente** (los matemáticos la llaman **derivada**), explicada desde cero, con dibujos y sin
fórmulas que asusten. Con ella, en lugar de dar palos de ciego, el robot sabrá **hacia dónde girar cada ruedecilla** para mejorar.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB15_numpy.ipynb")
    build(out, cells, title="NB15 · NumPy: números a toda velocidad")
