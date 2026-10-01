"""Construye NB21 · Python de verdad (2): colecciones.

Tuplas (inmutables, desempaquetar, intercambiar, el return de dos valores era
una tupla); listas a fondo (insert, pop, remove, index, extend, del, sort vs
sorted, reverse, porciones con salto, [::-1]); LA TRAMPA DEL ALIAS (dos
etiquetas, una caja; copy / list / [:]; copia superficial); enumerate y zip;
comprensiones de listas (con if); diccionarios (clave → valor, KeyError real,
get, añadir/cambiar/borrar, in, keys/values/items, anidados = configuración,
comprensión de diccionario, contar frecuencias); conjuntos (sin duplicados,
unión/intersección/diferencia); any/all; ordenar por una clave con key=función.
Proyecto: configuración de un entrenamiento + ranking de políticas.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB21 · Python de verdad (2): colecciones

**Parte 3 · Python de verdad — Lección 2**

> En el **NB20** aprendiste a manejar texto como un profesional. Hoy toca la otra herramienta de todos los días: las
> **colecciones**, es decir, las formas de guardar **muchos datos juntos**.

Ya conoces una colección: la **lista** (NB09). Hoy la estudiaremos a fondo (con una trampa famosísima que **tienes** que conocer
para no perder horas buscando un error), y conocerás tres más:

- La **tupla**: una lista que no se puede cambiar.
- El **diccionario**: datos con **nombre**, la estructura de todas las configuraciones.
- El **conjunto**: una colección sin repetidos.

Y al final, juntaremos todo para guardar la **configuración completa de un entrenamiento** y hacer un **ranking** de políticas, como en un
proyecto de verdad.
"""),

md(r"""## 1 · Tuplas: listas que no cambian

Una **tupla** es como una lista, pero se escribe con **paréntesis** en vez de corchetes, y, como las cadenas (NB20), es **inmutable**: una vez
creada, no se puede cambiar. Ya la viste de pasada en el NB15: la **forma** de un array, `(17, 348)`, es una tupla.
"""),

code(r"""posicion_pie = (0.25, -0.10, 0.0)      # x, y, z en metros
print(posicion_pie)
print(posicion_pie[0])
print(len(posicion_pie))"""),

md(r"""Índices y `len`, como en una lista. Pero si intentas cambiarla:"""),

code_err(r"""posicion_pie[2] = 0.5"""),

md(r"""`TypeError: 'tuple' object does not support item assignment`, el mismo error que con las cadenas. **¿Para qué quiero algo que no puedo
cambiar?** Para datos que **forman un todo fijo** y que no deberían modificarse por accidente: una posición (x, y, z), un color (rojo, verde,
azul), el tamaño de una matriz (filas, columnas). Si alguien intenta cambiarlos sin querer, Python lo impide. Es una **protección**.

(Un detalle curioso: una tupla de **un solo** elemento se escribe con una coma, `(5,)`, porque `(5)` sería simplemente el número 5 entre
paréntesis. Por eso la forma de un vector en NumPy sale como `(348,)`, NB15.)
"""),

md(r"""### Desempaquetar

La tupla tiene un truco precioso, que ya has usado sin saber su nombre. Si a la izquierda del `=` pones **varias cajas** separadas por comas, Python
**reparte** los elementos de la tupla entre ellas. Se llama **desempaquetar**:
"""),

code(r"""x, y, z = posicion_pie
print("x =", x, "| y =", y, "| z =", z)"""),

md(r"""Cada caja se lleva un elemento, por orden. (El número de cajas tiene que coincidir con el de elementos; si no, `ValueError`.)

¿Y te acuerdas de las funciones que devolvían dos valores, como `return altura, velocidad` en el NB10? **Estaban devolviendo una tupla**. Y
`altura, velocidad = paso_pelota(...)` la estaba **desempaquetando**. Lo mismo que `observacion, info = entorno.reset()` en el NB15. Ahora sabes qué
pasaba por debajo:
"""),

code(r"""def reiniciar():
    return 2.0, 0.0

resultado = reiniciar()
print(resultado, type(resultado))"""),

md(r"""`(2.0, 0.0)`, de tipo `tuple`. La coma en el `return` fabrica una tupla.

Y un truco elegantísimo que sale de aquí: **intercambiar** el contenido de dos cajas en una sola línea (en otros lenguajes hace falta una caja
auxiliar):
"""),

code(r"""a, b = 1, 2
a, b = b, a
print(a, b)"""),

md(r"""## 2 · Listas a fondo

Las listas tienen muchos más métodos que el `append` del NB09. Vamos con los importantes, sobre una lista de retornos:"""),

code(r"""retornos = [44.8, 213.5, 97.2, 455.3]

retornos.insert(1, 120.0)      # mete 120.0 en la posición 1 (desplaza el resto)
print(retornos)

ultimo = retornos.pop()        # saca el ÚLTIMO y lo devuelve
print("sacado:", ultimo, "| quedan:", retornos)

retornos.remove(213.5)         # quita el primer elemento que valga 213.5
print(retornos)"""),

md(r"""- **`insert(posición, valor)`** mete un elemento donde digas.
- **`pop()`** saca el último **y te lo da** (muy útil para ir "gastando" una lista). Con un índice, `pop(0)`, saca ese.
- **`remove(valor)`** quita el primer elemento con ese valor (si no existe, `ValueError`).

Unos cuantos más:
"""),

code(r"""print(retornos.index(97.2))         # ¿en qué posición está?
retornos.extend([300.0, 499.9])     # añade VARIOS al final (append añadiría la lista entera como un elemento)
print(retornos)
del retornos[0]                     # borra por posición
print(retornos)"""),

md(r"""### Ordenar: `sort` contra `sorted`

Hay **dos** formas de ordenar, y conviene no confundirlas:

- **`lista.sort()`** ordena **la propia lista**, cambiándola, y **no devuelve nada** (`None`, NB10).
- **`sorted(lista)`** **no toca** la lista: devuelve una lista **nueva**, ordenada.
"""),

code(r"""numeros = [3, 1, 2]
nueva = sorted(numeros)
print("sorted:", nueva, "| la original sigue:", numeros)

numeros.sort()
print("después de sort:", numeros)

print("de mayor a menor:", sorted(numeros, reverse=True))"""),

md(r"""Un error clásico es escribir `numeros = numeros.sort()`: como `sort` devuelve `None`, ¡te quedas con `None` y pierdes la lista! Regla: **`sort`
cambia y no devuelve; `sorted` devuelve y no cambia.** (`reverse=True` ordena de mayor a menor.)
"""),

md(r"""### Porciones con salto

Las porciones (NB09) admiten un **tercer número**, el **salto**, igual que `range` (NB07): `lista[inicio:fin:salto]`:"""),

code(r"""pasos = list(range(10))
print(pasos)
print(pasos[::2])       # de 2 en 2: todos los pares
print(pasos[::-1])      # salto -1: ¡al revés!"""),

md(r"""(`list(range(10))` convierte el recorrido de `range` en una lista de verdad, para poder verla.) `[::-1]` es el truco más usado para **dar la vuelta**
a una lista (o a una cadena: `"hola"[::-1]` da `"aloh"`). Y `[::2]` sirve, por ejemplo, para quedarte con una de cada dos fotos de una trayectoria.
"""),

md(r"""## 3 · La trampa del alias (importantísimo)

Esta es una de las fuentes de errores más famosas de Python. Lee esto con calma, porque **te va a pasar**.

Mira este código. Creamos una lista, hacemos una "copia" con `=`, y cambiamos la copia:
"""),

code(r"""original = [1, 2, 3]
copia = original
copia.append(4)

print("copia:   ", copia)
print("original:", original)"""),

md(r"""¡¿La **original** también tiene el 4?! No hemos tocado `original`... ¿o sí?

Lo que pasa es que `copia = original` **no copia la lista**. Lo que hace es pegarle **una segunda etiqueta** a **la misma caja**. Hay **una sola lista**,
con dos nombres:

```
   copia = original

   original ──┐
              ├──►  [1, 2, 3]      ← UNA sola lista, con dos etiquetas
   copia ─────┘

   copia.append(4) cambia ESA lista... y se ve desde las dos etiquetas.
```

Cuando dos nombres apuntan al mismo objeto, se dice que uno es un **alias** del otro. Con las cajas de números del NB06 no se notaba, porque los números
(como las cadenas y las tuplas) son inmutables: "cambiarlos" siempre crea uno nuevo. Pero las listas (y los diccionarios, y los arrays de NumPy) se pueden
**cambiar por dentro**, y entonces el alias muerde.

**¿Cómo se hace una copia de verdad?** Con el método **`copy()`** (que ya usaste con un array en el NB18), o con `list(...)`, o con la porción completa `[:]`:
"""),

code(r"""original = [1, 2, 3]
copia = original.copy()
copia.append(4)

print("copia:   ", copia)
print("original:", original)"""),

md(r"""Ahora sí: dos listas **independientes**. Para comprobar si dos nombres son **el mismo objeto** (no solo "iguales por dentro"), existe la palabra **`is`**:"""),

code(r"""a = [1, 2, 3]
b = a
c = a.copy()
print("a == c:", a == c, "(iguales por dentro)")
print("a is b:", a is b, "(el mismo objeto)")
print("a is c:", a is c, "(objetos distintos)")"""),

md(r"""**Dónde te morderá en robótica:** guardas el estado de un robot en una lista, la añades al historial de la trayectoria (NB09), y luego **modificas el
estado** para el siguiente paso... y todo el historial cambia a la vez, porque guardaste muchas veces **la misma** lista. La solución: guardar una **copia**
cada vez (`historial.append(estado.copy())`).

(Un último matiz, para más adelante: `copy()` hace una **copia superficial**. Si la lista contiene **otras listas** dentro (como una matriz, NB14), la copia
tiene sus propias "filas"... que siguen siendo las mismas listas de dentro. Para copiarlo todo, hasta el fondo, existe `copy.deepcopy`, del módulo `copy`.)
"""),

md(r"""## 4 · Recorrer con número: `enumerate`

Muchas veces, al recorrer una lista, necesitas **el elemento y su posición**. Podrías usar `range(len(...))` (NB09), pero hay una forma más limpia:
**`enumerate`**, que en cada vuelta te da **una tupla** (posición, elemento), que se desempaqueta en el propio `for`:
"""),

code(r"""motores = ["cadera", "rodilla", "tobillo"]
for i, motor in enumerate(motores):
    print(i, motor)"""),

md(r"""## 5 · Recorrer dos listas a la vez: `zip`

Y para recorrer **dos listas emparejadas** (las listas paralelas del NB09), **`zip`** ("cremallera"): junta los elementos de las dos listas por parejas,
como los dientes de una cremallera:
"""),

code(r"""valores = [0.3, -0.4, 0.1]
for motor, valor in zip(motores, valores):
    print(f"{motor:>8}: {valor:+.1f}")"""),

md(r"""Mucho más legible que `for i in range(len(motores)): print(motores[i], valores[i])`. **`enumerate` y `zip` son de las herramientas más usadas de Python**;
cuando veas `range(len(...))` en un código, casi siempre se puede escribir mejor con una de las dos.
"""),

md(r"""## 6 · Comprensiones de listas

En el NB14 viste de pasada una forma corta de fabricar listas: `[round(a, 2) for a in acciones]`. Se llama **comprensión de listas** y es una de las cosas
más "pythónicas" que existen (es decir, muy del estilo de Python). Es una forma de escribir en **una línea** este patrón tan común:

```
   resultado = []                          resultado = [x ** 2 for x in numeros]
   for x in numeros:              =
       resultado.append(x ** 2)
```

Se lee casi en castellano: "**x al cuadrado, para cada x en números**".
"""),

code(r"""numeros = [1, 2, 3, 4, 5]
cuadrados = [x ** 2 for x in numeros]
print(cuadrados)"""),

md(r"""Y admite un **filtro** con `if` al final: solo entran los elementos que cumplen la condición. Por ejemplo, quedarse solo con los retornos de los
episodios **completos** (más de 400 puntos), redondeados:
"""),

code(r"""retornos = [44.8, 97.23, 213.5, 455.31, 499.94]
buenos = [round(r) for r in retornos if r > 400]
print(buenos)"""),

md(r""""El retorno redondeado, para cada retorno, **si** es mayor que 400". Úsalas cuando la lista se pueda describir en una frase corta; si la lógica es
complicada, un bucle normal es más claro. **La claridad siempre gana a la brevedad.**
"""),

md(r"""## 7 · Diccionarios: datos con nombre

Imagina que quieres guardar la **ficha** de un robot: su nombre, su número de motores, su masa, si tiene tobillos... Con una lista tendrías que acordarte
de que "la posición 0 es el nombre, la 1 los motores, la 2 la masa"... un desastre.

Un **diccionario** guarda los datos con **nombre**: cada valor va asociado a una **clave**. Como un diccionario de papel, donde cada palabra (la clave)
tiene su definición (el valor). Se escribe con **llaves** `{ }`, con parejas `clave: valor` separadas por comas:
"""),

code(r"""robot = {
    "nombre": "Humanoid-v5",
    "motores": 17,
    "masa_kg": 40.0,
    "tiene_tobillos": False,
}
print(robot)"""),

md(r"""Para sacar un valor, se usa su **clave** entre corchetes (en vez de una posición):"""),

code(r"""print(robot["nombre"])
print(robot["motores"])"""),

md(r"""Mucho más legible que `robot[1]`: el código **dice** lo que hace. ¿Y si pides una clave que no existe?"""),

code_err(r"""print(robot["altura"])"""),

md(r"""`KeyError: 'altura'`: "**error de clave**: no existe la clave `'altura'`". Otro tipo de error para la colección, el primo del `IndexError` de las listas.

Para evitarlo, existe el método **`get`**, que devuelve `None` (o el valor que le digas) si la clave no está, en vez de dar error:
"""),

code(r"""print(robot.get("altura"))
print(robot.get("altura", 1.4))"""),

md(r"""### Añadir, cambiar, borrar y preguntar

Los diccionarios se pueden cambiar (como las listas: ¡cuidado con los alias del apartado 3!). Guardar con una clave **nueva** la **añade**; con una clave
que ya existe, **cambia** su valor:
"""),

code(r"""robot["altura"] = 1.4          # clave nueva: se añade
robot["masa_kg"] = 41.5        # clave existente: se cambia
del robot["tiene_tobillos"]    # se borra
print(robot)
print("¿Tiene 'motores'?", "motores" in robot)
print("Número de claves:", len(robot))"""),

md(r"""`in` pregunta si existe una **clave** (no un valor).

### Recorrer un diccionario

Hay tres formas, según lo que quieras: las **claves** (`keys`), los **valores** (`values`) o las **parejas** (`items`, que da tuplas para desempaquetar):
"""),

code(r"""for clave, valor in robot.items():
    print(f"{clave:>8}: {valor}")"""),

md(r"""`.items()` es, con diferencia, la más usada. (Desde hace años, los diccionarios de Python **recuerdan el orden** en que se añadieron las claves.)

### ¿Dónde están los diccionarios en robótica? En todas partes

- El `info` que devuelve `entorno.step(...)` en Gymnasium (NB15) **es un diccionario**, con datos extra sobre el paso.
- Las **configuraciones** de un entrenamiento (tasa de aprendizaje, número de pasos, tamaño de la red...) se guardan en diccionarios.
- Los **resultados** de un experimento ("retorno medio": 455,3; "episodios": 50...).
- Las redes de PyTorch guardan sus pesos en un diccionario (lo verás).

Miremos el `info` de verdad del humanoide:
"""),

code(r"""import gymnasium as gym
import numpy as np

entorno = gym.make("Humanoid-v5")
observacion, info = entorno.reset(seed=0)
observacion, recompensa, terminado, truncado, info = entorno.step(np.zeros(17))
entorno.close()

print(type(info))
for clave, valor in info.items():
    if isinstance(valor, float):
        print(f"{clave:>16}: {valor:.4f}")"""),

md(r"""¡Un diccionario! Y entre sus claves están los **ingredientes de la recompensa** del NB04, por separado: `reward_survive` (el +5 por seguir de pie),
`reward_forward` (el premio por avanzar), `reward_ctrl` (el castigo por esfuerzo) y `reward_contact` (el de los golpes). Sumados, dan la recompensa del
paso. (`isinstance(valor, float)` pregunta "¿es `valor` un número decimal?"; lo usamos para mostrar solo los números y saltarnos datos más complejos.)

Con esto, un ingeniero puede **vigilar cada ingrediente por separado** durante el entrenamiento, y detectar trampas como las del NB04 (por ejemplo, ver que
casi todos los puntos vienen de `reward_survive` y casi nada de `reward_forward`: ¡el robot se está quedando quieto!).
"""),

md(r"""### Diccionarios dentro de diccionarios

Los valores de un diccionario pueden ser **cualquier cosa**: listas, otros diccionarios... Así se construyen estructuras complejas, como la configuración
completa de un entrenamiento:
"""),

code(r"""configuracion = {
    "entorno": "Humanoid-v5",
    "semillas": [0, 1, 2, 3, 4],
    "red": {"capas_ocultas": [256, 256], "activacion": "relu"},
    "entrenamiento": {"tasa": 0.0003, "pasos_totales": 10_000_000},
}

print(configuracion["red"]["capas_ocultas"])
print(configuracion["entrenamiento"]["tasa"])
print(len(configuracion["semillas"]), "semillas")"""),

md(r"""Para llegar a un dato "profundo", se encadenan las claves: `configuracion["red"]["capas_ocultas"]` es "de la configuración, la red; y de la red, las capas
ocultas". Esta estructura es **exactamente** la de los ficheros de configuración que se usan en los proyectos de verdad (en el NB26 aprenderemos a guardarla
en un fichero y a cargarla).
"""),

md(r"""### Contar con un diccionario

Un uso clásico: **contar** cuántas veces aparece cada cosa. La clave es la cosa; el valor, cuántas veces la hemos visto. Por ejemplo, ¿por qué terminaron
estos episodios?
"""),

code(r"""finales = ["caída", "tiempo", "caída", "caída", "tiempo", "caída"]

conteo = {}
for final in finales:
    conteo[final] = conteo.get(final, 0) + 1
print(conteo)"""),

md(r"""El truco está en `conteo.get(final, 0) + 1`: "lo que hubiera contado hasta ahora (o 0 si es la primera vez), más 1". Es tan común que Python trae una
herramienta hecha, `Counter`, en el módulo `collections` (la veremos en el NB26).

Y como las listas, los diccionarios tienen su **comprensión**, con llaves y `clave: valor`:
"""),

code(r"""pesos_capa = {f"capa_{i}": 256 // (2 ** i) for i in range(3)}
print(pesos_capa)"""),

md(r"""(`//` es la **división entera**: divide y se queda solo con la parte entera, sin decimales. `256 // 4` da 64. Y su compañero, `%`, da el **resto**:
`7 % 2` es 1. Los dos son muy útiles; por ejemplo, `paso % 100 == 0` es `True` cada 100 pasos, el truco para mostrar un mensaje "de vez en cuando".)
"""),

md(r"""## 8 · Conjuntos: sin repetidos

Un **conjunto** (*set*) es una colección **sin orden y sin repetidos**. Se escribe con llaves, pero sin el `clave:`. Su superpoder: si metes algo dos veces,
solo queda una:
"""),

code(r"""entornos_probados = ["Hopper", "Walker2d", "Hopper", "Humanoid", "Walker2d"]
distintos = set(entornos_probados)
print(distintos)
print(len(distintos), "entornos distintos")"""),

md(r"""(El orden en que se muestran puede variar: los conjuntos **no guardan orden**.) Convertir una lista en conjunto es la forma más rápida de **quitar
repetidos**.

Y permiten las operaciones de los conjuntos de las matemáticas: **unión** (`|`, lo que está en cualquiera), **intersección** (`&`, lo que está en los dos) y
**diferencia** (`-`, lo que está en uno pero no en el otro):
"""),

code(r"""yo = {"Hopper", "Walker2d", "Humanoid"}
companero = {"Walker2d", "Ant", "Humanoid"}

print("Probados por los dos:  ", sorted(yo & companero))
print("Probados por alguno:   ", sorted(yo | companero))
print("Solo yo:               ", sorted(yo - companero))"""),

md(r"""(Usamos `sorted` para mostrarlos siempre en el mismo orden, alfabético.) Además, preguntar si algo está en un conjunto (`in`) es **rapidísimo**, mucho más que
en una lista larga, porque el conjunto no tiene que recorrer todos sus elementos para saberlo.
"""),

md(r"""## 9 · Preguntas a toda una colección: `any`, `all` y ordenar por una clave

**`any`** responde "¿**alguno** es verdadero?" y **`all`**, "¿**todos** son verdaderos?". Combinados con una comprensión, son muy expresivos:"""),

code(r"""pasos_por_episodio = [500, 500, 231, 500, 500]
print("¿Alguno se cayó?   ", any(p < 500 for p in pasos_por_episodio))
print("¿Todos completaron?", all(p == 500 for p in pasos_por_episodio))"""),

md(r"""(Fíjate: aquí la comprensión va **sin corchetes**, directamente dentro de `any`. Es una variante que no fabrica la lista entera; lo explicaremos en el NB23,
con los generadores.)

### Ordenar por lo que tú digas: `key`

`sorted`, `max` y `min` aceptan un parámetro **`key`**: una **función** que dice, para cada elemento, **por qué valor** hay que ordenar (o comparar). Por ejemplo,
para ordenar parejas (nombre, retorno) **por el retorno**:
"""),

code(r"""politicas = [("nada", 44.8), ("a mano", 499.9), ("azar", 43.2), ("solo inclinación", 296.0)]

def su_retorno(pareja):
    return pareja[1]

for nombre, retorno in sorted(politicas, key=su_retorno, reverse=True):
    print(f"{nombre:>17}: {retorno:6.1f}")

print("La mejor:", max(politicas, key=su_retorno))"""),

md(r"""`key=su_retorno` le dice a `sorted`: "para comparar dos parejas, mira lo que devuelve `su_retorno` de cada una" (fíjate: pasamos la **función** por su nombre,
sin paréntesis, como en el NB10). En el NB23 verás una forma más corta de escribir esas funciones de usar y tirar, las `lambda`.
"""),

md(r"""## 10 · Proyecto: el cuaderno de experimentos

Juntemos todo en algo muy real. Un ingeniero prueba varias políticas en el palo de escoba y apunta los resultados. Cada experimento es un **diccionario** (con nombre,
ruedecillas y retornos de 5 semillas), y todos juntos, una **lista de diccionarios** (la estructura más común del mundo para guardar datos):
"""),

code(r"""experimentos = [
    {"nombre": "nada",             "ruedecillas": (0, 0),  "retornos": [41.6, 46.2, 43.1, 45.3, 47.6]},
    {"nombre": "solo inclinación", "ruedecillas": (30, 0), "retornos": [499.7, 168.5, 144.5, 198.8, 468.3]},
    {"nombre": "a mano",           "ruedecillas": (30, 8), "retornos": [499.9, 499.9, 499.9, 499.9, 499.9]},
    {"nombre": "aprendida",        "ruedecillas": (47.9, 6.7), "retornos": [499.9, 499.9, 499.9, 499.8, 499.9]},
]

# Añadimos a cada experimento su media y si fue "robusto" (todos los episodios por encima de 400)
for exp in experimentos:
    exp["media"] = sum(exp["retornos"]) / len(exp["retornos"])
    exp["robusta"] = all(r > 400 for r in exp["retornos"])

def su_media(exp):
    return exp["media"]

print(f"{'puesto':>6} | {'política':<17} | {'ruedecillas':<12} | {'media':>6} | robusta")
print("-" * 64)
for puesto, exp in enumerate(sorted(experimentos, key=su_media, reverse=True), start=1):
    k, d = exp["ruedecillas"]
    marca = "sí" if exp["robusta"] else "no"
    print(f"{puesto:>6} | {exp['nombre']:<17} | ({k:>4}, {d:>3}) | {exp['media']:>6.1f} | {marca}")

robustas = [exp["nombre"] for exp in experimentos if exp["robusta"]]
print("\nPolíticas robustas:", ", ".join(robustas))"""),

md(r"""Un pequeño "cuaderno de experimentos", con todo lo de hoy: diccionarios con una tupla y una lista dentro, añadir claves, `all` con una comprensión, ordenar con
`key`, `enumerate` (con `start=1`, para que los puestos empiecen en 1 y no en 0), desempaquetar una tupla, f-strings con alineación, una comprensión con filtro y un
`join`. (Fíjate en un detalle de las f-strings: dentro de una f-string con comillas dobles, las claves del diccionario van con comillas **simples**,
`exp['nombre']`, para no cerrar la cadena antes de tiempo.)

Así es como se organizan los resultados en un proyecto de verdad, antes de guardarlos en un fichero (NB26) o dibujarlos.
"""),

md(r"""## 11 · ¿Qué colección uso?

| Colección | Se escribe | ¿Ordenada? | ¿Se puede cambiar? | ¿Repetidos? | Úsala para... |
|---|---|---|---|---|---|
| **Lista** | `[1, 2, 3]` | sí | sí | sí | secuencias que crecen: trayectorias, historiales |
| **Tupla** | `(1, 2, 3)` | sí | **no** | sí | datos fijos que van juntos: posiciones, formas, retornos de funciones |
| **Diccionario** | `{"a": 1}` | sí (orden de inserción) | sí | claves no | datos con nombre: configuraciones, fichas, resultados |
| **Conjunto** | `{1, 2, 3}` | **no** | sí | **no** | quitar repetidos, comprobar pertenencia rápido, comparar grupos |

Y recuerda la trampa: las colecciones que **se pueden cambiar** (listas, diccionarios, conjuntos) **sufren alias**. Si necesitas una copia independiente, `copy()`.
"""),

md(r"""## 12 · Resumen de la lección

1. **Tuplas** `( )`: como listas, pero **inmutables**. Se **desempaquetan** (`x, y, z = posicion`); el `return a, b` devuelve una tupla; `a, b = b, a` intercambia.
2. **Listas a fondo**: `insert`, `pop`, `remove`, `index`, `extend`, `del`; **`sort` cambia y no devuelve, `sorted` devuelve y no cambia**; porciones con salto
   (`[::2]`, `[::-1]`).
3. **La trampa del alias**: `b = a` no copia, pega otra etiqueta a la **misma** lista. Copia de verdad: `a.copy()`. `is` pregunta "¿el mismo objeto?".
4. **`enumerate`** (posición y elemento), **`zip`** (dos listas a la vez) y **comprensiones** (`[f(x) for x in lista if condición]`).
5. **Diccionarios** `{clave: valor}`: acceso por clave (`KeyError` si no está; mejor `get`), añadir/cambiar/borrar, `.items()`, anidados (configuraciones), contar.
   El `info` de Gymnasium es un diccionario con los ingredientes de la recompensa. **Conjuntos**: sin repetidos, `|`, `&`, `-`. **`any`/`all`** y ordenar con
   **`key`**.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Tupla** | Colección ordenada e inmutable: `(1, 2, 3)`. |
| **Desempaquetar** | Repartir los elementos de una tupla o lista en varias cajas: `a, b = (1, 2)`. |
| **Alias** | Dos nombres que apuntan al mismo objeto. |
| **Copia superficial / profunda** | `copy()` copia el primer nivel / `copy.deepcopy` copia todo. |
| **`is`** | ¿Son el mismo objeto (no solo iguales)? |
| **`enumerate` / `zip`** | Recorrer con la posición / recorrer dos colecciones a la vez. |
| **Comprensión** | Forma corta de crear una lista o diccionario: `[x**2 for x in lista]`. |
| **Diccionario** | Colección de parejas clave → valor: `{"motores": 17}`. |
| **Clave** | El "nombre" con el que se guarda y se busca un valor en un diccionario. |
| **`KeyError`** | Error por pedir una clave que no existe. |
| **Conjunto (*set*)** | Colección sin orden y sin repetidos. |
| **`//` y `%`** | División entera y resto: `7 // 2 = 3`, `7 % 2 = 1`. |
| **`key=`** | Función que dice por qué valor ordenar o comparar. |
"""),

md(r"""## 13 · Ejercicios

**E1.** Con `forma = (17, 348)`, desempaqueta en `filas` y `columnas` y calcula cuántos números tiene la matriz.

**E2.** Predice qué muestra este código y explica por qué:

```python
a = [0.1, 0.2]
b = a
b[0] = 99
print(a)
```

¿Cómo lo arreglarías para que `a` no cambie?

**E3.** Con una comprensión, a partir de `acciones = [0.5, -0.7, 0.1, 0.45, -0.2]`, fabrica la lista de acciones **recortadas** a ±0,4 (pista: `max(-0.4, min(0.4, a))`, NB18).

**E4.** Usa `zip` para calcular el producto escalar (NB13) de `[1, 2, 3]` y `[4, 5, 6]` en una línea, con `sum` y una comprensión.

**E5.** Crea un diccionario `motores` con la fuerza de los motores del humanoide: cadera 300, rodilla 200, hombro 25, codo 25. Recórrelo y muestra los que tengan fuerza
mayor que 100.

**E6.** A partir de `finales = ["caída", "tiempo", "caída", "atasco", "caída"]`, cuenta cuántas veces aparece cada final usando un diccionario.

**E7.** ¿Cuántos números distintos hay en `[3, 1, 3, 2, 1, 3, 2]`? Resuélvelo con un conjunto.

**E8.** Ordena `["Walker2d", "ant", "Hopper", "humanoid"]` alfabéticamente **sin que importen las mayúsculas**. (Pista: `key=str.lower`, pasando el método `lower` de las
cadenas como función.)

**E9.** **Reto.** En el proyecto, añade a cada experimento la clave `"peor"` (su peor retorno) y muestra solo los experimentos cuyo peor retorno sea mayor que 150.
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
forma = (17, 348)
filas, columnas = forma
print(filas * columnas)
```

Salida: **5916** números (sin contar los 17 sesgos, que harían 5.933, NB14).
</details>

<details>
<summary>▶ Solución E2</summary>

Muestra **`[99, 0.2]`**: `b = a` no copia, solo crea un **alias**; `a` y `b` son la misma lista, así que cambiar `b[0]` cambia lo que se ve desde `a`. Se arregla haciendo
una copia: `b = a.copy()` (o `b = list(a)`, o `b = a[:]`). Entonces `a` seguiría siendo `[0.1, 0.2]`.
</details>

<details>
<summary>▶ Solución E3</summary>

```python
acciones = [0.5, -0.7, 0.1, 0.45, -0.2]
recortadas = [max(-0.4, min(0.4, a)) for a in acciones]
print(recortadas)
```

Salida: `[0.4, -0.4, 0.1, 0.4, -0.2]`.
</details>

<details>
<summary>▶ Solución E4</summary>

```python
print(sum(a * b for a, b in zip([1, 2, 3], [4, 5, 6])))
```

Salida: **32** (como en el NB13). `zip` empareja (1, 4), (2, 5), (3, 6); se multiplica cada pareja y se suma todo.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
motores = {"cadera": 300, "rodilla": 200, "hombro": 25, "codo": 25}
for nombre, fuerza in motores.items():
    if fuerza > 100:
        print(nombre, fuerza)
```

Salen **cadera 300** y **rodilla 200**: las piernas, como vimos en el NB01.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
finales = ["caída", "tiempo", "caída", "atasco", "caída"]
conteo = {}
for f in finales:
    conteo[f] = conteo.get(f, 0) + 1
print(conteo)
```

Salida: `{'caída': 3, 'tiempo': 1, 'atasco': 1}`.
</details>

<details>
<summary>▶ Solución E7</summary>

```python
print(len(set([3, 1, 3, 2, 1, 3, 2])))
```

Salida: **3** (los números distintos son 1, 2 y 3).
</details>

<details>
<summary>▶ Solución E8</summary>

```python
print(sorted(["Walker2d", "ant", "Hopper", "humanoid"], key=str.lower))
```

Salida: `['ant', 'Hopper', 'humanoid', 'Walker2d']`. Sin el `key`, las mayúsculas irían primero (NB20) y saldría `['Hopper', 'Walker2d', 'ant', 'humanoid']`.
`str.lower` es el método `lower` de las cadenas usado como función: para cada nombre, `sorted` compara su versión en minúsculas.
</details>

<details>
<summary>▶ Solución E9</summary>

```python
for exp in experimentos:
    exp["peor"] = min(exp["retornos"])

for exp in experimentos:
    if exp["peor"] > 150:
        print(exp["nombre"], exp["peor"])
```

Salen **a mano** (499,9) y **aprendida** (499,8). La de "solo inclinación" tiene un peor retorno de 144,5, y "nada", de 41,6. Mirar el **peor caso**, y no solo la media,
es una costumbre muy profesional: en un robot real, un solo episodio malo puede significar una caída.
</details>
"""),

md(r"""## 14 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Ya sabes elegir y manejar la colección adecuada para cada cosa, y conoces la trampa del alias, que te ahorrará muchas horas de buscar errores. En el **NB22** vamos con el
**control del flujo** y los **errores**: el bucle `while`, `continue`, las **excepciones** (cómo provocar, capturar y manejar errores para que un entrenamiento de horas no se
caiga por un fallo tonto) y, sobre todo, cómo **depurar**: el arte de encontrar por qué un programa no hace lo que esperas.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB21_python_colecciones.ipynb")
    build(out, cells, title="NB21 · Python de verdad (2): colecciones")
