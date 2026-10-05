"""Construye NB44·P3 · Puente de Python (3): clases intermedias.

El "modelo de datos" de Python: los operadores y funciones incorporadas
llaman a métodos especiales. Una clase Trayectoria construida paso a paso:
__repr__ frente a __str__, __len__, __getitem__ (enteros, negativos y
porciones), iteración gratis, __contains__, __bool__, __add__ (y
NotImplemented). Igualdad frente a identidad, __eq__ y __hash__ (por qué un
objeto con __eq__ deja de poder ir en un set). Propiedades con validación
(setter) y calculadas. @classmethod (constructores alternativos) frente a
@staticmethod. Dataclasses a fondo: field (default_factory, repr, init),
__post_init__ (validar y derivar), frozen y hash, order=True, asdict/replace,
slots, y la trampa de __eq__ con arrays. Enum/IntEnum/auto. NamedTuple frente a
dataclass frente a dict. Composición frente a herencia. Laboratorio.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB44·P3 · Puente de Python (3): clases intermedias

**Puente de Python — Lección 3 de 6**

> En el NB24 y el NB25 aprendiste a escribir clases: `__init__`, `self`, métodos, `__repr__`, `@property`, herencia, `@dataclass`... Lo justo para escribir un entorno de Gymnasium. En el NB45, el NB47 y el NB48 aparecieron de golpe dataclasses congeladas, `@classmethod`, `__call__`, `NamedTuple`, `IntEnum`, composición... Hoy rellenamos el hueco.

La pregunta que guía la lección: **¿cómo consiguen los objetos de NumPy, de MuJoCo o de PyTorch comportarse como si fueran parte del propio Python?** ¿Cómo es que puedes escribir `len(array)`, `array[2:5]`, `for x in array`, `a + b` o `a == b` con objetos que no son listas ni números? La respuesta tiene nombre: el **modelo de datos** de Python, y la vas a dominar hoy.
"""),

code(r"""import os
os.environ["MUJOCO_GL"] = "egl"
import numpy as np
import mujoco

PENDULO = '''
<mujoco>
  <compiler angle="radian"/>
  <worldbody>
    <body pos="0 0 1">
      <joint name="bisagra" type="hinge" axis="0 1 0" damping="0.05"/>
      <geom type="capsule" fromto="0 0 0  0 0 -0.5" size="0.02" mass="1"/>
    </body>
  </worldbody>
</mujoco>
'''
modelo = mujoco.MjModel.from_xml_string(PENDULO)"""),

md(r"""## 1 · El modelo de datos: los métodos especiales

### Python traduce los operadores a métodos

Cuando escribes `len(x)`, Python no sabe medir "cosas" en general. Lo que hace es **llamar a un método** del objeto: `x.__len__()`. Cuando escribes `a + b`, llama a `a.__add__(b)`. Cuando escribes `x[3]`, a `x.__getitem__(3)`. Estos métodos con doble guion bajo a cada lado se llaman **métodos especiales** (o *dunder methods*, de *double underscore*), y ya conoces algunos: `__init__`, `__repr__`, `__call__` (NB24), `__truediv__` (la `/` de `pathlib`, NB26).

Compruébalo con una lista normal:
"""),

code(r"""lista = [10, 20, 30]
print(len(lista), lista.__len__())
print(lista[1], lista.__getitem__(1))
print(lista + [40], lista.__add__([40]))
print(20 in lista, lista.__contains__(20))"""),

md(r"""Son **exactamente** lo mismo: la sintaxis bonita (`len`, `[]`, `+`, `in`) es una **traducción** a métodos especiales. Y aquí está el poder: si **tu** clase define esos métodos, **tus** objetos funcionan con esa misma sintaxis. Así lo hacen NumPy (`ndarray` define `__add__`, `__getitem__`, `__len__`...), MuJoCo y todas las bibliotecas.

La tabla de los más útiles:

| Escribes | Python llama a | Para |
|---|---|---|
| `repr(x)`, en la consola | `x.__repr__()` | texto para programadores (sin ambigüedad) |
| `str(x)`, `print(x)` | `x.__str__()` | texto para humanos |
| `len(x)` | `x.__len__()` | tamaño |
| `x[i]`, `x[a:b]` | `x.__getitem__(i)` | acceso por índice o porción |
| `for e in x` | `x.__iter__()` | recorrer |
| `e in x` | `x.__contains__(e)` | pertenencia |
| `bool(x)`, `if x:` | `x.__bool__()` (o `__len__`) | ¿es "verdadero"? |
| `x == y` | `x.__eq__(y)` | igualdad |
| `hash(x)` | `x.__hash__()` | usarlo como clave de diccionario o en un `set` |
| `x + y` | `x.__add__(y)` | suma (y `__sub__`, `__mul__`, `__matmul__` para `@`...) |
| `x(...)` | `x.__call__(...)` | llamarlo como una función |
| `with x:` | `x.__enter__()` / `x.__exit__()` | gestor de contexto (P4) |

No hay que aprenderse la tabla: hay que saber que **existe**, y buscarla cuando haga falta.
"""),

md(r"""## 2 · Una clase Trayectoria, paso a paso

### El problema

En robótica grabamos **trayectorias** todo el rato: la lista de estados de una simulación, con sus tiempos. Hasta ahora usábamos listas sueltas (`tiempos = []`, `angulos = []`). Vamos a construir una clase `Trayectoria` que se comporte como una colección de Python de verdad. Empezamos por lo mínimo, y en cada paso añadimos un método especial y vemos qué **gana**.
"""),

code(r"""class Trayectoria:
    def __init__(self, nombre: str = "sin nombre"):
        self.nombre = nombre
        self.tiempos: list[float] = []
        self.estados: list[np.ndarray] = []

    def grabar(self, tiempo: float, estado: np.ndarray) -> None:
        self.tiempos.append(float(tiempo))
        self.estados.append(np.array(estado, dtype=float))     # ¡una COPIA! (trampa del alias, NB45)


def simular_pendulo(q0: float, segundos: float = 2.0) -> Trayectoria:
    d = mujoco.MjData(modelo)
    d.qpos[0] = q0
    tray = Trayectoria(f"péndulo desde {q0} rad")
    for paso in range(int(round(segundos / modelo.opt.timestep))):
        mujoco.mj_step(modelo, d)
        if paso % 50 == 0:                                   # grabamos cada 0,1 s
            tray.grabar(d.time, [d.qpos[0], d.qvel[0]])
    return tray

t1 = simular_pendulo(1.0)
print(t1)"""),

md(r"""Funciona, pero `print(t1)` da `<__main__.Trayectoria object at 0x7f...>`: inútil. Es lo que Python imprime cuando una clase no dice cómo mostrarse.

### Paso 1: __repr__ y __str__

Hay **dos** formas de convertir un objeto en texto:

- **`__repr__`**: para **programadores**. Debe ser **sin ambigüedad**, idealmente algo que parezca el código para crear el objeto. Es lo que muestra la consola y lo que aparece dentro de listas.
- **`__str__`**: para **humanos**. Más bonito. Es lo que usa `print`. Si no lo defines, `print` usa `__repr__`.

La regla práctica: **define siempre `__repr__`**; define `__str__` solo si quieres algo distinto para mostrar a usuarios.
"""),

code(r"""class Trayectoria(Trayectoria):          # heredamos de la versión anterior y le añadimos cosas (NB25)
    def __repr__(self) -> str:
        return f"Trayectoria({self.nombre!r}, {len(self.tiempos)} muestras)"

    def __str__(self) -> str:
        if not self.tiempos:
            return f"«{self.nombre}» (vacía)"
        return f"«{self.nombre}»: {len(self.tiempos)} muestras de {self.tiempos[0]:.2f} s a {self.tiempos[-1]:.2f} s"

t1 = simular_pendulo(1.0)
print(t1)                 # usa __str__
print(repr(t1))           # usa __repr__
print([t1, t1])           # dentro de una lista, Python usa __repr__ para cada elemento"""),

md(r"""(Un truco de esta lección: `class Trayectoria(Trayectoria):` crea una clase **nueva** que hereda de la anterior y la amplía, con el mismo nombre. Así no repetimos el código de cada paso. En un proyecto real escribirías la clase completa de una vez.)

El `!r` dentro del f-string usa `repr` del nombre, para que salga **entre comillas**: `Trayectoria('péndulo desde 1.0 rad', 20 muestras)`. Así se ve que es un texto.

### Paso 2: __len__ y __getitem__
"""),

code(r"""class Trayectoria(Trayectoria):
    def __len__(self) -> int:
        return len(self.tiempos)

    def __getitem__(self, indice):
        if isinstance(indice, slice):                       # t[a:b]: devolvemos OTRA trayectoria
            nueva = Trayectoria(f"{self.nombre} [{indice.start}:{indice.stop}]")
            nueva.tiempos = self.tiempos[indice]
            nueva.estados = self.estados[indice]
            return nueva
        return self.tiempos[indice], self.estados[indice]     # t[i]: una pareja (tiempo, estado)

t1 = simular_pendulo(1.0)
print("len:", len(t1))
print("primera muestra:", t1[0])
print("última muestra: ", t1[-1])
print("una porción:    ", repr(t1[5:10]))"""),

md(r"""Mira todo lo que hemos ganado con dos métodos:

- **`len(t1)`** funciona.
- **`t1[0]`**, y también **`t1[-1]`**: los índices negativos funcionan **gratis**, porque se los pasamos a una lista, que ya sabe tratarlos.
- **`t1[5:10]`**: cuando escribes una porción, Python llama a `__getitem__` con un objeto **`slice`** (porción), que tiene `.start`, `.stop` y `.step`. Lo detectamos con `isinstance` y devolvemos **otra trayectoria**, como hace NumPy (una porción de un array es un array, no una lista).

Y hay un regalo escondido. Prueba a **recorrerla**:
"""),

code(r"""for tiempo, (angulo, velocidad) in t1[:3]:
    print(f"t = {tiempo:.3f} s: ángulo {angulo:+.3f}, velocidad {velocidad:+.3f}")"""),

md(r"""¡Se puede recorrer con `for`, y no hemos escrito `__iter__`! Si una clase no tiene `__iter__` pero sí `__getitem__` con enteros, Python la recorre llamando a `t[0]`, `t[1]`, `t[2]`... hasta que salta un `IndexError`. Es un mecanismo antiguo, que sigue funcionando. (Lo moderno y recomendable es escribir `__iter__`, normalmente como generador: lo haremos en el P4.)

Fíjate también en el **desempaquetado anidado** del `for` (NB21): cada elemento es `(tiempo, estado)`, y el estado tiene dos números, así que `tiempo, (angulo, velocidad)` lo abre todo de una vez.

### Paso 3: __bool__, __contains__ y __add__
"""),

code(r"""class Trayectoria(Trayectoria):
    def __bool__(self) -> bool:
        return len(self) > 0                                  # vacía = falsa, como las listas

    def __contains__(self, tiempo: float) -> bool:
        return any(abs(t - tiempo) < 1e-9 for t in self.tiempos)   # ¿hay una muestra en ese instante?

    def __add__(self, otra):
        if not isinstance(otra, Trayectoria):
            return NotImplemented                             # "no sé sumarme con eso"
        suma = Trayectoria(f"{self.nombre} + {otra.nombre}")
        suma.tiempos = self.tiempos + otra.tiempos
        suma.estados = self.estados + otra.estados
        return suma

t1, t2 = simular_pendulo(1.0), simular_pendulo(0.5)
print("¿vacía es falsa?", bool(Trayectoria()), "| ¿t1 es verdadera?", bool(t1))
print("¿hay muestra en t = 0,302 s?", 0.302 in t1, "| ¿y en 0,3?", 0.3 in t1)
print(repr(t1 + t2))"""),

md(r"""- **`__bool__`**: ahora `if trayectoria:` significa "si tiene muestras", igual que con una lista (P1, predicción 8). (Si no defines `__bool__` pero sí `__len__`, Python usa `len(x) > 0`: ya funcionaba. Lo hemos escrito para verlo.)
- **`__contains__`**: `0.302 in t1` pregunta si hay una muestra en ese instante. Grabamos tras el primer paso y cada 50 pasos de 0,002 s, así que los tiempos son 0,002; 0,102; 0,202; 0,302... por eso 0,3 no está. (Y comparamos con tolerancia, nunca con `==`: P1, R11.)
- **`__add__`**: `t1 + t2` concatena. Si alguien intenta `t1 + 5`, devolvemos **`NotImplemented`** (una constante especial, no un error): le dice a Python "yo no sé; pregúntale al otro", y Python intentará `5.__radd__(t1)` y, si tampoco, lanzará un `TypeError` claro:
"""),

code_err(r"""t1 + 5"""),

md(r"""`TypeError: unsupported operand type(s) for +: 'Trayectoria' and 'int'`. Un mensaje perfecto, y lo ha escrito Python por nosotros gracias al `NotImplemented`.

### Lo que hemos construido

Una clase de unas 40 líneas que funciona con `print`, `len`, índices, porciones, `for`, `if`, `in` y `+`. Es lo que se llama un objeto **"pitónico"**: se usa como cualquier objeto de Python, sin tener que aprender métodos raros. Este es el secreto de las buenas bibliotecas.
"""),

md(r"""## 3 · Igualdad, identidad y hash

### == frente a is

Dos preguntas distintas (NB21):

- **`a is b`**: ¿son **el mismo objeto**? (identidad)
- **`a == b`**: ¿son **iguales**? (igualdad, y la decide `__eq__`)

Por defecto, una clase **no** sabe qué significa "igual", y `==` se comporta como `is`:
"""),

code(r"""class Objetivo:
    def __init__(self, x: float, z: float):
        self.x, self.z = x, z

a, b = Objetivo(0.3, 0.1), Objetivo(0.3, 0.1)
print(a == b, a is b)"""),

md(r"""`False`: aunque tienen los mismos números, son dos objetos distintos, y sin `__eq__` Python solo compara identidades. Definamos qué significa ser iguales:
"""),

code(r"""class Objetivo:
    def __init__(self, x: float, z: float):
        self.x, self.z = x, z

    def __eq__(self, otro) -> bool:
        if not isinstance(otro, Objetivo):
            return NotImplemented
        return (self.x, self.z) == (otro.x, otro.z)

a, b = Objetivo(0.3, 0.1), Objetivo(0.3, 0.1)
print(a == b, a is b)"""),

md(r"""Ahora `a == b` es verdadero (y siguen siendo objetos distintos). El truco de comparar **tuplas** `(self.x, self.z) == (otro.x, otro.z)` es la forma corta de comparar varios campos a la vez.

### La sorpresa: ya no cabe en un set

Probemos a meter objetivos en un conjunto (NB21), por ejemplo para quitar duplicados:
"""),

code_err(r"""{a, b}"""),

md(r"""`TypeError: unhashable type: 'Objetivo'`. ¿Qué ha pasado? Antes de definir `__eq__`, sí se podía.

Los conjuntos y los diccionarios funcionan con **hash** (NB21): un número que se calcula a partir del objeto y que dice "en qué cajón" guardarlo, para encontrarlo al instante. La regla de oro es: **si dos objetos son iguales (`==`), su hash debe ser igual**. Si no, el conjunto podría guardar dos objetos "iguales" en cajones distintos.

Por defecto, el hash se calcula a partir de la **identidad** (la dirección en memoria). Eso era coherente con el `==` por defecto (que también era identidad). Pero al definir tu propio `__eq__`, el hash por identidad ya **no** sería coherente: `a == b`, pero estarían en cajones distintos. Así que Python, para protegerte, **quita** el hash (`__hash__ = None`) en cuanto defines `__eq__`. Si quieres que se pueda usar en conjuntos, tienes que definir un `__hash__` coherente:
"""),

code(r"""class Objetivo(Objetivo):
    def __hash__(self) -> int:
        return hash((self.x, self.z))              # el hash de la tupla de los MISMOS campos que __eq__

a, b, c = Objetivo(0.3, 0.1), Objetivo(0.3, 0.1), Objetivo(0.5, 0.1)
print(len({a, b, c}), "objetivos distintos")"""),

md(r"""Dos objetivos distintos: `a` y `b` cuentan como uno. Pero hay una condición más, muy importante: **un objeto que se usa en un set o como clave no debe cambiar** después. Si cambias `a.x` mientras está en un conjunto, su hash cambia y el conjunto ya no lo encuentra. Por eso los objetos "hashables" suelen ser **inmutables** (números, textos, tuplas). Las dataclasses lo resuelven elegantemente con `frozen=True`, como veremos en la sección 5.
"""),

md(r"""## 4 · Propiedades, métodos de clase y métodos estáticos

### Propiedades con validación

En el NB24 viste `@property` para atributos **calculados** (de solo lectura). Una propiedad también puede tener un **setter**: un método que se ejecuta al **asignar**, ideal para **validar**. Por ejemplo, un motor que no acepta ganancias negativas (que harían inestable el control, NB40):
"""),

code(r"""class Motor:
    def __init__(self, kp: float, kv: float, par_maximo: float = 150.0):
        self.kp = kp                     # ← ¡esto ya pasa por el setter de abajo!
        self.kv = kv
        self.par_maximo = par_maximo

    @property
    def kp(self) -> float:
        return self._kp

    @kp.setter
    def kp(self, valor: float) -> None:
        if valor < 0:
            raise ValueError(f"kp debe ser positivo, no {valor}")
        self._kp = float(valor)

    @property
    def frecuencia(self) -> float:
        # Frecuencia natural (rad/s) con una inercia de 0,05 kg·m² (NB39b). Solo lectura.
        return (self.kp / 0.05) ** 0.5

motor = Motor(kp=300, kv=20)
print(motor.kp, round(motor.frecuencia, 1))
motor.kp = 100
print(motor.kp, round(motor.frecuencia, 1))"""),

code_err(r"""motor.kp = -5"""),

md(r"""Cómo funciona:

- `@property` encima de `def kp(self)` define cómo se **lee** `motor.kp`: devuelve el valor guardado en `self._kp` (con guion bajo: el atributo "de verdad", interno).
- `@kp.setter` encima de **otro** `def kp(self, valor)` define qué pasa al **asignar** `motor.kp = algo`: valida y guarda en `self._kp`.
- ¡Incluso en `__init__`! `self.kp = kp` pasa por el setter, así que `Motor(kp=-1, kv=1)` también falla. La validación está en **un solo sitio**.
- `frecuencia` no tiene setter: es de **solo lectura** (si intentas `motor.frecuencia = 3`, `AttributeError`). Se recalcula cada vez que se lee, así que siempre es coherente con `kp`.

Para quien usa la clase, `kp` parece un atributo normal. Esa es la gracia: puedes empezar con un atributo simple y, si más adelante necesitas validarlo, convertirlo en propiedad **sin cambiar el código** de nadie.

### @classmethod: constructores alternativos

Un **método de clase** recibe **la clase** (`cls`) en vez de un objeto (`self`). Su uso estrella (NB45): **constructores alternativos**, otras formas de crear objetos:
"""),

code(r"""class Motor(Motor):
    @classmethod
    def desde_dict(cls, config: dict) -> "Motor":
        return cls(kp=config["kp"], kv=config["kv"], par_maximo=config.get("par_maximo", 150.0))

    @classmethod
    def critico(cls, kp: float, inercia: float = 0.05) -> "Motor":
        # Un motor con amortiguamiento crítico: kv = 2·√(kp·I) (NB39b).
        return cls(kp=kp, kv=2 * (kp * inercia) ** 0.5)

    @staticmethod
    def par_a_corriente(par: float, constante: float = 0.1) -> float:
        # Utilidad: corriente necesaria para un par (par = constante · corriente, NB40).
        return par / constante

m1 = Motor.desde_dict({"kp": 200, "kv": 15})
m2 = Motor.critico(kp=300)
print(m1.kp, m1.kv, "|", m2.kp, round(m2.kv, 2))
print(Motor.par_a_corriente(15.0), "amperios")"""),

md(r"""- **`@classmethod`**: recibe `cls`, la clase, y la usa para crear el objeto (`cls(...)`). ¿Por qué `cls(...)` y no `Motor(...)`? Para que funcione con las **subclases**: si alguien hace `class MotorGrande(Motor)`, `MotorGrande.critico(300)` creará un `MotorGrande`, no un `Motor`. Ejemplos reales: `MjModel.from_xml_path(...)` y `MjSpec.from_file(...)` son constructores alternativos; `dict.fromkeys(...)` y `np.array(...)` también son de esta familia.
- **`@staticmethod`**: no recibe ni `self` ni `cls`. Es una función normal que vive dentro de la clase porque **tiene que ver** con ella. Se usa poco: muchas veces, una función normal en el módulo es igual de clara.
- La anotación `-> "Motor"` va **entre comillas** porque, mientras se define la clase, el nombre `Motor`... bueno, aquí ya existe (heredamos), pero dentro de la definición original aún no existiría. Las comillas le dicen al lector "es el tipo Motor" sin que Python lo busque todavía. (En el P5, la alternativa moderna, `Self`.)
"""),

md(r"""## 5 · Dataclasses a fondo

### Lo que ya sabes, y lo que falta

En el NB24 y el NB45 viste que `@dataclass` escribe por ti `__init__`, `__repr__` y `__eq__` a partir de los campos anotados. Vamos con todo lo demás, construyendo una **configuración de experimento**, el uso más típico de las dataclasses en robótica:
"""),

code(r"""from dataclasses import dataclass, field, asdict, replace

@dataclass
class Experimento:
    nombre: str
    kp: float = 300.0
    kv: float = 20.0
    semillas: list[int] = field(default_factory=lambda: [0, 1, 2])
    notas: str = field(default="", repr=False)
    pasos_totales: int = field(init=False)

    def __post_init__(self) -> None:
        if self.kp <= 0:
            raise ValueError(f"kp debe ser positivo, no {self.kp}")
        self.pasos_totales = 1000 * len(self.semillas)

e = Experimento("base", notas="primera prueba")
print(e)
print("pasos totales:", e.pasos_totales)"""),

md(r"""Las piezas nuevas:

- **`field(default_factory=...)`** (NB24): una **función** que fabrica el valor por defecto **para cada objeto**. Imprescindible para listas y diccionarios (la trampa del valor por defecto mutable, otra vez).
- **`field(repr=False)`**: el campo existe, pero **no** sale en el `repr` (útil para textos largos o datos enormes, como un array de 10.000 números).
- **`field(init=False)`**: el campo **no** es un argumento de `__init__`: se calcula después.
- **`__post_init__`**: un método que `@dataclass` llama **al final** de su `__init__` automático. Es el sitio para **validar** y para calcular campos **derivados** (como `pasos_totales`).
"""),

code_err(r"""Experimento("mal", kp=-10)"""),

md(r"""### asdict y replace
"""),

code(r"""print(asdict(e))                                   # a diccionario (para guardar en JSON, NB26)
e2 = replace(e, nombre="más rígido", kp=600)       # una COPIA con algunos campos cambiados
print(e2)
print("¿el original ha cambiado?", e.kp)"""),

md(r"""- **`asdict(objeto)`**: convierte la dataclass (y las que tenga dentro) en un diccionario. Con `json.dumps(asdict(e))` la guardas en un fichero de configuración.
- **`replace(objeto, campo=valor)`**: crea una **copia** con algunos campos cambiados, sin tocar el original. Perfecto para barridos: "el experimento base, pero con kp = 600". (Ojo: `replace` vuelve a llamar a `__init__` y a `__post_init__`, así que la validación y `pasos_totales` se recalculan.)

### frozen: inmutables (y hashables)

Con `frozen=True`, los campos no se pueden reasignar después de crear el objeto (NB45). Y como ya no pueden cambiar, `@dataclass` puede darles un **`__hash__`** seguro: ¡se pueden meter en conjuntos y usar como claves!
"""),

code(r"""@dataclass(frozen=True)
class Ganancias:
    kp: float
    kv: float

resultados = {Ganancias(300, 20): 0.86, Ganancias(600, 20): 0.91}     # ¡como CLAVES de diccionario!
print(resultados[Ganancias(300, 20)])
print(len({Ganancias(300, 20), Ganancias(300, 20), Ganancias(100, 5)}), "combinaciones distintas")"""),

code_err(r"""g = Ganancias(300, 20)
g.kp = 1"""),

md(r"""`FrozenInstanceError: cannot assign to field 'kp'`. Justo lo que pedíamos en la sección 3: `__eq__` y `__hash__` coherentes, y el objeto no puede cambiar mientras está en un diccionario. Para cambiar algo, `replace(g, kp=1)` crea uno nuevo.

### order: ordenar objetos

Con `order=True`, `@dataclass` escribe también `<`, `<=`, `>`, `>=`, comparando los campos **en orden**, como tuplas. Truco: pon primero el campo por el que quieras ordenar:
"""),

code(r"""@dataclass(order=True)
class Resultado:
    nota: float
    nombre: str = field(compare=False)            # no cuenta para comparar

carrera = [Resultado(412.0, "PPO"), Resultado(498.5, "PPO afinado"), Resultado(95.3, "azar")]
print(sorted(carrera))
print("el mejor:", max(carrera).nombre)"""),

md(r"""`field(compare=False)` saca un campo de las comparaciones (y de `==`): aquí ordenamos solo por `nota`.

### slots: más ligeras

Con `slots=True` (NB45), la dataclass no guarda sus atributos en un diccionario (`__dict__`) sino en "huecos" fijos: ocupa menos memoria, es un poco más rápida, y **prohíbe añadir atributos que no son campos** (lo que caza errores de escritura como `e.kpp = 3`). Recomendable para clases de las que crearás muchísimos objetos.

### La trampa de __eq__ con arrays

Y la trampa que viste en el NB45. Si un campo es un array de NumPy, el `==` automático **se comporta mal**:
"""),

code(r"""@dataclass
class Estado:
    tiempo: float
    qpos: np.ndarray

s1 = Estado(0.0, np.array([0.1, 0.2]))
s2 = Estado(0.0, np.array([0.1, 0.2]))"""),

code(r"""s3 = Estado(1.0, np.array([0.1, 0.2]))
print("s1 == s2 →", s1 == s2)
print("s1 == s3 →", s1 == s3)"""),

md(r"""¡`s1 == s2` no da `True`, sino **un array** `[True True]`! (Y `s1 == s3` sí da `False`.) ¿Qué pasa? En Python 3.13, el `__eq__` automático compara los campos uno a uno, encadenados con `and`: `(s1.tiempo == s2.tiempo) and (s1.qpos == s2.qpos)`. Y `and` devuelve el **último** valor si todos los anteriores son verdaderos (P1: evaluación de cortocircuito), que aquí es la comparación de dos arrays... que no es un booleano, sino un array de booleanos, uno por elemento (NB27). Con `s3`, el tiempo ya es distinto, el `and` se detiene ahí y devuelve `False`.

Parece inofensivo, hasta que lo usas donde Python necesita **un solo** booleano:
"""),

code_err(r"""if s1 == s2:
    print("iguales")"""),

md(r"""`ValueError: The truth value of an array with more than one element is ambiguous`: "¿es verdadero `[True, True]`? ¿Basta con que lo sea uno, o tienen que serlo todos?". Python no lo decide por ti (te sugiere `.any()` o `.all()`). Y si el array fuera el **primer** campo de la dataclass, el error saltaría ya en el propio `==`. Comportamiento distinto según el orden de los campos y según la versión de Python: una trampa de las buenas. Soluciones: `field(compare=False)` en el array (y compararlo a mano con `np.array_equal`), o escribir tu propio `__eq__` (con `@dataclass(eq=False)`).
"""),

md(r"""## 6 · Enum, NamedTuple y cuándo usar cada cosa

### Enum: un conjunto cerrado de opciones

Cuando una variable solo puede tomar **unas pocas** opciones con nombre (los modos de un robot, los tipos de articulación, los integradores de MuJoCo...), usar textos sueltos (`"andar"`, `"correr"`) es frágil: una errata (`"ardar"`) no da error. Una **enumeración** (`Enum`) define las opciones **una vez**:
"""),

code(r"""from enum import Enum, IntEnum, auto

class Modo(Enum):
    QUIETO = auto()
    ANDAR = auto()
    CORRER = auto()

modo = Modo.ANDAR
print(modo, modo.name, modo.value)
print(modo is Modo.ANDAR, modo == Modo.CORRER)
print([m.name for m in Modo])
print(Modo["CORRER"])                          # buscar por nombre"""),

code_err(r"""Modo.ARDAR"""),

md(r"""- Cada opción es un objeto único (`Modo.ANDAR`), con un `.name` (su nombre) y un `.value` (su valor; `auto()` numera solo: 1, 2, 3).
- Una errata da error **inmediatamente** (`AttributeError`), en vez de comportarse raro más tarde.
- Se pueden recorrer (`for m in Modo`) y buscar por nombre (`Modo["CORRER"]`).

**`IntEnum`** es igual, pero sus miembros **son también enteros**: se pueden comparar y operar con números. Las constantes de MuJoCo (`mjtIntegrator`, `mjtGeom`...) se comportan **como** un `IntEnum` (NB48), aunque por dentro son otra cosa: tipos fabricados por pybind11, la herramienta que conecta el C++ de MuJoCo con Python. Fíjate:
"""),

code(r"""print(isinstance(mujoco.mjtIntegrator.mjINT_RK4, int), int(mujoco.mjtIntegrator.mjINT_RK4))   # no ES un int, pero se convierte
print(mujoco.mjtIntegrator(3).name)             # del número al nombre (lo hemos hecho mil veces)
print(modelo.opt.integrator == mujoco.mjtIntegrator.mjINT_EULER)"""),

md(r"""No **es** un `int` (`isinstance` da `False`), pero se **convierte** en uno con `int(...)`, se puede **comparar** con enteros (`modelo.opt.integrator`, que es un entero, `==` `mjINT_EULER`) y `mjtIntegrator(3)` traduce un número a su nombre. Para quien lo usa, es como un `IntEnum`. (Moraleja de introspección, P1: no te fíes del nombre; compruébalo con `type` e `isinstance`.)

### NamedTuple, dataclass o diccionario

Tres formas de agrupar unos pocos datos con nombre:
"""),

code(r"""from typing import NamedTuple

class Contacto(NamedTuple):
    cuerpo: str
    fuerza: float

c = Contacto("pie_d", 115.8)
print(c, c.fuerza, c[1])          # acceso por nombre Y por posición
cuerpo, fuerza = c                # se desempaqueta como una tupla
print(cuerpo)"""),

md(r"""Una `NamedTuple` (NB48) es una **tupla con nombres**: inmutable, ligera, se desempaqueta y se indexa como una tupla. ¿Cuándo usar cada una?

| | `dict` | `NamedTuple` | `@dataclass` |
|---|---|---|---|
| Campos fijos y con nombre | no (cualquier clave) | sí | sí |
| Inmutable | no | **sí** | opcional (`frozen`) |
| Se desempaqueta como tupla | no | **sí** | no |
| Valores por defecto, validación, métodos | no | limitado | **sí** (`__post_init__`, `field`...) |
| Uso típico | datos de formato libre, JSON | resultados pequeños que se devuelven de una función (`return Contacto(...)`) | configuraciones, estados, objetos con lógica |

Regla práctica: **dataclass** por defecto; **NamedTuple** para devolver varios valores de una función de forma legible; **dict** solo cuando las claves no se conocen de antemano.
"""),

md(r"""## 7 · Composición frente a herencia

### "Es un" frente a "tiene un"

En el NB25 aprendiste la **herencia**: una clase hija **es una** versión especial de la madre (`PaloDeEscobaEnv` **es un** `gym.Env`). Hay otra forma de reutilizar código: la **composición**, donde un objeto **tiene** otros objetos dentro y les **delega** trabajo (NB47: la clase `Suma` de controladores).

Un robot no **es** un motor; un robot **tiene** motores. Escribirlo con herencia (`class Robot(Motor)`) sería absurdo. Con composición:
"""),

code(r"""@dataclass
class Pierna:
    cadera: Motor
    rodilla: Motor
    tobillo: Motor

    def motores(self) -> list[Motor]:
        return [self.cadera, self.rodilla, self.tobillo]

    def par_maximo_total(self) -> float:
        return sum(m.par_maximo for m in self.motores())

pierna = Pierna(cadera=Motor(300, 20), rodilla=Motor.critico(400), tobillo=Motor(100, 8, par_maximo=50))
print(pierna.par_maximo_total(), "N·m")
print([round(m.kv, 1) for m in pierna.motores()])"""),

md(r"""La `Pierna` **tiene** tres motores, y cada uno puede ser de una clase o configuración distinta. Si mañana quieres un tobillo con un modelo de motor eléctrico más realista, cambias **ese** objeto, sin tocar `Pierna`.

### La regla profesional

> **Prefiere la composición a la herencia** (*favor composition over inheritance*). Es una de las reglas más citadas del diseño de software.

¿Por qué? Porque la herencia **acopla** mucho: la hija depende de todos los detalles internos de la madre, y las jerarquías profundas (`A → B → C → D`) se vuelven imposibles de entender ("¿de cuál de los cuatro viene este método?"). La composición deja las piezas **independientes**: cada una se prueba, se cambia y se reutiliza por separado.

¿Cuándo herencia, entonces? Cuando la relación es de verdad **"es un"** y quieres que la hija se pueda usar **en lugar** de la madre: un entorno **es un** `gym.Env`; un controlador PD **es un** `Controlador` (NB47, con `ABC`). Y casi siempre, **un solo nivel**. Para todo lo demás, composición.
"""),

md(r"""## 8 · Resumen

1. **Modelo de datos**: la sintaxis de Python (`len`, `[]`, `for`, `in`, `+`, `==`, `print`, `()`) llama a **métodos especiales**. Si tu clase los define, tus objetos se usan como los de Python ("pitónicos").
2. **`__repr__`** (programadores; defínelo siempre) frente a **`__str__`** (humanos). **`__getitem__`** recibe enteros o `slice`; con él, el `for` funciona gratis. **`NotImplemented`** = "no sé hacer esta operación".
3. **`==` (igualdad, `__eq__`) frente a `is` (identidad)**. Si defines `__eq__`, Python quita el `__hash__`; para usarlo en sets/dicts, un `__hash__` con los mismos campos, y el objeto no debe cambiar.
4. **Propiedades** con `@x.setter` para validar en un solo sitio; propiedades sin setter = solo lectura y siempre coherentes.
5. **`@classmethod`** (recibe `cls`): constructores alternativos que funcionan con subclases. **`@staticmethod`**: utilidad dentro de la clase.
6. **Dataclasses**: `field(default_factory, repr, init, compare)`, `__post_init__` (validar/derivar), `asdict`, `replace`, `frozen=True` (inmutable y hashable), `order=True`, `slots=True`. Trampa: `==` con arrays.
7. **`Enum`/`IntEnum`/`auto`**: opciones cerradas con nombre; las erratas fallan pronto. **`NamedTuple`** para devolver resultados; **dataclass** por defecto; **dict** para claves libres.
8. **Composición** ("tiene un") antes que **herencia** ("es un", un nivel).

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Modelo de datos** | El conjunto de métodos especiales que conectan tus clases con la sintaxis de Python. |
| **Método especial (dunder)** | `__nombre__`: Python lo llama por ti ante un operador o una función incorporada. |
| **Pitónico** | Que se usa con la sintaxis natural de Python. |
| **`slice`** | El objeto que representa una porción `a:b:c`. |
| **`NotImplemented`** | Valor que devuelve un operador para decir "no sé hacerlo con ese tipo". |
| **Hash / hashable** | Número que identifica el contenido de un objeto; hashable = se puede usar en sets y como clave. |
| **Setter** | Método que se ejecuta al asignar una propiedad. |
| **Constructor alternativo** | `@classmethod` que crea objetos de otra forma (`desde_dict`, `from_file`). |
| **Enumeración (`Enum`)** | Tipo con un conjunto cerrado de valores con nombre. |
| **Composición** | Construir objetos que contienen otros objetos y les delegan trabajo. |
"""),

md(r"""## 9 · Laboratorio

**R1.** Añade a `Trayectoria` un método `angulos()` que devuelva un **array** de NumPy con el ángulo (primer número del estado) de cada muestra, y una propiedad `duracion` (último tiempo menos el primero; 0 si está vacía).

**R2.** ★ Predice qué imprime `print(Trayectoria("a"))` con la clase final de la sección 2. ¿Y `print([Trayectoria("a")])`? ¿Por qué son distintos?

**R3.** Escribe una clase `Vector2` con `x` e `y`, que soporte `+`, `-`, multiplicar por un número (`v * 3`), `abs(v)` (su longitud, NB12), `==` y `repr`. (Pista: `__mul__`, `__abs__`.) ¿Funciona `3 * v`? ¿Qué método falta?

**R4.** ★ Explica por qué esto da `True` y después `False`: `x = [1, 2]; print(x == [1, 2], x is [1, 2])`.

**R5.** Haz que `Objetivo` (sección 3) se pueda **ordenar** por su distancia al origen, definiendo `__lt__` (menor que). ¿Funciona `sorted` con solo `__lt__`?

**R6.** Escribe una propiedad `kv` con setter para `Motor` que, además de impedir valores negativos, avise con un `print` si el amortiguamiento queda por debajo del crítico (`kv < 2·√(kp·0,05)`).

**R7.** Escribe un `@classmethod` `Trayectoria.desde_listas(nombre, tiempos, estados)` y úsalo para crear una trayectoria de 3 muestras a mano.

**R8.** Crea una dataclass congelada `ConfigEntorno` con `peso_avance=1.0`, `peso_vida=1.0`, `peso_control=0.01` y `max_pasos=1000`, que valide en `__post_init__` que `max_pasos > 0`. Úsala con `replace` para generar las 3 variantes de un barrido de `peso_vida ∈ {0.5, 1, 2}`. (Pista: en una dataclass congelada, `__post_init__` puede **leer** pero no asignar campos de la forma normal.)

**R9.** ★ ¿Qué pasa si metes un objeto en un `set`, cambias uno de los campos que usa su `__hash__` y preguntas si está (`in`)? Pruébalo con una clase **no** congelada que tenga `__eq__` y `__hash__` escritos a mano.

**R10.** Crea un `Enum` `Fase` con `APOYO` y `VUELO`, y una función `fase(fuerza_pie: float) -> Fase` que devuelva `VUELO` si la fuerza del sensor de contacto es menor de 1 N. Pruébala con `[0.0, 0.5, 115.8]`.

**R11.** Reescribe `Contacto` como dataclass congelada. ¿Qué pierdes? (Pruébalo: `cuerpo, fuerza = c`.)

**R12.** ★ Diseña con **composición** una clase `ControladorFiltrado` que **tenga** un filtro (una función de un argumento) y un controlador (una función `(q, qd) -> par`), y que al llamarla (`__call__`) filtre la velocidad antes de pasársela al controlador. Pruébala con `crear_filtro` del P2 (cópialo) y un PD sencillo.
"""),

md(r'''<details>
<summary>▶ Solución R1</summary>

```python
class Trayectoria(Trayectoria):
    def angulos(self) -> np.ndarray:
        return np.array([estado[0] for estado in self.estados])

    @property
    def duracion(self) -> float:
        return self.tiempos[-1] - self.tiempos[0] if self else 0.0

t = simular_pendulo(1.0)
print(t.angulos()[:4].round(3), round(t.duracion, 3), Trayectoria().duracion)
```

`if self` usa nuestro `__bool__`: "si la trayectoria tiene muestras". (Con un array de estados, `np.array(self.estados)[:, 0]` haría lo mismo de forma vectorizada: P6.) Duración: de 0,002 s a 1,902 s → 1,9 s.
</details>

<details>
<summary>▶ Solución R2</summary>

`print(Trayectoria("a"))` → `«a» (vacía)`: `print` usa `__str__`, y la trayectoria no tiene muestras.
`print([Trayectoria("a")])` → `[Trayectoria('a', 0 muestras)]`: al imprimir una **lista**, Python usa el `repr` de cada elemento. Por eso es tan importante definir `__repr__`: es lo que verás al depurar, dentro de listas, diccionarios y mensajes de error.
</details>

<details>
<summary>▶ Solución R3</summary>

```python
class Vector2:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"
    def __add__(self, otro):
        return Vector2(self.x + otro.x, self.y + otro.y) if isinstance(otro, Vector2) else NotImplemented
    def __sub__(self, otro):
        return Vector2(self.x - otro.x, self.y - otro.y) if isinstance(otro, Vector2) else NotImplemented
    def __mul__(self, k):
        return Vector2(self.x * k, self.y * k) if isinstance(k, (int, float)) else NotImplemented
    __rmul__ = __mul__                       # 3 * v
    def __abs__(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    def __eq__(self, otro):
        return (self.x, self.y) == (otro.x, otro.y) if isinstance(otro, Vector2) else NotImplemented

v = Vector2(3, 4)
print(v + Vector2(1, 1), v * 2, 3 * v, abs(v), v == Vector2(3, 4))
```

`3 * v` necesita **`__rmul__`** ("multiplicación por la derecha"): Python intenta primero `(3).__mul__(v)`, el entero dice `NotImplemented` (no sabe multiplicarse por un `Vector2`), y entonces prueba `v.__rmul__(3)`. Como la multiplicación por un número es conmutativa, `__rmul__ = __mul__` reutiliza el mismo método. ¡Esto es exactamente el `Vector` del NB25, y lo que hace NumPy por dentro!
</details>

<details>
<summary>▶ Solución R4</summary>

`x == [1, 2]` → `True`: misma **contenido**. `x is [1, 2]` → `False`: `[1, 2]` crea una lista **nueva**, que no es el mismo objeto que `x`. Por eso `is` solo se usa para comparar con `None` (`if x is None`), con `True`/`False` o con miembros de un `Enum`: objetos de los que solo existe **uno**.
</details>

<details>
<summary>▶ Solución R5</summary>

```python
class Objetivo(Objetivo):
    def __lt__(self, otro):
        if not isinstance(otro, Objetivo):
            return NotImplemented
        return (self.x**2 + self.z**2) < (otro.x**2 + otro.z**2)
    def __repr__(self):
        return f"Objetivo({self.x}, {self.z})"

print(sorted([Objetivo(0.5, 0.5), Objetivo(0.1, 0.0), Objetivo(0.3, 0.1)]))
```

Sí: `sorted` (y `min`, `max`) solo necesitan `<`. Para tener los cuatro (`<`, `<=`, `>`, `>=`) sin escribirlos todos, existe el decorador `functools.total_ordering`: defines `__eq__` y `__lt__` y él deduce el resto. (Comparamos distancias **al cuadrado**: mismo orden, sin calcular raíces.)
</details>

<details>
<summary>▶ Solución R6</summary>

```python
class Motor(Motor):
    @property
    def kv(self) -> float:
        return self._kv

    @kv.setter
    def kv(self, valor: float) -> None:
        if valor < 0:
            raise ValueError(f"kv debe ser positivo, no {valor}")
        critico = 2 * (self.kp * 0.05) ** 0.5
        if valor < critico:
            print(f"  aviso: kv = {valor} está por debajo del crítico ({critico:.2f}): habrá sobreoscilación")
        self._kv = float(valor)

m = Motor(kp=300, kv=20)       # crítico = 7,75: sin aviso
m.kv = 3                       # aviso
```

Funciona también dentro de `__init__` porque allí se asigna `self.kv = kv` **después** de `self.kp = kp` (el setter de `kv` necesita `kp`). El **orden** de las asignaciones en `__init__` importa cuando las propiedades dependen unas de otras.
</details>

<details>
<summary>▶ Solución R7</summary>

```python
class Trayectoria(Trayectoria):
    @classmethod
    def desde_listas(cls, nombre: str, tiempos, estados):
        tray = cls(nombre)
        for t, e in zip(tiempos, estados, strict=True):
            tray.grabar(t, e)
        return tray

t = Trayectoria.desde_listas("a mano", [0.0, 0.1, 0.2], [[0, 0], [0.1, 1.0], [0.2, 0.9]])
print(t, t[1])
```

`zip(..., strict=True)` (Python 3.10+) lanza un error si las dos listas tienen **distinta longitud**, en vez de cortar en silencio por la más corta: un error típico que así se caza.
</details>

<details>
<summary>▶ Solución R8</summary>

```python
@dataclass(frozen=True)
class ConfigEntorno:
    peso_avance: float = 1.0
    peso_vida: float = 1.0
    peso_control: float = 0.01
    max_pasos: int = 1000

    def __post_init__(self) -> None:
        if self.max_pasos <= 0:
            raise ValueError(f"max_pasos debe ser positivo, no {self.max_pasos}")

base = ConfigEntorno()
barrido = [replace(base, peso_vida=v) for v in [0.5, 1.0, 2.0]]
for config in barrido:
    print(config)
```

Validar solo **lee** los campos, y eso se puede en una dataclass congelada. Si necesitaras **calcular** un campo derivado (como `pasos_totales`), tendrías que usar `object.__setattr__(self, "campo", valor)`: un truco feo, que es la forma oficial de "saltarse" el congelado dentro de `__post_init__`.
</details>

<details>
<summary>▶ Solución R9</summary>

```python
class Punto:
    def __init__(self, x): self.x = x
    def __eq__(self, otro): return isinstance(otro, Punto) and self.x == otro.x
    def __hash__(self): return hash(self.x)

p = Punto(1)
conjunto = {p}
p.x = 2
print(p in conjunto, Punto(1) in conjunto, Punto(2) in conjunto)     # False False False
```

¡El objeto **está** en el conjunto, pero no se encuentra de ninguna forma! Al cambiar `x`, su hash cambia, y el conjunto lo busca en el cajón del hash nuevo (el de 2), donde no está. Y `Punto(1)` va al cajón correcto (el de 1), donde sí está `p`... pero `p` ya no es igual a `Punto(1)`. Es un objeto **perdido** dentro del conjunto. Por eso: **solo objetos inmutables como claves** (`frozen=True`).
</details>

<details>
<summary>▶ Solución R10</summary>

```python
class Fase(Enum):
    APOYO = auto()
    VUELO = auto()

def fase(fuerza_pie: float) -> Fase:
    return Fase.VUELO if fuerza_pie < 1.0 else Fase.APOYO

print([fase(f).name for f in [0.0, 0.5, 115.8]])     # ['VUELO', 'VUELO', 'APOYO']
```

Usamos un umbral (1 N) en vez de `== 0` porque los sensores reales (y los contactos blandos de MuJoCo, NB48) dan valores pequeños pero no nulos justo al despegar o aterrizar. En el Bloque B, la fase de cada pie decidirá qué hace el controlador.
</details>

<details>
<summary>▶ Solución R11</summary>

```python
@dataclass(frozen=True)
class ContactoDC:
    cuerpo: str
    fuerza: float

c = ContactoDC("pie_d", 115.8)
cuerpo, fuerza = c          # TypeError: cannot unpack non-iterable ContactoDC object
```

Pierdes el **desempaquetado** y el acceso por posición (`c[1]`): una dataclass no es una tupla. Ganas validación, valores por defecto con `field`, `replace`, `asdict`, métodos... Por eso la `NamedTuple` sigue siendo la mejor opción para **devolver** varios valores de una función, y la dataclass para todo lo demás.
</details>

<details>
<summary>▶ Solución R12</summary>

```python
def crear_filtro(alfa):
    filtrado = None
    def filtrar(medida):
        nonlocal filtrado
        filtrado = medida if filtrado is None else alfa * medida + (1 - alfa) * filtrado
        return filtrado
    return filtrar

class ControladorFiltrado:
    def __init__(self, filtro, controlador):
        self.filtro = filtro                 # TIENE un filtro...
        self.controlador = controlador       # ...y TIENE un controlador

    def __call__(self, q: float, qd: float) -> float:
        return self.controlador(q, self.filtro(qd))     # delega en los dos

pd = lambda q, qd: -20 * q - 2 * qd
control = ControladorFiltrado(crear_filtro(0.3), pd)
print([round(control(0.5, v), 2) for v in [1.0, 1.0, -1.0]])
```

`ControladorFiltrado` no hereda de nada: **combina** dos piezas que ya existían, y cualquiera de las dos se puede cambiar (otro filtro, otro controlador) sin tocar la clase. Con `__call__`, se usa como una función, así que se puede pasar a cualquier sitio que espere un controlador (como `simular` del P2). Composición en estado puro.
</details>
'''),

md(r"""## 10 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **P4**, **iterar y gestionar recursos**: qué es de verdad un iterable y un iterador, generadores (con `yield` y `yield from`), expresiones generadoras, los módulos `itertools` y `collections` (`deque`, `Counter`, `defaultdict`), y los **gestores de contexto** (`with`), escritos como clase y con `contextlib`.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB44p3_puente_clases.ipynb")
    build(out, cells, title="NB44·P3 · Puente de Python (3): clases intermedias")
