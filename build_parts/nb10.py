"""Construye NB10 · Recetas con nombre: las funciones (Parte 1 · Lección 6).

Microdosis: def sin parámetros (definir no hace nada), llamar, parámetros,
return vs print, None (olvidar el return), TypeError por faltar un argumento,
varias entradas (recompensa con if), funciones que llaman a funciones (esfuerzo
dentro de recompensa), variables locales (NameError real), devolver dos cosas
(paso_pelota → simulador limpio), y la gran idea: la POLÍTICA ES UNA FUNCIÓN
(termostato) y el ENTORNO también (habitacion); simular(politica) con la
política intercambiable; dos termostatos comparados con números (60 min:
normal 23 min encendida, media 19.95; ahorrador 21 min, media 18.99).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB10 · Recetas con nombre: las funciones

**Parte 1 · Primeros pasos con el ordenador — Lección 6**

> En el **NB09** metiste los 17 motores del humanoide en una lista, grabaste la trayectoria de la
> pelota y usaste órdenes ya hechas como `len`, `sum` o `max`. Te dije que esas órdenes se llaman
> **funciones**. Hoy aprenderás a **fabricar las tuyas**.

Una función es una **receta con nombre**: un trozo de programa al que le pones un nombre para poder usarlo
cuantas veces quieras, sin volver a escribirlo. Parece una comodidad pequeña, pero es **la herramienta más
importante para organizar programas grandes**. Ningún simulador, ningún robot, ningún programa serio se
escribe sin funciones.

Y hoy descubrirás algo precioso: la **política** del NB03 —esa caja que recibe una observación y devuelve una
acción— **es, literalmente, una función**. Y el **entorno**, también. Al final de esta lección tendrás un
agente y un entorno separados, cada uno en su función, y podrás **cambiar la política sin tocar el mundo**,
que es justo lo que hacen los profesionales.

Una idea nueva por celda.
"""),

md(r"""## 1 · El botón de "palomitas" del microondas

Piensa en un microondas con un botón que pone **"palomitas"**. Al pulsarlo, el microondas hace una secuencia
de cosas: potencia máxima, 3 minutos, pitido al final. Tú no tienes que programar esos pasos cada vez: alguien
los guardó **una vez** bajo un nombre, y desde entonces **pulsas el botón** y listo.

Una función es exactamente eso:

```
   DEFINIR la función (una sola vez):        USARLA (todas las veces que quieras):

   "palomitas" significa:                     pulsar "palomitas"
       potencia máxima                        pulsar "palomitas"
       3 minutos                              pulsar "palomitas"
       pitido
```

Hay dos momentos distintos, y conviene no mezclarlos:

1. **Definir** la función: escribir la receta y ponerle nombre. Esto **no la ejecuta**; solo la guarda.
2. **Llamar** a la función: usarla. Cada vez que la llamas, se ejecuta la receta entera.

Ya llevas cinco lecciones **llamando** funciones que otros definieron: `print("hola")` es pulsar el botón
"print". Hoy vas a **definir**.
"""),

md(r"""## 2 · Definir tu primera función

Una función se define con la palabra **`def`** (de *define*, "definir"), el **nombre** que le quieras dar,
unos **paréntesis**, **dos puntos**, y debajo, **con sangría**, la receta. ¿Te suena? Dos puntos y sangría,
como en el `for` (NB07) y el `if` (NB08). Esta celda define una función llamada `saludar`:
"""),

code(r"""def saludar():
    print("¡Hola! Soy un robot y estoy aprendiendo a andar.")"""),

md(r"""**No ha salido nada.** Y es lo correcto: hemos **definido** la función (guardado la receta bajo el nombre
`saludar`), pero **no la hemos llamado**. Es como guardar el programa "palomitas" en el microondas sin pulsar
el botón.

```
   def   saludar   ( )   :
   ───   ───────   ───   ─
    │       │       │    └── dos puntos: "a continuación, la receta"
    │       │       └─────── paréntesis (aquí vacíos: no necesita ingredientes)
    │       └─────────────── el nombre que tú eliges (mismas reglas que las variables)
    └─────────────────────── "defino una función"

       print(...)       ← con sangría: el CUERPO de la función (la receta)
```
"""),

md(r"""## 3 · Llamar a la función

Para **usarla**, se escribe su nombre con los paréntesis, igual que `print(...)`:"""),

code(r"""saludar()"""),

md(r"""¡Ahora sí! Al llamarla, Python ha ido a buscar la receta guardada con el nombre `saludar` y la ha ejecutado.
Y la podemos llamar todas las veces que queramos:
"""),

code(r"""saludar()
saludar()"""),

md(r"""Dos llamadas, dos saludos, y la receta escrita **una sola vez**. Si mañana quieres cambiar el saludo, lo
cambias en **un** sitio (la definición) y cambia en todas las llamadas.

(¡Ojo con los paréntesis! `saludar()` **llama** a la función. `saludar` a secas, sin paréntesis, solo
**nombra** la función sin ejecutarla. Lo usaremos al final de la lección.)
"""),

md(r"""## 4 · Darle ingredientes: los parámetros

Un botón de "palomitas" siempre hace lo mismo. Pero muchas recetas necesitan **ingredientes** que cambian
cada vez: "calienta **X** minutos". Para eso, entre los paréntesis de la definición se ponen **nombres de
cajas** que se rellenarán en cada llamada. Se llaman **parámetros**:
"""),

code(r"""def saludar_a(nombre):
    print("Hola,", nombre)"""),

md(r"""La función `saludar_a` tiene un parámetro, `nombre`. Es una caja que, por ahora, está vacía. Se rellena
**al llamar a la función**, poniendo un valor entre los paréntesis:
"""),

code(r"""saludar_a("Atlas")
saludar_a("Digit")"""),

md(r"""En la primera llamada, la caja `nombre` se rellena con `"Atlas"`; en la segunda, con `"Digit"` (dos de los
robots del NB00). La misma receta, con ingredientes distintos.

Al valor concreto que se pasa en la llamada (`"Atlas"`) se le llama **argumento**. Parámetro y argumento son
las dos caras de lo mismo: el **parámetro** es el hueco en la receta; el **argumento**, lo que metes en el
hueco al usarla.
"""),

md(r"""## 5 · Que la función te devuelva un resultado: `return`

Hasta ahora nuestras funciones **muestran** cosas con `print`. Pero muchas veces no queremos que la función
diga nada en voz alta: queremos que **calcule algo y nos dé el resultado** para seguir usándolo. Como `len`
(NB09), que no imprime nada: te **devuelve** un número.

Para eso existe **`return`** ("devolver"). Esta función calcula el premio por avanzar del NB04 y lo
**devuelve**:
"""),

code(r"""def premio_avance(velocidad):
    return 1.25 * velocidad"""),

md(r"""Al llamarla, la llamada **se convierte** en el resultado, y podemos guardarlo en una caja como cualquier
otro valor:
"""),

code(r"""premio = premio_avance(2)
print(premio)"""),

md(r"""**2.5**. La llamada `premio_avance(2)` ha calculado 1,25 × 2 y ha **devuelto** 2,5, que se ha guardado en la
caja `premio`.

La diferencia entre `print` y `return` es importantísima:

```
   print   → lo DICE EN VOZ ALTA (lo muestra en pantalla) y el valor se pierde.
   return  → te lo DA EN LA MANO (lo devuelve) para que hagas con él lo que quieras:
             guardarlo, sumarlo, compararlo, pasárselo a otra función...
```

Es como pedirle a alguien que haga una cuenta: puede **decirte** el resultado en voz alta (y si no lo
apuntas, se olvida), o **escribírtelo en un papel y dártelo** (y lo guardas). `return` es el papel.
"""),

md(r"""### ¿Y si se me olvida el `return`?

Es un despiste muy común. Esta función **calcula** el premio pero no lo devuelve:"""),

code(r"""def premio_avance_mal(velocidad):
    premio = 1.25 * velocidad

print(premio_avance_mal(2))"""),

md(r"""Sale **`None`**, que en inglés significa "**nada**". La función hizo la cuenta por dentro, pero como no
tiene `return`, no devolvió nada, y Python representa "nada" con la palabra `None`. Si alguna vez ves un
`None` inesperado, lo primero que debes sospechar es: **"¿me he olvidado el `return`?"**.
"""),

md(r"""## 6 · Varias entradas: la recompensa completa como función

Una función puede tener **varios parámetros**, separados por comas. Y dentro puede tener todo lo que ya
sabes: `if`, bucles, cajas... Esta es la recompensa del humanoide del NB08 (con su `if` del +5) metida en
una función con tres parámetros:
"""),

code(r"""def recompensa(altura_torso, velocidad, esfuerzo):
    if altura_torso > 1.0 and altura_torso < 2.0:
        premio_de_pie = 5
    else:
        premio_de_pie = 0
    return premio_de_pie + 1.25 * velocidad - 0.1 * esfuerzo"""),

md(r"""Al llamarla, los argumentos se emparejan con los parámetros **por orden**: el primero con `altura_torso`, el
segundo con `velocidad`, el tercero con `esfuerzo` (como las listas en paralelo del NB09):
"""),

code(r"""print(recompensa(1.3, 2, 1))
print(recompensa(0.9, 2, 1))"""),

md(r"""**7.4** (de pie, como siempre desde el NB04) y **2.4** (caído: sin el +5). Ahora la recompensa es un
"botón": le das la situación y te devuelve los puntos. El simulador del humanoide tiene, literalmente, una
función así por dentro.

¿Y si nos olvidamos de un argumento? Python se queja, porque la receta necesita sus tres ingredientes:
"""),

code_err(r"""print(recompensa(1.3, 2))"""),

md(r"""`TypeError: recompensa() missing 1 required positional argument: 'esfuerzo'`: "a `recompensa()` le **falta
1 argumento** obligatorio: `esfuerzo`". Un mensaje muy claro: dice qué función, cuántos faltan y cuál.

| Tipo de error | Qué suele significar |
|---|---|
| `NameError` | Nombre desconocido |
| `SyntaxError` | Gramática rota |
| `IndentationError` | Sangría que falta o sobra |
| `IndexError` | Posición que la lista no tiene |
| `TypeError` | Has usado algo de forma que no encaja (aquí: faltan argumentos) |
"""),

md(r"""## 7 · Funciones que usan funciones

Una función puede **llamar a otra**. Así se construyen programas grandes: piezas pequeñas que se apoyan unas
en otras, como los ladrillos de una pared.

Primero, una función que calcula el **esfuerzo** de una acción (una lista, NB09):
"""),

code(r"""def calcular_esfuerzo(accion):
    total = 0
    for a in accion:
        total = total + a ** 2
    return total"""),

md(r"""Y ahora una versión de la recompensa que recibe **la acción entera** (la lista de motores) y **llama** a
`calcular_esfuerzo` por dentro, en lugar de recibir el esfuerzo ya calculado:
"""),

code(r"""def recompensa_paso(altura_torso, velocidad, accion):
    if altura_torso > 1.0 and altura_torso < 2.0:
        premio_de_pie = 5
    else:
        premio_de_pie = 0
    return premio_de_pie + 1.25 * velocidad - 0.1 * calcular_esfuerzo(accion)

print(round(recompensa_paso(1.3, 2, [0.4, -0.4, 0.1]), 3))"""),

md(r"""**7.467**: 5 de pie + 2,5 por avanzar − 0,033 de esfuerzo (0,1 × 0,33, el esfuerzo de esa acción que
calculamos en el NB09).

Fíjate en lo **legible** que es: `recompensa_paso` no sabe ni le importa **cómo** se calcula el esfuerzo; solo
llama a la función que lo sabe. Si mañana el diseñador decide medir el esfuerzo de otra manera, se cambia
**solo** `calcular_esfuerzo`, y todo lo demás sigue funcionando. A esto se le llama dividir un problema en
**piezas independientes**, y es el gran secreto para escribir programas que no se convierten en un caos.
"""),

md(r"""## 8 · Lo que pasa en la función se queda en la función

Un detalle importante. Las cajas que se crean **dentro** de una función (como `total` en `calcular_esfuerzo`, o
`premio_de_pie` en `recompensa_paso`) son **privadas** de la función: existen mientras la función trabaja, y
**desaparecen** cuando termina. Desde fuera no se ven. Comprobémoslo:
"""),

code_err(r"""calcular_esfuerzo([0.4, -0.4, 0.1])
print(total)"""),

md(r"""`NameError: name 'total' is not defined`. La caja `total` existió **dentro** de `calcular_esfuerzo` mientras
trabajaba, pero al terminar desapareció. Fuera de la función, no hay ninguna caja `total`.

A estas cajas se les llama **variables locales** (viven solo "en el local" de la función). Es como el
cocinero que usa cuencos para preparar la receta: cuando te entrega el plato (el `return`), los cuencos se
lavan y se guardan. Tú solo recibes el plato.

Esto es una **ventaja**, no un problema: puedes usar un nombre como `total` dentro de mil funciones distintas
sin que se pisen unas a otras. Y si quieres algo de dentro, la manera correcta de sacarlo es... `return`.
"""),

md(r"""## 9 · Devolver dos cosas a la vez

Una función puede devolver **varios** valores, separados por comas. Es justo lo que necesita el **pasito de
física** de la pelota (NB06): a partir de la altura y la velocidad de ahora, calcula la altura y la velocidad
**nuevas**. Dos entradas, dos salidas:
"""),

code(r"""def paso_pelota(altura, velocidad):
    velocidad = velocidad + 10 * 0.1
    altura = altura - velocidad * 0.1
    return altura, velocidad"""),

md(r"""Para recoger los dos resultados, se ponen **dos cajas a la izquierda del `=`**, separadas por una coma. La
primera recibe lo primero que se devolvió y la segunda, lo segundo:
"""),

code(r"""altura, velocidad = paso_pelota(2.0, 0.0)
print(altura, velocidad)"""),

md(r"""**1.9 y 1.0**: la fila 1 de la tabla del NB02, otra vez. Ahora mira lo limpio que queda el simulador entero
con un bucle (NB07) que llama a la función. Toda la física está escondida en `paso_pelota`; el bucle solo
dice "da 5 pasitos":
"""),

code(r"""altura = 2.0
velocidad = 0.0
for paso in range(5):
    altura, velocidad = paso_pelota(altura, velocidad)

print("Tras 5 pasitos:", round(altura, 2), "metros, a", velocidad, "m/s")"""),

md(r"""**0.5 metros a 5 m/s**: la fila 5 de la tabla. En cada vuelta, la función recibe el estado actual y devuelve
el estado siguiente, que vuelve a entrar en la vuelta siguiente.

Esta función tiene un nombre en el mundo de la robótica: es la **función de paso** del entorno, la que recibe
"cómo está el mundo ahora" y devuelve "cómo está un pasito después". Todos los simuladores tienen una. En
el simulador del humanoide se llama, literalmente, `step` ("paso").
"""),

md(r"""## 10 · La gran idea: la política es una función

Ahora, el momento por el que hemos llegado hasta aquí. Recuerda la definición de **política** del NB03:

> La regla que, dada una **observación**, decide qué **acción** tomar.

Recibe algo y devuelve algo. ¡Es una **función**! Escribamos la política del **termostato** (NB08) como una
función: recibe la observación (la temperatura) y devuelve la acción (encender o apagar):
"""),

code(r"""def termostato(temperatura):
    if temperatura < 20:
        return "encendida"
    else:
        return "apagada"
"""),

md(r"""(Fíjate: una función puede tener **varios `return`**, uno en cada camino del `if`. En cuanto Python
encuentra un `return`, devuelve ese valor y **la función termina**, como un `break` para funciones.)

Y el **entorno** (la habitación), otra función: recibe el estado (la temperatura) y la acción (la calefacción),
y devuelve el estado siguiente. Es su **función de paso**:
"""),

code(r"""def habitacion(temperatura, calefaccion):
    if calefaccion == "encendida":
        return temperatura + 0.5
    else:
        return temperatura - 0.25"""),

md(r"""Ahora, el **bucle agente-entorno** del NB03, con cada pieza en su sitio. Léelo despacio: es el esquema de
**todo** el aprendizaje por refuerzo, con un termostato en lugar de un humanoide:
"""),

code(r"""temperatura = 18.0

for minuto in range(1, 9):
    accion = termostato(temperatura)                # EL AGENTE: observación → acción
    temperatura = habitacion(temperatura, accion)   # EL ENTORNO: estado + acción → nuevo estado
    print("minuto", minuto, "|", accion, "|", temperatura, "grados")"""),

md(r"""Mismo resultado que en el NB08, pero ahora fíjate en la **forma**:

```
   ┌─────────────────────────────────────────────────────────────┐
   │   accion = termostato(temperatura)              ← AGENTE     │
   │   temperatura = habitacion(temperatura, accion) ← ENTORNO    │
   └─────────────────────────────────────────────────────────────┘
               (repetir en cada paso: el bucle del NB03)
```

**Dos líneas.** Una es el agente; la otra, el entorno. Están **separados**: el termostato no sabe nada de cómo
se calienta la habitación, y la habitación no sabe nada de qué regla usa el termostato. Solo se comunican por
lo que se pasan: la observación y la acción.
"""),

md(r"""## 11 · Cambiar la política sin tocar el mundo

¿Por qué es tan importante esa separación? Porque nos permite **probar políticas distintas en el mismo
mundo**, sin tocar el mundo. Y eso es, precisamente, lo que hace el entrenamiento: probar políticas y
quedarse con la mejor.

Vamos a escribir una **segunda política**, un termostato "ahorrador" que solo enciende por debajo de **19**
grados:
"""),

code(r"""def termostato_ahorrador(temperatura):
    if temperatura < 19:
        return "encendida"
    else:
        return "apagada"
"""),

md(r"""Y ahora, una función que **simula una hora entera** (60 minutos) con **la política que le pasemos**, y nos
devuelve dos medidas: cuántos minutos estuvo encendida la calefacción (gasto) y qué temperatura media hubo
(comodidad).

La idea nueva de esta celda: **una función puede recibir otra función como argumento**. Fíjate en el parámetro
`politica`: al llamar a `simular_una_hora`, le pasaremos el **nombre** de una de nuestras funciones,
**sin paréntesis** (apartado 3), y dentro se usará como `politica(temperatura)`. Es como darle al cocinero no
un ingrediente, sino **otra receta** para que la use:
"""),

code(r"""def simular_una_hora(politica):
    temperatura = 18.0
    minutos_encendida = 0
    temperaturas = []
    for minuto in range(60):
        accion = politica(temperatura)                 # la política que nos hayan pasado
        if accion == "encendida":
            minutos_encendida = minutos_encendida + 1
        temperatura = habitacion(temperatura, accion)  # el mundo, siempre el mismo
        temperaturas.append(temperatura)
    media = sum(temperaturas) / len(temperaturas)
    return minutos_encendida, media"""),

md(r"""Ahora probamos **las dos políticas en el mismo mundo**, con una línea cada una:"""),

code(r"""gasto, comodidad = simular_una_hora(termostato)
print("Termostato normal:     ", gasto, "minutos encendida | temperatura media", round(comodidad, 2))

gasto, comodidad = simular_una_hora(termostato_ahorrador)
print("Termostato ahorrador:  ", gasto, "minutos encendida | temperatura media", round(comodidad, 2))"""),

md(r"""Resultados de una hora:

| Política | Minutos encendida (gasto) | Temperatura media (comodidad) |
|---|---|---|
| Termostato normal (umbral 20) | 23 | 19,95 °C |
| Termostato ahorrador (umbral 19) | 21 | 18,99 °C |

¿Cuál es **mejor**? Pues... **depende de qué valores más**. El ahorrador gasta un poco menos, pero la casa está
un grado más fría. Si te importa mucho la factura, ganas con el ahorrador; si te importa estar calentito, con el
normal.

¿Te suena? Es **exactamente** el dilema de diseñar una recompensa del NB04. Para que un ordenador pudiera
**elegir solo** la mejor política, tendríamos que decirle con un **número** cuánto vale cada cosa: por ejemplo,
"+1 punto por cada minuto cerca de 20 grados, −0,5 por cada minuto de calefacción". Con ese número, comparar
políticas sería tan fácil como comparar dos retornos. Y probar **muchas** políticas automáticamente y quedarse con
la que más puntos saca... eso ya es **aprender**.

Que es justo lo que vas a hacer en el próximo notebook.
"""),

md(r"""## 12 · Resumen de la lección

1. Una **función** es una receta con nombre: se **define** una vez con `def nombre(parámetros):` y un cuerpo con
   sangría, y se **llama** las veces que haga falta con `nombre(argumentos)`. Definir no ejecuta nada.
2. Los **parámetros** son los huecos de la receta; los **argumentos**, lo que se mete en ellos al llamar (se
   emparejan **por orden**). Si falta alguno: `TypeError`.
3. **`return`** devuelve un resultado para seguir usándolo (`print` solo lo muestra). Sin `return`, la función
   devuelve **`None`**. Se pueden devolver varios valores: `a, b = funcion(...)`.
4. Las cajas creadas dentro de una función son **locales**: desaparecen al terminar. Las funciones pueden
   **llamar a otras** y hasta **recibir otras funciones** como argumento (por su nombre, sin paréntesis).
5. La **política** es una función (observación → acción) y el **entorno** también (estado + acción → nuevo
   estado: la **función de paso**, `step`). Separados, permiten **probar políticas distintas en el mismo
   mundo** y compararlas con números.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Función** | Una receta con nombre que se puede usar muchas veces. |
| **`def`** | La palabra para definir una función. |
| **Llamar** | Usar una función: `nombre(...)`. |
| **Parámetro** | El hueco de la receta, en la definición: `def f(velocidad)`. |
| **Argumento** | El valor que se mete en el hueco al llamar: `f(2)`. |
| **`return`** | Devuelve un resultado y termina la función. |
| **`None`** | "Nada": lo que devuelve una función sin `return`. |
| **`TypeError`** | Error por usar algo de forma que no encaja (por ejemplo, faltan argumentos). |
| **Variable local** | Una caja creada dentro de una función, que desaparece al terminar. |
| **Función de paso (`step`)** | La función del entorno: estado + acción → estado siguiente. |
"""),

md(r"""## 13 · Ejercicios

**E1.** Define una función `despedir()` que muestre "¡Hasta mañana, robot!" y llámala dos veces.

**E2.** Define una función `al_cuadrado(x)` que **devuelva** x al cuadrado. Úsala para calcular `al_cuadrado(3)`
y `al_cuadrado(-0.4)`.

**E3.** Predice qué muestra este programa y explica por qué:

```python
def doble(x):
    print(x * 2)

resultado = doble(5)
print(resultado)
```

**E4.** Define una función `media(lista)` que devuelva la media de una lista de números (NB09: suma entre
cuántos hay). Pruébala con `[5.2, 4.9, 6.1, 5.5, 5.8]`.

**E5.** Define una función `se_ha_caido(altura_torso)` que devuelva `True` si el torso está por debajo de 1
metro y `False` si no. Pista: puedes devolver directamente una comparación: `return altura_torso < 1.0`.

**E6.** Escribe una tercera política para el termostato, `termostato_caluroso`, que encienda por debajo de **21**
grados, y pruébala con `simular_una_hora`. ¿Gasta más o menos que la normal? ¿Qué temperatura media consigue?

**E7.** **Reto.** Escribe una función `puntos_termostato(gasto, comodidad)` que convierta las dos medidas en
**un solo número**, por ejemplo: `comodidad * 10 - gasto * 0.5`. Úsala para decidir cuál de las tres políticas
(normal, ahorrador, caluroso) es "la mejor" según ese criterio. ¿Cambia el ganador si en vez de `0.5` pones
`10`?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
def despedir():
    print("¡Hasta mañana, robot!")

despedir()
despedir()
```

La despedida sale dos veces. La definición no muestra nada; cada **llamada**, sí.
</details>

<details>
<summary>▶ Solución E2</summary>

```python
def al_cuadrado(x):
    return x ** 2

print(al_cuadrado(3))
print(al_cuadrado(-0.4))
```

Salida: `9` y `0.16000000000000003` (el ruido de decimales del NB06; con `round(..., 2)` saldría 0.16). Y fíjate:
como `-0.4` llega **dentro de la caja** `x`, no hay trampa con el signo menos (NB06): sale positivo.
</details>

<details>
<summary>▶ Solución E3</summary>

Muestra **`10`** y luego **`None`**. La función `doble` **muestra** el doble con `print` (por eso sale el 10),
pero **no lo devuelve** (no tiene `return`). Así que `doble(5)` vale `None`, que es lo que se guarda en
`resultado` y lo que muestra el segundo `print`. Para poder guardar el 10, la función debería usar
`return x * 2`.
</details>

<details>
<summary>▶ Solución E4</summary>

```python
def media(lista):
    return sum(lista) / len(lista)

print(round(media([5.2, 4.9, 6.1, 5.5, 5.8]), 2))
```

Salida: **5.5**, igual que en el ejercicio E6 del NB09, pero ahora la cuenta tiene nombre y sirve para cualquier
lista.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
def se_ha_caido(altura_torso):
    return altura_torso < 1.0

print(se_ha_caido(0.8))
print(se_ha_caido(1.3))
```

Salida: `True` y `False`. Una comparación ya **es** un valor (`True` o `False`, NB08), así que se puede devolver
directamente, sin `if`. Esta función es, literalmente, la que decide si un episodio del humanoide está
**terminado**.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
def termostato_caluroso(temperatura):
    if temperatura < 21:
        return "encendida"
    else:
        return "apagada"

gasto, comodidad = simular_una_hora(termostato_caluroso)
print(gasto, round(comodidad, 2))
```

Si lo ejecutas, verás que gasta **más** minutos que el normal (empieza más lejos de su objetivo y tiene que subir
hasta 21) y consigue una temperatura media de casi **21** grados. Más comodidad, más gasto. No hemos tocado
`habitacion` ni `simular_una_hora`: solo hemos escrito otra política y la hemos enchufado.
</details>

<details>
<summary>▶ Solución E7</summary>

```python
def puntos_termostato(gasto, comodidad):
    return comodidad * 10 - gasto * 0.5

for nombre, politica in [("normal", termostato), ("ahorrador", termostato_ahorrador),
                         ("caluroso", termostato_caluroso)]:
    gasto, comodidad = simular_una_hora(politica)
    print(nombre, round(puntos_termostato(gasto, comodidad), 2))
```

(Este bucle recorre una lista de **parejas**; si te resulta raro, puedes simplemente escribir tres bloques, uno por
política.) Resultados:

| Política | Gasto | Comodidad | Puntos con castigo 0,5 | Puntos con castigo 10 |
|---|---|---|---|---|
| normal (20) | 23 | 19,95 | 188,0 | −30,5 |
| ahorrador (19) | 21 | 18,99 | 179,38 | **−20,1** |
| caluroso (21) | 24 | 20,88 | **196,75** | −31,2 |

Con un castigo de **0,5** por minuto encendido, la comodidad pesa mucho y gana la política que más calienta (la
calurosa). Con un castigo de **10**, gastar sale carísimo y gana la ahorradora. (Con un castigo intermedio, como 3,
todavía gana la calurosa: el cambio de ganador ocurre a partir de algo más de 6.) **Cambiar el peso de un ingrediente
de la recompensa cambia qué política es "la mejor"**: es la lección del NB04, ahora con tus propias manos.
</details>
"""),

md(r"""## 14 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Con las funciones ya tienes **todas las herramientas de la Parte 1**: orden, variables, bucles, decisiones, listas
y funciones. Y has visto que agente y entorno, separados en funciones, encajan perfectamente con el bucle del
NB03.

El **NB11** es el **proyecto final de la Parte 1**, y es especial: vamos a construir **desde cero** un mundo para
un robot de juguete que tiene que **mantener el equilibrio de un palo de escoba** (¡el del NB00!). Tendrá su
función de paso, su recompensa, sus episodios que terminan cuando el palo se cae... y probaremos políticas: no
hacer nada, moverse al azar, una escrita a mano... y, por último, haremos que el ordenador **encuentre sola** una
buena política **probando**. Será tu primer aprendizaje por refuerzo, hecho con tus propias manos.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB10_funciones.ipynb")
    build(out, cells, title="NB10 · Recetas con nombre: las funciones")
