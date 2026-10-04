"""Construye NB44·P1 · Puente de Python (1): leer código como un profesional.

Primer notebook del PUENTE entre la Parte 3 (Python de verdad, NB20-NB27) y el
Python profesional del Bloque A (NB45-NB50). Repaso ACTIVO con "predice la
salida" (alias, porciones, get, comprensiones, default mutable, ámbito,
formato, verdad/falsedad, //, try/else/finally). Leer código ajeno con método
(de fuera a dentro, seguir los datos) aplicado a zancudo_env.py. Preguntarle a
Python: type, isinstance, dir, vars, help, __doc__, callable, inspect
(signature, getsource) y por qué los objetos de C no tienen código fuente.
Leer errores de bibliotecas (última línea primero; 'incompatible function
arguments'; formas que no encajan). Leer documentación y firmas. Laboratorio
de 12 retos resueltos.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB44·P1 · Puente de Python (1): leer código como un profesional

**Puente de Python — entre la Parte 3 (NB20-NB27) y el Bloque A (NB45-NB50) — Lección 1 de 6**

> En la Parte 3 aprendiste Python "de verdad". Después vinieron 17 notebooks de aprendizaje por refuerzo y de física en los que **usabas** Python, pero ya no lo **estudiabas**. Y en el NB45 el ritmo cambió de golpe: dataclasses avanzadas, `Protocol`, decoradores con argumentos, gestores de contexto, generadores, multiproceso, tipado... cuatro o cinco ideas profesionales por notebook, mezcladas con la parte más difícil de MuJoCo.

Ese salto fue **demasiado brusco**. Este puente de **6 notebooks** lo arregla. La idea es subir del nivel de la Parte 3 al del Bloque A **por escalones**, con mucha más **práctica** que explicación nueva:

| Lección | Tema | Prepara para |
|---|---|---|
| **P1 (hoy)** | Leer código ajeno, preguntarle a Python, leer errores y documentación | todo |
| P2 | Funciones como piezas: callbacks, cierres, decoradores, `functools` | NB47, NB49 |
| P3 | Clases intermedias: métodos especiales, dataclasses, `Enum`, composición | NB45, NB47, NB48 |
| P4 | Iterar y gestionar recursos: generadores, `itertools`, `collections`, `with` | NB48, NB49 |
| P5 | Tipos y errores profesionales: anotaciones de tipo, excepciones propias, `logging` | NB45-NB50 |
| P6 | NumPy intermedio para robótica: trayectorias, máscaras, lotes, álgebra lineal, decimales | NB45, NB46 |

Si ya has leído NB45-NB50, este puente te servirá para **asentar** lo que allí pasó deprisa: cuando vuelvas a ellos, se leerán de otra manera. Si vienes directamente del NB44, haz el puente **antes** del NB45.

Cada lección termina con un **laboratorio**: retos resueltos (ábrelos solo después de intentarlo), del estilo de los que te pondrían en una entrevista técnica de Python.

Hoy empezamos por la habilidad que más se usa en el trabajo real y que **nadie enseña**: **leer** código. Un programador profesional pasa mucho más tiempo leyendo código (el suyo de hace meses, el de sus compañeros, el de las bibliotecas) que escribiéndolo.
"""),

md(r"""## 1 · Calentamiento: predice la salida

### Por qué este ejercicio

La forma más rápida de saber si **entiendes** un trozo de código es **predecir** lo que hará **antes** de ejecutarlo. Si aciertas, lo entiendes. Si fallas, has encontrado exactamente lo que tienes que repasar. Es, además, un tipo de pregunta muy común en entrevistas.

Vamos a repasar la Parte 3 así: diez trozos de código cortos. Para cada uno:

1. Lee el código **sin ejecutarlo**.
2. Escribe en un papel (o en tu cabeza) qué crees que imprimirá.
3. Ejecuta la celda y compara.
4. Si has fallado, abre la explicación.

Cada uno está elegido porque esconde una **trampa** que aparece en el código de MuJoCo de los notebooks siguientes.
"""),

md(r"""**Predicción 1.** (NB21)
"""),

code(r"""angulos = [0.1, 0.2, 0.3]
copia = angulos
copia[0] = 99
print(angulos)"""),

md(r"""<details>
<summary>▶ Explicación</summary>

Imprime `[99, 0.2, 0.3]`. `copia = angulos` **no** copia la lista: crea un **segundo nombre** para la **misma** lista (un **alias**, NB21). Cambiar `copia[0]` cambia la única lista que hay. Para copiar de verdad: `angulos.copy()` o `list(angulos)`.

Esta trampa es **la** trampa de MuJoCo: `datos.qpos` es un array al que apuntan muchos nombres, y si guardas `postura = datos.qpos` sin `.copy()`, tu "postura guardada" cambiará con cada `mj_step` (NB45).
</details>
"""),

md(r"""**Predicción 2.** (NB20, NB21)
"""),

code(r"""qpos = [10, 11, 12, 13, 14, 15, 16, 17, 18]
print(qpos[3:6])
print(qpos[-3:])
print(qpos[::3])"""),

md(r"""<details>
<summary>▶ Explicación</summary>

- `qpos[3:6]` → `[13, 14, 15]`: desde el índice 3 **incluido** hasta el 6 **excluido** (NB20).
- `qpos[-3:]` → `[16, 17, 18]`: los tres últimos.
- `qpos[::3]` → `[10, 13, 16]`: de principio a fin, de 3 en 3.

En Zancudo, `qpos[3:6]` son justo los tres ángulos de la pierna derecha (cadera, rodilla, tobillo), y `qpos[6:9]` los de la izquierda: lo usamos en el `zancudo_env.py` (con `qpos[3:9]`, las seis articulaciones).
</details>
"""),

md(r"""**Predicción 3.** (NB21)
"""),

code(r"""pesos = {"avance": 1.0, "vida": 1.0}
print(pesos.get("control", 0.01))
print(pesos.get("vida", 5))
print(len(pesos))"""),

md(r"""<details>
<summary>▶ Explicación</summary>

`0.01`, `1.0` y `2`. `get(clave, valor_si_no_está)` devuelve el valor guardado si la clave **existe** (`"vida"` → 1.0, aunque le pasemos 5) y el valor de reserva si **no** existe (`"control"` → 0.01). Y `get` **no añade** la clave: el diccionario sigue teniendo 2. Con `pesos["control"]` habríamos tenido un `KeyError` (NB21).
</details>
"""),

md(r"""**Predicción 4.** (NB21)
"""),

code(r"""nombres = ["cadera_d", "rodilla_d", "tobillo_d", "cadera_i"]
print([n.split("_")[0] for n in nombres if n.endswith("_d")])
print({n: len(n) for n in nombres[:2]})"""),

md(r"""<details>
<summary>▶ Explicación</summary>

- `['cadera', 'rodilla', 'tobillo']`: la **comprensión de lista** recorre los nombres, se queda con los que acaban en `_d` (el `if` va **al final**) y de cada uno guarda la parte de antes del `_` (`split("_")` parte el texto en una lista, NB20, y `[0]` coge el primer trozo).
- `{'cadera_d': 8, 'rodilla_d': 9}`: una **comprensión de diccionario** (`clave: valor`) con los dos primeros nombres.
</details>
"""),

md(r"""**Predicción 5.** (NB23)
"""),

code(r"""def registrar(valor, historial=[]):
    historial.append(valor)
    return historial

print(registrar(1))
print(registrar(2))"""),

md(r"""<details>
<summary>▶ Explicación</summary>

`[1]` y después `[1, 2]`, **no** `[2]`. La trampa del **valor por defecto mutable** (NB23): la lista `[]` del valor por defecto se crea **una sola vez**, cuando Python lee el `def`, y todas las llamadas comparten esa misma lista. El arreglo de siempre:

```python
def registrar(valor, historial=None):
    if historial is None:
        historial = []
    ...
```

En el NB45 verás la versión con dataclasses: `field(default_factory=list)`.
</details>
"""),

md(r"""**Predicción 6.** (NB23)
"""),

code(r"""pasos = 0

def contar():
    pasos = pasos + 1
    return pasos"""),

code_err(r"""contar()"""),

md(r"""<details>
<summary>▶ Explicación</summary>

`UnboundLocalError`. Como dentro de la función hay una **asignación** a `pasos` (`pasos = ...`), Python decide que `pasos` es una variable **local** de la función. Y en la parte derecha, `pasos + 1`, esa variable local aún no tiene valor. No usa la `pasos` de fuera (NB23).

Hay tres arreglos: pasar `pasos` como argumento y devolverlo (lo mejor), usar `global pasos` (casi nunca buena idea), o, si la variable está en una función que envuelve a esta, `nonlocal` (lo veremos en el P2: es la clave de los cierres y los decoradores).
</details>
"""),

md(r"""**Predicción 7.** (NB20)
"""),

code(r"""energia = 4.509627
fuerza = 231.516
print(f"{energia:.2f} | {fuerza:8.1f} | {0.0314:.1%} | {-3:+d} | {7:03d}")"""),

md(r"""<details>
<summary>▶ Explicación</summary>

`4.51 |    231.5 | 3.1% | -3 | 007`. Dentro de las llaves de un f-string, después de `:`, va el **formato** (NB20):

- `.2f`: 2 decimales.
- `8.1f`: 1 decimal, ocupando **8** caracteres (rellena con espacios a la izquierda): sirve para alinear tablas.
- `.1%`: multiplica por 100 y añade `%`, con 1 decimal.
- `+d`: entero con signo siempre visible.
- `03d`: entero de 3 cifras rellenando con ceros.

Todas las tablas de resultados de NB45-NB50 usan esto.
</details>
"""),

md(r"""**Predicción 8.** (NB22)
"""),

code(r"""for valor in [0, 0.0, "", "0", [], [0], None, np.nan if False else 0.5]:
    print(repr(valor), "→", "verdadero" if valor else "falso")"""),

md(r"""<details>
<summary>▶ Explicación</summary>

Falsos: `0`, `0.0`, `''` (texto vacío), `[]` (lista vacía) y `None`. Verdaderos: `'0'` (¡un texto **con** un carácter, aunque sea un cero!), `[0]` (una lista **con** un elemento) y `0.5`. La regla (NB22): lo "vacío" o "cero" es falso; lo demás, verdadero.

(El último elemento es un truco para que veas una **expresión condicional**, `A if condición else B`: como `False` es falso, vale `0.5`. Y fíjate en que `np.nan` aparece pero nunca se evalúa... aunque **`np` no está importado todavía en este notebook**. Python no da error porque **nunca llega a evaluar** la parte del `if` que no se elige. Eso se llama **evaluación perezosa** o "de cortocircuito", y también pasa con `and` y `or`.)
</details>
"""),

md(r"""**Predicción 9.** (NB21)
"""),

code(r"""pasos_totales = 1003
print(pasos_totales // 10, pasos_totales % 10)
print(-7 // 2, -7 % 2)
print(7 / 2, type(7 / 2).__name__, type(7 // 2).__name__)"""),

md(r"""<details>
<summary>▶ Explicación</summary>

- `100 3`: `//` es la división **entera** (cuántas veces cabe) y `%` el **resto**. 1003 pasos de simulación son 100 decisiones completas de 10 pasos (el submuestreo de Zancudo) y sobran 3.
- `-4 1`: sorpresa: `//` redondea siempre **hacia abajo** (hacia −∞), no hacia el cero. −7 / 2 = −3,5 → −4. Y el resto se ajusta para que `(-7 // 2) * 2 + (-7 % 2) == -7`.
- `3.5 float int`: `/` **siempre** da un decimal, aunque la división sea exacta; `//` entre enteros da un entero.
</details>
"""),

md(r"""**Predicción 10.** (NB22)
"""),

code(r"""def dividir(a, b):
    try:
        resultado = a / b
    except ZeroDivisionError:
        print("  división por cero")
        return None
    else:
        print("  todo bien")
        return resultado
    finally:
        print("  esto se imprime SIEMPRE")

print(dividir(1, 2))
print(dividir(1, 0))"""),

md(r"""<details>
<summary>▶ Explicación</summary>

```
  todo bien
  esto se imprime SIEMPRE
0.5
  división por cero
  esto se imprime SIEMPRE
None
```

`else` se ejecuta solo si **no** hubo error; `except`, solo si lo hubo; y `finally`, **siempre**, incluso aunque haya un `return` antes (NB22). Fíjate en el orden: el `finally` se imprime **antes** que el resultado, porque el `print(dividir(...))` de fuera solo puede imprimir cuando la función ha terminado del todo, y "terminar del todo" incluye el `finally`. Es lo que garantiza que se restauren cosas aunque haya un error: la base de los gestores de contexto (P4, NB49).

**¿Cuántas has acertado?** Con 8 o más, la Parte 3 está bien asentada. Si has fallado varias, vuelve un momento al notebook indicado entre paréntesis: no hace falta releerlo entero, solo esa sección.
</details>
"""),

md(r"""## 2 · Leer código ajeno con método

### El error del principiante

Cuando un principiante abre un fichero de código que no ha escrito, lo lee como una novela: de la primera línea a la última. Y se pierde a la tercera función, porque el código **no se ejecuta en ese orden**. Un profesional lo lee como un **mapa**, de fuera hacia dentro:

1. **¿Qué importa?** Las primeras líneas dicen de qué depende (NumPy, MuJoCo, Gymnasium...) y dan pistas de qué hace.
2. **¿Qué define?** Una pasada rápida solo por los nombres: constantes, clases, funciones. **Sin entrar**.
3. **¿Cuál es la puerta de entrada?** ¿Qué es lo que usa el que usa este código? En un entorno de Gymnasium, `reset` y `step`.
4. **Seguir los datos.** Desde la entrada, sigue **una** variable importante: ¿de dónde viene?, ¿quién la cambia?, ¿a dónde va?
5. **Solo entonces**, los detalles de cada línea.

Vamos a practicarlo con un fichero que **ya usaste** pero que quizá no leíste con calma: `zancudo_env.py`, el entorno de Zancudo del NB43. Primero, el paso 1 y el paso 2, sin leerlo entero. ¡Que lo haga Python por nosotros!
"""),

code(r"""from pathlib import Path

lineas = Path("zancudo_env.py").read_text().splitlines()
print("líneas totales:", len(lineas))
print("\n--- importaciones ---")
for numero, linea in enumerate(lineas, start=1):
    if linea.startswith(("import", "from")):
        print(f"{numero:3d}  {linea}")"""),

md(r"""(Repaso de Python en esta celda: `.splitlines()` parte un texto en una lista de líneas; `enumerate(..., start=1)` numera desde 1, como los editores; y `startswith` acepta una **tupla** de opciones: "empieza por cualquiera de estas".)

Ya sabemos de qué depende: `pathlib` (rutas), NumPy, Gymnasium (y sus `spaces`) y MuJoCo. Es un entorno de Gymnasium que simula con MuJoCo. Ahora, el **mapa** de lo que define: las líneas que empiezan por `class`, `def` o que definen constantes en MAYÚSCULAS:
"""),

code(r"""for numero, linea in enumerate(lineas, start=1):
    limpia = linea.strip()
    if limpia.startswith(("class ", "def ")) or (linea[:1].isupper() and "=" in linea):
        print(f"{numero:3d}  {linea}")"""),

md(r"""El mapa completo en 9 líneas: una constante (`FICHERO`), una clase (`Zancudo`, que **hereda** de `gym.Env`, NB25) con seis métodos, y nada más. Los métodos que empiezan por `_` son **internos** (NB24): `_observacion` lo usan los otros métodos, no quien usa el entorno.

Paso 3: la puerta de entrada. Quien use este entorno hará (NB25):

```python
entorno = gym.make("Zancudo-v0")       # llama a __init__
obs, info = entorno.reset()            # llama a reset
obs, recompensa, terminado, truncado, info = entorno.step(accion)    # llama a step
```

Paso 4: **seguir un dato**. Sigamos la **acción**: lo que decide la política. Busquemos todas las líneas donde aparece:
"""),

code(r"""def buscar(palabra: str) -> None:
    for numero, linea in enumerate(lineas, start=1):
        if palabra in linea:
            print(f"{numero:3d}  {linea.rstrip()}")

buscar("accion")"""),

md(r"""Leyendo **solo** estas líneas, ya se entiende el viaje de la acción:

1. Llega a `step(self, accion)`.
2. Se **recorta** a [−1, 1] con `np.clip`, por si la política se pasa.
3. Se convierte en **ángulos objetivo**: `postura_base + amplitud * accion`. Una acción de 0 significa "la postura base"; +1, "la postura base más la amplitud".
4. Entra en la **recompensa** como coste: `peso_control * sum(accion ** 2)`: cuanto más brusca, más castigo.

Y la línea del `action_space` nos dice qué forma tiene: 6 números entre −1 y 1. Cuatro búsquedas y ya entendemos el corazón del entorno, sin haber leído las 90 líneas.

**Tu turno** (resuelto debajo): sigue el dato `postura_base`. ¿Dónde se define? ¿Dónde se usa? ¿Qué pasaría si la cambiaras a `[0, 0, 0, 0, 0, 0]`?
"""),

code(r"""buscar("postura_base")"""),

md(r"""<details>
<summary>▶ Solución</summary>

- **Se define** en `__init__`: `[0.3, -0.6, 0.3]` para cada pierna: cadera 0,3, rodilla −0,6, tobillo 0,3. Es la regla "rodilla = −2 × cadera" del NB50 (postura agachada con la planta plana), con a = 0,3.
- **Se usa** en `reset` (las articulaciones empiezan ahí, con un poco de azar, y los motores reciben esa orden) y en `step` (es el centro alrededor del cual se mueven las acciones).
- Si fuera todo ceros, el robot empezaría con las **piernas rectas**. Pero ojo: en `reset` hay otra línea, `qpos[1] = -0.8 * (1 - np.cos(0.3))`, que baja el torso lo que corresponde a a = 0,3. Con las piernas rectas, ese descenso ya no tendría sentido: los pies empezarían **hundidos** 3,6 cm en el suelo, y el contacto blando (NB48) los empujaría hacia arriba de golpe. Es un **acoplamiento oculto**: dos sitios del código que dependen de lo mismo (el 0,3), y solo uno lo nombra. Un buen arreglo sería calcular ese descenso **a partir de** `postura_base`, en vez de repetir el número.

Encontrar acoplamientos ocultos como este es **exactamente** para lo que sirve leer código con método.
</details>
"""),

md(r"""## 3 · Preguntarle a Python

### Python sabe muchas cosas de sí mismo

Cuando no sabes qué es un objeto o qué se puede hacer con él, no hace falta adivinar: **pregúntaselo a Python**. Hay un puñado de herramientas para eso (se llama **introspección**: "mirar hacia dentro"), y un profesional las usa todo el rato. Cargamos MuJoCo y un modelo para practicar:
"""),

code(r"""import os
os.environ["MUJOCO_GL"] = "egl"
import numpy as np
import mujoco

modelo = mujoco.MjModel.from_xml_path("robots/zancudo.xml")
datos = mujoco.MjData(modelo)"""),

md(r"""### type e isinstance: ¿qué es esto?
"""),

code(r"""for cosa in [modelo, datos, datos.qpos, datos.qpos[0], modelo.nq, mujoco.mj_step, "texto"]:
    print(f"{type(cosa).__module__:>18}.{type(cosa).__name__}")"""),

md(r"""- **`type(cosa)`** da la **clase** del objeto. `.__name__` es su nombre y `.__module__`, el módulo donde está definida.
- `modelo` es un `MjModel` del módulo `mujoco._structs` (el guion bajo indica que es un módulo interno: tú lo usas como `mujoco.MjModel`).
- `datos.qpos` es un `numpy.ndarray`; pero **un elemento** de ese array, `datos.qpos[0]`, no es un `float` de Python, sino un **`numpy.float64`**. Por eso a veces ves `np.float64(0.5)` en las salidas (como en el NB49, donde lo arreglamos con `float(...)`).
- `mj_step` es una función "incorporada" (*builtin*): está escrita en C, no en Python.

Para **comprobar** si algo es de un tipo, en el código se usa **`isinstance(cosa, Clase)`**, que también acepta las subclases (NB25):
"""),

code(r"""print(isinstance(datos.qpos[0], float))          # numpy.float64 hereda de float
print(isinstance(modelo.nq, int))
print(isinstance(datos.qpos, (list, np.ndarray)))  # ¿cualquiera de estos?"""),

md(r"""### dir: ¿qué tiene dentro?

**`dir(cosa)`** da la lista de **todos** los nombres (atributos y métodos) de un objeto. Con un `MjModel` son cientos, así que se combina con una comprensión para **filtrar**:
"""),

code(r"""nombres = [n for n in dir(modelo) if not n.startswith("_")]
print("nombres públicos de MjModel:", len(nombres))
print("los que empiezan por 'actuator_':", [n for n in nombres if n.startswith("actuator_")][:12])
print("¿los que tienen 'mass'?", [n for n in nombres if "mass" in n])"""),

md(r"""Esto es **oro** cuando trabajas con MuJoCo. ¿Dónde guarda MuJoCo la masa de cada cuerpo? Un `dir` filtrado por `"mass"` y ahí está: `body_mass`, `body_subtreemass`... (el que usamos en el NB50). La convención de nombres de MuJoCo ayuda mucho: **`objeto_propiedad`** (`body_mass`, `geom_friction`, `jnt_range`, `actuator_gainprm`...).

### help y __doc__: ¿cómo se usa?
"""),

code(r"""print(mujoco.mj_resetDataKeyframe.__doc__)"""),

md(r"""**`.__doc__`** es la **docstring** (NB23) de una función: su documentación. `help(cosa)` muestra lo mismo y más, pero es más largo. En Jupyter hay un atajo todavía más cómodo: escribir **`mujoco.mj_step?`** en una celda (con el signo de interrogación al final) abre la documentación en una ventana.

Aprende a leer esta línea, porque todas las funciones de MuJoCo la tienen:

```
mj_resetDataKeyframe(m: mujoco._structs.MjModel, d: mujoco._structs.MjData, key: typing.SupportsInt | typing.SupportsIndex) -> None
```

Es la **firma** de la función con sus **anotaciones de tipo** (las veremos a fondo en el P5): tres parámetros, `m` (un `MjModel`), `d` (un `MjData`) y `key` (algo que se puede convertir en entero: eso significa `SupportsInt`), y devuelve `None` (no devuelve nada: **modifica** `d`). Con eso sabes cómo llamarla sin mirar ningún tutorial.

### inspect: el código fuente

El módulo **`inspect`** va más allá. `inspect.signature` da la firma de una función de Python, e `inspect.getsource`, ¡su **código fuente**! Lo usamos en el NB34 para leer las tripas de Stable-Baselines3. Probemos con algo nuestro y con algo de MuJoCo:
"""),

code(r"""import inspect
import zancudo_env

print(inspect.signature(zancudo_env.Zancudo.__init__))
print()
print(inspect.getsource(zancudo_env.Zancudo.close))"""),

code_err(r"""inspect.getsource(mujoco.mj_step)"""),

md(r"""Con nuestro código, funciona: firma y fuente. Con `mj_step`, **error**: `TypeError: module, class, method, function, traceback, frame, or code object was expected, got builtin_function_or_method`. Es decir: "esto no es código de Python, no tengo fuente que enseñarte". Las funciones de MuJoCo están escritas en **C** (NB45) y compiladas: Python solo ve una "caja negra" con su firma y su docstring.

Moraleja: para bibliotecas escritas en Python (Gymnasium, Stable-Baselines3, PyTorch en su parte de Python), `getsource` te deja leer cómo funcionan por dentro. Para las partes en C (MuJoCo, NumPy por dentro), toca leer la **documentación**.

### vars y callable

Dos más, rápidas:
"""),

code(r"""entorno = zancudo_env.Zancudo()
atributos = vars(entorno)                        # el diccionario de atributos del objeto
print(sorted(atributos)[:10])
print("¿se puede llamar?", callable(entorno.step), callable(entorno.dt))
entorno.close()"""),

md(r"""- **`vars(objeto)`** da el **diccionario** donde un objeto guarda sus atributos (lo que puso `self.algo = ...` en `__init__`). Es la forma más rápida de ver "qué hay dentro" de un objeto tuyo. (No funciona con los objetos de C de MuJoCo, que no guardan sus datos en un diccionario.)
- **`callable(x)`**: ¿se puede **llamar** con paréntesis? `step` sí (es un método); `dt` no (es un número).

### Resumen: la caja de herramientas de introspección

| Pregunta | Herramienta |
|---|---|
| ¿Qué es? | `type(x)`, `isinstance(x, Clase)` |
| ¿Qué tiene? | `dir(x)` (filtrado con una comprensión), `vars(x)` |
| ¿Cómo se usa? | `help(x)`, `x.__doc__`, `x?` en Jupyter, `inspect.signature(x)` |
| ¿Cómo funciona por dentro? | `inspect.getsource(x)` (solo código de Python) |
| ¿Se puede llamar? | `callable(x)` |
"""),

md(r"""## 4 · Leer errores de bibliotecas

### Los errores largos asustan; no deberían

Cuando el error viene de **dentro** de una biblioteca, la traza (NB22) puede ser larguísima, con ficheros que no conoces. La estrategia profesional es siempre la misma:

1. **Lee la última línea primero.** Ahí están el **tipo** de error y el **mensaje**. El 80 % de las veces, con eso basta.
2. **Busca tu línea.** Sube por la traza hasta encontrar la primera línea que es de **tu** código (tu notebook, tu fichero). Ese es el sitio donde **tú** hiciste algo que la biblioteca no esperaba. Las líneas de dentro de la biblioteca casi nunca son el problema.
3. **Lee el mensaje con calma**, palabra por palabra. Los mensajes de error buenos dicen exactamente qué esperaban y qué recibieron.

Practiquemos con cuatro errores **típicos** de MuJoCo. Para cada uno, intenta averiguar el problema **antes** de leer la explicación.

**Error 1:**
"""),

code_err(r"""datos.ctrl[:] = np.zeros(5)"""),

md(r"""<details>
<summary>▶ Explicación</summary>

Última línea: `ValueError: could not broadcast input array from shape (5,) into shape (6,)`. Traducido: "no puedo meter un array de forma (5,) en un hueco de forma (6,)". Zancudo tiene **6** motores (`modelo.nu`), y le estamos dando 5 órdenes. Las palabras clave: **broadcast** (la "difusión" de NumPy, NB27: cómo encajan arrays de formas distintas) y las dos **formas** (*shape*). Siempre que veas `shape` en un error, imprime las formas de tus arrays.

Lo robusto: `np.zeros(modelo.nu)`, en vez de un 6 escrito a mano.
</details>

**Error 2:**
"""),

code_err(r"""mujoco.mj_step(datos, modelo)"""),

md(r"""<details>
<summary>▶ Explicación</summary>

`TypeError: mj_step(): incompatible function arguments. The following argument types are supported: 1. (m: MjModel, d: MjData, nstep: int = 1) -> None` y debajo, `Invoked with: <MjData...>, <MjModel...>`.

Este es **el** error de las bibliotecas escritas en C/C++ con Python por encima. Su estructura siempre es la misma:

- "**incompatible function arguments**": los argumentos no son del tipo que espera.
- "**The following argument types are supported**": lo que **sí** acepta (aquí, primero el modelo y después los datos... ¡y un `nstep` opcional que quizá no conocías!).
- "**Invoked with**": lo que **tú** le has pasado. Compara las dos listas: datos y modelo están **al revés**.
</details>

**Error 3:**
"""),

code_err(r"""modelo.body("cabeza")"""),

md(r"""<details>
<summary>▶ Explicación</summary>

`KeyError: "Invalid name 'cabeza'. Valid names: ['muslo_d', 'muslo_i', 'pie_d', 'pie_i', 'pierna_d', 'pierna_i', 'torso', 'world']"`.

Un error **amable**: te dice qué nombres son válidos. Zancudo no tiene ningún cuerpo llamado `cabeza`. Fíjate en que es un `KeyError`, como el de los diccionarios (NB21): por dentro, buscar por nombre es como buscar una clave.
</details>

**Error 4:**
"""),

code_err(r"""import gymnasium as gym
entorno = gym.make("Zancudo-v0")
entorno.reset(seed=0)
entorno.step([0.0, 0.0, 0.0])"""),

md(r"""<details>
<summary>▶ Explicación</summary>

Aquí la traza es **larga**: pasa por varios ficheros de Gymnasium (`order_enforcing.py`, `passive_env_checker.py`...) antes de llegar a `zancudo_env.py`. Esos ficheros intermedios son los **envoltorios** que `gym.make` pone alrededor de tu entorno (NB25); no son el problema.

Última línea: `ValueError: operands could not be broadcast together with shapes (6,) (3,)`. Y si subes, la línea culpable de `zancudo_env.py` es `objetivo = self.postura_base + self.amplitud * accion`: multiplicar la amplitud (6 números) por la acción (3 números). La causa real está en **tu** celda: la acción debe tener 6 números, uno por motor.

Lección: en una traza larga, las líneas de las bibliotecas te dicen **por dónde pasó** el error; tu línea te dice **qué hiciste**.
</details>
"""),

md(r"""## 5 · Leer documentación

### Dónde mirar

| Para | Documentación |
|---|---|
| Python y su biblioteca estándar | docs.python.org (también en español) |
| NumPy | numpy.org/doc |
| MuJoCo | mujoco.readthedocs.io (sobre todo: *Overview*, *XML Reference*, *API Reference*, *Python*) |
| Gymnasium | gymnasium.farama.org |
| Stable-Baselines3 | stable-baselines3.readthedocs.io |

Consejos para leer documentación técnica:

- **No la leas entera.** Busca (Ctrl+F) el nombre exacto de la función o del atributo.
- **Mira primero el ejemplo**, después la explicación. Casi todas las páginas buenas tienen uno.
- **Comprueba la versión.** La documentación de MuJoCo cambia con cada versión (en el NB50 vimos que la amortiguación de las articulaciones pasó a ser un vector de 3 números). Tu versión: `mujoco.__version__`.
- Para MuJoCo, la **Referencia XML** es la página más útil: cada atributo de cada etiqueta, con su valor por defecto. Cuando dudes de qué hace `solimp` o `armature`, ahí está.

### Leer una firma de Python

Las firmas de la documentación de Python tienen dos símbolos que confunden. Por ejemplo, la de `sorted`:
"""),

code(r"""print(inspect.signature(sorted))
print(inspect.signature(np.clip))"""),

md(r"""`sorted(iterable, /, *, key=None, reverse=False)`:

- La **`/`** dice: los parámetros de **antes** solo se pueden pasar **por posición**. No puedes escribir `sorted(iterable=lista)`.
- El **`*`** dice: los parámetros de **después** solo se pueden pasar **por nombre**. No puedes escribir `sorted(lista, None, True)`; tienes que escribir `sorted(lista, reverse=True)`.
- Lo que tiene `=algo` es **opcional**, con ese valor por defecto (NB23).

La de `np.clip` es más enrevesada (NumPy está escrito en C y arrastra historia): `<no value>` significa "opcional, sin un valor por defecto que se pueda mostrar"; después del `*`, `min` y `max` solo se pueden dar por nombre; y `**kwargs` recoge más opciones con nombre (NB23). No hace falta entenderla entera para usarla: con `np.clip(a, -1, 1)` basta.

En el P2 aprenderás a escribir tú funciones con `/` y `*`, y por qué es buena idea.
"""),

md(r"""## 6 · Resumen

1. **Predecir la salida** antes de ejecutar es la mejor prueba de que entiendes un código.
2. **Leer código ajeno**: de fuera a dentro (importaciones → mapa de nombres → puerta de entrada → seguir un dato → detalles). Busca los **acoplamientos ocultos**.
3. **Introspección**: `type`, `isinstance`, `dir` (filtrado), `vars`, `help`/`__doc__`/`?`, `inspect.signature`, `inspect.getsource` (solo código de Python, no C), `callable`.
4. **Errores**: última línea primero; después tu línea; el mensaje, palabra por palabra. `shape` → imprime formas; `incompatible function arguments` → compara "supported" con "invoked with".
5. **Documentación**: buscar, no leer entera; el ejemplo primero; ojo con la versión. Firmas: `/` = solo por posición; `*` = solo por nombre.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Introspección** | Que un programa examine sus propios objetos (tipo, atributos, documentación). |
| **Firma** | La lista de parámetros de una función, con sus valores por defecto y tipos. |
| **Acoplamiento oculto** | Dos partes del código que dependen de lo mismo sin decirlo. |
| **Evaluación perezosa (cortocircuito)** | No evaluar una parte de una expresión que no hace falta. |
| **Builtin** | Función incorporada, escrita en C: sin código fuente de Python. |
"""),

md(r"""## 7 · Laboratorio

Doce retos. Intenta cada uno en una celda nueva **antes** de abrir la solución. Los marcados con ★ son de nivel entrevista.

**R1.** Imprime una tabla con el nombre de cada articulación de Zancudo, su tipo (`hinge`/`slide`) y su rango. (Pista: `modelo.njnt`, `modelo.joint(i)`, `mujoco.mjtJoint`.)

**R2.** Usando `dir` y una comprensión, encuentra todos los atributos de `MjData` cuyo nombre empieza por `qfrc_`. ¿Cuántos hay?

**R3.** Predice la salida: `a = [[0] * 3] * 2; a[0][0] = 5; print(a)`.

**R4.** ★ Predice la salida: `print(sorted(["rodilla", "Cadera", "tobillo", "cadera"]))`. ¿Y con `key=str.lower`?

**R5.** Cuenta cuántas líneas de `zancudo_env.py` son comentarios (empiezan por `#` tras quitar los espacios), cuántas están vacías y cuántas tienen código.

**R6.** El entorno de Zancudo da una recompensa por paso. Siguiendo el dato `recompensa` en `zancudo_env.py`, escribe la fórmula y calcula a mano cuánto vale si el robot avanza a 0,5 m/s con la acción `[0.1] * 6` y los pesos por defecto.

**R7.** Busca con `dir` cómo se llama el atributo de `MjModel` que guarda el **pasito** de tiempo, y cámbialo a 0,005. (Pista: no empieza por nada obvio; está dentro de otro objeto.)

**R8.** ★ Explica por qué esta celda imprime `True` y después `False`: `x = datos.qpos; y = datos.qpos.copy(); mujoco.mj_step(modelo, datos); print(x is datos.qpos, np.array_equal(y, datos.qpos))`.

**R9.** Provoca a propósito un error al llamar a `mujoco.mj_forward` con un solo argumento, y lee el mensaje: ¿qué argumentos acepta?

**R10.** Con `inspect.getsource`, lee el método `reset` de `gym.Env` (la clase madre de Zancudo). ¿Qué hace con la `seed`?

**R11.** ★ Predice la salida: `print(0.1 + 0.2 == 0.3, round(0.1 + 0.2, 10) == 0.3, abs((0.1 + 0.2) - 0.3) < 1e-9)`.

**R12.** ★ Escribe una función `resumen_modelo(modelo) -> str` que devuelva un texto con: el nombre del modelo, nq, nv, nu, el número de cuerpos, la masa total y el pasito. Pruébala con Zancudo.
"""),

md(r'''<details>
<summary>▶ Solución R1</summary>

```python
for i in range(modelo.njnt):
    articulacion = modelo.joint(i)
    tipo = mujoco.mjtJoint(articulacion.type[0]).name
    print(f"{articulacion.name:>10} | {tipo:>15} | {articulacion.range}")
```

Nueve articulaciones: `raiz_x` y `raiz_z` son `mjJNT_SLIDE` (deslizantes) y el resto `mjJNT_HINGE` (bisagras). Las de la raíz tienen rango `[0, 0]`, que en MuJoCo significa "sin límite" (no tienen `range` en el fichero). Recuerda el `[0]` de `type`: los accesos por nombre o número (`modelo.joint(i)`) devuelven arrays de un elemento.
</details>

<details>
<summary>▶ Solución R2</summary>

```python
fuerzas = [n for n in dir(datos) if n.startswith("qfrc_")]
print(len(fuerzas), fuerzas)
```

Son las **fuerzas generalizadas** del NB45 (una por grado de libertad): `qfrc_actuator` (los motores), `qfrc_bias` (gravedad y efectos de velocidad), `qfrc_passive` (muelles y amortiguadores de las articulaciones), `qfrc_constraint` (contactos y límites), `qfrc_applied` (las que pones tú)... En MuJoCo 3.14 son **12** (incluidas algunas que solo se usan con opciones especiales, como `qfrc_fluid` para el aire o el agua).
</details>

<details>
<summary>▶ Solución R3</summary>

`[[5, 0, 0], [5, 0, 0]]`. `[0] * 3` crea **una** lista `[0, 0, 0]`, y `[...] * 2` crea una lista con **dos referencias a la misma** lista interior (la trampa del alias, otra vez). Para tener dos filas independientes: `[[0] * 3 for _ in range(2)]` (la comprensión crea una lista nueva en cada vuelta). Con NumPy no pasa: `np.zeros((2, 3))`.
</details>

<details>
<summary>▶ Solución R4</summary>

`['Cadera', 'cadera', 'rodilla', 'tobillo']`: las **mayúsculas van antes** que todas las minúsculas, porque se ordena por el número de cada carácter (NB20: `ord("C")` = 67 < `ord("c")` = 99). Con `key=str.lower`, se compara la versión en minúsculas de cada texto: `['Cadera', 'cadera', 'rodilla', 'tobillo']`... ¡igual! Porque "Cadera" y "cadera" en minúsculas son **iguales**, y `sorted` es **estable**: si dos elementos empatan, conserva su orden original. Prueba con `["rodilla", "cadera", "Cadera"]` para ver la diferencia: sin `key`, `['Cadera', 'cadera', 'rodilla']`; con `key=str.lower`, `['cadera', 'Cadera', 'rodilla']`.
</details>

<details>
<summary>▶ Solución R5</summary>

```python
comentarios = sum(1 for l in lineas if l.strip().startswith("#"))
vacias = sum(1 for l in lineas if not l.strip())
print("comentarios:", comentarios, "| vacías:", vacias, "| código:", len(lineas) - comentarios - vacias)
```

`sum(1 for ... if ...)` es un patrón muy común para **contar** los elementos que cumplen algo (una expresión generadora, NB23, que da un 1 por cada uno). `not l.strip()` es verdadero para las líneas vacías o solo con espacios (un texto vacío es falso, predicción 8).
</details>

<details>
<summary>▶ Solución R6</summary>

```
recompensa = peso_avance · velocidad + peso_vida − peso_control · Σ acción²
           = 1,0 · 0,5 + 1,0 − 0,01 · (6 · 0,1²)
           = 0,5 + 1,0 − 0,0006 = 1,4994
```

Con los pesos por defecto, el término de **vida** (1 punto por paso que sigue de pie) pesa el **doble** que avanzar a 0,5 m/s, y el coste de control es minúsculo. Por eso, en el NB43, la primera política aprendió a quedarse quieta de pie antes que a andar.
</details>

<details>
<summary>▶ Solución R7</summary>

```python
print([n for n in dir(modelo) if "time" in n])        # nada útil a primera vista...
print([n for n in dir(modelo.opt) if "time" in n])    # ¡aquí está!
modelo.opt.timestep = 0.005
```

Está en **`modelo.opt`**, el objeto con las opciones de la física (la sección `<option>` del MJCF, NB45). La introspección a veces requiere **dos niveles**: si no lo encuentras en un objeto, mira en sus atributos que sean objetos. (Devuélvelo a 0,002 si vas a seguir usando el modelo: `modelo.opt.timestep = 0.002`.)
</details>

<details>
<summary>▶ Solución R8</summary>

- `x is datos.qpos` → `True`: `x` no es una copia, es **otro nombre para el mismo objeto** array que da `datos.qpos` (y ese array mira directamente a la memoria de C de MuJoCo, NB45). Por eso `x` **ve los cambios** de `mj_step`. (Para preguntar "¿estos dos arrays miran a la misma memoria?", aunque sean objetos distintos, como una porción y su array original, la herramienta es `np.shares_memory(a, b)`.)
- `np.array_equal(y, datos.qpos)` → `False`, porque `y` es una **copia** hecha antes del paso: se quedó con los valores de entonces, y el paso ha movido el robot (aunque sea un poquito, porque cae hacia el suelo desde su postura inicial).

Es la regla de oro del NB45: si quieres **guardar** un estado, `.copy()`; si quieres **vigilarlo**, basta el nombre.
</details>

<details>
<summary>▶ Solución R9</summary>

```python
mujoco.mj_forward(modelo)
```

`TypeError: mj_forward(): incompatible function arguments. The following argument types are supported: 1. (m: MjModel, d: MjData) -> None`. Acepta exactamente dos argumentos: el modelo y los datos.
</details>

<details>
<summary>▶ Solución R10</summary>

```python
print(inspect.getsource(gym.Env.reset))
```

La docstring es larga; la parte importante está **al final** del código (las dos últimas líneas). Si le das una `seed`, crea un **generador de números aleatorios** nuevo con esa semilla y lo guarda en `self._np_random` (es lo que usa Zancudo como `self.np_random` para el azar de la postura inicial). Si no se la das, conserva el que tenía. Por eso todos los entornos llaman a `super().reset(seed=seed)` al principio de su `reset` (NB25): así la semilla funciona igual en todos.
</details>

<details>
<summary>▶ Solución R11</summary>

`False True True`. La suma de decimales del ordenador no es exacta (NB06, NB49): `0.1 + 0.2` es `0.30000000000000004`. Por eso **nunca** se comparan decimales con `==`, sino con una **tolerancia**: `abs(a - b) < 1e-9`, o mejor `math.isclose(a, b)` / `np.isclose(a, b)` (P6).
</details>

<details>
<summary>▶ Solución R12</summary>

```python
def resumen_modelo(modelo: mujoco.MjModel) -> str:
    nombre = modelo.names[:modelo.names.index(b"\0")].decode() or "(sin nombre)"
    return (f"{nombre}: nq={modelo.nq}, nv={modelo.nv}, nu={modelo.nu}, "
            f"{modelo.nbody} cuerpos, {modelo.body_subtreemass[0]:.1f} kg, pasito {modelo.opt.timestep} s")

print(resumen_modelo(modelo))
# zancudo: nq=9, nv=9, nu=6, 8 cuerpos, 23.6 kg, pasito 0.002 s
```

Lo difícil es el **nombre**: MuJoCo guarda todos los nombres en un único bloque de bytes, `modelo.names`, separados por el byte `\0` (así lo hace C), y el primero es el del modelo. `index(b"\0")` encuentra el primer separador; la porción hasta ahí son los bytes del nombre; y `.decode()` los convierte en texto (NB20). Lo encontrarías con `dir(modelo)` filtrando por `"name"`. (Fíjate: 8 cuerpos, porque el `world` cuenta como cuerpo 0.)
</details>
'''),

md(r"""## 8 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **P2**, las **funciones como piezas**: funciones que reciben funciones (*callbacks*), funciones que fabrican funciones (cierres, con `nonlocal`), y los **decoradores**, subiendo un escalón cada vez hasta los decoradores con argumentos del NB49. Más `functools` (`wraps`, `partial`, `lru_cache`) y los parámetros solo por posición y solo por nombre.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB44p1_puente_leer_codigo.ipynb")
    build(out, cells, title="NB44·P1 · Puente de Python (1): leer código como un profesional")
