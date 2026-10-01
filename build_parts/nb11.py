"""Construye NB11 · Proyecto: el palo de escoba (cierre de la Parte 1).

Un entorno de aprendizaje por refuerzo completo, desde cero, con lo de NB05-NB10.
Ideas nuevas (pocas, en microdosis): import random (módulo), random.uniform,
random.seed (repetir el mismo azar), constantes en MAYÚSCULAS, una función que
lee cajas de fuera. Física de juguete (unidades: grados, grados/s, paso 0,02 s):
  aceleración = 10 × inclinación + empuje (limitado a ±40) + viento (±30 al azar)
  terminado si |inclinación| > 30; recompensa = 1 − (inclinación/30)² (0 si cae)
  máx. 500 pasos (10 s). Empieza inclinado 2 grados, quieto.
Resultados medidos (semillas 0-4): nada ~44.8 (≈50 pasos), azar ~43.2,
solo inclinación (−30·i) 296.0 (2 de 5 completos; oscila y diverge),
inclinación+velocidad (−30·i − 8·v) 499.9 (5/5). Búsqueda aleatoria de 20
candidatos (semilla 42): mejor 499.9 (k≈47.9, d≈6.7); en 10 mundos nuevos 499.9.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB11 · Proyecto: el palo de escoba

**Parte 1 · Primeros pasos con el ordenador — Lección 7 (proyecto final)**

> Llevas seis lecciones construyendo herramientas: `print` (NB05), variables (NB06), bucles (NB07),
> decisiones (NB08), listas (NB09) y funciones (NB10). Hoy no vas a aprender casi nada nuevo. Hoy vas a
> **usarlo todo junto** para construir algo de verdad.

Vamos a construir, **desde cero y con tus propias manos**, un mundo completo de aprendizaje por refuerzo:
un robot de juguete que tiene que **mantener en equilibrio un palo de escoba**. Sí, el mismo palo de escoba
sobre la palma de la mano con el que empezó el curso, en el NB00.

Tendrá **todo** lo que vimos en la Parte 0, ahora en código:

| Pieza (Parte 0) | En este proyecto |
|---|---|
| El cuerpo y el mundo (NB01, NB02) | Una física de juguete, a pasitos, con gravedad, un motor y viento |
| La mente: observación → acción (NB03) | Funciones que reciben la inclinación y deciden un empuje |
| La recompensa (NB04) | Un número por paso: más puntos cuanto más derecho esté el palo |
| Episodios que terminan (NB03, NB08) | Si el palo se inclina más de 30 grados, se acabó |
| Comparar políticas (NB04, NB10) | Retorno medio en los mismos mundos |
| Aprender probando (NB00) | El ordenador busca **solo** una buena política |

Al final habrás hecho tu **primer aprendizaje por refuerzo**. Pequeñito, pero de verdad.

Es una lección larga. Tómatela en varios ratos si quieres; cada apartado deja algo terminado.
"""),

md(r"""## 1 · El problema: un palo que se cae

Imagina un palo de escoba de pie sobre un **carrito** (o sobre tu mano). El palo tiende a caerse: en cuanto
se inclina un poco, la gravedad lo inclina más, y cada vez más deprisa. Nuestro robot de juguete tiene **un
solo motor** que puede **empujar** la base hacia un lado o hacia el otro, para "ponerse debajo" del palo y
enderezarlo. Como tu mano con la escoba.

```
         inclinación
          (grados)
            ╲  │
             ╲ │            el palo se inclina hacia un lado;
              ╲│            el motor empuja la base para corregir
          ┌────●────┐
          │ carrito │  ◄── empuje ──►
          └─o─────o─┘
   ═══════════════════════════  suelo
```

Este problema es tan clásico que tiene nombre propio entre los investigadores: se parece mucho al
**"carro con péndulo"** (*CartPole*), uno de los primeros problemas con los que se probó el aprendizaje por
refuerzo, hace más de 40 años, y con el que todavía hoy empieza casi todo el mundo.

Antes de programar nada, hagamos lo que haría un profesional: escribir la **ficha del entorno**. Es la
descripción de qué observa el agente, qué puede hacer, qué puntos recibe y cuándo termina:

| | Nuestro palo de escoba |
|---|---|
| **Observación** | 2 números: la **inclinación** (grados; positiva hacia un lado, negativa hacia el otro) y la **velocidad de giro** (grados por segundo) |
| **Acción** | 1 número: el **empuje** del motor, entre −40 y +40 |
| **Recompensa por paso** | 1 − (inclinación / 30)²: **1 punto** si está perfectamente derecho, **menos** cuanto más inclinado |
| **Terminado** | Si la inclinación pasa de **30 grados** (hacia cualquier lado): el palo se ha caído |
| **Truncado** | A los **500 pasos** (10 segundos; cada paso son 0,02 s) |
| **Mejor retorno posible** | Casi **500** (500 pasos × casi 1 punto) |

Compárala con la del humanoide: allí la observación tenía 45 números y la acción 17. Aquí, 2 y 1. Es el
mismo tipo de problema, en miniatura.

(¿Ves la recompensa? Es **densa** —da puntos en cada paso, como el "frío, caliente" del NB04— y usa el
**cuadrado** para castigar mucho más las inclinaciones grandes que las pequeñas.)
"""),

md(r"""## 2 · La física de juguete

Necesitamos una "cadena de oro" (NB02) para el palo. Usaremos una versión **simplificada** a propósito: no es
la física exacta de una escoba (esa necesita matemáticas que aún no hemos visto), pero **se comporta como
una**, que es lo que importa para aprender. En cada pasito:

```
   aceleración de giro = 10 × inclinación  +  empuje del motor  +  viento
                         ──────────────────   ───────────────      ──────
                         la gravedad: cuanto   lo que decide la    un empujoncito al
                         MÁS inclinado, MÁS    política (limitado  azar en cada paso
                         rápido se cae         a ±40)              (entre −30 y +30)

   velocidad de giro = velocidad de giro + aceleración × 0,02      (fuerza → velocidad)
   inclinación       = inclinación + velocidad de giro × 0,02      (velocidad → posición)
```

Las dos últimas líneas son **exactamente** las de la pelota del NB06-NB07. La primera tiene tres
ingredientes:

- **La gravedad, `10 × inclinación`.** Fíjate: si el palo está derecho (inclinación 0), la gravedad no lo
  tumba hacia ningún lado. Pero si está inclinado 2 grados, lo empuja a caer más; si está inclinado 10, lo
  empuja **cinco veces más**. Por eso un palo inclinado se cae cada vez más deprisa: es la **inestabilidad**
  del NB00, metida en una fórmula.
- **El empuje del motor.** Lo decide la política. Está **limitado** a ±40, porque ningún motor es un
  superhéroe (NB01).
- **El viento.** Un número **al azar** en cada paso, entre −30 y +30. Representa todo lo que no controlamos
  (una corriente de aire, una vibración, el ruido de los sensores del NB01). Sin él, el problema sería
  demasiado fácil y poco realista.

Para el viento necesitamos algo que aún no sabemos hacer: **números al azar**. Es la primera (y casi la
única) idea nueva de hoy.
"""),

md(r"""## 3 · Una idea nueva: números al azar

Python trae muchísimas herramientas **guardadas en cajas de herramientas** separadas, que no se cargan si no
las pides (así el ordenador no se llena de cosas que no usas). A esas cajas se les llama **módulos**. Hay un
módulo para el azar, que se llama **`random`** ("aleatorio"), y para usarlo hay que **importarlo**, es decir,
sacarlo del armario. Se hace una vez, normalmente al principio:
"""),

code(r"""import random"""),

md(r"""No sale nada: solo hemos sacado la caja de herramientas. Ahora podemos usar lo que hay dentro, escribiendo
el nombre del módulo, **un punto**, y el nombre de la herramienta (como los métodos del NB09). La que
necesitamos es **`random.uniform(a, b)`**, que devuelve un número decimal **al azar entre `a` y `b`**:
"""),

code(r"""print(random.uniform(-30, 30))
print(random.uniform(-30, 30))
print(random.uniform(-30, 30))"""),

md(r"""Tres números al azar entre −30 y +30, cada uno distinto. (Si ejecutas tú la celda, te saldrán **otros**
números: ¡son al azar!) Ese es nuestro viento.
"""),

md(r"""### Repetir el mismo azar: la semilla

Pero tener azar trae un problema. Si queremos **comparar** dos políticas, ¿cómo sabemos que una ganó porque
es mejor y no porque **tuvo suerte** con el viento? En la vida real no se puede repetir exactamente el mismo
viento. Pero recuerda una de las ventajas del simulador (NB02): **se puede repetir exactamente el mismo
intento**.

Los números "al azar" de un ordenador en realidad salen de una receta matemática muy enrevesada que parte de
un número inicial, llamado **semilla**. Si fijas la semilla con **`random.seed(...)`**, la receta produce
**siempre la misma secuencia** de números "al azar". Mira: fijamos la semilla 7 y pedimos dos números; luego
**volvemos a fijar** la semilla 7 y pedimos otros dos:
"""),

code(r"""random.seed(7)
print(random.uniform(-1, 1), random.uniform(-1, 1))

random.seed(7)
print(random.uniform(-1, 1), random.uniform(-1, 1))"""),

md(r"""¡Los **mismos** dos números las dos veces! Con la misma semilla, el mismo azar.

Esto nos da un superpoder para comparar políticas con justicia: a cada episodio le daremos una **semilla**, y
así **todas las políticas se enfrentarán exactamente al mismo viento**. Como en una competición de esquí en la
que todos bajan **la misma pista**: si uno gana, no es porque le tocara mejor nieve.
"""),

md(r"""## 4 · Construyendo el mundo

Ya tenemos todas las piezas. Vamos a construir el entorno con **funciones** (NB10), pieza a pieza.

Primero, los números fijos del mundo. Por costumbre, los programadores escriben en **MAYÚSCULAS** los nombres
de las cajas que **no deben cambiar** durante el programa (se llaman **constantes**). Python no lo obliga; es
un aviso para quien lee: "esto es una regla del mundo, no lo toques":
"""),

code(r"""PASO_TIEMPO = 0.02       # cada paso dura 0,02 segundos (50 decisiones por segundo)
EMPUJE_MAXIMO = 40       # la fuerza máxima del motor
VIENTO_MAXIMO = 30       # el viento sopla, al azar, entre -30 y +30
CAIDA = 30               # si se inclina más de 30 grados, se ha caído
PASOS_MAXIMOS = 500      # 500 pasos = 10 segundos"""),

md(r"""Segundo, cómo **empieza** cada episodio: el palo arranca **un poquito inclinado** (2 grados) y quieto. Si
empezara perfectamente derecho y sin viento, nunca se caería: no sería un reto.
"""),

code(r"""def reiniciar():
    inclinacion = 2.0
    velocidad = 0.0
    return inclinacion, velocidad"""),

md(r"""## 5 · El corazón: la función de paso

Ahora, la pieza más importante: la **función de paso** (NB10), la que recibe el estado actual y la acción, y
devuelve lo que pasa un pasito después. Es nuestro "MuJoCo" de bolsillo. Devuelve **cuatro** cosas: la nueva
inclinación, la nueva velocidad, la recompensa del paso y si el episodio ha terminado.

Léela despacio, con sus comentarios. Cada línea es algo que ya conoces:
"""),

code(r"""def paso(inclinacion, velocidad, empuje):
    # 1. El motor no es un superhéroe: limitamos el empuje a +-40 (NB01, NB08)
    if empuje > EMPUJE_MAXIMO:
        empuje = EMPUJE_MAXIMO
    if empuje < -EMPUJE_MAXIMO:
        empuje = -EMPUJE_MAXIMO

    # 2. El viento: un empujoncito al azar (lo nuevo de hoy)
    viento = random.uniform(-VIENTO_MAXIMO, VIENTO_MAXIMO)

    # 3. La física: la cadena de oro (NB02, NB06)
    aceleracion = 10 * inclinacion + empuje + viento
    velocidad = velocidad + aceleracion * PASO_TIEMPO
    inclinacion = inclinacion + velocidad * PASO_TIEMPO

    # 4. ¿Se ha caído? (NB08: una comparación ya es True o False)
    terminado = inclinacion > CAIDA or inclinacion < -CAIDA

    # 5. La recompensa (NB04): 1 si está derecho, menos cuanto más inclinado, 0 si ha caído
    if terminado:
        recompensa = 0
    else:
        recompensa = 1 - (inclinacion / CAIDA) ** 2

    return inclinacion, velocidad, recompensa, terminado"""),

md(r"""Probémosla con **un solo paso**: el palo inclinado 2 grados, quieto, y el motor **sin empujar** (empuje 0).
Fijamos una semilla para que el viento sea siempre el mismo:
"""),

code(r"""random.seed(0)
inclinacion, velocidad, recompensa, terminado = paso(2.0, 0.0, 0)
print("inclinación:", round(inclinacion, 3), "| velocidad:", round(velocidad, 3))
print("recompensa:", round(recompensa, 4), "| ¿terminado?:", terminado)"""),

md(r"""Tras un pasito, el palo se ha inclinado un poquito más (la gravedad y el viento lo han empujado), ha empezado
a girar, y la recompensa es casi 1 (sigue casi derecho). No ha terminado. **El mundo funciona.**
"""),

md(r"""## 6 · Un episodio completo

Ahora, una función que juega **un episodio entero** con la política que le pasemos (como `simular_una_hora`
del NB10). Es el bucle agente-entorno del NB03, con todas sus piezas: reiniciar, y en cada paso, la política
decide, el mundo responde, se acumula la recompensa, y si el palo cae, `break` (NB08). Devuelve el **retorno**
(NB04) y cuántos pasos aguantó:
"""),

code(r"""def episodio(politica, semilla):
    random.seed(semilla)                        # el mismo viento para todas las políticas
    inclinacion, velocidad = reiniciar()
    retorno = 0
    pasos_aguantados = 0

    for n in range(PASOS_MAXIMOS):
        empuje = politica(inclinacion, velocidad)                      # EL AGENTE
        inclinacion, velocidad, recompensa, terminado = paso(inclinacion, velocidad, empuje)  # EL ENTORNO
        retorno = retorno + recompensa
        pasos_aguantados = pasos_aguantados + 1
        if terminado:
            break

    return retorno, pasos_aguantados"""),

md(r"""Y otra función que juega **cinco episodios** (con las semillas 0, 1, 2, 3 y 4, siempre las mismas) y devuelve
el **retorno medio** (NB09). Una sola partida puede ser cuestión de suerte; la media de cinco es mucho más fiable
(recuerda la costumbre del NB04: **medir bien**):
"""),

code(r"""def evaluar(politica):
    retornos = []
    for semilla in range(5):
        retorno, pasos_aguantados = episodio(politica, semilla)
        retornos.append(retorno)
    return sum(retornos) / len(retornos)"""),

md(r"""El mundo está terminado. Ahora, a probar políticas. Una política, recuerda (NB10), es una función que recibe la
observación (inclinación y velocidad) y devuelve una acción (el empuje).
"""),

md(r"""## 7 · Política 1: no hacer nada

La más sencilla de todas: el motor nunca empuja. Es el "muñeco de trapo" del NB04. (Fíjate en que recibe la
observación, pero no la usa: decide lo mismo pase lo que pase.)
"""),

code(r"""def politica_nada(inclinacion, velocidad):
    return 0

retorno, pasos_aguantados = episodio(politica_nada, 0)
print("Un episodio: retorno", round(retorno, 1), "| aguantó", pasos_aguantados, "pasos")
print("Media de 5 episodios:", round(evaluar(politica_nada), 1))"""),

md(r"""El palo aguanta unos **50 pasos** (1 segundo) y luego se cae. Retorno medio: unos **45 puntos** de 500
posibles. La gravedad (con ayuda del viento) gana siempre.
"""),

md(r"""## 8 · Política 2: moverse al azar

Como el humanoide del GIF del NB00: el motor empuja al azar, a lo loco, entre −40 y +40, sin mirar nada:"""),

code(r"""def politica_azar(inclinacion, velocidad):
    return random.uniform(-EMPUJE_MAXIMO, EMPUJE_MAXIMO)

print("Media de 5 episodios:", round(evaluar(politica_azar), 1))"""),

md(r"""Unos **43 puntos**: ¡**incluso un poco peor que no hacer nada**! Exactamente lo que medimos con el humanoide en el
NB04 (el robot al azar sacaba 98 puntos y el muñeco de trapo, 198). Moverse sin saber no sirve: empujar al azar
es como añadir **más viento**.
"""),

md(r"""## 9 · Política 3: escrita a mano (primera versión)

Ahora usemos la cabeza, como un ingeniero de **control clásico** (NB03). Recuerda la regla de la escoba:
"**si se inclina hacia un lado, empuja hacia ese lado** para ponerte debajo". En números: empujar **en contra**
de la inclinación (con el signo cambiado, como el rebote del NB08), y con más fuerza cuanto más inclinado
esté. Por ejemplo, 30 veces la inclinación:
"""),

code(r"""def politica_solo_inclinacion(inclinacion, velocidad):
    return -30 * inclinacion

print("Media de 5 episodios:", round(evaluar(politica_solo_inclinacion), 1))"""),

md(r"""**296 puntos de media**: ¡muchísimo mejor! Pero... no son 500. Algo falla a veces. Veamos episodio a episodio,
con un bucle sobre las cinco semillas:
"""),

code(r"""for semilla in range(5):
    retorno, pasos_aguantados = episodio(politica_solo_inclinacion, semilla)
    print("semilla", semilla, "| retorno", round(retorno, 1), "| aguantó", pasos_aguantados, "pasos")"""),

md(r"""En **dos** episodios aguanta (casi) los 500 pasos, pero en los otros **tres** el palo acaba cayéndose, a veces a
mitad del episodio. Para entender por qué, hagamos lo de los profesionales (NB09): **grabar** la trayectoria y
mirarla. Esta función es como `episodio`, pero en vez del retorno devuelve la **lista de inclinaciones**:
"""),

code(r"""def grabar(politica, semilla):
    random.seed(semilla)
    inclinacion, velocidad = reiniciar()
    inclinaciones = []
    for n in range(PASOS_MAXIMOS):
        empuje = politica(inclinacion, velocidad)
        inclinacion, velocidad, recompensa, terminado = paso(inclinacion, velocidad, empuje)
        inclinaciones.append(inclinacion)
        if terminado:
            break
    return inclinaciones"""),

md(r"""Grabamos el episodio de la semilla 1 (uno de los que fallan) y miramos la inclinación **cada 20 pasos**. Para
eso usamos `range` con un **tercer número**, el **salto** (lo viste en el reto E8 del NB07): `range(0, 181, 20)`
da 0, 20, 40... hasta 180:
"""),

code(r"""trayectoria = grabar(politica_solo_inclinacion, 1)
print("Pasos grabados:", len(trayectoria))
for i in range(0, len(trayectoria), 20):
    print("paso", i, "| inclinación", round(trayectoria[i], 1))"""),

md(r"""Fíjate en la secuencia: 2,0 → 0 → −2,8 → −3,3 → −2,5 → 1,2 → 4,0 → 6,4 → 11,7... El palo **oscila** de un lado
a otro, como un columpio, y cada oscilación es **más grande** que la anterior, hasta que se cae.

¿Por qué? Piensa en lo que hace la política: solo mira **dónde está** el palo, no **hacia dónde se mueve**. Cuando
el palo vuelve hacia el centro a toda velocidad, la política solo ve "ya casi está derecho, empujo poco"... y el
palo, por **inercia** (NB02), se pasa de largo hacia el otro lado. Entonces empuja hacia el otro lado, el palo vuelve
y se pasa otra vez... Cada vez llega con más velocidad, y el viento va sumando.

**Es el problema de la foto del NB03.** Una foto del palo en el centro no dice si está quieto o si cruza el centro a
toda velocidad. A esta política le falta mirar la **velocidad**.
"""),

md(r"""## 10 · Política 4: escrita a mano, mirando también la velocidad

Arreglémoslo. Además de empujar en contra de la inclinación, vamos a empujar **en contra de la velocidad**: si el
palo se está moviendo deprisa hacia un lado, **frenarlo** antes de que se pase. Es como frenar un columpio: no
esperas a que llegue arriba, lo frenas mientras se mueve.
"""),

code(r"""def politica_a_mano(inclinacion, velocidad):
    return -30 * inclinacion - 8 * velocidad

for semilla in range(5):
    retorno, pasos_aguantados = episodio(politica_a_mano, semilla)
    print("semilla", semilla, "| retorno", round(retorno, 1), "| aguantó", pasos_aguantados, "pasos")
print("Media de 5 episodios:", round(evaluar(politica_a_mano), 1))"""),

md(r"""**¡Los cinco episodios completos, 500 pasos cada uno, y 499,9 puntos de media!** Prácticamente el máximo
posible. Miremos su trayectoria para ver la diferencia:
"""),

code(r"""trayectoria = grabar(politica_a_mano, 1)
for i in range(0, 181, 20):
    print("paso", i, "| inclinación", round(trayectoria[i], 1))
print("Inclinación máxima de todo el episodio:", round(max(trayectoria), 1), "grados")"""),

md(r"""Con la misma semilla (el **mismo** viento que tumbó a la política anterior), ahora el palo se endereza enseguida
y se queda temblando a menos de medio grado del centro durante los 10 segundos. La inclinación más grande de todo
el episodio es la del principio, los 2 grados de salida.

Recapitulemos con una tabla, como la del NB04:

| Política | Qué mira | Retorno medio (máx. ~500) |
|---|---|---|
| Nada | Nada | ~45 |
| Al azar | Nada | ~43 |
| Solo inclinación | Dónde está el palo | ~296 (se cae 3 de cada 5 veces) |
| Inclinación + velocidad | Dónde está **y hacia dónde va** | **~499,9** (5 de 5) |

La lección es preciosa: la diferencia entre la tercera y la cuarta no es "más fuerza" ni "más inteligencia": es
**la información que usa**. Por eso la observación del humanoide incluye **velocidades** (NB03).
"""),

md(r"""## 11 · Las ruedecillas: ¿y si no supiéramos los números?

Fíjate en la política ganadora: `-30 * inclinacion - 8 * velocidad`. ¿De dónde salieron el **30** y el **8**? Los
elegí yo, porque sé un poco de control. Pero ¿y si no supiéramos qué números poner?

Esos dos números son, exactamente, las **ruedecillas** del NB03: los **parámetros** de la política. La "máquina"
es siempre la misma (empujar en contra de la inclinación y de la velocidad); lo que cambia es **cuánto**. Vamos a
escribir la política con las ruedecillas en dos cajas, **fuera** de la función.

(Una idea pequeñita nueva: una función puede **leer** cajas creadas fuera de ella. Lo que no puede es que sus cajas
**locales** se vean desde fuera, como vimos en el NB10. Aquí la función lee las dos ruedecillas de fuera, y así
podemos girarlas sin tocar la función.)
"""),

code(r"""ruedecilla_inclinacion = 30
ruedecilla_velocidad = 8

def politica_ruedecillas(inclinacion, velocidad):
    return -ruedecilla_inclinacion * inclinacion - ruedecilla_velocidad * velocidad

print("Con 30 y 8:", round(evaluar(politica_ruedecillas), 1))"""),

md(r"""Con las ruedecillas en 30 y 8, es la política a mano: 499,9. Si giramos las ruedecillas, la política cambia
**sin reescribirla**. Por ejemplo, con la ruedecilla de velocidad a 0 tendríamos la política "solo inclinación":
"""),

code(r"""ruedecilla_inclinacion = 30
ruedecilla_velocidad = 0
print("Con 30 y 0:", round(evaluar(politica_ruedecillas), 1))"""),

md(r"""296, como antes. **Misma máquina, otras ruedecillas, otro comportamiento.** Es exactamente la idea del NB03:
aprender es **encontrar dónde poner las ruedecillas**.
"""),

md(r"""## 12 · Aprender probando: que el ordenador busque solo

Y ahora, el gran final. Vamos a hacer que el **ordenador encuentre solo** unas buenas ruedecillas, **sin que nadie
le diga** que 30 y 8 funcionan. El método más sencillo que existe, y el primero que se le ocurriría a cualquiera:

```
   1. Inventa unas ruedecillas al azar.
   2. Pruébalas: juega unos episodios y mira el retorno medio.
   3. Si es el mejor retorno visto hasta ahora, apúntalas.
   4. Repite muchas veces. Al final, quédate con las mejores.
```

Se llama **búsqueda aleatoria** (*random search*), y aunque es muy simple, **es aprendizaje por refuerzo**: el
agente mejora su política **probando** y guiándose **solo por la recompensa** (NB00, NB04). Nadie le explica la
física, ni la regla de la escoba, ni el problema de la foto.

Primero, inventamos **20 candidatos** al azar: 20 parejas de ruedecillas, la de inclinación entre 0 y 50, y la de
velocidad entre 0 y 20. Los guardamos en dos listas paralelas (NB09). (Los inventamos **todos antes** de empezar a
probar, porque cada episodio fija su propia semilla para el viento, y si no, se "mezclarían" los dados del viento
con los dados de la búsqueda.)
"""),

code(r"""random.seed(42)
candidatos_inclinacion = []
candidatos_velocidad = []
for intento in range(20):
    candidatos_inclinacion.append(random.uniform(0, 50))
    candidatos_velocidad.append(random.uniform(0, 20))

print("Primer candidato:", round(candidatos_inclinacion[0], 1), "y", round(candidatos_velocidad[0], 1))"""),

md(r"""Y ahora, **el bucle del aprendizaje**. Para cada candidato: ponemos las ruedecillas, evaluamos, y si es el mejor
hasta ahora, lo apuntamos. Es el patrón del **acumulador** (NB07), pero en vez de sumar, **guarda el mejor**
(empezamos con un "mejor" de −1, peor que cualquier retorno posible, para que el primer candidato siempre lo supere):
"""),

code(r"""mejor_retorno = -1
mejor_inclinacion = 0
mejor_velocidad = 0

for intento in range(20):
    ruedecilla_inclinacion = candidatos_inclinacion[intento]
    ruedecilla_velocidad = candidatos_velocidad[intento]
    puntos = evaluar(politica_ruedecillas)

    if puntos > mejor_retorno:
        mejor_retorno = puntos
        mejor_inclinacion = ruedecilla_inclinacion
        mejor_velocidad = ruedecilla_velocidad
        print("intento", intento, "| ruedecillas", round(ruedecilla_inclinacion, 1), "y",
              round(ruedecilla_velocidad, 1), "| retorno", round(puntos, 1), "  <- ¡nuevo mejor!")
    else:
        print("intento", intento, "| ruedecillas", round(ruedecilla_inclinacion, 1), "y",
              round(ruedecilla_velocidad, 1), "| retorno", round(puntos, 1))

print()
print("LO APRENDIDO: ruedecillas", round(mejor_inclinacion, 1), "y", round(mejor_velocidad, 1),
      "| retorno", round(mejor_retorno, 1))"""),

md(r"""(Fíjate en un detalle de escritura: cuando una línea de código es muy larga, se puede **partir** dentro de un
paréntesis y seguir en la línea de abajo. Python sabe que el paréntesis aún no se ha cerrado.)

**¡El ordenador ha encontrado solo una política que mantiene el palo de pie!** Mira la lista con calma:

- Algunos candidatos son **malísimos**: los que tienen la ruedecilla de inclinación muy pequeña (por ejemplo, 1,3 o
  4,6) sacan menos de 100 puntos. Su motor empuja demasiado poco para vencer a la gravedad.
- Otros fallan por **falta de velocidad**: el que tiene 40,5 y 0,1 se queda en 300, como nuestra política "solo
  inclinación". ¡El ordenador ha "redescubierto" el problema de la foto, sin que nadie se lo explicara!
- Y muchísimos otros llegan a los 499 y pico. El primer "nuevo mejor" con 499,7 aparece ya en el **segundo** intento.

Los "nuevos mejores" del final mejoran en **centésimas** que el redondeo no deja ver: ya estamos tocando el techo.
"""),

md(r"""### La prueba de verdad: mundos que nunca ha visto

Cuidado con una trampa. Hemos elegido las ruedecillas mirando **solo** las semillas 0 a 4. ¿Y si ha encontrado unas
ruedecillas que solo funcionan **con esos cinco vientos concretos**, de casualidad? Sería como un estudiante que se
aprende de memoria las respuestas de un examen de prueba, y luego suspende el examen de verdad.

Así que hacemos lo que hacen los profesionales: **probar en mundos nuevos**, que no se usaron para elegir. Usamos las
semillas 100 a 109 (diez vientos que nunca ha visto):
"""),

code(r"""ruedecilla_inclinacion = mejor_inclinacion
ruedecilla_velocidad = mejor_velocidad

retornos_nuevos = []
for semilla in range(100, 110):
    retorno, pasos_aguantados = episodio(politica_ruedecillas, semilla)
    retornos_nuevos.append(retorno)

print("Retorno medio en 10 mundos nuevos:", round(sum(retornos_nuevos) / len(retornos_nuevos), 1))"""),

md(r"""**499,9** también en mundos nuevos. La política aprendida no ha memorizado cinco vientos: ha aprendido a
**mantener el palo de pie**, con cualquier viento razonable.

A esto se le llama **generalizar**: funcionar bien en situaciones nuevas, no solo en las de práctica. Es
exactamente lo que necesitaremos para el salto al mundo real (NB02): el mundo real es, para el robot, "un mundo
nuevo" más.
"""),

md(r"""## 13 · Lo que acabas de hacer (y por qué no basta para el humanoide)

Párate un momento. Con lo que has aprendido en **siete** lecciones de programación, has construido:

- Un **entorno** con su física, su azar, su recompensa y sus episodios (un "MuJoCo" de bolsillo).
- Cuatro **políticas** escritas a mano, comparadas con justicia (mismos vientos, media de varios episodios).
- Un **diagnóstico**: grabaste la trayectoria y descubriste por qué fallaba una de ellas.
- Un **algoritmo de aprendizaje**: la búsqueda aleatoria, que encontró sola una buena política.
- Una **prueba de generalización** en mundos nuevos.

Son, en miniatura, **todas** las piezas del trabajo de un ingeniero de aprendizaje por refuerzo.

Pero seamos honestos, como buenos ingenieros. ¿Serviría la búsqueda aleatoria para el humanoide? **No.** Nuestra
política tiene **2** ruedecillas, y probar 20 combinaciones al azar basta para encontrar una buena. La "máquina de
convertir" del humanoide (NB03) tiene **decenas de miles** de ruedecillas. Probar combinaciones al azar en un
espacio así es como intentar abrir una caja fuerte de decenas de miles de ruedas girándolas a ciegas: es la
**maldición de la dimensionalidad** del NB03. Nunca acabarías.

Para el humanoide hacen falta dos cosas que todavía no tenemos:

1. Una **máquina de convertir** mucho más potente que "empujar en contra de la inclinación y la velocidad": las
   **redes neuronales**.
2. Una forma **mucho más lista** de girar las ruedecillas que probar al azar: una que, en vez de dar palos de
   ciego, **calcule hacia dónde girar cada ruedecilla** para mejorar un poquito. Esa forma se apoya en unas
   matemáticas preciosas (el cálculo de las **pendientes**), y es el motor de toda la inteligencia artificial
   moderna.

Esas dos cosas son el camino que viene.
"""),

md(r"""## 14 · Resumen del proyecto

1. Un **entorno** se describe con su **ficha**: observación, acción, recompensa, cuándo termina y cuándo se trunca.
   El nuestro: 2 números de observación, 1 de acción, recompensa 1 − (inclinación/30)².
2. **`import random`** carga el **módulo** del azar; `random.uniform(a, b)` da un decimal al azar; **`random.seed`**
   fija la **semilla** para repetir el mismo azar y comparar políticas **con justicia**.
3. El entorno son funciones: `reiniciar`, `paso` (la función de paso: física + recompensa + ¿terminado?), y encima
   `episodio` y `evaluar` (retorno medio en 5 mundos).
4. Nada (~45) y azar (~43) fracasan; **solo inclinación** (~296) oscila y cae porque **le falta la velocidad** (el
   problema de la foto); **inclinación + velocidad** (~499,9) lo aguanta todo.
5. La **búsqueda aleatoria** de ruedecillas **aprende sola** una política de ~499,9 que **generaliza** a mundos
   nuevos. Funciona con 2 ruedecillas; para las decenas de miles del humanoide harán falta **redes neuronales** y una
   forma más lista de ajustar (las **pendientes**).

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Ficha del entorno** | La descripción de observación, acción, recompensa y finales de un problema. |
| **CartPole** | El clásico "carro con péndulo", primo de nuestro palo de escoba. |
| **Módulo** | Una caja de herramientas de Python que se carga con `import`. |
| **`random.uniform(a, b)`** | Un número decimal al azar entre `a` y `b`. |
| **Semilla (`random.seed`)** | El número inicial del azar del ordenador: misma semilla, mismo azar. |
| **Constante** | Una caja que no debe cambiar; por costumbre, en MAYÚSCULAS. |
| **Control clásico** | Políticas escritas a mano por ingenieros (como `-30·i − 8·v`). |
| **Búsqueda aleatoria** | Aprender probando ruedecillas al azar y quedándose con las mejores. |
| **Generalizar** | Funcionar bien en situaciones nuevas, no solo en las de práctica. |
"""),

md(r"""## 15 · Ejercicios y experimentos

Este proyecto es un **laboratorio**: lo mejor que puedes hacer es cambiar cosas y ver qué pasa. Si lo ejecutas tú,
recuerda volver a ejecutar las celdas que dependan de lo que cambies (por ejemplo, si cambias una constante,
ejecuta otra vez la celda de las constantes).

**E1.** Escribe una política `politica_al_reves` que empuje **a favor** de la inclinación (`+30 * inclinacion`) en
vez de en contra. Antes de probarla, predice: ¿aguantará más o menos que no hacer nada?

**E2.** Prueba la política a mano con la ruedecilla de inclinación a **8** (y la de velocidad a 8). ¿Qué pasa? ¿Y con
**12**? Pista: fíjate en el número que acompaña a la gravedad en la física (`10 * inclinacion`).

**E3.** Duplica el viento: cambia `VIENTO_MAXIMO` a **60**. ¿Sigue aguantando la política a mano (30 y 8)? ¿Y la de
solo inclinación?

**E4.** Ahora deja el viento en 30, pero pon un motor **débil**: `EMPUJE_MAXIMO = 15`. ¿Sigue aguantando la política
a mano? Prueba también con ruedecillas mucho más grandes, como 60 y 15. ¿Lo arreglan? ¿Por qué?

**E5.** Piensa como el robot tramposo del NB04. Si la recompensa fuera simplemente **+1 por cada paso sin caerse**
(sin el cuadrado), ¿qué diferencia habría entre una política que mantiene el palo perfectamente derecho y otra que lo
lleva siempre inclinado 25 grados, pero sin caerse? ¿Por qué usamos `1 − (inclinación/30)²`?

**E6.** Haz la búsqueda aleatoria con **100** candidatos en vez de 20. ¿Mejora mucho? ¿Por qué crees que no?

**E7.** **Reto.** Añade al final de la función `paso` un castigo por **esfuerzo**, como el del humanoide (NB04):
resta `0.0001 * empuje ** 2` a la recompensa (solo cuando no ha terminado). Repite la búsqueda aleatoria. ¿Siguen
ganando las ruedecillas grandes, o ahora el ordenador prefiere empujar con más suavidad?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
def politica_al_reves(inclinacion, velocidad):
    return 30 * inclinacion

print(round(evaluar(politica_al_reves), 1))
```

Aguanta **menos** que no hacer nada: empujar a favor de la inclinación es **ayudar a la gravedad** a tumbar el palo.
Es como mover la mano en el sentido contrario al que hay que moverla con la escoba. Si lo ejecutas, verás un retorno
medio de unos **31** puntos y episodios de unos **38** pasos: peor que el muñeco de trapo (~45 puntos, ~50 pasos).
</details>

<details>
<summary>▶ Solución E2</summary>

```python
ruedecilla_inclinacion = 8
ruedecilla_velocidad = 8
print(round(evaluar(politica_ruedecillas), 1))

ruedecilla_inclinacion = 12
print(round(evaluar(politica_ruedecillas), 1))
```

Con **8** el palo se cae en todos los episodios (retorno medio en torno a **180**); con **12** aguanta (en torno a
**499**). La razón está en la física: la gravedad empuja con `10 * inclinacion`, y la política empuja en contra con
`ruedecilla * inclinacion`. Si la ruedecilla es **menor que 10**, la gravedad gana siempre: por mucho que frenes la
velocidad, el palo acaba cayendo. Si es **mayor que 10**, el motor gana. ¡Acabas de descubrir una regla de control
por tu cuenta!
</details>

<details>
<summary>▶ Solución E3</summary>

Con `VIENTO_MAXIMO = 60`, la política a mano **sigue aguantando** los 5 episodios (~499,9): mirar la velocidad la hace
muy robusta. La de solo inclinación empeora mucho (en torno a **140** de media): con más viento, sus oscilaciones
crecen antes. Cuanto peor es el mundo, más se nota la diferencia entre una política buena y una regular.
</details>

<details>
<summary>▶ Solución E4</summary>

Con `EMPUJE_MAXIMO = 15`, la política a mano **se cae** en todos los episodios (en torno a **67** de media). Y con
ruedecillas 60 y 15 sale **exactamente lo mismo**. ¿Por qué? Porque el viento puede empujar hasta 30 y el motor solo
hasta 15: por muy bien que decida la política, **el motor no tiene fuerza suficiente** (recuerda: el empuje se limita
dentro de `paso`, así que pedir más no sirve de nada). Es la lección del NB01: **los motores no son superhéroes**. A
veces el problema no es la mente, es el cuerpo. Un buen ingeniero distingue entre "mi política es mala" y "mi robot no
puede".

(Cuando acabes, vuelve a poner `EMPUJE_MAXIMO = 40` y `VIENTO_MAXIMO = 30`.)
</details>

<details>
<summary>▶ Solución E5</summary>

Con "+1 por paso sin caerse", las dos políticas sacarían **exactamente los mismos puntos** (500), aunque una lleve el
palo perfecto y la otra torcidísimo, al borde de caerse. La recompensa no distinguiría lo que queremos (derecho) de lo
que no (torcido pero en pie): un agujero de los del NB04. Con `1 − (inclinación/30)²`, ir derecho da casi 1 punto por
paso, pero ir inclinado 25 grados da solo 1 − (25/30)² ≈ 0,31. Así la recompensa **premia lo que de verdad queremos**,
y el cuadrado castiga mucho más las inclinaciones grandes que las pequeñas.
</details>

<details>
<summary>▶ Solución E6</summary>

Cambia los dos `range(20)` por `range(100)`. El mejor retorno apenas mejora: ya con 20 candidatos llegábamos a ~499,9,
y el máximo posible es casi 500. **Cuando el problema es fácil** (2 ruedecillas, muchas combinaciones buenas), unos
pocos intentos al azar bastan. El problema de la búsqueda aleatoria no aparece aquí, sino cuando hay **muchísimas**
ruedecillas: entonces casi todas las combinaciones al azar son malas y no darías con una buena ni en un millón de
intentos.
</details>

<details>
<summary>▶ Solución E7</summary>

En la función `paso`, cambia el bloque de la recompensa por:

```python
    if terminado:
        recompensa = 0
    else:
        recompensa = 1 - (inclinacion / CAIDA) ** 2 - 0.0001 * empuje ** 2
```

Al repetir la búsqueda verás que los retornos bajan un poquito (empujar ahora cuesta puntos: el mejor queda en torno a
**495,7** en vez de 499,9) y que **el ganador cambia**: ya no es el de ruedecillas más grandes (47,9 y 6,7), sino uno
que empuja con más **suavidad**, como 32,5 y 10,9. Igual que con el humanoide: el castigo por esfuerzo anima a moverse
sin derrochar. Y si pusieras un castigo enorme (por ejemplo `0.01`), los retornos se desplomarían (el mejor candidato
no llega ni a 100 puntos, y algunos salen **negativos**): empujar costaría tanto que la recompensa ya no premiaría lo
que de verdad queremos. ¡Otro agujero de los del NB04, creado con un solo número! (Cuando acabes, deja la recompensa como estaba.)
</details>
"""),

md(r"""## 16 · Posdata: se acaba la Parte 1

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Con este proyecto **termina la Parte 1**. Mira hacia atrás: hace siete lecciones no sabías qué era `print`. Hoy has
construido un entorno de aprendizaje por refuerzo, has diagnosticado una política que fallaba mirando sus datos, y has
hecho que un ordenador **aprenda solo** a mantener un palo de pie. Con tu propio código, línea a línea.

En la **Parte 2** vamos a por las dos cosas que nos faltan para el humanoide: las **matemáticas** que permiten girar
miles de ruedecillas a la vez con inteligencia (empezando, desde cero, por las **flechas** —los vectores— y las
**pendientes**), y las herramientas de Python para manejar montones de números a toda velocidad. Todo, como siempre,
desde el principio y en gotas.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB11_proyecto_palo_de_escoba.ipynb")
    build(out, cells, title="NB11 · Proyecto: el palo de escoba")
