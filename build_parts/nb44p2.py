"""Construye NB44·P2 · Puente de Python (2): funciones como piezas.

Funciones como objetos (listas y diccionarios de funciones: tabla de
despacho). Funciones que reciben funciones: callbacks en un bucle de
simulación propio, key=, map/filter frente a comprensiones. Parámetros solo
por posición (/) y solo por nombre (*), y la trampa del booleano suelto.
Cierres paso a paso: fábrica de controladores PD, __closure__, la trampa del
cierre en un bucle (enlace tardío) y sus dos arreglos; nonlocal y estado
(contador, filtro paso bajo) frente a una clase. Decoradores escalón a
escalón: envolver a mano, la @, *args/**kwargs, functools.wraps, decoradores
que cambian el comportamiento (vigilar NaN), con argumentos (@recortar), y
apilar decoradores (orden). functools.partial frente a lambda, lru_cache /
cache. Laboratorio de 12 retos.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB44·P2 · Puente de Python (2): funciones como piezas

**Puente de Python — Lección 2 de 6**

> En el NB23 viste, de pasada, que las funciones son objetos, que se pueden fabricar (cierres) y envolver (decoradores). Fue una presentación rápida, con un ejemplo de cada cosa. Después, en el NB47 y el NB49, esas ideas volvieron convertidas en controladores intercambiables, decoradores con argumentos y `functools.partial`... sin escalones intermedios.

Hoy subimos esa escalera **peldaño a peldaño**, con mucha práctica. Todo gira alrededor de una idea:

> **Una función es un valor más**, como un número o una lista. Se puede guardar en una variable, meter en una lista, pasar a otra función, devolver desde otra función... y modificar envolviéndola.

Cuando esta idea se vuelve natural, el código profesional (Gymnasium, Stable-Baselines3, PyTorch, MuJoCo) deja de parecer magia: está lleno de funciones que reciben y devuelven funciones.

Usaremos un péndulo de MuJoCo como banco de pruebas, porque es rápido de simular.
"""),

code(r"""import os
os.environ["MUJOCO_GL"] = "egl"
import time
import numpy as np
import mujoco

PENDULO = '''
<mujoco>
  <compiler angle="radian"/>
  <option timestep="0.002"/>
  <worldbody>
    <body pos="0 0 1">
      <joint name="bisagra" type="hinge" axis="0 1 0" damping="0.05"/>
      <geom type="capsule" fromto="0 0 0  0 0 -0.5" size="0.02" mass="1"/>
    </body>
  </worldbody>
  <actuator>
    <motor joint="bisagra" ctrlrange="-10 10"/>
  </actuator>
</mujoco>
'''
modelo = mujoco.MjModel.from_xml_string(PENDULO)
print("péndulo de 0,5 m y 1 kg, con un motor de par de ±10 N·m")"""),

md(r"""## 1 · Las funciones son valores

### Un repaso que va un poco más lejos

Una función definida con `def` es un **objeto**, y su nombre es una variable que apunta a él (NB23). Así que se puede hacer con ella lo mismo que con cualquier valor:
"""),

code(r"""def nada(q: float, qd: float) -> float:
    return 0.0

def frenar(q: float, qd: float) -> float:
    return -2.0 * qd

def subir(q: float, qd: float) -> float:
    return -8.0 * (q - np.pi) - 1.0 * qd

otra_forma = frenar                          # otro nombre para la misma función (¡sin paréntesis!)
print(otra_forma is frenar, otra_forma(0.0, 1.0))
print(type(frenar).__name__, frenar.__name__)"""),

md(r"""La clave son los **paréntesis**: `frenar` (sin paréntesis) es **la función**, el objeto; `frenar(0.0, 1.0)` (con paréntesis) es **llamarla** y obtener su resultado. Un error muy común de principiante es escribir `x = frenar` queriendo decir `x = frenar(...)`, o al revés.

### Colecciones de funciones

Si las funciones son valores, se pueden guardar en **listas** y **diccionarios**. Un diccionario de funciones es un patrón muy usado, llamado **tabla de despacho** (*dispatch table*): elegir qué función usar **por su nombre**, sin una cadena de `if`/`elif`:
"""),

code(r"""controladores = {"nada": nada, "frenar": frenar, "subir": subir}

def simular(controlador, segundos: float = 3.0, q0: float = 1.0) -> float:
    d = mujoco.MjData(modelo)
    d.qpos[0] = q0
    for paso in range(int(round(segundos / modelo.opt.timestep))):
        d.ctrl[0] = controlador(d.qpos[0], d.qvel[0])          # ← llamamos a la función que nos han dado
        mujoco.mj_step(modelo, d)
    return d.qpos[0]

for nombre, controlador in controladores.items():
    print(f"{nombre:>7}: ángulo final {simular(controlador):6.3f} rad")"""),

md(r"""`simular` no sabe **qué** controlador va a usar: lo recibe como argumento y lo **llama** en cada paso. Con "nada", el péndulo oscila (con su pequeña amortiguación); con "frenar", se para colgando (ángulo ~0); con "subir", lo lleva hasta arriba (π = 3,14 rad) y lo mantiene, como el péndulo invertido del NB34.

Si mañana quieres un controlador nuevo, escribes la función y la añades al diccionario. `simular` no cambia. Este es el **patrón estrategia** del NB47, en su forma más simple: sin clases, solo funciones.
"""),

md(r"""## 2 · Funciones que reciben funciones

### Callbacks

Hemos pasado una función a `simular` para que **decida**. Otro uso, aún más común, es pasar una función para que la otra **te avise** de lo que pasa: un **callback** ("llamada de vuelta"). Tú le dices a la simulación: "en cada paso, llama a esta función mía", y dentro de tu función haces lo que quieras (guardar datos, dibujar, parar...).

Es exactamente lo que hacen los *callbacks* de Stable-Baselines3 (NB47) o el `key=` de `sorted` (NB21). Vamos a darle a `simular` un parámetro opcional `al_paso`:
"""),

code(r"""def simular(controlador, segundos: float = 3.0, q0: float = 1.0, al_paso=None) -> float:
    d = mujoco.MjData(modelo)
    d.qpos[0] = q0
    for paso in range(int(round(segundos / modelo.opt.timestep))):
        d.ctrl[0] = controlador(d.qpos[0], d.qvel[0])
        mujoco.mj_step(modelo, d)
        if al_paso is not None:
            al_paso(paso, d)                               # ← avisamos: "acabo de dar este paso"
    return d.qpos[0]

angulos = []
def guardar_angulo(paso, d):
    angulos.append(d.qpos[0])

simular(frenar, al_paso=guardar_angulo)
print(f"{len(angulos)} ángulos guardados; los 3 primeros: {np.round(angulos[:3], 4)}, el último: {angulos[-1]:.4f}")"""),

md(r"""Fíjate en el diseño:

- `simular` no sabe **qué** hace el callback: solo lo llama con `(paso, d)`. Ese "contrato" (qué argumentos recibe el callback) es lo único que tienen que acordar los dos lados.
- `al_paso=None` por defecto, y el `if al_paso is not None` (NB22): si nadie pide avisos, no se llama a nada.
- `guardar_angulo` escribe en una lista **de fuera** (`angulos`). Funciona porque no **asigna** `angulos = ...` (solo llama a su método `append`), así que no hay `UnboundLocalError` (P1, predicción 6).

Con la misma `simular`, otros callbacks hacen cosas completamente distintas sin tocarla:
"""),

code(r"""def imprimir_cada_segundo(paso, d):
    if paso % 500 == 499:                                  # 500 pasos de 0,002 s = 1 segundo
        print(f"  t = {d.time:.1f} s: ángulo {d.qpos[0]:+.3f}, velocidad {d.qvel[0]:+.3f}")

final = simular(nada, al_paso=imprimir_cada_segundo)"""),

md(r"""### key= y las funciones pequeñas

El parámetro `key` de `sorted`, `min` y `max` es otro callback: "para comparar los elementos, usa **lo que devuelva esta función** sobre cada uno". Y aquí es donde brillan las **`lambda`** (NB23), funciones de una línea sin nombre:
"""),

code(r"""resultados = [("nada", 0.95), ("frenar", 0.002), ("subir", 3.14), ("al azar", 1.7)]
print(sorted(resultados, key=lambda r: r[1]))                # por el número
print(max(resultados, key=lambda r: abs(r[1] - np.pi)))       # el MÁS lejos de π
print(min(resultados, key=lambda r: abs(r[1] - np.pi))[0])    # el nombre del más cerca de π"""),

md(r"""`lambda r: r[1]` es exactamente lo mismo que `def f(r): return r[1]`, pero escrito en el sitio donde se usa. Regla práctica: `lambda` para funciones **de una expresión** que se usan **una vez**; si necesitas más de una línea o la vas a reutilizar, `def` con un buen nombre.

### map y filter frente a comprensiones

Python trae dos funciones clásicas que reciben funciones: `map(f, lista)` aplica `f` a cada elemento, y `filter(f, lista)` se queda con los elementos para los que `f` da verdadero:
"""),

code(r"""import math

angulos_grados = [10, 45, 90, 180]
print(list(map(math.radians, angulos_grados)))
print(list(filter(lambda a: a > 30, angulos_grados)))
# lo mismo con comprensiones (NB21), que es lo que se prefiere en Python:
print([math.radians(a) for a in angulos_grados])
print([a for a in angulos_grados if a > 30])"""),

md(r"""Las dos formas hacen lo mismo. En Python moderno se prefieren las **comprensiones** (más legibles), pero `map` y `filter` aparecen mucho en código ajeno, y `map` es la que usa el multiproceso del NB49 (`repartidor.map(funcion, lista)`). (Devuelven un objeto "perezoso", por eso el `list(...)`: lo verás a fondo en el P4.)
"""),

md(r"""## 3 · Parámetros solo por posición y solo por nombre

### La trampa del booleano suelto

Imagina una función `simular(controlador, 3.0, 1.0, None, True, False)`. ¿Qué significan ese `True` y ese `False`? Imposible saberlo sin mirar la definición. Ahora compara con `simular(controlador, segundos=3.0, dibujar=True, guardar=False)`: se lee solo.

Python te permite **obligar** a quien llama a usar el nombre, con un `*` en la lista de parámetros (P1, sección 5):
"""),

code(r"""def simular_v2(controlador, /, *, segundos: float = 3.0, q0: float = 1.0, al_paso=None) -> float:
    return simular(controlador, segundos, q0, al_paso)

print(simular_v2(frenar, segundos=1.0))"""),

code_err(r"""simular_v2(frenar, 1.0)"""),

md(r"""`TypeError: simular_v2() takes 1 positional argument but 2 were given`: "acepta 1 argumento por posición, pero le has dado 2". Todo lo que va **después** del `*` es **solo por nombre** (*keyword-only*).

Y la **`/`**: lo que va **antes** es **solo por posición** (*positional-only*). Aquí, el controlador:
"""),

code_err(r"""simular_v2(controlador=frenar, segundos=1.0)"""),

md(r"""¿Para qué querrías **prohibir** el nombre? Para tener libertad de **renombrar** el parámetro en el futuro sin romper el código de nadie (si nadie puede escribir `controlador=...`, nadie depende de que se llame así). Es más propio de bibliotecas; en tu código, lo más útil con diferencia es el `*`.

**Regla profesional**: en funciones con muchas opciones (sobre todo booleanos y números de configuración), pon un `*` después de los parámetros "obvios" y obliga a nombrar el resto. Lo verás en todas las bibliotecas serias: `np.clip(a, -1, 1, *, ...)`, `sorted(lista, *, key=None, reverse=False)`.
"""),

md(r"""## 4 · Funciones que fabrican funciones: cierres

### El primer peldaño: una función que devuelve una función

Nuestros controladores tenían los números **escritos dentro** (`-2.0 * qd`, `-8.0 * (q - np.pi)`). ¿Y si queremos probar 10 controladores PD con distintas ganancias? No vamos a escribir 10 funciones. Escribimos **una función que fabrica controladores**:
"""),

code(r"""def crear_pd(kp: float, kv: float, objetivo: float = 0.0):
    def controlador(q: float, qd: float) -> float:
        return kp * (objetivo - q) - kv * qd
    return controlador                       # ¡sin paréntesis! devolvemos LA función

pd_suave = crear_pd(kp=5, kv=1)
pd_fuerte = crear_pd(kp=50, kv=5)
print(pd_suave(1.0, 0.0), pd_fuerte(1.0, 0.0))"""),

md(r"""Vamos despacio, porque esta es la idea más importante de la lección:

1. Al llamar a `crear_pd(kp=5, kv=1)`, Python ejecuta su cuerpo: **define** una función `controlador` (no la llama) y la **devuelve**.
2. `pd_suave` es ahora esa función. Al llamarla, `pd_suave(1.0, 0.0)`, calcula `kp * (objetivo - q) - kv * qd`... ¿con qué `kp`? `crear_pd` ya terminó hace rato, y sus variables locales deberían haber desaparecido.
3. No desaparecen: la función interior **se las lleva consigo**. Recuerda las variables del sitio donde se creó. Eso es un **cierre** (*closure*): una función más las variables que "encierra".
4. Cada llamada a `crear_pd` crea un `controlador` **nuevo** con **sus propias** variables: `pd_suave` recuerda kp = 5 y `pd_fuerte` recuerda kp = 50. Por eso dan −5 y −50.

Puedes ver lo que recuerda un cierre (es un detalle interno, pero ayuda a convencerse):
"""),

code(r"""print([celda.cell_contents for celda in pd_suave.__closure__])
print([celda.cell_contents for celda in pd_fuerte.__closure__])"""),

md(r"""Ahí están, guardados dentro de cada función: kp, kv y el objetivo. Y con la fábrica, un barrido de ganancias es inmediato:
"""),

code(r"""for kp in [5, 20, 80]:
    final = simular(crear_pd(kp=kp, kv=2, objetivo=0.5), segundos=2.0)
    print(f"kp = {kp:2d}: ángulo final {final:.3f} rad (objetivo 0,5)")"""),

md(r"""Cuanto más kp, más cerca del objetivo (NB40: un PD solo no compensa la gravedad, y se queda corto; más kp, menos error). Tres controladores distintos fabricados en una línea cada uno.

### La trampa del cierre en un bucle

Ahora, una trampa famosa, de las que salen en entrevistas. Queremos una lista de tres controladores proporcionales, con kp = 1, 2 y 3:
"""),

code(r"""controladores = []
for kp in [1, 2, 3]:
    controladores.append(lambda q, qd: -kp * q)

print([c(1.0, 0.0) for c in controladores])"""),

md(r"""¡`[-3.0, -3.0, -3.0]`! Esperábamos `[-1, -2, -3]`. ¿Qué ha pasado?

Un cierre recuerda **la variable**, no **su valor en el momento de crearse**. Las tres `lambda` recuerdan **la misma** variable `kp`, la del bucle. Cuando por fin las **llamamos**, el bucle ya terminó y `kp` vale 3. Las tres miran `kp` en ese momento y ven un 3. Se llama **enlace tardío** (*late binding*): el valor se busca al **llamar**, no al **crear**.

Dos arreglos clásicos:
"""),

code(r"""# Arreglo 1: un valor por defecto "congela" el valor al CREAR la función
controladores = [lambda q, qd, kp=kp: -kp * q for kp in [1, 2, 3]]
print([c(1.0, 0.0) for c in controladores])

# Arreglo 2: una fábrica (cada llamada tiene SU PROPIA variable kp)
def crear_p(kp):
    return lambda q, qd: -kp * q
controladores = [crear_p(kp) for kp in [1, 2, 3]]
print([c(1.0, 0.0) for c in controladores])"""),

md(r"""- **Arreglo 1**: los valores por defecto se calculan **al crear** la función (¡es la misma razón de la trampa del valor por defecto mutable!, P1). `kp=kp` guarda en cada lambda el valor que tenía `kp` en esa vuelta.
- **Arreglo 2** (el más limpio): cada llamada a `crear_p` tiene su propia variable local `kp`, y cada lambda encierra una distinta. Es justo lo que hacía `crear_pd`.

(Ojo: esta trampa **no** pasaba con `crear_pd` en el barrido anterior, porque allí llamábamos a cada controlador **dentro** de la misma vuelta del bucle, antes de que `kp` cambiara. Aparece cuando **guardas** las funciones y las llamas después.)
"""),

md(r"""## 5 · Cierres con estado: nonlocal

### Un cierre que recuerda y cambia

Hasta ahora, los cierres **leían** sus variables. ¿Y si queremos que las **cambien**, para recordar algo entre llamada y llamada? Por ejemplo, un **contador** de cuántas veces se ha llamado a un controlador:
"""),

code(r"""def crear_contador():
    cuenta = 0
    def contar() -> int:
        nonlocal cuenta                  # ← "cuenta NO es mía: es la de la función de fuera"
        cuenta += 1
        return cuenta
    return contar

contar = crear_contador()
print(contar(), contar(), contar())"""),

md(r"""Sin `nonlocal`, la línea `cuenta += 1` (que es una **asignación**: `cuenta = cuenta + 1`) haría que Python considerara `cuenta` una variable local nueva... y tendríamos el `UnboundLocalError` de la predicción 6 del P1. **`nonlocal cuenta`** le dice a Python: "esta variable es la de la función que me envuelve; cuando la cambie, cámbiala allí".

Un ejemplo útil en robótica: un **filtro paso bajo** (NB41), que suaviza una señal ruidosa mezclando cada medida nueva con el valor filtrado anterior: `filtrado = α·medida + (1 − α)·filtrado_anterior`. Necesita **recordar** el valor anterior:
"""),

code(r"""def crear_filtro(alfa: float):
    filtrado = None
    def filtrar(medida: float) -> float:
        nonlocal filtrado
        filtrado = medida if filtrado is None else alfa * medida + (1 - alfa) * filtrado
        return filtrado
    return filtrar

rng = np.random.default_rng(0)
medidas = 1.0 + rng.normal(0, 0.2, 200)            # una señal constante de 1,0 con ruido
filtro = crear_filtro(alfa=0.1)
filtradas = [filtro(m) for m in medidas]
print(f"desviación de las medidas: {np.std(medidas[50:]):.3f};  de las filtradas: {np.std(filtradas[50:]):.3f}")"""),

md(r"""El filtro reduce el ruido a menos de la cuarta parte (miramos desde la medida 50, cuando el filtro ya se ha "asentado"). Y cada filtro que fabriques tiene **su propio** valor guardado: puedes tener uno por sensor.

### ¿Cierre o clase?

Un cierre con estado y un objeto (NB24) resuelven el mismo problema: guardar datos junto al código que los usa. El filtro como clase sería:

```python
class Filtro:
    def __init__(self, alfa):
        self.alfa = alfa
        self.filtrado = None
    def __call__(self, medida):              # __call__ hace que el objeto se pueda llamar como una función (NB24)
        ...
```

¿Cuál usar? Regla práctica: **cierre** si es poca cosa (un valor, una sola operación); **clase** en cuanto necesites más de un método (por ejemplo, `reiniciar()`), quieras inspeccionar el estado desde fuera (`filtro.filtrado`) o vaya a crecer. Los decoradores, que vienen ahora, son casi siempre cierres.
"""),

md(r"""## 6 · Decoradores, escalón a escalón

### Escalón 1: envolver a mano

Un **decorador** es una función que recibe una función y devuelve **otra** función que la **envuelve**: hace algo antes, la llama, hace algo después. Empecemos **sin** ninguna sintaxis especial. Queremos saber cuánto tarda `simular`, sin tocar su código:
"""),

code(r"""def cronometrar(funcion):
    def envoltorio(controlador):
        inicio = time.perf_counter()
        resultado = funcion(controlador)
        print(f"  tardó {1000 * (time.perf_counter() - inicio):.1f} ms")
        return resultado
    return envoltorio

simular_cronometrada = cronometrar(simular)
print(simular_cronometrada(frenar))"""),

md(r"""`cronometrar` es un **cierre**: `envoltorio` recuerda `funcion`. `cronometrar(simular)` devuelve un `envoltorio` que, al llamarlo, mide el tiempo, llama a la `simular` original y devuelve su resultado. Hemos **añadido** un comportamiento sin modificar `simular`.

### Escalón 2: la arroba

Normalmente queremos que la versión envuelta **sustituya** a la original, con el mismo nombre: `simular = cronometrar(simular)`. Es tan común que Python tiene una sintaxis para ello, la **`@`**:

```python
@cronometrar
def simular(controlador):        # ← es EXACTAMENTE lo mismo que escribir, después del def,
    ...                          #   simular = cronometrar(simular)
```

No hay nada más: la `@` es una abreviatura.

### Escalón 3: cualquier argumento

Nuestro `envoltorio` solo acepta **un** argumento, `controlador`. Si llamamos a `simular_cronometrada(frenar, segundos=1.0)`, fallará:
"""),

code_err(r"""simular_cronometrada(frenar, segundos=1.0)"""),

md(r"""`TypeError: cronometrar.<locals>.envoltorio() got an unexpected keyword argument 'segundos'`. El envoltorio no sabe qué es `segundos`. La solución: que acepte **cualquier** cosa y la pase tal cual, con `*args, **kwargs` (NB23). Así el decorador sirve para **cualquier** función:
"""),

code(r"""def cronometrar(funcion):
    def envoltorio(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)
        print(f"  [{funcion.__name__}] {1000 * (time.perf_counter() - inicio):.1f} ms")
        return resultado
    return envoltorio

@cronometrar
def simular_largo(controlador, segundos: float = 3.0) -> float:
    "Simula el péndulo y devuelve el ángulo final."
    return simular(controlador, segundos)

print(simular_largo(frenar, segundos=1.0))"""),

md(r"""`*args` recoge los argumentos por posición en una tupla (`(frenar,)`), y `**kwargs` los de con nombre en un diccionario (`{"segundos": 1.0}`). Y al llamar, `funcion(*args, **kwargs)` los **desempaqueta** otra vez (NB23).

### Escalón 4: no perder la identidad

Hay un problema escondido. ¿Cómo se llama ahora `simular_largo`?
"""),

code(r"""print(simular_largo.__name__)
print(simular_largo.__doc__)"""),

md(r"""Se llama `envoltorio`, y ha perdido su documentación: el nombre `simular_largo` apunta al envoltorio, no a la función original. Eso confunde a `help`, a los mensajes de error, a los perfiladores (NB49)... El arreglo, **siempre**, es `functools.wraps`, que copia el nombre, la documentación y las anotaciones de la original en el envoltorio:
"""),

code(r"""import functools

def cronometrar(funcion):
    @functools.wraps(funcion)                      # ← ¡un decorador dentro de un decorador!
    def envoltorio(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)
        print(f"  [{funcion.__name__}] {1000 * (time.perf_counter() - inicio):.1f} ms")
        return resultado
    return envoltorio

@cronometrar
def simular_largo(controlador, segundos: float = 3.0) -> float:
    "Simula el péndulo y devuelve el ángulo final."
    return simular(controlador, segundos)

print(simular_largo.__name__, "|", simular_largo.__doc__)"""),

md(r"""Esta es la **plantilla** de un decorador. Apréndetela de memoria, porque el 90 % de los decoradores son así:

```python
def mi_decorador(funcion):
    @functools.wraps(funcion)
    def envoltorio(*args, **kwargs):
        # ... antes ...
        resultado = funcion(*args, **kwargs)
        # ... después ...
        return resultado
    return envoltorio
```

### Escalón 5: un decorador que cambia el comportamiento

Medir es solo observar. Un decorador también puede **cambiar** lo que pasa: comprobar, corregir, rechazar. Por ejemplo, un vigilante que comprueba que un controlador nunca devuelve `NaN` (NB22: la señal de que algo ha explotado), y si lo hace, falla **pronto** con un mensaje claro:
"""),

code(r"""def vigilar_nan(funcion):
    @functools.wraps(funcion)
    def envoltorio(*args, **kwargs):
        resultado = funcion(*args, **kwargs)
        if not math.isfinite(resultado):
            raise ValueError(f"{funcion.__name__} ha devuelto {resultado} con los argumentos {args}")
        return resultado
    return envoltorio

@vigilar_nan
def controlador_roto(q: float, qd: float) -> float:
    return -5.0 * q / qd                        # ¡divide por la velocidad! cuando qd = 0...

print(controlador_roto(1.0, 2.0))"""),

code_err(r"""simular(controlador_roto, segundos=0.1)"""),

md(r"""En el primer paso, el péndulo está quieto (qd = 0), y `−5.0 * 1.0 / 0.0`... en NumPy (porque `d.qvel[0]` es un `numpy.float64`) da `-inf` con un aviso, en vez de un error. Sin el vigilante, MuJoCo habría recibido un par infinito y la simulación habría explotado más tarde, lejos del verdadero culpable. Con el vigilante, el error salta **en el sitio exacto** y dice qué función, qué valor y con qué argumentos.

### Escalón 6: decoradores con argumentos

¿Y si el decorador necesita un **número**? Por ejemplo, `@recortar(-10, 10)`: limitar la salida de un controlador al rango del motor. Ya no basta con `@recortar`: hay que escribir `@recortar(-10, 10)`, y eso significa que `recortar(-10, 10)` se **ejecuta primero** y tiene que **devolver un decorador**. Un nivel más de funciones:
"""),

code(r"""def recortar(minimo: float, maximo: float):            # nivel 1: recibe los ARGUMENTOS del decorador
    def decorador(funcion):                            # nivel 2: recibe la FUNCIÓN (la plantilla de siempre)
        @functools.wraps(funcion)
        def envoltorio(*args, **kwargs):               # nivel 3: el envoltorio
            return float(np.clip(funcion(*args, **kwargs), minimo, maximo))
        return envoltorio
    return decorador

@recortar(-10, 10)
def pd_bruto(q: float, qd: float) -> float:
    return 200 * (0.5 - q) - 10 * qd

print(pd_bruto(0.0, 0.0), pd_bruto(0.49, 0.0))"""),

md(r"""Léelo desde fuera: `@recortar(-10, 10)` = `pd_bruto = recortar(-10, 10)(pd_bruto)`. Primero, `recortar(-10, 10)` devuelve `decorador` (un cierre que recuerda −10 y 10). Después, `decorador(pd_bruto)` devuelve `envoltorio`. Tres niveles, y cada uno recuerda lo del anterior.

El PD bruto pediría 100 N·m (0,5 rad de error × 200), pero el recorte lo deja en 10. Con un error de 0,01 rad pide 2 N·m, dentro del rango, y pasa sin tocar. Es el **mismo patrón** que `@medir(repeticiones=5)` del NB49 y `@pytest.mark.parametrize(...)` del NB46.

### Escalón 7: apilar decoradores

Se pueden poner varios decoradores, uno encima de otro. Se aplican **de abajo arriba** (el más cercano a la función, primero):
"""),

code(r"""@cronometrar
@recortar(-10, 10)
def pd_bruto_medido(q: float, qd: float) -> float:
    return 200 * (0.5 - q) - 10 * qd

# equivale a:  pd_bruto_medido = cronometrar(recortar(-10, 10)(pd_bruto_medido))
print(pd_bruto_medido(0.0, 0.0))"""),

md(r"""`recortar` envuelve a la función original, y `cronometrar` envuelve a la versión recortada. Al llamar, el orden es el contrario: primero entra en el envoltorio de `cronometrar` (de fuera), que llama al de `recortar`, que llama a la original. Como unas muñecas rusas.
"""),

md(r"""## 7 · functools: partial y la caché

### partial frente a lambda

`functools.partial(funcion, argumentos...)` crea una función nueva con algunos argumentos **ya puestos** (NB49). Es como una fábrica instantánea:
"""),

code(r"""simular_corto = functools.partial(simular, segundos=0.5, q0=2.0)
print(simular_corto(frenar))                              # = simular(frenar, segundos=0.5, q0=2.0)
print(simular_corto.func.__name__, simular_corto.keywords)"""),

md(r"""Lo mismo se podría hacer con `lambda c: simular(c, segundos=0.5, q0=2.0)`. ¿Por qué `partial`, entonces?

1. Se **inspecciona**: `.func` y `.keywords` dicen qué función envuelve y qué argumentos ha fijado. Una `lambda` es una caja cerrada.
2. Se puede enviar a **otro proceso** (NB49): `pickle` sabe guardar un `partial` de una función con nombre, pero **no** una `lambda`.
3. No tiene la trampa del cierre en un bucle: `partial` guarda los **valores** en el momento de crearse.

### lru_cache: no recalcular

`functools.lru_cache` (y su versión sin límite, `functools.cache`) guarda los resultados de una función para no recalcularlos si se repiten los argumentos (NB49). El ejemplo clásico es una función recursiva que repite muchísimo trabajo:
"""),

code(r"""llamadas = 0

def fib_lenta(n: int) -> int:
    global llamadas
    llamadas += 1
    return n if n < 2 else fib_lenta(n - 1) + fib_lenta(n - 2)

print(fib_lenta(25), "con", llamadas, "llamadas")

@functools.cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(25), "|", fib.cache_info())"""),

md(r"""Fibonacci (cada número es la suma de los dos anteriores) escrito "tal cual" llama a `fib_lenta(23)` dos veces, a `fib_lenta(22)` tres veces... en total, **242.785 llamadas** para n = 25. Con la caché, cada `fib(n)` se calcula **una sola vez**: 26 cálculos (*misses*) y 23 veces que se reutiliza un resultado guardado (*hits*).

Recuerda las dos condiciones para usar una caché (NB49): (1) que la función dé **siempre lo mismo** para los mismos argumentos (una **función pura**, NB46: sin azar, sin depender de nada de fuera); (2) que los argumentos se puedan usar como **claves de diccionario** (números, textos, tuplas: no listas ni arrays de NumPy). Y cuidado si devuelve objetos **modificables**: todos los que la llamen recibirán **el mismo**.
"""),

md(r"""## 8 · Resumen

1. **Las funciones son valores**: se guardan, se pasan, se devuelven. `f` es la función; `f()` es llamarla. **Tabla de despacho**: diccionario de funciones.
2. **Callbacks**: pasar una función para que te avisen (`al_paso`, `key=`). Contrato = qué argumentos recibe. `map`/`filter` frente a comprensiones (se prefieren estas).
3. **`*`** en los parámetros: lo de después, **solo por nombre** (adiós a los booleanos sueltos). **`/`**: lo de antes, **solo por posición**.
4. **Cierres**: una función que recuerda las variables de donde se creó; **fábricas** de funciones. **Trampa**: el cierre recuerda la **variable**, no el valor (enlace tardío); arreglos: valor por defecto o fábrica.
5. **`nonlocal`**: un cierre que **cambia** su variable (contador, filtro). Cierre para poca cosa; clase cuando crece.
6. **Decoradores**: envolver una función. Plantilla: `wraps` + `*args, **kwargs` + `return resultado`. Pueden observar (cronometrar) o cambiar (vigilar NaN, recortar). **Con argumentos** = un nivel más. **Apilados**: se aplican de abajo arriba.
7. **`functools.partial`**: fijar argumentos (inspeccionable, se puede enviar a otros procesos). **`cache`/`lru_cache`**: solo para funciones puras con argumentos inmutables.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Tabla de despacho** | Diccionario que asocia nombres a funciones, en vez de una cadena de `if`. |
| **Callback** | Función que pasas a otra para que te llame cuando ocurra algo. |
| **Solo por nombre / solo por posición** | Parámetros después de `*` / antes de `/`. |
| **Enlace tardío** | Un cierre busca el valor de sus variables al llamarse, no al crearse. |
| **`nonlocal`** | Declara que una variable es la de la función que envuelve a esta. |
| **Filtro paso bajo** | Suaviza una señal mezclando cada medida con el valor filtrado anterior. |
| **Función pura** | Siempre da lo mismo con los mismos argumentos, y no cambia nada de fuera. |
"""),

md(r"""## 9 · Laboratorio

**R1.** Escribe una tabla de despacho `operaciones` con cuatro funciones (`"sumar"`, `"restar"`, `"multiplicar"`, `"dividir"`) y una función `calcular(nombre, a, b)` que use la tabla. Si el nombre no existe, debe lanzar un `ValueError` con la lista de nombres válidos (como el `KeyError` amable de MuJoCo del P1).

**R2.** Escribe un callback para `simular` que guarde la **energía** del péndulo en cada paso (pista: `datos.energy` necesita `<flag energy="enable"/>`, NB49... o calcúlala tú: cinética ½·I·qd² con I = m·L²/3 y potencial m·g·(L/2)·(1 − cos q)). ¿Baja con el controlador "nada"? ¿Por qué?

**R3.** ★ Predice la salida y explica: `fs = [lambda: i for i in range(3)]; print([f() for f in fs])`.

**R4.** Escribe un callback `parar_si_cae` que pare la simulación cuando el ángulo supere 2 rad. (Pista: un callback no puede hacer `break` en el bucle de otro... pero puede lanzar una excepción propia, y quien llama a `simular` puede capturarla.)

**R5.** Escribe `crear_saturacion(limite)` que devuelva una función que recorte un número a [−limite, limite]. Úsala para crear `sat5` y `sat10`.

**R6.** ★ Escribe un cierre `crear_media_movil(n)` que devuelva una función que reciba números de uno en uno y devuelva la media de los **n últimos**. (Pista: guarda una lista; o mejor, mira `collections.deque(maxlen=n)`, que verás en el P4.)

**R7.** Escribe un decorador `@contar_llamadas` (sin mirar el E3 del NB49) usando `nonlocal` en vez de un atributo de la función. ¿Qué inconveniente tiene frente a la versión del NB49?

**R8.** Escribe un decorador con argumentos `@repetir(n)` que llame a la función `n` veces y devuelva la **lista** de resultados. Pruébalo con una función que devuelve un número al azar.

**R9.** ★ ¿En qué orden se imprimen los mensajes? Escribe dos decoradores, `@a` y `@b`, que impriman `"entra a"`/`"sale a"` y `"entra b"`/`"sale b"` antes y después de llamar a la función, aplícalos como `@a` encima de `@b`, y predice antes de ejecutar.

**R10.** Con `functools.partial`, crea a partir de `crear_pd` una fábrica `crear_pd_amortiguado(kp)` que fije `kv=3` y `objetivo=np.pi`. Úsala en un barrido de kp ∈ {10, 20, 40} para subir el péndulo.

**R11.** ★ Escribe una función `componer(*funciones)` que devuelva una función que aplique todas en orden: `componer(f, g, h)(x) == h(g(f(x)))`. Úsala para crear `procesar = componer(crear_filtro(0.2), sat5)`.

**R12.** ★ Reescribe el decorador `vigilar_nan` para que acepte un argumento opcional `accion` que puede ser `"error"` (lanza la excepción, como ahora) o `"cero"` (sustituye el valor no finito por 0.0 y avisa con un `print`). Debe funcionar como `@vigilar_nan(accion="cero")`.
"""),

md(r'''<details>
<summary>▶ Solución R1</summary>

```python
operaciones = {
    "sumar": lambda a, b: a + b,
    "restar": lambda a, b: a - b,
    "multiplicar": lambda a, b: a * b,
    "dividir": lambda a, b: a / b,
}

def calcular(nombre: str, a: float, b: float) -> float:
    if nombre not in operaciones:
        raise ValueError(f"operación desconocida {nombre!r}; las válidas son {sorted(operaciones)}")
    return operaciones[nombre](a, b)

print(calcular("multiplicar", 3, 4))       # 12
calcular("potencia", 2, 3)                 # ValueError: operación desconocida 'potencia'; las válidas son [...]
```

`operaciones[nombre]` es la función; `(a, b)` la llama. Y `{nombre!r}` en un f-string pone el texto **entre comillas** (usa `repr`), para que se vean bien espacios o textos vacíos. Añadir una operación = añadir una línea al diccionario.
</details>

<details>
<summary>▶ Solución R2</summary>

```python
energias = []
I, m, g, L = 1.0 * 0.5**2 / 3, 1.0, 9.81, 0.5

def guardar_energia(paso, d):
    q, qd = d.qpos[0], d.qvel[0]
    energias.append(0.5 * I * qd**2 + m * g * (L / 2) * (1 - np.cos(q)))

simular(nada, segundos=10, al_paso=guardar_energia)
print(f"energía al principio: {energias[0]:.3f} J; al final: {energias[-1]:.3f} J")
```

Baja muchísimo: de 1,127 J a **0,003 J** en 10 segundos, porque la articulación tiene `damping="0.05"`: un amortiguador que convierte energía de movimiento en "calor" en cada oscilación. Con `damping="0"`, se mantendría casi constante (NB49: el integrador semiimplícito apenas pierde energía). (`I = m·L²/3` es la inercia de una varilla que gira por un extremo, NB37; la geometría es una cápsula y MuJoCo la calcula algo distinta, así que tu energía puede diferir un poco de `datos.energy`.)
</details>

<details>
<summary>▶ Solución R3</summary>

`[2, 2, 2]`. La trampa del cierre en un bucle: las tres `lambda` encierran **la misma** variable `i`, y cuando se llaman, la comprensión ya terminó con `i = 2`. Arreglo: `[lambda i=i: i for i in range(3)]` → `[0, 1, 2]`.

(Detalle fino: en una comprensión, la variable `i` vive en el ámbito **de la comprensión**, no fuera; pero el efecto es el mismo.)
</details>

<details>
<summary>▶ Solución R4</summary>

```python
class Caida(Exception):
    pass

def parar_si_cae(paso, d):
    if abs(d.qpos[0]) > 2:
        raise Caida(f"ángulo {d.qpos[0]:.2f} rad en el paso {paso}")

empujar = lambda q, qd: 3.0                  # un par constante que lo hace girar
try:
    simular(empujar, segundos=5, q0=0.0, al_paso=parar_si_cae)
except Caida as e:
    print("parado:", e)
```

Una **excepción propia** (una clase que hereda de `Exception`, NB22; las verás a fondo en el P5) es la forma limpia de "salir" desde dentro de un callback: la excepción atraviesa `simular` y llega a quien la llamó. Así lo hacen muchas bibliotecas para pararse antes de tiempo (aunque Stable-Baselines3, por ejemplo, usa otra técnica: el callback devuelve `False`).
</details>

<details>
<summary>▶ Solución R5</summary>

```python
def crear_saturacion(limite: float):
    def saturar(x: float) -> float:
        return max(-limite, min(limite, x))
    return saturar

sat5, sat10 = crear_saturacion(5), crear_saturacion(10)
print(sat5(7), sat10(7), sat5(-12))         # 5 7 -5
```

`max(-limite, min(limite, x))` es el recorte clásico sin NumPy: `min` corta por arriba y `max` por abajo.
</details>

<details>
<summary>▶ Solución R6</summary>

```python
from collections import deque

def crear_media_movil(n: int):
    ultimos = deque(maxlen=n)
    def media(x: float) -> float:
        ultimos.append(x)
        return sum(ultimos) / len(ultimos)
    return media

media3 = crear_media_movil(3)
print([media3(x) for x in [3, 6, 9, 12]])    # [3.0, 4.5, 6.0, 9.0]
```

Una `deque` con `maxlen=n` es una "cola" que, al llenarse, **tira** el elemento más antiguo cada vez que entra uno nuevo. ¿Por qué aquí **no** hace falta `nonlocal`? Porque nunca **asignamos** `ultimos = ...`: solo llamamos a su método `append`, que **modifica** el objeto. `nonlocal` solo hace falta para **reasignar** la variable.
</details>

<details>
<summary>▶ Solución R7</summary>

```python
def contar_llamadas(funcion):
    cuenta = 0
    @functools.wraps(funcion)
    def envoltorio(*args, **kwargs):
        nonlocal cuenta
        cuenta += 1
        print(f"  {funcion.__name__}: llamada número {cuenta}")
        return funcion(*args, **kwargs)
    return envoltorio
```

Funciona, pero la cuenta queda **encerrada**: desde fuera no hay forma limpia de leerla (salvo imprimiéndola, como aquí, o con el truco de `__closure__`). La versión del NB49, con un atributo (`envoltorio.llamadas`), deja leerla con `funcion.llamadas`. Si el estado tiene que verse desde fuera, un atributo (o una clase) es mejor que `nonlocal`.
</details>

<details>
<summary>▶ Solución R8</summary>

```python
def repetir(n: int):
    def decorador(funcion):
        @functools.wraps(funcion)
        def envoltorio(*args, **kwargs):
            return [funcion(*args, **kwargs) for _ in range(n)]
        return envoltorio
    return decorador

rng = np.random.default_rng(0)

@repetir(4)
def tirar_dado() -> int:
    return int(rng.integers(1, 7))

print(tirar_dado())
```

Tres niveles: `repetir(4)` → `decorador` → `envoltorio`. El `_` como nombre de variable es la convención para "no la voy a usar" (NB22).
</details>

<details>
<summary>▶ Solución R9</summary>

```python
def a(funcion):
    @functools.wraps(funcion)
    def envoltorio(*args, **kwargs):
        print("entra a"); resultado = funcion(*args, **kwargs); print("sale a")
        return resultado
    return envoltorio

def b(funcion):
    @functools.wraps(funcion)
    def envoltorio(*args, **kwargs):
        print("entra b"); resultado = funcion(*args, **kwargs); print("sale b")
        return resultado
    return envoltorio

@a
@b
def hola():
    print("hola")

hola()
```

```
entra a
entra b
hola
sale b
sale a
```

`hola = a(b(hola))`: `a` es la muñeca de **fuera**. Al llamar, se entra de fuera a dentro (a, b, función) y se sale de dentro a fuera (b, a), como abrir y cerrar paréntesis. (El `;` permite poner varias instrucciones en una línea: útil en ejemplos, pero en código real, una por línea, PEP 8.)
</details>

<details>
<summary>▶ Solución R10</summary>

```python
crear_pd_amortiguado = functools.partial(crear_pd, kv=3, objetivo=np.pi)

for kp in [10, 20, 40]:
    final = simular(crear_pd_amortiguado(kp=kp), segundos=4.0)
    print(f"kp = {kp}: ángulo final {final:.3f} rad (objetivo π = 3.142)")
```

Fíjate: `partial` de una **fábrica** da otra fábrica más especializada. Arriba del todo (q = π), la gravedad no tira (el péndulo está en equilibrio, aunque inestable), así que el PD sin compensación de gravedad llega muy cerca del objetivo; los tres llegan a 3,142. Cuanto mayor kp, más rápido sube y más "firme" se queda ante perturbaciones. (Con kp muy pequeño no lo conseguiría: m·g·L/2 ≈ 2,5 N·m es el par máximo que hace la gravedad, a 90°, y el PD tiene que superarlo por el camino. Prueba kp = 1.)
</details>

<details>
<summary>▶ Solución R11</summary>

```python
def componer(*funciones):
    def compuesta(x):
        for f in funciones:
            x = f(x)
        return x
    return compuesta

procesar = componer(crear_filtro(0.2), sat5)
print([round(procesar(x), 2) for x in [10, 10, 10, -20]])
```

`*funciones` recoge cualquier número de funciones en una tupla, y `compuesta` (un cierre que la recuerda) las aplica en orden. Es la idea de las **tuberías** de procesamiento: medida → filtro → saturación → motor. (Cuidado: el filtro tiene **estado**, así que `procesar` también lo tiene: llamarla dos veces con lo mismo no da lo mismo. No sería una función pura, y no se podría cachear.)
</details>

<details>
<summary>▶ Solución R12</summary>

```python
def vigilar_nan(accion: str = "error"):
    if accion not in ("error", "cero"):
        raise ValueError(f"accion debe ser 'error' o 'cero', no {accion!r}")
    def decorador(funcion):
        @functools.wraps(funcion)
        def envoltorio(*args, **kwargs):
            resultado = funcion(*args, **kwargs)
            if not math.isfinite(resultado):
                if accion == "error":
                    raise ValueError(f"{funcion.__name__} ha devuelto {resultado}")
                print(f"  aviso: {funcion.__name__} devolvió {resultado}; lo cambio por 0.0")
                return 0.0
            return resultado
        return envoltorio
    return decorador

@vigilar_nan(accion="cero")
def controlador_roto(q, qd):
    return -5.0 * q / qd

print(simular(controlador_roto, segundos=0.01))
```

Dos detalles profesionales: (1) se **valida** el argumento `accion` en el nivel 1, nada más decorar, en vez de esperar a la primera llamada (fallar pronto); (2) ahora hay que escribir `@vigilar_nan()` con paréntesis aunque uses el valor por defecto, porque `vigilar_nan` ya no es un decorador, sino una **fábrica** de decoradores. (Hay un truco para que funcione con y sin paréntesis, comprobando si el primer argumento es una función, pero complica el código: muchas bibliotecas lo hacen, como `@dataclass` y `@dataclass(frozen=True)`.)
</details>
'''),

md(r"""## 10 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **P3**, las **clases intermedias**: los métodos especiales que hacen que tus objetos se comporten como los de Python (`__len__`, `__getitem__`, `__iter__`, `__eq__`, `__call__`...), las **dataclasses** a fondo (`field`, `__post_init__`, `frozen`, `order`), `Enum` y `NamedTuple`, `@classmethod` y `@staticmethod`, propiedades con validación y **composición frente a herencia**.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB44p2_puente_funciones.ipynb")
    build(out, cells, title="NB44·P2 · Puente de Python (2): funciones como piezas")
