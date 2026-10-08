"""Construye NB07 · Repetir sin cansarse: el bucle for (Parte 1 · Lección 3).

Microdosis: una idea nueva por celda. El bucle for con range, el cuerpo y la
sangría (IndentationError real), la variable del bucle (contar desde 0),
range(inicio, fin), usar la variable en cuentas (la piedra que cae), el patrón
acumulador (retorno de 1000 pasos = 5000, robot C del NB04), Gauss 1..100, y el
simulador de la pelota con bucle: tabla del NB02 completa (con su ruido de
decimales), y la comprobación de que el paso pequeño se acerca a la realidad:
dt 0.1 → 0.5 m, 0.01 → 0.725 m, 0.001 → 0.7475 m; exacto 0.75 m.
Práctica en MuJoCo (apartado 13): tu bucle for + mj_step; MuJoCo reproduce 0.5/0.725/0.7475
y la tabla (atraviesa el suelo en el paso 6); humanoide 333 pasitos → torso 0,28 m;
acumulador: altura media del torso en el 1.er segundo 0,98 m.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB07 · Repetir sin cansarse: el bucle `for`

**Parte 1 · Primeros pasos con el ordenador — Lección 3**

> En el **NB06** el ordenador ganó **memoria** (las variables) y programaste tu primer simulador:
> una pelota que cae, pasito a pasito. Pero para dar cada pasito tuviste que **copiar la misma
> celda** otra vez. Tres pasitos, tres copias. Hoy aprenderás a decirle al ordenador: **"repite esto
> mil veces"**, en una sola línea.

Esa herramienta se llama **bucle**, y es la tercera gran pieza de la programación, después de las
instrucciones en orden (NB05) y las variables (NB06). Con estas tres ya se pueden escribir programas
sorprendentemente potentes.

Al final de hoy:

- Harás que la pelota caiga **todos los pasitos que quieras** con tres líneas de código.
- Sumarás los puntos de un **episodio entero** del humanoide (¿te acuerdas del robot C del NB04, el
  que se quedaba quieto y sacaba 5.000 puntos?).
- Y **comprobarás con el ordenador** lo que el NB02 te contó sobre los pasos grandes y pequeños del
  simulador. Ya no tendrás que creértelo: lo verás.
- Y en la práctica final escribirás **tu propio bucle de simulación con MuJoCo**.

Una idea nueva por celda. Vamos.
"""),

md(r"""## 1 · Los ordenadores no se aburren

Si te pido que escribas "practicaré más" cien veces en un cuaderno, como un castigo de colegio, a la
vigésima vez estarás harto, y a la quincuagésima empezarás a cometer erratas. A un ordenador le da
exactamente igual repetir algo 3 veces o 3.000 millones: no se cansa, no se aburre y no se equivoca
por despiste.

Y repetir es justo lo que necesitamos en robótica:

- El simulador repite **el mismo pasito de física** cientos de veces por segundo (NB02).
- El bucle del agente repite **observar → decidir → actuar** en cada paso (NB03).
- El entrenamiento repite **episodios** y más episodios, millones de veces (NB00).

Todo es repetir. Así que necesitamos una forma de pedirle al ordenador que repita **sin escribir lo
mismo una y otra vez**.

Fíjate en cómo lo hacemos las personas en una receta: no escribimos "bate, bate, bate, bate..."
cincuenta veces. Escribimos **"bate 50 veces"**. Una sola instrucción que dice **qué** repetir y
**cuántas veces**. Un bucle es exactamente eso, para el ordenador.
"""),

md(r"""## 2 · Tu primer bucle

En Python, la forma más común de repetir algo se escribe con la palabra **`for`** (en inglés, "para":
se lee algo así como "**para cada** vuelta..."). Esta celda repite un `print` **tres veces**. Fíjate
en que la segunda línea empieza con unos **espacios**: son importantísimos, y enseguida veremos por
qué.
"""),

code(r"""for vuelta in range(3):
    print("¡Otra vuelta!")"""),

md(r"""Tres veces "¡Otra vuelta!", y solo hemos escrito el `print` **una vez**. Si cambias el 3 por un
1000, saldrá mil veces. Ese es todo el poder de un bucle.

Vamos a desmontar la primera línea, pieza a pieza, como hicimos con el `print` del NB05:

```
   for   vuelta   in   range(3)   :
   ───   ──────   ──   ────────   ─
    │      │       │       │      └── dos puntos: "a continuación, lo que hay que repetir"
    │      │       │       └───────── CUÁNTAS veces: range(3) = "tres vueltas"
    │      │       └───────────────── "en" (parte fija de la frase)
    │      └───────────────────────── un nombre para el contador de vueltas (lo eliges tú)
    └──────────────────────────────── "para cada": empieza un bucle

   se lee:  "para cada vuelta en tres vueltas, haz lo siguiente:"
```

Y la segunda línea, la que está **metida hacia la derecha**, es **lo que se repite**. A esas líneas
se les llama **el cuerpo del bucle**.

(**`range`** significa "rango" o "recorrido". `range(3)` es como decir "un recorrido de 3 pasos".
Enseguida veremos qué hay exactamente dentro de ese recorrido.)
"""),

md(r"""## 3 · La sangría: qué está dentro y qué está fuera

Los espacios al principio de la segunda línea se llaman **sangría** (en inglés, *indentation*). Son
**cuatro espacios** (en Jupyter, la tecla **Tabulador** los pone por ti, y después de escribir los dos
puntos y pulsar Enter, Jupyter los pone solo).

En Python, la sangría **no es decoración**: es la manera de decir **qué líneas pertenecen al bucle**.
Todo lo que tiene sangría debajo del `for` se repite; lo primero que vuelve a estar pegado a la
izquierda ya está **fuera** del bucle, y se ejecuta **una sola vez**, cuando el bucle ha terminado.

```
   for vuelta in range(3):
       print("dentro")        ← con sangría: SE REPITE (3 veces)
       print("también")       ← con sangría: SE REPITE (3 veces)
   print("fuera")             ← sin sangría: UNA vez, al terminar el bucle
```

Comprobémoslo. En esta celda, la segunda línea va **dentro** del bucle y la tercera **fuera**:
"""),

code(r"""for vuelta in range(3):
    print("El robot da un paso")
print("Fin del episodio")"""),

md(r"""Tres veces el paso (está dentro, con sangría) y **una sola vez** "Fin del episodio" (está fuera,
sin sangría), **al final**. La sangría es como los márgenes de un esquema: lo que está metido hacia
dentro pertenece a lo de arriba.

¿Y si olvidamos la sangría? Python se queja, porque un `for` con dos puntos **promete** que debajo
viene algo que repetir:
"""),

code_err(r"""for vuelta in range(3):
print("¡Otra vuelta!")"""),

md(r"""`IndentationError: expected an indented block after 'for' statement on line 1`: "**error de
sangría**: se esperaba un bloque con sangría después del `for` de la línea 1". Un tipo de error nuevo
para tu colección, y muy fácil de leer: **falta la sangría**. La solución: meter la línea hacia la
derecha con 4 espacios (o un Tabulador).

| Tipo de error | Qué suele significar |
|---|---|
| `NameError` | Nombre desconocido (NB05, NB06) |
| `SyntaxError` | Gramática rota (NB05) |
| `IndentationError` | **Sangría** que falta o que sobra |
"""),

md(r"""## 4 · El contador de vueltas: ¿qué vale en cada vuelta?

En el bucle, `vuelta` no es un adorno: es una **variable** (una caja, NB06) que el bucle va
**rellenando** él solo, con un valor distinto en cada vuelta. Vamos a mirar qué hay dentro en cada
vuelta. Usaremos el nombre `i`, que es el que usan tradicionalmente los programadores para un
contador:
"""),

code(r"""for i in range(3):
    print(i)"""),

md(r"""**0, 1, 2**. ¡Ojo, no 1, 2, 3! `range(3)` da **tres** valores, pero **empezando por el 0**:

```
   range(3)  →  0, 1, 2          (tres valores: el 0, el 1 y el 2)

   vuelta 1:  i vale 0
   vuelta 2:  i vale 1
   vuelta 3:  i vale 2           (el 3 NO llega a salir)
```

**Los programadores cuentan desde 0.** Al principio choca, pero ya lo conoces: en un edificio, la
planta de la calle es la **planta 0** (o "baja"), y la de encima es la 1. Un edificio de 3 plantas
tiene las plantas 0, 1 y 2. Pues `range(3)` es igual: tres valores, del 0 al 2.

Grábate la regla: **`range(n)` da `n` valores, del 0 al `n − 1`**.
"""),

md(r"""## 5 · Empezar donde quieras: `range(inicio, fin)`

Si prefieres contar desde otro número, `range` admite **dos** números: dónde **empieza** y dónde
**para**. Pero cuidado con el segundo: el recorrido **para justo antes** de llegar a él.
"""),

code(r"""for i in range(1, 4):
    print(i)"""),

md(r"""**1, 2, 3**: empieza en el 1 y para **antes** del 4.

```
   range(1, 4)   →  1, 2, 3        (empieza en 1, para ANTES del 4)
   range(5, 8)   →  5, 6, 7
   range(0, 3)   →  0, 1, 2        (igual que range(3))
```

¿Por qué "para antes"? Porque así `range(0, 3)` y `range(3)` dan lo mismo, y porque la cuenta de
cuántos valores salen es fácil: **fin − inicio**. En `range(1, 4)` salen 4 − 1 = 3 valores.
"""),

md(r"""## 6 · Usar el contador en una cuenta: la piedra que cae

Como `i` es una caja normal, se puede usar en cuentas, igual que cualquier variable. Recuerda el dato
del NB02: una piedra que cae **gana 10 m/s de velocidad cada segundo**. Vamos a mostrar su velocidad
en los segundos 1, 2 y 3. Usamos un nombre claro para el contador, `segundo`, y la coma del `print`
(NB05) para mostrar varias cosas en la misma línea:
"""),

code(r"""for segundo in range(1, 4):
    print("segundo", segundo, "->", 10 * segundo, "m/s")"""),

md(r"""En cada vuelta, `segundo` vale una cosa distinta (1, luego 2, luego 3), y la cuenta `10 * segundo`
da un resultado distinto. Una sola línea de cuerpo, tres líneas de tabla. Con `range(1, 61)` tendrías
la tabla del primer minuto entero, sin escribir nada más.
"""),

md(r"""## 7 · Ir sumando: el patrón del acumulador

Ahora una de las ideas más útiles de toda la programación. Juntemos el bucle con lo último del NB06,
**una caja que se actualiza con su propio valor** (`x = x + 1`).

¿Te acuerdas del **retorno** del NB04? Era la **suma** de todas las recompensas de un episodio. Para
calcularlo hay que ir sumando paso a paso, como quien va echando monedas en una hucha: empiezas con la
hucha **vacía** y en cada paso echas una moneda más.

Vamos a hacerlo con el robot C del NB04, el que se queda **quieto** y gana **5 puntos** en cada paso.
Primero solo con **5 pasos**, mostrando la hucha en cada vuelta para ver cómo crece:
"""),

code(r"""total = 0
for paso in range(5):
    total = total + 5
    print("paso", paso, "-> total", total)"""),

md(r"""La caja `total` empieza vacía (en 0) **antes** del bucle, y en cada vuelta se le suman 5: 5, 10,
15, 20, 25. A una caja que va guardando una suma así se le llama **acumulador**, y el esquema completo
es siempre el mismo:

```
   total = 0                    ← 1. hucha vacía, ANTES del bucle (una vez)
   for paso in range(...):
       total = total + algo     ← 2. echa una moneda, DENTRO del bucle (cada vuelta)
   print(total)                 ← 3. mira cuánto hay, DESPUÉS del bucle (una vez)
```

Fíjate en que cada parte tiene su sitio, y la sangría lo marca. Si pusieras `total = 0` **dentro** del
bucle, ¡vaciarías la hucha en cada vuelta!
"""),

md(r"""Ahora, el episodio **completo**: 1.000 pasos. Esta vez **no** ponemos el `print` dentro (saldrían mil
líneas): lo ponemos **fuera**, sin sangría, para ver solo el resultado final:"""),

code(r"""total = 0
for paso in range(1000):
    total = total + 5
print("Retorno del robot quieto:", total)"""),

md(r"""**5000**: el retorno del robot C que calculamos a mano en el NB04 (1.000 pasos × 5 puntos). El
ordenador ha hecho mil sumas en un instante.

Claro, aquí podríamos haber multiplicado 1.000 × 5 directamente. Pero en un episodio de verdad la
recompensa **cambia en cada paso** (depende de la velocidad, del esfuerzo...), y entonces no hay
multiplicación que valga: hay que ir sumando paso a paso. Exactamente así es como se calcula el
retorno de verdad.
"""),

md(r"""### Una historia: el niño que sumó del 1 al 100

Se cuenta que, hace más de 200 años, un maestro alemán quiso tener a su clase entretenida un buen rato
y mandó sumar todos los números **del 1 al 100**. Un niño de unos 9 años, **Carl Friedrich Gauss**, dio
la respuesta correcta casi al instante, con un truco ingenioso (que luego le convertiría en uno de los
matemáticos más grandes de la historia).

Tú no necesitas el truco: tienes un bucle. Fíjate en el `range(1, 101)`: empieza en 1 y para **antes**
del 101, así que llega hasta el 100. Y esta vez no sumamos siempre lo mismo, sino **el contador** `n`,
que vale 1, luego 2, luego 3...
"""),

code(r"""suma = 0
for n in range(1, 101):
    suma = suma + n
print(suma)"""),

md(r"""**5050**. La misma respuesta que dio el pequeño Gauss.

(¿Su truco? Emparejar el primero con el último: 1 + 100 = 101; 2 + 99 = 101; 3 + 98 = 101... Hay 50
parejas que suman 101 cada una: 50 × 101 = 5.050. Precioso, ¿verdad? A veces pensar ahorra muchas
cuentas. Pero cuando no hay truco, el bucle siempre funciona.)
"""),

md(r"""## 8 · El simulador de la pelota, con bucle

Llegó el momento. Vamos a convertir el simulador del NB06 (el que había que copiar celda a celda) en un
simulador con bucle. Primero, como siempre, el **estado inicial**: el mundo y la pelota. No hay nada
nuevo en esta celda:
"""),

code(r"""gravedad = 10           # la pelota gana 10 m/s cada segundo
paso_tiempo = 0.1       # cada pasito dura una décima de segundo
altura = 2.0            # metros
velocidad = 0.0         # metros por segundo (hacia abajo)"""),

md(r"""Y ahora, **el simulador entero**. Las dos líneas de la cadena de oro del NB06 (fuerza → velocidad →
posición) van **dentro** de un bucle de 6 vueltas, y un `print` dentro del bucle nos enseña cada fila de
la tabla. Usamos `range(1, 7)` para que los pasos se numeren del 1 al 6, como en la tabla del NB02:
"""),

code(r"""for paso in range(1, 7):
    velocidad = velocidad + gravedad * paso_tiempo
    altura = altura - velocidad * paso_tiempo
    print("paso", paso, "| velocidad", velocidad, "| altura", altura)"""),

md(r"""**Es la tabla del NB02**, la que hiciste a mano con lápiz y papel, generada en un instante. Compárala
con la tuya fila a fila:

| Paso | Velocidad | Altura (a mano, NB02) | Altura (Python) |
|---|---|---|---|
| 1 | 1 | 1,90 | `1.9` |
| 2 | 2 | 1,70 | `1.7` |
| 3 | 3 | 1,40 | `1.4` |
| 4 | 4 | 1,00 | `0.9999999999999999` |
| 5 | 5 | 0,50 | `0.4999999999999999` |
| 6 | 6 | −0,10 | `-0.1000000000000002` |

¡Ahí está el **ruido de los decimales** del NB06! En vez de 1 sale 0,9999999999999999: el número 0,1
no se puede guardar exacto en binario, y los minúsculos errores se van **acumulando** paso a paso (como
avisaba el ejercicio E9 del NB06). La diferencia es de una diezmilbillonésima de metro: completamente
despreciable para la física, pero fea de leer.

Y en el paso 6, la pelota está **por debajo del suelo**, como en el NB02: nuestro simulador todavía no
sabe que existe un suelo. Lo arreglaremos pronto.
"""),

md(r"""### La misma tabla, limpia

Para leerla mejor, redondeamos la altura a 2 decimales con `round` (NB06) **solo al mostrarla**: la
caja `altura` sigue guardando el valor exacto. Como el bucle ha cambiado las cajas, primero hay que
**volver al estado inicial** (si no, la pelota seguiría cayendo desde −0,1):
"""),

code(r"""altura = 2.0
velocidad = 0.0
for paso in range(1, 7):
    velocidad = velocidad + gravedad * paso_tiempo
    altura = altura - velocidad * paso_tiempo
    print("paso", paso, "| velocidad", velocidad, "| altura", round(altura, 2))"""),

md(r"""Ahora sí: **1.9, 1.7, 1.4, 1.0, 0.5, -0.1**. Idéntica a tu tabla del NB02.

Párate un momento a apreciar lo que tienes delante. Son **cinco líneas** de código. Si cambias `range(1,
7)` por `range(1, 1001)`, simulas mil pasitos en lugar de seis, sin escribir nada más. Si cambias
`gravedad = 10` por `gravedad = 1.6`, estás en **la Luna**. Este es, en miniatura, el corazón de
MuJoCo.
"""),

md(r"""## 9 · Comprobemos el NB02: pasos grandes contra pasos pequeños

En el NB02 te conté algo que tuviste que **creerte**: que con pasos grandes el simulador se equivoca, y
que con pasos más pequeños se acerca a la realidad. En concreto:

- La física exacta dice que, a los **0,5 segundos**, la pelota está a **0,75 metros** (la fórmula, h = h₀ − ½·g·t², la dedujimos en el NB04b).
- Con pasos de 0,1 segundos, nuestra tabla dice 0,50 (un error de 25 cm).
- Y te dije que con pasos de una milésima saldría **0,7475**.

Ahora tienes las herramientas para **comprobarlo tú**. La idea: simular siempre **medio segundo**, pero
con pasitos de distinto tamaño. Si el paso es de 0,1 s, medio segundo son **5** pasos; si es de 0,01 s,
son **50**; si es de 0,001 s, son **500**. Y como no queremos ver 500 líneas, el `print` va **fuera** del
bucle.

**Primero, pasos de 0,1 segundos (5 pasos):**
"""),

code(r"""paso_tiempo = 0.1
altura = 2.0
velocidad = 0.0
for paso in range(5):
    velocidad = velocidad + gravedad * paso_tiempo
    altura = altura - velocidad * paso_tiempo
print("Con pasos de 0.1 s:", round(altura, 4), "metros")"""),

md(r"""**0.5 metros**, como en la tabla: 25 cm por debajo de la verdad (0,75). **Ahora, pasos diez veces
más pequeños, de 0,01 segundos (50 pasos).** Fíjate en que solo cambian dos números: el tamaño del paso
y cuántas vueltas da el bucle:
"""),

code(r"""paso_tiempo = 0.01
altura = 2.0
velocidad = 0.0
for paso in range(50):
    velocidad = velocidad + gravedad * paso_tiempo
    altura = altura - velocidad * paso_tiempo
print("Con pasos de 0.01 s:", round(altura, 4), "metros")"""),

md(r"""**0.725 metros**: ya solo 2,5 cm por debajo de la verdad. ¡Mucho mejor! **Y ahora, pasos de una
milésima de segundo (500 pasos):**"""),

code(r"""paso_tiempo = 0.001
altura = 2.0
velocidad = 0.0
for paso in range(500):
    velocidad = velocidad + gravedad * paso_tiempo
    altura = altura - velocidad * paso_tiempo
print("Con pasos de 0.001 s:", round(altura, 4), "metros")"""),

md(r"""**0.7475 metros**: exactamente lo que te contó el NB02. A solo 2,5 **milímetros** de la verdad.

Pongámoslo todo junto:

| Tamaño del paso | Nº de pasos para 0,5 s | Altura calculada | Error (verdad: 0,75 m) |
|---|---|---|---|
| 0,1 s | 5 | 0,5 m | 25 cm |
| 0,01 s | 50 | 0,725 m | 2,5 cm |
| 0,001 s | 500 | 0,7475 m | 2,5 mm |

¿Ves el patrón? **Cada vez que el paso se hace 10 veces más pequeño, el error se hace 10 veces más
pequeño.** Pero, a cambio, hay que dar **10 veces más pasos** (más trabajo para el ordenador). Es el
dilema exacto del NB02: exactitud contra velocidad. Y ahora no te lo has creído: **lo has medido**.

(Ese patrón, "el error baja al mismo ritmo que el paso", es una propiedad conocida de este método de
cálculo. Los simuladores profesionales usan métodos más astutos, pero la idea de fondo es esta.)
"""),

md(r"""## 10 · Lo que aún no sabe hacer nuestro simulador

Nuestro simulador ya repite pasitos, pero tiene un problema enorme: **la pelota atraviesa el suelo**.
Cuando la altura baja de 0, debería **chocar**: pararse o rebotar. Y para eso, el programa tendría que
hacer algo **distinto según la situación**:

```
   en cada pasito:
       mueve la pelota (la cadena de oro)
       SI la altura es menor que 0:          ← ¡una decisión!
           ponla en el suelo y frénala
```

Fíjate en ese **"si"**. Hasta ahora, nuestros programas hacían siempre lo mismo, en el mismo orden,
pasara lo que pasara. Pero el mundo está lleno de "si": **si** el robot se cae, se acaba el episodio
(NB03); **si** la temperatura baja de 20 grados, enciende la calefacción (el termostato del NB03); **si**
el torso está entre 1 y 2 metros, gana 5 puntos (NB04).

Hacer que un programa **tome decisiones** es la cuarta gran pieza de la programación, y el tema del
próximo notebook.
"""),

md(r"""## 11 · Resumen de la lección

1. Un **bucle** repite instrucciones sin copiarlas. `for i in range(n):` repite **n** veces lo que hay
   debajo.
2. Las líneas que se repiten (el **cuerpo**) llevan **sangría** (4 espacios). Lo primero que vuelve a la
   izquierda está **fuera** del bucle y se ejecuta una vez al final. Sin sangría: `IndentationError`.
3. La variable del bucle cambia en cada vuelta. **`range(n)`** da 0, 1, ..., n − 1 (se cuenta **desde
   0**); **`range(inicio, fin)`** empieza en `inicio` y para **antes** de `fin`.
4. El **acumulador**: hucha a 0 **antes** del bucle, sumar **dentro**, mirar **después**. Así se calcula
   el **retorno** de un episodio (5.000 para el robot quieto) o la suma de Gauss (5.050).
5. Con un bucle, la pelota del NB02 se simula en cinco líneas, y has **medido** que **pasos 10 veces más
   pequeños dan un error 10 veces menor** (0,5 → 0,725 → 0,7475 m; verdad 0,75 m), a cambio de 10 veces
   más pasos.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Bucle** | Una instrucción que repite otras varias veces. |
| **`for`** | La palabra de Python para empezar un bucle: "para cada...". |
| **`range`** | Un recorrido de números: `range(3)` es 0, 1, 2. |
| **Cuerpo del bucle** | Las líneas con sangría que se repiten. |
| **Sangría** | Los espacios al principio de una línea; en Python marcan qué está dentro de qué. |
| **`IndentationError`** | Error por sangría que falta o sobra. |
| **Contador** | La variable del bucle, que cambia en cada vuelta. |
| **Acumulador** | Una variable que va sumando cosas vuelta a vuelta, como una hucha. |
"""),

md(r"""## 12 · Ejercicios

Si estás ejecutando el cuaderno, crea una celda nueva para cada uno. Si estás leyendo, escríbelo en un
papel y compara. En los de "predice", **no hagas trampa**: piensa primero.

**E1.** Escribe un bucle que muestre cinco veces la frase "Practico, me caigo, aprendo".

**E2.** Predice qué valores muestra un bucle con `range(4)`. ¿Y con `range(2, 6)`?

**E3.** Predice cuántas veces sale cada mensaje:

```python
for i in range(3):
    print("A")
    print("B")
print("C")
```

**E4.** Escribe un bucle que muestre el **premio por avanzar** del NB04 (1,25 × velocidad) para las
velocidades 1, 2, 3, 4 y 5.

**E5.** En el NB04 (P8), un robot aguantaba **400 pasos** ganando **5,95 puntos** en cada uno. Calcula su
retorno con un acumulador.

**E6.** ¿Qué saldría si, por error, pusiéramos la hucha **dentro** del bucle?

```python
for paso in range(1000):
    total = 0
    total = total + 5
print(total)
```

**E7.** Modifica la pelota para simular medio segundo **en la Luna**, donde la gravedad es de unos
**1,6** m/s cada segundo, con pasos de 0,001 s. ¿A qué altura queda? (La física exacta dice 1,8 m.)

**E8.** **Reto.** Cuenta hacia atrás para el despegue de un cohete: muestra 10, 9, 8... hasta 1. Pista:
`range` admite un **tercer** número, el **salto** entre valores; con un salto de `-1` cuenta hacia atrás:
`range(10, 0, -1)`.
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
for i in range(5):
    print("Practico, me caigo, aprendo")
```

La frase sale 5 veces. El nombre del contador (`i`) da igual, porque aquí no lo usamos.
</details>

<details>
<summary>▶ Solución E2</summary>

- `range(4)` → **0, 1, 2, 3** (cuatro valores, empezando en 0).
- `range(2, 6)` → **2, 3, 4, 5** (empieza en 2 y para **antes** del 6; salen 6 − 2 = 4 valores).
</details>

<details>
<summary>▶ Solución E3</summary>

"A" sale **3** veces y "B" sale **3** veces (los dos tienen sangría: están dentro del bucle, y se
alternan: A, B, A, B, A, B). "C" sale **1** vez, al final (no tiene sangría: está fuera).
</details>

<details>
<summary>▶ Solución E4</summary>

```python
for velocidad in range(1, 6):
    print("velocidad", velocidad, "-> premio", 1.25 * velocidad)
```

Salida: 1.25, 2.5, 3.75, 5.0 y 6.25 para las velocidades 1 a 5. Recuerda que `range(1, 6)` para
**antes** del 6, así que llega hasta el 5.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
total = 0
for paso in range(400):
    total = total + 5.95
print(total)
print(round(total, 2))
```

La primera línea muestra `2380.000000000001` (¡el ruido de los decimales acumulado en 400 sumas!) y la
segunda, ya redondeada, **`2380.0`**: los mismos **2.380 puntos** que calculaste en el NB04.
</details>

<details>
<summary>▶ Solución E6</summary>

Saldría **`5`**, no 5.000. En cada vuelta, la línea `total = 0` **vacía la hucha**, y luego se le suma
5. Así que al acabar cada vuelta la hucha tiene siempre 5, y al final también. Por eso la hucha se
prepara **antes** del bucle, una sola vez.
</details>

<details>
<summary>▶ Solución E7</summary>

```python
gravedad = 1.6
paso_tiempo = 0.001
altura = 2.0
velocidad = 0.0
for paso in range(500):
    velocidad = velocidad + gravedad * paso_tiempo
    altura = altura - velocidad * paso_tiempo
print(round(altura, 4))
```

Sale **1.7996** metros, a solo 0,4 milímetros del valor exacto (1,8 m). En la Luna, en medio segundo la
pelota solo ha bajado unos 20 cm, frente a los 125 cm de la Tierra: la gravedad lunar es unas seis veces
más débil. (Si luego vuelves a ejecutar celdas de la pelota terrestre, acuérdate de poner `gravedad =
10` otra vez.)
</details>

<details>
<summary>▶ Solución E8</summary>

```python
for i in range(10, 0, -1):
    print(i)
print("¡Despegue!")
```

`range(10, 0, -1)` empieza en 10, va **restando 1** en cada vuelta y para **antes** del 0, así que
muestra 10, 9, 8, 7, 6, 5, 4, 3, 2, 1. El "¡Despegue!" va **fuera** del bucle, sin sangría, para que
salga una sola vez al final.
</details>
"""),

md(r"""## 13 · 🛠 Práctica en MuJoCo: tu propio bucle de simulación

En el NB06 tuviste que **copiar** la celda de `mj_step` para cada pasito. Se acabó: hoy escribes
**tu propio bucle de simulación**, que es exactamente lo que hay en el corazón de todo programa
que usa MuJoCo, desde una pelota hasta un humanoide que aprende a andar:

```
   for paso in range(cuantos_pasitos):
       mujoco.mj_step(modelo, datos)
```

Dos líneas. Y con ellas vas a repetir con MuJoCo el experimento del apartado 9 (pasos grandes
contra pasos pequeños) y a dejar caer al humanoide con tu propio bucle.
"""),

md(r"""### Paso 1 · La pelota, otra vez (ya escrita)

El mismo plano del NB02, con la gravedad redonda de nuestras tablas (−10) escrita dentro del
plano, en la línea `<option ...>`:
"""),

code(r"""import mujoco
import taller

PELOTA = '''
<mujoco>
  <option gravity="0 0 -10"/>
  <worldbody>
    <light pos="0 0 5"/>
    <geom type="plane" size="5 5 0.1" rgba=".8 .9 .8 1"/>
    <body name="pelota" pos="0 0 2">
      <freejoint/>
      <geom type="sphere" size="0.05" rgba="1 .3 .1 1"/>
    </body>
  </worldbody>
</mujoco>
'''"""),

md(r"""### Paso 2 · Tu bucle: medio segundo con pasos de 0,1

Igual que en el apartado 9: medio segundo con pasos de 0,1 segundos son **5** pasitos. Las dos
primeras líneas (cargar y poner el paso) ya las conoces del NB06. Lo nuevo, lo tuyo, es el
**bucle**: en vez de copiar `mujoco.mj_step(modelo, datos)` cinco veces, se lo pides al `for`. Fíjate
en la **sangría**: `mj_step` está dentro del bucle (se repite) y el `print` está fuera (sale una
vez, al final):
"""),

code(r"""modelo, datos = taller.cargar(PELOTA)
modelo.opt.timestep = 0.1

for paso in range(5):
    mujoco.mj_step(modelo, datos)

print("Pasos de 0.1 s -> reloj:", round(datos.time, 4), "| altura:", round(datos.qpos[2], 4), "m")"""),

md(r"""**0,5 metros**, igual que tu simulador del apartado 9. Ahora, pasos **diez veces más pequeños**.
Como en el apartado 9, solo cambian dos números: el tamaño del paso y las vueltas del bucle:
"""),

code(r"""modelo, datos = taller.cargar(PELOTA)
modelo.opt.timestep = 0.01

for paso in range(50):
    mujoco.mj_step(modelo, datos)

print("Pasos de 0.01 s -> reloj:", round(datos.time, 4), "| altura:", round(datos.qpos[2], 4), "m")"""),

md(r"""**0,725**, como el tuyo. Y ahora, con pasitos de una milésima. **Escríbelo tú** antes de mirar la
celda de abajo: ¿qué dos números cambian?
"""),

code(r"""modelo, datos = taller.cargar(PELOTA)
modelo.opt.timestep = 0.001

for paso in range(500):
    mujoco.mj_step(modelo, datos)

print("Pasos de 0.001 s -> reloj:", round(datos.time, 4), "| altura:", round(datos.qpos[2], 4), "m")"""),

md(r"""**0,7475**. La misma tabla del apartado 9, número a número:

| Paso | Pasitos | Tu simulador (apartado 9) | MuJoCo | Verdad |
|---|---|---|---|---|
| 0,1 s | 5 | 0,5 m | 0,5 m | 0,75 m |
| 0,01 s | 50 | 0,725 m | 0,725 m | 0,75 m |
| 0,001 s | 500 | 0,7475 m | 0,7475 m | 0,75 m |

MuJoCo usa, para una pelota que cae, **la misma receta** que tú (primero la gravedad cambia la
velocidad; luego la velocidad nueva cambia la altura), así que comete **el mismo error** con los
pasos grandes. Por eso el humanoide usa pasitos de 0,003 s (NB05): con pasos finos, el error es
pequeño.
"""),

md(r"""### Paso 3 · La tabla, paso a paso

Con el `print` **dentro** del bucle (con sangría), sale una línea en cada vuelta. Es la tabla del
NB02, escrita ahora por MuJoCo. Usamos `range(1, 7)` para contar los pasos desde 1, como la tabla:
"""),

code(r"""modelo, datos = taller.cargar(PELOTA)
modelo.opt.timestep = 0.1

for paso in range(1, 7):
    mujoco.mj_step(modelo, datos)
    print("paso", paso, "| tiempo", round(datos.time, 1), "| altura", round(datos.qpos[2], 2))"""),

md(r"""1,9 → 1,7 → 1,4 → 1,0 → 0,5 → **−0,1**. En el paso 6, la pelota **atraviesa el suelo**, la rareza 1
del NB02. Tu simulador del apartado 8 hacía lo mismo... y MuJoCo, con pasos tan grandes, también.
"""),

md(r"""### Paso 4 · El humanoide, con tu bucle

Ahora, el robot de verdad. Un segundo del humanoide son **333 pasitos** de 0,003 s (NB05). Tu bucle
es **idéntico** al de la pelota: solo cambia el robot y el número de vueltas. Al final, una foto (ya
escrita) para ver cómo ha quedado:
"""),

code(r"""modelo, datos = taller.cargar("humanoide")

for paso in range(333):
    mujoco.mj_step(modelo, datos)

print("Reloj:", round(datos.time, 3), "s | altura del torso:", round(datos.qpos[2], 2), "m")
taller.foto(modelo, datos, titulo="Tras 333 pasitos de tu bucle");"""),

md(r"""Tras un segundo, el torso está a **0,28 m**: en el suelo. Es la misma caída del NB00, pero esta
vez la ha calculado **tu bucle**: 333 llamadas a `mj_step`, una detrás de otra.

Lo que hace `taller.video` (la herramienta del curso que llevas usando desde el NB00) es justo esto:
un bucle de `mj_step` que, cada pocos pasitos, saca una foto. Ya sabes lo que hay dentro de esa caja
negra.
"""),

md(r"""### Paso 5 · El acumulador, sobre la simulación

Una pregunta que necesita un **acumulador** (apartado 7): durante ese primer segundo, ¿a qué altura
estuvo el torso **de media**? La receta de siempre: hucha a 0 **antes** del bucle, sumar **dentro**
(la altura de cada pasito), mirar **después** (dividir entre el número de pasitos):
"""),

code(r"""modelo, datos = taller.cargar("humanoide")

suma_alturas = 0
for paso in range(333):
    mujoco.mj_step(modelo, datos)
    suma_alturas = suma_alturas + datos.qpos[2]

print("Altura media del torso en el primer segundo:", round(suma_alturas / 333, 2), "m")"""),

md(r"""**0,98 m de media**: empezó a 1,4 y acabó a 0,28. Ya ves lo que hacía la recompensa del NB04 al
**sumar** cosas paso a paso durante un episodio: es esta misma hucha, dentro del bucle de
simulación.
"""),

md(r"""### Tus retos

**Reto 1.** Haz con MuJoCo el ejercicio E7 (la pelota en la **Luna**): medio segundo con pasos de
0,001 s y gravedad 1,6. Pista: después de cargar la pelota, cambia la gravedad con
`modelo.opt.gravity = [0, 0, -1.6]` (NB06). ¿Sale lo mismo que con tu simulador?

**Reto 2.** Cambia el bucle del Paso 4 para simular **3 segundos** del humanoide. ¿Cuántas vueltas
necesitas? ¿Dónde está el torso al final?

**Reto 3.** En el Paso 3, usa pasos de **0,05** s. ¿Cuántas vueltas hacen falta para llegar a los
0,6 segundos? ¿Atraviesa también el suelo?

<details>
<summary>▶ Solución Reto 1</summary>

```python
modelo, datos = taller.cargar(PELOTA)
modelo.opt.timestep = 0.001
modelo.opt.gravity = [0, 0, -1.6]

for paso in range(500):
    mujoco.mj_step(modelo, datos)

print(round(datos.qpos[2], 4))
```

Sale **1.7996**, exactamente lo mismo que tu simulador de cajas del E7 (y a 0,4 mm de la verdad, 1,8 m).
</details>

<details>
<summary>▶ Solución Reto 2</summary>

3 segundos ÷ 0,003 = **1000 vueltas**: `for paso in range(1000):`. Al final el torso está a unos
**0,08 m**: el robot está completamente tumbado en el suelo (a los 3 segundos ya ha dejado de rodar).
</details>

<details>
<summary>▶ Solución Reto 3</summary>

0,6 ÷ 0,05 = **12** vueltas: `range(1, 13)` y `modelo.opt.timestep = 0.05`. En el paso 12 (0,60 s) la
pelota está a **0,05 m** (justo su radio: rozando el suelo) y, si das una vuelta más (`range(1, 14)`),
en el paso 13 salta a **−0,275**: sí, lo atraviesa, y más que con pasos de 0,1, igual que viste en el
Reto 1 del NB02. Con pasos grandes, que atraviese o no el suelo depende
de la casualidad de dónde caiga cada salto.
</details>

### Qué has aprendido de MuJoCo hoy

- **El bucle de simulación**: `for paso in range(n): mujoco.mj_step(modelo, datos)`. Todo programa de
  MuJoCo tiene uno.
- Con el `print` **dentro** del bucle ves cada pasito; **fuera**, solo el final.
- Para un mismo tiempo simulado: paso ÷ 10 → vueltas × 10 → error ÷ 10. MuJoCo lo confirma (0,5 →
  0,725 → 0,7475 m).
- Un **acumulador** dentro del bucle mide algo durante toda la simulación (altura media del torso: 0,98 m).
- `taller.video` es, por dentro, un bucle de `mj_step` que hace fotos.

En la práctica del NB08 tu bucle aprenderá a **parar solo**: con un `if` detectarás el momento en
que el humanoide se cae y acabarás el episodio con `break`.
"""),


md(r"""## 14 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Ya tienes tres de las cuatro grandes piezas de la programación: **instrucciones en orden** (NB05),
**memoria** (NB06) y **repetición** (este NB07). Con ellas has construido un simulador de verdad, has
comprobado por ti mismo una propiedad de los simuladores que antes solo podías creerte, y has escrito
el bucle que mueve a MuJoCo. Eso es pensar
como un ingeniero: **no te lo creas, mídelo**.

En el **NB08** llega la cuarta pieza: las **decisiones** (`if`, "si..."). Con ella, la pelota por fin
**chocará con el suelo**, sabremos cuándo **se acaba un episodio** como hace el simulador del humanoide,
y escribiremos nuestra primera **política a mano**: el termostato del NB03, en código.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB07_bucles.ipynb")
    build(out, cells, title="NB07 · Repetir sin cansarse: el bucle for")
