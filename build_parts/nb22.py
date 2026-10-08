"""Construye NB22 · Python de verdad (3): control de flujo, errores y depuración.

while (pelota hasta tocar el suelo; bucles infinitos y cómo pararlos; límite de
seguridad), break/continue (saltar líneas vacías y comentarios de un registro),
for...else, pass, valores "verdaderos" y "falsos" (listas vacías, 0, None, ""),
is None, match-case. Excepciones: qué son, leer una traza con llamadas
anidadas (de abajo arriba), try/except (tipos concretos, as e, varios except,
else, finally), raise para validar (ValueError propio), assert, detectar una
explosión numérica (NaN/infinito, math.isfinite) y parar con un mensaje claro.
Depurar: método (reproducir, leer, aislar, comprobar suposiciones), print con
f"{x=}", %debug / breakpoint() / pdb (explicado), catálogo de bugs típicos y un
ejercicio de "encuentra los fallos".
Práctica en MuJoCo (§13): planos rotos -> ValueError (catálogo de erratas con
try/except/else); palo con muelle rígido que explota con paso grande (x-20 por
paso) y el reinicio silencioso de MuJoCo; vigilante con datos.warning +
while con límite de seguridad; humanoide con paso 0,02 (vídeo + contar explosiones).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB22 · Python de verdad (3): control de flujo, errores y depuración

**Parte 3 · Python de verdad — Lección 3**

> En el **NB21** aprendiste a guardar datos en colecciones. Hoy vamos con dos cosas que separan a alguien que "sabe Python" de
> alguien que **trabaja** con Python: controlar con precisión **cuándo** se repite o se salta algo, y saber qué hacer cuando las
> cosas **fallan**.

Un entrenamiento de un robot puede durar **horas o días**. Si a las cinco horas aparece un dato raro y el programa se cae, pierdes
cinco horas. Si el robot "aprende" algo absurdo, tienes que averiguar **por qué**. Por eso hoy veremos:

1. Más control del flujo: el bucle **`while`**, `continue`, `pass`, `match`...
2. Las **excepciones**: qué son los errores por dentro, cómo **capturarlos** para que el programa no se caiga, y cómo **lanzar** los tuyos
   para detectar problemas pronto.
3. **Depurar**: el método para encontrar por qué un programa no hace lo que esperas. Es, literalmente, la mitad del trabajo de cualquier
   programador.
"""),

md(r"""## 1 · `while`: repetir **mientras** algo sea cierto

El `for` (NB07) repite un número **conocido** de veces: "para cada elemento", "1.000 veces". Pero a veces no sabes cuántas vueltas harán
falta: "**mientras** la pelota esté en el aire, sigue simulando". Para eso existe **`while`** ("mientras"):

```
   while condición:
       ...cuerpo...        ← se repite MIENTRAS la condición sea True
```

Antes de cada vuelta, Python mira la condición. Si es `True`, da la vuelta; si es `False`, sale del bucle. Simulemos la pelota del NB07
**hasta que toque el suelo**, sin saber de antemano cuántos pasos serán:
"""),

code(r"""altura = 2.0
velocidad = 0.0
pasos = 0

while altura > 0:
    velocidad = velocidad + 10 * 0.01
    altura = altura - velocidad * 0.01
    pasos = pasos + 1

print(f"La pelota toca el suelo tras {pasos} pasos ({pasos * 0.01:.2f} segundos)")"""),

md(r"""**63 pasos**, el mismo bote del NB08 (paso 63), pero esta vez el bucle ha parado **solo**, en cuanto la condición `altura > 0` dejó de cumplirse.
No hemos tenido que adivinar un número de vueltas.
"""),

md(r"""### El peligro: el bucle infinito

Un `while` tiene un riesgo que el `for` no tiene: si la condición **nunca** deja de ser cierta, el bucle **no termina jamás**. Por ejemplo, si
olvidas actualizar la altura dentro del bucle, `altura > 0` será siempre `True` y el programa se quedará colgado, dando vueltas para siempre (no lo
ejecutamos aquí, claro).

Si te pasa en Jupyter, verás el `[*]` a la izquierda de la celda sin terminar nunca. Para pararlo: botón **■ (Stop)** de arriba, o menú **Kernel →
Interrupt**. En una terminal, **Ctrl + C**.

La costumbre profesional para evitarlo: en los `while` que dependen de algo que **podría no pasar nunca** (por ejemplo, que un robot aprenda), poner
siempre un **límite de seguridad**:
"""),

code(r"""retorno = 0
intentos = 0
while retorno < 400 and intentos < 1000:     # para si lo consigue... o si se agota la paciencia
    intentos = intentos + 1
    retorno = retorno + 7.3                  # (aquí iría un episodio de entrenamiento de verdad)
print(f"Terminó tras {intentos} intentos con retorno {retorno:.1f}")"""),

md(r"""Con el `and intentos < 1000`, aunque el robot no aprendiera nunca, el bucle pararía a los 1.000 intentos. **Un `while` sin límite de seguridad en un
programa que corre durante horas es una bomba de relojería.**
"""),

md(r"""## 2 · `continue`: saltar a la siguiente vuelta

Ya conoces `break` (NB08), que **sale** del bucle. Su hermano **`continue`** no sale: **salta el resto de esta vuelta** y pasa directamente a la
siguiente. Es perfecto para **ignorar** elementos que no interesan. Por ejemplo, un registro real suele tener **líneas vacías** y **comentarios** (que
empiezan por `#`), que hay que saltarse al leerlo:
"""),

code(r"""registro = '''# entrenamiento del palo de escoba
episodio=1 retorno=44.8

episodio=2 retorno=97.2
# aquí cambié la tasa de aprendizaje
episodio=3 retorno=213.5'''

for linea in registro.split("\n"):
    linea = linea.strip()
    if linea == "" or linea.startswith("#"):
        continue                     # ¡a la siguiente línea!
    print("Procesando:", linea)"""),

md(r"""Las líneas vacías y los comentarios se han saltado; solo se procesan las tres líneas de datos. Sin `continue`, habría que meter todo el procesamiento
dentro de un `else`, con una sangría más. `continue` mantiene el código "plano" y legible.
"""),

md(r"""## 3 · Tres piezas pequeñas: `for ... else`, `pass` y `match`

**`for ... else`.** Un bucle puede llevar un `else` al final, que se ejecuta **solo si el bucle terminó sin `break`**. Suena raro, pero es justo lo que
hace falta para **buscar** algo: "recorre la lista; si lo encuentras, `break`; si acabas sin encontrarlo, haz el `else`":
"""),

code(r"""retornos = [44.8, 97.2, 213.5, 380.0]
for i, r in enumerate(retornos):
    if r > 400:
        print(f"Primer episodio por encima de 400: el {i}")
        break
else:
    print("Ningún episodio superó los 400")"""),

md(r"""Como ninguno supera 400, el bucle termina sin `break` y se ejecuta el `else`. (Es una herramienta poco común; mucha gente no la conoce. Úsala solo si
hace el código más claro.)

**`pass`** significa "**no hagas nada**". Sirve para cuando la gramática de Python exige un bloque pero aún no quieres escribirlo (por ejemplo, una
función que dejarás para luego):
"""),

code(r"""def politica_por_hacer(observacion):
    pass                 # TODO: escribir la política de verdad

print(politica_por_hacer([0.0, 0.0]))"""),

md(r"""Sin el `pass`, la función daría `IndentationError` (NB07: un bloque vacío no está permitido). Devuelve `None` (no tiene `return`). Por cierto, `TODO` ("por
hacer") es la marca que usan todos los programadores en los comentarios para lo que queda pendiente.

**`match`** (desde Python 3.10) es una forma elegante de elegir entre **muchos casos** según el valor de algo. Es como una cadena de `if`/`elif` (NB08), más
legible cuando se compara una misma cosa con muchos valores:
"""),

code(r"""def accion_desde_mando(boton):
    match boton:
        case "adelante":
            return [1.0, 0.0]
        case "atrás":
            return [-1.0, 0.0]
        case "izquierda" | "derecha":       # dos casos a la vez, con |
            return [0.0, 1.0 if boton == "izquierda" else -1.0]
        case _:                              # _ = "cualquier otra cosa"
            return [0.0, 0.0]

for b in ["adelante", "derecha", "saltar"]:
    print(b, "->", accion_desde_mando(b))"""),

md(r"""El `case _:` es el "si no" final: recoge todo lo que no coincida con los casos anteriores.
"""),

md(r"""## 4 · ¿Qué es "verdadero" para Python?

En un `if` o un `while` no hace falta poner siempre una comparación: Python acepta **cualquier valor**, y decide si es "verdadero" o "falso" con unas
reglas muy sencillas. Son **falsos**: `False`, `0`, `0.0`, `None`, el texto vacío `""` y las colecciones **vacías** (`[]`, `{}`, `()`, `set()`). **Todo lo demás
es verdadero**. `bool(...)` te dice cómo lo ve Python:
"""),

code(r"""for valor in [0, 3, "", "hola", [], [1, 2], None, {}]:
    print(f"{str(valor):>8} -> {bool(valor)}")"""),

md(r"""Esto permite escribir cosas muy naturales, como `if trayectoria:` ("si la trayectoria tiene algo") en vez de `if len(trayectoria) > 0:`.

Y para preguntar si algo es `None`, la forma correcta es con **`is`** (NB21), no con `==`: `if resultado is None:`. (Es una convención: `None` es un objeto
único, y `is` comprueba exactamente eso.)
"""),

md(r"""## 5 · Las excepciones: qué es un error por dentro

Llevas desde el NB05 viendo errores: `NameError`, `SyntaxError`, `IndentationError`, `IndexError`, `TypeError`, `ValueError`, `KeyError`... Ahora vamos a entender
qué son **por dentro**.

Cuando algo sale mal mientras el programa funciona, Python **lanza una excepción**: un "aviso de emergencia" que **interrumpe** lo que se estaba haciendo y sale
disparado hacia arriba. Si nadie lo **captura**, el programa se detiene y muestra el mensaje de error que ya conoces. (`SyntaxError` e `IndentationError` son
especiales: ocurren **antes** de ejecutar nada, al leer el código.)

| Excepción | Cuándo salta |
|---|---|
| `NameError` | Usas un nombre que no existe |
| `TypeError` | Usas algo de un tipo que no encaja (sumar texto y número, faltan argumentos...) |
| `ValueError` | El tipo está bien, pero el valor no tiene sentido (`float("hola")`) |
| `IndexError` | Posición fuera de una lista |
| `KeyError` | Clave que no existe en un diccionario |
| `ZeroDivisionError` | Dividir entre cero |
| `AttributeError` | Pides un método o dato que ese objeto no tiene (`[1, 2].upper()`) |
| `FileNotFoundError` | El fichero que intentas abrir no existe (NB26) |
| `AssertionError` | Falla un `assert` (apartado 9) |
"""),

md(r"""### Leer una traza larga

Cuando el error ocurre **dentro de una función llamada por otra función**, el mensaje es más largo: muestra **todo el camino** de llamadas. Se llama **traza**
(en inglés, *traceback*). Mira este ejemplo: `evaluar` llama a `episodio`, que llama a `politica`, y el error está en `politica`:
"""),

code_err(r"""def politica(observacion):
    return -30 * observacion[0] - 8 * observacion[2]     # ¡error! la observación solo tiene 2 números

def episodio(semilla):
    observacion = [2.0, 0.0]
    return politica(observacion)

def evaluar():
    return episodio(0)

evaluar()"""),

md(r"""La traza se lee **de abajo arriba**, como una pila de platos:

1. **La última línea** dice **qué** pasó: `IndexError: list index out of range`. Una posición que no existe (NB09).
2. **El bloque de justo encima** dice **dónde**: dentro de `politica`, en la línea `observacion[2]` (señalada con la flecha `---->`). ¡Ahí está el fallo! La
   observación tiene índices 0 y 1, y pedimos el 2.
3. **Los bloques de más arriba** dicen **cómo se llegó ahí**: `evaluar()` llamó a `episodio(0)`, que llamó a `politica(observacion)`.

El título lo dice: *Traceback (most recent call last)*, "traza (la llamada más reciente, al final)". **Regla: empieza por abajo.** El error casi siempre está en el
último bloque que sea **código tuyo** (a veces los últimos bloques son de una biblioteca, como NumPy; entonces sube hasta encontrar tu código, porque el fallo suele
estar en cómo la llamaste).
"""),

md(r"""## 6 · Capturar excepciones: `try` / `except`

A veces sabes que algo **puede** fallar, y no quieres que el programa se caiga por ello. Por ejemplo: leyendo un registro de miles de líneas, una está corrupta. ¿Vas
a perder todo el análisis por una línea? No: la **capturas**, avisas, y sigues.

```
   try:
       ...código que podría fallar...
   except TipoDeError:
       ...qué hacer si falla con ese error...
```

Python intenta (*try*) el bloque; si salta una excepción del tipo indicado, en vez de detener el programa, salta al bloque `except` ("excepto si...").
"""),

code(r"""lineas = ["455.3", "499.9", "error del sensor", "213.5", ""]

retornos = []
for linea in lineas:
    try:
        retornos.append(float(linea))
    except ValueError:
        print(f"Línea ignorada (no es un número): {linea!r}")

print("Retornos leídos:", retornos)"""),

md(r"""Las dos líneas malas se han ignorado con un aviso, y el resto se ha leído perfectamente. (En la f-string, `{linea!r}` muestra el texto **con comillas**, como lo
escribiría Python; así se ve claramente que la última línea era un texto **vacío**, `''`, que si no pasaría desapercibido.)

**Importante:** captura **solo el error que esperas** (aquí, `ValueError`). Hay una tentación muy peligrosa, escribir `except:` a secas (o `except Exception:`), que
captura **cualquier** error... incluidos los que **no** esperabas y que deberías ver, como una errata en un nombre (`NameError`). Es como desconectar la alarma de
incendios porque a veces salta al hacer tostadas. Captura lo concreto.
"""),

md(r"""### Ver el mensaje, varios tipos, `else` y `finally`

Con **`as e`** puedes guardar la excepción en una caja y ver su mensaje. Puedes tener **varios** `except` para distintos errores. **`else`** se ejecuta si **no**
hubo error, y **`finally`** se ejecuta **siempre**, haya error o no (perfecto para "recoger": cerrar un entorno, guardar lo que se tenga...):
"""),

code(r"""def leer_dato(registro, clave):
    try:
        valor = float(registro[clave])
    except KeyError:
        print(f"  Falta la clave {clave!r}")
        return None
    except ValueError as e:
        print(f"  Valor raro en {clave!r}: {e}")
        return None
    else:
        print(f"  Leído {clave} = {valor}")
        return valor
    finally:
        print("  (fin de la lectura)")

registro = {"retorno": "455.3", "pasos": "quinientos"}
for clave in ["retorno", "pasos", "semilla"]:
    print(f"Leyendo {clave}:")
    leer_dato(registro, clave)"""),

md(r"""Fíjate en que **"(fin de la lectura)" sale las tres veces**, incluso cuando la función salió con un `return` dentro de un `except`: el `finally` se ejecuta **pase lo
que pase**. Por eso es el sitio para el código de "limpieza" imprescindible.
"""),

md(r"""## 7 · Lanzar tus propias excepciones: `raise`

Las excepciones no son solo cosa de Python: **tú** puedes lanzarlas, con **`raise`**, cuando detectas que algo no tiene sentido. ¿Para qué? Para que un error se note
**pronto y con un mensaje claro**, en vez de que el programa siga con un dato absurdo y falle tres horas después de forma misteriosa.

Por ejemplo, una función que comprueba la configuración de un entrenamiento antes de empezar:
"""),

code(r"""def comprobar_configuracion(config):
    if config["tasa"] <= 0:
        raise ValueError(f"La tasa de aprendizaje debe ser positiva, y es {config['tasa']}")
    if config["pasos"] < 1:
        raise ValueError("Hay que entrenar al menos 1 paso")
    print("Configuración correcta")

comprobar_configuracion({"tasa": 0.0003, "pasos": 1000})"""),

md(r"""Con una configuración correcta, todo bien. Pero con una tasa negativa (una errata típica: escribir `-0.0003`)..."""),

code_err(r"""comprobar_configuracion({"tasa": -0.0003, "pasos": 1000})"""),

md(r"""...el programa se para **al instante**, con **nuestro** mensaje, que dice exactamente qué está mal. Sin esa comprobación, el entrenamiento habría arrancado, el robot
habría "aprendido" a empeorar (¡con la tasa negativa sube por la pendiente en vez de bajar, NB17!), y quizá habrías tardado horas en darte cuenta.

A esta filosofía se le llama **fallar pronto** (*fail fast*): **si algo está mal, que se note cuanto antes y lo más cerca posible de la causa.**
"""),

md(r"""## 8 · Detectar una explosión numérica

Un caso muy real. En el NB18 viste que con una tasa demasiado grande el entrenamiento **explota**: los números se disparan hasta tamaños absurdos. Y si siguen creciendo,
llega un momento en que el ordenador ya no puede representarlos, y aparecen dos valores especiales de los decimales:

- **`inf`** (infinito): un número demasiado grande.
- **`nan`** (de *Not a Number*, "no es un número"): el resultado de cuentas sin sentido, como infinito menos infinito.

Lo peor de `nan` es que **contagia**: cualquier cuenta con un `nan` da `nan`. Si un peso de tu red se vuelve `nan`, en el siguiente paso **todos** lo serán, y el robot se
volverá loco... sin ningún mensaje de error. Por eso, en los bucles de entrenamiento se **vigila**:
"""),

code(r"""import math

print(math.inf, math.inf - math.inf, math.nan + 1)
print(math.isfinite(455.3), math.isfinite(math.inf), math.isfinite(math.nan))"""),

md(r"""`math.isfinite(x)` es `True` solo si `x` es un número "normal" (ni infinito ni `nan`). Usémosla para vigilar un entrenamiento. Este es el descenso por gradiente del NB18
(en una versión mínima: una sola ruedecilla que tiene que llegar a −30) con una tasa **demasiado grande**, pero ahora con un **vigilante** que para el entrenamiento en
cuanto la pérdida deja de ser un número normal o se dispara:
"""),

code(r"""def entrenar(tasa, pasos=200):
    w = 0.0
    for paso in range(pasos):
        error = w - (-30)                  # queremos que w llegue a -30
        perdida = error ** 2
        if not math.isfinite(perdida) or perdida > 1e12:
            raise RuntimeError(f"El entrenamiento ha explotado en el paso {paso} "
                               f"(pérdida = {perdida:.3g}). Prueba con una tasa más pequeña.")
        w = w - tasa * 2 * error           # descenso por gradiente
    return w

print("Con tasa 0.1:", round(entrenar(0.1), 4))"""),

md(r"""(En `def entrenar(tasa, pasos=200)`, el `pasos=200` le da al parámetro un **valor por defecto**: si no se lo pasas, vale 200. Lo veremos a fondo en el NB23.)

Con tasa 0,1, llega a −30 sin problema. Ahora con una tasa de **1,5** (demasiado grande para este problema):"""),

code_err(r"""entrenar(1.5)"""),

md(r"""El vigilante ha parado el entrenamiento **en cuanto** la pérdida pasó de 10¹², con un mensaje que dice **qué** pasó, **cuándo** y **qué hacer**. (`RuntimeError`, "error en
tiempo de ejecución", es el tipo genérico para "algo ha ido mal mientras funcionaba". Y `:.3g` es otro código de formato, NB20: 3 cifras significativas, usando notación
científica si el número es muy grande o muy pequeño.)

Las bibliotecas profesionales hacen exactamente esto, y en tus propios entrenamientos **siempre** deberías vigilar que los números sigan siendo números.
"""),

md(r"""## 9 · `assert`: comprobaciones para ti mismo

**`assert`** ("afirmar") es una forma corta de decir "**esto tiene que ser cierto; si no lo es, para**". Se usa para comprobar **suposiciones** del propio código, sobre todo
mientras lo escribes:
"""),

code(r"""accion = [0.1, -0.3, 0.2]
assert len(accion) == 3, "la acción debería tener 3 números"
print("La acción tiene el tamaño correcto")"""),

md(r"""Si la condición es verdadera, no pasa nada. Si es falsa, salta un `AssertionError` con el mensaje (el texto que va tras la coma):"""),

code_err(r"""accion = [0.1, -0.3]
assert len(accion) == 3, f"la acción debería tener 3 números, y tiene {len(accion)}"
"""),

md(r"""**¿`assert` o `raise`?** Una regla práctica: `raise` para errores que **pueden pasar de verdad** cuando alguien usa tu código (una configuración mal escrita, un fichero que
falta); `assert` para **suposiciones internas** que, si fallan, significan que **tú** te has equivocado programando ("a esta altura, la lista nunca debería estar vacía"). Los
`assert` también son la base de los **tests**, que veremos en el NB27.
"""),

md(r"""## 10 · Depurar: el arte de encontrar el fallo

Los errores que **avisan** (las excepciones) son los fáciles: te dicen dónde están. Los difíciles son los **silenciosos**: el programa funciona, no da ningún error... pero el
resultado está **mal**. El robot no aprende, o el retorno es absurdo. A encontrar esos fallos se le llama **depurar** (en inglés, *debugging*: "quitar bichos", por una
anécdota famosa de los primeros ordenadores, en los que una vez se encontró una polilla de verdad atrapada entre los circuitos causando un fallo).

### El método

1. **Reprodúcelo.** Consigue que el fallo pase **siempre** (fija las semillas, NB11). Un fallo que aparece "a veces" es casi imposible de cazar.
2. **Lee el mensaje de error entero** (si lo hay), de abajo arriba.
3. **Aíslalo.** Haz el caso más pequeño posible que siga fallando: menos datos, menos pasos, una sola función. A menudo, al reducirlo, el fallo salta a la vista.
4. **Comprueba tus suposiciones**, una por una. "Esta lista **debería** tener 17 números" → compruébalo. "Esta variable **debería** ser positiva" → compruébalo. El fallo
   está, casi siempre, en algo que "seguro que está bien".
5. **Cambia una sola cosa cada vez**, y mira qué pasa.

Y un truco que sorprende por lo bien que funciona: **explícale el problema en voz alta a alguien** (o a un patito de goma, de ahí su nombre: *rubber duck debugging*). Al
explicar paso a paso lo que **debería** hacer el código, muchas veces te das cuenta tú solo de dónde no lo hace.
"""),

md(r"""### La herramienta número 1: `print` (con un truco)

La forma más usada de comprobar suposiciones es, simplemente, **mostrar** lo que valen las cosas en distintos puntos del programa. Y las f-strings tienen un truco
buenísimo para esto: si pones un **`=`** después del nombre, muestran **el nombre y el valor**:
"""),

code(r"""inclinacion = 2.0
velocidad = -1.27
empuje = -30 * inclinacion - 8 * velocidad
print(f"{inclinacion=}, {velocidad=}, {empuje=}")
print(f"{empuje=:.1f}")"""),

md(r"""`f"{empuje=}"` escribe `empuje=-49.84`. Ahorra mucho tiempo al depurar: no tienes que escribir el nombre dos veces. Y se puede combinar con un formato (`:.1f`).

Cuando depures arrays (NB15), lo primero que hay que mostrar casi siempre es su **forma**: `print(f"{x.shape=}")`. La mitad de los fallos con redes neuronales son tamaños que
no son los que crees.
"""),

md(r"""### El depurador

Además de `print`, Python trae un **depurador** (*debugger*): una herramienta que **detiene** el programa en un punto y te deja **mirar dentro**: ver el valor de cada variable,
avanzar línea a línea, ver quién llamó a quién... Dos formas de usarlo (no las ejecutamos aquí, porque necesitan que escribas tú las órdenes mientras el programa espera):

- **`breakpoint()`**: si escribes esta línea en cualquier sitio de tu código, el programa se **detendrá** ahí y te dejará escribir órdenes.
- **`%debug`**: en Jupyter, si una celda acaba de fallar, escribe `%debug` en una celda nueva y ejecútala: entrarás en el depurador **justo en el sitio del error**, con todas las
  variables tal y como estaban cuando falló. Es como poder viajar al momento del accidente.

Dentro del depurador se escriben órdenes cortas:

| Orden | Qué hace |
|---|---|
| `p variable` | Muestra (*print*) el valor de una variable |
| `n` | Ejecuta la siguiente línea (*next*) |
| `s` | Entra dentro de la función que se va a llamar (*step*) |
| `c` | Continúa hasta el siguiente punto de parada (*continue*) |
| `u` / `d` | Sube / baja por la pila de llamadas (*up* / *down*): mira las variables de quien llamó a la función |
| `q` | Sale del depurador (*quit*) |

Pruébalo tú: ejecuta la celda del apartado 5 (la de la traza larga), y luego una celda con `%debug`. Escribe `p observacion` para ver la observación, `u` para subir a `episodio`, y
`q` para salir. Es una herramienta que separa a los programadores que adivinan de los que **miran**.
"""),

md(r"""### Los bichos más comunes

Después de un tiempo programando, verás que los fallos se repiten. Aquí tienes los más típicos, casi todos ya conocidos:

| Bicho | Ejemplo | Síntoma |
|---|---|---|
| **Uno de más o de menos** (*off-by-one*) | `range(1, 10)` cuando querías hasta el 10 | Falta o sobra el último elemento |
| **Alias** (NB21) | `historial.append(estado)` sin `copy()` | Todo el historial sale igual |
| **Olvidar el `return`** (NB10) | La función calcula pero no devuelve | Aparece un `None` inesperado |
| **`sort` en vez de `sorted`** (NB21) | `x = x.sort()` | La lista se convierte en `None` |
| **Sangría equivocada** (NB07) | Un `print` dentro del bucle en vez de fuera | Sale mil veces, o una sola |
| **Formas que no encajan** (NB15) | Matriz 17×45 con observación de 348 | `ValueError` con *shapes* |
| **Hucha dentro del bucle** (NB07) | `total = 0` dentro del `for` | El total siempre es el último valor |
| **Signo cambiado** | `w + tasa * pendiente` para bajar (NB17-18) | La pérdida **sube** en vez de bajar |
| **Semilla sin fijar** (NB11) | Comparar políticas con vientos distintos | Resultados que cambian cada vez |
| **Un `except` demasiado amplio** (apartado 6) | `except:` a secas | Errores reales escondidos |
"""),

md(r"""## 11 · Resumen de la lección

1. **`while condición:`** repite mientras la condición sea cierta (pelota: 63 pasos hasta el suelo). Cuidado con el **bucle infinito**: pon un **límite de seguridad**; para
   pararlo, ■ / Kernel → Interrupt / Ctrl + C.
2. **`continue`** salta a la siguiente vuelta; **`for ... else`** ejecuta el `else` si no hubo `break`; **`pass`** = no hacer nada; **`match`/`case`** elige entre muchos casos.
   Son falsos: `0`, `""`, `None` y las colecciones vacías; `is None` para comparar con `None`.
3. Las **excepciones** interrumpen el programa. Una **traza** se lee **de abajo arriba**: qué pasó, dónde, y cómo se llegó ahí. **`try`/`except Tipo`** las captura (solo las que
   esperas); `as e`, varios `except`, `else` (si no hubo error) y `finally` (siempre).
4. **`raise`** lanza tus propias excepciones para **fallar pronto** con un mensaje claro. Vigila los entrenamientos con `math.isfinite` contra **`inf`** y **`nan`** (que
   contagia). **`assert`** comprueba suposiciones internas.
5. **Depurar**: reproducir, leer, aislar, comprobar suposiciones, cambiar una cosa cada vez. Herramientas: `print(f"{x=}")`, la forma de los arrays, el depurador (`breakpoint()`,
   `%debug`) y conocer los bichos típicos.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **`while`** | Bucle que repite mientras una condición sea cierta. |
| **Bucle infinito** | Un bucle que no termina nunca. |
| **`continue`** | Salta el resto de la vuelta y pasa a la siguiente. |
| **`pass`** | No hacer nada (relleno donde se exige un bloque). |
| **`match` / `case`** | Elegir qué hacer según el valor de algo, entre muchos casos. |
| **Excepción** | Aviso de error que interrumpe el programa. |
| **Traza (*traceback*)** | El camino de llamadas hasta un error; se lee de abajo arriba. |
| **`try` / `except` / `else` / `finally`** | Intentar algo, capturar sus errores, qué hacer si no los hubo, y qué hacer siempre. |
| **`raise`** | Lanzar una excepción. |
| **Fallar pronto** | Detectar los problemas cuanto antes, cerca de su causa. |
| **`inf` / `nan`** | Infinito / "no es un número": señales de una explosión numérica. |
| **`assert`** | Comprobar que algo es cierto; si no, `AssertionError`. |
| **Depurar** | Encontrar y arreglar fallos. |
| **Depurador** | Herramienta que detiene el programa para mirar dentro (`breakpoint()`, `%debug`). |
"""),

md(r"""## 12 · Ejercicios

**E1.** Con un `while`, calcula cuántas veces hay que dividir 1.000 entre 2 (quedándote con el resultado cada vez) hasta que el número sea menor que 1.

**E2.** ¿Qué tiene de malo este código? ¿Cómo lo arreglarías?

```python
pasos = 0
while pasos < 10:
    print(pasos)
```

**E3.** Recorre `[3, -1, 4, -1, 5]` y suma solo los positivos usando `continue`.

**E4.** Escribe una función `leer_retorno(texto)` que devuelva el texto convertido a `float`, o `None` (con un aviso) si no se puede convertir. Pruébala con `"455.3"`, `"abc"` y `""`.

**E5.** Escribe una función `comprobar_accion(accion)` que lance un `ValueError` con un mensaje claro si la acción no tiene **17** números, o si alguno se sale de ±0,4.

**E6.** Lee esta traza (inventada) e indica **qué** pasó y **en qué función** está el fallo:

```
Traceback (most recent call last)
Cell In[3], line 9
----> 9 entrenar(config)
Cell In[3], line 6, in entrenar(config)
----> 6     tasa = config["tasa_aprendizaje"]
KeyError: 'tasa_aprendizaje'
```

**E7.** **Encuentra los fallos.** Esta función debería devolver el retorno medio de una lista de episodios, ignorando los que no tengan retorno (`None`). Tiene **tres** fallos.
Encuéntralos sin ejecutarla y arréglala.

```python
def retorno_medio(retornos):
    total = 0
    for r in retornos:
        if r == None:
            continue
        total = 0
        total = total + r
    return total / len(retornos)
```
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
numero = 1000
veces = 0
while numero >= 1:
    numero = numero / 2
    veces = veces + 1
print(veces, numero)
```

Salen **10** divisiones (1000 → 500 → 250 → ... → 0,977). Es un caso típico de `while`: no sabías de antemano cuántas vueltas haría falta.
</details>

<details>
<summary>▶ Solución E2</summary>

Es un **bucle infinito**: `pasos` nunca cambia dentro del bucle, así que `pasos < 10` es siempre `True` y mostraría `0` para siempre. Se arregla actualizando la variable dentro:

```python
pasos = 0
while pasos < 10:
    print(pasos)
    pasos = pasos + 1
```

(Para algo así, en realidad, un `for pasos in range(10):` sería más claro y no tendría el riesgo.)
</details>

<details>
<summary>▶ Solución E3</summary>

```python
total = 0
for x in [3, -1, 4, -1, 5]:
    if x < 0:
        continue
    total = total + x
print(total)
```

Salida: **12** (3 + 4 + 5).
</details>

<details>
<summary>▶ Solución E4</summary>

```python
def leer_retorno(texto):
    try:
        return float(texto)
    except ValueError:
        print(f"Aviso: {texto!r} no es un número")
        return None

print(leer_retorno("455.3"), leer_retorno("abc"), leer_retorno(""))
```

Salen `455.3`, y dos avisos con `None` para `'abc'` y `''`.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
def comprobar_accion(accion):
    if len(accion) != 17:
        raise ValueError(f"La acción debe tener 17 números, y tiene {len(accion)}")
    for i, a in enumerate(accion):
        if a < -0.4 or a > 0.4:
            raise ValueError(f"La acción del motor {i} vale {a}, fuera de [-0.4, 0.4]")
```

Con `enumerate` (NB21), el mensaje dice **qué motor** está mal: un buen mensaje de error ahorra mucho tiempo a quien lo lee (que suele ser tu "yo" del futuro).
</details>

<details>
<summary>▶ Solución E6</summary>

Leyendo de abajo arriba: **qué** pasó, un `KeyError`: se pidió la clave `'tasa_aprendizaje'` y el diccionario no la tiene. **Dónde**: en la función `entrenar`, línea 6, al hacer
`config["tasa_aprendizaje"]`. **Cómo se llegó**: la celda llamó a `entrenar(config)` en su línea 9. Lo más probable: la configuración usa otro nombre para esa clave (por ejemplo,
`"tasa"`), o se olvidó ponerla. Habría que mirar qué claves tiene `config` (por ejemplo, con `print(config.keys())`).
</details>

<details>
<summary>▶ Solución E7</summary>

Los tres fallos:

1. **`total = 0` dentro del bucle** (la hucha del NB07): vacía la suma en cada vuelta, así que al final `total` solo tiene el último retorno. Hay que quitar esa línea.
2. **Divide entre `len(retornos)`**, que **incluye** los `None` que se han saltado. Hay que dividir entre el número de retornos **válidos**.
3. (De estilo, pero importante) **`r == None`** debería ser **`r is None`** (apartado 4).

Arreglada:

```python
def retorno_medio(retornos):
    total = 0
    validos = 0
    for r in retornos:
        if r is None:
            continue
        total = total + r
        validos = validos + 1
    return total / validos

print(retorno_medio([400.0, None, 500.0]))      # 450.0
```

(Y un cuarto fallo "escondido": si **todos** son `None`, `validos` es 0 y saltaría un `ZeroDivisionError`. Se podría comprobar al principio y lanzar un error claro con `raise`, o
devolver `None`.)
</details>
"""),

md(r"""## 13 · 🛠 Práctica en MuJoCo: rompe MuJoCo a propósito (y atrapa sus errores)

Hasta ahora, en todas las prácticas MuJoCo ha funcionado a la primera. En la vida real no es así: escribirás planos con erratas, elegirás
pasos de tiempo demasiado grandes y verás simulaciones que **explotan**. Hoy vas a provocar todo eso **a propósito**, en un sitio seguro,
para reconocerlo cuando te pase de verdad.

Hay dos familias de errores en MuJoCo, y se comportan de forma muy distinta:

1. **Errores al cargar** (un plano mal escrito): MuJoCo **se queja en voz alta** con una excepción. Fácil: lo has aprendido hoy.
2. **Errores al simular** (la física se vuelve loca): MuJoCo **no lanza ninguna excepción**. Lo arregla "a su manera" y sigue como si nada.
   Este es el peligroso, y tendrás que construirte un **vigilante** como el del apartado 8.
"""),

md(r"""### Paso 1 · Un plano con una errata

Este plano de una pelota tiene un fallo típico: se abre `<body>` y **nunca se cierra** (falta `</body>`). Intentamos cargarlo directamente
con MuJoCo:
"""),

code(r"""import mujoco
import numpy as np
import taller

ROTO = '''
<mujoco>
  <worldbody>
    <body name="pelota" pos="0 0 1">
      <freejoint/>
      <geom type="sphere" size="0.1"/>
  </worldbody>
</mujoco>
'''"""),

code_err(r"""modelo = mujoco.MjModel.from_xml_string(ROTO)"""),

md(r"""Lee la traza **de abajo arriba** (apartado 5). La última línea es la importante: **`ValueError: XML parse error 14`** y, debajo,
`XML_ERROR_MISMATCHED_ELEMENT ... XMLElement name=body`: "error leyendo el XML: **elemento que no casa**, el `body`". Es decir: has abierto
un `body` y lo que viene después no encaja. MuJoCo te dice incluso el **tipo** de excepción: un `ValueError`, el mismo que `float("hola")`
(NB20): "el tipo está bien (es texto), pero el valor no tiene sentido".
"""),

md(r"""### Paso 2 · Atrapar el error con `try` / `except`

Como sabemos qué excepción lanza MuJoCo, podemos **capturarla** (apartado 6), avisar con un mensaje claro y seguir. Usamos `as e` para
leer el mensaje, y nos quedamos solo con su **primera línea** con `split` (NB20):
"""),

code(r"""try:
    modelo = mujoco.MjModel.from_xml_string(ROTO)
except ValueError as e:
    print("MuJoCo no ha podido leer el plano.")
    print("Motivo:", str(e).split("\n")[0])"""),

md(r"""Ahora, un **catálogo de erratas**. Un diccionario (NB21) con cuatro planos rotos de cuatro formas distintas, y un bucle que intenta cargar
cada uno. El `else` del `try` se ejecuta solo si **no** hubo error. Fíjate en que las erratas 2, 3 y 4 son **una sola palabra** mal escrita:
"""),

code(r"""erratas = {
    "sin cerrar":         ROTO,
    "etiqueta mal":       '<mujoco><worldbody><bodi/></worldbody></mujoco>',
    "número en letras":   '<mujoco><worldbody><geom type="sphere" size="dos"/></worldbody></mujoco>',
    "forma inventada":    '<mujoco><worldbody><geom type="esfera" size="1"/></worldbody></mujoco>',
}

for nombre, plano in erratas.items():
    try:
        mujoco.MjModel.from_xml_string(plano)
    except ValueError as e:
        lineas = str(e).strip().split("\n")
        print(f"{nombre:>17}: {lineas[0]}  ({lineas[-1].strip()})")
    else:
        print(f"{nombre:>17}: se ha cargado bien")"""),

md(r"""MuJoCo es un buen chivato: para cada errata dice **qué** está mal y **dónde** (en qué elemento y en qué línea del plano):

- `<bodi/>` → *unrecognized element*: "elemento desconocido" (no existe la etiqueta `bodi`).
- `size="dos"` → *bad format in attribute 'size'*: "formato malo en el atributo `size`" (esperaba números).
- `type="esfera"` → *invalid keyword: 'esfera'*: "palabra no válida" (MuJoCo habla inglés: `sphere`).

Ese **"y en qué línea"** es oro cuando el plano tiene 300 líneas, como el del humanoide.
"""),

md(r"""### Paso 3 · Una simulación que explota

Ahora el error peligroso. Este plano es un **palo de medio metro sobre una bisagra con muelle**: el atributo `stiffness="10000"`
("rigidez") pone en la bisagra un muelle **durísimo** que empuja el palo hacia la vertical, como el muelle de un tentetieso. Lo inclinamos
0,3 radianes (unos 17°) y lo soltamos. Debería vibrar muy deprisa alrededor de la vertical.
"""),

code(r"""MUELLE = '''
<mujoco>
  <option timestep="0.01"/>
  <worldbody>
    <light pos="0 0 4"/>
    <geom type="plane" size="4 4 0.1"/>
    <body name="palo" pos="0 0 1">
      <joint name="bisagra" type="hinge" axis="0 1 0" stiffness="10000"/>
      <geom type="capsule" fromto="0 0 0 0 0 0.5" size="0.03" mass="0.5"/>
    </body>
  </worldbody>
</mujoco>
'''
modelo, datos = taller.cargar(MUELLE)
datos.qpos[0] = 0.3
print("paso   reloj      ángulo (rad)")
for paso in range(7):
    mujoco.mj_step(modelo, datos)
    print(f"{paso:>4}   {datos.time:5.2f}   {datos.qpos[0]:>14.2f}")"""),

md(r"""Mira la columna del ángulo: 0,3 → **−6,59** → **137,89** → **−2.884,93** → **60.357,98** radianes... ¡En el cuarto paso el palo ha
girado **diez mil vueltas**! En cada paso el ángulo se multiplica por unas **−20**: cambia de lado y crece. Es **exactamente** la
explosión del apartado 8 (y del NB18), con otro disfraz.

¿Por qué? Un muelle tan duro hace vibrar el palo unas **77 veces por segundo** (lo he medido con pasos diminutos): una vibración completa
dura 0,013 segundos. Y nuestro paso es de **0,01**: MuJoCo solo "mira" el palo una vez por vibración. Con la cadena de oro del NB02 (la
fuerza cambia la velocidad y la velocidad cambia la posición), cada paso **se pasa de frenada**, cada vez más. Igual que la tasa de
aprendizaje demasiado grande del NB18: **paso demasiado grande = explosión**.

Ahora mira las tres últimas filas: el reloj ha vuelto a **0,01** y el ángulo a **0,00**. ¿Qué ha pasado?
"""),

md(r"""### Paso 4 · El vigilante de MuJoCo (y por qué no basta)

MuJoCo lleva dentro su propio vigilante, como el del apartado 8. Cuando ve un número **infinito, `nan` o enorme** (más de diez mil
millones) en las posiciones, velocidades o aceleraciones, hace dos cosas:

1. **Reinicia la simulación** al estado inicial (reloj a 0, piezas en su sitio). Por eso el reloj ha vuelto atrás.
2. Apunta un **aviso** (*warning*): escribe una línea `WARNING: Nan, Inf or huge value in QACC... The simulation is unstable` ("valor
   `nan`, infinito o enorme en la aceleración: la simulación es inestable"), que seguramente ves debajo de la tabla; la copia en el fichero
   `MUJOCO_LOG.TXT`; y suma 1 a un contador dentro de `datos.warning`.

Lo que **no** hace es lanzar una excepción. Tu **programa** no se entera de nada y sigue tan tranquilo. Y esa línea de aviso, en un
entrenamiento de horas que escribe miles de líneas, pasa desapercibida: estarías entrenando un robot en un mundo que se reinicia solo
cada cuatro pasos. Miremos esos contadores. Hay uno por tipo de aviso; los que nos interesan son tres,
los de "valor malo" en posición (`QPOS`), velocidad (`QVEL`) y aceleración (`QACC`):
"""),

code(r"""MALOS = [mujoco.mjtWarning.mjWARN_BADQPOS,
         mujoco.mjtWarning.mjWARN_BADQVEL,
         mujoco.mjtWarning.mjWARN_BADQACC]

for tipo in MALOS:
    print(f"{tipo.name:<16} -> {datos.warning[tipo].number} aviso(s)")"""),

md(r"""Ahí está la huella: un aviso de **aceleración mala** (`BADQACC`). Con esto ya podemos escribir **nuestro** vigilante, que convierta ese
aviso silencioso en una excepción con un buen mensaje (apartado 7: **fallar pronto**):
"""),

code(r"""def comprobar(datos):
    for tipo in MALOS:
        if datos.warning[tipo].number > 0:
            raise RuntimeError(f"La simulación ha explotado ({tipo.name}) "
                               f"con paso de {modelo.opt.timestep} s. Prueba un paso más pequeño.")"""),

md(r"""### Paso 5 · Un bucle `while` vigilado

Ahora simulamos **mientras** el reloj no llegue a 1 segundo (`while`, apartado 1), comprobando después de cada paso. Pero ojo: acabamos de
ver que MuJoCo **pone el reloj a 0** cuando explota. Si la simulación explotara cada cuatro pasos sin que nadie lo comprobara, el reloj nunca
llegaría a 1 y el `while` sería un **bucle infinito**. Por eso, además del vigilante, le ponemos un **límite de seguridad** de pasos (apartado 1):
"""),

code(r"""def simular_vigilado(modelo, datos, segundos, limite=100_000):
    pasos = 0
    while datos.time < segundos:
        mujoco.mj_step(modelo, datos)
        comprobar(datos)
        pasos += 1
        if pasos >= limite:
            raise RuntimeError("Demasiados pasos: ¿el reloj está volviendo atrás?")
    return pasos"""),

md(r"""Y la usamos para **buscar un paso que funcione**: probamos pasos cada vez más pequeños, capturamos la explosión con `try/except`, y en cuanto
uno va bien, `break`. El `else` del `for` (apartado 3) solo saltaría si **ninguno** funcionara:
"""),

code(r"""for paso in [0.01, 0.005, 0.002, 0.001]:
    modelo, datos = taller.cargar(MUELLE)
    modelo.opt.timestep = paso
    datos.qpos[0] = 0.3
    try:
        n = simular_vigilado(modelo, datos, segundos=1)
    except RuntimeError as e:
        print("✗", e)
    else:
        print(f"✓ Con paso de {paso} s: 1 segundo simulado en {n} pasos, sin explotar.")
        print(f"  Ángulo final: {datos.qpos[0]:.3f} rad")
        break
else:
    print("Ningún paso ha funcionado.")"""),

md(r"""Con 0,01 y con 0,005 explota (con 0,005 MuJoCo mira el palo dos veces y media por vibración: todavía poco). Con **0,002** (unas seis
miradas por vibración) ya va bien: el palo vibra alrededor de la vertical, como debe.

La regla de oro que te llevas: **el paso de tiempo tiene que ser bastante más pequeño que lo más rápido que pase en tu robot.** Un muelle
duro, un motor muy fuerte o un choque violento piden pasos pequeños.
"""),

md(r"""### Paso 6 · Así se ve una explosión

Ahora el humanoide, que normalmente usa pasos de 0,003 s, con un paso **casi siete veces más grande**, 0,02 s, y los motores al azar (NB00).
Mira el vídeo con atención:
"""),

code(r"""modelo, datos = taller.cargar("humanoide")
print("Paso normal del humanoide:", modelo.opt.timestep, "s")
modelo.opt.timestep = 0.02
taller.video(modelo, datos, segundos=2, control=taller.al_azar(0), nombre="nb22_explota");"""),

md(r"""El humanoide da **tirones** y vuelve una y otra vez a la postura inicial, como un vídeo rayado, y algún fotograma sale vacío (cuando el robot
está en las posiciones absurdas justo antes del reinicio). Cada "vuelta atrás" es una explosión y un reinicio de MuJoCo. Contémoslos con el
vigilante, capturando la excepción cada vez y siguiendo (`continue`, apartado 2):
"""),

code(r"""modelo, datos = taller.cargar("humanoide")
modelo.opt.timestep = 0.02
control = taller.al_azar(0)
explosiones = 0
for paso in range(100):                 # 100 pasos de 0,02 s = 2 segundos
    control(modelo, datos)
    mujoco.mj_step(modelo, datos)
    try:
        comprobar(datos)
    except RuntimeError:
        explosiones += 1
        datos.warning[mujoco.mjtWarning.mjWARN_BADQACC].number = 0   # bajamos las banderas
        datos.warning[mujoco.mjtWarning.mjWARN_BADQVEL].number = 0
        datos.warning[mujoco.mjtWarning.mjWARN_BADQPOS].number = 0
        continue
print(f"En 2 segundos simulados: {explosiones} explosiones, o sea, {explosiones} reinicios")"""),

md(r"""**22** explosiones en dos segundos (una cada 0,09 s, más o menos): la simulación no llega a vivir ni cinco pasos seguidos. (Verás también
un montón de líneas `WARNING`: los gritos de MuJoCo, uno por explosión.) Si estuvieras
entrenando, tu robot aprendería en un mundo roto... y sin un solo mensaje de error en pantalla. Por eso, en cualquier simulación tuya, **vigila
los avisos**.

### Tus retos

**Reto 1.** En el catálogo de erratas, añade una quinta: un plano donde la pelota tenga `size="-0.1"` (radio negativo). ¿Se queja MuJoCo?
¿Qué te dice eso sobre lo que MuJoCo comprueba y lo que no?

**Reto 2.** Escribe una función `cargar_seguro(plano)` que devuelva `(modelo, datos)` si el plano está bien, y `None` (NB10) si está mal,
avisando con la primera línea del mensaje. Pruébala con `ROTO` y con `MUELLE`.

**Reto 3.** En el Paso 5, cambia la rigidez del muelle de 10000 a **100** (con `MUELLE.replace(...)`, NB20). ¿Sigue explotando con paso 0,01?
¿Por qué?

<details>
<summary>▶ Solución Reto 1</summary>

```python
erratas["radio negativo"] = '<mujoco><worldbody><geom type="sphere" size="-0.1"/></worldbody></mujoco>'
```

**Sí** se queja: `Error: size 0 must be positive in geom`, "el tamaño 0 (el primero, el radio) debe ser positivo en la forma". MuJoCo no solo revisa que el
texto esté bien escrito; también comprueba que algunos números tengan **sentido físico**. Pero no puede comprobarlo todo: un `timestep`
demasiado grande, como en el Paso 3, se acepta sin rechistar, porque solo se sabe que es malo **al simular**.
</details>

<details>
<summary>▶ Solución Reto 2</summary>

```python
def cargar_seguro(plano):
    try:
        modelo, datos = taller.cargar(plano)
    except ValueError as e:
        print("Plano roto:", str(e).split("\n")[0])
        return None
    return modelo, datos

print(cargar_seguro(ROTO))          # avisa y devuelve None
print(cargar_seguro(MUELLE))        # devuelve la pareja (modelo, datos)
```

Quien llame a `cargar_seguro` tendrá que comprobar `if resultado is None:` (apartado 4) antes de usarlo.
</details>

<details>
<summary>▶ Solución Reto 3</summary>

```python
modelo, datos = taller.cargar(MUELLE.replace('stiffness="10000"', 'stiffness="100"'))
datos.qpos[0] = 0.3
print(simular_vigilado(modelo, datos, segundos=1))     # 100 pasos, sin explotar
```

**Ya no explota.** Un muelle 100 veces más blando vibra 10 veces más despacio (unas 7,5 veces por segundo): ahora el paso de 0,01 s mira el
palo más de trece veces por vibración, de sobra. No es que el paso sea "bueno" o "malo" en sí: es bueno o malo **comparado con lo rápido que
pasan las cosas** en tu robot.
</details>

### Qué has aprendido de MuJoCo hoy

- Un plano mal escrito hace que `MjModel.from_xml_string` lance un **`ValueError`** que dice **qué** falla y **en qué línea**. Se captura con
  `try/except ValueError as e`.
- MuJoCo también comprueba algunas cosas con sentido físico (tamaños positivos), pero no puede saber si tu **paso de tiempo** es bueno hasta simular.
- Con un paso demasiado grande para lo rápido que pasan las cosas (muelles duros, motores fuertes), la simulación **explota**, como un descenso
  por gradiente con tasa demasiado grande.
- Cuando explota, MuJoCo **no lanza una excepción**: **reinicia** la simulación en silencio y apunta un aviso en **`datos.warning`**
  (`mjWARN_BADQPOS`, `mjWARN_BADQVEL`, `mjWARN_BADQACC`) y en `MUJOCO_LOG.TXT`.
- Un buen bucle de simulación lleva un **vigilante** que convierte esos avisos en excepciones y un **límite de seguridad** de pasos.

En la práctica del NB23 abrirás por fin la caja negra: leerás `taller.py`, el fichero que has usado desde el NB00, y escribirás tu propia versión
de sus funciones.
"""),

md(r"""## 14 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has aprendido a controlar los bucles con precisión y, sobre todo, a convivir con los errores: leerlos, capturarlos, lanzarlos y cazarlos (también los de MuJoCo, que no siempre avisan). Es, de verdad, la mitad del oficio.
En el **NB23** vamos a por las **funciones a fondo**: parámetros con valores por defecto, `*args` y `**kwargs`, las `lambda`, funciones que fabrican funciones (con las que crearemos
una "fábrica de políticas"), **decoradores** (como un cronómetro que se le pone a cualquier función) y **generadores**, la forma de producir datos uno a uno sin llenar la memoria.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB22_python_errores.ipynb")
    build(out, cells, title="NB22 · Python de verdad (3): control de flujo, errores y depuración")
