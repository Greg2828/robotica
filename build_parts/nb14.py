"""Construye NB14 · Tablas de números: las matrices (Parte 2 · Lección 3).

De una neurona a muchas: un robot de dos ruedas que se equilibra (tipo
Segway) con 2 motores y 3 observaciones → tabla 2×3 de pesos. Matriz =
filas × columnas; lista de listas (M[fila][columna]); bucle dentro de bucle;
matriz × vector = cada fila · vector; la regla de los tamaños (IndexError
real si no encajan); capa lineal = M·x + b; la política lineal del humanoide
(17×45 + 17 = 782 ruedecillas; con la observación completa 17×348 + 17 =
5.933) aplicada a una observación inventada, recortando a ±0,4; por qué la
búsqueda aleatoria no da abasto (0,5**782 en notación científica); dos capas
en fila = una red (avance).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB14 · Tablas de números: las matrices

**Parte 2 · Matemáticas y herramientas para robots — Lección 3**

> En el **NB13** descubriste que una **neurona** es un producto escalar más un sesgo, y que la política del palo de
> escoba era **una** neurona con 2 pesos. Pero el palo tenía **un** motor. El humanoide tiene **17**.

¿Cómo decide una política **varias acciones a la vez**? La respuesta es sencillísima: con **varias neuronas**, una
por motor, cada una con sus propios pesos. Y para tener todos esos pesos ordenados se usa una **tabla de números**,
que los matemáticos llaman **matriz**.

Hoy aprenderás qué es una matriz, cómo se guarda en Python, y la operación estrella: **multiplicar una matriz por un
vector**, que es exactamente lo que hace una política para convertir **una observación en todas las acciones a la
vez**. Y al final contaremos cuántas ruedecillas tiene la política más sencilla posible del humanoide. Prepárate,
porque el número impresiona.
"""),

md(r"""## 1 · Un robot con dos motores

Para no saltar directamente a 17 motores, empecemos con un robot de **dos**. Imagina un robot de **dos ruedas** que
se mantiene de pie solo, como esos patinetes eléctricos de dos ruedas en paralelo en los que la gente va de pie
(los "Segway"). Es un palo de escoba (NB11) con ruedas: si se inclina hacia delante, las ruedas tienen que avanzar
para "ponerse debajo".

Tiene **dos motores**: la **rueda izquierda** y la **rueda derecha**. Y su observación tiene **tres** números:

```
   observación = (inclinación, velocidad de inclinación, giro)

     inclinación  → cuánto está inclinado hacia delante (grados)
     velocidad    → lo deprisa que se está inclinando (grados por segundo)
     giro         → cuánto está girado respecto a hacia donde debería mirar (grados)
```

Cada rueda necesita **su propia neurona**: tres pesos (uno por cada número de la observación). Pensemos qué pesos
tendrían sentido:

- Para **no caerse**, las **dos** ruedas deben hacer lo mismo que el palo de escoba: empujar en contra de la
  inclinación y de la velocidad. Pesos −30 y −8, igual en las dos ruedas.
- Para **corregir el giro**, las ruedas deben hacer cosas **opuestas**: si una gira más que la otra, el robot gira
  (como un tanque o una silla de ruedas). Peso −5 en una rueda y +5 en la otra.

```
                    inclinación   velocidad   giro
   rueda izquierda:     −30          −8        −5
   rueda derecha:       −30          −8        +5
```

¡Ahí está! Hemos escrito, sin querer, una **tabla de pesos**: una **matriz**.
"""),

md(r"""## 2 · ¿Qué es una matriz?

Una **matriz** es una tabla de números ordenada en **filas** (horizontales) y **columnas** (verticales). La conoces de
mil sitios: un horario de clases, una hoja de cálculo, la tabla de clasificación de una liga, el tablero de "Hundir
la flota" (NB12)...

```
                  columna 0   columna 1   columna 2
                ┌───────────┬───────────┬───────────┐
       fila 0   │    −30    │    −8     │    −5     │   ← la neurona de la rueda izquierda
                ├───────────┼───────────┼───────────┤
       fila 1   │    −30    │    −8     │    +5     │   ← la neurona de la rueda derecha
                └───────────┴───────────┴───────────┘
```

- Cada **fila** es **una neurona** (los pesos de un motor).
- Cada **columna** corresponde a **un dato de la observación** (todos los pesos que reciben ese dato).

El **tamaño** de una matriz se dice "**filas por columnas**". Esta es una matriz **2 × 3** ("dos por tres"): 2 filas
y 3 columnas, en total 2 × 3 = 6 números. Siempre se dicen **primero las filas**.
"""),

md(r"""## 3 · Una matriz en Python: una lista de listas

¿Cómo guardamos una tabla en Python? Con algo que aún no hemos usado, pero que ya puedes adivinar: una **lista cuyos
elementos son listas**. Cada fila es una lista (NB09), y la matriz es la lista de las filas:
"""),

code(r"""pesos = [
    [-30, -8, -5],     # fila 0: rueda izquierda
    [-30, -8,  5],     # fila 1: rueda derecha
]

print(pesos)"""),

md(r"""(Para que se lea mejor, hemos escrito cada fila en su propia línea: Python permite partir una lista entre corchetes
en varias líneas, igual que los paréntesis del NB11.)

Como es una lista, `pesos[0]` es su **primer elemento**... que es **una fila entera**:
"""),

code(r"""print("Fila 0 (rueda izquierda):", pesos[0])
print("Fila 1 (rueda derecha):  ", pesos[1])"""),

md(r"""Y como cada fila es a su vez una lista, para sacar **un solo número** se ponen **dos índices seguidos**: primero la
**fila** y luego la **columna**. Como en "Hundir la flota": primero una coordenada, luego la otra.
"""),

code(r"""print("Fila 1, columna 2:", pesos[1][2])"""),

md(r"""**5**: el peso del **giro** (columna 2) en la neurona de la **rueda derecha** (fila 1). Lee `pesos[1][2]` de izquierda
a derecha: "de `pesos`, coge la fila 1; y de esa fila, el elemento 2".

Para saber el tamaño: `len(pesos)` da el número de **filas** (cuántas listas hay dentro), y `len(pesos[0])` el número de
**columnas** (cuánto mide una fila):
"""),

code(r"""print("Filas:", len(pesos), "| Columnas:", len(pesos[0]))"""),

md(r"""## 4 · Recorrer una tabla: un bucle dentro de otro

Para recorrer **todos** los números de una tabla, hace falta recorrer las filas y, **dentro de cada fila**, recorrer
sus números. Es decir: **un bucle dentro de otro bucle**. Fíjate en la sangría: el segundo `for` está **dentro** del
primero, y su `print`, todavía más dentro:
"""),

code(r"""for fila in pesos:
    for numero in fila:
        print(numero)"""),

md(r"""Seis números, en orden: primero los 3 de la fila 0, luego los 3 de la fila 1. Así funciona un **bucle anidado**
("anidado" = metido dentro, como un nido):

```
   for fila in pesos:            ← bucle de FUERA: da 2 vueltas (una por fila)
       for numero in fila:       ← bucle de DENTRO: en CADA vuelta de fuera, da 3 vueltas
           print(numero)
                                    total: 2 × 3 = 6 vueltas del print
```

Es como leer un libro: para cada **línea** (bucle de fuera), lees cada **palabra** (bucle de dentro).

Por ejemplo, para **contar todos los pesos** de una tabla (algo que haremos enseguida con el humanoide), un acumulador
con un bucle anidado:
"""),

code(r"""total_pesos = 0
for fila in pesos:
    for numero in fila:
        total_pesos = total_pesos + 1

print("Esta tabla tiene", total_pesos, "pesos")"""),

md(r"""## 5 · La operación estrella: matriz por vector

Ahora la idea central de la lección. Tenemos la tabla de pesos y una observación. Queremos las **dos acciones** (una por
rueda). Cada rueda es una neurona, así que su acción es el **producto escalar** (NB13) de **su fila** por la observación:

```
   observación = (2, 5, 1)       inclinado 2°, cayéndose a 5°/s, girado 1°

   rueda izquierda = (−30, −8, −5) · (2, 5, 1) = −60 − 40 − 5 = −105
   rueda derecha   = (−30, −8, +5) · (2, 5, 1) = −60 − 40 + 5 =  −95
```

**Cada fila de la matriz, multiplicada (producto escalar) por el vector, da un número del resultado.** Dos filas, dos
números. A esta operación se le llama **multiplicar una matriz por un vector**, y el resultado es **otro vector**: uno
con un número por fila.

```
   ┌ −30  −8  −5 ┐   ┌ 2 ┐     ┌ −105 ┐   ← fila 0 · observación
   └ −30  −8  +5 ┘ × │ 5 │  =  └  −95 ┘   ← fila 1 · observación
                     └ 1 ┘
     matriz 2×3     vector de 3   vector de 2
```

En Python es facilísimo, con el `producto_escalar` del NB13 y un bucle sobre las filas:
"""),

code(r"""def producto_escalar(a, b):
    total = 0
    for i in range(len(a)):
        total = total + a[i] * b[i]
    return total

def matriz_por_vector(matriz, vector):
    resultado = []
    for fila in matriz:
        resultado.append(producto_escalar(fila, vector))
    return resultado

observacion = [2, 5, 1]
print(matriz_por_vector(pesos, observacion))"""),

md(r"""**[−105, −95]**: las dos acciones a la vez. Las dos ruedas empujan con fuerza "hacia atrás" (signo negativo, para
ponerse debajo de la inclinación)... pero la izquierda **un poco más** que la derecha. Esa pequeña diferencia hace que el
robot **gire** un poquito, corrigiendo el grado de giro que tenía. **Una sola operación decide a la vez "no te caigas" y
"gira".**

¿Y si el robot no está girado (giro = 0)? Entonces las dos ruedas hacen exactamente lo mismo:
"""),

code(r"""print(matriz_por_vector(pesos, [2, 5, 0]))"""),

md(r"""Las dos, −100: va recto y solo se ocupa de no caerse. Los pesos de la columna del giro (−5 y +5) solo entran en juego
cuando hay giro que corregir.
"""),

md(r"""## 6 · La regla de los tamaños

Hay una regla que **siempre** se tiene que cumplir para multiplicar una matriz por un vector:

> **El vector tiene que tener tantos números como columnas tiene la matriz.** Y el resultado tiene tantos números como
> **filas**.

Tiene todo el sentido: cada fila se multiplica (producto escalar) con el vector, y para eso tienen que medir lo mismo.
Nuestra matriz es 2 × 3: necesita vectores de **3**, y da vectores de **2**.

```
   matriz (filas × columnas)  ×  vector (columnas)  =  vector (filas)
            2 × 3             ×        3            =       2
                  └────── tienen que coincidir ─┘
```

¿Qué pasa si no se cumple? Si le pasamos una observación de **2** números a una matriz de 3 columnas:
"""),

code_err(r"""print(matriz_por_vector(pesos, [2, 5]))"""),

md(r"""`IndexError: list index out of range` (NB09). Dentro de `producto_escalar`, el bucle va hasta el índice 2 (porque la
fila tiene 3 números), pero el vector solo tiene los índices 0 y 1. El tercer peso no tiene con quién multiplicarse.

Este error, **"los tamaños no encajan"**, es el error más común de todo el que trabaja con redes neuronales, también de
los profesionales. Cuando aparezca, la primera pregunta siempre es: **¿cuánto mide cada cosa?**
"""),

md(r"""## 7 · El sesgo, para cada neurona

En el NB13 vimos que una neurona es pesos · entradas **+ sesgo**. Si cada fila es una neurona, cada una tiene su propio
sesgo. Así que los sesgos forman **otro vector**, con un número por fila, que se **suma** al resultado (suma de flechas,
NB12):

```
   acciones = matriz × observación + sesgos
```

Por ejemplo, si la rueda derecha estuviera un poco gastada y tirara menos, un sesgo positivo pequeño en ella la
compensaría siempre. A esta pareja "matriz de pesos + vector de sesgos" se le llama **capa lineal** (o **capa densa**),
y es **la pieza básica de toda red neuronal**:
"""),

code(r"""def sumar(a, b):
    resultado = []
    for i in range(len(a)):
        resultado.append(a[i] + b[i])
    return resultado

def capa(matriz, sesgos, entrada):
    return sumar(matriz_por_vector(matriz, entrada), sesgos)

sesgos = [0, 3]
print(capa(pesos, sesgos, observacion))"""),

md(r"""[−105, −92]: la rueda derecha, con su sesgo de +3, empuja un poco menos hacia atrás que antes (−92 en vez de −95).

Fíjate en el tamaño de las ruedecillas de esta capa: **6 pesos** (la matriz 2 × 3) **+ 2 sesgos** = **8 parámetros**. La
regla general:

```
   ruedecillas de una capa = (salidas × entradas) + salidas
                              └── la matriz ──┘    └ sesgos ┘
```
"""),

md(r"""## 8 · La política lineal del humanoide

Y ahora, a por el humanoide. Su política lineal más sencilla es **una capa**: una matriz de pesos y un vector de sesgos.

- **Salidas**: 17 (una acción por motor) → la matriz tiene **17 filas**.
- **Entradas**: 45 (la observación básica, NB03) → la matriz tiene **45 columnas**.

Contemos las ruedecillas con la regla del apartado anterior:
"""),

code(r"""salidas = 17
entradas = 45
ruedecillas = salidas * entradas + salidas
print("Ruedecillas de la política lineal del humanoide:", ruedecillas)"""),

md(r"""**782 ruedecillas.** Frente a las **2** del palo de escoba. Y eso con la observación básica; con la observación completa
del humanoide (348 números, NB03), serían 17 × 348 + 17 = **5.933**. Y eso solo para la política **más sencilla** posible:
una sola capa.

Vamos a construir una de esas políticas, con **pesos al azar** (como un robot que aún no ha aprendido nada), y a usarla
con una observación inventada de 45 números. Usamos un **bucle anidado** para fabricar la matriz: 17 filas, cada una con
45 pesos al azar entre −0,1 y 0,1:
"""),

code(r"""import random
random.seed(0)

matriz_humanoide = []
for motor in range(17):
    fila = []
    for dato in range(45):
        fila.append(random.uniform(-0.1, 0.1))
    matriz_humanoide.append(fila)

sesgos_humanoide = []
for motor in range(17):
    sesgos_humanoide.append(0)

print("Tamaño:", len(matriz_humanoide), "filas x", len(matriz_humanoide[0]), "columnas")"""),

md(r"""Una tabla de 17 × 45 llena de números al azar. Ahora, una observación inventada (45 números al azar entre −1 y 1, para
hacer la prueba) y la política en acción:
"""),

code(r"""observacion_humanoide = []
for dato in range(45):
    observacion_humanoide.append(random.uniform(-1, 1))

acciones = capa(matriz_humanoide, sesgos_humanoide, observacion_humanoide)
print("Número de acciones:", len(acciones))
print("Primeras 5 acciones:", [round(a, 2) for a in acciones[0:5]])"""),

md(r"""(¿Has visto ese `[round(a, 2) for a in acciones[0:5]]`? Es una forma corta de Python para "**haz una lista** redondeando
cada `a` de las 5 primeras acciones". Se llama **lista por comprensión**. No la usaremos mucho todavía; aquí solo sirve
para mostrar los números cortitos.)

**17 acciones**, una por motor, calculadas a la vez con una sola operación. Exactamente lo que necesita el simulador en
cada paso.

Pero cuidado: el humanoide solo acepta acciones entre **−0,4 y +0,4** (NB03). Con estos pesos y esta observación, por
casualidad, ninguna se pasa; pero con pesos más grandes u observaciones más extremas **sí** se pasarían. Así que, por
seguridad, igual que el motor del palo de escoba limitaba el empuje (NB11), **siempre** se recorta cada acción a su rango:
"""),

code(r"""def recortar(x, minimo, maximo):
    if x < minimo:
        return minimo
    if x > maximo:
        return maximo
    return x

acciones_recortadas = []
for a in acciones:
    acciones_recortadas.append(recortar(a, -0.4, 0.4))

print("Mayor acción:", round(max(acciones_recortadas), 2), "| menor:", round(min(acciones_recortadas), 2))"""),

md(r"""Todas dentro de ±0,4 (aquí no ha hecho falta tocar ninguna, pero el recorte nos protege para cuando sí). Esto, matriz por observación más sesgos y recortar, **es una política completa para el
humanoide**. Con los pesos al azar, haría que el robot convulsionara y se cayera, como en el GIF del NB00. Lo que falta es
**encontrar** los 782 pesos buenos.
"""),

md(r"""## 9 · Por qué probar al azar ya no da abasto

En el NB11, la búsqueda aleatoria encontró buenas ruedecillas en un par de intentos. ¿Funcionaría con 782?

Hagamos una cuenta muy simplificada (solo para hacernos una idea). Supón que cada ruedecilla, por separado, tiene un **50 %
de probabilidad** de caer en una "zona buena" al elegirla al azar (como lanzar una moneda). Para que la política entera sea
buena, **todas** tienen que caer bien a la vez. Con 2 ruedecillas: 0,5 × 0,5 = 0,25, uno de cada cuatro intentos. ¿Y con 782?
Hay que multiplicar 0,5 por sí mismo 782 veces, es decir, elevar a 782 (`**`, NB06):
"""),

code(r"""print("Con 2 ruedecillas:  ", 0.5 ** 2)
print("Con 782 ruedecillas:", 0.5 ** 782)"""),

md(r"""El segundo número sale escrito de una forma rara: **`3.93...e-236`**. Es la **notación científica**, la forma que usa Python
para números **gigantes o minúsculos**. La `e-236` significa "**multiplicado por 10 elevado a −236**", es decir: **un cero, una
coma, y 235 ceros más** antes del 3 y pico. Es un número tan pequeño que no tiene nombre.

Para que te hagas una idea: si probaras **mil millones** de políticas por segundo desde el **origen del universo** (hace unos
13.800 millones de años), habrías probado unas 4 × 10²⁶ políticas (un 4 seguido de 26 ceros)... y la probabilidad de haber dado con una buena seguiría
siendo prácticamente **cero**.

Es la **maldición de la dimensionalidad** del NB03, ahora con números de verdad. **Probar al azar es inútil con tantas
ruedecillas.** Hace falta una forma de girarlas que **no sea a ciegas**: una que, para cada ruedecilla, calcule **hacia dónde
girarla** para mejorar un poquito. Ese es el gran tema que viene en las próximas lecciones: las **pendientes**.
"""),

md(r"""## 10 · Un adelanto: capas una detrás de otra

Una última idea, solo para que veas hacia dónde vamos. ¿Qué pasa si la **salida** de una capa se usa como **entrada** de otra
capa?

```
   observación ──► CAPA 1 ──► números intermedios ──► CAPA 2 ──► acciones
     (45)        (matriz       (por ejemplo, 64)     (matriz        (17)
                  64 × 45)                            17 × 64)
```

La primera capa convierte la observación en unos números "intermedios", y la segunda convierte esos números en las acciones.
Eso, con un pequeño ingrediente extra entre capa y capa (que veremos cuando toque, y que es lo que le da su poder), es una **red
neuronal**: **capas de neuronas, una detrás de otra**. Las redes que mueven a los humanoides de verdad tienen tres o cuatro capas
así.

Cuenta las ruedecillas de esa red de dos capas: capa 1, 64 × 45 + 64 = 2.944; capa 2, 17 × 64 + 17 = 1.105. En total, **4.049**.
¿Recuerdas que en el NB03 dijimos que una red pequeña para el humanoide tiene "unas decenas de miles" de ruedecillas? Con capas un
poco más anchas (256 números intermedios, por ejemplo), se llega enseguida. Ahora ya sabes **de dónde salen todas esas
ruedecillas**: son los números de las matrices.
"""),

md(r"""## 11 · Resumen de la lección

1. Para decidir **varias acciones a la vez** hacen falta **varias neuronas**, una por motor. Sus pesos se ordenan en una
   **matriz**: una tabla con **filas** (una por neurona/salida) y **columnas** (una por dato de entrada). Su tamaño se dice
   **filas × columnas**.
2. En Python, una matriz es una **lista de listas**; `matriz[fila][columna]` saca un número. Para recorrerla entera, un **bucle
   anidado**.
3. **Matriz por vector**: cada fila (producto escalar) por el vector da un número del resultado. Regla de tamaños: (filas ×
   columnas) × (columnas) = (filas). Si no encajan, error.
4. Una **capa lineal** = matriz × entrada + **sesgos**. Ruedecillas = salidas × entradas + salidas. La política lineal del
   humanoide (17 × 45 + 17) tiene **782**; con la observación completa, **5.933**. Las acciones se **recortan** a ±0,4.
5. Con tantas ruedecillas, probar al azar es inútil (0,5⁷⁸² ≈ 10⁻²³⁶, en **notación científica**). Hace falta girarlas **con
   cabeza**: las **pendientes**. Varias **capas** en fila forman una **red neuronal**.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Matriz** | Una tabla de números con filas y columnas. |
| **Fila / columna** | Línea horizontal / vertical de una matriz. |
| **Tamaño (filas × columnas)** | Cuántas filas y columnas tiene: 2 × 3, 17 × 45... |
| **Lista de listas** | Cómo se guarda una matriz en Python. |
| **Bucle anidado** | Un bucle dentro de otro. |
| **Matriz por vector** | Cada fila (producto escalar) por el vector: da un vector con un número por fila. |
| **Capa lineal / densa** | Matriz × entrada + sesgos: la pieza básica de una red neuronal. |
| **Recortar** | Limitar un número a un rango (como las acciones a ±0,4). |
| **Notación científica** | `1.5e-236` = 1,5 × 10⁻²³⁶: forma de escribir números gigantes o minúsculos. |
| **Lista por comprensión** | Forma corta de crear una lista: `[round(a, 2) for a in lista]`. |
| **Red neuronal** | Varias capas, una detrás de otra (con un ingrediente extra que veremos). |
"""),

md(r"""## 12 · Ejercicios

**E1.** ¿De qué tamaño es esta matriz? ¿Cuánto vale el elemento de la fila 0, columna 1? ¿Y `M[2][0]`?

```python
M = [[1, 2],
     [3, 4],
     [5, 6]]
```

**E2.** Multiplica a mano la matriz del E1 por el vector (10, 1). ¿Cuántos números tiene el resultado? Compruébalo con
`matriz_por_vector`.

**E3.** ¿Se puede multiplicar una matriz de 4 × 2 por un vector de 4 números? ¿Y por uno de 2? ¿Qué tamaño tendría el
resultado en el caso que funciona?

**E4.** En el robot de dos ruedas, ¿qué pasaría si las dos filas tuvieran **el mismo** peso para el giro (por ejemplo, −5 y
−5)? Calcula las acciones para la observación (0, 0, 10): derecho, quieto, pero girado 10 grados.

**E5.** Cuenta las ruedecillas de una capa lineal que convierte 10 entradas en 4 salidas. ¿Y de una que convierte 348 entradas
en 17 salidas? (Compara con el 5.933 del apartado 8.)

**E6.** Escribe con bucles anidados una función `suma_de_la_matriz(matriz)` que sume **todos** los números de una matriz.
Pruébala con la del E1.

**E7.** **Reto.** Escribe 1.000.000 (un millón) y 0,000001 (una millonésima) en notación científica de Python. Comprueba
tus respuestas escribiendo `print(1e6)` y `print(1e-6)`.
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

Es una matriz **3 × 2** (3 filas, 2 columnas). `M[0][1]` = **2** (fila 0, columna 1). `M[2][0]` = **5** (fila 2, columna 0).
</details>

<details>
<summary>▶ Solución E2</summary>

Cada fila por (10, 1):

- Fila 0: 1 × 10 + 2 × 1 = **12**
- Fila 1: 3 × 10 + 4 × 1 = **34**
- Fila 2: 5 × 10 + 6 × 1 = **56**

Resultado: **(12, 34, 56)**, con **3** números (uno por fila). `matriz_por_vector(M, [10, 1])` da `[12, 34, 56]`.
</details>

<details>
<summary>▶ Solución E3</summary>

La matriz 4 × 2 tiene **2 columnas**, así que necesita vectores de **2** números. Con uno de 4, **no** se puede (los tamaños no
encajan). Con uno de 2, sí, y el resultado tiene **4** números (uno por fila).
</details>

<details>
<summary>▶ Solución E4</summary>

Con la matriz `[[-30, -8, -5], [-30, -8, -5]]` y la observación (0, 0, 10): las dos ruedas darían −30 × 0 − 8 × 0 − 5 × 10 =
**−50**. ¡Las dos iguales! Si las dos ruedas giran igual, el robot avanza (o retrocede) en línea recta, pero **no gira**: el giro
nunca se corregiría. Para girar, las ruedas tienen que hacer cosas **distintas**, y por eso los pesos del giro tienen **signos
opuestos** en las dos filas.
</details>

<details>
<summary>▶ Solución E5</summary>

- 10 entradas → 4 salidas: 4 × 10 + 4 = **44** ruedecillas.
- 348 entradas → 17 salidas: 17 × 348 + 17 = **5.933**. Exactamente la política lineal del humanoide con la observación completa.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
def suma_de_la_matriz(matriz):
    total = 0
    for fila in matriz:
        for numero in fila:
            total = total + numero
    return total

print(suma_de_la_matriz([[1, 2], [3, 4], [5, 6]]))
```

Salida: **21** (1 + 2 + 3 + 4 + 5 + 6). Es el acumulador del NB07, con un bucle anidado.
</details>

<details>
<summary>▶ Solución E7</summary>

- Un millón = 1 × 10⁶ → **`1e6`**. `print(1e6)` muestra `1000000.0`.
- Una millonésima = 1 × 10⁻⁶ → **`1e-6`**. `print(1e-6)` muestra `1e-06` (Python prefiere la notación científica para números tan
  pequeños).

El número que va detrás de la `e` dice cuántas posiciones se mueve la coma: positivo, hacia la derecha (números grandes);
negativo, hacia la izquierda (números pequeños).
</details>
"""),

md(r"""## 13 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has visto que la política de un robot con muchos motores es una **tabla de pesos** multiplicada por la observación, y has
contado sus ruedecillas: cientos, miles. Y has notado algo: nuestras funciones con bucles funcionan, pero con matrices de 17 × 348
(y redes con miles de pesos, que hay que usar **millones** de veces durante un entrenamiento) los bucles de Python se quedan
**lentos**.

En el **NB15** conocerás la herramienta que usa **todo** el mundo de la robótica y la inteligencia artificial para esto: **NumPy**,
que hace estas operaciones decenas de veces más rápido y con una sola línea. Y como gran final, abriremos **el simulador de
verdad** del humanoide, MuJoCo, por primera vez en el curso: veremos que su observación **es** un vector de NumPy, le
aplicaremos **tu** política lineal... y mediremos cuántos puntos saca.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB14_matrices.ipynb")
    build(out, cells, title="NB14 · Tablas de números: las matrices")
