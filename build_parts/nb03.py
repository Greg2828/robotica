"""Construye NB03 · La mente y el bucle: observación, decisión, acción (conceptual, 0 código).

Pieza (3) del mapa. La política como caja que convierte lo que percibe en lo que
ordena. Observación (y por qué no es el estado completo; por qué hacen falta
velocidades), acción (números con signo: recta numérica), políticas escritas a
mano (termostato, escoba) vs tabla imposible vs máquina con ruedecillas
(parámetros), agente/entorno, paso y episodio, explorar vs aprovechar.

Datos verificados del Humanoid-v5:
  observación básica = 45 números (22 de postura: altura 1 + orientación 4 +
  17 ángulos; 23 de velocidades: 6 del cuerpo + 17 articulares); la versión
  completa añade extras hasta 348. Posición x,y EXCLUIDA de la observación.
  acción = 17 números entre -0,4 y +0,4 (se multiplican por la fuerza de cada motor).
  episodio termina si la altura del torso sale de 1,0–2,0 m, o a las 1000
  decisiones (15 s).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, build

cells = [

md(r"""# NB03 · La mente y el bucle: observación, decisión, acción

**Parte 0 · El terreno — Lección 4**

> Ya conoces el **cuerpo** del robot (NB01) y el **mundo de mentira** donde vive (NB02). Has
> visto que el simulador sabe de física pero **no sabe andar**: solo calcula qué pasa cuando
> los motores empujan. Falta la pieza que decide **cuánto empuja cada motor**. Hoy toca la
> pieza (3) del mapa: **la mente**, a la que llamamos **política**.

Seguimos sin código. Pero esta lección es especial: al terminarla tendrás en la cabeza el
**vocabulario completo** con el que hablan los profesionales del aprendizaje por refuerzo
(*observación, acción, agente, entorno, paso, episodio*). Son seis palabras. Las vamos a
construir una a una, con ejemplos, hasta que te parezcan obvias.

Y descubrirás algo que sorprende a casi todo el mundo: **la mente del robot, por dentro, no es
más que una máquina que convierte una lista de números en otra lista de números.** Eso es todo.
Lo difícil no es entender qué es; lo difícil es conseguir que convierta **bien**.

Vamos despacio.
"""),

md(r"""## 1 · La mente es una caja que convierte

Empecemos por la idea más sencilla posible. Imagina la mente del robot como una **caja
cerrada**:

```
                        ┌─────────────────────┐
   lo que percibe ────► │      LA MENTE       │ ────► lo que ordena
   (cómo estoy)         │    (la política)    │      (cómo muevo
                        └─────────────────────┘       los motores)
```

Por un lado **entra** información sobre cómo está el robot. Por el otro **sale** una orden para
los motores. Lo que pasa dentro de la caja es, precisamente, lo que el robot tiene que
**aprender**.

Esto puede parecer demasiado simple para algo tan difícil como andar, pero piensa en cosas que
ya conoces que funcionan igual:

- **Un termostato.** Entra: la temperatura de la habitación. Sale: encender o apagar la
  calefacción. Dentro: una regla muy simple ("si hace menos de 20 grados, enciende").
- **Tú conduciendo una bici.** Entra: lo que ves y notas (me inclino a la izquierda, viene una
  curva). Sale: lo que haces con el manillar y los pedales. Dentro: lo que aprendiste a base de
  caerte.
- **Un portero de fútbol.** Entra: por dónde viene el balón. Sale: hacia dónde se lanza. Dentro:
  años de entrenamiento.

En los tres casos hay **algo que entra**, **algo que sale** y **algo en medio que decide**. La
mente del robot es exactamente eso. Ahora vamos a ver con detalle qué entra, qué sale y qué hay
en medio.
"""),

md(r"""## 2 · Lo que entra: la observación

A lo que entra en la caja se le llama **observación**: es **todo lo que la mente sabe del
mundo en un instante**. Recuerda que en el NB01 vimos los sentidos del robot (los sensores);
la observación es, básicamente, **lo que dicen esos sensores en ese momento**.

¿Y en qué forma llega? Aquí está la primera gran idea de la lección:

> **Para la mente, la observación es una lista de números.** Nada de imágenes, nada de palabras:
> números.

¿Por qué números? Porque eso es lo que dan los sensores. El medidor de la rodilla no dice "la
rodilla está bastante doblada"; dice "45 grados". El sensor de inclinación no dice "me estoy
yendo hacia delante"; da unos números que describen cuánto y hacia dónde está inclinado el
torso.

Para nuestro humanoide de práctica, la observación básica es una lista de **45 números**:

```
   OBSERVACIÓN del humanoide (versión básica, 45 números)

   POSTURA (22 números): cómo está colocado ahora mismo
     · 1 número  → a qué altura está el torso
     · 4 números → hacia dónde está inclinado y girado el torso
     · 17 números → el ángulo de cada articulación con motor

   MOVIMIENTO (23 números): cómo de deprisa está cambiando todo
     · 6 números  → a qué velocidad se mueve y gira el torso
     · 17 números → a qué velocidad gira cada articulación
```

(Puede que te preguntes por qué hacen falta **4** números para describir hacia dónde mira el
torso. Es un truco matemático para describir giros en tres dimensiones sin que se líen; lo
veremos cuando llegue su momento. Por ahora basta con saber que "la inclinación del torso" se
describe con unos pocos números.)

Existe también una versión "completa" de la observación de este robot, con muchos datos extra
(por ejemplo, las fuerzas de los choques), que llega a **348 números**. Pero la idea es la misma:
**una lista de números que resume cómo está el robot**.
"""),

md(r"""### ¿Por qué hacen falta las velocidades? El problema de la foto

Fíjate en que casi la mitad de la observación son **velocidades**. ¿No bastaría con la postura?
Vamos a verlo con un acertijo.

Te enseño **una foto** de una pelota en el aire, a un metro del suelo:

```
            ●        ← la pelota, a 1 metro

   ─────────────────  suelo
```

Pregunta: ¿la pelota **sube** o **baja**?

No lo puedes saber. Con una sola foto, una pelota que sube y una que baja son **idénticas**. Te
falta saber **cómo se está moviendo**. Si además te digo "va a 3 metros por segundo hacia
abajo", ya lo sabes todo: está cayendo, y deprisa.

Con el robot pasa igual. Si la mente solo supiera la postura, no podría distinguir entre "estoy
recto y quieto" y "estoy recto pero cayéndome a toda velocidad hacia delante". Son la misma foto,
pero exigen decisiones **completamente distintas**. Por eso la observación incluye las
**velocidades**: son lo que convierte una foto en una película. Y recuerda la **inercia** del
NB02: lo que se está moviendo va a seguir moviéndose, así que saber la velocidad es saber **qué
va a pasar a continuación**.
"""),

md(r"""### Un detalle curioso: el robot no sabe dónde está

Hay un dato que **no** está en la observación, y es a propósito: **en qué lugar del mundo está
el robot** (si está en el centro de la habitación o tres metros más allá).

¿Por qué se quita? Porque **no importa para andar**. Andar bien es igual aquí que tres metros
más allá: el suelo es el mismo, la gravedad es la misma. Si la mente recibiera ese dato, podría
aprender cosas absurdas como "cuando estoy en este punto concreto, hago esto", y luego no
sabría andar en otro sitio. Quitándolo, la obligamos a fijarse solo en lo que de verdad
importa: **su propio cuerpo**.

Esto es una lección general muy valiosa, que usarás como profesional:

> **Elegir bien qué entra en la observación es parte del trabajo.** Darle a la mente
> información inútil la confunde; quitarle información importante la deja a ciegas.
"""),

md(r"""### La observación NO es toda la verdad

Ahora una distinción fina, pero importante. En el NB02 vimos que el simulador guarda el
**estado** del mundo: la "foto" completa y exacta, con todo. La observación **no** es lo mismo:

| | Estado | Observación |
|---|---|---|
| ¿Quién lo tiene? | El simulador (el mundo) | La mente del robot |
| ¿Qué incluye? | **Todo**, con total exactitud | Solo lo que miden los sensores |
| ¿Es perfecto? | Sí | En un robot real, no: trae **ruido** y retrasos |

Es como conducir con **niebla**. El mundo real (el estado) incluye el coche que viene a 200
metros; pero tú (la observación) solo ves lo que la niebla te deja ver. Tienes que decidir con
la información que **tienes**, no con la que **existe**.

En el simulador, la observación suele ser bastante buena. Pero en el robot real (pieza 6 del
mapa) los sensores tiemblan y se equivocan un poco. Una mente que ha aprendido a decidir solo
con observaciones perfectas puede despistarse en el mundo real. (¿Te acuerdas de la idea de
**aleatorizar el mundo** del NB02? Una de las cosas que se aleatorizan es justamente el **ruido
de los sensores**, para que la mente se acostumbre a decidir con niebla.)
"""),

md(r"""## 3 · Lo que sale: la acción

A lo que sale de la caja se le llama **acción**: la **orden que la mente da a los motores** en
ese instante. Y, como ya imaginarás:

> **Para el simulador, la acción también es una lista de números.** Uno por cada motor.

Nuestro humanoide tiene 17 motores, así que su acción es una lista de **17 números**. Cada
número le dice a un motor **cuánto retorcer su articulación y hacia qué lado** (el "par de giro"
del NB01).

¿Hacia qué lado? Aquí necesitamos una herramienta de matemáticas que quizá ya conozcas, pero que
vamos a repasar desde cero: los **números negativos**.

### Un repaso rápido: los números negativos

Imagina una línea con el cero en el medio. A la derecha, los números de siempre (1, 2, 3...).
A la izquierda, los mismos números pero con un signo menos delante (−1, −2, −3...):

```
   ◄──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────►
         −3     −2     −1      0     +1     +2     +3

          hacia un lado        nada       hacia el otro lado
```

Los números negativos sirven para decir **"lo mismo, pero en sentido contrario"**. Los conoces
de la vida diaria aunque no lo parezca: un termómetro a **−5 grados** (5 por debajo de cero), un
ascensor en la planta **−2** (dos por debajo de la calle), una cuenta del banco en **−20 euros**
(debes 20).

Para un motor funciona así:

- Un número **positivo** → retuerce hacia un lado (por ejemplo, doblar la rodilla).
- Un número **negativo** → retuerce hacia el lado contrario (estirarla).
- **Cero** → no hace fuerza.
- Cuanto más **lejos del cero** está el número (sea positivo o negativo), **más fuerte** retuerce.

En nuestro humanoide, cada uno de los 17 números va de **−0,4 a +0,4**. Y luego cada motor
multiplica ese número por su propia fuerza (por eso un mismo 0,4 es mucho par en la cadera y poco
en el hombro: ¿te acuerdas de que la cadera era 12 veces más fuerte?).

```
   ACCIÓN del humanoide (17 números, cada uno entre −0,4 y +0,4)

     abdomen:  [ +0,1   −0,3    0,0 ]
     cadera dcha.: [ −0,2   +0,4   +0,1 ]   rodilla dcha.: [ −0,4 ]
     cadera izq.:  [  0,0   −0,1   +0,3 ]   rodilla izq.:  [ +0,2 ]
     hombro dcho.: [ +0,1    0,0 ]          codo dcho.:    [ −0,1 ]
     hombro izq.:  [  0,0   +0,2 ]          codo izq.:     [  0,0 ]

   (números inventados, solo para que veas la forma)
```

Esa lista de 17 números es **todo** lo que la mente le dice al cuerpo en cada decisión. Unas 67
listas así por segundo.
"""),

md(r"""## 4 · Lo que hay dentro: la política

Ya sabemos qué entra (45 números) y qué sale (17 números). Lo que hay **dentro** de la caja, la
**regla** que convierte lo uno en lo otro, es la **política**:

```
                        ┌─────────────────────┐
   observación  ──────► │      POLÍTICA       │ ──────►  acción
   (45 números)         │  "dada esta lista,  │         (17 números)
                        │   responde esta"    │
                        └─────────────────────┘
```

> **Política = la regla que, dada una observación, decide qué acción tomar.**

Ahora la gran pregunta: **¿cómo se construye esa regla?** Vamos a ver tres maneras, de la más
ingenua a la que de verdad se usa. Entender por qué fallan las dos primeras es la mejor forma de
entender por qué funciona la tercera.
"""),

md(r"""### Manera 1: escribir las reglas a mano

Para problemas sencillos, la política se puede escribir a mano, con reglas del tipo "si pasa
esto, haz aquello". Por ejemplo, el **termostato**:

```
   POLÍTICA DEL TERMOSTATO (escrita a mano):

     si la temperatura es menor que 20 grados  →  enciende la calefacción
     si no                                     →  apágala
```

Una sola regla, y funciona perfectamente. Para la **escoba en la mano** también se puede
escribir algo razonable:

```
   POLÍTICA DE LA ESCOBA (escrita a mano):

     si la escoba se inclina hacia la derecha  →  mueve la mano a la derecha
     si se inclina hacia la izquierda          →  mueve la mano a la izquierda
     (y cuanto más deprisa se esté cayendo, más rápido mueves la mano)
```

Esto ya es una política de verdad, y con un poco de ajuste fino funciona bastante bien. De hecho,
durante décadas se controlaron muchos robots así, con reglas escritas por ingenieros muy listos
(a eso se le llama **control clásico**, y lo estudiaremos, porque sigue siendo muy útil).

¿Y para andar? Ya lo viste en el NB00: la receta tendría **millones** de reglas, cada una
dependiendo de las otras, para 45 números de entrada y 17 de salida. Nadie sabe escribirla. La
manera 1 se queda corta.
"""),

md(r"""### Manera 2: una tabla gigante con todas las respuestas

Otra idea: ¿y si hacemos una **tabla** enorme, como una chuleta, que para **cada** observación
posible diga qué acción tomar? Como el listín de un restaurante: buscas tu situación en la tabla
y lees la respuesta.

```
   | si la observación es...          | entonces la acción es...   |
   |----------------------------------|----------------------------|
   | [altura 1,3; inclinación 0; ...] | [+0,1; −0,2; ...]          |
   | [altura 1,3; inclinación 1; ...] | [+0,2; −0,1; ...]          |
   | ...                              | ...                        |
```

El problema es **el tamaño**. Hagamos una cuenta pequeñita. Supón que, para simplificar,
redondeamos cada uno de los 45 números de la observación a solo **10 valores posibles** (por
ejemplo, la rodilla solo puede estar "en el punto 1, 2, ..., 10"). ¿Cuántas situaciones
distintas habría?

- Con **1** número: 10 situaciones.
- Con **2** números: 10 × 10 = 100 situaciones (cada valor del primero con cada valor del
  segundo).
- Con **3** números: 10 × 10 × 10 = 1.000.
- Con **45** números: un 1 seguido de **45 ceros**.

Para que te hagas una idea: se calcula que el número de átomos de toda la Tierra es, más o menos, un 1 seguido de
50 ceros. Nuestra tabla tendría casi tantas filas como **átomos tiene el planeta**. Y eso
redondeando muchísimo. No hay ordenador en el mundo que pueda guardarla, ni robot que viva lo
bastante para rellenarla probando.

Este problema tiene nombre propio entre los profesionales: **la maldición de la
dimensionalidad** (cada número más que añades multiplica las situaciones posibles, y enseguida
salen cantidades imposibles). La manera 2 también se queda corta.
"""),

md(r"""### Manera 3: una máquina con ruedecillas que se ajustan

La solución que se usa hoy es una idea intermedia, y muy ingeniosa. En vez de escribir las reglas
(manera 1) o apuntar todas las respuestas (manera 2), construimos una **máquina de convertir**
números en números que tiene **muchas ruedecillas de ajuste**.

Piensa en una **mesa de mezclas** de un DJ, o en el ecualizador de un equipo de música: está
llena de ruedecillas. Si las giras de una manera, la música suena con muchos graves; si las giras
de otra, suena aguda. **La máquina es siempre la misma; lo que cambia es dónde están las
ruedecillas.**

```
                    ┌──────────────────────────────────┐
                    │   ◐   ◑   ◒   ◓   ◐   ◑   ◒  ...  │
   observación ───► │   ◓   ◐   ◑   ◒   ◓   ◐   ◑  ...  │ ───► acción
   (45 números)     │   ◒   ◓   ◐   ◑   ◒   ◓   ◐  ...  │      (17 números)
                    │        (miles de ruedecillas)     │
                    └──────────────────────────────────┘
```

Nuestra máquina de convertir es igual: según dónde estén sus ruedecillas, ante una misma
observación responderá con una acción u otra. Con las ruedecillas en una posición cualquiera,
responde tonterías (el robot convulsiona y se cae, como en el GIF del NB00). Con las ruedecillas
en la posición **justa**, responde con la acción perfecta para cada situación, y el robot anda.

A esas ruedecillas se les llama **parámetros** (o, en las máquinas que usaremos, **pesos**). Y
entonces llegamos a la frase más importante de esta lección:

> **Aprender = encontrar dónde poner las ruedecillas.** La máquina no cambia. Lo que cambia,
> intento a intento, es la posición de sus miles de ruedecillas, hasta que las respuestas son
> buenas.

Las ventajas sobre las otras dos maneras son enormes:

- No hay que escribir reglas: las ruedecillas se ajustan **solas** practicando (manera 1 ✗).
- No hay que guardar una respuesta para cada situación: la máquina **calcula** la respuesta,
  también para situaciones que nunca ha visto, parecidas a otras que sí vio (manera 2 ✗).

Las máquinas de convertir más usadas hoy se llaman **redes neuronales**. Solo el nombre, por
ahora: las construiremos desde cero, pieza a pieza, más adelante en el curso. Lo único que
necesitas saber hoy es que **son máquinas de convertir números en números, con muchas
ruedecillas ajustables**. Una red pequeña para nuestro humanoide puede tener unas **decenas de
miles** de ruedecillas.
"""),

md(r"""## 5 · Las dos partes del mundo: agente y entorno

Ahora vamos a darle nombre a los dos lados del bucle, con las palabras que usan los
profesionales.

- El **agente** es **el que decide**: la mente, la política. ("Agente" viene de "el que actúa",
  como un agente de viajes actúa por ti.)
- El **entorno** es **todo lo demás**: lo que recibe las acciones del agente y le devuelve
  observaciones.

Y aquí viene la sorpresa. ¿Qué crees que forma parte del entorno? ¿Solo el suelo y la gravedad?
No: **el cuerpo del robot también es entorno**.

```
   ┌──────────────────────────────────────────────────────────────┐
   │                         EL ENTORNO                            │
   │                                                              │
   │    el cuerpo del robot  +  el simulador (física, suelo,      │
   │    (piezas, motores,        gravedad, choques)               │
   │     sensores)                                                │
   │                                                              │
   └───────────────┬──────────────────────────────▲───────────────┘
                   │                              │
          observación (45 números)       acción (17 números)
                   │                              │
                   ▼                              │
            ┌──────────────────────────────────────┐
            │      EL AGENTE (la mente, la política) │
            └──────────────────────────────────────┘
```

¿Por qué el cuerpo es parte del entorno? Porque, **desde el punto de vista de la mente**, el
cuerpo es algo que está "ahí fuera": ella manda números a los motores y recibe números de los
sensores, igual que mandaría y recibiría números de cualquier otra cosa. La mente no "es" el
cuerpo; **lo maneja**. Es como un piloto dentro de un avión: el avión no es el piloto, es lo que
el piloto maneja.

Esta forma de partir el mundo en dos es **la misma para cualquier problema** de aprendizaje por
refuerzo: un programa que aprende a jugar al ajedrez, uno que aprende a conducir, uno que aprende
a andar. Siempre hay un agente que decide y un entorno que responde. Cambia lo que hay dentro del
entorno, pero el esquema es idéntico. Por eso todo lo que aprendas aquí te servirá también para
otras cosas.
"""),

md(r"""## 6 · El ritmo del bucle: pasos y episodios

Ya conoces el bucle. Vamos a ponerle las dos últimas palabras: cómo se mide el tiempo dentro de
él.

**Paso.** Cada vuelta del bucle (el agente recibe una observación, decide una acción, el entorno
la aplica y devuelve la siguiente observación) es **un paso**. En el NB02 vimos que la física da
pasitos de 3 milésimas; aquí, cuando hablemos del bucle del agente, "un paso" será **una
decisión** (en nuestro humanoide, 5 pasitos de física, 15 milésimas). Cuando un profesional dice
"he entrenado durante 10 millones de pasos", quiere decir 10 millones de decisiones.

**Episodio.** Es **un intento completo**, desde que el robot "nace" de pie hasta que el intento
se acaba. Como una partida de un videojuego: empieza, juegas, y en algún momento termina (o
porque pierdes, o porque se acaba el tiempo). Después se **reinicia**: el robot vuelve a aparecer
de pie, como nuevo, y empieza otro episodio.

¿Cuándo termina un episodio de nuestro humanoide? En dos casos:

- **Se ha caído.** El simulador vigila la altura del torso: si baja de **1 metro** (o sube de
  2, cosa rara), da el intento por terminado. Es como el "game over".
- **Se ha acabado el tiempo.** Si aguanta **1.000 decisiones** (15 segundos) sin caerse, el
  episodio termina igualmente y se reinicia. Es como el final del partido.

```
   EPISODIO 1:  nace ─► paso ─► paso ─► ... ─► (22 pasos) ─► se cae ✗  ─► reinicio
   EPISODIO 2:  nace ─► paso ─► paso ─► ... ─► (30 pasos) ─► se cae ✗  ─► reinicio
   ...
   EPISODIO 50.000: nace ─► paso ─► ... ─► (1.000 pasos) ─► ¡tiempo! ✓ ─► reinicio
```

¿Recuerdas el robot del GIF? De media aguantaba **22 pasos** (decisiones al azar) antes de caer.
El objetivo del entrenamiento es llegar a las 1.000 sin caerse... y además avanzando.

Entrenar, por tanto, es jugar **muchísimos** episodios seguidos (o, en el simulador, muchos a la
vez), y entre uno y otro ir ajustando las ruedecillas de la política.
"""),

md(r"""## 7 · Un dilema de la mente: probar cosas nuevas o ir a lo seguro

Queda una última idea sobre cómo decide una mente que está aprendiendo. Y la vas a reconocer
enseguida.

Imagina que vas a cenar fuera. Hay un restaurante que conoces y que **sabes** que está bien. Y hay
uno nuevo que no has probado nunca: podría ser horrible... o podría ser el mejor de tu vida.
¿Qué haces?

- Si **siempre** vas al de siempre, nunca te llevarás un chasco... pero nunca descubrirás si hay
  uno mejor.
- Si **siempre** pruebas uno nuevo, descubrirás mucho... pero cenarás mal a menudo.

Lo sensato es una mezcla: **casi siempre** vas a lo seguro, pero **de vez en cuando** pruebas algo
nuevo. Y al principio, cuando aún conoces pocos sitios, conviene probar más.

Una mente que aprende tiene **exactamente** este dilema, y tiene nombre:

- **Explorar** = probar acciones nuevas, distintas de las que cree mejores, para descubrir si hay
  algo mejor.
- **Aprovechar** = hacer lo que, hasta ahora, cree que funciona mejor.

Por eso, mientras aprende, la política del robot **no es del todo fija**: le añade un poco de
**azar** a sus acciones. Ante la misma observación, a veces mueve la rodilla un pelín más, a veces
un pelín menos. Ese pequeño temblor no es un defecto: **es su manera de explorar**. Si el temblor
resulta en algo mejor, la mente lo nota y ajusta sus ruedecillas hacia ahí.

```
   al principio del entrenamiento:   mucho azar   (explora mucho, aún no sabe nada)
   a mitad:                          algo de azar
   al final:                         casi nada    (aprovecha lo aprendido)
```

Sin explorar no se aprende nada nuevo. Sin aprovechar no se usa lo aprendido. El arte está en el
equilibrio, y volverá a salir cuando estudiemos el entrenamiento a fondo.
"""),

md(r"""## 8 · Todo junto: el bucle completo, con todas sus palabras

Vamos a volver a dibujar el bucle del NB00, pero ahora con el vocabulario de un profesional.
Léelo despacio: deberías entender **cada palabra**.

```
   ┌─────────────────────────── UN EPISODIO ───────────────────────────┐
   │                                                                    │
   │   (inicio: el robot aparece de pie)                                │
   │              │                                                     │
   │              ▼                                                     │
   │     ┌─► OBSERVACIÓN ──────►  AGENTE / POLÍTICA ──────► ACCIÓN ─┐   │
   │     │   (45 números:         (la máquina de            (17      │   │
   │     │    postura y           convertir con sus         números, │   │
   │     │    velocidades)        ruedecillas, más un       uno por  │   │
   │     │                        poco de azar para          motor)  │   │
   │     │                        explorar)                          │   │
   │     │                                                           ▼   │
   │     │                      ENTORNO                                  │
   │     │       (el cuerpo + el simulador: 5 pasitos de física)         │
   │     │                         │                                     │
   │     └────── siguiente ◄───────┤      ───► RECOMPENSA (un número:    │
   │             observación       │            ¿qué tal lo has hecho?)  │
   │                               │             → próxima lección       │
   │                               ▼                                     │
   │                ¿se ha caído o se acabó el tiempo?                   │
   │                     no → otro PASO   /   sí → FIN del episodio      │
   └─────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
            ENTRENAMIENTO: muchísimos episodios, y entre ellos
            se ajustan las ruedecillas de la política
```

Hay una flecha que todavía no hemos explicado: la **recompensa**. Es lo que le dice al agente si
lo que acaba de hacer estuvo bien o mal, y es lo que guía hacia dónde girar las ruedecillas. Sin
ella, el robot no tendría forma de saber si va mejorando. Es la pieza (4) del mapa, y la
protagonista de la próxima lección.
"""),

md(r"""## 9 · Resumen de la lección

1. La **mente** (la **política**) es una caja que convierte lo que el robot percibe en lo que
   ordena. Por dentro, **convierte una lista de números en otra lista de números**.
2. Lo que entra es la **observación**: en nuestro humanoide, 45 números de postura y velocidad.
   Las **velocidades** son imprescindibles (una foto no dice si caes o subes), y no es todo el
   **estado**: es solo lo que dicen los sensores.
3. Lo que sale es la **acción**: 17 números, uno por motor; el **signo** dice hacia qué lado
   retorcer y el **tamaño**, cuánto.
4. Escribir las reglas a mano no da para andar, y una tabla con todas las respuestas sería más
   grande que el planeta. La solución: una **máquina con ruedecillas** (parámetros); **aprender
   es encontrar dónde ponerlas**. Esas máquinas suelen ser **redes neuronales**.
5. El **agente** decide; el **entorno** (¡cuerpo incluido!) responde. Cada vuelta es un **paso**;
   cada intento completo, un **episodio**. Mientras aprende, el agente **explora** (con un poco de
   azar) y **aprovecha** lo que ya sabe.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Observación** | Lo que la mente sabe del mundo en un instante: una lista de números. |
| **Acción** | La orden de la mente a los motores: una lista de números, uno por motor. |
| **Política** | La regla que convierte cada observación en una acción. |
| **Número negativo** | Un número por debajo de cero; sirve para decir "en sentido contrario". |
| **Parámetros / pesos** | Las "ruedecillas" ajustables de la máquina de convertir. |
| **Red neuronal** | Un tipo de máquina de convertir números con muchas ruedecillas. |
| **Maldición de la dimensionalidad** | Cada dato más multiplica las situaciones posibles, hasta cantidades imposibles. |
| **Control clásico** | Controlar un robot con reglas escritas a mano por ingenieros. |
| **Agente** | El que decide (la mente). |
| **Entorno** | Todo lo demás, incluido el cuerpo: recibe acciones y devuelve observaciones. |
| **Paso** | Una vuelta del bucle: observación → acción → nueva observación. |
| **Episodio** | Un intento completo, desde que el robot nace hasta que cae o se acaba el tiempo. |
| **Explorar / aprovechar** | Probar cosas nuevas / hacer lo que ya sabes que funciona. |
"""),

md(r"""## 10 · Preguntas de comprensión

Responde con tus palabras antes de abrir cada solución.

**P1.** Describe la **política** como una caja: ¿qué entra, qué sale y qué hay dentro?

**P2.** ¿Por qué la observación incluye **velocidades** y no solo la postura? Usa el ejemplo de
la foto de la pelota.

**P3.** ¿Qué diferencia hay entre el **estado** y la **observación**? Pon un ejemplo de la vida
diaria.

**P4.** La acción de un motor es **−0,3**. ¿Qué significa el signo menos? ¿Y qué cambiaría si
fuera **+0,3**? ¿Y **−0,1**?

**P5.** Calcula: si la observación tuviera solo **4 números** y cada uno pudiera tomar 10
valores, ¿cuántas filas tendría la tabla de la "manera 2"? ¿Y con 6 números?

**P6.** Explica con la analogía de la mesa de mezclas qué significa que "aprender es encontrar
dónde poner las ruedecillas".

**P7.** ¿Por qué decimos que el **cuerpo** del robot forma parte del **entorno** y no del agente?

**P8.** ¿Qué es un **episodio**? ¿Cuáles son las dos formas en que termina un episodio de nuestro
humanoide?

**P9.** ¿Por qué se quita de la observación el dato de **en qué lugar del mundo** está el robot?

**P10.** ¿Por qué una política que está aprendiendo añade un poco de **azar** a sus acciones?
Usa el ejemplo de los restaurantes.
"""),

md(r"""<details>
<summary>▶ Solución P1</summary>

**Entra** la observación (cómo está el robot: una lista de números de postura y velocidades).
**Sale** la acción (una lista de números, uno por motor, que dice cuánto y hacia dónde retorcer
cada articulación). **Dentro** está la regla que convierte lo uno en lo otro; en la práctica, una
máquina de convertir números (una red neuronal) con muchas ruedecillas ajustables.
</details>

<details>
<summary>▶ Solución P2</summary>

Porque **una foto no dice cómo se mueven las cosas**. Una pelota quieta a un metro, una que sube y
una que baja salen idénticas en una foto. Con el robot, "estoy recto y quieto" y "estoy recto pero
cayéndome deprisa" tienen la misma postura pero exigen decisiones muy distintas. Las velocidades
convierten la foto en una película y, gracias a la inercia, dicen qué va a pasar a continuación.
</details>

<details>
<summary>▶ Solución P3</summary>

El **estado** es la descripción completa y exacta del mundo, que solo tiene el simulador. La
**observación** es lo que la mente recibe: solo lo que miden los sensores, y en un robot real con
errores (ruido) y retrasos. Ejemplo: conducir con niebla. El estado incluye el coche que viene a
200 metros; tu observación es solo lo que la niebla te deja ver, y tienes que decidir con eso.
</details>

<details>
<summary>▶ Solución P4</summary>

El **signo menos** indica el **sentido**: el motor retuerce la articulación hacia un lado (por
ejemplo, estirar la rodilla). Con **+0,3** retorcería con la **misma fuerza** pero hacia el
**lado contrario** (doblarla). Con **−0,1**, retorcería hacia el mismo lado que con −0,3, pero
**más suave**, porque está más cerca del cero.
</details>

<details>
<summary>▶ Solución P5</summary>

Con 4 números: 10 × 10 × 10 × 10 = **10.000** filas. Con 6 números: 10 × 10 × 10 × 10 × 10 × 10 =
**1.000.000** (un millón). Fíjate: añadir solo 2 números ha multiplicado la tabla por 100. Esa es
la maldición de la dimensionalidad: con los 45 números del humanoide sale un 1 seguido de 45 ceros.
</details>

<details>
<summary>▶ Solución P6</summary>

En una mesa de mezclas, el aparato es siempre el mismo; lo que cambia cómo suena la música es la
posición de sus ruedecillas. La máquina de convertir del robot es igual: siempre es la misma, pero
según dónde estén sus ruedecillas (parámetros) responde a cada observación con una acción u otra.
Al principio están en cualquier sitio y el robot hace tonterías; **aprender es ir girándolas,
intento a intento, hasta la posición en la que las respuestas son buenas** y el robot anda.
</details>

<details>
<summary>▶ Solución P7</summary>

Porque, desde el punto de vista de la mente, el cuerpo es algo "de fuera" que ella maneja: le
manda números a los motores y recibe números de los sensores, igual que haría con cualquier otra
cosa. La mente no es el cuerpo; lo pilota, como un piloto pilota un avión. Por eso cuerpo y
simulador juntos forman el entorno, y el agente es solo la parte que decide.
</details>

<details>
<summary>▶ Solución P8</summary>

Un episodio es **un intento completo**: desde que el robot aparece de pie hasta que el intento
termina, como una partida de un videojuego. En nuestro humanoide termina (1) si **se cae** (la
altura del torso baja de 1 metro) o (2) si **se acaba el tiempo** (llega a 1.000 decisiones, unos
15 segundos, sin caerse). Después se reinicia y empieza otro.
</details>

<details>
<summary>▶ Solución P9</summary>

Porque **no importa para andar**: andar bien es igual en un sitio que en otro. Si la mente
recibiera ese dato, podría aprender reglas absurdas ligadas a un lugar concreto y luego no sabría
andar en otro sitio. Quitándolo, la obligamos a fijarse en lo que de verdad importa: su propio
cuerpo. Elegir bien qué entra en la observación es parte del trabajo del profesional.
</details>

<details>
<summary>▶ Solución P10</summary>

Para **explorar**: probar acciones distintas de las que cree mejores, por si alguna resulta ser
aún mejor. Es como los restaurantes: si siempre vas al de siempre, nunca descubres uno mejor; si
siempre pruebas uno nuevo, cenas mal a menudo. Lo sensato es ir casi siempre a lo seguro
(**aprovechar**) y de vez en cuando probar algo nuevo (**explorar**), probando más al principio,
cuando aún sabes poco. El azar de la política es su forma de explorar.
</details>
"""),

md(r"""## 11 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Con esta lección ya tienes tres piezas del mapa: el **cuerpo** (NB01), el **mundo** (NB02) y la
**mente** (este NB03), unidas por el **bucle** de observación → acción. Y ya hablas el idioma de
los profesionales: agente, entorno, observación, acción, paso, episodio.

Antes de seguir con la robótica, el **NB03b** es una parada técnica: los **números** que vas a usar en todo el curso (decimales, porcentajes, potencias, notación científica...), contados con calma. Y después, en el **NB04**, llega la pieza que lo pone todo en marcha: **la recompensa**, los "puntos" que le
dicen al robot si lo está haciendo bien. Veremos cómo se diseña con los números de verdad de
nuestro humanoide... y descubriremos que es facilísimo que el robot **haga trampas** y consiga
muchos puntos sin aprender a andar. Es una de las lecciones más divertidas del curso.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB03_la_mente_y_el_bucle.ipynb")
    build(out, cells, title="NB03 · La mente y el bucle: observación, decisión, acción")
