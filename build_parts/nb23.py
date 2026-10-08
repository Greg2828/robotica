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
Práctica en MuJoCo (§17): abrir taller.py (help + inspect.getsource), mi_cargar con
docstring/tipos/**opciones, generador de pasos (yield), al_azar es un cierre ->
fábrica crear_pd para el palo de escoba MuJoCo, mi_video con Renderer + @cronometro.
taller.py NO se modifica.
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

md(r"""## 17 · 🛠 Práctica en MuJoCo: abre la caja negra (`taller.py`)

Desde el NB00 has usado `taller.cargar`, `taller.video`, `taller.al_azar`... como una **caja negra**: las llamabas y funcionaban, sin saber
qué hacían por dentro. Hoy, con todo lo que sabes de funciones, toca **abrir la caja**. Vas a:

1. Leer la "ficha" (docstring) y el **código** de las funciones de `taller` sin salir del cuaderno.
2. Escribir **tu propia versión** de `cargar`, con docstring, anotaciones de tipo y `**opciones`.
3. Convertir el bucle de simulación en un **generador** (`yield`).
4. Descubrir que `taller.al_azar` es un **cierre**, y fabricar con la misma idea **controladores** para el palo de escoba.
5. Escribir tu propio `video`, cronometrado con un **decorador**.

Una regla importante: **no vamos a modificar `taller.py`** (otras prácticas lo usan tal cual). Tu versión vive aquí, en el cuaderno, con
nombres que empiezan por `mi_`.
"""),

md(r"""### Paso 1 · ¿Dónde está la caja y qué dice su ficha?

Un módulo de Python es un fichero `.py`, y `__file__` dice **dónde** está. Y como las funciones de `taller` tienen **docstring** (apartado 15),
`help` las explica:
"""),

code(r"""import taller

print(taller.__file__)
help(taller.cargar)"""),

md(r"""Exactamente la ficha que escribirías tú: qué devuelve, `(modelo, datos)`, y los **tres casos** que acepta: un nombre conocido, un texto que
empieza por `<` o la ruta de un fichero.

### Paso 2 · Leer el código de verdad

El módulo `inspect` ("inspeccionar") de Python puede enseñarte el **código fuente** de cualquier función escrita en Python. Leamos `cargar`:
"""),

code(r"""import inspect

print(inspect.getsource(taller.cargar))"""),

md(r"""Léelo despacio; ya entiendes **cada línea**:

- `def cargar(nombre_o_xml: str):` → un parámetro con **anotación de tipo** (apartado 15): espera un texto.
- `if nombre_o_xml in _MODELOS:` → `_MODELOS` es un **diccionario** nombre → fichero (NB21). Si el nombre está, busca su fichero y lo carga
  con `mujoco.MjModel.from_xml_path` ("desde la ruta de un XML").
- `elif nombre_o_xml.lstrip().startswith("<"):` → métodos de cadena del NB20: quita espacios de la izquierda y mira si empieza por `<`. Si sí,
  es un plano escrito a mano: `from_xml_string`.
- `else:` → si no, lo trata como la ruta de un fichero.
- `datos = mujoco.MjData(modelo)` y `mujoco.mj_forward(modelo, datos)` → crea los datos y calcula dónde está cada pieza **sin avanzar el
  tiempo** (por eso las fotos salen bien antes de simular).
- `return modelo, datos` → devuelve una **tupla** (NB21), que tú desempaquetas con `modelo, datos = taller.cargar(...)`.

(¿Y el guion bajo de `_MODELOS`? Es una **costumbre**: un nombre que empieza por `_` significa "esto es de uso interno del módulo; no lo
toques desde fuera". Python no lo prohíbe, pero es de buena educación respetarlo.)
"""),

md(r"""### Paso 3 · Tu propio `cargar`

Ahora, tu versión. Hará lo mismo para dos robots, y algo **más**: aceptará `**opciones` (apartado 5) para cambiar el **paso de tiempo** y la
**gravedad** al cargar. Así, `mi_cargar("humanoide", gravedad=-1.62)` te da el humanoide en la Luna en una sola línea.

Primero, el diccionario de robots. El humanoide vive dentro de la biblioteca Gymnasium; `os.path.join` pega trozos de una ruta de carpetas
(lo verás a fondo en el NB26):
"""),

code(r"""import os
import gymnasium
import mujoco

CARPETA_GYM = os.path.join(os.path.dirname(gymnasium.__file__), "envs", "mujoco", "assets")
MIS_MODELOS = {
    "humanoide": os.path.join(CARPETA_GYM, "humanoid.xml"),
    "palo_escoba": os.path.join("robots", "palo_escoba.xml"),
}
print(MIS_MODELOS["palo_escoba"])"""),

md(r"""Y la función, con su docstring y sus anotaciones. Fíjate en el tipo que devuelve: `tuple[mujoco.MjModel, mujoco.MjData]`, una tupla con
un modelo y unos datos.
"""),

code(r"""def mi_cargar(que: str, **opciones) -> tuple[mujoco.MjModel, mujoco.MjData]:
    '''Carga un robot y devuelve (modelo, datos).

    que: un nombre de MIS_MODELOS o un plano MJCF escrito como texto.
    opciones: paso=... (segundos) y/o gravedad=... (m/s², negativa = hacia abajo).
    '''
    if que in MIS_MODELOS:
        modelo = mujoco.MjModel.from_xml_path(MIS_MODELOS[que])
    else:
        modelo = mujoco.MjModel.from_xml_string(que)
    if "paso" in opciones:
        modelo.opt.timestep = opciones["paso"]
    if "gravedad" in opciones:
        modelo.opt.gravity[2] = opciones["gravedad"]
    datos = mujoco.MjData(modelo)
    mujoco.mj_forward(modelo, datos)
    return modelo, datos"""),

md(r"""Probémosla con y sin opciones:"""),

code(r"""modelo, datos = mi_cargar("palo_escoba")
print("Palo de escoba:", modelo.nu, "motor, paso", modelo.opt.timestep, "s")

modelo, datos = mi_cargar("humanoide", gravedad=-1.62, paso=0.005)
print("Humanoide:     ", modelo.nu, "motores, paso", modelo.opt.timestep, "s, gravedad", modelo.opt.gravity)"""),

md(r"""### Paso 4 · El bucle de simulación como generador

En todas las prácticas repetimos el mismo bucle: "aplica el control, da un paso, mira". Vamos a escribirlo **una vez**, como un **generador**
(apartado 14): en cada paso hace su trabajo y **entrega** (`yield`) los datos, pausándose hasta que le pidan el siguiente. Quien lo usa decide
qué hacer con cada paso, sin repetir el bucle. El parámetro `control=None` (apartado 1) permite simular sin controlador:
"""),

code(r"""def pasos(modelo, datos, segundos, control=None):
    '''Simula `segundos` y entrega los datos después de cada paso.'''
    for _ in range(round(segundos / modelo.opt.timestep)):
        if control is not None:
            control(modelo, datos)
        mujoco.mj_step(modelo, datos)
        yield datos"""),

md(r"""(El `_` como nombre de la variable del `for` es otra costumbre: "esta variable no la voy a usar".)

Ahora, la magia. Con una **comprensión** sobre el generador registramos la altura del torso del humanoide (en `qpos[2]`, NB21) durante 1 segundo
de caída, en **una** línea:
"""),

code(r"""modelo, datos = mi_cargar("humanoide")
alturas = [d.qpos[2] for d in pasos(modelo, datos, 1.0)]

print(len(alturas), "pasos")
print(f"Altura al principio: {alturas[0]:.2f} m  |  la más baja: {min(alturas):.2f} m")"""),

md(r"""333 pasos de 0,003 s y el torso ha bajado de 1,40 m a menos de 30 cm: se ha desplomado (NB00). El generador ha simulado y la comprensión ha
recogido; cada uno hace **una** cosa.

### Paso 5 · `al_azar` era un cierre

Ahora mira el código de `taller.al_azar`, el que mueve los motores al azar desde el NB00:
"""),

code(r"""print(inspect.getsource(taller.al_azar))"""),

md(r"""¡Es una **fábrica de funciones**, un **cierre** (apartado 10)! `al_azar(semilla)` crea un generador de números aleatorios, `azar`, y fabrica
una función `control` que lo **recuerda**. Por eso pasabas `control=taller.al_azar(0)`: estabas pasando la función fabricada.

Con la misma idea, fabriquemos **controladores** para el palo de escoba de MuJoCo. El palo tiene dos articulaciones (`qpos` = posición del
carro y ángulo del palo; `qvel` = sus velocidades). Un buen controlador empuja el carro **hacia donde se cae** el palo: tanto más cuanto más
inclinado (`k`) y cuanto más deprisa cae (`d`), igual que tus ruedecillas del NB11. Le añadimos dos términos pequeños fijos (0,1 y 0,2) para que
el carro no se escape del raíl, y recortamos a ±1, el rango del motor:
"""),

code(r"""import numpy as np

def crear_pd(k, d):
    def control(modelo, datos):
        x, angulo = datos.qpos               # desempaquetar (NB21)
        vx, vel_angulo = datos.qvel
        empuje = k * angulo + d * vel_angulo + 0.1 * x + 0.2 * vx
        datos.ctrl[0] = np.clip(empuje, -1, 1)
    return control"""),

md(r"""Y una función que mide cuánto aguanta un controlador, usando el generador: inclinamos el palo 5 grados y recorremos los pasos de 10 segundos.
Si en algún paso el palo pasa de 45° (0,785 rad), devolvemos el reloj con `return` (que también sale del `for`). Si llega al final, aguantó
los 10 segundos:
"""),

code(r"""def aguanta(control, segundos=10):
    modelo, datos = mi_cargar("palo_escoba")
    datos.qpos[1] = np.radians(5)
    for d in pasos(modelo, datos, segundos, control):
        if abs(d.qpos[1]) > 0.785:
            return d.time
    return segundos

print(f"sin controlador: aguanta {aguanta(None):.2f} s")
for k, d in [(3, 0), (1, 0.8), (3, 0.8)]:
    print(f"k={k}, d={d}: aguanta {aguanta(crear_pd(k, d)):.2f} s")"""),

md(r"""- Sin controlador (`control=None`), cae en **0,68 s**.
- Solo con inclinación (`k=3, d=0`), aguanta **1,5 s**: empuja, pero se pasa de frenada y el palo oscila cada vez más (el mismo fallo del NB11).
- Con poca fuerza (`k=1`), aunque frene bien, aguanta **3,22 s**: no empuja lo bastante.
- Con **`k=3, d=0,8`**, aguanta los **10 segundos** enteros.

Cuatro controladores fabricados con la **misma** fábrica, cada uno recordando sus números.
"""),

md(r"""### Paso 6 · Tu propio `video`, con cronómetro

Ahora lee el código de `taller.video` (es más largo; tómate tu tiempo):
"""),

code(r"""print(inspect.getsource(taller.video))"""),

md(r"""Su receta: (1) calcular cuántos pasos dar y **cada cuántos** pasos hacer una foto (para sacar unas 30 fotos por segundo de vídeo); (2) crear un
**dibujante** (`mujoco.Renderer`) y una **cámara**; (3) en el bucle, simular y, de vez en cuando, hacer una foto; (4) guardar las fotos como MP4
con `imageio.mimsave` y enseñarlo con `display(Video(...))`.

Tu versión hará lo mismo, pero usando **tu generador** para el bucle y con el **decorador cronómetro** del apartado 11 encima. Primero, el
decorador (copiado tal cual del apartado 11):
"""),

code(r"""import time
import functools

def cronometro(funcion):
    @functools.wraps(funcion)
    def envuelta(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)
        print(f"[{funcion.__name__} tardó {time.perf_counter() - inicio:.1f} s]")
        return resultado
    return envuelta"""),

md(r"""Y `mi_video`. La cámara es "libre" (`mjv_defaultFreeCamera` la coloca mirando al centro del robot) y la giramos para mirar de lado
(`azimuth=90`) y un poco desde arriba (`elevation=-15`), como hace `taller`. Las fotos se guardan en la misma carpeta que las de `taller`:
"""),

code(r"""import imageio
from IPython.display import Video, display

@cronometro
def mi_video(modelo, datos, segundos, control=None, nombre="mi_video", distancia=4.0):
    '''Simula `segundos`, guarda un MP4 de unas 30 fotos por segundo y lo enseña.'''
    cada = max(1, round(1 / (30 * modelo.opt.timestep)))      # una foto cada `cada` pasos
    camara = mujoco.MjvCamera()
    mujoco.mjv_defaultFreeCamera(modelo, camara)
    camara.distance, camara.azimuth, camara.elevation = distancia, 90, -15
    fotos = []
    with mujoco.Renderer(modelo, 270, 360) as dibujante:
        for i, d in enumerate(pasos(modelo, datos, segundos, control)):
            if i % cada == 0:
                dibujante.update_scene(d, camera=camara)
                fotos.append(dibujante.render())
    ruta = os.path.join("assets", "practicas", f"{nombre}.mp4")
    imageio.mimsave(ruta, fotos, fps=1 / (cada * modelo.opt.timestep), macro_block_size=1)
    display(Video(ruta, embed=True, html_attributes="controls loop autoplay muted"))
    return len(fotos)"""),

md(r"""(`with ... as dibujante:` abre el dibujante y lo **cierra solo** al terminar el bloque, aunque haya un error; es como un `try/finally` del
NB22 ya hecho. Lo verás a fondo con los ficheros, en el NB26. Y `i % cada == 0` es el truco del NB21: verdadero cada `cada` pasos.)

¡A probarlo! El palo de escoba con tu mejor controlador, 4 segundos. (Si al ejecutarlo aparece alguna línea rara como *"Couldn't open plugin directory"*, es un aviso inofensivo de la parte gráfica. `taller`
los tapa con un truco, `_dibujante`, que puedes leer con `inspect` si tienes curiosidad.)
"""),

code(r"""modelo, datos = mi_cargar("palo_escoba")
datos.qpos[1] = np.radians(5)
mi_video(modelo, datos, 4, control=crear_pd(3, 0.8), nombre="nb23_palo_pd")"""),

md(r"""El carrito corrige con un par de vaivenes y el palo se queda **de pie**. Y el decorador te ha dicho cuánto ha tardado en fabricar el vídeo,
sin tocar el código de `mi_video`. Ahora el controlador que solo mira la inclinación (`k=3, d=0`), para ver el fallo:
"""),

code(r"""modelo, datos = mi_cargar("palo_escoba")
datos.qpos[1] = np.radians(5)
mi_video(modelo, datos, 2, control=crear_pd(3, 0), nombre="nb23_palo_sin_d")"""),

md(r"""Cada vaivén es más grande que el anterior, hasta que el palo cae: le falta el término de la **velocidad** (`d`), que es el que frena.

### Tus retos

**Reto 1.** Usa `mi_cargar` con `**` (apartado 6): guarda las opciones en un diccionario `luna = {"gravedad": -1.62}` y carga el palo de escoba
con `mi_cargar("palo_escoba", **luna)`. ¿Cuánto tarda en caer **sin controlador** en la Luna? (Pista: `aguanta` usa `mi_cargar` sin opciones;
copia sus líneas y añade el `**luna`.)

**Reto 2.** Un controlador no tiene por qué fabricarse con `def`: escribe uno con **`lambda`** (apartado 9) que empuje siempre al máximo,
`lambda modelo, datos: datos.ctrl.fill(1)`, y pásalo a `aguanta`. ¿Aguanta más o menos que sin controlador? ¿Por qué?

**Reto 3.** Escribe un generador `hasta_caer(modelo, datos, control)` que entregue los datos paso a paso **solo mientras** el palo no pase
de 45°, y que se pare solo (un `return` dentro de un generador lo termina). Úsalo para contar los pasos que aguanta `crear_pd(1, 0.8)`.

<details>
<summary>▶ Solución Reto 1</summary>

```python
luna = {"gravedad": -1.62}
modelo, datos = mi_cargar("palo_escoba", **luna)
datos.qpos[1] = np.radians(5)
for d in pasos(modelo, datos, 10):
    if abs(d.qpos[1]) > 0.785:
        break
print(f"En la Luna cae en {d.time:.2f} s")
```

Cae en **1,69 s**, frente a 0,68 s en la Tierra: unas 2,5 veces más despacio. (La gravedad es 6 veces más débil y el tiempo crece con su raíz
cuadrada, √6 ≈ 2,45: otra raíz cuadrada, como la de los palos largos del NB20.) En la Luna, equilibrar es más fácil.
</details>

<details>
<summary>▶ Solución Reto 2</summary>

```python
print(aguanta(lambda modelo, datos: datos.ctrl.fill(1)))
```

Cae en **0,37 s**, mucho **antes** que sin controlador (0,68 s). Empujar el carro hacia +x sin mirar hace que el palo se vaya hacia atrás
(como cuando arrancas un autobús de golpe y te vas hacia atrás) y, si estaba cayendo hacia el otro lado, lo empeora. Un controlador que no
**mira** no es un controlador. (`fill(1)` es un método de los arrays de NumPy que pone todos sus números a 1.)
</details>

<details>
<summary>▶ Solución Reto 3</summary>

```python
def hasta_caer(modelo, datos, control):
    for d in pasos(modelo, datos, 10, control):
        if abs(d.qpos[1]) > 0.785:
            return              # termina el generador
        yield d

modelo, datos = mi_cargar("palo_escoba")
datos.qpos[1] = np.radians(5)
print(sum(1 for _ in hasta_caer(modelo, datos, crear_pd(1, 0.8))), "pasos")
```

Unos **321 pasos** (3,22 s con pasos de 0,01 s). Fíjate: un generador puede usar **otro** generador por dentro. `sum(1 for _ in ...)` es una
expresión generadora que cuenta cuántos elementos entrega.
</details>

### Qué has aprendido de MuJoCo hoy

- `taller` no tiene magia: `cargar` = `MjModel.from_xml_path` / `from_xml_string` + `MjData` + **`mj_forward`** (colocar las piezas sin avanzar
  el tiempo).
- `video` = un bucle de `mj_step` + un **`mujoco.Renderer`** (`update_scene` y `render` dan una foto como array) + una **`MjvCamera`** +
  `imageio` para el MP4.
- Puedes cambiar el paso y la gravedad de un modelo ya cargado: `modelo.opt.timestep`, `modelo.opt.gravity`.
- Un **generador** de pasos separa "simular" de "qué hago con cada paso"; un **cierre** fabrica controladores que recuerdan sus parámetros.
- En el palo de escoba de MuJoCo, el controlador `crear_pd(3, 0.8)` lo sostiene 10 s; sin el término de velocidad (`d=0`) cae a los 1,5 s.

En la práctica del NB24 meterás `modelo`, `datos` y estas funciones dentro de **una sola cosa**: una **clase** `Simulacion`, con sus propios
`reiniciar`, `paso` y `foto`.
"""),

md(r"""## 19 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has visto todo lo que pueden hacer las funciones: configurarse, combinarse, fabricarse, envolverse y producir datos de uno en uno, y has abierto la caja negra de `taller.py`. En el **NB24** llega la gran herramienta
para organizar programas grandes, y la base de **todo** Gymnasium y PyTorch: las **clases** y los **objetos**. Convertiremos el palo de escoba en un objeto con su propio
`reset` y su propio `step`... como los entornos de verdad.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB23_python_funciones.ipynb")
    build(out, cells, title="NB23 · Python de verdad (4): funciones a fondo")
