"""Construye NB48 · Contactos a fondo (Parte 6 · Bloque A · Lección 4).

Detección: pares de geoms, fase amplia/estrecha, exclusión madre-hija,
contype/conaffinity (regla de bits), la estructura contact (pos, frame, dist).
Python (repaso del P3/P4): generadores (yield, perezosos, protocolo iterador),
NamedTuple, itertools/collections. Contactos blandos: por qué (LCP frente a
optimización convexa), solref (timeconst, dampratio), penetración que no
depende de la masa, impacto; solimp. Rebote: dampratio y solref negativo.
Rozamiento: Coulomb, plano inclinado (umbral arctan μ), deslizamiento lento
(creep) y cómo quitarlo (cono elíptico + impratio + noslip), condim 1/3/4/6.
Solucionadores PGS/CG/Newton. Fuerzas: mj_contactForce (marco del contacto,
signo), fuerza total = peso, cfrc_ext. Centro de presiones (ZMP medido),
empujones crecientes: x_cdp = x_cdm + F·h/W, vuelco entre 15 y 16 N.
Contactos y sim-to-real.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB48 · Contactos a fondo

**Parte 6 · Simulación de bípedos a fondo — Bloque A: MuJoCo por dentro — Lección 4**

> Un bípedo **solo** puede moverse empujando el suelo (NB47: su torso no tiene motor). Todo lo que hace (sostenerse, andar, frenar, girar) pasa por unos pocos puntos de contacto bajo sus pies. Si la simulación de esos contactos no se parece a la realidad, nada de lo que aprenda en el simulador servirá en el robot de verdad.

Los contactos son, con diferencia, **la parte más difícil** de un motor de física, y la que más diferencia a unos simuladores de otros. También son una de las fuentes principales del **reality gap** (NB02). En una entrevista de simulación, te pueden caer preguntas como:

- "¿Cómo modela MuJoCo los contactos? ¿Por qué permite que los cuerpos se atraviesen un poquito?"
- "¿Qué son `solref` y `solimp`?"
- "¿Qué diferencia hay entre el cono de rozamiento piramidal y el elíptico?"
- "¿Cómo medirías la fuerza de reacción del suelo y el centro de presiones de un robot?"
- "Tu robot simulado resbala despacio en una rampa en la que no debería. ¿Qué tocas?"

Hoy contestaremos a todas con experimentos. Y en el hilo de Python, un **repaso en acción** de lo que estudiaste en el P3 y el P4: **generadores** (la forma de recorrer cosas "a demanda"), `NamedTuple` y los módulos `itertools` y `collections`, ahora aplicados a los contactos.
"""),

code(r"""import os
os.environ["MUJOCO_GL"] = "egl"

import mujoco
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(precision=4, suppress=True, linewidth=120)

zancudo = mujoco.MjModel.from_xml_path("robots/zancudo.xml")
datos = mujoco.MjData(zancudo)
for paso in range(500):                      # 1 segundo de pie, quieto (ctrl = 0)
    mujoco.mj_step(zancudo, datos)
print("contactos activos:", datos.ncon)"""),

md(r"""## 1 · ¿Quién toca a quién? La detección

### Dos fases

En cada paso, lo primero que hace MuJoCo con los contactos es **detectarlos**: averiguar qué pares de geometrías se tocan y dónde. Con N geometrías hay N·(N−1)/2 parejas posibles (con 100 geometrías, ¡casi 5.000!), y comprobar cada una con todo detalle sería lentísimo. Por eso se hace en dos fases:

1. **Fase amplia** (*broad phase*): se envuelve cada geometría en una caja sencilla (alineada con los ejes) y se descartan rápidamente las parejas cuyas cajas ni se rozan. Es muy barato y elimina casi todas.
2. **Fase estrecha** (*narrow phase*): para las pocas parejas que quedan, se calcula con precisión la distancia, el punto de contacto y la dirección, con una fórmula específica para cada combinación de formas (esfera-plano, cápsula-caja...). Las mallas (NB50) son lo más caro.

### Qué parejas se comprueban

No todas las parejas se pueden tocar. MuJoCo descarta:

- **Las de un mismo cuerpo**, y las de un cuerpo con su **madre** (el muslo y la pierna se tocan en la rodilla todo el rato: si eso contara como contacto, el robot no podría moverse). Por eso los contactos entre un cuerpo y su "abuela" **sí** se comprueban, y a veces sorprenden.
- **Las que se excluyen a mano**, con `<exclude body1="..." body2="..."/>` en el MJCF.
- **Las que no pasan el filtro de bits** de `contype` y `conaffinity`, que es lo siguiente.

### contype y conaffinity

Cada geometría tiene dos números enteros, `contype` ("tipo de contacto") y `conaffinity` ("afinidad"), que por defecto valen 1. Dos geometrías A y B pueden chocar si:

```
   (contype de A  &  conaffinity de B)  ≠  0      O      (contype de B  &  conaffinity de A)  ≠  0
```

donde `&` es la **y de bits** del NB45. La idea: cada bit es un "canal"; `contype` dice en qué canales **emite** una geometría y `conaffinity` en cuáles **escucha**. Chocan si alguna escucha a la otra. Comprobémoslo con una bola sobre el suelo:
"""),

code(r"""def chocan(tipo_suelo: int, afinidad_suelo: int, tipo_bola: int, afinidad_bola: int) -> bool:
    xml = f'''
    <mujoco><worldbody>
      <geom type="plane" size="1 1 .1" contype="{tipo_suelo}" conaffinity="{afinidad_suelo}"/>
      <body pos="0 0 .05"><freejoint/>
        <geom type="sphere" size=".1" contype="{tipo_bola}" conaffinity="{afinidad_bola}"/>
      </body>
    </worldbody></mujoco>'''
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)                  # la detección es parte de la etapa de posición (NB45)
    return d.ncon > 0

for caso in [(1, 1, 1, 1), (1, 1, 0, 0), (1, 0, 1, 0), (2, 1, 1, 2), (2, 2, 1, 1)]:
    print(caso, "→", "chocan" if chocan(*caso) else "no chocan")"""),

md(r"""- **(1, 1, 1, 1)**, los valores por defecto: todo choca con todo.
- **(1, 1, 0, 0)**: la bola ni emite ni escucha: es un **fantasma** que atraviesa todo. Es lo que usamos en el NB47 para el soporte y el marcador verde (`contype="0" conaffinity="0"`): geometrías solo para **ver**.
- **(1, 0, 1, 0)**: los dos emiten, pero **ninguno escucha**: no chocan.
- **(2, 1, 1, 2)**: el suelo emite en el canal 2 (bit 1) y la bola escucha en el 2: chocan.
- **(2, 2, 1, 1)**: el suelo solo usa el canal 2 y la bola solo el 1: no se ven.

`chocan(*caso)` "desempaqueta" la tupla en los cuatro argumentos (NB23).

¿Para qué sirve en un robot? Por ejemplo, para que las dos piernas de un humanoide **no choquen entre sí** (simplifica y acelera la simulación, aunque sea menos realista), pero las dos choquen con el suelo: piernas con `contype=1 conaffinity=2`... y el suelo con `conaffinity=1 contype=2`. O para tener geometrías **visuales** detalladas (mallas bonitas, sin choques) y otras de **colisión** sencillas (cápsulas, cajas), que es lo que hacen todos los modelos profesionales (NB50, NB58).
"""),

md(r"""### La lista de contactos

Los contactos detectados están en `datos.contact`, una lista de `datos.ncon` elementos. Zancudo, de pie, tiene **4**. Miremos uno:
"""),

code(r"""c = datos.contact[0]
print("geometrías:  ", zancudo.geom(c.geom1).name, "y", zancudo.geom(c.geom2).name)
print("posición:    ", c.pos)
print("distancia:   ", c.dist)
print("dimensión:   ", c.dim)
print("marco (filas):\n", c.frame.reshape(3, 3))"""),

md(r"""- **`geom1`, `geom2`**: las dos geometrías (aquí, el suelo y el pie derecho).
- **`pos`**: el punto de contacto, en el mundo: (−0,06, −0,1, 0), el **talón** del pie derecho (el pie va de −0,06 a +0,14 en x, NB42).
- **`dist`**: la distancia entre las dos geometrías. **Negativa**: están **atravesadas** unos 0,6 mm. Lo explicaremos en la sección 3: es a propósito.
- **`dim`**: la dimensión del contacto, 3 (sección 5).
- **`frame`**: el **marco del contacto**, una matriz de rotación (NB46) guardada por **filas**. La primera fila es la **normal** (la dirección perpendicular a la superficie, que aquí es (0, 0, 1): hacia arriba), y las otras dos son las direcciones **tangentes** (a lo largo de la superficie), por donde actúa el rozamiento.

Las 4 posiciones son el talón y la punta de cada pie: una cápsula sobre un plano da **un** punto de contacto por cada extremo que toca. (Una caja sobre un plano daría hasta 4, uno por esquina.)
"""),

md(r"""## 2 · Python: generadores (repaso del P4)

### Recorrer contactos con comodidad

Para trabajar con los contactos vamos a escribir a menudo "recorre los contactos, quédate con los que te interesan, y saca unos datos de cada uno". Podríamos hacer una función que devuelva una **lista**. Pero hay una herramienta de Python mejor para esto, que estudiaste a fondo en el P4: un **generador**. Repasémosla con un caso real.
"""),

code(r"""from typing import NamedTuple, Iterator

class Contacto(NamedTuple):
    geometria_1: str
    geometria_2: str
    posicion: np.ndarray
    distancia: float


def contactos(modelo: mujoco.MjModel, datos: mujoco.MjData) -> Iterator[Contacto]:
    for i in range(datos.ncon):
        c = datos.contact[i]
        yield Contacto(modelo.geom(c.geom1).name, modelo.geom(c.geom2).name, c.pos.copy(), float(c.dist))


for contacto in contactos(zancudo, datos):
    print(contacto)"""),

md(r"""Dos cosas que ya conoces (del P3 y del P4), ahora en acción.

**`NamedTuple`** (del módulo `typing`, P3): recuerda, una **tupla con nombres**. Se define como una dataclass (campos con anotaciones), pero es una tupla de verdad: **inmutable**, ligera, y se puede usar por posición (`contacto[2]`) **o** por nombre (`contacto.posicion`), y desempaquetar (`g1, g2, pos, dist = contacto`). Es perfecta para "registros" pequeños que no van a cambiar. ¿Dataclass o NamedTuple? Dataclass si necesitas métodos, valores por defecto mutables o que sea modificable; NamedTuple para datos sencillos e inmutables que quieres poder desempaquetar.

**`yield`** (P4): la palabra clave de los **generadores**. Repaso rápido: una función con `yield` dentro no es una función normal; al llamarla, **no se ejecuta**. Devuelve un objeto **generador**, que irá ejecutando el cuerpo de la función **a trozos**, cada vez que le pidan el siguiente elemento: corre hasta el `yield`, **entrega** ese valor, y se **queda congelada** ahí, con todas sus variables, hasta que le pidan el siguiente. Mira:
"""),

code(r"""generador = contactos(zancudo, datos)
print(generador)
print(next(generador).posicion)        # ejecuta hasta el primer yield
print(next(generador).posicion)        # sigue desde ahí hasta el segundo"""),

md(r"""`next(generador)` pide **el siguiente** elemento. Cuando ya no quedan, `next` lanza una excepción especial, `StopIteration`, que es la forma en que un generador dice "se acabó". El bucle `for` hace exactamente eso por dentro: llama a `next` una y otra vez hasta que recibe `StopIteration`.

### ¿Por qué generadores y no listas? (recordatorio del P4)

1. **Pereza** (*lazy evaluation*): un generador no calcula nada hasta que se lo piden. Si solo te interesa el **primer** contacto del pie izquierdo, el generador se detiene ahí, sin procesar los demás.
2. **Memoria**: una lista guarda **todos** los elementos a la vez; un generador, **uno** cada vez. Para recorrer las 10 millones de líneas de un fichero de registro de un entrenamiento, la diferencia es entre que quepa en memoria o no.
3. **Pueden ser infinitos**: un generador que produce números al azar, o que lee un sensor, puede no acabar nunca, y el que lo usa decide cuándo parar.
4. **Encadenarse**: se pueden pasar de uno a otro, como una cadena de montaje, sin crear listas intermedias.

Y la trampa que ya conoces del P4: **un generador se gasta**. Una vez recorrido, está vacío:
"""),

code(r"""generador = contactos(zancudo, datos)
print(len(list(generador)), "contactos la primera vez")
print(len(list(generador)), "contactos la segunda vez")"""),

md(r"""La segunda vez, **cero**. Si necesitas recorrerlo varias veces, conviértelo en lista (`list(...)`) o crea otro generador llamando otra vez a la función.

### Expresiones generadoras

Igual que hay **listas por comprensión** (NB21), `[x * 2 for x in datos]`, hay **expresiones generadoras** (P4), con paréntesis en vez de corchetes: `(x * 2 for x in datos)`. Son generadores escritos en una línea. Ya usamos una en el NB47, dentro de `sum(...)`. Por ejemplo, la penetración máxima:
"""),

code(r"""print("penetración máxima:", max(-c.distancia for c in contactos(zancudo, datos)) * 1000, "mm")"""),

md(r"""(Cuando la expresión generadora es el único argumento de una función, como aquí, se pueden omitir sus propios paréntesis: `max(... for ...)`.)

### El protocolo iterador

Como viste en el P4, lo que hace que algo se pueda recorrer con `for` es un **protocolo** (como los del P5 y el NB47): tener un método `__iter__` que devuelva un **iterador**, que es un objeto con un método `__next__`. Las listas, las tuplas, los diccionarios, los ficheros, los `range`... todos lo cumplen. Y los generadores son la forma más fácil de **fabricar** iteradores: Python les pone esos dos métodos automáticamente.

### itertools y collections

Los dos módulos de la biblioteca estándar que exploraste en el P4. Unas pocas de sus herramientas, aplicadas a los contactos:
"""),

code(r"""from collections import Counter
from itertools import islice, groupby

# ¿Cuántos contactos tiene cada geometría del robot?
print(Counter(c.geometria_2 for c in contactos(zancudo, datos)))

# Solo los dos primeros (sin generar los demás)
for c in islice(contactos(zancudo, datos), 2):
    print("primeros:", c.geometria_2, c.posicion)

# Agrupar por pie (groupby agrupa elementos SEGUIDOS con la misma clave)
for pie, grupo in groupby(contactos(zancudo, datos), key=lambda c: c.geometria_2):
    print(pie, "→", [round(float(c.posicion[0]), 2) for c in grupo])"""),

md(r"""- **`Counter`** cuenta cuántas veces aparece cada cosa: dos contactos por pie.
- **`islice(iterable, n)`** es como `lista[:n]`, pero para cualquier iterable, y **sin** generar lo que sobra.
- **`groupby(iterable, key=...)`** agrupa los elementos **seguidos** que tienen la misma clave. ¡Ojo!, solo los seguidos: si los datos no vienen ordenados por la clave, hay que ordenarlos antes (`sorted(..., key=...)`). Aquí funciona porque MuJoCo da los contactos de cada pie juntos.

Otros de `itertools` que ya viste en el P4 y que encontrarás en código profesional: `chain` (pegar varios iterables uno detrás de otro), `product` (todas las combinaciones, como bucles anidados: lo usaremos para barridos de parámetros en el NB55), `pairwise` (pares seguidos: (a, b), (b, c)...), `accumulate` (sumas acumuladas).
"""),

md(r"""## 3 · Contactos blandos: por qué se atraviesan

### El problema de los contactos "duros"

En el mundo real, dos sólidos **no se atraviesan**. Y el rozamiento es "todo o nada": un objeto o está quieto o desliza. Estas condiciones son muy difíciles para un ordenador. Matemáticamente son **condiciones de complementariedad**: "o hay distancia y no hay fuerza, o no hay distancia y hay fuerza, pero nunca las dos". Los simuladores clásicos las resuelven como un **problema de complementariedad lineal** (*LCP*). El problema es que:

- son **discontinuas**: la fuerza salta de golpe de 0 a mucho en el instante del contacto;
- no siempre tienen solución, o tienen varias, y los métodos para resolverlas pueden fallar;
- pequeñas diferencias (un milímetro, un decimal) cambian mucho el resultado.

### La solución de MuJoCo

MuJoCo hace algo distinto, y es una de las claves de su éxito en robótica: plantea los contactos como un problema de **optimización convexa** (un problema con un único "fondo de valle", como el de los valles del NB17 pero sin valles falsos: siempre tiene solución y se encuentra de forma fiable), y a cambio **permite** que los cuerpos se atraviesen un poquito. Los contactos son "**blandos**": se comportan como un **muelle con amortiguador** (NB39b) muy rígido, que empuja con más fuerza cuanto más se atraviesan.

Eso explica los 0,6 mm de penetración de los pies de Zancudo. No es un error: es el **diseño**. Y tiene ventajas enormes: la simulación es **estable**, **suave** (las fuerzas varían de forma continua, lo que ayuda al RL y a los métodos que usan derivadas, NB59) y **rápida**.

### solref: el muelle del contacto

¿Cómo de rígido es ese muelle? Lo decide el parámetro **`solref`** (*solver reference*), con dos números: `solref="timeconst dampratio"`, por defecto `"0.02 1"`.

- **`timeconst`** (constante de tiempo): **lo rápido** que el contacto corrige una penetración, en segundos. Con 0,02, en unas pocas centésimas de segundo. Más pequeño = contacto más **duro**.
- **`dampratio`** (razón de amortiguamiento): es la **ζ** del muelle con amortiguador que estudiaste en el NB39b (y que usamos en el NB47). Con 1, amortiguamiento crítico: corrige **sin rebotar**; por debajo de 1, oscila (rebota).

Hagamos un experimento: dejamos caer una caja de 10 kg desde 30 cm (su centro; la caja mide 20 cm, así que su base cae 20 cm) y medimos dos cosas: cuánto se hunde **en el impacto** (lo máximo) y cuánto queda hundida **en reposo**:
"""),

code(r"""def dejar_caer(solref: str = "0.02 1", masa: float = 10.0, segundos: float = 3.0) -> tuple[float, float]:
    xml = f'''
    <mujoco><option timestep="0.002"/><worldbody>
      <geom type="plane" size="2 2 .1"/>
      <body pos="0 0 0.3"><freejoint/>
        <geom type="box" size=".1 .1 .1" mass="{masa}" solref="{solref}"/>
      </body>
    </worldbody></mujoco>'''
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    alturas = []
    while d.time < segundos:
        mujoco.mj_step(m, d)
        alturas.append(d.qpos[2])
    alturas = np.array(alturas)
    return 1000 * (0.1 - alturas.min()), 1000 * (0.1 - alturas[-1])    # en mm

print(f"{'solref':>12} | hundimiento en el impacto | en reposo")
for solref in ["0.005 1", "0.02 1", "0.1 1"]:
    impacto, reposo = dejar_caer(solref)
    print(f"{solref:>12} | {impacto:12.1f} mm            | {reposo:.3f} mm")"""),

md(r"""- Con el contacto **duro** (`timeconst` = 0,005), la caja se hunde 7,7 mm en el impacto y queda a 0,04 mm.
- Con el de **por defecto** (0,02), 13 mm en el impacto y 0,108 mm en reposo.
- Con uno **blando** (0,1), ¡41 mm en el impacto (como un colchón) y 0,6 mm en reposo!

En el impacto se hunde mucho más que en reposo: llega con velocidad, y el "muelle" tarda en frenarla. En reposo, una fracción de milímetro: imperceptible a la vista, pero ahí está, y es la que vimos en los pies de Zancudo.

¿Por qué no usar siempre un contacto muy duro? Porque cuanto más duro, más **rápidos** son los cambios de fuerza, y más pequeño tiene que ser el pasito de tiempo para seguirlos sin que la simulación se vuelva inestable. La documentación de MuJoCo recomienda que `timeconst` sea **al menos el doble del pasito** (aquí, 0,004 s). El valor por defecto, 0,02, es un buen compromiso para robots.
"""),

md(r"""### Una sorpresa: la masa no importa

Ahora, la pregunta de entrevista con trampa: **¿una caja más pesada se hunde más?** Con un muelle de verdad, sí (el doble de peso, el doble de hundimiento). Probémoslo:
"""),

code(r"""for masa in [1, 10, 100]:
    impacto, reposo = dejar_caer(masa=masa)
    print(f"masa {masa:>3} kg  →  en reposo, hundida {reposo:.4f} mm")"""),

md(r"""**Exactamente lo mismo**: 0,1078 mm con 1, 10 o 100 kg. En MuJoCo, `solref` no define un muelle con una rigidez fija (N/m), sino un comportamiento: "corrige la penetración con **esta** rapidez". Y para conseguirlo, MuJoCo ajusta la rigidez a la **masa** que hay en juego en cada contacto (la "masa efectiva", que sale de la matriz M del NB45). Un contacto que sostiene 100 kg es automáticamente 100 veces más rígido.

Ventaja: puedes poner los mismos parámetros de contacto a un robot de 2 kg y a uno de 200, y los dos se comportan "igual de bien". Inconveniente: es **menos físico**. Un suelo de verdad tiene **una** rigidez, y un robot más pesado se hunde más. Si quieres eso, MuJoCo permite dar `solref` con números **negativos**: entonces se interpretan como rigidez y amortiguamiento **de verdad**, en N/m y N·s/m. Lo usaremos ahora mismo para hacer rebotar una pelota.

### solimp, en una frase

Hay un segundo parámetro, **`solimp`** (*solver impedance*), con 5 números (por defecto `"0.9 0.95 0.001 0.5 2"`), que decide **cuánto "cede"** el contacto según lo atravesado que esté: con poca penetración, el contacto es algo más blando (0,9); a partir de 0,001 m, más duro (0,95). Es un ajuste fino que rara vez hay que tocar; si alguna vez ves que tu robot "flota" o "se hunde" demasiado, `solimp` y `solref` son los primeros sospechosos. La documentación de MuJoCo tiene una gráfica de la curva; para la entrevista basta con saber **qué es** y que, junto con `solref`, define la blandura del contacto.
"""),

md(r"""## 4 · Rebotar

Con `dampratio = 1`, el contacto no rebota nada (NB45: la caja que perdía toda su energía al chocar). Para un pie, es lo que queremos. Pero, ¿y si queremos simular una pelota? Bajando el amortiguamiento, o dando la rigidez y el amortiguamiento directamente con `solref` negativo:
"""),

code(r"""def rebote(solref: str) -> float:
    xml = f'''
    <mujoco><option timestep="0.001"/><worldbody>
      <geom type="plane" size="2 2 .1"/>
      <body pos="0 0 1"><freejoint/>
        <geom type="sphere" size=".05" mass="0.1" solref="{solref}"/>
      </body>
    </worldbody></mujoco>'''
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    alturas = []
    while d.time < 3.0:
        mujoco.mj_step(m, d)
        alturas.append(d.qpos[2])
    alturas = np.array(alturas)
    primer_choque = np.argmin(alturas[:800])           # el punto más bajo de la primera caída
    return alturas[primer_choque:].max()                # lo más alto que sube después

for solref in ["0.02 1", "0.02 0.1", "0.02 0.01", "-10000 0", "-10000 -2", "-10000 -10"]:
    print(f"solref = {solref:>11}  →  rebota hasta {rebote(solref):.3f} m  (soltada desde 1 m)")"""),

md(r"""- **`"0.02 1"`** (por defecto): **no rebota**. La "altura máxima" de 0,050 m es la pelota en reposo sobre el suelo (su radio es 5 cm).
- Bajando el **amortiguamiento** a 0,1 o 0,01: rebota un poco (hasta 10-11 cm). Con `timeconst` positivo, MuJoCo no deja que rebote mucho.
- Con **`solref` negativo**, el primer número es la **rigidez** (−10.000 N/m) y el segundo el **amortiguamiento** (en N·s/m, con signo menos). Sin amortiguamiento, la pelota **rebota hasta donde la soltamos** (1,001 m: el milímetro de más es el error del integrador, NB45); con un poco, pierde parte de su energía en cada bote (0,94 m, 0,75 m).

Para un **robot**, no queremos que los pies reboten: el valor por defecto es el bueno. El rebote importa si simulas pelotas, juguetes o caídas.
"""),

md(r"""## 5 · Rozamiento

### La ley de Coulomb y el cono

El rozamiento "normal" (el de deslizar) sigue la ley de **Coulomb**: la fuerza de rozamiento puede valer, como mucho, **μ veces** la fuerza normal (la que aprieta las dos superficies). μ es el **coeficiente de rozamiento**: unos 0,3 para madera sobre madera, 0,8 para goma sobre asfalto seco, 0,05 para hielo... Mientras la fuerza que intenta mover el objeto sea menor que μ·N, no se mueve; si la supera, desliza.

Si dibujas todas las fuerzas de contacto **permitidas** (una normal N y un rozamiento de hasta μ·N en cualquier dirección del suelo), forman un **cono** con la punta en el contacto: el **cono de rozamiento**. Cuanto mayor μ, más abierto. Una fuerza fuera del cono significa que el pie **resbala**.

### El plano inclinado

El experimento clásico: una caja sobre una rampa. La gravedad tira de ella a lo largo de la rampa con m·g·sen(θ) y la aprieta contra ella con m·g·cos(θ). Desliza cuando sen(θ) > μ·cos(θ), es decir, cuando **tan(θ) > μ**: el ángulo crítico es **arctan(μ)**, ¡sin importar la masa! Comprobémoslo en MuJoCo, inclinando el suelo (con `euler`, NB46) y midiendo cuánto avanza la caja entre los segundos 2 y 4:
"""),

code(r"""def rampa(angulo_grados: float, mu: float, cono: str = "pyramidal", impratio: float = 1.0,
          noslip: int = 0) -> float:
    a = np.radians(angulo_grados)
    xml = f'''
    <mujoco>
      <compiler angle="radian"/>
      <option timestep="0.002" cone="{cono}" impratio="{impratio}" noslip_iterations="{noslip}"/>
      <worldbody>
        <geom type="plane" size="3 3 .1" euler="0 {-a} 0" friction="{mu} 0.005 0.0001"/>
        <body pos="0 0 0.2" euler="0 {-a} 0"><freejoint/>
          <geom type="box" size=".1 .1 .1" mass="1" friction="{mu} 0.005 0.0001"/>
        </body>
      </worldbody>
    </mujoco>'''
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    while d.time < 2.0 - 1e-9:
        mujoco.mj_step(m, d)
    antes = d.qpos[:3].copy()
    while d.time < 4.0 - 1e-9:
        mujoco.mj_step(m, d)
    return 1000 * np.linalg.norm(d.qpos[:3] - antes) / 2.0          # velocidad media, en mm/s

for mu in [0.3, 0.5]:
    print(f"μ = {mu}: ángulo crítico arctan(μ) = {np.degrees(np.arctan(mu)):.1f}°")
    for angulo in [10, 15, 20, 25, 27, 30]:
        print(f"    rampa de {angulo:2d}°  →  la caja avanza a {rampa(angulo, mu):8.2f} mm/s")"""),

md(r"""(El `- 1e-9` en las condiciones del bucle es por el ruido de los decimales (NB06): sumar 0,002 mil veces puede dar 1,9999999999 o 2,0000000001. Comparar tiempos con un pequeño margen es un hábito sano.)

**El umbral de arctan μ se cumple**: con μ = 0,3 la caja se queda quieta a 15° y sale disparada a 20° (el umbral es 16,7°); con μ = 0,5, quieta a 25° y deslizando a 27° (umbral 26,6°). Por encima del umbral, avanza a **metros** por segundo (acelerando por la rampa).

Pero mira los valores **por debajo** del umbral: 0,6, 1, 2,5, 5,6 mm/s. No son cero. Eso merece su propio apartado.
"""),

md(r"""### El deslizamiento lento, y cómo quitarlo

Por debajo del ángulo crítico, la caja **no debería moverse nada**. Pero se mueve: unos pocos **milímetros por segundo**. Es el **deslizamiento lento** (*creep*), una consecuencia de los contactos blandos: igual que el contacto normal permite atravesarse un poquito, el rozamiento permite deslizar un poquito.

Un milímetro por segundo parece nada, pero en un robot que está de pie un minuto son 6 cm de "patinar" sin motivo, y un pie que resbala despacio puede engañar a una política de RL (aprende a contar con algo que en la realidad no pasa). MuJoCo tiene tres herramientas para reducirlo, y vamos a medirlas en la rampa de 25° con μ = 0,5 (por debajo del ángulo crítico de 26,6°):

- **El cono elíptico** (`cone="elliptic"`). Por defecto, MuJoCo aproxima el cono de rozamiento por una **pirámide** (más rápida de calcular). El elíptico es el cono "de verdad", redondo.
- **`impratio`**: hace el rozamiento más "duro" que el contacto normal (la razón entre sus impedancias). Recomendado con el cono elíptico.
- **El solucionador `noslip`** (`noslip_iterations`): una pasada extra al final de cada paso que elimina específicamente el deslizamiento de los contactos que deberían estar "pegados".
"""),

code(r"""configuraciones = [
    dict(cono="pyramidal"),
    dict(cono="elliptic"),
    dict(cono="elliptic", impratio=10),
    dict(cono="elliptic", impratio=10, noslip=10),
]
for config in configuraciones:
    lento = rampa(25, 0.5, **config)
    rapido = rampa(27, 0.5, **config)
    print(f"{str(config):<55}  25°: {lento:7.3f} mm/s   27°: {rapido:6.1f} mm/s")"""),

md(r"""Cada herramienta reduce el deslizamiento lento en la rampa de 25°:

- **Pirámide** (por defecto): 5,6 mm/s.
- **Cono elíptico**: 1,5 mm/s (casi 4 veces menos).
- **+ `impratio = 10`**: 0,15 mm/s (10 veces menos todavía).
- **+ `noslip`**: 0,001 mm/s. **Prácticamente cero.**

Y, muy importante, en la rampa de **27°** (por encima del umbral) la caja sigue deslizando a unos 323 mm/s con todas las configuraciones: las herramientas quitan el deslizamiento **falso** sin quitar el **verdadero**.

¿Por qué no se usan siempre? Porque cuestan: el cono elíptico es algo más caro de resolver, y el `noslip` añade una pasada más en cada paso. Para robots con patas, la práctica habitual es **elíptico + `impratio` alto**; el `noslip` se añade cuando la precisión del agarre importa mucho (manipulación). Es exactamente la configuración que verás en los modelos de MuJoCo Playground (NB60).
"""),

md(r"""### condim: cuántas direcciones tiene el contacto

El número `dim` que vimos en la sección 1 se elige con el atributo **`condim`** de las geometrías:

| `condim` | Qué incluye | Para qué |
|---|---|---|
| 1 | solo la normal: **sin rozamiento** | hielo perfecto; cosas que deben deslizar libremente |
| 3 | normal + rozamiento al **deslizar** (en 2 direcciones) | **lo normal**, el valor por defecto |
| 4 | + rozamiento al **girar** sobre sí mismo (torsional) | pies que no deben pivotar sobre un punto; dedos que agarran |
| 6 | + rozamiento al **rodar** | pelotas, ruedas |

Por eso el atributo `friction` tiene **tres** números (`"1 0.005 0.0001"` en Zancudo, NB42): rozamiento al deslizar, al girar y al rodar. Los dos últimos solo se usan con `condim` 4 o 6. Cuando dos geometrías se tocan, MuJoCo usa, por defecto, el **mayor** de los dos `condim` y el **mayor** de cada rozamiento.

Con un pie de verdad (una suela plana con varios puntos de contacto) el rozamiento torsional "aparece solo", porque los distintos puntos resisten el giro. Pero los pies de **un solo punto** (una esfera, típica en cuadrúpedos) pueden girar sobre sí mismos sin resistencia con `condim="3"`: ahí se usa `condim="4"` o `"6"`.

Una comprobación rápida: con `condim="1"` (sin rozamiento), la caja resbala incluso en una rampa de 5°. La E5 de los ejercicios lo mide.
"""),

md(r"""## 6 · El solucionador

Una vez detectados los contactos, MuJoCo plantea el problema de optimización de la sección 3 (encontrar las fuerzas de contacto que cumplen todas las condiciones a la vez) y lo resuelve **por iteraciones** (NB45: el warmstart). Tiene tres algoritmos, que se eligen con `<option solver="...">`:

- **PGS** (*projected Gauss-Seidel*): el más sencillo; va ajustando las fuerzas de una en una. Muchas iteraciones, cada una muy barata.
- **CG** (gradiente conjugado): un término medio.
- **Newton** (el valor por defecto): usa segundas derivadas (el método de Newton del NB17b); **muy** pocas iteraciones, cada una más cara. Suele ser el más rápido y preciso.

Comparémoslos con Zancudo de pie durante 10 segundos: velocidad y número medio de iteraciones por paso:
"""),

code(r"""import time

for nombre, solver in [("PGS", mujoco.mjtSolver.mjSOL_PGS), ("CG", mujoco.mjtSolver.mjSOL_CG),
                       ("Newton", mujoco.mjtSolver.mjSOL_NEWTON)]:
    prueba = mujoco.MjModel.from_xml_path("robots/zancudo.xml")
    prueba.opt.solver = solver
    d = mujoco.MjData(prueba)
    iteraciones = []
    inicio = time.perf_counter()
    for paso in range(5000):
        mujoco.mj_step(prueba, d)
        iteraciones.append(d.solver_niter[0])
    segundos = time.perf_counter() - inicio
    print(f"{nombre:>7}: {5000 / segundos:8,.0f} pasos/s   {np.mean(iteraciones):5.2f} iteraciones por paso   "
          f"altura final {0.865 + d.qpos[1]:.4f} m")"""),

md(r"""Los tres dan **el mismo resultado** (altura final idéntica): resuelven el mismo problema, solo cambia el camino.

- **Newton** necesita **menos de una iteración por paso** de media. ¿Cómo puede ser menos de una? Gracias al **warmstart** (NB45): con Zancudo quieto, la solución del paso anterior ya es casi la buena, y muchas veces basta con comprobarla.
- **CG** hace unas 2, y **PGS** unas 7,5.
- En velocidad, aquí ganan **CG** y **Newton** (unos 60.000 pasos/s); **PGS**, el más lento (unos 47.000).

Con robots más complejos y muchos contactos (un humanoide andando), las diferencias crecen y Newton suele ganar con claridad. Por eso es el valor por defecto, y casi nunca hay que cambiarlo. (Las cifras exactas de velocidad cambian algo de una ejecución a otra: el ordenador está haciendo otras cosas a la vez.)
"""),

md(r"""## 7 · Medir las fuerzas de contacto

### mj_contactForce

Para el control (NB47) y para entender lo que hace un robot, necesitamos **medir** las fuerzas con que el suelo empuja sus pies: las **fuerzas de reacción del suelo** (*ground reaction forces*, GRF). MuJoCo da la fuerza de cada contacto con `mj_contactForce`, con dos detalles que hay que conocer:

1. **Está en el marco del contacto**, no en el del mundo: el primer número es la componente **normal** (perpendicular a la superficie) y los dos siguientes, las **tangentes** (el rozamiento). Para pasarla al mundo, se gira con la matriz `frame` (NB46: mundo = Rᵀ·local, porque `frame` guarda los ejes por **filas**).
2. **Es la fuerza que `geom1` hace sobre `geom2`**. Si el robot es `geom1`, hay que cambiarle el signo para tener la fuerza **sobre el robot**.

Con eso, un generador que da la fuerza de cada contacto del robot con el suelo, en el mundo:
"""),

code(r"""SUELO = zancudo.geom("suelo").id

class FuerzaContacto(NamedTuple):
    pie: str
    posicion: np.ndarray
    fuerza: np.ndarray          # en el mundo, la que el SUELO hace sobre el PIE


def fuerzas_del_suelo(modelo: mujoco.MjModel, datos: mujoco.MjData) -> Iterator[FuerzaContacto]:
    seis = np.zeros(6)
    for i in range(datos.ncon):
        c = datos.contact[i]
        if SUELO not in (c.geom1, c.geom2):
            continue                                       # un contacto que no es con el suelo
        mujoco.mj_contactForce(modelo, datos, i, seis)     # [normal, tangente 1, tangente 2, (pares)]
        fuerza = c.frame.reshape(3, 3).T @ seis[:3]        # del marco del contacto al mundo
        if c.geom1 == SUELO:
            pie = c.geom2
        else:
            pie, fuerza = c.geom1, -fuerza                 # la fuerza era la del pie sobre el suelo
        yield FuerzaContacto(modelo.geom(pie).name, c.pos.copy(), fuerza)


total = np.zeros(3)
for f in fuerzas_del_suelo(zancudo, datos):
    print(f"{f.pie}: en x = {f.posicion[0]:+.2f} m  →  fuerza {f.fuerza} N")
    total += f.fuerza
print("total:", total, "N   peso de Zancudo:", zancudo.body_mass.sum() * 9.81, "N")"""),

md(r"""Cuatro fuerzas, casi verticales (el rozamiento es de centésimas de newton: nadie empuja el robot de lado), y su suma es **231,516 N**: exactamente el **peso** de Zancudo. Es la tercera ley de Newton (NB37) medida: el suelo empuja hacia arriba lo mismo que pesa el robot.

El reparto es interesante: cada **talón** (x = −0,06) soporta **80,8 N** y cada **punta** (x = +0,14), **35,0 N**. El talón carga más del doble. ¿Por qué? Porque el centro de masas está casi encima del tobillo (x ≈ 0), mucho más cerca del talón (a 6 cm) que de la punta (a 14 cm). Es la ley de la palanca (NB37): el punto más cercano a la carga soporta más.
"""),

md(r"""### Otra forma: cfrc_ext

MuJoCo también calcula, para cada cuerpo, la **suma** de todas las fuerzas externas que recibe (contactos incluidos), en `datos.cfrc_ext`. Son 6 números (primero el par, luego la fuerza, como `mj_objectVelocity` en el NB46), expresados en un marco un poco especial (centrado en el CdM del subárbol). Para la fuerza vertical total de un pie basta con mirar el último número... pero ojo, `cfrc_ext` **solo se calcula si algo lo pide** (un sensor que lo use, o la función `mj_rnePostConstraint`):
"""),

code(r"""mujoco.mj_rnePostConstraint(zancudo, datos)
print("fuerza vertical sobre pie_d, según cfrc_ext:", datos.body("pie_d").cfrc_ext[5].round(2), "N")
print("y sumando sus contactos:                    ",
      round(sum(f.fuerza[2] for f in fuerzas_del_suelo(zancudo, datos) if f.pie == "pie_d"), 2), "N")"""),

md(r"""Coinciden. En un robot real, esa medida la da un **sensor de fuerza** en el tobillo o una **plantilla** con sensores de presión; en MuJoCo hay sensores `force`, `torque` y `touch` que la dan directamente (NB50).
"""),

md(r"""## 8 · El centro de presiones, medido

### Del NB39 a los números

En el NB39 vimos el **ZMP** (punto de momento cero) o **centro de presiones** (CdP): el punto del suelo donde "actúa" la suma de todas las fuerzas de los pies. Para un robot en el suelo plano, es la **media de las posiciones de los contactos, pesada por su fuerza vertical**:

```
   x_CdP  =  Σ (x_i · F_z,i)  /  Σ F_z,i
```

Y la regla de oro del NB39: el CdP **siempre** está dentro del **polígono de apoyo** (la zona bajo los pies). Si "querría" salir, el robot **vuelca**. Ahora lo podemos **medir**:
"""),

code(r"""def centro_de_presiones(modelo: mujoco.MjModel, datos: mujoco.MjData) -> np.ndarray | None:
    fuerzas = list(fuerzas_del_suelo(modelo, datos))
    if not fuerzas:
        return None                                   # en el aire: no hay centro de presiones
    pesos = np.array([f.fuerza[2] for f in fuerzas])
    posiciones = np.array([f.posicion for f in fuerzas])
    return (posiciones * pesos[:, None]).sum(axis=0) / pesos.sum()

print("centro de presiones:   ", centro_de_presiones(zancudo, datos))
print("centro de masas (CdM): ", datos.subtree_com[0])"""),

md(r"""Fíjate en tres cosas del código:

- **`list(fuerzas_del_suelo(...))`**: aquí **sí** convertimos el generador en lista, porque lo vamos a recorrer **dos** veces (para los pesos y para las posiciones). Recuerda: un generador se gasta.
- **`-> np.ndarray | None`** y el `return None`: si no hay contactos (el robot salta), no hay CdP. Devolver `None` y documentarlo en la anotación obliga al que llama a pensar en ese caso.
- **`pesos[:, None]`**: convierte el vector de 4 pesos en una columna de 4 × 1, para que la difusión (NB27) lo multiplique por cada **fila** de las posiciones (4 × 3).

Con Zancudo quieto, el CdP está justo debajo del CdM (x ≈ 0,001 m): como en el NB38, un cuerpo en reposo tiene su CdP en la vertical de su CdM.

### Empujar hasta volcar

Ahora el experimento de verdad. Empujamos el torso de Zancudo con una fuerza horizontal **constante** (`xfrc_applied`, NB42), esperamos 3 segundos a que se estabilice y medimos el CdP. Cada vez más fuerte:
"""),

code(r"""TORSO = zancudo.body("torso").id
empujes = [0, 5, 10, 12, 14, 15, 16]
centros, centros_de_masas, de_pie = [], [], []
for empuje in empujes:
    d = mujoco.MjData(zancudo)
    while d.time < 3.0:
        d.xfrc_applied[TORSO, 0] = empuje                 # fuerza en x, aplicada en el CdM del torso
        mujoco.mj_step(zancudo, d)
    mujoco.mj_forward(zancudo, d)
    altura = 0.865 + d.qpos[1]
    centros.append(centro_de_presiones(zancudo, d)[0])
    centros_de_masas.append(d.subtree_com[0][0])
    de_pie.append(altura > 0.8)
    print(f"empuje {empuje:2d} N:  CdP en x = {centros[-1]:+.4f} m,  CdM en x = {centros_de_masas[-1]:+.4f} m,  "
          f"{'de pie' if de_pie[-1] else 'EN EL SUELO'}")"""),

md(r"""A medida que empujamos más fuerte, el **CdP avanza hacia la punta** del pie: 0,04 m con 5 N, 0,07 con 10 N, 0,10 con 14 N... El suelo "se defiende" del empuje cargando cada vez más la punta. Con **16 N, Zancudo se cae**: el CdP ya no puede avanzar más para compensar.

Fíjate en que se cae **antes** de que el CdP llegue a la punta (x = 0,14): con 15 N está en 0,104. Si Zancudo fuera un bloque rígido, aguantaría hasta unos 29 N (cuando el CdP llegara a la punta). Pero no es rígido: sus articulaciones son motores de posición que **ceden** (NB40), y al empujarlo se inclina y su CdM avanza (de 0,001 a 0,037 m). Cada milímetro que avanza el CdM le quita margen. Un robot **más rígido**, o uno que **reaccione** (moviendo el tobillo o dando un paso: el punto de captura del NB39), aguantaría más.
"""),

md(r"""### La comprobación

¿Podemos **predecir** dónde estará el CdP? En reposo, el robot está en equilibrio de **momentos** (NB37): el empuje F, aplicado en el CdM del torso a una altura h, hace un par F·h que intenta volcarlo, y el suelo lo compensa desplazando el CdP. Igualando momentos alrededor del CdM:

```
   x_CdP  =  x_CdM  +  F · h / Peso
```

El CdM del torso está a 0,865 + 0,25 = 1,115 m de altura (NB42: el torso va de 0,05 a 0,45 sobre su origen). Comprobémoslo con los empujes en que sigue de pie:
"""),

code(r"""peso = zancudo.body_mass.sum() * 9.81
h = 0.865 + 0.25
for empuje, cdp, cdm, ok in zip(empujes, centros, centros_de_masas, de_pie):
    if ok:
        print(f"empuje {empuje:2d} N:  medido {cdp:+.4f} m   predicho {cdm + empuje * h / peso:+.4f} m")"""),

md(r"""Hasta 12 N, la fórmula acierta **al milímetro** (0,0868 medido frente a 0,0878 predicho). Con 14 y 15 N empieza a separarse (2 y 5 mm): ahí el robot ya **no está del todo en reposo**, sino empezando a inclinarse (el principio de la caída), y la fórmula, que es la del equilibrio **estático**, deja de ser exacta. Es justo la diferencia entre el CdP "estático" (el del NB38) y el ZMP "dinámico" del NB39, que incluye las aceleraciones.

Este es el tipo de comprobación que distingue a un ingeniero que **entiende** su simulador de uno que solo lo usa: predecir con física sencilla lo que debería salir, medirlo, y saber explicar las diferencias.
"""),

md(r"""## 9 · Contactos y el salto a la realidad

Para terminar, lo que tiene que saber un ingeniero de simulación sobre contactos y robots reales, y lo que conviene decir en una entrevista:

1. **Los contactos son la mayor fuente de *reality gap*.** El rozamiento real cambia con el suelo, la suciedad, la temperatura y el desgaste de la suela; la blandura real depende del material. Por eso se **aleatorizan** (rozamiento entre, digamos, 0,4 y 1,2; NB55): la política aprende a no depender de un valor exacto.
2. **Geometrías de colisión sencillas.** Cápsulas, esferas y cajas para los pies, aunque el robot real tenga formas complicadas. Mallas solo para ver (NB50, NB58). Los contactos malla-malla son lentos y "saltarines".
3. **El número y la posición de los puntos de contacto importan.** Un pie de cápsula tiene dos puntos (talón y punta); uno de caja, cuatro. Los modelos profesionales a veces ponen pequeñas esferas en las esquinas de la suela para tener contactos estables.
4. **Para robots con patas**: cono `elliptic`, `impratio` alto (10 es habitual en los modelos de MuJoCo Playground), y vigilar el deslizamiento lento.
5. **Pasito de tiempo** y contactos van de la mano: contactos más duros (`timeconst` pequeño) necesitan pasitos más pequeños. La documentación de MuJoCo recomienda que `timeconst` sea, al menos, el doble del pasito. La idea de fondo ya la viste en el NB39b (un muelle muy rápido, con ω grande, pide pasito·ω pequeño); en el NB49 la veremos con los integradores de MuJoCo.
6. **Medir** las fuerzas de contacto y el CdP en simulación sirve para **depurar** (¿por qué se cae mi robot?), para **recompensas** (castigar golpes fuertes al apoyar el pie, NB54) y como **observación** (los robots reales tienen sensores de contacto o los estiman).
"""),

md(r"""## 10 · Resumen de la lección

1. **Detección** en dos fases (amplia con cajas, estrecha con fórmulas exactas). Se excluyen las parejas de un mismo cuerpo y madre-hija, las de `<exclude>` y las que no pasan **`contype & conaffinity`** (en cualquiera de los dos sentidos).
2. `datos.contact`: `geom1`, `geom2`, `pos`, `dist` (negativa = atravesados), `dim` y `frame` (fila 0 = normal).
3. Python (repaso del P3 y el P4): **generadores** (`yield`, perezosos, se gastan, `next`, `StopIteration`), expresiones generadoras, el protocolo iterador, `NamedTuple`, `Counter`, `islice`, `groupby` (¡solo agrupa seguidos!).
4. **Contactos blandos**: optimización convexa en vez de complementariedad; se atraviesan un poquito, a cambio de estabilidad y suavidad. **`solref`** = (timeconst, dampratio): lo rápido que se corrige la penetración y si rebota. La penetración **no depende de la masa** (salvo con `solref` negativo = rigidez y amortiguamiento físicos). **`solimp`**: cuánto cede según la penetración.
5. **Rebote**: dampratio < 1, o `solref` negativo con poco amortiguamiento.
6. **Rozamiento** de Coulomb: como mucho μ·N; cono de rozamiento; en una rampa, desliza si tan θ > μ. **Deslizamiento lento** por los contactos blandos: se quita con cono **elíptico** + **`impratio`** + **noslip**. **`condim`** 1, 3, 4, 6; `friction` = (deslizar, girar, rodar).
7. **Solucionadores** PGS, CG y Newton (el de por defecto: pocas iteraciones, rápido).
8. **Fuerzas**: `mj_contactForce` da la fuerza de `geom1` sobre `geom2` en el marco del contacto; girar con `frame.T`. Suma = peso en reposo. `cfrc_ext` (tras `mj_rnePostConstraint`).
9. **Centro de presiones** = media de los contactos pesada por la fuerza vertical. Con un empuje F a una altura h: x_CdP = x_CdM + F·h/Peso, comprobado al milímetro. Cuando el CdP se acerca al borde del pie, el robot vuelca.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Fase amplia / estrecha** | Descarte rápido con cajas / cálculo exacto del contacto. |
| **contype / conaffinity** | Canales en que una geometría "emite" / "escucha" para chocar. |
| **Normal / tangente** | Dirección perpendicular / a lo largo de la superficie de contacto. |
| **Complementariedad (LCP)** | Planteamiento "duro" del contacto: o distancia o fuerza, nunca las dos. |
| **Contacto blando** | El de MuJoCo: se atraviesa un poco y empuja como un muelle muy rígido. |
| **solref / solimp** | Los parámetros de ese "muelle": rapidez y amortiguamiento / cuánto cede. |
| **Coeficiente de rozamiento μ** | Rozamiento máximo = μ × fuerza normal. |
| **Cono de rozamiento** | El conjunto de fuerzas de contacto posibles sin resbalar. Piramidal o elíptico. |
| **Deslizamiento lento (*creep*)** | Resbalar despacio donde no se debería, por los contactos blandos. |
| **condim** | Dimensión del contacto: 1 sin rozamiento, 3 deslizar, 4 + girar, 6 + rodar. |
| **Fuerza de reacción del suelo (GRF)** | La fuerza con que el suelo empuja los pies. |
| **Centro de presiones (CdP)** | Punto medio de los contactos pesado por su fuerza: el ZMP medido. |
| **Generador** | Función con `yield` que produce valores a demanda. |
| **NamedTuple** | Tupla inmutable con campos con nombre. |
"""),

md(r"""## 11 · Ejercicios

**E1.** Cuatro geometrías: A (`contype=1, conaffinity=1`), B (`contype=2, conaffinity=2`), C (`contype=3, conaffinity=0`), D (`contype=0, conaffinity=4`). Sin ejecutar nada, ¿qué parejas pueden chocar? Comprueba tu respuesta escribiendo una función `pueden_chocar(a, b)` con la regla de bits.

**E2.** Repite el experimento de `dejar_caer` con `timeconst` de 0,001, 0,002, 0,004 y 0,008 (con `dampratio` 1). ¿Cómo cambia la penetración en reposo?

**E3.** Escribe una función que encuentre el μ **mínimo** para que la caja **no** deslice en una rampa de 35°, por **búsqueda binaria** (probar en la mitad del intervalo y quedarte con la mitad donde está la respuesta, como al buscar una palabra en un diccionario: si con μ desliza, el crítico es mayor; si no, menor). Compárala con tan(35°).

**E4.** Escribe un generador `fuerza_por_pie(modelo, datos)` que dé parejas `(pie, fuerza_vertical_total)` sumando los contactos de cada pie, usando `fuerzas_del_suelo`. Úsalo con Zancudo empujado hacia delante con 10 N. ¿Cambia el reparto entre los dos pies? ¿Por qué?

**E5.** Con `condim="1"` en el suelo y en la caja, ¿a qué velocidad desliza la caja en una rampa de solo 5°? (Pista: añade un parámetro `condim` a `rampa` y ponlo en las dos geometrías.)

**E6.** **Reto.** Haz un barrido: para cada combinación de μ ∈ {0,3, 0,5, 0,8} y ángulo ∈ {10°, 20°, 30°, 40°}, ¿desliza (más de 50 mm/s) o no? Usa `itertools.product` para recorrer las combinaciones sin bucles anidados, y presenta el resultado como una tabla. ¿Coincide con tan θ > μ en todos los casos?
"""),

md(r'''<details>
<summary>▶ Solución E1</summary>

Aplicando la regla (contype de uno `&` conaffinity del otro, en los dos sentidos):

- A–B: 1 & 2 = 0 y 2 & 1 = 0 → **no**.
- A–C: 1 & 0 = 0, pero 3 & 1 = 1 → **sí** (C emite en los canales 1 y 2, y A escucha en el 1).
- A–D: 1 & 4 = 0 y 0 & 1 = 0 → **no**.
- B–C: 2 & 0 = 0, pero 3 & 2 = 2 → **sí**.
- B–D: 2 & 4 = 0 y 0 & 2 = 0 → **no**.
- C–D: 3 & 4 = 0 y 0 & 0 = 0 → **no** (D escucha en el canal 3, bit 2, y nadie emite ahí).

```python
from itertools import combinations

def pueden_chocar(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return bool((a[0] & b[1]) or (b[0] & a[1]))

geometrias = {"A": (1, 1), "B": (2, 2), "C": (3, 0), "D": (0, 4)}
print([(x, y) for x, y in combinations(geometrias, 2) if pueden_chocar(geometrias[x], geometrias[y])])
# [('A', 'C'), ('B', 'C')]
```

C es una geometría que "toca a los demás pero nadie la toca a ella por su lado" (no escucha nada), y D es inútil: escucha en un canal en el que nadie emite. `combinations` (de `itertools`) da todas las parejas sin repetir.
</details>

<details>
<summary>▶ Solución E2</summary>

```python
for timeconst in [0.001, 0.002, 0.004, 0.008]:
    impacto, reposo = dejar_caer(f"{timeconst} 1")
    print(timeconst, round(reposo, 4), "mm")
```

En reposo: **0,030**, **0,033**, **0,039** y **0,053** mm. La penetración crece con `timeconst` (contacto más blando), pero fíjate en que de 0,001 a 0,002 apenas cambia: por debajo de unos pocos pasitos, endurecer más el contacto ya no sirve de mucho (el pasito de 0,002 s no puede seguir cambios tan rápidos), y es cuando la documentación aconseja no bajar de 2 pasitos.
</details>

<details>
<summary>▶ Solución E3</summary>

```python
def mu_critico(angulo: float, tolerancia: float = 1e-4) -> float:
    abajo, arriba = 0.0, 2.0                 # con μ = 0 desliza seguro; con μ = 2, a 35° no
    while arriba - abajo > tolerancia:
        medio = (abajo + arriba) / 2
        if rampa(angulo, medio) > 50:        # desliza: hace falta más rozamiento
            abajo = medio
        else:
            arriba = medio
    return arriba

print(mu_critico(35), np.tan(np.radians(35)))     # ≈ 0.703 y 0.700
```

Sale **0,703**, frente a tan 35° = **0,700**: la física de Coulomb, recuperada por búsqueda binaria con un 0,4 % de diferencia (por el criterio de "desliza" que hemos elegido, más de 50 mm/s, y el deslizamiento lento). Cada vuelta del bucle **divide por dos** el intervalo: con 15 vueltas se pasa de un intervalo de 2 a uno de 0,00006. La búsqueda binaria es una herramienta que todo ingeniero tiene que tener a mano: encontrar umbrales (de empuje, de rozamiento, de ganancia...) con muy pocas simulaciones.
</details>

<details>
<summary>▶ Solución E4</summary>

```python
def fuerza_por_pie(modelo, datos):
    totales: dict[str, float] = {}
    for f in fuerzas_del_suelo(modelo, datos):
        totales[f.pie] = totales.get(f.pie, 0.0) + f.fuerza[2]
    yield from totales.items()

d = mujoco.MjData(zancudo)
while d.time < 3.0:
    d.xfrc_applied[TORSO, 0] = 10
    mujoco.mj_step(zancudo, d)
mujoco.mj_forward(zancudo, d)
print(list(fuerza_por_pie(zancudo, d)))      # [('pie_d', 115.76), ('pie_i', 115.76)]
```

**Los dos cargan lo mismo**, 115,76 N (la mitad del peso). El empuje es hacia **delante** (x) y Zancudo es simétrico de izquierda a derecha: lo que cambia es el reparto entre **talón y punta** de cada pie (el CdP avanza, sección 8), no entre pies. Para cargar más un pie habría que empujar de lado... y Zancudo, que es plano, ni siquiera puede caerse de lado (NB53).

Dos cosas de Python (repaso del P4): `yield from iterable` entrega, uno a uno, todos los elementos de otro iterable (aquí, las parejas del diccionario); y `dict.get(clave, 0.0)` da el valor guardado o 0,0 si la clave aún no está (otra forma de hacerlo: `collections.defaultdict(float)`).
</details>

<details>
<summary>▶ Solución E5</summary>

Añadiendo a `rampa` un argumento `condim` y poniendo `condim="{condim}"` en los dos `<geom>`:

- con `condim=1`: la caja baja la rampa de 5° a unos **2.566 mm/s** de media entre los segundos 2 y 4 (y acelerando: sin rozamiento, nada la frena);
- con `condim=3`: **0,28 mm/s** (el pequeño deslizamiento lento).

Sin rozamiento, **cualquier** inclinación hace deslizar.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
from itertools import product

print("   μ   ángulo  ¿desliza?  ¿tan θ > μ?")
for mu, angulo in product([0.3, 0.5, 0.8], [10, 20, 30, 40]):
    desliza = rampa(angulo, mu) > 50
    teoria = np.tan(np.radians(angulo)) > mu
    print(f"  {mu}    {angulo}°      {'sí' if desliza else 'no':<3}         {'sí' if teoria else 'no'}")
```

En los **12** casos coinciden. Desliza: μ = 0,3 a partir de 20°; μ = 0,5 a partir de 30°; μ = 0,8 solo a 40° (umbral, 38,7°). `product` recorre todas las combinaciones como si fueran dos bucles anidados, en una sola línea: es la herramienta estándar para los **barridos de parámetros** (lo usaremos mucho en el NB55).
</details>
'''),

md(r"""## 12 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **NB49** cerramos el "motor" de MuJoCo con el **tiempo**: los integradores (Euler, implícito, RK4), cómo elegir el **pasito**, cuándo y por qué una simulación **explota**, el **determinismo**, y cómo hacer que todo vaya **más rápido** (medir con un perfilador, simular muchos robots en paralelo). En Python: **decoradores**, **gestores de contexto** (`with`), `functools` y **multiproceso**.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB48_contactos_a_fondo.ipynb")
    build(out, cells, title="NB48 · Contactos a fondo")
