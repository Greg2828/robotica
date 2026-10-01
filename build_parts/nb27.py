"""Construye NB27 · Python de verdad (8): NumPy a fondo, tests y Git (cierra el bloque).

NumPy a fondo: dtype (float64 vs float32, astype), fábricas (arange, linspace,
ones, full, eye, normal), forma (ndim, reshape con -1, ravel, .T), índices 2D
(M[i, j], M[:, j], porciones), máscaras booleanas y np.where, argmax/argsort,
EJES (tabla políticas × semillas: mean por axis), BROADCASTING (normalizar
observaciones por columnas; reglas; ValueError real), apilar (stack,
concatenate), VISTAS vs copias (la trampa del alias en NumPy). Proyecto:
1.000 palos de escoba a la vez (vectorizar con máscaras): a mano 499,9,
solo inclinación 339,2 con ~63 % de caídas (vs 3/5 con 5 semillas), 10-20×
más rápido que el bucle. Tests: por qué, assert, pytest (escribir test_palo.py
y ejecutarlo con subprocess), comparar decimales (pytest.approx /
np.testing.assert_allclose), un test que caza un fallo. Git: conceptos
(repositorio, commit, historial, diff, rama, remoto), práctica real en un
repositorio de juguete (init, add, commit, log, diff, branch, merge),
.gitignore, el historial de este curso, buenas costumbres. Estilo (PEP 8) y
cierre del bloque de Python.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB27 · Python de verdad (8): NumPy a fondo, tests y Git

**Parte 3 · Python de verdad — Lección 8 (cierre del bloque)**

> Última lección del bloque de Python. Ya sabes manejar texto, colecciones, errores, funciones, clases, ficheros, módulos y la terminal.
> Hoy cerramos con las tres herramientas que te faltan para trabajar en un equipo profesional de robótica.

1. **NumPy a fondo.** En el NB15 viste lo básico. Pero el día a día con redes neuronales y simuladores es, sobre todo, **manejar arrays**: sus
   tipos, sus formas, sus ejes... y evitar sus trampas. Lo veremos todo, y lo usaremos para simular **mil palos de escoba a la vez**, que es
   exactamente la idea con la que se entrenan los humanoides de verdad.
2. **Tests.** Programas que **comprueban** que tu código funciona, para que un cambio de hoy no rompa en silencio lo que funcionaba ayer.
3. **Git.** La herramienta con la que **todo** el mundo guarda el historial de su código y trabaja en equipo. Este mismo curso vive en Git.

Como en el NB26, las prácticas con ficheros irán a una carpeta `practica_nb27`.
"""),

md(r"""## 1 · El tipo de los números: `dtype`

Todos los números de un array de NumPy son **del mismo tipo**, y ese tipo se llama su **`dtype`** (*data type*). Los dos más importantes en robótica:"""),

code(r"""import numpy as np

a = np.array([1.5, 2.0, 3.25])
b = a.astype(np.float32)          # convertir a otro tipo
print(a.dtype, "->", a.nbytes, "bytes")
print(b.dtype, "->", b.nbytes, "bytes")"""),

md(r"""- **`float64`** (el normal): cada número ocupa 8 bytes y tiene unas 16 cifras de precisión. Es lo que da NumPy por defecto.
- **`float32`**: cada número ocupa **la mitad** (4 bytes) y tiene unas 7 cifras de precisión.

¿Por qué importa? Porque las **tarjetas gráficas** (con las que se entrenan las redes y los robots en paralelo) trabajan casi siempre en **`float32`**: la mitad de
memoria y muchísimo más rápido, y 7 cifras de precisión son más que suficientes para una red neuronal. Por eso los espacios de Gymnasium (NB25) piden `float32`, y
por eso las redes de PyTorch usan `float32` por defecto. **Mezclar tipos** es una fuente clásica de errores y avisos (por ejemplo, Gymnasium avisa si tu entorno
devuelve `float64` cuando su espacio dice `float32`).

`astype` convierte un array a otro tipo (devolviendo uno **nuevo**). Y cuidado con los enteros: un array de enteros (`dtype` `int64`) **corta** los decimales si
metes un decimal en él.
"""),

md(r"""## 2 · Fábricas de arrays

Además de `np.array`, `np.zeros` y `np.linspace` (NB15, NB19), hay muchas formas de fabricar arrays:"""),

code(r"""print(np.arange(0, 1, 0.25))         # como range, pero admite decimales
print(np.ones(3))                     # todo unos
print(np.full(3, 0.4))                # todo un valor
print(np.eye(3))                      # la matriz IDENTIDAD: unos en la diagonal

generador = np.random.default_rng(0)
print(generador.normal(0, 1, size=4).round(2))   # números al azar "en campana" (la veremos en la parte de probabilidad)"""),

md(r"""La **matriz identidad** (`np.eye`) es la que, multiplicada por un vector, lo deja **igual** (como multiplicar un número por 1). Aparece mucho con las rotaciones (en la parte de física).
"""),

md(r"""## 3 · La forma: `reshape`, `ravel` y la traspuesta

Un array tiene un número de **dimensiones** (`ndim`), una **forma** (`shape`) y un número total de elementos (`size`). Y se puede **reorganizar** en otra forma con el mismo
número de elementos, con **`reshape`**:
"""),

code(r"""x = np.arange(12)
print(x, "| ndim:", x.ndim, "| shape:", x.shape)

tabla = x.reshape(3, 4)               # los mismos 12 números, en 3 filas y 4 columnas
print(tabla)
print("ndim:", tabla.ndim, "| shape:", tabla.shape, "| size:", tabla.size)"""),

md(r"""Un truco muy usado: poner **`-1`** en una de las dimensiones significa "**calcúlala tú**":"""),

code(r"""print(x.reshape(-1, 6).shape)         # 6 columnas, y las filas que salgan (2)
print(tabla.ravel())                  # de vuelta a una sola fila ("aplanar")
print(tabla.T)                        # la TRASPUESTA: las filas pasan a ser columnas
print(tabla.T.shape)"""),

md(r"""La **traspuesta** (`.T`) "gira" la tabla: lo que eran filas son columnas y al revés, así que una forma (3, 4) pasa a (4, 3). Aparece constantemente en las fórmulas de las redes
neuronales (la retropropagación del NB18-19, escrita con matrices, está llena de `.T`).

¿Y si pides una forma imposible?
"""),

code_err(r"""x.reshape(5, 3)"""),

md(r"""`ValueError: cannot reshape array of size 12 into shape (5,3)`: no se pueden meter 12 números en 5 × 3 = 15 huecos. El tamaño total tiene que coincidir.
"""),

md(r"""## 4 · Índices en dos dimensiones

En una tabla, `M[fila, columna]` (NB15). Y con porciones (`:`) en cada dimensión se cogen filas enteras, columnas enteras o trozos:"""),

code(r"""print(tabla)
print("fila 1:       ", tabla[1])
print("columna 2:    ", tabla[:, 2])          # ":" = todas las filas; 2 = la columna 2
print("trozo:\n", tabla[0:2, 1:3])           # filas 0-1, columnas 1-2
print("última columna:", tabla[:, -1])"""),

md(r"""`tabla[:, 2]` se lee "**todas** las filas, columna 2": la columna entera. Es la forma de sacar, por ejemplo, **todas las inclinaciones** de una tabla de observaciones donde cada fila
es un paso y cada columna un dato.
"""),

md(r"""## 5 · Máscaras: filtrar con condiciones

Una comparación con un array da **un array de `True` y `False`**, uno por elemento (lo viste en el NB19, con `zs > 0`). Se llama **máscara**, y se puede usar **como índice** para quedarse
solo con los elementos donde vale `True`:
"""),

code(r"""retornos = np.array([44.8, 499.9, 168.5, 499.7, 296.0, 43.2])

buenos = retornos > 400
print(buenos)
print(retornos[buenos])                       # solo los que cumplen
print("¿Cuántos?", buenos.sum(), "| proporción:", buenos.mean())"""),

md(r"""`retornos[retornos > 400]` filtra en una línea, sin bucle ni comprensión. Y como `True` vale 1 y `False` vale 0, **`.sum()`** cuenta los que cumplen, y **`.mean()`** da la **proporción**
(aquí, 2 de 6). Las máscaras se combinan con **`&`** ("y"), **`|`** ("o") y **`~`** ("no"), siempre con paréntesis: `(retornos > 100) & (retornos < 400)`.

Para **elegir** entre dos valores según una condición, elemento a elemento, **`np.where(condición, si_cierto, si_falso)`** (lo viste en el ejercicio E6 del NB19):
"""),

code(r"""print(np.where(retornos > 400, "completo", "caído"))"""),

md(r"""Y para saber **dónde** está el mayor o en qué orden van los elementos: **`argmax`** (la **posición** del mayor) y **`argsort`** (las posiciones que **ordenarían** el array):"""),

code(r"""print("El mejor está en la posición", retornos.argmax())
orden = retornos.argsort()[::-1]                 # de mayor a menor (NB21: [::-1] da la vuelta)
print("Posiciones de mejor a peor:", orden)
print("Retornos ordenados:        ", retornos[orden])"""),

md(r"""¿Has visto `retornos[orden]`? Un array se puede usar como índice con **una lista de posiciones**, y devuelve esos elementos en ese orden. Muy útil: si tienes los retornos y las
políticas en dos arrays paralelos, `politicas[retornos.argsort()]` ordena las políticas por su retorno.
"""),

md(r"""## 6 · Los ejes: hacer cuentas por filas o por columnas

Esta es, quizá, la idea más importante de NumPy para el trabajo diario. Imagina una tabla de resultados: cada **fila** es una política, cada **columna** una semilla (los retornos del
NB11):
"""),

code(r"""resultados = np.array([
    [41.6,  46.2,  43.1,  45.3,  47.6],      # nada
    [499.7, 168.5, 144.5, 198.8, 468.3],     # solo inclinación
    [499.9, 499.9, 499.9, 499.9, 499.9],     # a mano
])
print(resultados.shape)
print("Media de TODO:", resultados.mean().round(1))"""),

md(r"""`mean()` a secas da la media de **todos** los números juntos, que no significa gran cosa. Lo que queremos es la media **de cada política** (de cada fila), o **de cada semilla** (de cada
columna). Para eso, las funciones de NumPy aceptan un **eje** (`axis`):
"""),

code(r"""print("Media por política (axis=1):", resultados.mean(axis=1).round(1))
print("Media por semilla  (axis=0):", resultados.mean(axis=0).round(1))
print("Peor episodio de cada política:", resultados.min(axis=1))"""),

md(r"""La regla para no liarse: **el eje que dices es el que desaparece**. La tabla es (3 políticas, 5 semillas):

```
                      ← axis=1 (a lo largo de las semillas, "hacia la derecha") →
                    semilla 0  semilla 1  semilla 2  semilla 3  semilla 4
   ↑   nada            41.6      46.2      43.1      45.3      47.6     → mean(axis=1) = 44.8
 axis=0 inclinación   499.7     168.5     144.5     198.8     468.3     → mean(axis=1) = 296.0
   ↓   a mano         499.9     499.9     499.9     499.9     499.9     → mean(axis=1) = 499.9
                        ↓         ↓         ↓         ↓         ↓
                    mean(axis=0): una media por semilla (5 números)
```

- `axis=1` **recorre** las columnas (las semillas) y las **resume**: queda un número por fila → forma (3,).
- `axis=0` **recorre** las filas (las políticas) y las resume: queda un número por columna → forma (5,).

Funciona igual con `sum`, `max`, `min`, `std` (la desviación típica), `argmax`... **Siempre que una cuenta te salga con la forma equivocada, revisa el `axis`.**
"""),

md(r"""## 7 · Broadcasting: operar con formas distintas

En el NB15 viste que sumar arrays de formas **distintas** daba un `ValueError` con la palabra *broadcast*. Pero a veces NumPy **sí** combina formas distintas, y con mucha inteligencia: estira
la más pequeña para que encaje. Se llama **broadcasting** ("difusión"). El caso más simple ya lo conoces: `2 * array` "estira" el 2 a todo el array.

El caso más útil en robótica: **normalizar las observaciones**. Las redes neuronales aprenden mucho mejor si cada dato de la observación está "centrado en 0" y con un tamaño parecido (la
inclinación del palo va de −30 a 30, pero su velocidad puede ir de −100 a 100: muy distintos). Se hace restando a **cada columna** su media y dividiendo entre su desviación típica:
"""),

code(r"""generador = np.random.default_rng(1)
observaciones = np.column_stack([generador.normal(5, 2, size=6),        # columna 0: inclinaciones
                                 generador.normal(-40, 30, size=6)])    # columna 1: velocidades
print("Forma:", observaciones.shape)

media = observaciones.mean(axis=0)            # una media por columna: forma (2,)
desviacion = observaciones.std(axis=0)        # una desviación por columna: forma (2,)
normalizadas = (observaciones - media) / desviacion    # ¡(6, 2) menos (2,)!

print("Media de cada columna, antes:  ", media.round(2))
print("Media de cada columna, después:", normalizadas.mean(axis=0).round(2))
print("Desviación, después:           ", normalizadas.std(axis=0).round(2))"""),

md(r"""(`np.column_stack` pega varios arrays como columnas de una tabla.) La línea clave es `observaciones - media`: una tabla de forma **(6, 2)** menos un vector de forma **(2,)**. NumPy "repite"
el vector en cada una de las 6 filas, así que a cada fila se le resta la media de **su** columna. Resultado: cada columna, centrada en 0 y con desviación 1. **Esto se hace de verdad** al
entrenar robots (lo verás como "normalización de observaciones").

Las **reglas** del broadcasting: NumPy compara las formas **empezando por la derecha**; cada pareja de tamaños tiene que ser **igual**, o **uno de ellos ser 1** (o no existir). (6, 2) y (2,):
a la derecha, 2 y 2, iguales; a la izquierda, 6 y "nada", vale. Si no se cumple:
"""),

code_err(r"""observaciones - np.array([1.0, 2.0, 3.0])"""),

md(r"""(6, 2) y (3,): a la derecha, 2 contra 3, ni iguales ni 1. Error. **El broadcasting es potentísimo, pero también peligroso**: a veces encaja formas que **no** querías combinar, y el
resultado es un array de forma inesperada **sin ningún error**. Por eso, la costumbre profesional del NB22: **mirar siempre `.shape`**.
"""),

md(r"""## 8 · Apilar arrays

Para juntar arrays: **`np.stack`** los apila creando una dimensión **nueva**, y **`np.concatenate`** los pega a lo largo de una dimensión **existente**:"""),

code(r"""paso1 = np.array([2.0, 0.0])
paso2 = np.array([2.02, 0.81])
paso3 = np.array([2.05, 1.55])

trayectoria = np.stack([paso1, paso2, paso3])         # 3 observaciones de 2 -> tabla (3, 2)
print(trayectoria.shape)
print(np.concatenate([paso1, paso2]))                # pegadas en fila -> (4,)"""),

md(r"""`np.stack` es lo que se usa para convertir una **lista de observaciones** (las que vas guardando paso a paso, NB09) en una **tabla**, una fila por paso. Así se preparan los datos para
entrenar.
"""),

md(r"""## 9 · La trampa del alias en NumPy: vistas

En el NB21 viste la trampa del alias con las listas. NumPy tiene **su propia versión**, más sutil. Una **porción** de un array **no es una copia**: es una **vista**, una "ventana" a los mismos
datos. Si cambias la porción, **cambias el original**:
"""),

code(r"""pesos = np.zeros(6)
primeros = pesos[0:3]          # ¡una VISTA, no una copia!
primeros[0] = 99
print(pesos)"""),

md(r"""¡El 99 aparece en `pesos`! (Con una lista normal, `lista[0:3]` **sí** sería una copia; NumPy funciona distinto a propósito, para no gastar memoria copiando arrays enormes.) Si necesitas
una copia independiente, **`.copy()`**:
"""),

code(r"""pesos = np.zeros(6)
primeros = pesos[0:3].copy()
primeros[0] = 99
print(pesos)"""),

md(r"""Ahora `pesos` sigue intacto. **Dónde muerde**: guardas los pesos "buenos" de una red con `mejores = pesos[...]` para recuperarlos luego, sigues entrenando... y los "buenos" han cambiado con
el entrenamiento, porque eran una vista. **Al guardar un estado para después, siempre `.copy()`.** (Las máscaras y las listas de posiciones del apartado 5, en cambio, sí devuelven copias.)
"""),

md(r"""## 10 · Proyecto: mil palos de escoba a la vez

Y ahora, la aplicación más potente de todo lo anterior. Hasta ahora simulábamos los episodios **de uno en uno**, con bucles de Python. Pero ¿y si simulamos **mil palos a la vez**? En vez de una
inclinación, un **array** de mil inclinaciones; en vez de un viento, un array de mil vientos. Y la física se aplica a **todos a la vez**, con operaciones de NumPy. Se llama **vectorizar**.

La única dificultad: cada palo se cae en un momento distinto. Lo resolvemos con una **máscara** de "vivos": los caídos dejan de sumar recompensa. Léelo despacio; cada línea es algo de hoy:
"""),

code(r"""def evaluar_en_paralelo(k, d, n_palos=1000, semilla=0, viento_maximo=30):
    generador = np.random.default_rng(semilla)
    inclinacion = np.full(n_palos, 2.0)          # mil inclinaciones (apartado 2)
    velocidad = np.zeros(n_palos)
    vivos = np.ones(n_palos, dtype=bool)         # una máscara: todos empiezan vivos
    retornos = np.zeros(n_palos)

    for paso in range(500):
        empuje = np.clip(-k * inclinacion - d * velocidad, -40, 40)       # la política, para los mil
        viento = generador.uniform(-viento_maximo, viento_maximo, size=n_palos)
        aceleracion = 10 * inclinacion + empuje + viento                   # la física, para los mil
        velocidad = velocidad + aceleracion * 0.02
        inclinacion = inclinacion + velocidad * 0.02
        vivos = vivos & (np.abs(inclinacion) <= 30)                        # los que caen, dejan de estar vivos
        retornos = retornos + np.where(vivos, 1 - (inclinacion / 30) ** 2, 0.0)

    return retornos

import time
for nombre, k, d in [("nada", 0, 0), ("solo inclinación", 30, 0), ("a mano", 30, 8)]:
    inicio = time.perf_counter()
    retornos_mil = evaluar_en_paralelo(k, d)
    duracion = time.perf_counter() - inicio
    caidos = (retornos_mil < 490).mean()
    print(f"{nombre:>17}: media {retornos_mil.mean():6.1f} | peor {retornos_mil.min():6.1f} | "
          f"se cae el {caidos:5.1%} | {duracion * 1000:.0f} ms")"""),

md(r"""**Mil episodios en unas pocas centésimas de segundo** por política. Y los resultados nos enseñan algo importante:

- "a mano": **499,9** de media y de **peor caso**: no se cae **ninguna** de las mil veces.
- "solo inclinación": se cae alrededor de **dos de cada tres** veces (en torno al 63 %). Con nuestras 5 semillas del NB11 parecía un 60 % (3 de 5)... y con otras 5 semillas, en el NB25, salió
  bastante mejor. **Cinco episodios son muy pocos para medir algo con fiabilidad.** Con mil, el número ya es de fiar. (La estadística, en la próxima parte, nos dirá exactamente **cuánto** fiarnos.)

Comparémoslo con la versión de bucles de toda la vida, para la política a mano, con los mismos mil episodios:
"""),

code(r"""import random

def evaluar_con_bucles(k, d, n_episodios=1000):
    total = 0
    for semilla in range(n_episodios):
        azar = random.Random(semilla)
        inclinacion, velocidad = 2.0, 0.0
        for paso in range(500):
            empuje = max(-40, min(40, -k * inclinacion - d * velocidad))
            velocidad += (10 * inclinacion + empuje + azar.uniform(-30, 30)) * 0.02
            inclinacion += velocidad * 0.02
            if abs(inclinacion) > 30:
                break
            total += 1 - (inclinacion / 30) ** 2
    return total / n_episodios

inicio = time.perf_counter()
media_bucles = evaluar_con_bucles(30, 8)
duracion_bucles = time.perf_counter() - inicio

inicio = time.perf_counter()
media_paralelo = evaluar_en_paralelo(30, 8).mean()
duracion_paralelo = time.perf_counter() - inicio

print(f"Con bucles:    {media_bucles:.1f} en {duracion_bucles * 1000:.0f} ms")
print(f"En paralelo:   {media_paralelo:.1f} en {duracion_paralelo * 1000:.0f} ms")
print(f"Unas {duracion_bucles / duracion_paralelo:.0f} veces más rápido")"""),

md(r"""El mismo resultado, **entre diez y veinte veces más rápido** (el número exacto cambia en cada ejecución). Y con más palos la ventaja crece.

**Esta es exactamente la idea de los simuladores profesionales para entrenar humanoides** (lo veremos en la Parte 5): en vez de un robot, simulan **miles a la vez**, con arrays enormes, en la
tarjeta gráfica. Por eso un entrenamiento que llevaría semanas con un robot cada vez se hace en minutos. Acabas de escribir, en pequeño, un **entorno vectorizado**.
"""),

md(r"""## 11 · Tests: programas que comprueban tu código

Imagina que cambias una línea de la física del palo de escoba para "mejorarla"... y sin darte cuenta rompes algo. Todo sigue funcionando, no hay errores, pero los resultados ya no son correctos.
Puedes tardar días en darte cuenta. Los **tests** (o **pruebas**) evitan esto: son pequeñas funciones que **comprueban automáticamente** que tu código hace lo que debe. Cada vez que cambias algo,
los ejecutas, y si algo se ha roto, **te lo dicen al instante**.

Un test es, en el fondo, un **`assert`** (NB22) dentro de una función:

```python
def test_reset_empieza_inclinado():
    entorno = PaloDeEscoba()
    (inclinacion, velocidad), info = entorno.reset(seed=0)
    assert inclinacion == 2.0
    assert velocidad == 0.0
```

La herramienta estándar para ejecutar tests en Python se llama **pytest**. Su funcionamiento es sencillísimo: busca ficheros cuyo nombre empiece por `test_`, dentro de ellos las funciones que
empiecen por `test_`, las ejecuta todas, y te dice cuáles pasan y cuáles fallan.

Vamos a escribir un fichero de tests para el módulo `palo.py` del NB26 (lo copiamos a nuestra carpeta de prácticas):
"""),

code(r"""from pathlib import Path
import shutil

carpeta = Path("practica_nb27")
carpeta.mkdir(exist_ok=True)
origen = Path("practica_nb26") / "palo.py"
if not origen.exists():
    raise FileNotFoundError("Ejecuta primero el NB26: este apartado usa el módulo palo.py que se crea allí.")
shutil.copy(origen, carpeta / "palo.py")          # shutil: copiar ficheros (biblioteca estándar)
print("palo.py copiado")"""),

md(r"""(Fíjate en el `raise` con un mensaje claro si falta el fichero: fallar pronto, NB22.) Y ahora, el fichero de tests:"""),

code(r"""tests = '''# test_palo.py: tests del entorno del palo de escoba.
import pytest
from palo import PaloDeEscoba, evaluar


def test_reset_empieza_inclinado():
    entorno = PaloDeEscoba()
    (inclinacion, velocidad), info = entorno.reset(seed=0)
    assert inclinacion == 2.0
    assert velocidad == 0.0


def test_misma_semilla_mismo_resultado():
    # reproducibilidad: dos evaluaciones con las mismas semillas dan lo mismo
    assert evaluar(30, 8) == evaluar(30, 8)


def test_recompensa_entre_0_y_1():
    entorno = PaloDeEscoba()
    entorno.reset(seed=3)
    for paso in range(100):
        obs, recompensa, terminado, truncado, info = entorno.step(0)
        assert 0.0 <= recompensa <= 1.0
        if terminado:
            break


def test_no_hacer_nada_se_cae():
    assert evaluar(0, 0) < 100


def test_politica_a_mano_aguanta():
    assert evaluar(30, 8) == pytest.approx(499.93, abs=0.05)
'''
(carpeta / "test_palo.py").write_text(tests, encoding="utf-8")
print("Tests escritos")"""),

md(r"""Cinco tests, cada uno comprueba **una** cosa, con un nombre que dice **qué**. Fíjate en el último: **`pytest.approx`**. Comparar decimales con `==` es peligroso (el ruido de los decimales del
NB06: `0.1 + 0.2 == 0.3` es `False`). `pytest.approx(valor, abs=0.05)` significa "aproximadamente este valor, con un margen de 0,05". (NumPy tiene su equivalente para arrays:
`np.testing.assert_allclose`.)

Ejecutémoslos. En una terminal escribirías `pytest` en la carpeta; desde aquí, con `subprocess` (NB26):
"""),

code(r"""import subprocess, sys

def ejecutar_tests():
    resultado = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--color=no"],
                               cwd=carpeta, capture_output=True, text=True)
    print(resultado.stdout.strip()[-600:])

ejecutar_tests()"""),

md(r"""**`5 passed`**: los cinco tests pasan. (Cada punto `.` es un test que ha ido bien. `-q` pide un resumen corto, y `-p no:cacheprovider` evita que pytest deje una carpeta de caché.)

Ahora, lo importante: **¿cazan los tests un fallo?** Vamos a "estropear" `palo.py` a propósito, como si alguien hubiera cambiado sin querer la gravedad de 10 a 1 (un error de una sola tecla), y
volvemos a ejecutar los tests:
"""),

code(r"""ruta_palo = carpeta / "palo.py"
original = ruta_palo.read_text(encoding="utf-8")
_ = ruta_palo.write_text(original.replace("10 * self.inclinacion", "1 * self.inclinacion"), encoding="utf-8")

ejecutar_tests()

_ = ruta_palo.write_text(original, encoding="utf-8")   # lo dejamos como estaba"""),

md(r"""**`1 failed, 4 passed`**: el test `test_no_hacer_nada_se_cae` ha **fallado**. Con una gravedad diez veces más débil, el palo ya no se cae aunque no hagas nada, y el test lo ha detectado
**al instante**, diciendo **qué test** falló y **por qué** (pytest muestra el `assert` que no se cumplió, con los valores). Sin el test, ese error de una tecla podría haber pasado desapercibido
durante semanas.

**Costumbres profesionales con los tests:**

- Cada test comprueba **una** cosa, con un nombre que diga **qué**.
- Se ejecutan **antes de subir cualquier cambio**. En las empresas, se ejecutan solos cada vez que alguien sube código (se llama **integración continua**).
- Cuando encuentras un fallo, **primero escribes un test que lo reproduzca**, y luego lo arreglas: así ese fallo no vuelve jamás.
- En robótica, se prueban cosas como: que el entorno sea **reproducible** con la misma semilla, que las observaciones tengan la **forma** y el **tipo** correctos, que las recompensas estén en su
  rango, y que una política conocida dé el resultado esperado.
"""),

md(r"""## 12 · Git: el historial de tu código

Llevas todo el curso viendo que "este notebook se sube a GitHub". Ahora vas a entender qué es eso.

**Git** es un programa de **control de versiones**: guarda el **historial completo** de un proyecto. Cada vez que llegas a un punto que merece la pena (un notebook terminado, un fallo arreglado),
haces una **"foto"** de todos los ficheros, con un mensaje que explica qué cambiaste. Esa foto se llama **commit** ("confirmación"). Con Git puedes:

- **Volver atrás** a cualquier foto anterior (si rompes algo, recuperas la versión buena).
- **Ver qué cambió** entre dos fotos, línea a línea (el **diff**, "diferencia").
- **Trabajar en paralelo** en una **rama** (*branch*): una línea de trabajo separada para probar algo sin tocar lo principal, y **fusionarla** (*merge*) si sale bien.
- **Trabajar en equipo**: una copia del proyecto vive en un servidor **remoto** (como **GitHub**), y cada persona **sube** (*push*) y **baja** (*pull*) los cambios.

Los conceptos, en una tabla:

| Concepto | Qué es |
|---|---|
| **Repositorio** | La carpeta del proyecto, con todo su historial (en una carpeta oculta `.git`) |
| **Commit** | Una "foto" de los ficheros, con un mensaje, una fecha y un autor |
| **Área de preparación** (*staging*) | Donde eliges qué cambios van en el próximo commit (`git add`) |
| **Rama** (*branch*) | Una línea de trabajo; la principal suele llamarse `main` |
| **Remoto** | Una copia del repositorio en otro sitio (GitHub) |
| **`push` / `pull`** | Subir tus commits al remoto / bajar los de los demás |

Vamos a practicar con un **repositorio de juguete** dentro de nuestra carpeta de prácticas. Una pequeña función para lanzar órdenes de Git (con `subprocess`, NB26):
"""),

code(r"""repo = carpeta / "mi_robot"
if repo.exists():
    shutil.rmtree(repo)               # empezamos de cero cada vez (rmtree borra una carpeta entera)
repo.mkdir()

def git(*ordenes):
    resultado = subprocess.run(["git", *ordenes], cwd=repo, capture_output=True, text=True)
    salida = (resultado.stdout + resultado.stderr).strip()
    if salida:
        print(salida)

git("init", "-q", "-b", "main")                             # crear el repositorio, con la rama 'main'
git("config", "user.name", "Alumno de robótica")           # quién firma los commits (solo en este repositorio)
git("config", "user.email", "alumno@ejemplo.com")"""),

md(r"""`git init` ha convertido la carpeta en un repositorio (vacío; `-q` le pide que no diga nada). `git config` dice quién firma los commits (cada persona lo configura una vez en su ordenador; aquí lo hacemos solo para este
repositorio de juguete). Ahora creamos un fichero, lo **preparamos** con `git add` y hacemos el **primer commit**:
"""),

code(r"""(repo / "politica.py").write_text("K = 30\nD = 8\n", encoding="utf-8")

git("add", "politica.py")                                   # 1. preparar el fichero para la foto
git("commit", "-q", "-m", "Primera política: k=30, d=8")   # 2. hacer la foto, con su mensaje
git("log", "--oneline")                                     # 3. ver el historial"""),

md(r"""El historial ya tiene **un commit**, identificado por un código (los primeros caracteres de un número larguísimo, único para cada commit) y su mensaje. Cambiemos el fichero y veamos qué ha
cambiado **antes** de hacer la siguiente foto, con `git diff`:
"""),

code(r"""(repo / "politica.py").write_text("K = 25\nD = 6\n", encoding="utf-8")
git("diff")"""),

md(r"""El **diff** muestra, línea a línea, lo que ha cambiado: las líneas con **`-`** delante son las que se han quitado y las de **`+`**, las que se han añadido. Las ruedecillas pasaron de 30 y 8 a 25 y
6. Es la herramienta que usan los equipos para **revisar** los cambios de los demás antes de aceptarlos. Hagamos el segundo commit:
"""),

code(r"""git("commit", "-q", "-am", "Ruedecillas aprendidas por el gradiente (NB17): k=25, d=6")
git("log", "--oneline")"""),

md(r"""(`-am` = añadir todos los ficheros ya conocidos que hayan cambiado, y hacer el commit, en un paso.) Dos fotos en el historial, de la más reciente a la más antigua.

Ahora, una **rama**: queremos **probar** una idea arriesgada (unas ruedecillas enormes) **sin tocar** la versión buena. Creamos una rama, cambiamos el fichero allí, y hacemos un commit en ella:
"""),

code(r"""git("switch", "-q", "-c", "prueba-ruedecillas-grandes")    # crear una rama nueva y cambiarse a ella
(repo / "politica.py").write_text("K = 80\nD = 20\n", encoding="utf-8")
git("commit", "-q", "-am", "Probar ruedecillas grandes")

git("switch", "-q", "main")                                 # volver a la rama principal
print("En main, el fichero dice:", (repo / "politica.py").read_text(encoding="utf-8").split())
git("log", "--oneline", "--all", "--decorate")"""),

md(r"""Al volver a `main`, el fichero vuelve a tener **25 y 6**: la prueba vive **solo** en su rama. El historial (con `--all`, que muestra todas las ramas, y `--decorate`,
que pone las etiquetas) lo enseña: el commit de la prueba lleva la etiqueta de su rama, `prueba-ruedecillas-grandes`, y `main` (con `HEAD`, "donde estás ahora") sigue en el commit
anterior. Si la prueba saliera bien, se **fusionaría** con
`git merge prueba-ruedecillas-grandes`; si sale mal, se abandona la rama, y `main` nunca se enteró. Así trabajan los equipos: cada idea, en su rama; a `main`, solo lo que funciona.

### El `.gitignore`

No todo debe ir al historial. Las carpetas enormes o que se pueden regenerar (como el entorno virtual `venv`), las cachés, y **sobre todo las contraseñas y claves secretas**, se excluyen con un fichero
**`.gitignore`**: una lista de patrones de ficheros que Git debe ignorar. Mira el de este curso:
"""),

code(r"""print(Path("..", ".gitignore").read_text(encoding="utf-8"))"""),

md(r"""Ahí están `venv/` (el entorno virtual, NB26), las cachés de Python (`__pycache__/`) y las carpetas de prácticas como esta (`notebooks/practica_*/`). **Regla de oro: jamás subas contraseñas, claves de
APIs ni datos privados a Git.** Aunque los borres después, siguen en el historial.

### Este curso, en Git

Este mismo curso es un repositorio de Git, y cada notebook terminado ha sido un commit. Mira los últimos:
"""),

code(r"""historial = subprocess.run(["git", "log", "--oneline", "-5"], cwd="..", capture_output=True, text=True).stdout
print(historial)"""),

md(r"""Los últimos commits del curso: cada lección, una foto. Y desde ahí, `git push` los sube a GitHub, de donde los lees en otro dispositivo.

Las órdenes de Git que usarás a diario:

| Orden | Qué hace |
|---|---|
| `git status` | ¿Qué ha cambiado y qué está preparado? (la orden más usada) |
| `git add fichero` | Preparar cambios para el próximo commit |
| `git commit -m "mensaje"` | Hacer la foto |
| `git log --oneline` | Ver el historial |
| `git diff` | Ver los cambios aún no confirmados |
| `git switch -c rama` / `git switch rama` | Crear una rama y cambiarse / cambiarse a una rama |
| `git merge rama` | Traer los cambios de otra rama a la actual |
| `git clone URL` | Descargar un repositorio entero (por ejemplo, de GitHub) |
| `git pull` / `git push` | Bajar / subir cambios del remoto |

Y un consejo sobre los **mensajes**: que digan **qué** y **por qué**, en una línea clara ("Arregla la recompensa: el castigo por esfuerzo tenía el signo cambiado"). Un historial con mensajes como
"cambios" o "arreglo" no sirve de nada dentro de seis meses.
"""),

md(r"""## 13 · Escribir código como un profesional

Para terminar el bloque, las costumbres que distinguen el código profesional. Casi todas ya las has visto a lo largo del curso:

- **Estilo PEP 8**: la guía de estilo oficial de Python. Nombres `en_minusculas_con_guiones` para variables y funciones, `CadaPalabraConMayuscula` para clases, `MAYUSCULAS` para constantes (NB11);
  **4 espacios** de sangría; líneas no demasiado largas; espacios alrededor de `=` y de los operadores. Hay herramientas que lo comprueban y lo arreglan solas.
- **Nombres que expliquen** (NB06): `velocidad_hacia_delante`, no `v`.
- **Funciones pequeñas que hacen una sola cosa**, con docstring (NB23).
- **Nada de números mágicos** (NB06): constantes con nombre o configuración.
- **Fallar pronto** con mensajes claros (NB22).
- **Reproducibilidad** (NB11, NB26): semillas fijas, configuración guardada, versiones apuntadas en `requirements.txt`.
- **Tests** para lo importante, y **Git** para todo.
- **Comentarios que explican el porqué**, no el qué (el código ya dice el qué).
- **Simple antes que ingenioso**: el código se lee muchas más veces de las que se escribe.
"""),

md(r"""## 14 · Resumen de la lección (y del bloque)

1. **NumPy a fondo**: `dtype` (`float32` para tarjetas gráficas; `astype`), fábricas (`arange`, `ones`, `full`, `eye`, `normal`), forma (`reshape` con `-1`, `ravel`, `.T`), índices 2D (`M[:, j]`), **máscaras**
   (`x[x > 400]`, `.sum()`, `.mean()`, `np.where`), `argmax`/`argsort`.
2. **Ejes**: `mean(axis=1)` resume cada fila, `axis=0` cada columna (el eje que dices desaparece). **Broadcasting**: formas distintas que encajan comparando desde la derecha (normalizar observaciones).
   **Vistas**: una porción de un array **no** es una copia; usa `.copy()`.
3. **Vectorizar**: mil palos de escoba a la vez, con máscaras de "vivos", entre diez y veinte veces más rápido; y la lección de que **5 episodios no bastan para medir** ("solo inclinación" se cae ~63 % de las veces).
4. **Tests** con **pytest** (funciones `test_...` con `assert`, `pytest.approx` para decimales): cazan al instante un fallo de una sola tecla.
5. **Git**: commits (fotos con mensaje), `add`/`commit`/`log`/`diff`, ramas (`switch -c`, `merge`), remotos (`push`/`pull`), `.gitignore` (jamás secretos). Y el estilo profesional (PEP 8 y buenas costumbres).

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **`dtype`** | El tipo de los números de un array (`float64`, `float32`, `int64`...). |
| **Traspuesta (`.T`)** | La tabla "girada": filas por columnas. |
| **Matriz identidad** | La que deja igual a un vector al multiplicarlo (`np.eye`). |
| **Máscara** | Array de `True`/`False` para filtrar otro array. |
| **Eje (`axis`)** | La dimensión a lo largo de la que se hace una cuenta. |
| **Broadcasting** | Operar con arrays de formas distintas que NumPy hace encajar. |
| **Normalizar observaciones** | Centrar cada dato en 0 y con tamaño 1, para que la red aprenda mejor. |
| **Vista** | Una porción de un array que comparte los datos con el original. |
| **Vectorizar** | Hacer con arrays, de golpe, lo que se haría con un bucle. |
| **Test / pytest** | Función que comprueba el código / la herramienta para ejecutarlas. |
| **Integración continua** | Ejecutar los tests automáticamente cada vez que se sube código. |
| **Git / repositorio / commit** | Control de versiones / proyecto con historial / una "foto" del proyecto. |
| **Diff** | Las diferencias, línea a línea, entre dos versiones. |
| **Rama / merge** | Una línea de trabajo separada / fusionarla con otra. |
| **Remoto / push / pull** | Copia en un servidor (GitHub) / subir / bajar cambios. |
| **PEP 8** | La guía de estilo oficial de Python. |
"""),

md(r"""## 15 · Ejercicios

**E1.** Crea con `np.arange` y `reshape` una tabla de 4 filas y 5 columnas con los números del 0 al 19. Saca la tercera columna y la última fila.

**E2.** Con la tabla `resultados` del apartado 6, calcula la **desviación típica** de cada política (`std` con el `axis` correcto). ¿Cuál es la más irregular?

**E3.** Predice la forma del resultado: (a) un array (100, 17) menos uno (17,); (b) un (100, 17) por uno (100,). ¿Funciona el (b)? ¿Por qué? (Pista: reglas del broadcasting.)

**E4.** Con `retornos = np.array([44.8, 499.9, 168.5, 499.7, 296.0, 43.2])`, cuenta con una máscara cuántos están **entre** 100 y 400.

**E5.** Explica por qué este código da un resultado inesperado y arréglalo:

```python
mejores = pesos[0:5]
pesos[0:5] = 0      # seguimos entrenando...
print(mejores)      # ¿los mejores pesos?
```

**E6.** Usa `evaluar_en_paralelo` para medir qué porcentaje de las veces se cae la política con ruedecillas (8, 8). ¿Y con (12, 8)? (NB11, E2.)

**E7.** Añade a `test_palo.py` un test `test_viento_cero_y_derecho_no_se_mueve` que compruebe que, sin viento (`PaloDeEscoba(viento_maximo=0)`) y con el palo **perfectamente derecho**, no se mueve.
(Pista: tras el `reset`, pon `entorno.inclinacion = 0.0` y da un paso con empuje 0.)

**E8.** ¿Qué tres cosas **nunca** deberían ir en un repositorio de Git? ¿Cómo se evita que vayan?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
t = np.arange(20).reshape(4, 5)
print(t[:, 2])      # [ 2  7 12 17]
print(t[-1])        # [15 16 17 18 19]
```
</details>

<details>
<summary>▶ Solución E2</summary>

```python
print(resultados.std(axis=1).round(1))
```

Una desviación por política (`axis=1`: se resumen las semillas de cada fila). La más irregular, con mucha diferencia, es "solo inclinación" (unos 152): a veces aguanta y a veces cae enseguida. "A mano" tiene
desviación **0**: siempre da lo mismo.
</details>

<details>
<summary>▶ Solución E3</summary>

(a) (100, 17) − (17,): desde la derecha, 17 y 17 encajan → resultado **(100, 17)** (a cada fila se le resta el vector). (b) (100, 17) × (100,): desde la derecha, **17 contra 100**: ni iguales ni 1 → **error**. Para
multiplicar cada **fila** por un número distinto, el vector tendría que tener forma (100, 1): `v.reshape(-1, 1)`. Entonces, desde la derecha, 17 contra 1 (vale) y 100 contra 100 (vale).
</details>

<details>
<summary>▶ Solución E4</summary>

```python
retornos = np.array([44.8, 499.9, 168.5, 499.7, 296.0, 43.2])
print(((retornos > 100) & (retornos < 400)).sum())     # 2
```

Los paréntesis alrededor de cada comparación son obligatorios con `&`.
</details>

<details>
<summary>▶ Solución E5</summary>

`pesos[0:5]` es una **vista**: `mejores` y `pesos` comparten los datos. Al poner `pesos[0:5] = 0`, `mejores` también se llena de ceros. Arreglo: `mejores = pesos[0:5].copy()`.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
for k, d in [(8, 8), (12, 8)]:
    r = evaluar_en_paralelo(k, d)
    print(k, d, f"{(r < 490).mean():.1%}")
```

Con (8, 8) se cae el **100 %** de las veces (la ruedecilla no vence a la "gravedad" de 10); con (12, 8), el **0 %**: ni una sola caída en mil episodios. Con mil episodios, la frontera del NB11 se ve con toda claridad.
</details>

<details>
<summary>▶ Solución E7</summary>

Añade al texto de `tests`:

```python
def test_viento_cero_y_derecho_no_se_mueve():
    entorno = PaloDeEscoba(viento_maximo=0)
    entorno.reset(seed=0)
    entorno.inclinacion = 0.0
    (inclinacion, velocidad), r, terminado, truncado, info = entorno.step(0)
    assert inclinacion == 0.0
    assert velocidad == 0.0
```

Sin viento, sin empuje y sin inclinación, ninguna fuerza actúa: el palo se queda quieto (la inercia del NB02). Vuelve a escribir el fichero y ejecuta `ejecutar_tests()`: debería decir `6 passed`.
</details>

<details>
<summary>▶ Solución E8</summary>

1. **Contraseñas, claves de APIs y datos privados** (lo más grave: aunque se borren, quedan en el historial).
2. **Entornos virtuales** (`venv/`): enormes, y solo sirven en tu ordenador; se sube el `requirements.txt`.
3. **Ficheros generados** que se pueden volver a crear (cachés, `__pycache__/`, resultados temporales, carpetas de prácticas).

Se evita con un fichero **`.gitignore`** con sus patrones, y revisando `git status` antes de cada commit.
</details>
"""),

md(r"""## 16 · Posdata: se acaba el bloque de Python

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

**Enhorabuena: has terminado el bloque "Python de verdad".** Mira todo lo que sabes ahora: texto y f-strings, colecciones y la trampa del alias, `while` y excepciones, depurar, funciones a fondo
(cierres, decoradores, generadores), clases y herencia, tu propio entorno de Gymnasium, ficheros y formatos, módulos, scripts, la terminal, `pip`, NumPy a fondo con ejes y broadcasting, entornos
vectorizados, tests y Git. **Es, sin exagerar, el Python que se usa en un trabajo de verdad.** A partir de aquí, el código de las bibliotecas profesionales dejará de parecer magia.

En la **Parte 4** vuelve la robótica, a lo grande: el **aprendizaje por refuerzo de verdad**. Empezaremos por la **probabilidad desde cero** (la campana de Gauss que ya ha asomado hoy), para construir
políticas que **exploran** con azar; y con ella, el primer algoritmo que aprende **solo con recompensas**, sin maestro: **REINFORCE**. Después vendrán PyTorch, actor-crítico y PPO, el algoritmo con el que
se entrenan los humanoides. Y lo entrenaremos sobre **tu** palo de escoba, el entorno de Gymnasium del NB25.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB27_python_numpy_tests_git.ipynb")
    build(out, cells, title="NB27 · Python de verdad (8): NumPy a fondo, tests y Git")
