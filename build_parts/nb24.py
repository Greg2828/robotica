"""Construye NB24 · Python de verdad (5): clases y objetos (I).

Por qué (datos + comportamiento juntos); clase = molde, objeto = galleta;
class, instancias, __init__ y self, atributos, métodos, objetos independientes,
objetos mutables (alias), __repr__ y __str__, atributos de clase vs de
instancia, convención _privado, @property (esta_caido, inclinación en
radianes), AttributeError real. Proyecto: class PaloDeEscoba con reset/step al
estilo Gymnasium (obs, recompensa, terminado, truncado, info) y su propio
random.Random(semilla) (arregla la mezcla de dados del NB11); PoliticaLineal
con __call__ (objeto que se llama como una función); bucle de episodio con
objetos (mismos resultados: 44,8 / 296,0 / 499,9); @dataclass para la
configuración (y field(default_factory=list), la trampa del NB23); todo en
Python es un objeto (type, isinstance, dir).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB24 · Python de verdad (5): clases y objetos (I)

**Parte 3 · Python de verdad — Lección 5**

> Llevas todo el curso usando **objetos** sin saberlo. Una lista es un objeto (con su método `append`). Una cadena también (con
> `split`, `upper`...). El entorno del humanoide de Gymnasium (`entorno.reset()`, `entorno.step(...)`) es un objeto. Y las redes
> neuronales de PyTorch, que llegarán pronto, también lo son. Hoy aprenderás a **fabricar los tuyos**.

Esta es, probablemente, la lección más importante del bloque de Python para tu futuro trabajo. **Todo** el código profesional de robótica
y de aprendizaje automático está organizado en **clases**. Sin entenderlas, el código de Gymnasium o de PyTorch parece magia; con ellas,
se lee como un libro.

Al final de hoy, el palo de escoba del NB11 será un **objeto** con su propio `reset` y su propio `step`, **exactamente** como los entornos de
Gymnasium. Y la política, otro objeto. Y el bucle de un episodio se escribirá igual que con el humanoide de verdad.
"""),

md(r"""## 1 · El problema: datos sueltos por todas partes

Mira cómo era el palo de escoba en el NB11. Su estado eran **dos cajas sueltas**, `inclinacion` y `velocidad`; sus reglas, unas **constantes**
sueltas (`EMPUJE_MAXIMO`, `CAIDA`...); y para dar un paso había que **pasarle** el estado a la función `paso`, que lo **devolvía** cambiado:

```
   inclinacion, velocidad, recompensa, terminado = paso(inclinacion, velocidad, empuje)
```

Funcionaba, pero imagina que quieres **dos** palos de escoba a la vez (por ejemplo, para entrenar en paralelo, como se hace de verdad). Necesitarías
`inclinacion_1`, `velocidad_1`, `inclinacion_2`, `velocidad_2`... y no confundirlos nunca. Con diez palos, un caos. Y con un humanoide, cuyo estado
tiene cientos de números, imposible.

La idea de las clases es muy sencilla: **juntar en un mismo "paquete" los datos de algo (su estado) y las acciones que se pueden hacer con ello**. Un
palo de escoba **sabe** su inclinación y su velocidad, y **sabe** dar un paso. Tú solo le dices `palo.step(empuje)`.
"""),

md(r"""## 2 · Clase y objeto: el molde y las galletas

Dos palabras que hay que distinguir bien:

- Una **clase** es un **molde**, un **plano**: la descripción de cómo es y qué sabe hacer un tipo de cosa. Por ejemplo, "un palo de escoba tiene
  una inclinación y una velocidad, y sabe reiniciarse y dar pasos".
- Un **objeto** (o **instancia**) es **una cosa concreta** fabricada con ese molde. Cada una tiene **sus propios datos**.

Como un **molde de galletas**: el molde (la clase) es uno; con él haces muchas galletas (los objetos), todas con la misma forma, pero cada una es una
galleta distinta (puedes morder una sin que se muerdan las demás). O como el plano de una casa y las casas construidas con él: mismo plano, pero
cada casa tiene sus propios muebles.

Ya lo has visto: `list` es una clase, y cada lista que creas es un objeto distinto. `type` te dice de qué clase es un objeto:
"""),

code(r"""print(type([1, 2, 3]))
print(type("hola"))
print(type(3.5))"""),

md(r"""`list`, `str`, `float`: son **clases**. Y `[1, 2, 3]`, `"hola"` y `3.5`, **objetos** de esas clases.

## 3 · Tu primera clase

Una clase se define con la palabra **`class`**, un nombre, dos puntos y un bloque con sangría. Por costumbre, los nombres de las clases se escriben
con **cada palabra empezando en mayúscula** y sin guiones bajos (`PaloDeEscoba`, `PoliticaLineal`), para distinguirlas de las funciones y variables
(`palo_de_escoba`). La clase más sencilla posible, vacía:
"""),

code(r"""class Robot:
    pass

mi_robot = Robot()        # fabricar un objeto: el nombre de la clase con paréntesis
print(type(mi_robot))"""),

md(r"""`Robot()` (el nombre de la clase **con paréntesis**, como si la llamaras) fabrica un objeto nuevo. Aún no hace nada útil, porque la clase está vacía.
Vamos a darle datos.
"""),

md(r"""## 4 · `__init__` y `self`: los datos de cada objeto

Para que cada objeto nazca con sus propios datos, se escribe dentro de la clase una función especial llamada **`__init__`** (de *initialize*,
"inicializar"; con dos guiones bajos a cada lado). Python la llama **automáticamente** cada vez que se fabrica un objeto:
"""),

code(r"""class Robot:
    def __init__(self, nombre, motores):
        self.nombre = nombre
        self.motores = motores

humanoide = Robot("Humanoid-v5", 17)
print(humanoide.nombre)
print(humanoide.motores)"""),

md(r"""Hay una palabra nueva, y es **la clave de todo**: **`self`** ("uno mismo").

- Cuando haces `Robot("Humanoid-v5", 17)`, Python fabrica un objeto nuevo y llama a `__init__`, pasándole **ese objeto recién nacido** como primer
  argumento, que se recibe con el nombre `self`. Los demás argumentos (`"Humanoid-v5"` y `17`) van a `nombre` y `motores`.
- `self.nombre = nombre` significa: "**guarda en este objeto** un dato llamado `nombre`, con el valor que me han pasado".

A los datos guardados así en un objeto se les llama **atributos**, y se leen con un **punto**: `humanoide.nombre`. ¡Como los métodos de las listas, que
también se escriben con un punto! (Y como `envuelta.llamadas` del ejercicio E8 del NB23.)

Piensa en `self` como **"este objeto concreto"**. Cuando escribes la clase, no sabes qué objetos se fabricarán con ella; `self` es la forma de decir "el que
sea, el que se esté usando ahora mismo".
"""),

md(r"""## 5 · Métodos: lo que sabe hacer un objeto

Las funciones definidas dentro de una clase se llaman **métodos**: son las acciones que sabe hacer cada objeto. **Todas** reciben `self` como primer
parámetro, para poder usar los datos de **su** objeto:
"""),

code(r"""class Robot:
    def __init__(self, nombre, motores):
        self.nombre = nombre
        self.motores = motores

    def describir(self):
        return f"{self.nombre}, con {self.motores} motores"

    def ruedecillas_politica_lineal(self, observaciones):
        return self.motores * observaciones + self.motores      # NB14

humanoide = Robot("Humanoid-v5", 17)
print(humanoide.describir())
print(humanoide.ruedecillas_politica_lineal(45))"""),

md(r"""Al llamar `humanoide.describir()`, **no** se pasa `self` entre los paréntesis: Python lo pone **solo**, con el objeto que está a la izquierda del punto.
`humanoide.describir()` es, por dentro, `Robot.describir(humanoide)`. Por eso dentro del método `self.nombre` es el nombre **de ese** robot.

Y el segundo método recibe, además de `self`, un parámetro normal: `observaciones`. Calcula las ruedecillas de la política lineal (NB14) con **sus** 17
motores: 782.
"""),

md(r"""## 6 · Cada objeto, sus propios datos

Con un mismo molde se fabrican objetos **independientes**: cada uno con sus atributos.
"""),

code(r"""humanoide = Robot("Humanoid-v5", 17)
saltador = Robot("Hopper-v5", 3)
andador = Robot("Walker2d-v5", 6)

for robot in [humanoide, saltador, andador]:
    print(robot.describir(), "->", robot.ruedecillas_politica_lineal(11), "ruedecillas con 11 observaciones")"""),

md(r"""Tres robots, cada uno con su nombre y sus motores, y el mismo método funciona para todos usando los datos de cada uno. Esa es la gracia: **escribes el
comportamiento una vez, y sirve para todos los objetos**.

Los atributos se pueden **cambiar** después (los objetos que fabriques serán **mutables**, como las listas):
"""),

code(r"""saltador.motores = 4
print(saltador.describir())"""),

md(r"""Y por ser mutables, **les afecta la trampa del alias** (NB21): `otro = saltador` no copia el robot, solo le pega otra etiqueta. Si cambias `otro.motores`,
cambias el de `saltador`. (Para copiar objetos existe el módulo `copy`: `copy.copy(objeto)` o `copy.deepcopy(objeto)`.)

¿Y si pides un atributo que no existe?
"""),

code_err(r"""print(saltador.altura)"""),

md(r"""`AttributeError: 'Robot' object has no attribute 'altura'`: "un objeto `Robot` no tiene el atributo `altura`". Es el error que viste en la tabla del NB22
(`[1, 2].upper()` da lo mismo: las listas no tienen el método `upper`). Suele ser una **errata** en el nombre de un atributo o de un método.
"""),

md(r"""## 7 · Que se muestre bonito: `__repr__`

Si haces `print` de un objeto tuyo, sale algo poco útil:"""),

code(r"""print(humanoide)"""),

md(r"""Algo como `<__main__.Robot object at 0x7f...>`: la clase y una dirección de memoria. Para que se muestre algo legible, se define otro método especial, **`__repr__`**
(de *representation*), que devuelve el texto con el que se representa el objeto:
"""),

code(r"""class Robot:
    def __init__(self, nombre, motores):
        self.nombre = nombre
        self.motores = motores

    def __repr__(self):
        return f"Robot(nombre={self.nombre!r}, motores={self.motores})"

humanoide = Robot("Humanoid-v5", 17)
print(humanoide)
print([humanoide, Robot("Hopper-v5", 3)])"""),

md(r"""Mucho mejor, y también dentro de listas. La costumbre es que `__repr__` devuelva algo que **parezca el código** para crear ese objeto. (Existe también `__str__`,
para un texto "para personas"; si no lo defines, Python usa `__repr__`. Con `__repr__` suele bastar.)

Estos métodos con dos guiones bajos a cada lado (`__init__`, `__repr__`...) se llaman **métodos especiales** (o, en jerga, *dunder methods*, de *double underscore*). No
se llaman directamente: **Python los llama solo** en ciertos momentos (al crear un objeto, al mostrarlo...). Hay muchos más; en el NB25 veremos cómo hacer que tus
objetos se puedan **sumar** o **medir con `len`**.
"""),

md(r"""## 8 · Atributos de la clase: lo que comparten todos

A veces hay datos que son **iguales para todos** los objetos de una clase, como la gravedad para todos los palos de escoba. Se pueden poner **directamente en la clase**
(fuera de cualquier método), y todos los objetos los ven:
"""),

code(r"""class Pelota:
    GRAVEDAD = 10                       # atributo de la CLASE: lo comparten todas las pelotas

    def __init__(self, altura):
        self.altura = altura            # atributo del OBJETO: cada pelota tiene el suyo
        self.velocidad = 0.0

    def paso(self, dt):
        self.velocidad = self.velocidad + self.GRAVEDAD * dt
        self.altura = self.altura - self.velocidad * dt

a = Pelota(2.0)
b = Pelota(5.0)
for i in range(5):
    a.paso(0.1)
    b.paso(0.1)
print(f"a: {a.altura:.2f} m | b: {b.altura:.2f} m | gravedad de ambas: {Pelota.GRAVEDAD}")"""),

md(r"""Las dos pelotas comparten la gravedad (atributo de clase), pero cada una tiene su altura y su velocidad (atributos de objeto), y caen por su cuenta. Fíjate en lo
cómodo que es `a.paso(0.1)`: la pelota **se actualiza a sí misma**, sin tener que pasarle ni recoger su estado. Compara con el `paso_pelota(altura, velocidad)` del NB10.
"""),

md(r"""## 9 · Lo privado y las propiedades

En Python no hay atributos "prohibidos": desde fuera se puede leer y cambiar cualquier cosa de un objeto. Pero hay una **convención**: un atributo cuyo nombre empieza por
**un guion bajo** (`self._velocidad`) significa "**esto es de uso interno; no lo toques desde fuera**". Todo el mundo la respeta.

Y a veces quieres algo que **parezca un atributo** pero que se **calcule** al pedirlo. Para eso existe el decorador **`@property`** (¡un decorador, NB23!): convierte un
método en algo que se lee como un atributo, **sin paréntesis**:
"""),

code(r"""import math

class Torso:
    def __init__(self, altura, inclinacion_grados):
        self.altura = altura
        self.inclinacion_grados = inclinacion_grados

    @property
    def esta_caido(self):
        return self.altura < 1.0              # la regla del humanoide (NB03)

    @property
    def inclinacion_radianes(self):
        return math.radians(self.inclinacion_grados)

torso = Torso(1.3, 30)
print(torso.esta_caido)                  # sin paréntesis: se lee como un atributo
print(round(torso.inclinacion_radianes, 4))
torso.altura = 0.8
print(torso.esta_caido)                  # se recalcula solo"""),

md(r"""`torso.esta_caido` se lee como un dato, pero **se calcula cada vez**, así que siempre está al día (al bajar la altura a 0,8, pasa a `True` sin hacer nada más).

(`math.radians` convierte grados en **radianes**, otra forma de medir ángulos que usan casi todos los simuladores, MuJoCo incluido: una vuelta entera son 360 grados o unos
6,28 radianes, que es 2π. La veremos con calma en la parte de física; por ahora, solo saber que existe.)
"""),

md(r"""## 10 · Proyecto: el palo de escoba como objeto

Ahora sí. Vamos a reescribir el entorno del NB11 como una **clase**, con la **misma interfaz que Gymnasium** (NB15): un método `reset` que devuelve la observación y
un diccionario `info`, y un método `step` que devuelve **cinco** cosas (observación, recompensa, terminado, truncado, info).

Y de paso arreglamos un problema del NB11. ¿Recuerdas que en la búsqueda aleatoria tuvimos que inventar **todos** los candidatos antes de empezar, porque `random.seed`
dentro de cada episodio "mezclaba los dados" del viento con los de la búsqueda? Era porque todo usaba **el mismo** generador de azar, el general de Python. Con objetos,
cada palo puede llevar **su propio** generador de azar: `random.Random(semilla)` fabrica un **objeto** generador independiente (¡`Random` es una clase!), con sus propios
métodos `uniform`, etc., que no se mezcla con ningún otro.
"""),

code(r"""import random

class PaloDeEscoba:
    PASO_TIEMPO = 0.02
    EMPUJE_MAXIMO = 40
    CAIDA = 30
    PASOS_MAXIMOS = 500

    def __init__(self, viento_maximo=30):
        self.viento_maximo = viento_maximo
        self.inclinacion = 0.0
        self.velocidad = 0.0
        self.pasos = 0
        self._azar = random.Random(0)          # su PROPIO generador de azar

    def reset(self, seed=None):
        if seed is not None:
            self._azar = random.Random(seed)   # mismo nombre de parámetro que en Gymnasium
        self.inclinacion = 2.0
        self.velocidad = 0.0
        self.pasos = 0
        return self._observacion(), {}

    def step(self, empuje):
        empuje = max(-self.EMPUJE_MAXIMO, min(self.EMPUJE_MAXIMO, empuje))
        viento = self._azar.uniform(-self.viento_maximo, self.viento_maximo)
        aceleracion = 10 * self.inclinacion + empuje + viento
        self.velocidad = self.velocidad + aceleracion * self.PASO_TIEMPO
        self.inclinacion = self.inclinacion + self.velocidad * self.PASO_TIEMPO
        self.pasos = self.pasos + 1

        terminado = abs(self.inclinacion) > self.CAIDA
        truncado = self.pasos >= self.PASOS_MAXIMOS
        recompensa = 0.0 if terminado else 1 - (self.inclinacion / self.CAIDA) ** 2
        info = {"viento": viento, "empuje_aplicado": empuje}
        return self._observacion(), recompensa, terminado, truncado, info

    def _observacion(self):
        return (self.inclinacion, self.velocidad)

    def __repr__(self):
        return f"PaloDeEscoba(inclinacion={self.inclinacion:.2f}, velocidad={self.velocidad:.2f}, pasos={self.pasos})"
"""),

md(r"""Léela con calma: no hay **nada** nuevo en la física; es la del NB11, metida en una clase. Fíjate en:

- Las **constantes** son atributos de clase (apartado 8).
- El estado (`inclinacion`, `velocidad`, `pasos`) son atributos del objeto: cada palo tiene el suyo.
- `_azar` y `_observacion` empiezan por guion bajo: son "de uso interno" (apartado 9).
- `reset(seed=...)` usa el mismo nombre de parámetro que Gymnasium, `seed` ("semilla" en inglés), para que se use **igual**.
- `step` devuelve las **cinco** cosas de Gymnasium, y el `info` es un diccionario con datos extra (NB21).

Probémoslo: un palo, reiniciado con la semilla 0, y un paso sin empujar:
"""),

code(r"""palo = PaloDeEscoba()
observacion, info = palo.reset(seed=0)
print(palo)
observacion, recompensa, terminado, truncado, info = palo.step(0)
print(palo)
print(f"recompensa {recompensa:.4f} | viento {info['viento']:.2f}")"""),

md(r"""El objeto lleva la cuenta él solo de su estado (gracias al `__repr__`, lo vemos de un vistazo). ¿Y dos palos a la vez? Trivial:"""),

code(r"""palo_a = PaloDeEscoba()
palo_b = PaloDeEscoba(viento_maximo=60)     # ¡este, con el doble de viento!
palo_a.reset(seed=1)
palo_b.reset(seed=1)
for i in range(20):
    palo_a.step(0)
    palo_b.step(0)
print(palo_a)
print(palo_b)"""),

md(r"""Dos palos independientes, cada uno con su estado, su viento y su generador de azar. Con funciones sueltas, esto requeriría el doble de variables.
"""),

md(r"""## 11 · La política como objeto: `__call__`

Ahora la política. Podríamos usar la fábrica de políticas del NB23 (un cierre). Pero hay otra forma, muy usada: una **clase** con un método especial, **`__call__`**,
que hace que los objetos se puedan **llamar como si fueran funciones**:
"""),

code(r"""class PoliticaLineal:
    def __init__(self, k, d):
        self.k = k
        self.d = d

    def __call__(self, observacion):
        inclinacion, velocidad = observacion
        return -self.k * inclinacion - self.d * velocidad

    def __repr__(self):
        return f"PoliticaLineal(k={self.k}, d={self.d})"

politica = PoliticaLineal(30, 8)
print(politica)
print(politica((2.0, 0.0)))        # ¡el objeto se llama como una función!"""),

md(r"""`politica((2.0, 0.0))` llama al `__call__` del objeto. Por fuera, se usa como una función; por dentro, es un objeto con sus ruedecillas **a la vista** (`politica.k`, que
con un cierre quedaban escondidas) y que podría tener más métodos (guardarse, describirse, mejorarse...).

**Esto es exactamente cómo funcionan las redes neuronales de PyTorch**: una red es un objeto con sus pesos como atributos, y para usarla se la "llama" como a una función,
`red(observacion)`, que por dentro ejecuta su método... `__call__`. Cuando lo veas, ya sabrás qué pasa.
"""),

md(r"""## 12 · El bucle de un episodio, con objetos

Juntemos entorno y política. El bucle de un episodio queda así, y fíjate en que es **idéntico** al que se escribe con el humanoide de Gymnasium (NB15):
"""),

code(r"""def jugar_episodio(entorno, politica, semilla):
    observacion, info = entorno.reset(seed=semilla)
    retorno = 0.0
    while True:
        accion = politica(observacion)
        observacion, recompensa, terminado, truncado, info = entorno.step(accion)
        retorno = retorno + recompensa
        if terminado or truncado:
            return retorno, entorno.pasos

def evaluar(entorno, politica, semillas=range(5)):
    retornos = [jugar_episodio(entorno, politica, s)[0] for s in semillas]
    return sum(retornos) / len(retornos)

entorno = PaloDeEscoba()
for politica in [PoliticaLineal(0, 0), PoliticaLineal(30, 0), PoliticaLineal(30, 8)]:
    print(f"{politica}: {evaluar(entorno, politica):.1f}")"""),

md(r"""¡**44,8**, **296,0** y **499,9**! Exactamente los resultados del NB11 (nada, solo inclinación, a mano). Hemos reorganizado el código entero en objetos sin cambiar el
comportamiento. (Salen idénticos porque `random.Random(semilla)` produce la misma secuencia que `random.seed(semilla)`: es la misma receta de azar, NB11, solo que en un
generador propio.)

Fíjate en el `while True:` con un `return` dentro: es un bucle "infinito" que siempre termina, porque el entorno **garantiza** que acabará truncado a los 500 pasos (el límite
de seguridad del NB22 está dentro del propio entorno).

Ahora, ese bucle sirve para **cualquier** entorno que tenga `reset` y `step`, y para **cualquier** política que se pueda llamar con una observación. En el NB25 lo
comprobaremos haciendo que nuestro palo de escoba sea un entorno **oficial** de Gymnasium.
"""),

md(r"""## 13 · Clases de datos: `@dataclass`

Muchas clases sirven solo para **guardar datos** con nombre, como la configuración de un entrenamiento. Escribir su `__init__` (con un `self.x = x` por cada dato) y su
`__repr__` es repetitivo. Python trae un decorador que los escribe **solos**: **`@dataclass`**, del módulo `dataclasses`. Solo hay que listar los atributos con su tipo
(NB23) y, si quieres, su valor por defecto:
"""),

code(r"""from dataclasses import dataclass, field

@dataclass
class Configuracion:
    entorno: str = "palo de escoba"
    tasa: float = 0.0003
    pasos_totales: int = 1_000_000
    semillas: list = field(default_factory=lambda: [0, 1, 2, 3, 4])

config = Configuracion(tasa=0.001)
print(config)
print(config.tasa, config.semillas)"""),

md(r"""Sin escribir `__init__` ni `__repr__`, la clase ya acepta sus datos (por nombre o por orden), con sus valores por defecto, y se muestra legible.

¿Y ese `field(default_factory=...)` raro de las semillas? ¡Es la **trampa del valor por defecto mutable** del NB23! Una lista como valor por defecto se compartiría entre
todos los objetos. `field(default_factory=...)` le da a `dataclass` una **función** (aquí, una `lambda`) que fabrica una lista **nueva** para cada objeto. De hecho, si
intentas poner `semillas: list = [0, 1, 2]` directamente, `dataclass` te para con un `ValueError`: se sabe la trampa.

Las *dataclasses* son perfectas para configuraciones y resultados, y las verás mucho.
"""),

md(r"""## 14 · En Python, todo es un objeto

Para terminar, una idea que une todo: en Python, **absolutamente todo es un objeto**: números, cadenas, listas, funciones (NB23), módulos (como `math`), clases... Cada
uno es de alguna clase, y `isinstance` pregunta "¿es de esta clase?" (lo usamos en el NB21 y el NB23):
"""),

code(r"""print(isinstance(3.5, float))
print(isinstance(politica, PoliticaLineal))
print(isinstance(entorno, PaloDeEscoba))
print([nombre for nombre in dir(entorno) if not nombre.startswith("__")])"""),

md(r"""`dir(objeto)` lista **todo** lo que tiene un objeto (atributos y métodos); hemos filtrado los especiales (los que empiezan por `__`) para ver solo los nuestros. Es una
herramienta muy útil para **explorar** objetos que no conoces: por ejemplo, `dir(entorno_de_gymnasium)` te enseña todo lo que puedes hacer con él. (Junto con `help`, NB23,
son tus dos linternas para orientarte en código ajeno.)
"""),

md(r"""## 15 · Resumen de la lección

1. Una **clase** (`class Nombre:`) es un **molde** que junta datos y comportamiento; un **objeto** o **instancia** (`Nombre(...)`) es una cosa concreta fabricada con él. Nombres
   de clases en `CadaPalabraConMayuscula`.
2. **`__init__(self, ...)`** se ejecuta al crear el objeto y guarda sus **atributos** (`self.x = x`). **`self`** es "este objeto concreto". Los **métodos** son funciones de la clase
   que reciben `self`; se llaman `objeto.metodo(...)` (sin pasar `self`). Si un atributo no existe: `AttributeError`.
3. Métodos especiales: **`__repr__`** (cómo se muestra), **`__call__`** (llamar al objeto como a una función). Atributos **de clase** (compartidos) y **de objeto** (propios).
   `_nombre` = uso interno; **`@property`** = atributo que se calcula.
4. Proyecto: **`PaloDeEscoba`** con `reset(seed)` y `step(accion)` al estilo Gymnasium (5 valores), con su propio **`random.Random`**; **`PoliticaLineal`** con `__call__` (como las redes
   de PyTorch); el mismo bucle de episodio que con el humanoide da **44,8 / 296,0 / 499,9**, como en el NB11.
5. **`@dataclass`** fabrica clases de datos (y obliga a usar `field(default_factory=...)` para listas). Todo es un objeto: `type`, `isinstance`, `dir`.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Clase** | Un molde: la descripción de un tipo de cosa (datos + comportamiento). |
| **Objeto / instancia** | Una cosa concreta fabricada con una clase. |
| **`__init__`** | El método que prepara cada objeto al crearlo. |
| **`self`** | "Este objeto concreto", dentro de los métodos. |
| **Atributo** | Un dato guardado en un objeto: `objeto.nombre`. |
| **Método** | Una función de una clase: `objeto.metodo()`. |
| **Método especial** | Métodos con `__` a cada lado que Python llama solo (`__init__`, `__repr__`, `__call__`...). |
| **Atributo de clase** | Un dato compartido por todos los objetos de la clase. |
| **`@property`** | Convierte un método en algo que se lee como un atributo. |
| **`AttributeError`** | Error por pedir un atributo o método que el objeto no tiene. |
| **`@dataclass`** | Decorador que fabrica clases de datos automáticamente. |
| **`isinstance` / `dir`** | ¿Es de esta clase? / ¿Qué tiene este objeto? |
"""),

md(r"""## 16 · Ejercicios

**E1.** Crea una clase `Motor` con atributos `nombre` y `fuerza_maxima`, y un método `recortar(par)` que devuelva el par limitado a ±`fuerza_maxima`. Fabrica la rodilla (200)
y el codo (25) y prueba `recortar(150)` en los dos.

**E2.** Añade a `Motor` un `__repr__` que muestre algo como `Motor('rodilla', 200)`.

**E3.** Explica qué es `self` en `humanoide.describir()` y por qué no hay que pasarlo entre los paréntesis.

**E4.** Crea una clase `Contador` con un método `sumar()` que aumente en 1 un atributo `cuenta` (que empieza en 0). Fabrica dos contadores, suma 3 veces en uno y 1 en el otro,
y muestra los dos.

**E5.** Añade a `PaloDeEscoba` una propiedad `esta_derecho` que sea `True` si la inclinación está entre −1 y 1 grados.

**E6.** Escribe una `PoliticaAzar` (con `__call__`) que devuelva un empuje al azar entre −40 y 40 usando **su propio** generador `random.Random(semilla)`, y evalúala con
`evaluar`. ¿Sale algo parecido a los ~43 puntos del NB11?

**E7.** **Reto.** Crea con `@dataclass` una clase `Resultado` con `nombre: str`, `retornos: list` (con `field(default_factory=list)`) y una **propiedad** `media`. Guarda los
resultados de las tres políticas del apartado 12 y muéstralos ordenados por media.
"""),

md(r"""<details>
<summary>▶ Solución E1 y E2</summary>

```python
class Motor:
    def __init__(self, nombre, fuerza_maxima):
        self.nombre = nombre
        self.fuerza_maxima = fuerza_maxima

    def recortar(self, par):
        return max(-self.fuerza_maxima, min(self.fuerza_maxima, par))

    def __repr__(self):
        return f"Motor({self.nombre!r}, {self.fuerza_maxima})"

rodilla = Motor("rodilla", 200)
codo = Motor("codo", 25)
print(rodilla, rodilla.recortar(150))     # Motor('rodilla', 200) 150
print(codo, codo.recortar(150))           # Motor('codo', 25) 25
```

El mismo método recorta distinto según el objeto: la rodilla aguanta 150, el codo se queda en 25 (NB01: los motores de las piernas son mucho más fuertes).
</details>

<details>
<summary>▶ Solución E3</summary>

`self` es **el objeto `humanoide`**. Al escribir `humanoide.describir()`, Python llama por dentro a `Robot.describir(humanoide)`: pone automáticamente como primer argumento el objeto
que está a la izquierda del punto. Por eso dentro del método, `self.nombre` es el nombre de **ese** robot, y por eso no hay que escribirlo entre los paréntesis.
</details>

<details>
<summary>▶ Solución E4</summary>

```python
class Contador:
    def __init__(self):
        self.cuenta = 0

    def sumar(self):
        self.cuenta = self.cuenta + 1

a = Contador()
b = Contador()
for i in range(3):
    a.sumar()
b.sumar()
print(a.cuenta, b.cuenta)     # 3 1
```

Cada contador tiene su propia `cuenta`: son objetos independientes.
</details>

<details>
<summary>▶ Solución E5</summary>

Dentro de la clase `PaloDeEscoba`, añade:

```python
    @property
    def esta_derecho(self):
        return -1 < self.inclinacion < 1
```

(y vuelve a ejecutar la celda de la clase). Después, `palo.esta_derecho` (sin paréntesis) dirá si el palo está casi vertical en ese momento.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
class PoliticaAzar:
    def __init__(self, semilla=0):
        self._azar = random.Random(semilla)

    def __call__(self, observacion):
        return self._azar.uniform(-40, 40)

print(f"{evaluar(entorno, PoliticaAzar()):.1f}")
```

Sale un retorno bajo, del orden de los ~43 puntos del NB11 (no idéntico, porque ahora el azar de la política va por su propio generador, separado del viento: ¡los dados ya no se
mezclan!). Moverse al azar sigue siendo tan malo como no hacer nada.
</details>

<details>
<summary>▶ Solución E7</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Resultado:
    nombre: str
    retornos: list = field(default_factory=list)

    @property
    def media(self):
        return sum(self.retornos) / len(self.retornos)

resultados = []
for politica in [PoliticaLineal(0, 0), PoliticaLineal(30, 0), PoliticaLineal(30, 8)]:
    r = Resultado(nombre=repr(politica))
    for semilla in range(5):
        r.retornos.append(jugar_episodio(entorno, politica, semilla)[0])
    resultados.append(r)

for r in sorted(resultados, key=lambda r: r.media, reverse=True):
    print(f"{r.nombre}: {r.media:.1f}")
```

Las dataclasses también pueden tener métodos y propiedades: son clases normales, solo que con el `__init__` y el `__repr__` hechos.
</details>
"""),

md(r"""## 17 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has aprendido a construir tus propios objetos, y has convertido el palo de escoba en un entorno con la misma forma que los de Gymnasium. En el **NB25** veremos la otra mitad de
las clases: la **herencia** (una clase que "hereda" todo de otra y cambia solo lo que necesita, que es como se construyen **todos** los entornos de Gymnasium y **todas** las redes
de PyTorch), más métodos especiales para que tus objetos se sumen o se midan con `len`. Y el gran final: convertiremos el palo de escoba en un **entorno oficial de Gymnasium**,
que pasará el verificador de Gymnasium y se podrá crear con `gym.make`, igual que el humanoide.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB24_python_clases.ipynb")
    build(out, cells, title="NB24 · Python de verdad (5): clases y objetos (I)")
