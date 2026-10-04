"""Construye NB44·P4 · Puente de Python (4): iterar y gestionar recursos.

Iterable frente a iterador (iter/next, StopIteration, un iterador se gasta).
El protocolo: __iter__ como generador en Trayectoria. Generadores: yield paso
a paso (pausa y reanuda), perezosos e infinitos, una simulación como
generador, send no; yield from; expresiones generadoras (memoria con
sys.getsizeof), cadenas de generadores (tuberías). itertools: count, islice,
chain, product, combinations, accumulate, pairwise, groupby, cycle.
collections: deque (maxlen, ventanas), Counter, defaultdict. Gestores de
contexto: with, __enter__/__exit__ (sus tres argumentos, devolver True traga
el error), contextlib.contextmanager con try/finally, suppress, ExitStack.
Laboratorio de 12 retos.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB44·P4 · Puente de Python (4): iterar y gestionar recursos

**Puente de Python — Lección 4 de 6**

> En el NB23 viste los iteradores y los generadores en una sección cada uno, y en el NB26, `itertools.product` y `Counter` de pasada. Luego, en el NB48, los generadores volvieron como protagonistas (para recorrer contactos), con `itertools` y `collections`; y en el NB49, los gestores de contexto escritos con `contextlib`. Hoy lo asentamos todo, con calma y con muchos ejemplos.

Dos temas, unidos por una misma idea: **hacer las cosas a su debido tiempo**.

1. **Iterar**: producir datos **de uno en uno, cuando se piden**, en vez de todos de golpe. Ahorra memoria, permite secuencias infinitas y encadenar procesos como una tubería.
2. **Gestionar recursos**: hacer algo al **empezar** y deshacerlo **siempre** al **terminar** (cerrar un fichero, restaurar una opción, liberar la cámara), pase lo que pase.
"""),

code(r"""import os
os.environ["MUJOCO_GL"] = "egl"
import sys
import time
import numpy as np
import mujoco

zancudo = mujoco.MjModel.from_xml_path("robots/zancudo.xml")"""),

md(r"""## 1 · Iterables e iteradores

### Dos papeles distintos

Cuando escribes `for x in algo`, intervienen **dos** objetos con papeles diferentes (NB23):

- El **iterable**: la colección que se puede recorrer (una lista, un texto, un diccionario, un `range`...). Es como un **libro**.
- El **iterador**: el objeto que **lleva la cuenta** de por dónde vas, y da el siguiente elemento cuando se le pide. Es como un **marcapáginas**.

Del libro se sacan marcapáginas con **`iter(iterable)`**, y al marcapáginas se le pide la siguiente página con **`next(iterador)`**. Cuando no quedan, `next` lanza **`StopIteration`**:
"""),

code(r"""articulaciones = ["cadera", "rodilla", "tobillo"]      # el iterable (el libro)
marcapaginas = iter(articulaciones)                      # el iterador
print(next(marcapaginas))
print(next(marcapaginas))
print(next(marcapaginas))"""),

code_err(r"""next(marcapaginas)"""),

md(r"""Un `for` hace exactamente esto por dentro: llama a `iter(...)` una vez, y luego a `next(...)` en cada vuelta, hasta que salta `StopIteration`, que el `for` captura en silencio para terminar. Es decir:

```python
for x in articulaciones:          #   iterador = iter(articulaciones)
    print(x)                      #   while True:
                                  #       try: x = next(iterador)
                                  #       except StopIteration: break
                                  #       print(x)
```

### Un iterador se gasta

La diferencia práctica más importante: de un **iterable** puedes sacar **muchos** iteradores (puedes recorrer una lista mil veces), pero un **iterador** se **gasta**: una vez llegado al final, no vuelve a empezar.
"""),

code(r"""marcapaginas = iter(articulaciones)
print("primera vuelta:", list(marcapaginas))
print("segunda vuelta:", list(marcapaginas))          # ¡vacía! el marcapáginas ya está al final
print("la lista sigue entera:", list(articulaciones), list(articulaciones))"""),

md(r"""Esto causa uno de los errores más desconcertantes de Python. `map`, `filter`, `zip`, `enumerate`, los ficheros abiertos y los **generadores** son **iteradores**, no listas. Si los recorres dos veces, la segunda vez están vacíos, sin ningún error:
"""),

code(r"""cuadrados = map(lambda x: x * x, [1, 2, 3])
print(sum(cuadrados))        # 14
print(sum(cuadrados))        # 0: ¡ya se gastó!"""),

md(r"""Si necesitas recorrer algo varias veces, conviértelo primero en lista: `cuadrados = list(map(...))`.

### Tus objetos, iterables: __iter__

En el P3, la `Trayectoria` se podía recorrer gracias a un truco antiguo (`__getitem__`). La forma moderna es definir **`__iter__`**, que debe devolver un iterador. Y la manera más fácil de escribir un iterador es... un **generador**. Antes de verlo, entendamos bien qué es un generador.
"""),

md(r"""## 2 · Generadores

### Una función que se pausa

Un **generador** es una función con **`yield`** en vez de (o además de) `return`. Al llamarla, **no** se ejecuta: devuelve un objeto generador (un iterador). Cada `next` la ejecuta **hasta el siguiente `yield`**, entrega ese valor y **se pausa ahí**, recordando todas sus variables. El siguiente `next` **continúa** desde donde se quedó. Míralo con mensajes:
"""),

code(r"""def tres_pasos():
    print("  (empiezo)")
    yield "paso 1"
    print("  (sigo después del primer yield)")
    yield "paso 2"
    print("  (sigo después del segundo yield)")
    yield "paso 3"
    print("  (termino)")

gen = tres_pasos()
print("he llamado a la función, pero no ha impreso nada:", gen)
print(next(gen))
print(next(gen))"""),

md(r"""Fíjate en el orden: llamar a `tres_pasos()` **no imprime nada** (solo crea el generador). El primer `next` ejecuta hasta el primer `yield` (imprime "(empiezo)" y entrega "paso 1"). El segundo `next` **continúa** justo después de ese `yield`. Y así:
"""),

code(r"""print(next(gen))"""),

code_err(r"""next(gen)"""),

md(r"""El cuarto `next` ejecuta el final ("(termino)") y, al acabar la función sin más `yield`, lanza `StopIteration`. Exactamente el protocolo de iteradores: por eso un generador se puede usar directamente en un `for`.

### Una simulación como generador

Aquí está la utilidad en robótica. Una simulación es, por naturaleza, una **secuencia** de estados. Escrita como generador, **quien la usa decide** cuánto simular y qué hacer con cada estado, sin que la simulación tenga que saberlo:
"""),

code(r"""def simular(modelo: mujoco.MjModel, decimar: int = 1):
    # Genera (tiempo, altura de la cadera, contactos) sin fin, cada `decimar` pasos.
    d = mujoco.MjData(modelo)
    paso = 0
    while True:                                      # ¡infinito! pero solo avanza cuando le piden
        mujoco.mj_step(modelo, d)
        paso += 1
        if paso % decimar == 0:
            yield d.time, 0.865 + d.qpos[1], d.ncon

for tiempo, altura, contactos in simular(zancudo, decimar=250):
    print(f"t = {tiempo:.1f} s: cadera a {altura:.3f} m, {contactos} contactos")
    if tiempo >= 2.0:
        break"""),

md(r"""El generador tiene un `while True`: **nunca termina** por sí solo. Pero no pasa nada, porque es **perezoso**: solo simula cuando el `for` le pide el siguiente estado. Cuando el `for` hace `break`, el generador se queda pausado para siempre (y Python lo limpia).

Compara con la versión "normal", que tendría que recibir los segundos como argumento y devolver una lista enorme con todo. Con el generador:

- **Quien usa** decide cuándo parar (por tiempo, por caída, por lo que quiera).
- **No se guarda nada** que no se pida: memoria constante, aunque simules horas.
- Se pueden **encadenar** generadores, como veremos enseguida.

### __iter__ como generador

Y ya podemos dar a la `Trayectoria` su `__iter__` moderno: un método generador.
"""),

code(r"""class Trayectoria:
    def __init__(self):
        self.tiempos: list[float] = []
        self.alturas: list[float] = []

    def grabar(self, tiempo: float, altura: float) -> None:
        self.tiempos.append(tiempo)
        self.alturas.append(altura)

    def __iter__(self):
        for t, h in zip(self.tiempos, self.alturas):
            yield t, h

    def __len__(self) -> int:
        return len(self.tiempos)

tray = Trayectoria()
for tiempo, altura, _ in simular(zancudo, decimar=100):
    tray.grabar(tiempo, altura)
    if len(tray) == 5:
        break

for t, h in tray:                         # se puede recorrer...
    print(f"{t:.1f} s → {h:.4f} m")
print("¿y otra vez?", len(list(tray)))   # ...las veces que quieras: cada for crea un generador NUEVO"""),

md(r"""Como `__iter__` es un método generador, cada `for` lo llama y obtiene un **iterador nuevo**: la trayectoria (el libro) se puede recorrer muchas veces, cada vez con su propio marcapáginas.

(Y aquí tienes otra versión aún más corta del mismo `__iter__`: `return iter(zip(self.tiempos, self.alturas))`. O con `yield from`, que viene ahora.)

### yield from: delegar en otro iterable

**`yield from iterable`** entrega, uno a uno, todos los elementos de otro iterable. Es un atajo de `for x in iterable: yield x`, muy útil para generadores que **combinan** otros:
"""),

code(r"""def todas_las_articulaciones():
    yield from ["raiz_x", "raiz_z", "raiz_giro"]
    for lado in ["d", "i"]:
        yield from (f"{parte}_{lado}" for parte in ["cadera", "rodilla", "tobillo"])

print(list(todas_las_articulaciones()))
print([zancudo.joint(i).name for i in range(zancudo.njnt)] == list(todas_las_articulaciones()))"""),

md(r"""### Expresiones generadoras

Una **expresión generadora** es como una comprensión de lista, pero con **paréntesis** en vez de corchetes (NB23). No crea la lista: crea un generador que produce los elementos a demanda. La diferencia de memoria es enorme:
"""),

code(r"""lista = [x * x for x in range(1_000_000)]
generador = (x * x for x in range(1_000_000))
print(f"lista:      {sys.getsizeof(lista):>10,} bytes")
print(f"generador:  {sys.getsizeof(generador):>10,} bytes")
print(sum(generador) == sum(lista))"""),

md(r"""La lista ocupa **8 MB** (un millón de referencias); el generador, unos **200 bytes**, porque solo guarda "por dónde va". Cuando solo vas a recorrer una vez los datos (para sumarlos, buscar el máximo, contarlos...), una expresión generadora es lo correcto. Y cuando es el único argumento de una función, se pueden quitar los paréntesis extra: `sum(x * x for x in datos)`, `max(h for _, h in tray)`, `any(c > 0 for c in contactos)`.

### Tuberías de generadores

Lo más elegante: encadenar generadores, cada uno haciendo **una** cosa. Los datos fluyen de uno al siguiente **de uno en uno**, como por una tubería, sin listas intermedias:
"""),

code(r"""def solo_en_el_aire(estados):
    # Deja pasar solo los estados en los que el robot no toca el suelo.
    for tiempo, altura, contactos in estados:
        if contactos == 0:
            yield tiempo, altura

estados = simular(zancudo, decimar=1)                   # fuente (infinita)
en_el_aire = solo_en_el_aire(estados)                    # filtro
primeros = [next(en_el_aire) for _ in range(3)]
print([(round(t, 3), round(float(h), 4)) for t, h in primeros])"""),

md(r"""¡Interesante! Los primeros estados "en el aire" son los del **principio** de la simulación: Zancudo empieza con los pies **5 mm por encima del suelo** (NB48) y tarda unas centésimas en tocarlo (los 16 primeros pasos, hasta t = 0,032 s). Después, ya no despega nunca.

Y aquí hay una **trampa** muy seria, que me pasó de verdad preparando este notebook: si hubiéramos pedido **20** estados en el aire, en vez de 3, la celda se habría quedado **colgada para siempre**. La fuente es infinita, y el filtro sigue pidiéndole estados, uno tras otro, buscando un estado en el aire que **nunca** llega. Sin ningún error, sin ningún aviso: solo un programa que no termina. Moraleja: en una tubería con una fuente infinita y un **filtro**, pon siempre un **límite a la fuente** (con `itertools.islice`, sección 3: `solo_en_el_aire(islice(simular(...), 10_000))`). Entonces, si se acaba, `next(iterador, None)` devuelve `None` en vez de colgarse: con un segundo argumento, `next` entrega ese valor en lugar de lanzar `StopIteration`.

Cada pieza de la tubería es pequeña, se prueba por separado y se reutiliza. Así se procesan en la práctica datos enormes (registros de horas de un robot real, millones de pasos de entrenamiento) sin cargarlos enteros en memoria.
"""),

md(r"""## 3 · itertools: la caja de herramientas de los iteradores

El módulo `itertools` trae piezas listas para construir tuberías. Las más útiles:
"""),

code(r"""import itertools as it

print("count:       ", list(it.islice(it.count(0, 0.002), 4)))            # 0, 0.002, 0.004... sin fin
print("islice:      ", list(it.islice("ABCDEFG", 2, 6)))                 # porción de un iterador
print("chain:       ", list(it.chain([1, 2], (3, 4), "ab")))             # uno detrás de otro
print("cycle:       ", list(it.islice(it.cycle(["apoyo_d", "apoyo_i"]), 5)))   # repetir sin fin
print("accumulate:  ", list(it.accumulate([1, 2, 3, 4])))                # sumas acumuladas
print("pairwise:    ", list(it.pairwise([0.0, 0.1, 0.3, 0.6])))          # parejas consecutivas"""),

md(r"""- **`count(inicio, paso)`**: cuenta sin fin. **`cycle(iterable)`**: repite sin fin (el ciclo de la marcha: apoyo derecho, apoyo izquierdo, apoyo derecho...).
- **`islice(iterador, [inicio,] fin)`**: la "porción" de un iterador. Imprescindible con los infinitos: `islice(simular(...), 100)` = los 100 primeros estados. (Los iteradores no admiten `[a:b]`, porque no se sabe su longitud.)
- **`chain(a, b, ...)`**: uno detrás de otro, sin crear una lista con todo.
- **`accumulate`**: sumas acumuladas (el retorno acumulado de un episodio, NB29).
- **`pairwise`** (Python 3.10+): cada elemento con el siguiente. Perfecto para **diferencias**: velocidades a partir de posiciones, intervalos entre tiempos.

Y tres combinatorias, para barridos de parámetros (NB26, NB48):
"""),

code(r"""kps, kvs = [100, 300], [10, 20]
print("product:      ", list(it.product(kps, kvs)))                    # todas las combinaciones
print("combinations: ", list(it.combinations(["pie_d", "pie_i", "torso"], 2)))     # parejas sin repetir
print("permutations: ", len(list(it.permutations(range(4)))), "órdenes de 4 cosas")"""),

md(r"""- **`product`**: el producto cartesiano, es decir, todas las combinaciones (un bucle anidado escrito en una línea). El barrido de ganancias de siempre.
- **`combinations(iterable, k)`**: todos los grupos de k elementos **sin importar el orden** (las parejas de cuerpos que podrían chocar, NB48).
- **`permutations`**: todas las **ordenaciones** (4! = 24).

### groupby: agrupar elementos consecutivos

`groupby` agrupa elementos **consecutivos** que comparten una clave. Un uso perfecto: encontrar las **fases** de la marcha (tramos seguidos con el pie en el suelo o en el aire) a partir de una secuencia de lecturas de contacto:
"""),

code(r"""contacto_pie = [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1]       # 1 = apoyado, 0 = en el aire
for apoyado, grupo in it.groupby(contacto_pie):
    print(f"{'APOYO' if apoyado else 'vuelo'}: {len(list(grupo))} muestras")"""),

md(r"""Cuidado con la trampa de `groupby`: agrupa solo lo **consecutivo**. Si quieres agrupar todos los iguales aunque estén separados, tienes que **ordenar** antes (o usar un `defaultdict`, que viene ahora). Y cada `grupo` es un iterador que se gasta: por eso lo convertimos en lista para medirlo.
"""),

md(r"""## 4 · collections: estructuras de datos de más

### deque: una cola de dos extremos

Una **`deque`** ("double-ended queue", se pronuncia "dek") es como una lista optimizada para añadir y quitar por **los dos extremos**. Su superpoder es **`maxlen`**: al llenarse, cada elemento nuevo **expulsa** al más antiguo. Es la estructura perfecta para una **ventana deslizante** de las últimas N medidas (P2, R6):
"""),

code(r"""from collections import deque

ventana = deque(maxlen=3)
for medida in [10, 20, 30, 40, 50]:
    ventana.append(medida)
    print(f"entra {medida}: ventana = {list(ventana)}, media = {sum(ventana) / len(ventana):.1f}")"""),

md(r"""En robótica, las ventanas deslizantes están por todas partes: el historial de las últimas acciones que se le da a una política (para que "recuerde" lo que acaba de hacer, NB54), los últimos estados para estimar una velocidad, el retraso de un motor (¡el `nsample` del NB50 es exactamente una ventana de órdenes pasadas!).

Además, añadir o quitar por la **izquierda** (`appendleft`, `popleft`) es instantáneo en una `deque` y lento en una lista (la lista tiene que mover todos los demás elementos). Para una cola de tareas (FIFO: el primero que entra es el primero que sale), `deque`.

### Counter: contar

**`Counter`** cuenta cuántas veces aparece cada cosa (NB26). Por ejemplo, qué parejas de cuerpos están en contacto a lo largo de una simulación:
"""),

code(r"""from collections import Counter

d = mujoco.MjData(zancudo)
pares = Counter()
for paso in range(1000):
    mujoco.mj_step(zancudo, d)
    for i in range(d.ncon):
        g1, g2 = d.contact.geom1[i], d.contact.geom2[i]
        pares[(zancudo.geom(g1).name or f"geom{g1}", zancudo.geom(g2).name or f"geom{g2}")] += 1

print(pares.most_common(3))
print("contactos totales:", pares.total())"""),

md(r"""- `pares[clave] += 1` funciona aunque la clave **no exista** todavía: un `Counter` empieza en 0 para cualquier clave (a diferencia de un `dict`, que daría `KeyError`).
- **`most_common(n)`**: los n más frecuentes. **`total()`**: la suma de todas las cuentas.
- Resultado: los dos pies contra el suelo, con 2 contactos cada uno en cada paso (los dos extremos de la cápsula, NB48) durante los 1.000 pasos... menos los primeros pasos en los que aún no tocaban.

### defaultdict: diccionarios con valor inicial

Un **`defaultdict(fabrica)`** es un diccionario que, cuando le pides una clave que no existe, la **crea** con `fabrica()`. Con `list`, cada clave nueva empieza como una lista vacía: perfecto para **agrupar**:
"""),

code(r"""from collections import defaultdict

experimentos = [("PPO", 412.0), ("SAC", 380.5), ("PPO", 455.2), ("azar", 12.1), ("SAC", 401.3), ("PPO", 430.8)]
por_algoritmo = defaultdict(list)
for algoritmo, nota in experimentos:
    por_algoritmo[algoritmo].append(nota)          # sin comprobar si la clave existía

for algoritmo, notas in por_algoritmo.items():
    print(f"{algoritmo:>5}: {len(notas)} ejecuciones, media {np.mean(notas):.1f}")"""),

md(r"""Sin `defaultdict`, tendrías que escribir `if algoritmo not in por_algoritmo: por_algoritmo[algoritmo] = []` antes de cada `append`. (Otras fábricas útiles: `defaultdict(int)` para contar, que es casi un `Counter`, y `defaultdict(set)` para agrupar sin repetidos.)
"""),

md(r"""## 5 · Gestores de contexto

### El problema: deshacer siempre

Muchas operaciones vienen en **parejas**: abrir/cerrar un fichero, encender/apagar un motor, cambiar/restaurar una opción, crear/liberar el renderizador de MuJoCo, coger/soltar un candado... La segunda mitad tiene que ocurrir **siempre**, incluso si algo falla en medio. Con `try/finally` (NB22) se puede:

```python
renderizador = mujoco.Renderer(modelo)
try:
    imagen = renderizador.render()
finally:
    renderizador.close()          # se ejecuta aunque render() falle
```

Pero hay que acordarse cada vez. La sentencia **`with`** lo empaqueta: un objeto que sabe qué hacer al **entrar** y al **salir**, y Python garantiza que la salida ocurre:

```python
with mujoco.Renderer(modelo) as renderizador:      # ¡el Renderer de MuJoCo es un gestor de contexto!
    imagen = renderizador.render()
# aquí ya está cerrado, pase lo que pase
```

### Por dentro: __enter__ y __exit__

Un **gestor de contexto** es cualquier objeto con dos métodos especiales (P3): **`__enter__`** (al entrar; lo que devuelve va al `as`) y **`__exit__`** (al salir, **siempre**). Escribamos uno que avise de cuánto tiempo **simulado** ha pasado dentro del bloque, para ver cada pieza:
"""),

code(r"""class TramoSimulado:
    def __init__(self, datos: mujoco.MjData, nombre: str):
        self.datos, self.nombre = datos, nombre

    def __enter__(self):
        self.inicio = self.datos.time
        print(f"[{self.nombre}] entra en t = {self.inicio:.3f} s")
        return self

    def __exit__(self, tipo, valor, traza):
        print(f"[{self.nombre}] sale en t = {self.datos.time:.3f} s "
              f"({self.datos.time - self.inicio:.3f} s simulados); error: {tipo.__name__ if tipo else 'ninguno'}")
        return False

d = mujoco.MjData(zancudo)
with TramoSimulado(d, "de pie"):
    for paso in range(250):
        mujoco.mj_step(zancudo, d)"""),

md(r"""Los tres argumentos de `__exit__` describen el error que ha ocurrido dentro del bloque (si lo hubo): su **tipo** (la clase, como `ValueError`), su **valor** (el objeto excepción, con el mensaje) y la **traza**. Si el bloque terminó bien, los tres son `None`.

Y el valor que **devuelve** `__exit__` decide qué pasa con el error:

- **`False`** (o nada): el error **sigue su camino** (sale del `with` y lo verás, o lo capturará un `try` de fuera). Es lo normal.
- **`True`**: el error se **traga**: desaparece, como si no hubiera pasado. Solo para gestores diseñados exactamente para eso.

Comprobemos que la salida ocurre aunque haya un error:
"""),

code_err(r"""with TramoSimulado(d, "con error"):
    mujoco.mj_step(zancudo, d)
    raise RuntimeError("algo ha ido mal a mitad")"""),

md(r"""Primero se imprimen los mensajes de entrada y **de salida** (con el tipo de error: `RuntimeError`), y **después** aparece el error, porque `__exit__` devolvió `False`. La salida está garantizada.

### La forma corta: contextlib.contextmanager

Escribir una clase con dos métodos para cada gestor es pesado. El decorador **`contextlib.contextmanager`** convierte un **generador con un solo `yield`** en un gestor de contexto (NB49):

- lo de **antes** del `yield` es la entrada (`__enter__`),
- lo que se entrega con `yield` va al `as`,
- lo de **después** es la salida (`__exit__`)... y para que ocurra **aunque haya error**, va dentro de un **`finally`**.
"""),

code(r"""from contextlib import contextmanager

@contextmanager
def gravedad(modelo: mujoco.MjModel, g: float):
    original = modelo.opt.gravity.copy()            # ¡.copy()! (si no, guardaríamos una vista, NB45)
    modelo.opt.gravity[:] = [0, 0, -g]
    try:
        yield modelo
    finally:
        modelo.opt.gravity[:] = original

with gravedad(zancudo, 1.62):
    print("en la Luna:", zancudo.opt.gravity)
print("de vuelta:  ", zancudo.opt.gravity)"""),

md(r"""¿Por qué el generador encaja tan bien? Porque un generador **se pausa** en el `yield`: el `with` ejecuta hasta el `yield` (entrada), deja que corra el bloque, y luego **reanuda** el generador para que ejecute lo de después (salida). Si el bloque lanza un error, `contextmanager` lo **relanza dentro** del generador, justo en la línea del `yield`... y por eso hace falta el `try/finally`: sin él, el error saltaría por encima de la restauración.

Dos detalles de este ejemplo que son trampas de verdad:

1. **`.copy()`** al guardar la gravedad original: `modelo.opt.gravity` es una **vista** de la memoria de MuJoCo (NB45). Sin la copia, `original` cambiaría al cambiar la gravedad, y "restauraríamos" la gravedad de la Luna.
2. **`gravity[:] = ...`** en vez de `gravity = ...`: escribe **dentro** del array de MuJoCo, en lugar de intentar sustituirlo.

### Dos gestores útiles de la biblioteca estándar

**`contextlib.suppress(Error)`**: ignora un tipo de error concreto dentro del bloque (un `try/except: pass` en una línea, para cuando de verdad no te importa):
"""),

code(r"""from contextlib import suppress
from pathlib import Path

with suppress(FileNotFoundError):
    Path("este_fichero_no_existe.txt").unlink()        # borrar si existe; si no, nada
print("seguimos sin problemas")"""),

md(r"""**`contextlib.ExitStack`**: para cuando el **número** de gestores no se sabe de antemano (abrir N ficheros, crear N renderizadores...). Se van "apilando" con `enter_context`, y al salir los cierra todos, en orden inverso:
"""),

code(r"""from contextlib import ExitStack

modelos = [mujoco.MjModel.from_xml_path("robots/zancudo.xml") for _ in range(3)]
with ExitStack() as pila:
    for i, m in enumerate(modelos):
        pila.enter_context(gravedad(m, g=1.62 * (i + 1)))
    print("dentro:", [float(m.opt.gravity[2]) for m in modelos])
print("fuera: ", [float(m.opt.gravity[2]) for m in modelos])"""),

md(r"""Y varios gestores **conocidos** se pueden poner en un mismo `with`, separados por comas: `with open(a) as f1, open(b) as f2:`.
"""),

md(r"""## 6 · Resumen

1. **Iterable** (el libro: se recorre muchas veces) frente a **iterador** (el marcapáginas: `iter`, `next`, `StopIteration`; **se gasta**). `map`, `filter`, `zip`, `enumerate`, ficheros y generadores son iteradores.
2. **Generadores**: funciones con `yield` que se **pausan** y se reanudan. Perezosos; pueden ser **infinitos** (una simulación); memoria constante. `__iter__` como generador: el objeto se recorre muchas veces. `yield from` delega.
3. **Expresiones generadoras** `(… for …)`: sin lista intermedia (8 MB frente a 200 B). **Tuberías** de generadores.
4. **`itertools`**: `count`, `cycle`, `islice` (porciones de iteradores), `chain`, `accumulate`, `pairwise`, `product`, `combinations`, `permutations`, `groupby` (solo consecutivos).
5. **`collections`**: `deque(maxlen=N)` (ventanas deslizantes, colas), `Counter` (`most_common`, `total`), `defaultdict(list)` (agrupar).
6. **Gestores de contexto**: `with` garantiza la salida. `__enter__` (→ `as`) y `__exit__(tipo, valor, traza)` (devolver `True` traga el error). **`@contextmanager`** + un `yield` + **`try/finally`**. `suppress`, `ExitStack`.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Iterable** | Objeto que se puede recorrer (tiene `__iter__`). |
| **Iterador** | Objeto que da los elementos de uno en uno con `next`, y se gasta. |
| **Perezoso** | Que calcula cada valor solo cuando se le pide. |
| **Tubería (*pipeline*)** | Cadena de etapas por las que fluyen los datos de uno en uno. |
| **Ventana deslizante** | Los N últimos elementos de una secuencia, que avanzan con ella. |
| **FIFO** | "First in, first out": cola donde sale primero lo que entró primero. |
| **Gestor de contexto** | Objeto que se usa con `with`: hace algo al entrar y al salir. |
"""),

md(r"""## 7 · Laboratorio

**R1.** ★ Predice la salida: `z = zip([1, 2, 3], "abc"); print(list(z)); print(list(z))`.

**R2.** Escribe un generador `cuenta_atras(n)` que entregue n, n−1, ..., 1 y, al final, `"¡despegue!"`. Úsalo en un `for`.

**R3.** Usando `simular` (sección 2) e `itertools.islice`, guarda en una lista los **10 primeros** estados con `decimar=50`, sin escribir ningún `break`.

**R4.** ★ Escribe un generador `velocidades(estados)` que reciba un iterable de `(tiempo, altura, contactos)` y entregue `(tiempo, velocidad_vertical)` calculando la velocidad como diferencia de alturas entre estados consecutivos dividida por la diferencia de tiempos. (Pista: `itertools.pairwise`.) Úsalo sobre los 5 primeros estados de `simular(zancudo, decimar=10)`.

**R5.** Escribe un generador `simular_agachado(modelo, profundidad, t_orden)` que, a partir del instante `t_orden`, mande a los motores la postura agachada (cadera p, rodilla −2p, tobillo p), y entregue `(tiempo, altura)` cada 50 pasos. ¿Cuánto baja la cadera con p = 0,5?

**R6.** Con `groupby`, cuenta cuántos **tramos** de apoyo y cuántos de vuelo hay en `[1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0]` y la duración del tramo de vuelo más largo.

**R7.** Con `Counter`, cuenta las letras de `"zancudo anda despacio"` (sin espacios) y muestra las 3 más frecuentes.

**R8.** Con una `deque(maxlen=5)`, escribe una función que reciba una secuencia de alturas y devuelva la primera posición en la que la **media de las 5 últimas** baja de 0,8 m (señal de que el robot se está cayendo). Pruébala con `[0.86] * 10 + [0.85, 0.80, 0.72, 0.60, 0.45, 0.30]`.

**R9.** Con `defaultdict(list)`, agrupa las articulaciones de Zancudo por **lado** (`"d"`, `"i"` o `"raiz"`) a partir de sus nombres.

**R10.** ★ Escribe un gestor de contexto con `@contextmanager` llamado `pasito(modelo, dt)` que cambie temporalmente el pasito de tiempo y lo restaure. Comprueba con un error dentro del bloque que se restaura igualmente.

**R11.** Escribe un gestor de contexto **como clase**, `ContarPasos`, que al entrar guarde `datos.time` y al salir imprima cuántos pasos de simulación se han dado dentro del bloque (tiempo transcurrido / pasito). Haz que su `__enter__` devuelva el propio objeto y que tenga un atributo `pasos` que se pueda leer después del `with`.

**R12.** ★ Escribe un gestor de contexto `ignorar_explosion()` que **trague** solo los errores `FloatingPointError` (y ninguno más), imprimiendo un aviso. Pruébalo con `np.errstate(all="raise")` (otro gestor de contexto, de NumPy, que convierte los avisos numéricos en errores) y una división `np.float64(1.0) / 0.0`.
"""),

md(r'''<details>
<summary>▶ Solución R1</summary>

`[(1, 'a'), (2, 'b'), (3, 'c')]` y después `[]`. `zip` devuelve un **iterador**, que el primer `list` gasta. Es un error clásico al guardar un `zip` en una variable para usarlo dos veces: si lo necesitas varias veces, `pares = list(zip(...))`.
</details>

<details>
<summary>▶ Solución R2</summary>

```python
def cuenta_atras(n: int):
    while n > 0:
        yield n
        n -= 1
    yield "¡despegue!"

for valor in cuenta_atras(3):
    print(valor)          # 3 2 1 ¡despegue!
```

Un generador puede tener varios `yield` en sitios distintos: entrega lo que encuentre, en el orden en que se ejecutan.
</details>

<details>
<summary>▶ Solución R3</summary>

```python
import itertools as it
primeros = list(it.islice(simular(zancudo, decimar=50), 10))
print(len(primeros), primeros[0][0], primeros[-1][0])     # 10, 0.1, 1.0
```

`islice` pide al generador exactamente 10 elementos y para. Como el generador es perezoso, solo se simulan 500 pasos (10 × 50), ni uno más. (El primer tiempo es 0,1 s, no 0,002, porque decimar=50 entrega el estado tras 50 pasos.)
</details>

<details>
<summary>▶ Solución R4</summary>

```python
def velocidades(estados):
    for (t0, h0, _), (t1, h1, _) in it.pairwise(estados):
        yield t1, (h1 - h0) / (t1 - t0)

for t, v in it.islice(velocidades(simular(zancudo, decimar=10)), 5):
    print(f"t = {t:.2f} s: velocidad vertical {v:+.4f} m/s")
```

La primera velocidad es negativa (cae los 5 mm hasta tocar el suelo), y después salen valores pequeños positivos y negativos: el pequeño rebote del contacto blando (NB48), que se va apagando. Fíjate en el **desempaquetado anidado** del `for`: cada elemento de `pairwise` es una pareja de estados, y cada estado una tupla de tres. ¡Y la tubería sigue siendo perezosa: `pairwise` también es un iterador!
</details>

<details>
<summary>▶ Solución R5</summary>

```python
def simular_agachado(modelo, profundidad: float, t_orden: float):
    d = mujoco.MjData(modelo)
    postura = np.array([profundidad, -2 * profundidad, profundidad] * 2)
    paso = 0
    while True:
        if d.time >= t_orden:
            d.ctrl[:] = postura
        mujoco.mj_step(modelo, d)
        paso += 1
        if paso % 50 == 0:
            yield d.time, 0.865 + d.qpos[1]

alturas = [h for t, h in it.islice(simular_agachado(zancudo, 0.5, t_orden=0.5), 40)]
print(f"antes (0,4 s): {alturas[3]:.3f} m;  al final (2 s): {alturas[-1]:.3f} m")
```

Antes de la orden, 0,859 m; tras agacharse, unos **0,75 m** (como el keyframe `agachado` del NB50: 0,751). Baja unos 11 cm.
</details>

<details>
<summary>▶ Solución R6</summary>

```python
secuencia = [1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0]
tramos = [(clave, len(list(grupo))) for clave, grupo in it.groupby(secuencia)]
print(tramos)
print("apoyos:", sum(1 for c, _ in tramos if c == 1), "| vuelos:", sum(1 for c, _ in tramos if c == 0))
print("vuelo más largo:", max(n for c, n in tramos if c == 0))
```

3 tramos de apoyo y 3 de vuelo, y el vuelo más largo dura 3 muestras.
</details>

<details>
<summary>▶ Solución R7</summary>

```python
from collections import Counter
print(Counter("zancudo anda despacio".replace(" ", "")).most_common(3))
# [('a', 4), ('d', 3), ('n', 2)]  (los empates salen en el orden en que aparecen por primera vez)
```

Un `Counter` acepta directamente cualquier iterable: un texto se recorre letra a letra.
</details>

<details>
<summary>▶ Solución R8</summary>

```python
from collections import deque

def detectar_caida(alturas, umbral: float = 0.8, n: int = 5):
    ventana = deque(maxlen=n)
    for posicion, h in enumerate(alturas):
        ventana.append(h)
        if len(ventana) == n and sum(ventana) / n < umbral:
            return posicion
    return None

alturas = [0.86] * 10 + [0.85, 0.80, 0.72, 0.60, 0.45, 0.30]
print(detectar_caida(alturas))      # 13
```

En la posición 13, las 5 últimas son 0,86; 0,85; 0,80; 0,72; 0,60 → media 0,766 < 0,8. La media de una ventana es más **robusta** que mirar una sola medida (un sensor ruidoso podría dar un 0,79 suelto sin que el robot se caiga). `len(ventana) == n` evita decidir antes de tener la ventana llena.
</details>

<details>
<summary>▶ Solución R9</summary>

```python
from collections import defaultdict

por_lado = defaultdict(list)
for i in range(zancudo.njnt):
    nombre = zancudo.joint(i).name
    lado = "raiz" if nombre.startswith("raiz") else nombre.split("_")[-1]
    por_lado[lado].append(nombre)
print(dict(por_lado))
```

`dict(por_lado)` lo convierte en un diccionario normal para imprimirlo más limpio.
</details>

<details>
<summary>▶ Solución R10</summary>

```python
@contextmanager
def pasito(modelo, dt: float):
    original = modelo.opt.timestep
    modelo.opt.timestep = dt
    try:
        yield modelo
    finally:
        modelo.opt.timestep = original

try:
    with pasito(zancudo, 0.01):
        print("dentro:", zancudo.opt.timestep)
        raise ValueError("fallo a propósito")
except ValueError:
    pass
print("después:", zancudo.opt.timestep)      # 0.002
```

Aquí **no** hace falta `.copy()`: `timestep` es un número (inmutable), no un array. La copia solo es necesaria con arrays (vistas).
</details>

<details>
<summary>▶ Solución R11</summary>

```python
class ContarPasos:
    def __init__(self, modelo, datos):
        self.modelo, self.datos = modelo, datos
        self.pasos = 0

    def __enter__(self):
        self.inicio = self.datos.time
        return self

    def __exit__(self, tipo, valor, traza):
        self.pasos = round((self.datos.time - self.inicio) / self.modelo.opt.timestep)
        print(f"  {self.pasos} pasos dentro del bloque")
        return False

d = mujoco.MjData(zancudo)
with ContarPasos(zancudo, d) as contador:
    for _ in range(123):
        mujoco.mj_step(zancudo, d)
print(contador.pasos)        # 123
```

El objeto del `as` **sigue existiendo** después del `with` (el `with` no lo borra, solo llama a `__exit__`), así que podemos leer `contador.pasos`. Usamos `round` porque `(tiempo / pasito)` da algo como 122,99999999 (decimales, otra vez).
</details>

<details>
<summary>▶ Solución R12</summary>

```python
@contextmanager
def ignorar_explosion():
    try:
        yield
    except FloatingPointError as e:
        print(f"  aviso: explosión numérica ignorada ({e})")

with ignorar_explosion(), np.errstate(all="raise"):
    x = np.float64(1.0) / 0.0
    print("esto no se imprime")
print("y seguimos")
```

Con `@contextmanager`, "tragar" un error es simplemente **capturarlo** con `except` alrededor del `yield` (y no relanzarlo). Solo se tragan los `FloatingPointError`: cualquier otro error sale normalmente. Es justo lo que hace `contextlib.suppress(FloatingPointError)`, pero con un aviso. Fíjate en el orden de los dos gestores en el `with`: el de fuera (el primero) captura lo que lanza el bloque de dentro. (En general, **tragar** errores es peligroso: úsalo solo cuando sepas exactamente qué error esperas y por qué no importa.)
</details>
'''),

md(r"""## 8 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **P5**, **tipos y errores profesionales**: las anotaciones de tipo de lo más básico (`int`, `list[float]`) a lo avanzado (`Optional`, `Callable`, `TypeAlias`, `Protocol`, genéricos, `Self`), cómo las comprueba una herramienta (y por qué Python no lo hace), excepciones **propias** con jerarquías, `raise ... from`, y el módulo `logging` a fondo.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB44p4_puente_iterar_y_recursos.ipynb")
    build(out, cells, title="NB44·P4 · Puente de Python (4): iterar y gestionar recursos")
