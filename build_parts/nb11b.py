"""Construye NB11b · Python que vas a ver (Parte 1 · lección intermedia, antes de la Parte 2).

Añadida tras la auditoría de 2026-10-04: desde el NB12 aparecían argumentos con
nombre, tuplas, listas de listas, el operador in, atributos sin paréntesis y
from ... import sin haberlos explicado. Argumentos con nombre (y por qué),
valores por defecto en tus funciones, tuplas (paréntesis, desempaquetar,
tupla de uno, en un for), listas de listas (índice doble, recorrer), in y
not in, métodos frente a atributos (math.pi, "hola".upper()), módulos:
import, import ... as, from ... import, y cómo leer una llamada larga.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB11b · Python que vas a ver

**Parte 1 · Primeros pasos con Python — Lección intermedia (entre el NB11 y el NB12)**

> Con la Parte 1 has aprendido lo esencial de Python: `print`, variables, bucles, `if`, listas y funciones, y con eso has hecho aprender a un palo de escoba. En la Parte 2 llegan las matemáticas (vectores, matrices, pendientes) y las herramientas para dibujarlas y calcularlas. Y con ellas aparecerá código con **formas nuevas** que todavía no te he presentado: `figsize=(5, 5)`, `datos.shape`, `[[0.6, 0.1], [0.2, 0.3]]`, `if paso in [1, 2, 5]`, `from math import sqrt`...

Esta lección presenta esas formas **antes** de que las necesites, una a una y con calma, para que en la Parte 2 puedas concentrarte en las matemáticas. Son seis ideas pequeñas:

1. **Argumentos con nombre**: `round(3.14159, ndigits=2)`.
2. **Tuplas**: `(5, 5)`, listas que no se pueden cambiar.
3. **Listas de listas**: `[[1, 2], [3, 4]]`.
4. El operador **`in`**: "¿está esto dentro de aquello?".
5. **Métodos y atributos**: `lista.append(x)` frente a `math.pi`.
6. Las formas de **importar**: `import ... as ...` y `from ... import ...`.
"""),

md(r"""## 1 · Argumentos con nombre

### Lo que ya sabes

En el NB10 aprendiste que una función recibe **argumentos**, que se emparejan con sus **parámetros** por **orden**: el primero con el primero, el segundo con el segundo. Por ejemplo, `round` (NB06) recibe el número y cuántos decimales quieres:
"""),

code(r"""print(round(3.14159, 2))"""),

md(r"""### Llamar a los argumentos por su nombre

Los parámetros de una función tienen **nombre**, y Python permite usarlo al llamarla, escribiendo `nombre=valor`. El segundo parámetro de `round` se llama `ndigits` ("número de cifras"):
"""),

code(r"""print(round(3.14159, ndigits=2))"""),

md(r"""Hace exactamente lo mismo, pero ahora se **lee** qué significa ese 2. A esto se le llama **argumento con nombre** (o *keyword argument*). Las ventajas:

- **Se lee mejor**: `round(x, ndigits=2)` dice qué es el 2; `round(x, 2)` hay que saberlo.
- **El orden da igual**: con nombre, cada valor va a su parámetro aunque lo escribas en otro orden.
- **Puedes saltarte parámetros**: muchas funciones tienen parámetros **opcionales** (con un valor que se usa si no dices nada) y, con nombres, eliges solo el que te interesa.

Un ejemplo que ya conoces: `print`. Tiene un parámetro opcional, `sep` ("separador"), que dice qué poner **entre** las cosas que imprime (por defecto, un espacio), y otro, `end`, que dice qué poner **al final** (por defecto, un salto de línea):
"""),

code(r"""print("cadera", "rodilla", "tobillo")
print("cadera", "rodilla", "tobillo", sep=" → ")
print("sin salto de línea...", end=" ")
print("...y sigo en la misma línea")"""),

md(r"""La regla de escritura: en una llamada, **primero** los argumentos sin nombre (por orden) y **después** los que llevan nombre. `print(sep=" → ", "cadera")` da error.

### Valores por defecto en tus funciones

¿Cómo hace una función para tener parámetros opcionales? Escribiendo un **valor por defecto** con `=` en el `def`:
"""),

code(r"""def recompensa(velocidad, esfuerzo, peso_vida=5.0):
    return peso_vida + 1.25 * velocidad - 0.1 * esfuerzo

print(recompensa(1.0, 0.2))                     # usa peso_vida = 5.0
print(recompensa(1.0, 0.2, peso_vida=0.0))      # sin el premio por estar vivo (la trampa del NB04)"""),

md(r"""Si no le das `peso_vida`, vale 5. Si se lo das, usa el tuyo. En la Parte 2 verás llamadas como `plt.figure(figsize=(5, 5))` o `uniform(-1, 1, size=10)`: son exactamente esto, funciones con parámetros opcionales que se eligen por su nombre. (Hay mucho más que contar sobre parámetros; lo verás a fondo en el NB23.)
"""),

md(r"""## 2 · Tuplas

### Una lista que no se puede cambiar

Una **tupla** es una colección de valores, como una lista, pero escrita entre **paréntesis** en vez de corchetes, y con una diferencia importante: **no se puede cambiar** después de crearla (no se le añaden, quitan ni cambian elementos).
"""),

code(r"""tamano = (5, 3)                 # una tupla: 5 de ancho, 3 de alto
print(tamano)
print(tamano[0], tamano[1])     # se lee como una lista: con índices desde 0
print(len(tamano))"""),

code_err(r"""tamano[0] = 10"""),

md(r"""`TypeError: 'tuple' object does not support item assignment`: "las tuplas no permiten asignar elementos". Ese es su sentido: se usan para agrupar cosas que **van juntas y no deben cambiar**, como las dos medidas de un dibujo `(ancho, alto)`, las coordenadas de un punto `(x, y)` o el tamaño de una tabla `(filas, columnas)`.

### Ya las has usado sin saberlo

En el NB10, una función devolvía **dos** valores con `return a, b`, y los recogías con `x, y = funcion()`. Por dentro, `return a, b` devuelve una **tupla**: los paréntesis son opcionales cuando no hay confusión. Y "recoger" cada valor en su variable se llama **desempaquetar**:
"""),

code(r"""punto = (0.3, 0.8)
x, y = punto                    # desempaquetar: x recibe el primero, y el segundo
print("x =", x, "| y =", y)"""),

md(r"""### Tuplas en un bucle

Una forma muy común (la verás en la Parte 2): una **lista de tuplas** recorrida con un `for` que desempaqueta cada tupla en dos variables a la vez:
"""),

code(r"""pruebas = [("lenta", 0.01), ("buena", 0.1), ("rápida", 0.5)]
for nombre, tasa in pruebas:
    print(nombre, "→", tasa)"""),

md(r"""En cada vuelta, el `for` coge una tupla, por ejemplo `("lenta", 0.01)`, y la desempaqueta: `nombre` recibe `"lenta"` y `tasa` recibe `0.01`.

### La tupla de un solo elemento

Un detalle raro que verás algún día: `(5)` **no** es una tupla, es solo el número 5 entre paréntesis (como en las cuentas, NB04b). Para una tupla de un elemento hay que poner una **coma**: `(5,)`. Lo que hace la tupla es la coma, más que los paréntesis.
"""),

md(r"""## 3 · Listas de listas

### Una lista puede contener listas

Los elementos de una lista pueden ser **cualquier cosa**: números, textos... y también **otras listas**. Una lista de listas sirve para guardar datos en forma de **tabla** (filas y columnas). Por ejemplo, tres pasos de un robot, cada uno con su avance en x y en y:
"""),

code(r"""pasos = [[0.6, 0.1],
         [0.4, -0.2],
         [0.5, 0.0]]
print(len(pasos), "pasos")
print("el segundo paso:", pasos[1])
print("su avance en y: ", pasos[1][1])"""),

md(r"""Para leer un elemento hacen falta **dos** índices, uno detrás de otro:

- `pasos[1]` es la **fila** 1 (la segunda): la lista `[0.4, -0.2]`.
- `pasos[1][1]` es el elemento 1 **de esa fila**: `-0.2`.

Se lee de izquierda a derecha: "de `pasos`, coge la fila 1; de esa fila, coge el elemento 1". (Python escribe la lista de una línea; el código de arriba la parte en tres líneas solo para que se lea como una tabla, lo que se puede hacer dentro de corchetes.)

### Recorrer una tabla

Se puede recorrer fila a fila, y desempaquetar cada fila como si fuera una tupla:
"""),

code(r"""x, y = 0.0, 0.0                 # dos asignaciones en una línea (desempaquetando una tupla)
for avance_x, avance_y in pasos:
    x = x + avance_x
    y = y + avance_y
print("posición final:", round(x, 2), round(y, 2))"""),

md(r"""Y se pueden ir añadiendo filas con `append` (NB09), como a cualquier lista: `pasos.append([0.3, 0.1])` añade una fila nueva.

En la Parte 2, las tablas de números (las **matrices**, NB14) se escribirán primero así, como listas de listas, y después con una herramienta mucho más potente (NumPy, NB15).
"""),

md(r"""## 4 · El operador in: ¿está dentro?

### Pertenencia

Hasta ahora, `in` solo aparecía dentro de un `for` (`for x in lista`). Pero `in` también funciona **solo**, como una pregunta de sí o no: **¿está este elemento dentro de esta colección?** El resultado es `True` o `False` (NB08):
"""),

code(r"""articulaciones = ["cadera", "rodilla", "tobillo"]
print("rodilla" in articulaciones)
print("codo" in articulaciones)
print("codo" not in articulaciones)        # not in: lo contrario"""),

md(r"""Funciona con listas, tuplas, y también con textos (¿está este trozo de texto dentro de aquel?):
"""),

code(r"""print("dill" in "rodilla")
print(3 in (1, 2, 3))"""),

md(r"""Y es muy cómodo dentro de un `if`, para hacer algo solo en algunos casos. Por ejemplo, imprimir solo en ciertos pasos de un bucle:
"""),

code(r"""for paso in range(1, 31):
    if paso in [1, 2, 5, 10, 20, 30]:
        print("paso", paso)"""),

md(r"""Sin `in`, ese `if` sería `paso == 1 or paso == 2 or paso == 5 or ...`: mucho más largo. (No confundas los dos usos: en `for x in lista`, `in` **recorre**; en `x in lista`, solo **pregunta**.)
"""),

md(r"""## 5 · Métodos y atributos: el punto

### Lo que ya conoces: los métodos

En el NB09 escribiste `lista.append(5)`: una función "pegada" a la lista con un **punto**, que hace algo **con** esa lista. A esas funciones pegadas a un objeto se les llama **métodos**. Los textos también tienen los suyos:
"""),

code(r"""nombre = "zancudo"
print(nombre.upper())               # el método upper devuelve el texto en mayúsculas
print(nombre.count("u"))            # cuántas veces aparece la letra u"""),

md(r"""### Lo nuevo: los atributos

Pero detrás de un punto no siempre hay un método. A veces hay un **dato**: un valor guardado dentro del objeto, que se lee **sin paréntesis**. A eso se le llama **atributo**. El ejemplo más sencillo está en el módulo `math`, que guarda el número π:
"""),

code(r"""import math
print(math.pi)                      # un atributo: un dato, sin paréntesis
print(math.sqrt(25))                # un método (una función del módulo): se llama con paréntesis"""),

md(r"""La regla para distinguirlos:

- **Con paréntesis** → es algo que se **hace** (un método o función): `lista.append(5)`, `math.sqrt(25)`, `nombre.upper()`.
- **Sin paréntesis** → es algo que se **lee** (un atributo, un dato): `math.pi`.

En la Parte 2 verás muchos atributos de este tipo. Por ejemplo, las tablas de números de NumPy (NB15) tienen un atributo `.shape` que dice su tamaño (filas, columnas) como una **tupla**: `tabla.shape` (sin paréntesis), que devuelve algo como `(17, 45)`.

¿Qué pasa si te confundes y pones paréntesis a un atributo?
"""),

code_err(r"""math.pi()"""),

md(r"""`TypeError: 'float' object is not callable`: "un decimal no se puede llamar". `math.pi` es un número, y los números no se "ejecutan". Y al revés, si olvidas los paréntesis de un método, no da error pero tampoco hace lo que querías: `nombre.upper` (sin paréntesis) es **la función en sí**, sin ejecutar (NB10: una función se puede nombrar sin llamarla).
"""),

md(r"""## 6 · Las formas de importar

### Lo que ya sabes

En el NB11 importaste el módulo `random` con `import random`, y usaste sus funciones con un punto: `random.uniform(a, b)`. Un **módulo** es un archivo de código con funciones y datos listos para usar (las **bibliotecas** del NB05b son colecciones de módulos). Hay otras dos formas de importar, que verás constantemente.

### import ... as ...: un apodo

Algunos módulos tienen nombres largos, y se usan tantísimo que se les pone un **apodo** corto con `as`:
"""),

code(r"""import random as rnd
print(rnd.uniform(0, 1))"""),

md(r"""`rnd` es ahora otro nombre para el módulo `random`. En la Parte 2 verás dos apodos que usa **todo el mundo**, en todos los programas de ciencia: `import numpy as np` y `import matplotlib.pyplot as plt`. Son tan comunes que si escribes otro apodo, quien lea tu código se extrañará.

### from ... import ...: traer solo lo que necesitas

La otra forma trae **directamente** algunas funciones o datos de un módulo, para usarlos **sin** escribir el nombre del módulo delante:
"""),

code(r"""from math import sqrt, pi
print(sqrt(16), pi)"""),

md(r"""Ahora `sqrt` y `pi` se usan solos, sin `math.` delante.

¿Cuál usar? Las dos son correctas, y depende del gusto y del caso:

| Forma | Se usa como | Ventaja |
|---|---|---|
| `import math` | `math.sqrt(16)` | siempre se sabe de qué módulo viene cada cosa |
| `import numpy as np` | `np.zeros(3)` | igual, con un nombre corto |
| `from math import sqrt` | `sqrt(16)` | más corto, si usas mucho esa función |

Verás mucho la tercera forma con cosas que tienen nombres muy claros: `from pathlib import Path`, `from dataclasses import dataclass`... (las conocerás en la Parte 3).

### Un módulo dentro de otro

Algunos módulos son grandes y están organizados en **submódulos**, separados por puntos: `matplotlib.pyplot` es el submódulo `pyplot` (el de dibujar) del módulo `matplotlib`. Por eso se escribe `import matplotlib.pyplot as plt`.
"""),

md(r"""## 7 · Leer una llamada larga

Con todo lo de hoy, ya puedes leer una línea como esta, que encontrarás en el NB12 para dibujar una flecha:

```python
plt.arrow(0, 0, 3, 2, color="gray", head_width=0.25, length_includes_head=True)
```

Por partes:

- `plt.arrow`: la función `arrow` ("flecha") del módulo `plt` (el apodo de `matplotlib.pyplot`).
- `0, 0, 3, 2`: cuatro argumentos **por posición**: dónde empieza la flecha (0, 0) y cuánto avanza (3 a la derecha, 2 hacia arriba).
- `color="gray"`, `head_width=0.25`, `length_includes_head=True`: tres argumentos **con nombre**, opcionales: el color, el ancho de la punta y si la punta cuenta dentro de la longitud.

No hace falta saberse los nombres de memoria (nadie se los sabe: se miran cuando hacen falta). Lo importante es saber **leer la forma**: primero lo obligatorio por orden; después, las opciones con su nombre.
"""),

md(r"""## 8 · Resumen de la lección

1. **Argumentos con nombre**: `f(x, nombre=valor)`. Se leen mejor, el orden da igual y permiten elegir opciones. Primero los de posición, después los de nombre. **Valores por defecto** en el `def`: `def f(a, b=5)`.
2. **Tuplas**: `(5, 3)`. Como listas, pero **no se pueden cambiar**. `return a, b` devuelve una tupla. **Desempaquetar**: `x, y = punto`. En un for: `for nombre, valor in lista_de_tuplas`. Tupla de uno: `(5,)`.
3. **Listas de listas**: tablas. `tabla[fila][columna]`. Se recorren fila a fila.
4. **`in` / `not in`**: ¿está dentro? Da `True` o `False`. Distinto del `in` del `for`.
5. **Métodos** (con paréntesis, hacen algo: `lista.append(5)`) y **atributos** (sin paréntesis, son datos: `math.pi`, `tabla.shape`).
6. **Importar**: `import modulo`, `import modulo as apodo` (`np`, `plt`), `from modulo import nombre`. Submódulos con puntos.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Argumento con nombre** | Argumento que se pasa escribiendo `parametro=valor`. |
| **Valor por defecto** | El valor que toma un parámetro si no se le da ninguno. |
| **Tupla** | Colección entre paréntesis que no se puede cambiar. |
| **Desempaquetar** | Repartir los elementos de una tupla (o lista) en varias variables. |
| **Lista de listas** | Lista cuyos elementos son listas: una tabla. |
| **Pertenencia (`in`)** | Preguntar si un elemento está dentro de una colección. |
| **Atributo** | Dato guardado dentro de un objeto, que se lee sin paréntesis. |
| **Apodo (`as`)** | Nombre corto para un módulo al importarlo. |
| **Submódulo** | Módulo que está dentro de otro (`matplotlib.pyplot`). |
"""),

md(r"""## 9 · Ejercicios

**E1.** Escribe una función `describir(nombre, edad, ciudad="Madrid")` que devuelva un texto como `"Ana, 14 años, Madrid"`. Llámala con y sin ciudad, y una vez con todos los argumentos por nombre y en otro orden.

**E2.** Guarda en una tupla las dimensiones de una caja `(largo, ancho, alto) = (0.4, 0.2, 0.1)`, desempaquétala en tres variables y calcula su volumen.

**E3.** Con la lista de listas `notas = [[7, 8, 6], [9, 9, 10], [5, 6, 7]]` (tres alumnos, tres exámenes), imprime la nota media de cada alumno.

**E4.** Con la misma lista, ¿cómo accedes a la nota del tercer examen del segundo alumno?

**E5.** Escribe un programa que recorra los números del 1 al 20 e imprima solo los que **no** están en la lista `[3, 6, 9, 12, 15, 18]`.

**E6.** ¿Qué imprime `print("rod" in "rodilla", "Rod" in "rodilla")`? ¿Por qué?

**E7.** Importa la función `floor` del módulo `math` con `from` (redondea siempre hacia abajo) y úsala con 3.7 y con −3.7. ¿Te sorprende el segundo?

**E8.** Para cada una de estas expresiones, di si es un método o un atributo: `nombre.upper()`, `math.e`, `lista.append(3)`, `math.pi`.
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
def describir(nombre, edad, ciudad="Madrid"):
    return nombre + ", " + str(edad) + " años, " + ciudad

print(describir("Ana", 14))                                   # Ana, 14 años, Madrid
print(describir("Leo", 15, "Sevilla"))                        # Leo, 15 años, Sevilla
print(describir(ciudad="Bilbao", edad=13, nombre="Iker"))     # Iker, 13 años, Bilbao
```

`str(edad)` convierte el número en texto para poder pegarlo con `+` (sumar un texto y un número da error: se verá a fondo en el NB20). Con todos los argumentos por nombre, el orden da igual.
</details>

<details>
<summary>▶ Solución E2</summary>

```python
caja = (0.4, 0.2, 0.1)
largo, ancho, alto = caja
print("volumen:", largo * ancho * alto, "m³")      # 0.008 m³ (8 litros)
```

(Te saldrá algo como `0.008000000000000002`: el "ruido" de los decimales del NB05b. Con `round(..., 4)` queda limpio.)
</details>

<details>
<summary>▶ Solución E3</summary>

```python
notas = [[7, 8, 6], [9, 9, 10], [5, 6, 7]]
for alumno in notas:
    print(sum(alumno) / len(alumno))       # 7.0, 9.33..., 6.0
```

Cada `alumno` es una fila (una lista de tres notas), y `sum` y `len` (NB09) funcionan con ella como con cualquier lista.
</details>

<details>
<summary>▶ Solución E4</summary>

`notas[1][2]` → **10**. La fila 1 es el segundo alumno (los índices empiezan en 0) y, dentro de ella, el elemento 2 es el tercer examen.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
for numero in range(1, 21):
    if numero not in [3, 6, 9, 12, 15, 18]:
        print(numero)
```
</details>

<details>
<summary>▶ Solución E6</summary>

`True False`. `"rod"` está dentro de `"rodilla"`, pero `"Rod"` no, porque Python distingue **mayúsculas y minúsculas**: para él, `R` y `r` son caracteres distintos (números distintos en la tabla Unicode del NB05b).
</details>

<details>
<summary>▶ Solución E7</summary>

```python
from math import floor
print(floor(3.7), floor(-3.7))       # 3 -4
```

`floor` ("suelo") redondea siempre **hacia abajo** en la recta numérica (NB03b). Para −3,7, "hacia abajo" es −4 (más a la izquierda), no −3. Sorprende porque solemos pensar en "quitar los decimales", pero eso sería redondear hacia el cero.
</details>

<details>
<summary>▶ Solución E8</summary>

- `nombre.upper()`: **método** (con paréntesis: hace algo).
- `math.e`: **atributo** (sin paréntesis: el número e ≈ 2,718, que conocerás en el NB15b).
- `lista.append(3)`: **método**.
- `math.pi`: **atributo**.
</details>
"""),

md(r"""## 10 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Ahora sí: en la **Parte 2** empezamos con las **matemáticas** del aprendizaje. El **NB12** arranca con las **flechas** (los vectores), con dibujos hechos por el ordenador... y ya sabrás leer todas las líneas que los dibujan.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB11b_python_que_vas_a_ver.ipynb")
    build(out, cells, title="NB11b · Python que vas a ver")
