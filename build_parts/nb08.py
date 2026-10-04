"""Construye NB08 · Tomar decisiones: if (Parte 1 · Lección 4).

Microdosis: comparaciones (< > <= >= == !=), True/False (bool), la trampa = vs ==
(SyntaxError real), if, if que no se cumple, else, elif (estable / en peligro /
caído), and/or y la condición "sano" del Humanoid-v5 (1 < altura < 2) dando el +5,
if dentro de un bucle: el termostato (1.ª política a mano), la pelota que REBOTA
(choque con el suelo), y break: el fin de episodio (terminado vs truncado).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB08 · Tomar decisiones: `if`

**Parte 1 · Primeros pasos con el ordenador — Lección 4**

> Ya tienes tres piezas de la programación: **instrucciones en orden** (NB05), **memoria** con las
> variables (NB06) y **repetición** con los bucles (NB07). Con ellas construiste un simulador de una
> pelota... que **atravesaba el suelo**, porque tu programa hacía siempre lo mismo, pasara lo que
> pasara. Hoy llega la cuarta pieza: que el programa **decida**.

La herramienta es la palabra **`if`** ("si", en inglés): "**si** pasa esto, haz aquello". Parece poca
cosa, pero es lo que separa una calculadora de algo que **reacciona** al mundo.

Al final de hoy:

- La pelota **chocará con el suelo y rebotará**, como una pelota de verdad.
- Escribirás tu **primera política a mano**: el termostato del NB03, en código, controlando la
  temperatura de una habitación simulada.
- Programarás el **fin de un episodio** exactamente como lo hace el simulador del humanoide: "si el
  torso baja de 1 metro, se acabó".
- Y verás que el premio de **+5 por seguir de pie** del NB04 es, por dentro, un simple `if`.

Una idea nueva por celda, como siempre.
"""),

md(r"""## 1 · El mundo está lleno de "si"

Antes del código, fíjate en cuántas veces ha aparecido ya la palabra "si" en el curso:

- **Si** el torso baja de 1 metro, el episodio termina (NB03).
- **Si** la temperatura es menor que 20 grados, enciende la calefacción (el termostato del NB03).
- **Si** el torso está entre 1 y 2 metros, gana 5 puntos (NB04).
- **Si** la pelota está por debajo del suelo, sácala y hazla rebotar (NB02).
- **Si** la escoba se inclina a la derecha, mueve la mano a la derecha (NB03).

Todas tienen la misma forma: **una pregunta de sí o no**, y **algo que hacer según la respuesta**.

```
   SI  ( pregunta de sí o no )  ENTONCES  haz algo
         └─ ¿la altura es menor que 1?      └─ termina el episodio
```

Para programarlas, necesitamos dos cosas: saber hacerle **preguntas de sí o no** al ordenador, y saber
decirle **qué hacer** según la respuesta. Empezamos por las preguntas.
"""),

md(r"""## 2 · Preguntas de sí o no: las comparaciones

La pregunta más común que se le hace a un ordenador es **comparar dos cosas**: ¿esto es mayor que
aquello? ¿son iguales? Para preguntar "¿es 3 mayor que 2?" se escribe `3 > 2`. Veamos qué responde:
"""),

code(r"""print(3 > 2)"""),

md(r"""Responde **`True`**, que en inglés significa "**verdadero**": sí, 3 es mayor que 2. Y si la pregunta
es falsa:
"""),

code(r"""print(3 < 2)"""),

md(r"""**`False`**, "**falso**": no, 3 no es menor que 2.

Un ordenador responde a cualquier comparación con **solo dos respuestas posibles**: `True` o `False`.
Ni "quizá", ni "más o menos". Estos dos valores son tan importantes que tienen su propio tipo, como
los enteros y los decimales del NB06: se llaman **booleanos** (`bool`), en honor a **George Boole**,
un matemático inglés que hace casi 200 años inventó unas matemáticas hechas solo de "verdadero" y
"falso". Esas matemáticas son hoy la base de todos los ordenadores.

Estas son todas las comparaciones de Python:

| Pregunta | En Python | Ejemplo | Respuesta |
|---|---|---|---|
| ¿Es mayor que...? | `>` | `3 > 2` | `True` |
| ¿Es menor que...? | `<` | `3 < 2` | `False` |
| ¿Es mayor **o igual** que...? | `>=` | `2 >= 2` | `True` |
| ¿Es menor **o igual** que...? | `<=` | `3 <= 2` | `False` |
| ¿Es **igual** a...? | `==` | `2 == 2` | `True` |
| ¿Es **distinto** de...? | `!=` | `5 != 5` | `False` |

(`>=` se lee "mayor o igual", y se escribe con los dos símbolos seguidos, sin espacio. `!=` se lee
"distinto de": el `!` significa "no".)
"""),

md(r"""## 3 · Comparar con variables

Lo útil, claro, es comparar **cajas** (variables), cuyo contenido cambia. Por ejemplo, la pregunta del
fin de episodio: "¿el torso está por debajo de 1 metro?". Guardamos una altura y preguntamos:
"""),

code(r"""altura_torso = 0.8
print(altura_torso < 1.0)"""),

md(r"""**`True`**: 0,8 es menor que 1, así que sí, el torso está por debajo de 1 metro. Si la caja tuviera
1,3, la misma pregunta respondería `False`. **La pregunta es la misma; la respuesta depende de lo que
haya en la caja en ese momento.** Esa es la clave de todo lo que viene.
"""),

md(r"""## 4 · La trampa más famosa: `=` contra `==`

Fíjate en que para preguntar "¿es igual?" se usan **dos** signos: `==`. ¿Por qué no uno? Porque el `=`
solo ya tiene otro trabajo: **guardar** (NB06).

```
   altura = 0       →  GUARDA un 0 en la caja altura          (una orden)
   altura == 0      →  PREGUNTA: ¿lo que hay en altura es 0?  (una pregunta: True o False)
```

Confundirlos es el error más típico de todos los principiantes (y de muchos que no lo son). Por
suerte, Python suele darse cuenta. Mira lo que pasa si usamos un solo `=` en una pregunta, dentro de un
`if` (que veremos en un momento):
"""),

code_err(r"""altura = 2
if altura = 0:
    print("la pelota está en el suelo")"""),

md(r"""`SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?`: "sintaxis no válida.
**¿Quizá querías decir `==`** (...) en lugar de `=`?". Python ha visto un `=` donde esperaba una
pregunta, y te sugiere la solución. (Lo de `:=` es otra cosa más avanzada; ignóralo.)

> **Regla:** un `=` **guarda**. Dos `==` **preguntan**.
"""),

md(r"""## 5 · Tu primer `if`

Ya sabemos hacer preguntas. Ahora, **actuar según la respuesta**. Se escribe con la palabra **`if`**, la
pregunta, dos puntos, y debajo, **con sangría**, lo que hay que hacer si la respuesta es `True`.
¿Te suena la forma? Es igual que la del `for` del NB07:
"""),

code(r"""altura = -0.1
if altura < 0:
    print("¡La pelota está bajo el suelo!")"""),

md(r"""Como `-0.1 < 0` es `True`, Python ha ejecutado la línea con sangría y ha salido el mensaje.

```
   if   altura < 0   :
   ──   ──────────   ─
    │        │       └── dos puntos: "a continuación, lo que hay que hacer"
    │        └────────── la pregunta (una comparación: True o False)
    └─────────────────── "si"

       print(...)        ← con sangría: se ejecuta SOLO si la pregunta es True
```

Se lee exactamente como en castellano: "**si** la altura es menor que 0, **entonces** muestra el
mensaje".
"""),

md(r"""## 6 · Cuando la respuesta es "no"

¿Y si la pregunta es falsa? Mismo código, pero la pelota está a 1,5 metros:"""),

code(r"""altura = 1.5
if altura < 0:
    print("¡La pelota está bajo el suelo!")"""),

md(r"""**No ha salido nada.** Y es justo lo correcto: `1.5 < 0` es `False`, así que Python se ha **saltado**
las líneas con sangría. Un `if` es como una puerta que solo se abre si la respuesta es sí; si es no,
pasas de largo.

Esta celda vacía es tan importante como la anterior: el **mismo** código hace cosas distintas según lo
que haya en las cajas. Por primera vez en el curso, **tu programa reacciona**.
"""),

md(r"""## 7 · Si no...: `else`

Muchas veces queremos hacer una cosa si la respuesta es sí, y **otra distinta** si es no. Para eso
existe **`else`** ("si no", "en otro caso"). Va al mismo nivel que el `if` (sin sangría), con sus dos
puntos, y debajo lo que hay que hacer cuando la pregunta es `False`:
"""),

code(r"""altura_torso = 1.3
if altura_torso < 1.0:
    print("Se ha caído: fin del episodio")
else:
    print("Sigue de pie: otro paso")"""),

md(r"""1,3 no es menor que 1, así que la pregunta es `False`: Python se salta el primer bloque y ejecuta el
del `else`. Con `if` y `else`, **siempre** se ejecuta exactamente **uno** de los dos bloques, nunca los
dos, nunca ninguno. Es una bifurcación en un camino:

```
                    ¿altura_torso < 1.0?
                      /            \
                   True            False
                    /                \
       "Se ha caído..."          "Sigue de pie..."
```
"""),

md(r"""## 8 · Más de dos caminos: `elif`

A veces hay **tres o más** situaciones. Por ejemplo, podríamos clasificar el estado de un robot según
cuánto está inclinado (en grados): poco inclinado, **estable**; bastante, **en peligro**; mucho,
**caído**. Para encadenar preguntas se usa **`elif`**, que es la abreviatura de "*else if*", "si no,
si...". (Para simplificar, solo miramos inclinaciones hacia un lado, con números positivos.)
"""),

code(r"""inclinacion = 25
if inclinacion > 30:
    print("caído")
elif inclinacion > 10:
    print("en peligro")
else:
    print("estable")"""),

md(r"""**"en peligro"**. Python va haciendo las preguntas **de arriba abajo** y se queda con la **primera**
que sea verdadera:

```
   ¿inclinacion > 30?  →  25 > 30 es False   →  sigue preguntando
   ¿inclinacion > 10?  →  25 > 10 es True    →  "en peligro", y YA NO pregunta más
   (el else solo se usa si TODAS las anteriores son False)
```

Con una inclinación de 5, la respuesta sería "estable"; con 40, "caído". Puedes poner tantos `elif`
como quieras, uno debajo de otro.
"""),

md(r"""## 9 · Juntar preguntas: `and` y `or`

A veces una sola comparación no basta. Recuerda la condición del NB04 para ganar los **+5 puntos**:
el torso tiene que estar **entre 1 y 2 metros**. Eso son **dos** preguntas a la vez: ¿es mayor que 1?
**y** ¿es menor que 2?

- **`and`** ("y"): es `True` solo si **las dos** preguntas son `True`.
- **`or`** ("o"): es `True` si **al menos una** de las dos es `True`.

Probemos con `and`:
"""),

code(r"""altura_torso = 1.3
print(altura_torso > 1.0 and altura_torso < 2.0)"""),

md(r"""**`True`**: 1,3 es mayor que 1 **y** menor que 2. Si fuera 0,8, la primera pregunta fallaría y el
resultado sería `False` (con `and`, basta que **una** falle).

| `and` (y) | | `or` (o) | |
|---|---|---|---|
| `True and True` | `True` | `True or True` | `True` |
| `True and False` | `False` | `True or False` | `True` |
| `False and False` | `False` | `False or False` | `False` |

Es igual que en castellano: "voy a la playa si hace sol **y** tengo tiempo" (necesito las dos cosas);
"me pongo el abrigo si hace frío **o** llueve" (me basta una).

(Un truco de Python: `1.0 < altura_torso < 2.0` también funciona y se lee igual que en matemáticas,
"entre 1 y 2". Es exactamente lo mismo que la versión con `and`.)
"""),

md(r"""### El +5 del humanoide, por dentro

Ahora puedes escribir el ingrediente "sigue de pie" de la recompensa del NB04 **tal y como está
programado** en el simulador del humanoide. Por dentro, el programa original hace justo esto: comprueba
si el torso está entre 1 y 2 metros y, si lo está, da 5 puntos; si no, 0. Ya conoces todas las piezas:
"""),

code(r"""altura_torso = 1.3

if altura_torso > 1.0 and altura_torso < 2.0:
    premio_de_pie = 5
else:
    premio_de_pie = 0

print("Premio por seguir de pie:", premio_de_pie)"""),

md(r"""**5**. Cambia la altura a 0,8 y saldría 0. Lo que en el NB04 era una frase ("+5 si sigue de pie"),
ahora es un programa que entiendes línea a línea. Fíjate en un detalle: dentro de un `if` puedes
**guardar** valores en cajas, no solo mostrar mensajes. Así, lo que pase después en el programa
depende de la decisión.
"""),

md(r"""## 10 · Decidir en cada vuelta: tu primera política a mano

Aquí empieza lo bueno: poner un `if` **dentro de un bucle**. Así el programa toma una decisión **en cada
paso**, según cómo esté el mundo en ese momento. Eso es, exactamente, **una política** (NB03): una regla
que mira el estado y decide qué hacer.

Vamos a programar el **termostato** del NB03. El mundo: una habitación que empieza a 18 grados. Cada
minuto:

- Si la calefacción está **encendida**, la habitación sube **0,5** grados.
- Si está **apagada**, se enfría **0,25** grados.

La política (escrita a mano): **si la temperatura es menor que 20, enciende; si no, apaga**.

Lee la celda despacio. Es un bucle (NB07) con un `if`/`else` dentro (lo de hoy), y cajas que se
actualizan con su propio valor (NB06). Casi todo son piezas que ya conoces, **combinadas**, con
**una idea pequeña nueva**: una caja también puede guardar **texto**. La caja `calefaccion` guarda
`"encendida"` o `"apagada"` (entre comillas, como en el `print` del NB05), y con `==` se puede
**comparar** si un texto es igual a otro, igual que con los números. Los textos se comparan letra a
letra: `"encendida" == "encendida"` es `True`, y `"encendida" == "Encendida"` es `False` (una
mayúscula ya los hace distintos):
"""),

code(r"""temperatura = 18.0

for minuto in range(1, 16):
    # LA POLÍTICA: mira la temperatura y decide
    if temperatura < 20:
        calefaccion = "encendida"
    else:
        calefaccion = "apagada"

    # EL MUNDO: la habitación cambia según la decisión
    if calefaccion == "encendida":
        temperatura = temperatura + 0.5
    else:
        temperatura = temperatura - 0.25

    print("minuto", minuto, "|", calefaccion, "| ahora hay", temperatura, "grados")"""),

md(r"""Fíjate en lo que pasa: al principio la calefacción está encendida y la temperatura **sube**. Al llegar a
20, la política la **apaga**, y la habitación se enfría un poco... hasta bajar de 20, y entonces la
**vuelve a encender**. La temperatura se queda **oscilando** alrededor de 20, sin que nadie la toque.

Fíjate también en cómo está organizado el programa, porque es **exactamente el bucle del NB03**:

```
   cada minuto (cada PASO):
       1. LA POLÍTICA mira el estado (la temperatura) y decide una ACCIÓN (encender/apagar)
       2. EL MUNDO (el entorno) cambia según la acción
       3. vuelta a empezar
```

Acabas de escribir un **agente** (la política del termostato) y un **entorno** (la habitación), y los has
conectado con un bucle. Es diminuto, pero es **la misma estructura** que tendrá el humanoide.

(Una curiosidad: hemos comparado **texto** con `==`: `calefaccion == "encendida"`. Las comparaciones
funcionan también con cadenas de texto. Y hemos elegido 0,5 y 0,25 a propósito: son de los pocos
decimales que el ordenador guarda **exactos** en binario, así que esta vez no hay ruido de decimales.)
"""),

md(r"""## 11 · La pelota, por fin, choca con el suelo

Ahora el simulador de la pelota. En cada pasito, después de moverla con la cadena de oro, preguntamos:
**¿está por debajo del suelo?** Si es así:

1. La **devolvemos al suelo**: altura = 0 (como hace el simulador profesional, que "saca" las piezas que
   se han metido donde no deben; NB02).
2. La hacemos **rebotar**: su velocidad cambia de **sentido**. Recuerda que en nuestro simulador la
   velocidad positiva significa "hacia abajo"; al rebotar, pasa a ser **negativa**, "hacia arriba"
   (los números negativos del NB03: "lo mismo, en sentido contrario").
3. Y como ninguna pelota real rebota con toda su fuerza, en el bote **pierde un 20 %** de su velocidad:
   la multiplicamos por **0,8**.

Usamos pasitos de 0,01 segundos durante 3 segundos (300 pasos), y solo mostramos un mensaje **cuando hay
un bote** (por eso el `print` está **dentro del `if`**):
"""),

code(r"""gravedad = 10
paso_tiempo = 0.01
altura = 2.0
velocidad = 0.0

for paso in range(1, 301):
    velocidad = velocidad + gravedad * paso_tiempo
    altura = altura - velocidad * paso_tiempo

    if altura < 0:                        # ¿ha atravesado el suelo?
        altura = 0                        # 1. devuélvela al suelo
        velocidad = -velocidad * 0.8      # 2 y 3. rebota hacia arriba, perdiendo un 20 %
        print("¡Bote! en el paso", paso, "| sale hacia arriba a", round(-velocidad, 2), "m/s")

print("Al cabo de 3 segundos, la pelota está a", round(altura, 2), "metros")"""),

md(r"""**¡La pelota rebota!** Tres botes en tres segundos, y cada uno **más flojo** que el anterior (sale a
5,04 m/s, luego a 3,97, luego a 3,15), porque en cada bote pierde un 20 % de velocidad. Y los botes
están **cada vez más juntos** en el tiempo (pasos 63, 163, 242), porque cuanto más flojo sale, antes
vuelve a caer. Es exactamente lo que hace una pelota de verdad. Si dejaras el bucle correr más tiempo,
los botes serían cada vez más pequeños, hasta que se quedara quieta en el suelo.

Lee otra vez la línea `velocidad = -velocidad * 0.8`. Primero la derecha (NB06): coge la velocidad (que
iba hacia abajo, positiva), cámbiale el signo (ahora hacia arriba) y multiplícala por 0,8 (un 20 % más
lenta). Luego guárdala en la caja. **Una línea es un rebote.**

A ese 0,8 los físicos lo llaman **coeficiente de restitución**: cuánto "devuelve" una superficie al
chocar. Una pelota de goma tiene un valor alto; una de plastilina, casi 0. En MuJoCo existen ajustes
parecidos para decidir cómo de "botones" son los pies del robot contra el suelo.
"""),

md(r"""## 12 · Parar el bucle: `break` y el fin del episodio

Última idea nueva de hoy. A veces queremos **salir de un bucle antes de tiempo**. Recuerda el NB03: un
episodio del humanoide puede terminar de **dos** formas:

- **Se cae** (el torso baja de 1 metro): el intento termina **antes de tiempo**.
- **Se acaba el tiempo** (llega a 1.000 pasos): el intento termina porque sí.

La segunda ya sabes hacerla: un `for` con `range(1, 1001)` da como mucho 1.000 vueltas. Para la primera,
existe la palabra **`break`** ("romper"): cuando Python la encuentra, **sale del bucle inmediatamente**,
aunque queden vueltas por dar.

Vamos a simular un "robot" muy tonto: su torso empieza a **1,4 metros** (la altura a la que aparece el
humanoide de verdad al empezar un episodio) y, como no hace nada por sostenerse, cae como una piedra.
Pasos de 0,015 segundos, como el humanoide:
"""),

code(r"""altura_torso = 1.4
velocidad = 0.0
paso_tiempo = 0.015

for paso in range(1, 1001):
    velocidad = velocidad + 10 * paso_tiempo
    altura_torso = altura_torso - velocidad * paso_tiempo

    if altura_torso < 1.0:
        print("Se ha caído en el paso", paso, "-> fin del episodio")
        break

print("El bucle ha terminado. Altura final del torso:", round(altura_torso, 2), "metros")"""),

md(r"""El bucle **podía** dar 1.000 vueltas, pero en la 19.ª el torso bajó de 1 metro, el `if` se cumplió y el
`break` **cortó el bucle en seco**. Después, el programa siguió con lo que hay **después** del bucle (el
último `print`).

```
   for paso in range(1, 1001):      ← como mucho 1.000 vueltas (fin por TIEMPO)
       ...física...
       if altura_torso < 1.0:       ← ¿se ha caído?
           break                    ← fin ANTES de tiempo (fin por CAÍDA)
   ...lo de después del bucle...    ← aquí se sigue en cualquiera de los dos casos
```

Esta estructura, un `for` con un `if` y un `break` dentro, es **exactamente** cómo funciona un episodio en
los simuladores de verdad. Los profesionales tienen incluso dos palabras para los dos finales:
**terminado** (*terminated*: ha pasado algo que acaba el intento, como caerse) y **truncado**
(*truncated*: se ha cortado porque se acabó el tiempo). Las verás muchísimo.

(19 pasos de 0,015 segundos son menos de 0,3 segundos: un torso que no se sostiene llega al suelo muy
rápido. Recuerda que el robot al azar del NB00 aguantaba un tercio de segundo... no mucho más que esta
piedra.)
"""),

md(r"""## 13 · Resumen de la lección

1. Las **comparaciones** (`<`, `>`, `<=`, `>=`, `==`, `!=`) son preguntas de sí o no; responden **`True`**
   o **`False`** (los **booleanos**). **`=` guarda; `==` pregunta.**
2. **`if pregunta:`** ejecuta el bloque con sangría **solo si** la respuesta es `True`. **`else:`** da el
   camino alternativo; **`elif`** encadena más preguntas (gana la **primera** verdadera).
3. **`and`** exige que se cumplan las dos preguntas; **`or`**, al menos una. El +5 del humanoide es un `if`
   con `and`: torso entre 1 y 2 metros.
4. Un `if` **dentro de un bucle** decide en cada paso: eso es una **política**. El termostato (política) y
   la habitación (entorno), unidos por un bucle, son el bucle agente-entorno del NB03 en miniatura.
5. Con un `if`, la pelota **choca y rebota** (cambiar el signo de la velocidad y perder un 20 %). **`break`**
   sale de un bucle antes de tiempo: un episodio acaba **terminado** (se cae) o **truncado** (se acaba el
   tiempo).

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Comparación** | Una pregunta de sí o no entre dos valores: `3 > 2`. |
| **Booleano (`bool`)** | El tipo de los valores `True` (verdadero) y `False` (falso). |
| **`==` / `!=`** | ¿Es igual? / ¿Es distinto? |
| **`if`** | "Si": ejecuta un bloque solo si la pregunta es `True`. |
| **`else`** | "Si no": el bloque que se ejecuta cuando la pregunta es `False`. |
| **`elif`** | "Si no, si...": encadena otra pregunta. |
| **`and` / `or`** | "Y" (las dos) / "o" (al menos una). |
| **Coeficiente de restitución** | Cuánta velocidad conserva algo al rebotar (0,8 = conserva el 80 %). |
| **`break`** | Sale de un bucle inmediatamente. |
| **Terminado / truncado** | Episodio que acaba porque pasa algo (caerse) / porque se acaba el tiempo. |
"""),

md(r"""## 14 · Ejercicios

**E1.** Predice qué responde cada una: `print(5 >= 5)`, `print(2 != 3)`, `print(1.5 < 1.0)`,
`print(7 == 7.0)`.

**E2.** Escribe un programa que, dada una caja `velocidad`, muestre "avanza" si es mayor que 0, "retrocede"
si es menor que 0 y "quieto" si es exactamente 0. Pruébalo con `velocidad = -0.5`.

**E3.** Predice qué muestra este programa:

```python
x = 15
if x > 20:
    print("A")
elif x > 10:
    print("B")
elif x > 5:
    print("C")
else:
    print("D")
```

**E4.** Predice si estas preguntas dan `True` o `False`, con `altura = 2.5`:
`altura > 1.0 and altura < 2.0`, `altura > 1.0 or altura < 2.0`.

**E5.** Modifica el termostato para que **cuente** cuántos minutos, de los 15, ha estado la calefacción
encendida. Pista: un acumulador (NB07) que suma 1 dentro del `if`.

**E6.** En la pelota que rebota, ¿qué cambiarías para que fuera una pelota de **plastilina**, que casi no
rebota? ¿Y una **superpelota**, que rebota muchísimo?

**E7.** Escribe la recompensa **completa** de un paso del humanoide, con el `if` del premio por seguir de
pie: `altura_torso = 1.2`, `velocidad = 1.0`, `esfuerzo = 0.5`. (Fórmula del NB04: premio de pie +
1,25 × velocidad − 0,1 × esfuerzo.) ¿Y si `altura_torso = 0.9`?

**E8.** ¿Qué pasaría en el programa del episodio (apartado 12) si quitáramos la línea `break`?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

- `5 >= 5` → **`True`** (5 es igual a 5, y "mayor **o igual**" lo incluye).
- `2 != 3` → **`True`** (2 es distinto de 3).
- `1.5 < 1.0` → **`False`**.
- `7 == 7.0` → **`True`** (valen lo mismo, aunque uno sea entero y otro decimal).
</details>

<details>
<summary>▶ Solución E2</summary>

```python
velocidad = -0.5
if velocidad > 0:
    print("avanza")
elif velocidad < 0:
    print("retrocede")
else:
    print("quieto")
```

Con `-0.5` muestra **"retrocede"**. Si no es mayor que 0 ni menor que 0, solo puede ser 0: por eso el caso
"quieto" va en el `else`.
</details>

<details>
<summary>▶ Solución E3</summary>

Muestra **"B"**. Python pregunta de arriba abajo: `15 > 20` es `False`; `15 > 10` es `True` → muestra "B"
y **no pregunta más** (aunque `15 > 5` también sería `True`, ya no llega a mirarlo).
</details>

<details>
<summary>▶ Solución E4</summary>

- `altura > 1.0 and altura < 2.0` → **`False`**: 2,5 es mayor que 1 (`True`) pero no es menor que 2
  (`False`), y con `and` basta una falsa. (El robot estaría "demasiado alto": no gana el +5.)
- `altura > 1.0 or altura < 2.0` → **`True`**: con `or` basta una verdadera, y la primera lo es.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
temperatura = 18.0
minutos_encendida = 0

for minuto in range(1, 16):
    if temperatura < 20:
        calefaccion = "encendida"
        minutos_encendida = minutos_encendida + 1
    else:
        calefaccion = "apagada"

    if calefaccion == "encendida":
        temperatura = temperatura + 0.5
    else:
        temperatura = temperatura - 0.25

print("La calefacción estuvo encendida", minutos_encendida, "minutos de 15")
```

La hucha (`minutos_encendida = 0`) va **antes** del bucle, y la suma **dentro del `if`**, para que solo
cuente los minutos en que se encendió. Si lo ejecutas, verás que sale **8**.
</details>

<details>
<summary>▶ Solución E6</summary>

Cambiaría el **0,8** de la línea del rebote (el coeficiente de restitución):

- **Plastilina**: un número muy pequeño, por ejemplo `0.1` (solo conserva el 10 % de la velocidad: apenas
  se levanta del suelo).
- **Superpelota**: un número cercano a 1, por ejemplo `0.95` (conserva el 95 %: rebota casi a la misma
  altura una y otra vez).

(Con un número **mayor que 1**, la pelota ganaría velocidad en cada bote, ¡cosa que ninguna pelota real
hace! Sería un "fallo de física" que un agente tramposo, como los del NB04, aprovecharía encantado.)
</details>

<details>
<summary>▶ Solución E7</summary>

```python
altura_torso = 1.2
velocidad = 1.0
esfuerzo = 0.5

if altura_torso > 1.0 and altura_torso < 2.0:
    premio_de_pie = 5
else:
    premio_de_pie = 0

recompensa = premio_de_pie + 1.25 * velocidad - 0.1 * esfuerzo
print(recompensa)
```

Con `altura_torso = 1.2` sale **6.2** (5 + 1,25 − 0,05). Con `altura_torso = 0.9`, el `if` da `False`, el
premio de pie es 0, y sale **1.2** (0 + 1,25 − 0,05). Además, en el simulador de verdad ese episodio
terminaría ahí.
</details>

<details>
<summary>▶ Solución E8</summary>

Sin `break`, el bucle **no se detendría** al caer: el mensaje "Se ha caído..." saldría en el paso 19... ¡y
en el 20, y en el 21, y en todos los siguientes hasta el 1.000!, porque el torso seguiría por debajo de 1
metro (de hecho, seguiría cayendo sin fin, porque este simulador no tiene suelo). El episodio solo
terminaría por **tiempo**, nunca por caída. Por eso el `break` es imprescindible.
</details>
"""),

md(r"""## 15 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Ya tienes las **cuatro grandes piezas** de la programación: orden, memoria, repetición y decisión. Con
solo eso se puede escribir, en teoría, **cualquier** programa que exista. Lo que viene a partir de ahora
son herramientas para escribirlos **más cómodamente**.

La primera, en el **NB09**, son las **listas**: cajas que guardan **muchos valores a la vez**, en orden.
Las necesitamos ya, porque la observación del humanoide son **45 números** y su acción **17**: no vamos a
crear 17 cajas sueltas con nombres como `motor_1`, `motor_2`... Con una lista, los 17 motores irán en una
sola caja, y un bucle los recorrerá todos.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB08_decisiones_if.ipynb")
    build(out, cells, title="NB08 · Tomar decisiones: if")
