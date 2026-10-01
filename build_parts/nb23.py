"""Construye NB23 · Python de verdad (4): funciones a fondo.

Valores por defecto y argumentos por nombre; la trampa del valor por defecto
mutable (historial=[]) y su arreglo con None; *args y **kwargs, y desempaquetar
al llamar (f(*lista), f(**dicc)); ámbito local/global, UnboundLocalError real,
global (y por qué evitarlo); funciones como objetos; lambda (sorted con key);
cierres: la fábrica de políticas crear_politica(k, d) (sustituye el truco de
cajas globales del NB11) evaluada en el palo de escoba; decoradores (@cronometro,
functools.wraps); recursión (mostrar una configuración anidada); iteradores
(iter/next, StopIteration real) y generadores (yield, lotes de datos, expresión
generadora y memoria con sys.getsizeof); docstrings (help) y anotaciones de tipo.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB23 · Python de verdad (4): funciones a fondo

**Parte 3 · Python de verdad — Lección 4**

> En el **NB10** aprendiste lo esencial de las funciones: `def`, parámetros, `return`. Con eso has escrito políticas, entornos,
> funciones de recompensa y hasta la retropropagación de una red. Hoy vamos a ver **todo lo demás** que puede hacer una función,
> que es muchísimo, y que verás constantemente en el código profesional.

Esta lección tiene bastantes ideas nuevas, pero todas siguen la misma lógica: **las funciones son piezas que se pueden configurar,
combinar, pasar de mano en mano y hasta fabricar**. Veremos:

- Parámetros con **valor por defecto**, por **nombre**, y en cantidad variable (`*args`, `**kwargs`).
- Dónde "vive" cada variable (el **ámbito**).
- Funciones de una línea (**`lambda`**), funciones que **fabrican funciones** (**cierres**) y funciones que **envuelven** a otras
  (**decoradores**).
- **Generadores**: funciones que producen datos **de uno en uno**, sin llenar la memoria.
- Y cómo **documentar** una función para que otros (y tu "yo" del futuro) la entiendan.

Con los cierres, por cierto, arreglaremos algo que quedó un poco feo en el NB11.
"""),

md(r"""## 1 · Valores por defecto

Ya lo viste de pasada en el NB22: un parámetro puede tener un **valor por defecto**, que se usa si quien llama a la función **no** se lo
da. Se escribe con `=` en la definición:
"""),

code(r"""def describir_episodio(retorno, pasos=500, entorno="palo de escoba"):
    return f"{entorno}: {retorno:.1f} puntos en {pasos} pasos"

print(describir_episodio(455.3))
print(describir_episodio(213.5, 231))
print(describir_episodio(198.6, 40, "Humanoid-v5"))"""),

md(r"""La primera llamada solo da el retorno: `pasos` y `entorno` usan sus valores por defecto. La segunda da también los pasos. La tercera, los tres.
Así, las funciones tienen un **comportamiento normal** sencillo de usar, y **se pueden ajustar** cuando hace falta. (Regla: los parámetros con
valor por defecto van **después** de los que no lo tienen.)

## 2 · Argumentos por nombre

Al llamar a una función, puedes decir **a qué parámetro** va cada valor, con su nombre (ya lo hiciste en el NB16 con `pendiente(funcion=f, x=3, h=h)`).
Así puedes **saltarte** parámetros intermedios y cambiar el orden:
"""),

code(r"""print(describir_episodio(300.0, entorno="Walker2d-v5"))
print(describir_episodio(pasos=104, retorno=97.2))"""),

md(r"""En la primera, cambiamos el entorno **sin tocar** los pasos. En la segunda, el orden da igual porque cada valor lleva su nombre. En el código
profesional verás muchísimas llamadas así, porque **se leen solas**: `gym.make("Humanoid-v5", render_mode="rgb_array")` es mucho más claro que con
el valor a secas.
"""),

md(r"""## 3 · La trampa del valor por defecto mutable

Una trampa famosa, que mezcla los valores por defecto con el **alias** del NB21. Mira esta función, que añade un retorno a un historial (que, si no
le das uno, empieza vacío... o eso parece):
"""),

code(r"""def apuntar(retorno, historial=[]):
    historial.append(retorno)
    return historial

print(apuntar(44.8))
print(apuntar(97.2))"""),

md(r"""¡¿La segunda llamada tiene **también** el 44,8?! Esperábamos `[97.2]`.

El motivo: el valor por defecto `[]` se crea **una sola vez**, cuando se **define** la función, no cada vez que se llama. Así que todas las llamadas que
no dan su propio historial **comparten la misma lista**, que va acumulando todo. Es el alias del NB21, escondido en una definición.

**El arreglo estándar**: usar `None` como valor por defecto, y crear la lista **dentro**:
"""),

code(r"""def apuntar(retorno, historial=None):
    if historial is None:
        historial = []          # una lista NUEVA en cada llamada
    historial.append(retorno)
    return historial

print(apuntar(44.8))
print(apuntar(97.2))"""),

md(r"""Ahora sí. **Regla de oro: nunca uses una lista o un diccionario como valor por defecto.** Usa `None` y créalos dentro. (Números, textos, tuplas y
`None` sí son seguros, porque son inmutables.)
"""),

md(r"""## 4 · Cualquier número de argumentos: `*args`

A veces quieres una función que acepte **cuantos valores le den**, como `print`, que acepta uno, dos o veinte. Se consigue poniendo un **asterisco**
delante de un parámetro: recogerá **todos** los argumentos sobrantes en una **tupla** (NB21). Por costumbre se llama `args`:
"""),

code(r"""def media(*valores):
    print("He recibido:", valores)
    return sum(valores) / len(valores)

print(media(4, 6))
print(media(44.8, 97.2, 213.5, 455.3))"""),

md(r"""`valores` es una tupla con todo lo que se le pasó. La misma función sirve para dos números o para cien.

## 5 · Cualquier número de argumentos con nombre: `**kwargs`

Con **dos** asteriscos, el parámetro recoge todos los argumentos **con nombre** sobrantes en un **diccionario** (NB21). Por costumbre se llama `kwargs`
(de *keyword arguments*, "argumentos con nombre"). Es la forma típica de aceptar **opciones de configuración** que no sabes de antemano:
"""),

code(r"""def crear_configuracion(entorno, **opciones):
    configuracion = {"entorno": entorno, "tasa": 0.0003, "semillas": 5}   # valores normales
    configuracion.update(opciones)                                         # las opciones mandan
    return configuracion

print(crear_configuracion("Humanoid-v5"))
print(crear_configuracion("Walker2d-v5", tasa=0.001, red=[64, 64]))"""),

md(r"""(`update` mete en un diccionario todas las parejas de otro, sustituyendo las que ya estuvieran.) La segunda llamada cambia la tasa y añade una opción
nueva, `red`, que la función ni siquiera conocía.

## 6 · Desempaquetar al llamar

Y al revés: si **ya tienes** los valores en una lista o un diccionario, puedes **repartirlos** entre los parámetros al llamar, con `*` y `**`:
"""),

code(r"""def describir(retorno, pasos, entorno):
    return f"{entorno}: {retorno} en {pasos} pasos"

datos = [455.3, 500, "palo"]
opciones = {"retorno": 198.6, "pasos": 40, "entorno": "Humanoid"}

print(describir(*datos))         # = describir(455.3, 500, "palo")
print(describir(**opciones))     # = describir(retorno=198.6, pasos=40, entorno="Humanoid")"""),

md(r"""Esto lo verás muchísimo: por ejemplo, guardar los ajustes de un entorno en un diccionario y crearlo con `gym.make("Humanoid-v5", **ajustes)`. Toda la
configuración de un experimento en un solo diccionario, repartida automáticamente.
"""),

md(r"""## 7 · ¿Dónde vive cada variable? El ámbito

En el NB10 viste que las variables creadas **dentro** de una función son **locales**: desaparecen al terminar. Y en el NB11, que una función puede **leer**
variables de fuera. Al sitio donde "vive" una variable se le llama su **ámbito**. Hay una regla que provoca un error muy desconcertante. Mira:
"""),

code_err(r"""contador = 0

def contar_episodio():
    contador = contador + 1
    return contador

contar_episodio()"""),

md(r"""`UnboundLocalError: cannot access local variable 'contador' where it is not associated with a value`: "no se puede usar la variable **local** `contador`
porque aún no tiene valor". ¿Local? ¡Si `contador` es de fuera!

La regla es esta: **si dentro de una función hay una asignación (`contador = ...`), Python decide que esa variable es local en TODA la función**. Así que,
al calcular `contador + 1`, busca la `contador` **local**... que aún no existe. Leer una variable de fuera está bien; **asignarle** un valor la convierte en
local.

Existe la palabra **`global`** para decirle a Python "esta variable es la de fuera" (`global contador` al principio de la función), pero **casi nunca deberías
usarla**: las funciones que cambian variables de fuera son difíciles de entender y de depurar (no sabes quién cambió qué). La forma limpia: **recibir lo que
necesites por parámetro y devolver el resultado con `return`**:
"""),

code(r"""def contar_episodio(contador):
    return contador + 1

contador = 0
contador = contar_episodio(contador)
contador = contar_episodio(contador)
print(contador)"""),

md(r"""## 8 · Las funciones son objetos

En Python, una función es un **objeto como cualquier otro**: se puede guardar en una variable, meter en una lista, pasar como argumento (lo hiciste en el NB10
con la política, y en el NB16 con `pendiente`) y **devolver** desde otra función. Por ejemplo, una lista de políticas para probarlas todas:
"""),

code(r"""def nada(inclinacion, velocidad):
    return 0

def a_mano(inclinacion, velocidad):
    return -30 * inclinacion - 8 * velocidad

politicas = [nada, a_mano]
for politica in politicas:
    print(politica.__name__, "->", politica(2.0, 0.0))"""),

md(r"""(`politica.__name__` es el **nombre** de la función: las funciones, como objetos, tienen datos propios. Los nombres con dos guiones bajos delante y detrás son
"especiales" de Python; verás muchos en el NB24.)

## 9 · Funciones de una línea: `lambda`

Para funciones muy cortas y de **usar y tirar** (como la `su_retorno` que usamos en el NB21 para ordenar), Python tiene una forma abreviada: **`lambda`**. Se
escribe `lambda parámetros: resultado`, en una sola línea, sin `def`, sin nombre y sin `return`:
"""),

code(r"""cuadrado = lambda x: x ** 2
print(cuadrado(5))

politicas = [("nada", 44.8), ("a mano", 499.9), ("azar", 43.2)]
print(sorted(politicas, key=lambda pareja: pareja[1]))"""),

md(r"""La segunda línea es el uso típico de verdad: ordenar por el segundo elemento **sin tener que definir** una función aparte (compara con el NB21). **Usa `lambda`
solo para cosas cortitas**; si necesitas más de una expresión, escribe una función normal con `def` (y su nombre ayudará a entender el código).
"""),

md(r"""## 10 · Funciones que fabrican funciones: los cierres

Ahora una de las ideas más bonitas de la lección. Una función puede **crear otra función dentro** y **devolverla**. Y la función de dentro **recuerda** los
valores que tenía la de fuera cuando la creó.

¿Te acuerdas del NB11? Para probar ruedecillas distintas, tuvimos que guardarlas en **cajas de fuera** (`ruedecilla_inclinacion`, `ruedecilla_velocidad`) y que la
política las leyera. Funcionaba, pero era frágil (justo lo que el apartado 7 desaconseja). Con una **fábrica de políticas** queda limpísimo:
"""),

code(r"""def crear_politica(k, d):
    def politica(inclinacion, velocidad):
        return -k * inclinacion - d * velocidad      # usa los k y d de la fábrica
    return politica                                  # ¡devuelve la función, sin llamarla!

suave = crear_politica(15, 3)
fuerte = crear_politica(45, 12)

print("suave: ", suave(2.0, 0.0))
print("fuerte:", fuerte(2.0, 0.0))"""),

md(r"""`crear_politica(15, 3)` **fabrica** una política que lleva "pegados" el 15 y el 3; `crear_politica(45, 12)`, otra con sus propios números. Cada política **recuerda**
sus ruedecillas, aunque la fábrica ya haya terminado. A una función que recuerda variables del sitio donde se creó se le llama **cierre** (*closure*).

Probemos la fábrica con el palo de escoba del NB11, en versión compacta (la física de siempre). Ahora buscar ruedecillas es tan fácil como fabricar políticas y
evaluarlas, sin ninguna caja global:
"""),

code(r"""import random

def evaluar(politica, semillas=range(5)):
    total = 0
    for semilla in semillas:
        random.seed(semilla)
        inclinacion, velocidad = 2.0, 0.0
        for paso in range(500):
            empuje = max(-40, min(40, politica(inclinacion, velocidad)))
            aceleracion = 10 * inclinacion + empuje + random.uniform(-30, 30)
            velocidad = velocidad + aceleracion * 0.02
            inclinacion = inclinacion + velocidad * 0.02
            if abs(inclinacion) > 30:
                break
            total = total + 1 - (inclinacion / 30) ** 2
    return total / len(semillas)

for k, d in [(8, 8), (30, 0), (30, 8)]:
    print(f"ruedecillas ({k}, {d}): {evaluar(crear_politica(k, d)):.1f}")"""),

md(r"""(`abs(x)` es el **valor absoluto**, la versión de Python de `np.abs` del NB19: `abs(inclinacion) > 30` dice "inclinado más de 30 grados hacia cualquier lado". Y
fíjate en `semillas=range(5)` como valor por defecto: es seguro, porque un `range` no se puede modificar, al contrario que una lista.)

Los mismos resultados del NB11 (182 con 8 y 8, que no vence a la gravedad; 296 con 30 y 0; 499,9 con 30 y 8), pero con un código mucho más limpio. Las fábricas
de funciones son muy comunes en el código de aprendizaje por refuerzo (por ejemplo, para fabricar entornos con distintas configuraciones).
"""),

md(r"""## 11 · Decoradores: envolver una función

Un **decorador** es una función que **recibe una función y devuelve otra versión de ella, "envuelta"** con algo extra, sin tocar su código. Es como ponerle una
funda a un móvil: el móvil sigue siendo el mismo, pero ahora además tiene protección.

Un ejemplo muy útil: un **cronómetro**, que mide cuánto tarda **cualquier** función que envuelva:
"""),

code(r"""import time
import functools

def cronometro(funcion):
    @functools.wraps(funcion)                    # (detalle: conserva el nombre de la original)
    def envuelta(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)     # llama a la función original, con lo que le den
        duracion = time.perf_counter() - inicio
        print(f"[{funcion.__name__} tardó {duracion * 1000:.1f} ms]")
        return resultado
    return envuelta"""),

md(r"""Fíjate en cómo usa todo lo de hoy: es una **fábrica** (apartado 10) que crea `envuelta`, que acepta **cualquier** argumento con `*args, **kwargs` (apartados 4-5) y
se los **pasa** a la original desempaquetados (apartado 6). Y para aplicarlo, Python tiene un símbolo especial, la **arroba `@`**, que se pone encima del `def`:
"""),

code(r"""@cronometro
def evaluar_a_mano():
    return evaluar(crear_politica(30, 8))

print(f"Retorno: {evaluar_a_mano():.1f}")"""),

md(r"""Al llamar a `evaluar_a_mano()`, primero se mide el tiempo, luego se ejecuta, y se muestra cuánto tardó, **sin haber tocado su código**. Poner `@cronometro` encima
del `def` es exactamente lo mismo que escribir, después de definirla, `evaluar_a_mano = cronometro(evaluar_a_mano)`.

**Verás decoradores por todas partes** en el código profesional: `@torch.no_grad()` en PyTorch (para no calcular pendientes cuando no hacen falta), `@property` y
`@dataclass` en las clases (NB24-25), `@pytest.fixture` en los tests (NB27)... Ahora sabes que todos son lo mismo: funciones que envuelven funciones.
"""),

md(r"""## 12 · Funciones que se llaman a sí mismas: la recursión

Una función puede **llamarse a sí misma**. Se llama **recursión**, y es la forma natural de recorrer estructuras que tienen **otras estructuras iguales dentro**, como
la configuración anidada del NB21 (diccionarios dentro de diccionarios dentro de diccionarios...).

Por ejemplo, una función que muestra una configuración con sangría, entre al nivel que entre: si un valor es otro diccionario, **se llama a sí misma** para mostrarlo,
con más sangría:
"""),

code(r"""def mostrar(configuracion, nivel=0):
    for clave, valor in configuracion.items():
        if isinstance(valor, dict):
            print("    " * nivel + f"{clave}:")
            mostrar(valor, nivel + 1)            # ¡se llama a sí misma, un nivel más adentro!
        else:
            print("    " * nivel + f"{clave}: {valor}")

configuracion = {
    "entorno": "Humanoid-v5",
    "red": {"capas": [256, 256], "activacion": "relu"},
    "entrenamiento": {"tasa": 0.0003, "optimizador": {"nombre": "adam", "beta": 0.9}},
}
mostrar(configuracion)"""),

md(r"""Da igual cuántos niveles de profundidad tenga la configuración: la función baja sola hasta el fondo. Toda recursión necesita un **caso base**, una situación en la que
**no** se llama a sí misma (aquí: cuando el valor no es un diccionario), o se llamaría para siempre. (Si eso pasa, Python lo corta con un `RecursionError` tras unas
mil llamadas.)
"""),

md(r"""## 13 · Iteradores: de uno en uno

Para entender la última herramienta de hoy, hay que ver qué hace un `for` por dentro. Las listas, las cadenas, los diccionarios, `range`... son **iterables**: cosas que se
pueden recorrer. Por dentro, el `for` le pide a la colección un **iterador** (con `iter`) y luego le va pidiendo "el siguiente" (con `next`), uno a uno:
"""),

code(r"""motores = ["cadera", "rodilla"]
iterador = iter(motores)
print(next(iterador))
print(next(iterador))"""),

md(r"""¿Y si pedimos uno más de los que hay?"""),

code_err(r"""print(next(iterador))"""),

md(r"""`StopIteration`: "se acabó la iteración". ¡El `for` funciona exactamente así!: pide `next` una y otra vez, y cuando recibe un `StopIteration`, sabe que ha terminado
y sale del bucle, sin mostrarte ningún error. Un `for` es, en el fondo, un `while` con `next` y un `try`/`except StopIteration` escondidos.
"""),

md(r"""## 14 · Generadores: producir datos de uno en uno

Un **generador** es una función que, en vez de devolver todo de golpe con `return`, va **entregando** valores **de uno en uno** con la palabra **`yield`** ("ceder",
"entregar"). Cada vez que entrega uno, **se pausa**, y cuando le piden el siguiente, **continúa** justo donde se quedó.

El ejemplo más útil en aprendizaje automático: los **lotes** (*batches*). Cuando se entrena con miles de ejemplos (NB18), no se usan todos a la vez, sino en **trozos**:
16, 64 o 256 ejemplos cada vez. Un generador que va entregando trozos:
"""),

code(r"""def lotes(datos, tamano):
    for inicio in range(0, len(datos), tamano):
        yield datos[inicio:inicio + tamano]          # entrega un trozo y se pausa

ejemplos = list(range(10))
for lote in lotes(ejemplos, 4):
    print(lote)"""),

md(r"""Tres lotes: dos de 4 y el último de 2 (lo que sobra). Fíjate en que el generador se usa en un `for` como cualquier colección.

¿Qué ganamos? Que **nunca existen todos los lotes a la vez en la memoria**: el generador fabrica cada uno justo cuando se necesita. Con 10 ejemplos da igual, pero un
robot puede generar **millones** de datos. Lo mismo hace la comprensión **sin corchetes** que usamos con `any` en el NB21: se llama **expresión generadora**, y produce los
valores de uno en uno en vez de construir la lista. Comparemos cuánta memoria ocupan (con `sys.getsizeof`, que dice el tamaño de un objeto en **bytes**, la unidad de
memoria):
"""),

code(r"""import sys

lista = [x ** 2 for x in range(1_000_000)]           # con corchetes: fabrica TODA la lista
generador = (x ** 2 for x in range(1_000_000))       # con paréntesis: los fabrica de uno en uno

print(f"La lista ocupa:      {sys.getsizeof(lista):>12,} bytes")
print(f"El generador ocupa:  {sys.getsizeof(generador):>12,} bytes")
print("Las dos suman lo mismo:", sum(lista) == sum(generador))"""),

md(r"""La lista ocupa **millones** de bytes (y eso sin contar los números de dentro); el generador, una cantidad diminuta, porque solo guarda "por dónde va". Y suman lo mismo.

Un detalle: un generador **solo se puede recorrer una vez** (como el iterador del apartado anterior, se "gasta"). Si lo necesitas otra vez, hay que crearlo de nuevo.

**Dónde los verás**: los "cargadores de datos" de PyTorch son, en esencia, generadores de lotes; y muchos bucles de entrenamiento producen episodios con generadores.
"""),

md(r"""## 15 · Documentar una función

Una función que solo entiende quien la escribió no sirve en un equipo. Dos herramientas para que se entienda sola:

**El *docstring***: un texto entre comillas triples **justo debajo del `def`**, que explica qué hace la función, qué recibe y qué devuelve. Python lo guarda, y **`help`**
lo muestra.

**Las anotaciones de tipo** (*type hints*): después de cada parámetro, dos puntos y su **tipo esperado**; y antes de los dos puntos finales, una flecha `->` con el tipo que
devuelve. **Python no las comprueba** (si pasas otra cosa, no da error por ello): son **documentación** que leen las personas y los editores de código, que te avisan si te
equivocas.
"""),

code(r"""def recompensa(altura_torso: float, velocidad: float, esfuerzo: float = 0.0) -> float:
    '''Recompensa de un paso del humanoide (NB04).

    altura_torso: altura del torso en metros (sano entre 1 y 2).
    velocidad: velocidad hacia delante del centro de masas, en m/s.
    esfuerzo: suma de las acciones al cuadrado.
    Devuelve los puntos del paso.
    '''
    premio_de_pie = 5 if 1.0 < altura_torso < 2.0 else 0
    return premio_de_pie + 1.25 * velocidad - 0.1 * esfuerzo

help(recompensa)
print(recompensa(1.3, 2.0, 1.0))"""),

md(r"""`help` muestra la "ficha" de la función, con sus tipos y su explicación. En un proyecto de verdad, **toda** función que vaya a usar otra persona debería tener su
docstring. (Y ahora entiendes la línea de documentación que pusimos al principio de cada script de construcción de estos cuadernos.)

Algunos tipos que verás en las anotaciones: `int`, `float`, `str`, `bool`, `list[float]` (lista de decimales), `dict[str, int]` (diccionario de texto a entero),
`tuple[float, float]`, `None`, y `np.ndarray` (un array de NumPy).
"""),

md(r"""## 16 · Resumen de la lección

1. **Valores por defecto** (`def f(x, pasos=500)`) y **argumentos por nombre** (`f(x, pasos=100)`). **Nunca** una lista o diccionario como valor por defecto: se comparte
   entre llamadas; usa `None` y créalo dentro.
2. **`*args`** recoge los argumentos sobrantes en una tupla y **`**kwargs`**, los con nombre en un diccionario. Al llamar, `f(*lista)` y `f(**diccionario)` los reparten.
3. **Ámbito**: asignar a una variable dentro de una función la hace local (`UnboundLocalError` si se lee antes). Evita `global`: recibe por parámetro y devuelve con `return`.
4. Las funciones son **objetos**: se guardan, se pasan y se devuelven. **`lambda`** para funciones cortitas de usar y tirar. Un **cierre** es una función fabricada por otra que
   recuerda sus valores (la **fábrica de políticas**). Un **decorador** envuelve una función con algo extra (`@cronometro`). La **recursión** recorre estructuras anidadas.
5. Un `for` usa **iteradores** (`iter`, `next`, `StopIteration`). Los **generadores** (`yield`) y las **expresiones generadoras** producen datos de uno en uno, sin llenar la memoria
   (**lotes**). Documenta con **docstrings** (`help`) y **anotaciones de tipo**.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Valor por defecto** | El valor que toma un parámetro si no se le da. |
| **Argumento por nombre** | Pasar un valor indicando el parámetro: `f(pasos=100)`. |
| **`*args` / `**kwargs`** | Recoger argumentos sobrantes en una tupla / en un diccionario. |
| **Ámbito** | El sitio donde "vive" una variable (local o global). |
| **`UnboundLocalError`** | Error por usar una variable local antes de darle valor. |
| **`lambda`** | Función anónima de una línea: `lambda x: x ** 2`. |
| **Cierre (*closure*)** | Función que recuerda variables del sitio donde se creó. |
| **Decorador** | Función que envuelve a otra para añadirle algo; se aplica con `@`. |
| **Recursión** | Una función que se llama a sí misma; necesita un **caso base**. |
| **Iterable / iterador** | Algo que se puede recorrer / el objeto que lo recorre con `next`. |
| **Generador / `yield`** | Función que entrega valores de uno en uno. |
| **Lote (*batch*)** | Un trozo de los datos de entrenamiento. |
| **Docstring** | Texto de documentación justo debajo del `def`. |
| **Anotación de tipo** | Indicar el tipo esperado: `x: float`, `-> float`. |
"""),

md(r"""## 17 · Ejercicios

**E1.** Escribe una función `potencia(base, exponente=2)` y llámala de tres formas: solo con la base, con base y exponente, y con argumentos por nombre en orden inverso.

**E2.** Predice qué muestra este código y explica por qué. ¿Cómo lo arreglas?

```python
def registrar(evento, eventos={}):
    eventos[evento] = eventos.get(evento, 0) + 1
    return eventos

print(registrar("caída"))
print(registrar("tiempo"))
```

**E3.** Escribe `mayor(*numeros)` que devuelva el mayor de cuantos números le pasen, **sin** usar `max` (con un bucle).

**E4.** Con un diccionario `ajustes = {"retorno": 455.3, "pasos": 500, "entorno": "palo"}`, llama a la función `describir` del apartado 6 desempaquetándolo.

**E5.** Ordena `["Walker2d", "Ant", "Humanoid", "Hopper"]` por **longitud** del nombre, con una `lambda`.

**E6.** Escribe una fábrica `crear_recompensa(peso_avance)` que devuelva una función de recompensa `recompensa(velocidad)` que calcule `5 + peso_avance * velocidad`.
Fabrica dos (con 1,25 y con 3) y compáralas para una velocidad de 2.

**E7.** Escribe un generador `cuenta_atras(n)` que entregue n, n−1, ..., 1. Úsalo en un `for`.

**E8.** **Reto.** Escribe un decorador `contador_de_llamadas` que cuente cuántas veces se ha llamado a una función y lo muestre en cada llamada. (Pista: guarda el contador
en un **atributo** de la función envuelta, por ejemplo `envuelta.llamadas = 0`, y súmale 1 dentro.)
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
def potencia(base, exponente=2):
    return base ** exponente

print(potencia(5))                         # 25 (exponente por defecto)
print(potencia(2, 10))                     # 1024
print(potencia(exponente=3, base=2))       # 8
```
</details>

<details>
<summary>▶ Solución E2</summary>

Muestra `{'caída': 1}` y luego **`{'caída': 1, 'tiempo': 1}`**: el diccionario por defecto se crea **una sola vez** y se comparte entre llamadas (la trampa del apartado 3).
Arreglo:

```python
def registrar(evento, eventos=None):
    if eventos is None:
        eventos = {}
    eventos[evento] = eventos.get(evento, 0) + 1
    return eventos
```
</details>

<details>
<summary>▶ Solución E3</summary>

```python
def mayor(*numeros):
    resultado = numeros[0]
    for n in numeros[1:]:
        if n > resultado:
            resultado = n
    return resultado

print(mayor(3, 9, 2, 7))     # 9
```

(Si se llama sin ningún número, `numeros[0]` daría `IndexError`; un `raise ValueError` al principio, NB22, lo haría más claro.)
</details>

<details>
<summary>▶ Solución E4</summary>

```python
ajustes = {"retorno": 455.3, "pasos": 500, "entorno": "palo"}
print(describir(**ajustes))
```

Salida: `palo: 455.3 en 500 pasos`.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
print(sorted(["Walker2d", "Ant", "Humanoid", "Hopper"], key=lambda nombre: len(nombre)))
```

Salida: `['Ant', 'Hopper', 'Walker2d', 'Humanoid']` (3, 6, 8 y 8 letras; a igual longitud, mantiene el orden original). Por cierto, `key=len` a secas haría lo mismo: `len` ya es
una función.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
def crear_recompensa(peso_avance):
    def recompensa(velocidad):
        return 5 + peso_avance * velocidad
    return recompensa

normal = crear_recompensa(1.25)
ansiosa = crear_recompensa(3)
print(normal(2), ansiosa(2))     # 7.5 y 11
```

Con la fábrica, probar distintos diseños de recompensa (NB04) es tan fácil como fabricarlos.
</details>

<details>
<summary>▶ Solución E7</summary>

```python
def cuenta_atras(n):
    while n > 0:
        yield n
        n = n - 1

for x in cuenta_atras(5):
    print(x)
```

Muestra 5, 4, 3, 2, 1. El generador se pausa tras cada `yield` y continúa con el `n = n - 1` cuando el `for` pide el siguiente.
</details>

<details>
<summary>▶ Solución E8</summary>

```python
import functools

def contador_de_llamadas(funcion):
    @functools.wraps(funcion)
    def envuelta(*args, **kwargs):
        envuelta.llamadas = envuelta.llamadas + 1
        print(f"{funcion.__name__} llamada {envuelta.llamadas} veces")
        return funcion(*args, **kwargs)
    envuelta.llamadas = 0
    return envuelta

@contador_de_llamadas
def saludar():
    return "hola"

saludar()
saludar()
```

Muestra "llamada 1 veces" y "llamada 2 veces". Las funciones, como objetos, pueden guardar datos propios (**atributos**) con un punto: `envuelta.llamadas`. En el NB24 verás que
esto es justo lo que hacen los **objetos** de las clases.
</details>
"""),

md(r"""## 18 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has visto todo lo que pueden hacer las funciones: configurarse, combinarse, fabricarse, envolverse y producir datos de uno en uno. En el **NB24** llega la gran herramienta
para organizar programas grandes, y la base de **todo** Gymnasium y PyTorch: las **clases** y los **objetos**. Convertiremos el palo de escoba en un objeto con su propio
`reset` y su propio `step`... como los entornos de verdad.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB23_python_funciones.ipynb")
    build(out, cells, title="NB23 · Python de verdad (4): funciones a fondo")
