"""Construye NB44·P5 · Puente de Python (5): tipos y errores profesionales.

Anotaciones de tipo: qué son (notas que Python no comprueba), los básicos,
contenedores (list[float], dict, tuple fija y variable), None y X | None con
estrechamiento (narrowing), mypy de verdad sobre un fichero (subprocess) con
sus mensajes, Callable, alias de tipo (sentencia type de 3.12), numpy.typing,
Literal, Protocol (tipado estructural) frente a ABC, genéricos con la sintaxis
de 3.12 y Self. Errores: el árbol de excepciones, orden de los except,
excepciones propias con jerarquía y atributos, raise ... from (encadenar),
raise a secas, add_note, EAFP frente a LBYL, no capturar de más. logging:
niveles, getLogger(__name__), formato, a fichero, formato perezoso, en un
notebook (force=True). Laboratorio de 12 retos.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB44·P5 · Puente de Python (5): tipos y errores profesionales

**Puente de Python — Lección 5 de 6**

> Desde el NB45, casi todas las funciones del curso llevan **anotaciones de tipo** (`def f(x: float) -> np.ndarray:`), y en el NB47 apareció `Protocol`, en el NB46 `numpy.typing`, en el NB50 `Self`... sin una lección que lo explicara de principio a fin. Lo mismo con los errores: en el NB22 aprendiste `try`/`except`/`raise`, pero el código profesional usa **excepciones propias**, cadenas de errores y `logging`. Hoy cerramos esos huecos.

Las dos mitades de la lección tienen el mismo objetivo: que tu código **avise** de los problemas **pronto** y **con claridad**. Los tipos avisan **antes** de ejecutar (cuando una herramienta los revisa); las excepciones y los registros (*logs*), **mientras** se ejecuta.
"""),

code(r"""import os
os.environ["MUJOCO_GL"] = "egl"
import re
import sys
import subprocess
import tempfile
from pathlib import Path
import numpy as np
import mujoco

zancudo = mujoco.MjModel.from_xml_path("robots/zancudo.xml")"""),

md(r"""## 1 · Las anotaciones de tipo son notas

### Python no las comprueba

Una **anotación de tipo** dice qué tipo **se espera** que tenga un parámetro, una variable o lo que devuelve una función. Lo primero que hay que entender, y que sorprende a todo el mundo, es que **Python las ignora** al ejecutar:
"""),

code(r"""def duplicar(x: int) -> int:
    return x * 2

print(duplicar(21))
print(duplicar("ja"))           # ¡un texto! la anotación dice int, y Python no protesta
print(duplicar([1, 2]))"""),

md(r"""`duplicar("ja")` da `"jaja"` sin ningún error: la anotación `x: int` es solo una **nota**. Python la guarda (en `duplicar.__annotations__`) pero no la mira.

¿Para qué sirven, entonces? Para tres cosas, todas importantísimas en un proyecto real:

1. **Documentar**: quien lee `def avanzar(modelo: MjModel, pasos: int) -> float` sabe qué pasar y qué recibirá, sin leer el cuerpo.
2. **El editor**: VS Code, PyCharm o Jupyter usan las anotaciones para **autocompletar** (escribes `modelo.` y te propone `opt`, `nq`...) y para subrayar errores mientras escribes.
3. **Comprobadores de tipos** (*type checkers*), como **mypy** o **pyright**: programas que leen tu código **sin ejecutarlo** y encuentran incoherencias ("aquí pasas un texto donde se espera un número"). Es como un corrector ortográfico para el código. Lo usaremos en la sección 3.

En las empresas, el código de Python moderno va **anotado**, y un comprobador de tipos se ejecuta automáticamente antes de aceptar cada cambio (junto a los tests, NB46). Por eso tiene sentido aprenderlo bien.
"""),

md(r"""## 2 · Los tipos básicos y los contenedores

### Escalón 1: los básicos

Los tipos sencillos se escriben con su nombre: `int`, `float`, `str`, `bool`, `bytes`. Para una función que no devuelve nada, `-> None`. Y las variables también se pueden anotar (aunque casi nunca hace falta, porque el comprobador **deduce** el tipo de lo que asignas):

```python
pasito: float = 0.002
nombre: str = "zancudo"

def reiniciar(datos: mujoco.MjData) -> None:      # no devuelve nada
    ...
```

Un detalle: donde se espera `float`, los comprobadores aceptan también un `int` (porque un entero "sirve" como decimal). Al revés, no.

### Escalón 2: contenedores

Para colecciones, el tipo de los **elementos** va entre corchetes:

| Anotación | Significa |
|---|---|
| `list[float]` | una lista de decimales (de cualquier longitud) |
| `dict[str, float]` | un diccionario con claves texto y valores decimales |
| `set[str]` | un conjunto de textos |
| `tuple[float, float]` | una tupla de **exactamente** dos decimales |
| `tuple[str, int, float]` | una tupla de tres, cada uno de su tipo |
| `tuple[float, ...]` | una tupla de decimales de **cualquier** longitud |

Fíjate en la diferencia entre listas y tuplas: una lista se anota con **un** tipo (todos sus elementos son "del mismo tipo"), y una tupla, con **un tipo por posición** (cada posición tiene su significado, NB21). Un ejemplo con todo:
"""),

code(r"""def resumen_contactos(fuerzas: dict[str, list[float]]) -> tuple[str, float]:
    # Devuelve el cuerpo con la mayor fuerza media, y esa media.
    medias = {cuerpo: sum(lista) / len(lista) for cuerpo, lista in fuerzas.items()}
    mejor = max(medias, key=medias.get)
    return mejor, medias[mejor]

print(resumen_contactos({"pie_d": [115.0, 117.2], "pie_i": [110.1, 112.5]}))"""),

md(r"""La firma se lee sola: recibe un diccionario que asocia nombres de cuerpos a listas de fuerzas, y devuelve una pareja (nombre, media). (`key=medias.get`: la función `get` del diccionario como callback, P2: "compara los cuerpos por su media".)

### Escalón 3: puede ser None

Muchas funciones devuelven `None` cuando no encuentran algo (como `dict.get`, o `detectar_caida` del P4). Eso se anota con **`|`** ("o"): `int | None` significa "un entero, o `None`". (En código antiguo verás `Optional[int]`, de `typing`: es lo mismo.)
"""),

code(r"""def primer_contacto(modelo: mujoco.MjModel, max_pasos: int = 1000) -> float | None:
    # Instante del primer contacto, o None si no lo hay en max_pasos.
    d = mujoco.MjData(modelo)
    for _ in range(max_pasos):
        mujoco.mj_step(modelo, d)
        if d.ncon > 0:
            return d.time
    return None

t = primer_contacto(zancudo)
if t is not None:
    print(f"primer contacto a los {t * 1000:.0f} ms")"""),

md(r"""Zancudo toca el suelo a los 34 ms (los 16 pasos en el aire que vimos en el P4, más alguno). Lo importante es el **`if t is not None`**. El comprobador de tipos sabe que `t` es `float | None`, y que no se puede multiplicar `None * 1000`. Así que, si escribes `t * 1000` **sin** comprobar antes, te avisa. **Dentro** del `if`, sabe que `t` ya no puede ser `None`, y lo trata como `float`. A esto se le llama **estrechamiento** (*narrowing*): las comprobaciones (`is None`, `isinstance`...) estrechan el tipo posible de una variable.

Es una de las cosas más valiosas de los tipos: `None` es la causa de una enorme cantidad de errores (`AttributeError: 'NoneType' object has no attribute ...`), y anotarlo con `| None` obliga a pensar en ese caso.
"""),

md(r"""## 3 · mypy: el corrector de tipos

### Probarlo de verdad

Vamos a escribir un pequeño fichero con **errores de tipo** a propósito, y a pasárselo a **mypy** (ya instalado en el entorno del curso). mypy es un programa de la terminal (NB26): lo ejecutamos con `subprocess`, como hicimos con pytest en el NB27.
"""),

code(r"""CODIGO = '''
def media(valores: list[float]) -> float:
    return sum(valores) / len(valores)

def buscar_motor(nombres: list[str], buscado: str) -> int | None:
    for i, nombre in enumerate(nombres):
        if nombre == buscado:
            return i
    return None

def describir(n: int) -> str:
    return n * 2                                    # error 1: devuelve un int, no un str

media(["0.1", "0.2"])                               # error 2: textos en vez de decimales
indice = buscar_motor(["cadera", "rodilla"], "rodilla")
print(indice + 1)                                   # error 3: ¿y si es None?
'''

def revisar_tipos(codigo: str) -> str:
    with tempfile.TemporaryDirectory() as carpeta:
        fichero = Path(carpeta) / "ejemplo.py"
        fichero.write_text(codigo)
        resultado = subprocess.run([sys.executable, "-m", "mypy", "--no-error-summary", "--no-color-output", str(fichero)],
                                   capture_output=True, text=True)
    return re.sub(r"\S*ejemplo\.py", "ejemplo.py", resultado.stdout)

print(revisar_tipos(CODIGO))"""),

md(r"""mypy ha encontrado los **tres** errores **sin ejecutar** el código, cada uno con su número de línea y una explicación:

1. **`Incompatible return value type (got "int", expected "str")`**: `describir` promete devolver un texto y devuelve un número.
2. **`List item 0 has incompatible type "str"; expected "float"`**: le pasamos textos a una función que espera decimales. (En ejecución, este error **sí** habría saltado, pero dentro de `sum`, con un mensaje mucho menos claro.)
3. **`Unsupported operand types for + ("None" and "int")`** y la nota **`Left operand is of type "int | None"`**: `indice` puede ser `None`, y no hemos comprobado ese caso. Este es el más valioso: en esta ejecución concreta **no** habría fallado (porque "rodilla" sí está), pero algún día, con otro nombre, sí. mypy lo encuentra **antes** de que ocurra.

(Detalles de la celda: `subprocess.run([...], capture_output=True, text=True)` ejecuta un programa y recoge lo que imprime en `.stdout`, NB26; `sys.executable` es la ruta del Python del entorno, para usar el mypy de **nuestro** venv; `--no-error-summary` quita la línea de resumen final y `--no-color-output` los códigos de color de la terminal; y el `re.sub` (una expresión regular, la herramienta de buscar y reemplazar patrones de texto) acorta la ruta de la carpeta temporal a solo `ejemplo.py`.)

En un proyecto real se ejecuta en la terminal: `python -m mypy mi_paquete/`. Y el editor (con pyright, que viene en VS Code) hace lo mismo **mientras escribes**, subrayando en rojo.
"""),

md(r"""## 4 · Tipos para funciones, alias y arrays

### Callable: una función como argumento

En el P2 pasábamos funciones a otras funciones (controladores, callbacks). ¿Cómo se anota "una función que recibe dos decimales y devuelve un decimal"? Con **`Callable`**, del módulo `collections.abc`:

```python
from collections.abc import Callable

def simular(controlador: Callable[[float, float], float], segundos: float = 3.0) -> float:
    ...
```

`Callable[[tipos de los argumentos], tipo que devuelve]`. Para un callback que no devuelve nada: `Callable[[int, mujoco.MjData], None]`.

### Alias de tipo

Cuando un tipo es largo y se repite, se le da un **nombre** con un **alias**. Desde Python 3.12, con la sentencia **`type`**:
"""),

code(r"""from collections.abc import Callable

type Controlador = Callable[[float, float], float]          # alias: "un Controlador es esto"
type Callback = Callable[[int, mujoco.MjData], None]

def crear_pd(kp: float, kv: float) -> Controlador:
    def controlador(q: float, qd: float) -> float:
        return -kp * q - kv * qd
    return controlador

pd = crear_pd(50, 5)
print(pd(0.1, 0.0), Controlador.__value__)"""),

md(r"""Ahora `crear_pd(...) -> Controlador` se lee como una frase: "fabrica un controlador". Y si un día cambia la definición de controlador (por ejemplo, para que reciba también el tiempo), se cambia en **un solo sitio**. (En código anterior a 3.12 verás `Controlador: TypeAlias = Callable[...]`, o simplemente `Controlador = Callable[...]`: hacen lo mismo.)

### Arrays de NumPy

Para arrays, el tipo general es `np.ndarray`, pero con **`numpy.typing`** (NB46) se puede decir también el tipo de sus elementos:
"""),

code(r"""import numpy.typing as npt

type Vector = npt.NDArray[np.float64]

def normalizar(v: Vector) -> Vector:
    return v / np.linalg.norm(v)

print(normalizar(np.array([3.0, 4.0])))"""),

md(r"""`npt.NDArray[np.float64]` dice "un array de decimales de 64 bits". Lo que **no** se puede decir (todavía, de forma estándar) es la **forma**: "un vector de 3" o "una matriz de 6×9". Por eso es costumbre escribir la forma en la **docstring** o en un comentario (NB46: "docstrings estilo NumPy").

### Literal: solo estos valores

Si un parámetro solo puede tomar unos pocos valores concretos (como el `accion` del decorador del P2, R12), **`Literal`** lo dice, y mypy avisa si pasas otro:

```python
from typing import Literal

def vigilar(accion: Literal["error", "cero"] = "error") -> ...:
    ...

vigilar("cero")     # bien
vigilar("ceros")    # mypy: Argument 1 has incompatible type "Literal['ceros']"; expected "Literal['error', 'cero']"
```

Es una alternativa ligera a un `Enum` (P3) cuando las opciones son textos sencillos.
"""),

md(r"""## 5 · Protocol: si anda como un pato...

### Tipado nominal frente a estructural

En el NB25 y el NB47 viste dos formas de decir "estas clases son intercambiables":

- **Herencia de una clase base abstracta** (`ABC`): `class PD(Controlador)`. Una clase "es un" controlador **porque lo dice** (hereda de él). Se llama tipado **nominal** (por el nombre).
- **`Protocol`**: una clase "es un" controlador **si tiene los métodos adecuados**, aunque no herede de nada ni sepa que el protocolo existe. Se llama tipado **estructural** (por la estructura), y es la versión "oficial" del famoso **duck typing** de Python: *"si anda como un pato y hace cua como un pato, es un pato"*.
"""),

code(r"""from typing import Protocol

class Politica(Protocol):
    def __call__(self, observacion: np.ndarray) -> np.ndarray: ...

class PoliticaLineal:                               # NO hereda de Politica
    def __init__(self, pesos: np.ndarray):
        self.pesos = pesos
    def __call__(self, observacion: np.ndarray) -> np.ndarray:
        return np.tanh(self.pesos @ observacion)

def quieta(observacion: np.ndarray) -> np.ndarray:  # ¡una función normal también encaja!
    return np.zeros(6)

def evaluar(politica: Politica, pasos: int = 3) -> float:
    obs = np.zeros(18)
    return float(sum(np.abs(politica(obs)).sum() for _ in range(pasos)))

rng = np.random.default_rng(0)
print(evaluar(PoliticaLineal(rng.normal(0, 0.1, (6, 18)))), evaluar(quieta))"""),

md(r"""`Politica` es un **protocolo**: dice "una política es algo que se puede llamar con una observación y devuelve un array". El cuerpo del método es `...` (los puntos suspensivos, un "aquí no hay nada" válido en Python): el protocolo solo **describe**, no implementa.

`PoliticaLineal` no hereda de `Politica`, y `quieta` es una simple función. Pero las dos **encajan** en la descripción (las dos se pueden llamar así), y mypy aceptará pasar cualquiera de las dos a `evaluar`. Una red de PyTorch (`nn.Module` tiene `__call__`, NB31) o un modelo de Stable-Baselines3 envuelto en una función también encajarían, sin modificar su código.

¿Cuándo cada uno?

| | `ABC` (nominal) | `Protocol` (estructural) |
|---|---|---|
| Las clases tienen que heredar | sí | no |
| Sirve para código ajeno (bibliotecas, funciones) | no | **sí** |
| Comprueba en ejecución que implementas los métodos | **sí** (no deja crear el objeto) | no (solo el comprobador de tipos) |
| Puede dar código compartido (métodos ya hechos) | **sí** | no |

Regla práctica: **`Protocol`** para describir lo que **recibe** una función (sé generoso con lo que aceptas); **`ABC`** cuando quieres una familia de clases **tuyas** que compartan código.
"""),

md(r"""## 6 · Genéricos y Self

### Una función que vale para cualquier tipo

¿Cómo se anota una función que devuelve el **mismo** tipo que recibe, sea cual sea? Por ejemplo, "el último elemento de una lista": si le das una lista de decimales, devuelve un decimal; si le das una lista de textos, un texto. No podemos escribir `-> float` ni `-> str`. Necesitamos una **variable de tipo**, un "tipo comodín" que se llama, por convención, `T`. Desde Python 3.12, se declara entre corchetes después del nombre de la función:
"""),

code(r"""def ultimo[T](elementos: list[T]) -> T:
    return elementos[-1]

def primero_que_cumple[T](elementos: list[T], condicion: Callable[[T], bool]) -> T | None:
    for e in elementos:
        if condicion(e):
            return e
    return None

print(ultimo([0.1, 0.2, 0.3]), ultimo(["cadera", "rodilla"]))
print(primero_que_cumple([0.86, 0.85, 0.79, 0.6], lambda h: h < 0.8))"""),

md(r"""`def ultimo[T](elementos: list[T]) -> T` se lee: "para cualquier tipo T, recibe una lista de T y devuelve un T". El comprobador **une** las T: si pasas `list[float]`, sabe que el resultado es `float`. A estas funciones se les llama **genéricas**. Las verás en las firmas de muchas bibliotecas (en código anterior a 3.12, con `T = TypeVar("T")` al principio del fichero).

### Self

Y el último tipo especial, que ya usaste en el NB50: **`Self`** ("el tipo de esta misma clase"), para métodos que devuelven el propio objeto (`return self`, la interfaz fluida) o una instancia nueva de la misma clase. Con `Self`, las subclases heredan la anotación correcta automáticamente:

```python
from typing import Self

class Constructor:
    def piernas(self, largo: float) -> Self:
        self.largo = largo
        return self
```

### Hasta dónde anotar

Un consejo de profesional: **anota las firmas** de las funciones y métodos (parámetros y lo que devuelven), sobre todo las que usan otros. **No hace falta** anotar las variables locales: el comprobador las deduce. Y no te obsesiones: un tipo un poco impreciso (`dict` en vez de `dict[str, list[tuple[float, float]]]`) es mejor que ninguno, y mucho mejor que pasarse una hora peleando con el comprobador.
"""),

md(r"""## 7 · Errores profesionales: la jerarquía de excepciones

### Las excepciones son clases

En el NB22 aprendiste a capturar errores con `try`/`except`. Lo que no vimos es que las excepciones son **clases** (P3), organizadas en un **árbol de herencia**. Un trozo del árbol de Python:

```
BaseException
 ├── KeyboardInterrupt        (pulsar Ctrl+C / el botón de parar de Jupyter)
 └── Exception                (todos los errores "normales")
      ├── ArithmeticError
      │    ├── ZeroDivisionError
      │    ├── OverflowError
      │    └── FloatingPointError
      ├── LookupError
      │    ├── IndexError
      │    └── KeyError
      ├── ValueError
      ├── TypeError
      ├── AttributeError
      ├── OSError
      │    └── FileNotFoundError
      └── RuntimeError
```

Y aquí está la clave: **`except Clase` captura esa clase y todas sus hijas**. `except LookupError` captura tanto `IndexError` como `KeyError`. `except Exception` captura casi todo.
"""),

code(r"""print(issubclass(KeyError, LookupError), issubclass(ZeroDivisionError, ArithmeticError))
print([clase.__name__ for clase in KeyError.__mro__])            # su "árbol genealógico" (NB25)

for accion in [lambda: {}["x"], lambda: [][3], lambda: 1 / 0]:
    try:
        accion()
    except LookupError as e:
        print("error de búsqueda:", type(e).__name__)
    except ArithmeticError as e:
        print("error aritmético: ", type(e).__name__)"""),

md(r"""### El orden de los except importa

Python prueba los `except` **de arriba abajo** y usa el **primero** que encaje. Así que van de lo **más concreto** a lo **más general**. Si pones `except Exception` primero, se lo come todo y los de debajo nunca se ejecutan.

### No captures de más

Dos reglas de oro:

1. **Nunca** escribas `except:` a secas (sin clase): captura **todo**, incluido el Ctrl+C (`KeyboardInterrupt`), y no podrías ni parar el programa. Como mucho, `except Exception`.
2. **Captura solo lo que sabes manejar.** Un `except Exception: pass` que "silencia" los errores es la peor trampa: el programa sigue con datos rotos, y el fallo aparece mucho más tarde, lejos de la causa (lo mismo que decíamos de los `NaN` en el P2). Si no sabes qué hacer con un error, **déjalo salir**.
"""),

md(r"""## 8 · Excepciones propias

### Una jerarquía para tu proyecto

Para los errores **de tu dominio** (la simulación explota, el modelo no es válido, el robot se ha caído...), lo profesional es definir **tus propias** excepciones. Basta con heredar de `Exception` (o de una más concreta):
"""),

code(r"""class ErrorSimulacion(Exception):
    # La madre de todos los errores de nuestra simulación.
    pass

class ExplosionNumerica(ErrorSimulacion):
    def __init__(self, paso: int, valor: float):
        super().__init__(f"la simulación explotó en el paso {paso} (valor {valor})")
        self.paso = paso
        self.valor = valor

class ModeloInvalido(ErrorSimulacion):
    pass

print([c.__name__ for c in ExplosionNumerica.__mro__][:3])"""),

md(r"""¿Por qué molestarse en crear clases nuevas, si podríamos lanzar siempre `RuntimeError("...")`?

1. **Se pueden capturar por separado**: quien use tu código puede escribir `except ExplosionNumerica:` para reintentar con un pasito más pequeño, sin capturar por accidente otros errores.
2. **La jerarquía permite elegir el nivel**: `except ErrorSimulacion` captura **todos** los de tu proyecto a la vez, y nada más.
3. **Llevan datos**: `ExplosionNumerica` guarda `paso` y `valor` como atributos, que quien la captura puede **leer** para decidir qué hacer (no solo un mensaje de texto).

El `super().__init__(mensaje)` le pasa el mensaje a la clase madre (NB25), que es lo que se muestra al imprimir el error. Usémoslas:
"""),

code(r"""def avanzar(modelo: mujoco.MjModel, datos: mujoco.MjData, pasos: int) -> None:
    if modelo.nu == 0:
        raise ModeloInvalido("el modelo no tiene motores")
    for paso in range(pasos):
        mujoco.mj_step(modelo, datos)
        mayor = float(np.abs(datos.qvel).max())
        if not np.isfinite(mayor) or mayor > 1e3:
            raise ExplosionNumerica(paso, mayor)

modelo_inestable = mujoco.MjModel.from_xml_path("robots/zancudo.xml")
modelo_inestable.actuator_gainprm[:, 0] = 1e5           # kp absurdo...
modelo_inestable.actuator_biasprm[:, 1] = -1e5          # ...en sus dos sitios (NB50)
modelo_inestable.actuator_forcelimited[:] = 0           # y sin límite de fuerza

for pasito in [0.002, 0.0005, 0.0001]:
    modelo_inestable.opt.timestep = pasito
    datos = mujoco.MjData(modelo_inestable)
    datos.ctrl[:] = 0.3
    try:
        avanzar(modelo_inestable, datos, pasos=int(0.2 / pasito))
        print(f"pasito {pasito}: ¡bien!")
        break
    except ExplosionNumerica as e:
        print(f"pasito {pasito}: explota en el paso {e.paso}; pruebo uno más pequeño")"""),

md(r"""Este bucle es un patrón real: **reintentar** con un pasito menor si la simulación explota (NB49: con un kp de cien mil, ω = √(kp/I) es enorme y la regla pasito·ω < 2 pide pasitos mucho menores). Un detalle instructivo: si **no** quitáramos el límite de fuerza (`forcelimited`), no explotaría ni con el pasito normal: el `forcerange` de ±150 N·m (NB42) recorta los pares absurdos. Los límites realistas también **protegen la simulación**. Fíjate en cómo el código de fuera usa `e.paso`: un dato, no un texto que habría que trocear.

(Si se te ocurre usar `RuntimeError` para todo, recuerda que **cualquier** cosa de dentro de MuJoCo o de NumPy podría lanzar también un `RuntimeError`, y tu `except` los capturaría confundiéndolos con los tuyos.)

### raise ... from: encadenar errores

A veces capturas un error de bajo nivel y lanzas uno **tuyo** más significativo. Por ejemplo, al cargar un modelo: MuJoCo lanza un `ValueError` con su mensaje técnico, y tú quieres un `ModeloInvalido` que diga **qué fichero** falló. Con **`raise NuevoError(...) from error_original`**, el error original **se conserva** dentro del nuevo:
"""),

code(r"""def cargar_robot(ruta: str) -> mujoco.MjModel:
    try:
        return mujoco.MjModel.from_xml_path(ruta)
    except ValueError as e:
        raise ModeloInvalido(f"no se pudo cargar el robot de {ruta!r}") from e"""),

code_err(r"""cargar_robot("robots/no_existe.xml")"""),

md(r"""La traza muestra **los dos** errores: primero el original de MuJoCo (con su detalle técnico: no encuentra el fichero), después la frase **"The above exception was the direct cause of the following exception"** ("la excepción de arriba fue la causa directa de esta"), y por último el nuestro, con el mensaje para humanos. Quien depure tiene **toda** la información: el qué (nuestro mensaje) y el porqué (el original). El original queda guardado en `e.__cause__`.

(Variantes: `raise ... from None` **oculta** el original, para cuando de verdad no aporta nada; y un **`raise`** a secas, dentro de un `except`, **relanza** el mismo error que se capturó: útil para "hacer algo y dejar que siga", como registrar el error en el log y relanzarlo.)

### add_note: añadir contexto

Desde Python 3.11, se puede **añadir una nota** a un error sin cambiar su tipo, con `e.add_note(...)`. Útil en bucles, para decir **en qué vuelta** falló:
"""),

code_err(r"""for semilla in [0, 1, 2]:
    try:
        if semilla == 2:
            raise ExplosionNumerica(paso=812, valor=float("inf"))
    except ExplosionNumerica as e:
        e.add_note(f"ocurrió con la semilla {semilla}")
        raise"""),

md(r"""La nota aparece al final de la traza ("ocurrió con la semilla 2"), y el error sigue siendo una `ExplosionNumerica`, así que quien la capture fuera la reconoce. (Fíjate en el `raise` a secas: relanza el mismo error, ya con su nota.)

### Pedir perdón o pedir permiso

Dos estilos para manejar situaciones que pueden fallar:

- **LBYL** (*look before you leap*, "mira antes de saltar"): comprobar antes. `if clave in diccionario: valor = diccionario[clave]`.
- **EAFP** (*easier to ask forgiveness than permission*, "es más fácil pedir perdón que permiso"): intentarlo y capturar el error. `try: valor = diccionario[clave] except KeyError: ...`.

Python tiende a preferir **EAFP**: es más directo, y evita una trampa sutil (entre que compruebas y que actúas, la situación puede cambiar: un fichero que existía cuando lo comprobaste puede haberse borrado cuando vas a abrirlo). Pero LBYL es más claro cuando el caso "malo" es **frecuente** y normal (las excepciones están pensadas para lo **excepcional**).
"""),

md(r"""## 9 · logging: registrar lo que pasa

### Por qué no basta con print

Durante el curso hemos usado `print` para todo. En un programa de verdad (un entrenamiento de 10 horas en un servidor, un robot real funcionando), `print` se queda corto:

- No se puede **apagar** sin borrar líneas, ni elegir **cuánto** detalle ver.
- No dice **cuándo** ocurrió, ni **dónde** (qué módulo).
- Va a la pantalla, y en un servidor nadie la mira: hay que guardarlo en un **fichero**.

El módulo **`logging`** de la biblioteca estándar resuelve todo eso (lo presentamos en el NB26; hoy, a fondo). La idea: cada mensaje tiene un **nivel** de importancia, y tú decides a partir de qué nivel se muestran:

| Nivel | Para | Ejemplo |
|---|---|---|
| `DEBUG` | detalles para depurar | "paso 512: qvel máx 3,21" |
| `INFO` | hitos normales | "episodio 40 terminado: 312,5 puntos" |
| `WARNING` | algo raro, pero se puede seguir | "la recompensa es NaN; la cambio por 0" |
| `ERROR` | algo ha fallado | "no se pudo guardar el modelo" |
| `CRITICAL` | fallo gravísimo | "el robot real no responde: parada de emergencia" |
"""),

code(r"""import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
                    datefmt="%H:%M:%S", force=True, stream=sys.stdout)
log = logging.getLogger("simulacion")

log.debug("esto NO se ve: el nivel es INFO")
log.info("empiezo la simulación de %s", "zancudo")
log.warning("el pasito es grande: %.3f s", 0.01)
log.error("algo ha fallado")"""),

md(r"""Las piezas:

- **`logging.basicConfig(...)`** configura el registro **una vez**, al principio del programa: el **nivel** mínimo que se muestra (`INFO`: se ven INFO, WARNING, ERROR y CRITICAL, pero no DEBUG), el **formato** de cada línea (`%(asctime)s` la hora, `%(levelname)s` el nivel, `%(name)s` quién lo dice, `%(message)s` el mensaje; el `-8` alinea a 8 caracteres) y a dónde va (`stream=sys.stdout`, la salida normal).
- **`force=True`**: en un notebook, Jupyter ya ha configurado el registro por su cuenta, y `basicConfig` no haría nada sin `force`. En un script normal no hace falta.
- **`logging.getLogger("nombre")`** da un **registrador** (*logger*) con nombre. En un módulo `.py`, la costumbre es **`log = logging.getLogger(__name__)`**: el nombre del módulo, así cada línea dice de qué fichero viene.
- **Formato perezoso**: `log.info("empiezo la simulación de %s", "zancudo")`, con `%s` y los valores **aparte**, en vez de un f-string. ¿Por qué? Porque si el mensaje no se va a mostrar (por el nivel), **no se construye el texto**: en un bucle de millones de pasos con `log.debug(...)`, eso ahorra mucho tiempo. (`%s` = cualquier cosa como texto, `%.3f` = 3 decimales, `%d` = entero.)

### Cambiar el nivel sin tocar el código

Lo mejor: para ver los detalles, **no** hay que añadir `print`. Basta con bajar el nivel:
"""),

code(r"""log.setLevel(logging.DEBUG)
log.debug("ahora sí se ve el detalle")
log.setLevel(logging.WARNING)
log.info("y ahora esto ya no se ve")
log.warning("pero esto sí")
log.setLevel(logging.INFO)"""),

md(r"""### Registrar a un fichero

En un entrenamiento largo, lo normal es guardar el registro en un fichero (y quizá, a la vez, mostrarlo en pantalla). Se hace añadiendo un **manejador** (*handler*) al registrador:
"""),

code(r"""with tempfile.TemporaryDirectory() as carpeta:
    ruta_log = Path(carpeta) / "entrenamiento.log"
    a_fichero = logging.FileHandler(ruta_log)
    a_fichero.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(a_fichero)

    for episodio in range(3):
        log.info("episodio %d: %.1f puntos", episodio, 100.0 + 50 * episodio)

    log.removeHandler(a_fichero)
    a_fichero.close()
    print("--- contenido del fichero ---")
    print(ruta_log.read_text())"""),

md(r"""Cada mensaje ha ido a **dos** sitios: la pantalla (el manejador que puso `basicConfig`) y el fichero (el nuestro). Un registrador puede tener varios manejadores, cada uno con su formato y su nivel (por ejemplo: a la pantalla solo WARNING, al fichero todo desde DEBUG).

### logging y excepciones

Y un truco final que une las dos mitades de la lección: **`log.exception(...)`**, dentro de un `except`, registra el mensaje **y la traza completa** del error, con nivel ERROR:
"""),

code(r"""try:
    cargar_robot("robots/no_existe.xml")
except ModeloInvalido:
    log.exception("no he podido cargar el robot; sigo con el de serie")"""),

md(r"""El programa **no** se detiene (hemos capturado el error), pero ha quedado **todo** registrado: el mensaje, la traza, y las dos excepciones encadenadas. Es la forma profesional de "manejar" un error del que el programa se puede recuperar: no se silencia, se **registra**.
"""),

md(r"""## 10 · Resumen

1. **Las anotaciones de tipo son notas**: Python no las comprueba. Sirven para documentar, para el editor y para **comprobadores** (mypy, pyright), que encuentran errores sin ejecutar.
2. Básicos (`int`, `float`, `str`, `None`); contenedores (`list[float]`, `dict[str, float]`, `tuple[float, float]`, `tuple[float, ...]`); **`X | None`** + `if x is not None` (estrechamiento).
3. **`Callable[[args], resultado]`**; alias con **`type Nombre = ...`**; **`npt.NDArray[np.float64]`** (la forma, en la docstring); **`Literal[...]`**.
4. **`Protocol`** (estructural: encaja si tiene los métodos) frente a **`ABC`** (nominal: hay que heredar). Protocol para lo que recibes; ABC para familias tuyas con código compartido.
5. **Genéricos**: `def f[T](x: list[T]) -> T`. **`Self`** para `return self`. Anota firmas; no te obsesiones.
6. **Excepciones = clases en un árbol**; `except Madre` captura las hijas; de lo concreto a lo general; nunca `except:` a secas; no silenciar.
7. **Excepciones propias** con jerarquía (`ErrorSimulacion` → `ExplosionNumerica`) y **atributos**. **`raise ... from e`** (encadenar), `raise` a secas (relanzar), `add_note`. EAFP frente a LBYL.
8. **`logging`**: niveles (DEBUG < INFO < WARNING < ERROR < CRITICAL), `basicConfig` (`force=True` en notebooks), `getLogger(__name__)`, formato perezoso con `%s`, manejadores (fichero), **`log.exception`** dentro de un `except`.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Comprobador de tipos** | Programa (mypy, pyright) que revisa los tipos sin ejecutar el código. |
| **Estrechamiento (*narrowing*)** | Una comprobación (`is None`, `isinstance`) reduce los tipos posibles de una variable. |
| **Alias de tipo** | Un nombre para un tipo largo (`type Controlador = ...`). |
| **Tipado nominal / estructural** | Compatible por herencia declarada / por tener los métodos adecuados. |
| **Duck typing** | "Si anda como un pato...": importa lo que un objeto sabe hacer, no su clase. |
| **Genérico / variable de tipo** | Función o clase que vale para cualquier tipo `T`, manteniendo la coherencia. |
| **Encadenar excepciones** | `raise Nueva from original`: el error nuevo conserva su causa. |
| **EAFP / LBYL** | Intentar y capturar / comprobar antes de actuar. |
| **Registrador (*logger*) / manejador (*handler*)** | Quien emite los mensajes / a dónde van (pantalla, fichero...). |
"""),

md(r"""## 11 · Laboratorio

**R1.** Anota la firma de esta función: `def mezclar(a, b, peso=0.5): return [peso * x + (1 - peso) * y for x, y in zip(a, b)]` (recibe dos listas de decimales).

**R2.** ★ ¿Qué tipo tiene el resultado de `dict.get` en `{"kp": 300.0}.get("kv")`? Escribe la anotación y una línea que lo use de forma segura.

**R3.** Pasa a mypy (con `revisar_tipos`) una función `def altura(qpos) -> float: return qpos[1] + 0.865` llamada como `altura("zancudo")`. ¿Detecta el error? ¿Por qué? Ahora anota `qpos: list[float]` y repite. Y por último, prueba a anotar con un tipo de MuJoCo (`import mujoco` y `datos: mujoco.MjData`): ¿qué dice mypy?

**R4.** Escribe un alias `type Estado = tuple[float, float, int]` para los estados `(tiempo, altura, contactos)` del P4, y anota con él un generador `simular(modelo) -> Iterator[Estado]`. (Pista: `Iterator` está en `collections.abc`.)

**R5.** ★ Escribe un `Protocol` llamado `Sensor` con un método `leer(self, datos: mujoco.MjData) -> float`, dos clases que lo cumplan sin heredar (`SensorAltura`, `SensorContactos`), y una función `leer_todos(sensores: list[Sensor], datos) -> dict[str, float]`.

**R6.** Escribe una función genérica `def agrupar_por[T, K](elementos: list[T], clave: Callable[[T], K]) -> dict[K, list[T]]` y úsala para agrupar los nombres de las articulaciones de Zancudo por su última letra.

**R7.** ★ Predice qué imprime, y en qué orden: un `try` que lanza `KeyError`, con `except LookupError` → imprime "A", `except KeyError` → imprime "B", y un `finally` → imprime "C".

**R8.** Crea una excepción `Caida(ErrorSimulacion)` con atributos `tiempo` y `altura`, y una función `vigilar_altura(datos)` que la lance si la cadera baja de 0,55 m. Pruébala empujando a Zancudo con 40 N (`xfrc_applied`, NB48) y captúrala mostrando sus atributos.

**R9.** Escribe `cargar_config(ruta) -> dict` que lea un JSON y, si el fichero no existe **o** el JSON está mal escrito, lance un `ConfigInvalida` (excepción tuya) encadenado (`from`) al error original. Pruébala con un fichero que no existe y con un fichero con `{"kp": 300,}` (coma de más).

**R10.** ★ Explica la diferencia entre estas tres líneas dentro de un `except ValueError as e:`: `raise`, `raise e` y `raise RuntimeError("x") from e`. (Pista: mira qué sale en la traza.)

**R11.** Configura un registrador `"entreno"` que escriba en pantalla solo desde WARNING y en un fichero desde DEBUG. Emite un mensaje de cada nivel y comprueba qué fue a cada sitio.

**R12.** ★ Reescribe el bucle de reintentos de la sección 8 para que, en vez de `print`, use `log.info` en cada éxito, `log.warning` en cada reintento, y, si **ningún** pasito funciona, lance una `ErrorSimulacion` con un mensaje que diga todos los pasitos probados. (Pista: el `for ... else` del NB22.)
"""),

md(r'''<details>
<summary>▶ Solución R1</summary>

```python
def mezclar(a: list[float], b: list[float], peso: float = 0.5) -> list[float]:
    return [peso * x + (1 - peso) * y for x, y in zip(a, b)]
```

Con valor por defecto, la anotación va **antes** del `=`: `peso: float = 0.5` (con espacios alrededor del `=` cuando hay anotación; sin anotación, la costumbre es `peso=0.5`, PEP 8).
</details>

<details>
<summary>▶ Solución R2</summary>

`float | None`: `get` devuelve el valor si la clave existe y `None` si no.

```python
config: dict[str, float] = {"kp": 300.0}
kv: float | None = config.get("kv")
kv_seguro: float = config.get("kv", 20.0)        # con valor por defecto, ya no puede ser None
print(kv, kv_seguro)                              # None 20.0
```

mypy entiende `get` con dos argumentos: si el valor de reserva es un `float`, el resultado es `float`, sin `None`. Es la forma más limpia de evitar el `| None`.
</details>

<details>
<summary>▶ Solución R3</summary>

```python
print(revisar_tipos("""
def altura(qpos) -> float:
    return qpos[1] + 0.865
altura("zancudo")
"""))                        # no dice nada

print(revisar_tipos("""
def altura(qpos: list[float]) -> float:
    return qpos[1] + 0.865
altura("zancudo")
"""))                        # error: Argument 1 to "altura" has incompatible type "str"; expected "list[float]"
```

Sin anotación, mypy no sabe qué es `qpos` y lo deja pasar todo (lo considera de tipo `Any`, "cualquier cosa"): **las funciones sin anotar no se comprueban**. Con la anotación, lo detecta. Moraleja: los tipos ayudan en proporción a lo que anotas.

¿Y con MuJoCo? mypy responde: `Skipping analyzing "mujoco": module is installed, but missing library stubs or py.typed marker`. Es decir: esta versión de MuJoCo **no publica** información de tipos para los comprobadores (los ficheros de "*stubs*"), así que mypy no sabe qué es un `MjData` y lo trata también como `Any`: no puede comprobar nada de lo que hagas con él. Es muy común con bibliotecas escritas en C/C++. La opción `--ignore-missing-imports` silencia ese aviso (sin arreglar el fondo). En la práctica, en un proyecto con MuJoCo, los tipos te protegen sobre todo en **tu** código (tus funciones, tus dataclasses, tus listas y diccionarios), que es donde están la mayoría de los errores.
</details>

<details>
<summary>▶ Solución R4</summary>

```python
from collections.abc import Iterator

type Estado = tuple[float, float, int]

def simular(modelo: mujoco.MjModel, decimar: int = 1) -> Iterator[Estado]:
    d = mujoco.MjData(modelo)
    paso = 0
    while True:
        mujoco.mj_step(modelo, d)
        paso += 1
        if paso % decimar == 0:
            yield d.time, 0.865 + float(d.qpos[1]), d.ncon
```

Un generador se anota con lo que **entrega**: `Iterator[Estado]` ("un iterador de estados"). Fíjate en el `float(...)`: `d.qpos[1]` es un `numpy.float64`, y para que el tipo sea exactamente `float` lo convertimos. (Existe también `Generator[Entrega, Recibe, Devuelve]` para generadores que reciben valores con `send`, pero casi nunca hace falta.)
</details>

<details>
<summary>▶ Solución R5</summary>

```python
class Sensor(Protocol):
    nombre: str
    def leer(self, datos: mujoco.MjData) -> float: ...

class SensorAltura:
    nombre = "altura"
    def leer(self, datos: mujoco.MjData) -> float:
        return 0.865 + float(datos.qpos[1])

class SensorContactos:
    nombre = "contactos"
    def leer(self, datos: mujoco.MjData) -> float:
        return float(datos.ncon)

def leer_todos(sensores: list[Sensor], datos: mujoco.MjData) -> dict[str, float]:
    return {s.nombre: s.leer(datos) for s in sensores}

d = mujoco.MjData(zancudo)
for _ in range(500):
    mujoco.mj_step(zancudo, d)
print(leer_todos([SensorAltura(), SensorContactos()], d))     # {'altura': 0.859..., 'contactos': 4.0}
```

Un protocolo también puede pedir **atributos** (`nombre: str`), no solo métodos. Ninguna clase hereda de `Sensor`, y las dos encajan.
</details>

<details>
<summary>▶ Solución R6</summary>

```python
from collections import defaultdict

def agrupar_por[T, K](elementos: list[T], clave: Callable[[T], K]) -> dict[K, list[T]]:
    grupos: defaultdict[K, list[T]] = defaultdict(list)
    for e in elementos:
        grupos[clave(e)].append(e)
    return dict(grupos)

nombres = [zancudo.joint(i).name for i in range(zancudo.njnt)]
print(agrupar_por(nombres, lambda n: n[-1]))
# {'x': ['raiz_x'], 'z': ['raiz_z'], 'o': ['raiz_giro'], 'd': [...], 'i': [...]}
```

Dos variables de tipo: `T` (los elementos) y `K` (las claves). El comprobador sabe que, con `list[str]` y una clave que devuelve `str`, el resultado es `dict[str, list[str]]`. Aquí sí anotamos una variable local (`grupos`), porque `defaultdict(list)` solo no le dice al comprobador de qué tipo son sus elementos.
</details>

<details>
<summary>▶ Solución R7</summary>

```python
try:
    raise KeyError("x")
except LookupError:
    print("A")
except KeyError:
    print("B")
finally:
    print("C")
```

Imprime `A` y `C`. El `KeyError` encaja ya en el primer `except` (es hijo de `LookupError`), así que el segundo nunca se usa. Por eso, de **lo concreto a lo general**: al revés (`except KeyError` primero), imprimiría `B` y `C`. (Algunos comprobadores y editores avisan de un `except` que nunca se puede alcanzar.)
</details>

<details>
<summary>▶ Solución R8</summary>

```python
class Caida(ErrorSimulacion):
    def __init__(self, tiempo: float, altura: float):
        super().__init__(f"caída a los {tiempo:.2f} s (cadera a {altura:.2f} m)")
        self.tiempo, self.altura = tiempo, altura

def vigilar_altura(datos: mujoco.MjData) -> None:
    altura = 0.865 + float(datos.qpos[1])
    if altura < 0.55:
        raise Caida(datos.time, altura)

d = mujoco.MjData(zancudo)
torso = zancudo.body("torso").id
try:
    for _ in range(2500):
        d.xfrc_applied[torso, 0] = 40.0
        mujoco.mj_step(zancudo, d)
        vigilar_altura(d)
except Caida as e:
    print(e, "|", e.tiempo, e.altura)
```

Con 40 N (más del doble del vuelco del NB48, entre 15 y 16 N), Zancudo cae en menos de un segundo. El que captura puede usar `e.tiempo` para, por ejemplo, calcular la nota de un episodio.
</details>

<details>
<summary>▶ Solución R9</summary>

```python
import json

class ConfigInvalida(Exception):
    pass

def cargar_config(ruta: str | Path) -> dict:
    try:
        return json.loads(Path(ruta).read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ConfigInvalida(f"configuración no válida en {str(ruta)!r}: {e}") from e

with tempfile.TemporaryDirectory() as carpeta:
    mala = Path(carpeta) / "mala.json"
    mala.write_text('{"kp": 300,}')
    for ruta in [Path(carpeta) / "no_existe.json", mala]:
        try:
            cargar_config(ruta)
        except ConfigInvalida as e:
            print(type(e.__cause__).__name__, "→", e)
```

Un `except` puede capturar **varias** clases con una tupla. El primero falla con `FileNotFoundError`; el segundo, con `JSONDecodeError` (el JSON no admite una coma final: "Illegal trailing comma before end of object"). Quien llama solo tiene que conocer **un** error, `ConfigInvalida`, y si quiere el detalle, está en `e.__cause__`.
</details>

<details>
<summary>▶ Solución R10</summary>

- **`raise`** a secas: relanza **el mismo** error, con su traza original intacta (empieza donde ocurrió de verdad). Es lo normal para "registrar y dejar que siga".
- **`raise e`**: también relanza el mismo objeto, pero añade a la traza la línea del `raise e`. Funciona, pero `raise` a secas es más limpio.
- **`raise RuntimeError("x") from e`**: lanza un error **nuevo**, de otro tipo, con el original como **causa** ("The above exception was the direct cause..."). Para traducir un error técnico a uno de tu dominio.

(Y si lanzas un error nuevo **sin** `from` dentro de un `except`, Python también muestra el original, pero con otra frase: "During handling of the above exception, another exception occurred", que sugiere que el segundo error fue un **accidente** al manejar el primero. Por eso, cuando es intencionado, se escribe `from`.)
</details>

<details>
<summary>▶ Solución R11</summary>

```python
entreno = logging.getLogger("entreno")
entreno.setLevel(logging.DEBUG)              # el registrador deja pasar todo...
entreno.propagate = False                    # (no reenviar al registrador raíz de basicConfig)

pantalla = logging.StreamHandler(sys.stdout)
pantalla.setLevel(logging.WARNING)           # ...pero la pantalla solo muestra desde WARNING
entreno.addHandler(pantalla)

with tempfile.TemporaryDirectory() as carpeta:
    ruta = Path(carpeta) / "entreno.log"
    fichero = logging.FileHandler(ruta)
    fichero.setLevel(logging.DEBUG)          # y el fichero, todo
    entreno.addHandler(fichero)
    for nivel in ["debug", "info", "warning", "error", "critical"]:
        getattr(entreno, nivel)(f"mensaje de nivel {nivel}")
    fichero.close()
    print("--- fichero ---")
    print(ruta.read_text())
```

Pantalla: 3 mensajes (warning, error, critical). Fichero: los 5. Hay **dos** filtros: el nivel del **registrador** (lo que deja salir) y el de cada **manejador** (lo que acepta). `propagate = False` evita que los mensajes se repitan también por el manejador de `basicConfig` (los registradores forman un árbol y, por defecto, pasan sus mensajes hacia arriba). Y `getattr(entreno, nivel)` (NB49) llama al método por su nombre.
</details>

<details>
<summary>▶ Solución R12</summary>

```python
probados = []
for pasito in [0.002, 0.0005, 0.0001]:
    modelo_inestable.opt.timestep = pasito
    probados.append(pasito)
    datos = mujoco.MjData(modelo_inestable)
    datos.ctrl[:] = 0.3
    try:
        avanzar(modelo_inestable, datos, pasos=int(0.2 / pasito))
    except ExplosionNumerica as e:
        log.warning("pasito %s: explota en el paso %d; reintento", pasito, e.paso)
        continue
    log.info("pasito %s: estable", pasito)
    break
else:
    raise ErrorSimulacion(f"ningún pasito funciona; probados: {probados}")
```

El `else` de un `for` (NB22) se ejecuta solo si el bucle terminó **sin** `break`: es decir, si ningún pasito funcionó. Y el `continue` dentro del `except` salta al siguiente pasito sin llegar al `break`. Es un patrón compacto y muy legible, una vez que se conoce el `for ... else`.
</details>
'''),

md(r"""## 12 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **P6**, el último escalón: **NumPy intermedio para robótica**. Trayectorias como arrays de forma (T, n), máscaras e índices avanzados, operaciones por **lotes** con broadcasting (rotar 1.000 puntos de una vez), el álgebra lineal de `np.linalg` que usan el NB46 y el NB47 (`norm`, `solve`, `inv`, `cross`, `outer`), vistas frente a copias (otra vez, ahora a fondo) y cómo comparar decimales sin caer en trampas (`isclose`, `allclose`, la precisión de la máquina).
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB44p5_puente_tipos_y_errores.ipynb")
    build(out, cells, title="NB44·P5 · Puente de Python (5): tipos y errores profesionales")
