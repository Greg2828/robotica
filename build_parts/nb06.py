"""Construye NB06 · Cajas con nombre: variables y números (Parte 1 · Lección 2).

Microdosis: una idea nueva por celda. Variables como cajas con etiqueta, el =
como "guarda", reescribir, memoria del cuaderno (orden de ejecución), NameError
explicado, reglas de nombres, enteros y decimales, operaciones (+ - * / **), el
"ruido" de los decimales y round(), orden de operaciones y paréntesis, la trampa
de -0.4 ** 2, actualizar una caja con su propio valor, y dos programas de robot:
la recompensa del NB04 con nombres y los primeros pasitos de la pelota del NB02.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB06 · Cajas con nombre: variables y números

**Parte 1 · Primeros pasos con el ordenador — Lección 2**

> En el **NB05** escribiste tus primeras líneas: `print`, texto entre comillas, números sin
> comillas, tus primeros errores y la recompensa de un paso calculada por el ordenador. Pero
> aquel cálculo, `5 + 1.25 * 2 - 0.1 * 1`, tenía un problema: **era una ristra de números
> sueltos**. Hoy vamos a arreglarlo con la herramienta más usada de toda la programación.

La herramienta se llama **variable**, y la idea es sencillísima: **una caja con un nombre donde el
ordenador guarda un valor para recordarlo**. Con ella, el ordenador deja de ser una calculadora que
olvida todo al instante y pasa a tener **memoria**.

Al final de hoy sabrás crear cajas, mirar lo que hay dentro, cambiarlo, y hacer todas las
operaciones de números que necesitaremos durante mucho tiempo. Y lo usaremos para escribir dos
programas de robot de verdad: la **recompensa** de un paso del humanoide, y los primeros **pasitos de
la pelota** del simulador del NB02.

Como siempre: una idea nueva por celda, y antes de cada celda te digo qué va a pasar.
"""),

md(r"""## 1 · El problema de los números sueltos

Mira otra vez la recompensa del NB05:

```
   print(5 + 1.25 * 2 - 0.1 * 1)
```

Ahora imagina que la ves dentro de un mes, sin recordar nada. ¿Qué es ese 5? ¿Y el 2? ¿El 1 del
final? Es imposible saberlo. Son **números mágicos**: números que funcionan, pero que nadie sabe de
dónde salen.

Y hay un segundo problema. Si el robot ahora va a **3** metros por segundo en vez de 2, tienes que
averiguar cuál de todos esos números es la velocidad, y cambiarlo con cuidado de no tocar otro. Con
una cuenta así ya es fácil equivocarse; con un programa de mil líneas, es casi imposible no
equivocarse.

Lo que queremos es poder escribir algo como:

```
   recompensa = premio_de_pie + peso_avance * velocidad - peso_esfuerzo * esfuerzo
```

donde **cada número tiene un nombre** que dice qué es. Eso es exactamente lo que vamos a aprender.
"""),

md(r"""## 2 · La idea: una caja con una etiqueta

Imagina una **caja** de cartón con una **etiqueta** pegada. En la etiqueta escribes un nombre, por
ejemplo `velocidad`. Dentro de la caja metes un valor, por ejemplo el número `2`.

```
          etiqueta
       ┌───────────┐
       │ velocidad │
       └─────┬─────┘
         ┌───┴───┐
         │       │
         │   2   │   ← lo que hay dentro
         │       │
         └───────┘
```

Desde ese momento, cada vez que digas **"velocidad"**, el ordenador irá a la caja con esa etiqueta y
usará lo que hay dentro: el 2. Eso es una **variable**: un **nombre** que guarda un **valor**. Se
llama "variable" porque lo que hay dentro puede **variar**: puedes sacar el 2 y meter un 3 cuando
quieras.

La memoria del ordenador es, a efectos prácticos, un **almacén enorme** lleno de estas cajas.
"""),

md(r"""## 3 · Crear tu primera caja

Para crear una caja y meter algo dentro se escribe: **el nombre, un signo `=`, y el valor**. Esta
celda crea una caja llamada `velocidad` y guarda dentro el número 2:
"""),

code(r"""velocidad = 2"""),

md(r"""¿No ha salido nada debajo? **Es lo normal.** No le hemos pedido que **muestre** nada (no hay
`print`); solo le hemos pedido que **guarde** algo. El ordenador lo ha guardado en silencio, como
quien mete algo en un cajón sin decir nada.

Pero la caja **existe**, y el 2 está dentro. Vamos a comprobarlo.
"""),

md(r"""## 4 · Mirar dentro de la caja

Para ver lo que hay dentro, se usa `print` con el **nombre de la caja, sin comillas**:"""),

code(r"""print(velocidad)"""),

md(r"""¡**2**! Python ha visto el nombre `velocidad`, ha buscado la caja con esa etiqueta y ha mostrado lo
que había dentro.

¿Y si le ponemos comillas? Recuerda el NB05: **con comillas es texto que se copia tal cual**.
"""),

code(r"""print("velocidad")"""),

md(r"""Con comillas, Python no busca ninguna caja: copia la palabra *velocidad*, letra a letra.

```
   print(velocidad)     →  2            (sin comillas: busca la caja y muestra su contenido)
   print("velocidad")   →  velocidad    (con comillas: copia el texto tal cual)
```

### Por fin entendemos el primer error del NB05

¿Recuerdas `print(hola)` y su mensaje `NameError: name 'hola' is not defined`? Ahora tiene todo el
sentido: sin comillas, Python pensó que `hola` era **el nombre de una caja**, la buscó en su almacén...
y no había ninguna caja con esa etiqueta. "El nombre `hola` no está definido" significa exactamente:
**"no tengo ninguna caja que se llame así"**.
"""),

md(r"""## 5 · Usar la caja en una cuenta

Una caja se puede usar en cualquier cuenta, en lugar del número que contiene. Por ejemplo, el premio
por avanzar del NB04 era 1,25 × velocidad:
"""),

code(r"""print(1.25 * velocidad)"""),

md(r"""**2.5**. Python ha sustituido `velocidad` por lo que hay dentro (el 2) y ha calculado 1,25 × 2 =
2,5. Fíjate en que la caja **no ha cambiado**: sigue teniendo un 2. Mirar o usar el contenido de una
caja no lo gasta ni lo modifica, igual que leer un libro no lo borra.
"""),

md(r"""## 6 · El signo `=` NO significa "igual"

Esto confunde a casi todo el mundo al principio, así que vamos con calma.

En matemáticas, `=` significa "es igual a": `2 + 2 = 4` afirma que las dos cosas valen lo mismo. En
Python, **`=` significa otra cosa**: significa **"guarda"**. Es una **orden**, no una afirmación.

```
   velocidad = 2

   se lee:  "guarda el 2 en la caja velocidad"
   NO se lee: "velocidad es igual a 2"

   mejor imagínalo como una flecha que va de derecha a izquierda:

   velocidad  ◄────  2
   (la caja)        (el valor que entra en ella)
```

A esta operación de guardar se le llama **asignar** ("le asignamos el valor 2 a la variable
`velocidad`"), y al `=` se le llama **operador de asignación**. Grábate la flecha: lo que está a la
**derecha** del `=` se mete en la caja de la **izquierda**.
"""),

md(r"""## 7 · Cambiar lo que hay dentro

Si guardas un valor nuevo en una caja que ya existe, **el valor antiguo desaparece** y su sitio lo
ocupa el nuevo. Una caja solo guarda **una cosa a la vez**. Esta celda guarda un 3 en `velocidad` y
luego lo muestra:
"""),

code(r"""velocidad = 3
print(velocidad)"""),

md(r"""**3**. El 2 que había antes se ha ido para siempre; ahora la caja contiene un 3. Por eso se llaman
*variables*: su contenido varía.

```
   antes:   velocidad │ 2 │
   velocidad = 3
   después: velocidad │ 3 │     (el 2 se ha tirado)
```
"""),

md(r"""## 8 · La memoria del cuaderno (y por qué importa el orden)

Una cosa importante sobre los cuadernos. Las cajas que creas en una celda **siguen existiendo** en
las celdas de más abajo: la celda del apartado 5 pudo usar `velocidad` aunque la creamos en el
apartado 3. Todas las celdas comparten **el mismo almacén**, el del *kernel* (el motor de Python del
NB05).

Esto tiene dos consecuencias prácticas, si ejecutas el cuaderno tú:

1. **Hay que ejecutar las celdas en orden.** Si te saltas la celda que crea una caja y ejecutas una
   que la usa, Python no la encontrará.
2. **Si reinicias el kernel** (Kernel → Restart), el almacén **se vacía**: todas las cajas
   desaparecen. Tendrás que volver a ejecutar las celdas desde arriba.

Vamos a ver qué pasa si usamos una caja que **nunca** hemos creado, por ejemplo `altura`:
"""),

code_err(r"""print(altura)"""),

md(r"""El viejo conocido: `NameError: name 'altura' is not defined`. "No tengo ninguna caja llamada
`altura`". Ahora ya sabes leerlo a la primera: **o la caja no se ha creado, o has escrito mal su
nombre, o te has saltado la celda que la creaba.**
"""),

md(r"""## 9 · Cómo se pueden llamar las cajas

Los nombres de las variables tienen unas reglas. Pocas y fáciles:

| Regla | Bien | Mal |
|---|---|---|
| Solo letras, números y guion bajo `_` | `masa_torso` | `masa-torso` |
| No pueden **empezar** por un número | `motor1` | `1motor` |
| **Sin espacios** (se usa `_` en su lugar) | `velocidad_maxima` | `velocidad maxima` |
| Mayúsculas y minúsculas **cuentan** | `altura` y `Altura` son **dos cajas distintas** | |

Y un consejo, que no es regla pero casi: **evita las tildes y la ñ** en los nombres (`anio` en vez de
`año`). Python las acepta, pero mucho otro software no, y te dará problemas más adelante. (En el
**texto entre comillas** sí puedes usarlas siempre.)

Veamos qué pasa si rompemos una regla, por ejemplo empezando por un número:
"""),

code_err(r"""2velocidad = 5"""),

md(r"""`SyntaxError: invalid decimal literal`: "número decimal no válido". Python ve un `2` al principio y
cree que vas a escribir un número... pero luego vienen letras, y se lía. La regla es justo para
evitar esa confusión.

**Un buen nombre dice qué hay dentro.** Compara:

```
   v = 2                              ← ¿v de qué? ¿velocidad? ¿voltaje? ¿vida?
   velocidad_hacia_delante = 2        ← imposible confundirse
```

Escribir nombres claros es una de las costumbres que más distinguen a un buen programador. Un nombre
un poco largo pero claro es **mucho** mejor que uno corto y misterioso.
"""),

md(r"""## 10 · Dos tipos de números: enteros y decimales

Python distingue dos tipos de números:

- **Enteros**: sin parte decimal, como `2`, `17`, `-3` o `1000`. En inglés, *integer*, y Python los
  llama **`int`**.
- **Decimales**: con punto decimal, como `1.25`, `0.4` o `9.8`. Python los llama **`float`** (de
  *floating point*, "coma flotante", el nombre técnico de cómo los guarda el ordenador).

La mayoría de las veces no tienes que preocuparte: Python los mezcla sin problema. Pero hay un detalle
que verás constantemente. Mira esta división:
"""),

code(r"""print(7 / 2)"""),

md(r"""**3.5**, lo esperado: 7 entre 2 es 3,5. Ahora una división **exacta**:"""),

code(r"""print(6 / 2)"""),

md(r"""**3.0**, no `3`. ¿Por qué ese `.0`? Porque en Python **dividir con `/` siempre da un decimal**,
aunque la división sea exacta. `3.0` y `3` valen lo mismo; solo cambia el tipo de número. Cuando veas
un `.0` al final, ahora sabes de dónde sale.
"""),

md(r"""## 11 · Las operaciones con números

Estas son las operaciones básicas en Python. Ya conoces casi todas:

| Operación | En matemáticas | En Python | Ejemplo | Resultado |
|---|---|---|---|---|
| Sumar | 2 + 3 | `2 + 3` | `print(2 + 3)` | `5` |
| Restar | 5 − 2 | `5 - 2` | `print(5 - 2)` | `3` |
| Multiplicar | 4 × 3 | `4 * 3` | `print(4 * 3)` | `12` |
| Dividir | 7 ÷ 2 | `7 / 2` | `print(7 / 2)` | `3.5` |
| Elevar (potencia) | 3² | `3 ** 2` | `print(3 ** 2)` | `9` |

La única nueva es la última: **dos asteriscos `**`** significan "**elevado a**". `3 ** 2` es "3 elevado
a 2", es decir, **3 al cuadrado**, la operación que aprendiste en el NB04 para medir el esfuerzo de los
motores. Comprobémoslo:
"""),

code(r"""print(3 ** 2)"""),

md(r"""**9**, porque 3 × 3 = 9. Ahora el cuadrado de una acción de motor a tope, **0,4**, que en el NB04
calculamos a mano y daba **0,16**. A ver qué dice Python:
"""),

code(r"""print(0.4 ** 2)"""),

md(r"""¿¿**0.16000000000000003**?? ¡Debería ser 0,16! ¿Se ha equivocado el ordenador?

## 12 · El "ruido" de los decimales

No es un error tuyo ni un fallo del ordenador: es una **limitación de cómo guardan los ordenadores
los decimales**, y la vas a ver toda tu vida, así que merece la pena entenderla.

Piensa en cómo escribirías **un tercio** (1 ÷ 3) con decimales: 0,3333333... y los treses no se acaban
nunca. Si solo tienes espacio para, digamos, 10 cifras, tienes que cortar: 0,3333333333. Y ese número
**no es exactamente** un tercio: le falta un poquito. Si sumas tres de ellos, te sale 0,9999999999,
no 1.

Al ordenador le pasa lo mismo, pero con **otros** números. Por dentro guarda todo con ceros y unos (el
sistema **binario**), y en binario hay números que nosotros escribimos fácil, como **0,4** o **0,1**,
que **no tienen un final**, igual que un tercio en nuestro sistema. El ordenador tiene que cortarlos,
y queda un error **minúsculo**: en este caso, 3 diezmilbillonésimas (el `3` del final, en el decimal
número 17).

Para un robot, un error así es **completamente despreciable**: ningún motor del mundo nota la
diferencia entre 0,16 y 0,16000000000000003. Pero queda feo al mostrarlo. Para eso existe la orden
**`round`** ("redondear"), que redondea un número a los decimales que le digas:
"""),

code(r"""print(round(0.4 ** 2, 2))"""),

md(r"""**0.16**. `round` recibe **dos** cosas, separadas por una coma: **el número** a redondear y
**cuántos decimales** quieres conservar (aquí, 2).

```
   round( 0.4 ** 2 ,  2 )
          ────────    ─
          el número   cuántos decimales
```

> **Regla práctica:** si ves un número con una ristra de ceros o nueves y un dígito suelto al final
> (`0.16000000000000003`, `0.9999999999999999`), no te asustes: es ruido de los decimales. Si te
> molesta al mostrarlo, usa `round`.
"""),

md(r"""## 13 · ¿Qué se calcula primero? El orden de las operaciones

Cuando una cuenta tiene varias operaciones, Python sigue **las mismas reglas que en matemáticas**:

```
   1.º  lo que está entre PARÉNTESIS
   2.º  las POTENCIAS (**)
   3.º  las MULTIPLICACIONES y DIVISIONES (* y /)
   4.º  las SUMAS y RESTAS (+ y -)
   (y, a igualdad, de izquierda a derecha)
```

Mira esta cuenta. ¿Qué sale: 20 o 14?
"""),

code(r"""print(2 + 3 * 4)"""),

md(r"""**14**: primero la multiplicación (3 × 4 = 12) y luego la suma (2 + 12 = 14). Si quieres que se
sume primero, usa **paréntesis**:
"""),

code(r"""print((2 + 3) * 4)"""),

md(r"""**20**: ahora primero el paréntesis (2 + 3 = 5) y luego la multiplicación (5 × 4 = 20).

Por eso la recompensa del NB05, `5 + 1.25 * 2 - 0.1 * 1`, salía bien sin paréntesis: las
multiplicaciones se hacían primero, solas.

> **Consejo:** si dudas de qué se hace antes, **pon paréntesis**. Nunca sobran, y hacen la cuenta más
> fácil de leer.
"""),

md(r"""### Una trampa con los negativos y las potencias

Esta trampa es famosa, y te la encontrarás. En el NB04 vimos que **(−0,4)² = 0,16**: el cuadrado se
come el signo. Pero mira lo que pasa si lo escribimos **sin paréntesis**:
"""),

code(r"""print(-0.4 ** 2)"""),

md(r"""¡Sale **negativo**! (Con su ruido de decimales.) ¿Por qué? Por el orden de las operaciones: las
**potencias van antes** que el signo menos. Así que Python ha entendido `-(0.4 ** 2)`: primero eleva
0,4 al cuadrado (0,16) y **después** le pone el menos (−0,16).

Para elevar al cuadrado el número negativo entero, hay que **envolverlo en paréntesis**:
"""),

code(r"""print((-0.4) ** 2)"""),

md(r"""Ahora sí, **positivo** (0,16 con su ruido). La buena noticia: cuando el número negativo está
**dentro de una caja**, no hay trampa, porque Python saca primero el valor de la caja entero, con su
signo. Lo veremos enseguida, en el programa del esfuerzo.
"""),

md(r"""## 14 · Una caja que se actualiza con su propio valor

Esta es la última idea nueva de hoy, y es **importantísima**: la vamos a usar en la próxima lección
para construir un simulador.

Primero, una caja normal. Creamos `velocidad` con un 0 dentro:
"""),

code(r"""velocidad = 0
print(velocidad)"""),

md(r"""Ahora una línea que parece absurda en matemáticas, pero que en Python tiene todo el sentido:"""),

code(r"""velocidad = velocidad + 1
print(velocidad)"""),

md(r"""**1**. En matemáticas, "velocidad = velocidad + 1" sería imposible (ningún número es igual a sí
mismo más uno). Pero recuerda: **en Python `=` no es "igual", es "guarda"**. Y Python lo hace en dos
tiempos, **primero la derecha, luego la izquierda**:

```
   velocidad = velocidad + 1

   1.º  calcula la DERECHA:  mira qué hay en la caja (0), súmale 1  →  1
   2.º  guarda el resultado en la caja de la IZQUIERDA               →  velocidad │ 1 │
```

Es decir: "**coge lo que hay en la caja, súmale 1, y vuelve a guardarlo en la misma caja**".

Si estás ejecutando el cuaderno, **ejecuta esa celda otra vez** (Mayúsculas + Enter encima de ella):
verás un **2**. Y otra vez: **3**. Cada vez que la ejecutas, la caja crece en 1. Es como un
**contador** de personas a la entrada de un concierto: cada vez que entra alguien, *clic*, uno más.

¿Te suena de algo "sumar 1 a la velocidad en cada paso"? Es **exactamente** lo que hacíamos con la
pelota del NB02: en cada pasito, *velocidad nueva = velocidad + 1*. Vamos a ello.
"""),

md(r"""## 15 · Programa 1: la recompensa del humanoide, con nombres

Ya tienes todo lo necesario para reescribir la recompensa del NB04 como un **programa de verdad**,
legible. No hay ninguna idea nueva en esta celda: solo cajas, operaciones y `print`, que ya conoces.
Léela línea a línea, con los comentarios:
"""),

code(r"""# Los "pesos" de la recompensa: los eligió el diseñador (NB04)
premio_de_pie = 5
peso_avance = 1.25
peso_esfuerzo = 0.1

# Lo que ha pasado en este paso
velocidad = 2       # metros por segundo hacia delante
esfuerzo = 1        # suma de las acciones al cuadrado

# La fórmula, que ahora se lee como una frase
recompensa = premio_de_pie + peso_avance * velocidad - peso_esfuerzo * esfuerzo

print("Recompensa del paso:", recompensa)"""),

md(r"""**7.4**, igual que en el NB04 y en el NB05. Pero compara las dos versiones:

```
   antes:   print(5 + 1.25 * 2 - 0.1 * 1)
   ahora:   recompensa = premio_de_pie + peso_avance * velocidad - peso_esfuerzo * esfuerzo
```

La segunda se lee como una frase. Dentro de un año la entenderás a la primera. (Y fíjate en la coma
del `print`, del NB05: muestra el texto **y además** el contenido de la caja, en la misma línea.)

Ahora la ventaja de verdad. Si el robot está **quieto** (velocidad 0), solo cambiamos **una** caja y
recalculamos:
"""),

code(r"""velocidad = 0
recompensa = premio_de_pie + peso_avance * velocidad - peso_esfuerzo * esfuerzo
print("Recompensa del paso:", recompensa)"""),

md(r"""**4.9**: sin avanzar, el robot pierde el premio por avance (2,5 puntos). Solo hemos tocado una caja,
sin miedo a romper nada más.

Y piensa en lo que esto significa para un **diseñador de recompensas** (NB04): esos tres números de
arriba, `premio_de_pie`, `peso_avance` y `peso_esfuerzo`, son literalmente **sus mandos**. Si el robot
se queda quieto porque estar de pie da demasiados puntos, el ingeniero cambia `premio_de_pie = 5` por
otro valor y vuelve a entrenar. Así de concreto es el trabajo.
"""),

md(r"""### El esfuerzo de los motores, calculado

Calculemos también el **esfuerzo** de un paso, como en el NB04: cada acción al cuadrado, y todo sumado.
Para no alargarlo, con solo 3 motores (el humanoide tiene 17, pero la idea es la misma). Fíjate en que
`motor_2` es **negativo** y, como está dentro de una caja, `motor_2 ** 2` sale **positivo** sin
necesidad de paréntesis:
"""),

code(r"""motor_1 = 0.4
motor_2 = -0.4
motor_3 = 0.1

esfuerzo = motor_1 ** 2 + motor_2 ** 2 + motor_3 ** 2

print("Esfuerzo:", esfuerzo)
print("Esfuerzo redondeado:", round(esfuerzo, 2))"""),

md(r"""El esfuerzo es **0,33** (con su ruido de decimales en la primera línea, y limpio en la segunda gracias
a `round`). Comprobémoslo a mano: 0,4² = 0,16; (−0,4)² = 0,16; 0,1² = 0,01. Suma: 0,16 + 0,16 + 0,01 =
**0,33**. Perfecto.
"""),

md(r"""## 16 · Programa 2: los primeros pasitos de la pelota

Y ahora, lo más emocionante de la lección. En el NB02 calculaste a mano, en una tabla, cómo cae una
pelota soltada desde 2 metros: en cada pasito de 0,1 segundos, **la gravedad cambia la velocidad** y
**la velocidad cambia la altura**. Era la "cadena de oro", lo que hace un simulador por dentro.

Vamos a programarlo. Primero, el **estado inicial** del mundo, en cajas. Reutilizamos el nombre
`velocidad`: lo que tuviera dentro se sustituye (apartado 7):
"""),

code(r"""# El mundo
gravedad = 10           # la pelota gana 10 m/s cada segundo
paso_tiempo = 0.1       # cada pasito dura una décima de segundo

# El estado inicial de la pelota
altura = 2.0            # metros
velocidad = 0.0         # metros por segundo (hacia abajo), empieza quieta

print("Inicio:", velocidad, altura)"""),

md(r"""Ahora, **un pasito** de simulación. Son las dos líneas de la cadena de oro, usando la idea del
apartado 14 (una caja que se actualiza con su propio valor):

- **Fuerza → velocidad:** la velocidad nueva es la de antes, más lo que la gravedad añade en este
  pasito (10 × 0,1 = 1).
- **Velocidad → posición:** la altura nueva es la de antes, menos lo que baja en este pasito
  (velocidad × 0,1).
"""),

code(r"""velocidad = velocidad + gravedad * paso_tiempo
altura = altura - velocidad * paso_tiempo
print("Tras un pasito:", velocidad, altura)"""),

md(r"""**Velocidad 1.0, altura 1.9**: exactamente la fila 1 de la tabla que hiciste a mano en el NB02.
(Los números salen como `1.0` y `1.9`, con punto, porque son decimales: empezamos con `0.0` y `2.0`.)

Para dar el **segundo** pasito, hay que hacer exactamente lo mismo otra vez. Así que copiamos la celda:
"""),

code(r"""velocidad = velocidad + gravedad * paso_tiempo
altura = altura - velocidad * paso_tiempo
print("Tras otro pasito:", velocidad, altura)"""),

md(r"""**2.0 y 1.7**: la fila 2 de la tabla. Y otro más:"""),

code(r"""velocidad = velocidad + gravedad * paso_tiempo
altura = altura - velocidad * paso_tiempo
print("Tras otro pasito:", velocidad, altura)"""),

md(r"""**3.0 y 1.4**: la fila 3. **Acabas de programar un simulador de física.** Diminuto, de una sola
pelota y sin suelo, pero es **la misma idea** que hay dentro de MuJoCo, el simulador profesional que
moverá a nuestro humanoide.

Pero mira lo que hemos tenido que hacer: **copiar la misma celda** una y otra vez. Para tres pasitos,
vale. ¿Y para los **333 pasitos** de un solo segundo de simulación? ¿Y para el millón de pasos de un
entrenamiento? Copiar sería una locura.

Los ordenadores son buenísimos en justo eso: **repetir lo mismo muchas veces sin cansarse**. Para
pedírselo hay una herramienta especial, y es el tema del próximo notebook.
"""),

md(r"""## 17 · Resumen de la lección

1. Una **variable** es una **caja con nombre** que guarda un valor: `velocidad = 2`. Se mira con
   `print(velocidad)` (**sin comillas**). Usar la caja no la gasta.
2. En Python, **`=` significa "guarda"** (asignar), no "igual": lo de la **derecha** entra en la caja
   de la **izquierda**. Guardar otra vez **sustituye** el valor anterior.
3. Las cajas viven en la **memoria del kernel**: hay que ejecutar las celdas **en orden**, y reiniciar
   lo borra todo. `NameError` = "no tengo ninguna caja con ese nombre".
4. Números **enteros** (`int`) y **decimales** (`float`); `/` siempre da decimal. Operaciones: `+ - * /`
   y `**` (potencia). Orden: **paréntesis, potencias, multiplicar/dividir, sumar/restar**. Cuidado con
   `-0.4 ** 2`. Los decimales traen un **ruido** minúsculo; se limpia con **`round`**.
5. **`x = x + 1`** significa "coge lo que hay en la caja, súmale 1 y guárdalo otra vez". Con eso
   programamos la **recompensa** del humanoide y los primeros **pasitos de la pelota**.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Variable** | Una caja con nombre que guarda un valor. |
| **Asignar** | Guardar un valor en una variable con `=`. |
| **Operador de asignación** | El signo `=` de Python: "guarda". |
| **Número mágico** | Un número suelto en el código que nadie sabe qué significa. |
| **Entero (`int`)** | Número sin parte decimal: `2`, `17`, `-3`. |
| **Decimal (`float`)** | Número con punto decimal: `1.25`, `0.4`, `3.0`. |
| **Potencia (`**`)** | "Elevado a": `3 ** 2` es 3 al cuadrado (9). |
| **`round`** | Redondea un número: `round(número, decimales)`. |
| **Binario** | El sistema de ceros y unos con el que el ordenador guarda todo. |
| **Estado inicial** | Los valores con los que empieza una simulación. |
"""),

md(r"""## 18 · Ejercicios

Si estás ejecutando el cuaderno, crea una celda nueva para cada uno (**Esc** y luego **B**). Si estás
leyendo, escríbelo en un papel y compara con la solución.

**E1.** Crea una variable `masa_torso` con el valor 8,91 (la masa del torso del humanoide, en kilos) y
muéstrala.

**E2.** Sin ejecutarlo, ¿qué mostrará este programa?

```python
x = 5
x = x * 2
x = x - 3
print(x)
```

**E3.** ¿Cuáles de estos nombres de variable son **válidos** en Python? `altura_torso`, `3motores`,
`motor_3`, `velocidad maxima`, `Velocidad`.

**E4.** Sin ejecutarlo, calcula qué sale en `print(10 - 2 * 3)` y en `print((10 - 2) * 3)`.

**E5.** Usando las cajas de la recompensa del apartado 15 (`premio_de_pie`, `peso_avance`,
`peso_esfuerzo`), calcula la recompensa de un paso con velocidad **1,5** y esfuerzo **0,5**.

**E6.** ¿Qué muestra `print(-3 ** 2)`? ¿Y `print((-3) ** 2)`? ¿Por qué son distintos?

**E7.** Un episodio del humanoide dura como mucho **1.000 pasos** de **0,015 segundos** cada uno. Usa
dos variables, `pasos` y `duracion_paso`, para calcular cuántos segundos dura un episodio completo.

**E8.** En el NB00 dijimos que un robot real que se cayera un millón de veces, una cada 10 segundos,
necesitaría unos **115 días**. Compruébalo con Python. Pista: un día tiene 60 × 60 × 24 segundos.

**E9.** Continúa la pelota del apartado 16: tras los tres pasitos, la velocidad es 3,0 y la altura 1,4.
¿Qué valores saldrían si ejecutaras la celda del pasito **una vez más**? Hazlo a mano.
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
masa_torso = 8.91
print(masa_torso)
```

Salida: `8.91`. Recuerda el **punto** decimal (NB05).
</details>

<details>
<summary>▶ Solución E2</summary>

Muestra **`7`**. Paso a paso: `x` empieza en 5; `x = x * 2` calcula 5 × 2 = 10 y lo guarda en `x`;
`x = x - 3` calcula 10 − 3 = 7 y lo guarda en `x`. Cada línea usa lo que dejó la anterior.
</details>

<details>
<summary>▶ Solución E3</summary>

- `altura_torso` → **válido**.
- `3motores` → **no válido**: empieza por un número.
- `motor_3` → **válido**: los números están permitidos si no van al principio.
- `velocidad maxima` → **no válido**: tiene un espacio (sería `velocidad_maxima`).
- `Velocidad` → **válido**, pero ojo: es una caja **distinta** de `velocidad` (mayúsculas cuentan).
</details>

<details>
<summary>▶ Solución E4</summary>

- `10 - 2 * 3` → primero la multiplicación (2 × 3 = 6), luego la resta: 10 − 6 = **4**.
- `(10 - 2) * 3` → primero el paréntesis (10 − 2 = 8), luego la multiplicación: 8 × 3 = **24**.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
velocidad = 1.5
esfuerzo = 0.5
recompensa = premio_de_pie + peso_avance * velocidad - peso_esfuerzo * esfuerzo
print(recompensa)
```

Salida: **`6.825`**. A mano: 5 + 1,25 × 1,5 − 0,1 × 0,5 = 5 + 1,875 − 0,05 = 6,825.
</details>

<details>
<summary>▶ Solución E6</summary>

- `print(-3 ** 2)` muestra **`-9`**: la potencia va antes que el signo menos, así que calcula
  −(3²) = −9.
- `print((-3) ** 2)` muestra **`9`**: el paréntesis hace que se eleve al cuadrado el −3 entero, y
  menos por menos da más.
</details>

<details>
<summary>▶ Solución E7</summary>

```python
pasos = 1000
duracion_paso = 0.015
print(pasos * duracion_paso)
```

Salida: **`15.0`** segundos (con `.0` porque hay un decimal en la cuenta). Es el "final del partido"
del NB03.
</details>

<details>
<summary>▶ Solución E8</summary>

```python
caidas = 1000000
segundos_por_caida = 10
segundos_por_dia = 60 * 60 * 24
dias = caidas * segundos_por_caida / segundos_por_dia
print(dias)
```

Salida: **`115.74074074074075`**, es decir, unos **115 días** y tres cuartos. (Un día tiene 60 × 60 × 24
= 86.400 segundos.) Fíjate en que los números grandes se escriben **sin puntos de miles**: `1000000`,
no `1.000.000`, porque en Python el punto es el decimal.
</details>

<details>
<summary>▶ Solución E9</summary>

- Velocidad: 3,0 + 10 × 0,1 = **4,0**.
- Altura: 1,4 − 4,0 × 0,1 = 1,4 − 0,4 = **1,0**.

Es la fila 4 de la tabla del NB02. (Si lo ejecutas en Python puede que veas `0.9999999999999999` en
vez de `1.0`: es el ruido de los decimales del apartado 12. Lo veremos en directo en el NB07.)
</details>
"""),

md(r"""## 19 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy el ordenador ha ganado **memoria**: ya puede guardar la velocidad, la altura, los pesos de la
recompensa... y tú has programado tu primer simulador de física, aunque a base de copiar y pegar. En el
**NB07** aprenderás a decirle al ordenador "**repite esto 1.000 veces**" en una sola línea: los
**bucles**. Con ellos, la pelota caerá durante todos los pasitos que queramos, comprobaremos con el
ordenador lo que el NB02 te contó sobre los pasos grandes y pequeños, y sumaremos los puntos de un
episodio entero del humanoide sin despeinarnos.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB06_variables_y_numeros.ipynb")
    build(out, cells, title="NB06 · Cajas con nombre: variables y números")
