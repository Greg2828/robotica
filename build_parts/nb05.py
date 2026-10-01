"""Construye NB05 · Tu primer contacto con el ordenador (Parte 1 · Lección 1).

Primer notebook CON código, en microdosis: una idea nueva por celda. Antes del
código, todo el contexto: qué es un ordenador, un programa, un lenguaje, un
notebook y cómo se ejecuta. Luego: print("hola"), texto vs número, orden de
ejecución, errores REALES (celdas code_err) y cómo leerlos, comentarios, punto
decimal (no coma), y la recompensa del NB04 calculada por el ordenador.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB05 · Tu primer contacto con el ordenador

**Parte 1 · Primeros pasos con el ordenador — Lección 1**

> Terminaste la Parte 0: ya entiendes **qué** es un robot que aprende, **por qué** andar es
> difícil y **cómo** se le guía con premios. Ahora toca empezar a construir las herramientas
> para hacerlo de verdad. Y la primera herramienta es **hablar con el ordenador**.

Te lo prometí en la primera lección: el código llegaría **en gotas, una idea nueva por vez**.
Así va a ser. Hoy aparecerán las primeras celdas de código de todo el curso, pero:

- **Antes** de ver ninguna, entenderemos qué es un ordenador, qué es un programa y qué es este
  documento que estás leyendo.
- Cada celda de código tendrá **una sola idea nueva**, normalmente en **una sola línea**.
- Antes de cada celda te diré **qué va a pasar**, y después te explicaré **qué ha pasado**.

Al final de hoy habrás escrito tu primer programa, habrás visto tus primeros errores (y sabrás
que no pasa nada por cometerlos), y habrás hecho que el ordenador calcule la recompensa de
nuestro humanoide. Vamos despacio.
"""),

md(r"""## 1 · ¿Qué es un ordenador, en realidad?

Un ordenador es una máquina que hace **operaciones muy sencillas** (sumar, comparar dos números,
copiar un dato de un sitio a otro) a una **velocidad increíble**: miles de millones por segundo.
El procesador de la Raspberry Pi en la que se ha preparado este curso hace del orden de **miles de
millones** de operaciones cada segundo.

Pero un ordenador tiene dos características que conviene grabarse a fuego:

1. **Es completamente obediente.** Hace **exactamente** lo que le dices. Ni más, ni menos.
2. **No tiene sentido común.** No sabe lo que "quieres decir"; solo sabe lo que **has dicho**.

¿Te suena? Es el **rey Midas** del NB04, o el genio de la lámpara que concede los deseos al pie de
la letra. Si le pides a un ordenador algo con una pequeña errata, no la corregirá "porque se
entiende": hará la errata, o se quejará de que no entiende.

La mejor imagen: un ordenador es como un **cocinero rapidísimo que no sabe cocinar**. Si le das una
receta, la sigue a una velocidad de vértigo y sin cansarse jamás. Pero si la receta dice "añade sal"
y no dice cuánta, se queda parado. Y si dice "añade 3 kilos de sal" por una errata, añade 3 kilos de
sal sin pestañear.
"""),

md(r"""## 2 · ¿Qué es un programa?

Un **programa** es justo eso: **una receta para el ordenador**. Una lista de instrucciones, en
orden, que el ordenador sigue una detrás de otra.

```
   RECETA (para una persona)            PROGRAMA (para un ordenador)

   1. Casca 2 huevos                    1. Guarda el número 5
   2. Bátelos                           2. Multiplícalo por 2
   3. Echa una pizca de sal             3. Muestra el resultado en pantalla
   4. Cuaja en la sartén
```

Las dos cosas que tienen en común son las más importantes:

- **El orden importa.** No puedes batir los huevos antes de cascarlos. El ordenador sigue las
  instrucciones **de arriba abajo**, en el orden en que están escritas.
- **Las instrucciones tienen que ser precisas.** A una persona le vale "una pizca de sal". Al
  ordenador hay que decírselo todo con exactitud.

Programar, por tanto, es **escribir recetas muy precisas**. Nada más (y nada menos).
"""),

md(r"""## 3 · ¿En qué idioma se le habla? Python

Por dentro, el ordenador solo entiende **ceros y unos** (en su procesador, todo son interruptores
encendidos o apagados). Escribir recetas en ceros y unos sería una tortura. Por eso existen los
**lenguajes de programación**: idiomas intermedios, pensados para que una **persona** pueda
escribirlos y leerlos con comodidad, y que luego un programa especial **traduce** a los ceros y unos
del ordenador.

```
   tú escribes           un traductor            el procesador
   en Python    ──────►  lo convierte    ──────►  lo ejecuta
   (casi inglés)         a ceros y unos           (miles de millones de
                                                   operaciones por segundo)
```

Hay cientos de lenguajes. Nosotros usaremos **Python**, por tres razones:

1. **Es de los más fáciles de leer.** Se parece mucho al inglés escrito, sin símbolos raros por todas
   partes. Es el lenguaje que más se usa para aprender a programar.
2. **Es el lenguaje de la robótica con aprendizaje.** El simulador MuJoCo (NB02), las herramientas
   para entrenar robots y las "máquinas con ruedecillas" (las redes neuronales del NB03) se manejan
   todas desde Python.
3. **Es gratis** y funciona en cualquier ordenador, también en la Raspberry Pi.

(El nombre no viene de la serpiente, sino de un grupo de humor británico, los Monty Python. Al
creador del lenguaje le gustaban mucho.)

No hace falta saber inglés para programar en Python. Solo hay unas pocas palabras en inglés que
aprenderemos de una en una, y te diré siempre qué significan.
"""),

md(r"""## 4 · ¿Qué es este documento? Un cuaderno con celdas

Lo que estás leyendo ahora mismo se llama un **notebook** ("cuaderno", en inglés). Es como un
**cuaderno de laboratorio**: mezcla explicaciones escritas con experimentos que se pueden hacer ahí
mismo.

Un notebook está hecho de **celdas**, unas debajo de otras. Hay dos tipos:

```
   ┌────────────────────────────────────────────────────────────┐
   │ CELDA DE TEXTO                                              │
   │ Como esta que estás leyendo. Explicaciones, dibujos,        │
   │ tablas. El ordenador no las ejecuta: son para ti.           │
   └────────────────────────────────────────────────────────────┘
   ┌────────────────────────────────────────────────────────────┐
   │ [1]: CELDA DE CÓDIGO                                        │
   │      una instrucción en Python                              │
   ├────────────────────────────────────────────────────────────┤
   │      ← SALIDA: lo que el ordenador responde aparece aquí,   │
   │        justo debajo de la celda                             │
   └────────────────────────────────────────────────────────────┘
```

Las celdas de código se reconocen fácilmente: tienen un **fondo distinto**, el texto con otro tipo
de letra, y a su izquierda un número entre corchetes, como `[1]`. Ese número dice **en qué orden**
se ejecutaron: `[1]` fue la primera, `[2]` la segunda... Y debajo de ellas aparece la **salida**: la
respuesta del ordenador.

**Ejecutar** una celda significa decirle al ordenador: "haz lo que pone aquí".
"""),

md(r"""## 5 · ¿Cómo lo uso? Leer o ejecutar

Puedes usar este cuaderno de dos maneras, y las dos valen.

**Manera 1 · Solo leer (por ejemplo, en la web de GitHub, desde el móvil o cualquier ordenador).**
Este cuaderno ya viene **ejecutado**: debajo de cada celda de código ya está la salida que dio el
ordenador cuando se preparó. Así que puedes leerlo entero y ver todos los resultados sin instalar
nada. Para aprender al principio, esto basta.

**Manera 2 · Ejecutarlo tú (en la Raspberry Pi).** Es la manera de **experimentar**: cambiar algo
y ver qué pasa. Para abrirlo, en la Raspberry Pi abres una **terminal** (la ventana negra donde se
escriben órdenes) y escribes estas tres líneas, pulsando Enter tras cada una:

```
cd ~/dev/robotica
source venv/bin/activate
jupyter lab
```

(No te preocupes por entender qué significan; las explicaremos más adelante. Por ahora, son "las
palabras mágicas para abrir el cuaderno".) Se abrirá el navegador con una lista de archivos: entra
en la carpeta `notebooks` y abre este.

Una vez dentro, lo único que necesitas saber es:

| Para... | Haz esto |
|---|---|
| Ejecutar una celda | Haz clic en ella y pulsa **Mayúsculas + Enter** (las dos teclas a la vez) |
| Saber si está trabajando | A su izquierda aparece `[*]`; cuando termina, sale un número, como `[3]` |
| Empezar de cero si algo se lía | Menú **Kernel → Restart Kernel** (reinicia el "motor" de Python) |

Una palabra que verás: **kernel** ("núcleo"). Es el **motor de Python** que trabaja detrás del
cuaderno: tú escribes en las celdas, y el kernel es quien las ejecuta. Si el cuaderno te pregunta
qué kernel usar, elige **"Python (robotica)"**.

> **Tranquilidad absoluta:** no puedes romper nada. Si cambias una celda y sale un desastre, borras
> lo que escribiste y vuelves a ejecutar. El ordenador no se estropea por un error en un cuaderno.
"""),

md(r"""## 6 · Tu primera línea de código

Ha llegado el momento. Vamos a pedirle al ordenador que **muestre un mensaje en la pantalla**. Es,
por tradición, el primer programa que escribe todo el mundo cuando aprende a programar, desde hace
más de 50 años: hacer que el ordenador diga "hola".

La instrucción para mostrar algo en Python se llama **`print`** (en inglés, "imprimir": viene de la
época en que los ordenadores mostraban los resultados imprimiéndolos en papel). Así se escribe.
Fíjate en la celda de código de aquí debajo, y en su salida:
"""),

code(r"""print("hola")"""),

md(r"""Debajo de la celda ha aparecido la palabra **hola**. ¡Ese es tu primer programa! El ordenador ha
seguido tu receta de una sola instrucción: "muestra la palabra hola".

Vamos a desmontar esa línea, pieza a pieza, porque cada pieza importa:

```
   print  (  "hola"  )
   ─────  ─  ──────  ─
     │    │     │    └── cierra el paréntesis
     │    │     └─────── LO QUE quieres mostrar, entre comillas
     │    └───────────── abre el paréntesis: "a continuación, lo que te doy"
     └────────────────── LA ORDEN: "muestra en pantalla"
```

- **`print`** es el nombre de la orden. Python conoce muchas órdenes con nombre; esta es la primera.
- **Los paréntesis `( )`** rodean lo que le **das** a la orden para que trabaje con ello. Es como
  darle los ingredientes al cocinero.
- **Las comillas `" "`** le dicen a Python: "esto es **texto**, tal cual; no intentes entenderlo,
  solo cópialo". Por eso en la salida sale `hola`, sin comillas: las comillas no son parte del
  mensaje, son solo el "envoltorio" que marca dónde empieza y dónde acaba.
"""),

md(r"""## 7 · El texto entre comillas es libre

Lo que va entre comillas puede ser **cualquier texto**: con mayúsculas, espacios, tildes, la ñ,
signos de exclamación... Python lo copia tal cual. Mira:
"""),

code(r"""print("¡Hola, robot! Mañana aprenderás a andar.")"""),

md(r"""Exactamente el texto de dentro de las comillas, con su tilde, su ñ y sus signos de exclamación.

A un texto así, entre comillas, los programadores lo llaman **cadena de texto** (en inglés,
*string*, que significa "hilo" o "cadena": imagina las letras ensartadas una detrás de otra como
las cuentas de un collar). Cuando oigas "una cadena", piensa: "un trozo de texto entre comillas".
"""),

md(r"""## 8 · Varias instrucciones: de arriba abajo

Un programa casi nunca tiene una sola instrucción. Cuando hay varias, el ordenador las sigue **en
orden, de arriba abajo**, como una receta. Esta celda tiene tres líneas (la idea nueva es solo
esa: varias líneas en una celda):
"""),

code(r"""print("1. El robot percibe cómo está.")
print("2. La mente decide qué hacer.")
print("3. Los motores se mueven.")"""),

md(r"""Tres mensajes, **en el mismo orden** en que están escritos. Si cambiaras el orden de las líneas,
cambiaría el orden de los mensajes. El ordenador no "entiende" que el robot primero percibe y luego
decide (¡el bucle del NB03!): simplemente ejecuta la línea 1, luego la 2, luego la 3. **El orden lo
pones tú.**
"""),

md(r"""## 9 · Texto y números no son lo mismo

Ahora una idea muy importante, en dos celdas. Primero, algo entre comillas que **parece** una
cuenta:
"""),

code(r"""print("2 + 3")"""),

md(r"""El ordenador ha mostrado `2 + 3`, tal cual. ¿Por qué no ha calculado 5? Porque **está entre
comillas**, y las comillas significan "esto es texto, cópialo sin pensar". Para el ordenador,
`"2 + 3"` no es una suma: son cinco caracteres (un 2, un espacio, un +, otro espacio y un 3).

Ahora, **la misma cosa sin comillas**:
"""),

code(r"""print(2 + 3)"""),

md(r"""¡Ahora sí: **5**! Sin comillas, Python **interpreta** lo que hay dentro: ve dos números y un signo
de sumar, calcula la suma, y muestra el resultado.

```
   print("2 + 3")   →  2 + 3     (texto: lo copia tal cual)
   print(2 + 3)     →  5         (números: los calcula)
```

Esta diferencia —**con comillas es texto que se copia; sin comillas es algo que Python interpreta**—
es una de las ideas más importantes de toda la programación, y te va a explicar de golpe el primer
error que vamos a ver.
"""),

md(r"""## 10 · Tus primeros errores (y por qué son buenos)

Vas a cometer **muchísimos** errores al programar. Todo el mundo los comete, todos los días, también
los profesionales con veinte años de experiencia. Un error no es un fracaso: es el ordenador
diciéndote "no te he entendido, y te digo dónde".

Por eso vamos a provocar **tres errores a propósito**, para aprender a leerlos con calma. Las tres
celdas que siguen **fallan adrede**: lo que verás debajo, en rojo o con un fondo de color, es el
**mensaje de error**.

**Error 1.** Vamos a olvidar las comillas alrededor de `hola`:
"""),

code_err(r"""print(hola)"""),

md(r"""El mensaje de error parece un jaleo, pero tiene truco: **lee primero la última línea**. Es la que
explica qué ha pasado. Aquí dice:

```
NameError: name 'hola' is not defined
```

Traducido: **"Error de nombre: el nombre `hola` no está definido"**. ¿Y eso por qué? Recuerda el
apartado anterior: **sin comillas, Python interpreta**. Así que, al ver `hola` sin comillas, Python
no piensa "es un texto"; piensa "esto debe de ser el **nombre** de algo que conozco"... y busca algo
llamado `hola`. Como no existe nada con ese nombre, se queja.

Además, más arriba en el mensaje verás una **flecha** `---->` a la izquierda de `print(hola)`: señala
**la línea** donde está el problema. Aquí la celda solo tiene una línea, pero cuando tenga veinte, esa
flecha te ahorrará mucho tiempo. (Encima también pone `Cell In[...], line 1`: "en la celda tal, línea
1".)

(Dentro de poco aprenderás a **crear** cosas con nombre. Entonces este mensaje te parecerá obvio.)
"""),

md(r"""**Error 2.** Ahora escribimos bien las comillas, pero ponemos `Print` con **P mayúscula**:"""),

code_err(r"""Print("hola")"""),

md(r"""Última línea:

```
NameError: name 'Print' is not defined
```

"El nombre `Print` no está definido". (Si algún día ejecutas Python fuera del cuaderno, verás que a
veces incluso añade *Did you mean: 'print'?*, "¿querías decir `print`?".) Aquí aprendemos algo
importante: **para Python, mayúsculas y minúsculas son letras
distintas**. `print` y `Print` son, para él, dos palabras tan diferentes como "casa" y "cosa". Es el
cocinero literal: no "se imagina" que querías decir `print`.
"""),

md(r"""**Error 3.** Ahora abrimos las comillas pero se nos olvida cerrarlas:"""),

code_err(r"""print("hola)"""),

md(r"""Última línea:

```
SyntaxError: unterminated string literal (detected at line 1)
```

"Error de sintaxis: cadena de texto sin terminar (detectado en la línea 1)". La **sintaxis** es la
**gramática** de un lenguaje: las reglas de cómo se escribe. Aquí hemos roto una regla: abrimos unas
comillas y nunca las cerramos, así que Python no sabe dónde acaba el texto. Aquí la flecha es distinta: una marquita `^` debajo de la
línea, que señala el **sitio exacto** donde empieza la cadena que no se cerró.

### Cómo leer cualquier error, en tres pasos

```
   1. Lee la ÚLTIMA línea: dice el TIPO de error y una frase que lo explica.
   2. Busca la FLECHA: ----> señala la línea; ^ señala el sitio exacto.
   3. Mira lo señalado con calma: casi siempre es una errata.
```

| Tipo de error | Qué suele significar |
|---|---|
| `NameError` | Has usado un nombre que Python no conoce (errata, mayúsculas, o faltan comillas) |
| `SyntaxError` | Has roto la gramática: falta un paréntesis, unas comillas... |

Con estos dos tipos ya cubres la mayoría de los errores de un principiante. Iremos conociendo más.
"""),

md(r"""## 11 · Notas para humanos: los comentarios

A veces queremos escribir una **nota** dentro del código, para nosotros o para otra persona, que el
ordenador debe **ignorar**. Para eso existe el símbolo **almohadilla `#`**: todo lo que va detrás de
un `#`, hasta el final de la línea, es un **comentario**, y Python no lo ejecuta.
"""),

code(r"""# Esto es un comentario: Python no lo ejecuta, es solo para quien lee.
print("Esta línea sí se ejecuta")  # y esto de aquí tampoco se ejecuta"""),

md(r"""Solo ha salido el mensaje del `print`. Los dos comentarios (el de la primera línea y el que va al
final de la segunda) han sido ignorados por completo.

Los comentarios sirven para **explicar el porqué** de las cosas. Los buenos programadores los usan
mucho, porque dentro de un mes no recordarás por qué escribiste algo. En este curso los usaremos a
menudo para ir explicando el código línea a línea.
"""),

md(r"""## 12 · Una trampa para hispanohablantes: el punto decimal

En España escribimos los decimales con **coma**: 1,25. Pero Python (como casi todos los lenguajes
de programación, que nacieron en países de habla inglesa) usa el **punto**: `1.25`.

¿Y qué pasa si usamos la coma? Mira esta celda, que **no da error**... pero hace algo inesperado:
"""),

code(r"""print(1,25)"""),

md(r"""Ha mostrado `1 25`: **dos números separados**, no "uno coma veinticinco". Para Python, la coma
dentro de `print( )` significa "**y además, muestra esto otro**". Así que ha entendido: "muestra el
1, y además muestra el 25", y los ha puesto uno detrás de otro con un espacio.

Esta trampa es peligrosa precisamente porque **no da error**: el programa sigue adelante con un
número equivocado. Es el cocinero literal otra vez. Grábatelo:

> **En Python, los decimales se escriben con PUNTO: `1.25`, `0.4`, `9.8`.**

(La coma dentro de `print` es, por cierto, muy útil: sirve para mostrar varias cosas en la misma
línea, como `print("La respuesta es", 5)`. La usaremos mucho.)
"""),

md(r"""## 13 · El ordenador como calculadora: la recompensa del NB04

Para terminar, juntemos lo aprendido con la Parte 0. ¿Te acuerdas de la **pregunta P7 del NB04**? Un
paso en el que el robot sigue de pie, avanza a 2 metros por segundo y hace un esfuerzo de 1. La
recompensa era:

```
   5  +  1,25 × 2  −  0,1 × 1  =  7,4
```

En Python, **multiplicar** se escribe con un **asterisco `*`** (no con ×, que no está en el
teclado), y los decimales llevan **punto**. Así que la misma cuenta se escribe así:
"""),

code(r"""print(5 + 1.25 * 2 - 0.1 * 1)"""),

md(r"""**7.4**: exactamente lo que calculaste a mano en el NB04. Acabas de hacer que el ordenador calcule
la recompensa de un paso de nuestro humanoide. Es el mismo cálculo que hace el simulador de verdad
**67 veces por segundo**, para cada robot, durante millones de pasos.

Fíjate en un detalle: Python ha hecho **primero las multiplicaciones** (1.25 * 2 = 2.5; 0.1 * 1 = 0.1)
y **después** la suma y la resta (5 + 2.5 − 0.1 = 7.4), igual que en las matemáticas del colegio. En
la próxima lección veremos esto con calma, junto con todas las demás operaciones.
"""),

md(r"""## 14 · Resumen de la lección

1. Un **ordenador** hace operaciones sencillas a velocidad enorme; es **obediente y literal**, sin
   sentido común. Un **programa** es una **receta** precisa que sigue **de arriba abajo**.
2. Le hablamos en **Python**, un lenguaje legible y el más usado en robótica con aprendizaje. Este
   documento es un **notebook**: celdas de texto y celdas de código con su **salida** debajo; se
   ejecutan con **Mayúsculas + Enter**.
3. **`print(...)`** muestra en pantalla lo que va entre paréntesis. Con **comillas** es texto (una
   **cadena**) que se copia tal cual; **sin comillas**, Python lo **interpreta** (y calcula).
4. Los **errores** son normales: lee la **última línea** y busca la **flecha**. `NameError` = nombre
   desconocido; `SyntaxError` = gramática rota. Mayúsculas y minúsculas **cuentan**.
5. **`#`** empieza un **comentario** (Python lo ignora). Los decimales llevan **punto** (`1.25`), y
   multiplicar se escribe con **`*`**.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Programa** | Una receta precisa de instrucciones para el ordenador. |
| **Lenguaje de programación** | Un idioma para escribir programas que luego se traduce a ceros y unos. |
| **Python** | El lenguaje de programación que usaremos. |
| **Notebook / cuaderno** | Documento con celdas de texto y celdas de código ejecutables. |
| **Celda** | Cada bloque del cuaderno: de texto o de código. |
| **Ejecutar** | Decirle al ordenador que haga lo que pone en una celda (Mayúsculas + Enter). |
| **Salida** | Lo que el ordenador responde, debajo de la celda. |
| **Kernel** | El "motor" de Python que ejecuta las celdas del cuaderno. |
| **`print`** | La orden que muestra algo en pantalla. |
| **Cadena de texto (*string*)** | Un trozo de texto entre comillas. |
| **Error** | El aviso del ordenador de que no ha entendido algo, y dónde. |
| **`NameError`** | Error por usar un nombre que Python no conoce. |
| **`SyntaxError`** | Error por romper la gramática (sintaxis) del lenguaje. |
| **Comentario** | Texto detrás de `#` que Python ignora; es para las personas. |
"""),

md(r"""## 15 · Ejercicios

Si estás ejecutando el cuaderno, crea una celda nueva para cada ejercicio (en Jupyter: haz clic en
una celda, pulsa **Esc** y luego la tecla **B**, que crea una celda nueva debajo; o usa el botón
**+** de arriba).
Si solo estás leyendo, intenta **escribir en un papel** cómo sería la línea, y luego mira la
solución. Las dos formas valen.

**E1.** Escribe una línea que muestre tu nombre.

**E2.** Escribe un programa de **tres líneas** que muestre las tres primeras piezas del mapa del NB00
(el robot, el mundo de mentira, la mente), una por línea.

**E3.** Sin ejecutarlo, **predice** qué mostrará cada una de estas dos líneas, y por qué son distintas:
`print("10 + 5")` y `print(10 + 5)`.

**E4.** Esta línea tiene **un** error: `print("adiós)`. ¿Qué tipo de error dará y cómo se arregla?

**E5.** Y esta otra: `prinnt("hola")`. ¿Qué tipo de error dará?

**E6.** Calcula con Python la recompensa de un paso del NB04 (pregunta P8) en el que el robot sigue de
pie, avanza a **0,8 m/s** y tiene un castigo por esfuerzo de **0,05**. La cuenta era `5 + 1,25 × 0,8 −
0,05`. (¡Cuidado con las comas!)

**E7.** Alguien escribe `print(9,8)` queriendo mostrar la gravedad, 9,8. ¿Qué saldrá? ¿Cómo se arregla?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
print("Gregori")
```

(O el nombre que sea, siempre **entre comillas**, porque es texto.) Salida: `Gregori`.
</details>

<details>
<summary>▶ Solución E2</summary>

```python
print("1. El robot")
print("2. El mundo de mentira")
print("3. La mente")
```

Salida: las tres frases, una por línea, en ese orden (de arriba abajo).
</details>

<details>
<summary>▶ Solución E3</summary>

- `print("10 + 5")` muestra **`10 + 5`**: está entre comillas, así que es texto y se copia tal cual.
- `print(10 + 5)` muestra **`15`**: sin comillas, Python interpreta los números y el signo + y calcula.
</details>

<details>
<summary>▶ Solución E4</summary>

Dará un **`SyntaxError`** (*unterminated string literal*): se abren las comillas antes de `adiós` pero
nunca se cierran, así que Python no sabe dónde acaba el texto. Se arregla cerrándolas:
`print("adiós")`.
</details>

<details>
<summary>▶ Solución E5</summary>

Dará un **`NameError`** (*name 'prinnt' is not defined*): Python no conoce ninguna orden llamada
`prinnt` (sobra una n). Se arregla corrigiendo la errata:
`print("hola")`.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
print(5 + 1.25 * 0.8 - 0.05)
```

Salida: **`5.95`**, igual que calculaste a mano en el NB04. Las claves: decimales con **punto** (`1.25`,
`0.8`, `0.05`) y multiplicar con **`*`**.
</details>

<details>
<summary>▶ Solución E7</summary>

Saldrá **`9 8`**: la coma dentro de `print` separa dos cosas distintas, así que muestra el 9 y el 8 por
separado. **No da error**, que es justo lo peligroso. Se arregla usando punto decimal: `print(9.8)`, que
muestra `9.8`.
</details>
"""),

md(r"""## 16 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has escrito tus primeras líneas de código, y has visto que la programación no es magia: es
escribir recetas precisas para un cocinero literal. En el **NB06** daremos el siguiente paso, y es un
paso enorme: aprender a **guardar** valores en "cajas con nombre" (las **variables**), para que el
ordenador pueda **recordar** cosas como la velocidad del robot o su altura. Con eso, el cálculo de la
recompensa dejará de ser una ristra de números y se convertirá en un pequeño programa que se entiende
al leerlo. Y también descubriremos por qué el error `NameError: name 'hola' is not defined` decía
exactamente lo que decía.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB05_primer_contacto.ipynb")
    build(out, cells, title="NB05 · Tu primer contacto con el ordenador")
