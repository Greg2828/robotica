"""Construye NB03 · La mente y el bucle: observación, decisión, acción (conceptual; código solo en la Práctica en MuJoCo, ya escrito).

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

Práctica en MuJoCo (medido, arranque exacto sin ruido): datos.ctrl = acción (17, ±0,4);
obs = qpos[2:] + qvel = 45. Episodio (5 pasitos/decisión, cae si torso < 1 m):
muñeco de trapo 40 pasos (0,60 s); azar semilla 0 → 22 (semillas 0-9: 17-38, media ~25);
tenso +0,4 → 47, −0,4 → 12; reglas ctrl = clip(−5·ángulo) → 92 (1,38 s); k=0,5 → 93, k=20 → 76.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB03 · La mente y el bucle: observación, decisión, acción

**Parte 0 · El terreno — Lección 4**

> Ya conoces el **cuerpo** del robot (NB01) y el **mundo de mentira** donde vive (NB02). Has
> visto que el simulador sabe de física pero **no sabe andar**: solo calcula qué pasa cuando
> los motores empujan. Falta la pieza que decide **cuánto empuja cada motor**. Hoy toca la
> pieza (3) del mapa: **la mente**, a la que llamamos **política**.

Seguimos sin escribir código (solo al final, en la **Práctica en MuJoCo**, ejecutarás código ya
escrito para darle una mente al humanoide). Pero esta lección es especial: al terminarla tendrás en la cabeza el
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

md(r"""## 11 · 🛠 Práctica en MuJoCo: dale una mente al humanoide

En esta lección has aprendido seis palabras: **observación**, **acción**, **política**, **agente**,
**entorno**, **paso** y **episodio** (bueno, siete). Ahora vas a verlas **funcionando** dentro de
MuJoCo. Vas a mirar con tus propios ojos los 45 números que percibe el humanoide y los 17 que
ordena, vas a montar el **bucle** percibir → decidir → actuar, y vas a probar **cuatro mentes
distintas** (cuatro políticas) para ver cuánto aguanta de pie con cada una.

Como en las prácticas anteriores, el código ya está escrito: ejecutas, miras y cambias algún número.
No hace falta que entiendas cada símbolo; debajo de cada celda te cuento qué hace con palabras.
"""),

md(r"""### Paso 1 · La acción: 17 números en `datos.ctrl`

Cargamos el humanoide, como en el NB00. En los **datos** (el estado de ahora mismo, NB02) hay un
sitio especial para las órdenes de los motores: **`datos.ctrl`** ("ctrl" de *control*). Es la
**acción** del apartado 3: una lista con un número por motor. Lo que escribas ahí es lo que
cada motor intentará hacer en los siguientes pasitos de física.

La celda enseña cuántos números hay, qué vale cada uno ahora (todos a cero: nadie ha decidido
nada todavía) y entre qué valores puede moverse cada uno.
"""),

code(r"""import mujoco
import numpy as np
import taller

modelo, datos = taller.cargar("humanoide")

print("Número de motores:", modelo.nu)
print("La acción ahora mismo (datos.ctrl):")
print(datos.ctrl)
print("Cada número puede ir de", modelo.actuator_ctrlrange[0][0], "a", modelo.actuator_ctrlrange[0][1])"""),

md(r"""Ahí están los **17 números** del apartado 3, todos a **0** (ningún motor hace fuerza), y su
margen: de **−0,4 a +0,4**. Recuerda la recta numérica: el signo dice hacia qué lado retuerce el
motor, y la distancia al cero, cuánto.

(La primera línea, `import numpy as np`, trae una herramienta para trabajar con listas de números;
la conocerás a fondo en el NB15. Hoy solo la usamos por dentro.)
"""),

md(r"""### Paso 2 · La observación: los 45 números que percibe

En el apartado 2 te conté que la observación del humanoide son **45 números**: 22 de postura y 23
de velocidades, **sin** la posición x, y en el mundo. Vamos a comprobarlo.

MuJoCo guarda la postura completa en `datos.qpos` (la "q" es la letra que usan los físicos para las
posiciones) y las velocidades en `datos.qvel`. La celda:

1. cuenta cuántos números hay en cada una;
2. fabrica la observación igual que la fabrica el programa del humanoide: la postura **quitándole
   los dos primeros números** (la x y la y: dónde está en el suelo), seguida de las velocidades;
3. y enseña el primer número de la observación, que es la **altura del torso**.
"""),

code(r"""print("Números de postura (qpos):    ", len(datos.qpos))
print("Números de velocidad (qvel):  ", len(datos.qvel))

observacion = np.concatenate([datos.qpos[2:], datos.qvel])   # postura sin x,y + velocidades

print("Números de la observación:    ", len(observacion))
print("Altura del torso (el primero):", observacion[0], "metros")"""),

md(r"""**24** de postura, menos los 2 de la posición en el suelo, son **22**; más **23** de velocidades:
**45**. Exactamente lo del apartado 2. Y el primero es la altura del torso, **1,4 metros**: el robot
acaba de nacer, de pie.

(¿Por qué hay 24 de postura y solo 23 de velocidades, si deberían ir a la par? Por los famosos
**4 números** de la inclinación del torso: para *estar* inclinado hacen falta 4, pero para decir
*a qué velocidad gira* bastan 3. Una rareza de las matemáticas de los giros que verás más
adelante.)
"""),

md(r"""### Paso 3 · El bucle de un episodio

Ahora montamos el **bucle** del apartado 8, con sus palabras. Esta celda no pone nada en marcha
todavía: solo **define** (deja preparada) una receta llamada `episodio` que hace esto:

```
   el robot nace de pie
   repetir hasta 1.000 veces (cada vuelta es un PASO):
       la POLÍTICA mira el estado y escribe su ACCIÓN en datos.ctrl   ← percibir y decidir
       el ENTORNO avanza 5 pasitos de física (15 milésimas)            ← actuar
       si el torso ha bajado de 1 metro → fin del EPISODIO (se ha caído)
   contar cuántos pasos ha aguantado
```

Los 5 pasitos por decisión y el "se cae si el torso baja de 1 metro" son las reglas reales del
humanoide de Gymnasium (apartado 6). La política es lo único que cambiará entre una prueba y otra:
se la pasamos a la receta como si fuera una pieza intercambiable.
"""),

code(r"""def episodio(politica):
    modelo, datos = taller.cargar("humanoide")          # nace de pie
    for paso in range(1, 1001):                          # como mucho 1.000 pasos
        politica(modelo, datos)                          # percibe y decide: escribe datos.ctrl
        for _ in range(5):                               # el entorno actúa: 5 pasitos de física
            mujoco.mj_step(modelo, datos)
        if datos.qpos[2] < 1.0:                          # ¿el torso ha bajado de 1 metro?
            break                                        # se ha caído: fin del episodio
    print(f"Aguanta {paso} pasos ({datos.time:.2f} segundos)")"""),

md(r"""### Paso 4 · Mente número 1: no hacer nada (el muñeco de trapo)

La política más sencilla del mundo: ignorar la observación y dejar los 17 motores a **cero**.
El robot no hace ninguna fuerza; se desmaya, como en el vídeo del NB00.
"""),

code(r"""def muneco_de_trapo(modelo, datos):
    datos.ctrl[:] = 0            # los 17 motores a cero

episodio(muneco_de_trapo)"""),

md(r"""**40 pasos**, 0,6 segundos. Apúntalo: es la marca que deben batir las demás mentes.
"""),

md(r"""### Paso 5 · Mente número 2: al azar

La política del GIF del NB00: en cada paso, 17 números **al azar** entre −0,4 y +0,4. Es pura
**exploración** sin nada de **aprovechar** (apartado 7). Para que el azar sea repetible usamos una
**semilla**: un número que fija qué tirada de dados sale (misma semilla, mismos dados).
"""),

code(r"""dados = np.random.default_rng(0)       # la semilla es el 0

def al_azar(modelo, datos):
    datos.ctrl[:] = dados.uniform(-0.4, 0.4, size=17)   # 17 números al azar

episodio(al_azar)"""),

md(r"""**22 pasos**: aguanta la mitad que sin hacer nada. Moverse sin saber es **peor** que no moverse:
las sacudidas al azar lo tiran al suelo antes que la gravedad sola. Con otras semillas sale entre
17 y 38 pasos (lo he probado con las semillas 0 a 9: unos 25 de media), pero casi siempre por
debajo de los 40 del muñeco de trapo.
"""),

md(r"""### Paso 6 · Mente número 3: tenso

Una política "de ingeniero novato": todos los motores **siempre** con la misma orden, **+0,4**, la
máxima. Sigue sin mirar la observación; es una mente que decide siempre lo mismo pase lo que pase.
"""),

code(r"""def tenso(modelo, datos):
    datos.ctrl[:] = 0.4          # los 17 motores a tope, siempre igual

episodio(tenso)"""),

md(r"""**47 pasos**: un poquito más que el muñeco de trapo, pero se cae igual. Apretar todo a la vez
no es equilibrarse. Ninguna de estas tres mentes **percibe**: ninguna lee la observación antes de
decidir. Les falta la mitad del bucle.
"""),

md(r"""### Paso 7 · Mente número 4: reglas escritas a mano (la que sí percibe)

Ahora una política de la **manera 1** del apartado 4, como la de la escoba: reglas escritas a mano
que **miran** la observación. La regla es una sola, para cada uno de los 17 motores:

```
   si mi articulación se ha doblado hacia un lado, empujo hacia el lado contrario,
   y cuanto más doblada esté, más fuerte empujo.
```

En números: **orden = −5 × ángulo**. El **signo menos** hace que empuje *en contra* del doblez
(recta numérica: si el ángulo es positivo, la orden sale negativa, y al revés). El 5 dice "cuánto
de fuerte" reacciona: es una **ruedecilla** (un parámetro, apartado 4). Y como los motores solo
admiten de −0,4 a +0,4, la orden se recorta a ese margen.

Las dos primeras líneas son "fontanería": buscan dónde está, dentro de `datos.qpos`, el ángulo
de la articulación que mueve cada motor (cada motor sabe cuál es la suya).
"""),

code(r"""juntas = modelo.actuator_trnid[:, 0]            # qué articulación mueve cada motor
sitio = modelo.jnt_qposadr[juntas]               # dónde está su ángulo dentro de qpos

def reglas(modelo, datos):
    angulos = datos.qpos[sitio]                  # PERCIBE: los 17 ángulos
    orden = -5 * angulos                         # DECIDE: empujar en contra del doblez
    datos.ctrl[:] = np.clip(orden, -0.4, 0.4)    # ACTÚA: recortado al margen de los motores

episodio(reglas)"""),

md(r"""**92 pasos** (1,38 segundos): **más del doble** que el muñeco de trapo, con una sola regla y
una sola ruedecilla. En cuanto la mente **percibe** y reacciona, el robot dura más. ¡Pero sigue
cayéndose! Mantener las articulaciones rectas no es lo mismo que mantener el equilibrio: el cuerpo
entero, tieso, acaba volcando como un árbol talado. Para equilibrarse de verdad habría que mirar
más cosas (la inclinación del torso, las velocidades...) y combinarlas con muchísimo tino. Esa
receta ya no hay quien la escriba a mano: por eso existe la **manera 3**, la máquina con
ruedecillas que se ajustan solas.

Veámoslo. Primero el robot tieso de las reglas:
"""),

code(r"""modelo, datos = taller.cargar("humanoide")
taller.video(modelo, datos, segundos=2.5, control=reglas, nombre="nb03_reglas");"""),

md(r"""Fíjate en cómo cae **en bloque**, casi sin doblarse: las reglas mantienen cada articulación
recta, pero nadie le ha enseñado a mover los pies para no volcar. Ahora, para comparar, la mente
"tensa", con todos los motores a tope:
"""),

code(r"""modelo, datos = taller.cargar("humanoide")
taller.video(modelo, datos, segundos=2.5, control=tenso, nombre="nb03_tenso");"""),

md(r"""Se dobla por la cintura, levanta los brazos y se va al suelo retorcido: todos los motores
apretando a la vez, sin mirar, lo doblan sobre sí mismo. Dos mentes, dos formas distintas de fracasar. (Un detalle técnico: en los vídeos, la mente
decide en **cada** pasito de física, no cada 5; para estas mentes tan simples da casi igual.)
"""),

md(r"""### Tus retos

**Reto 1.** En el Paso 6, cambia `0.4` por `-0.4` (todos los motores a tope, pero hacia el **otro**
lado). ¿Aguanta más o menos? ¿Por qué crees que el signo importa tanto?

**Reto 2.** En el Paso 5, cambia la semilla `0` por otro número (1, 2, 3...). ¿Cambia cuánto aguanta?
¿Hay alguna semilla que bata al muñeco de trapo?

**Reto 3.** En el Paso 7, la ruedecilla vale `5`. Prueba `0.5` y `20`. ¿Más fuerte es siempre mejor?

**Reto 4 (para pensar).** ¿Qué parte del código del Paso 3 es el **agente** y qué parte es el
**entorno**? ¿Dónde está la **acción**? ¿Y la **observación**?

<details>
<summary>▶ Solución Reto 1</summary>

¡Aguanta **muchísimo menos**: solo **12 pasos** (0,18 segundos)! El signo cambia el **sentido** de
cada motor: con +0,4 las articulaciones se doblan hacia un lado que, por casualidad, mantiene las
piernas más o menos debajo del cuerpo; con −0,4 se doblan hacia el lado contrario y el robot se
pliega de golpe. Mismo tamaño de orden (0,4), sentido opuesto, resultado completamente distinto:
por eso la acción necesita números **con signo**.
</details>

<details>
<summary>▶ Solución Reto 2</summary>

Sí cambia: con las semillas de la 0 a la 9 sale **22, 24, 31, 21, 27, 25, 38, 17, 21 y 21** pasos.
Ninguna llega a los 40 del muñeco de trapo (la que más se acerca, la 6, se queda en 38). El azar
puro casi nunca gana a no hacer nada, y aun cuando tiene suerte, no aguanta ni un segundo.
</details>

<details>
<summary>▶ Solución Reto 3</summary>

Con `0.5` aguanta **93 pasos** (casi igual que con 5) y con `20`, **76** (¡menos!). Más fuerte **no**
siempre es mejor: reaccionar con demasiada fuerza hace que el robot sobrecorrija. Elegir el valor de
la ruedecilla tiene su arte... y con 17 motores y muchas ruedecillas a la vez, hacerlo a mano es
imposible. Eso es justo lo que hará el **entrenamiento**: girar las ruedecillas por nosotros.
</details>

<details>
<summary>▶ Solución Reto 4</summary>

El **agente** es la `politica` (la línea `politica(modelo, datos)`): la única parte que decide. El
**entorno** es todo lo demás: el modelo con su cuerpo y `mj_step`, que aplica la física (¡el cuerpo
es entorno, apartado 5!). La **acción** es `datos.ctrl`, lo que escribe la política. La
**observación** es lo que la política lee de `datos` antes de decidir (en la mente de las reglas,
`datos.qpos[sitio]`, los ángulos). Y cada vuelta del `for` es un **paso**; todo el `for`, un
**episodio**.
</details>

### Qué has aprendido de MuJoCo hoy

- **`datos.ctrl`** es la **acción**: un número por motor (`modelo.nu` = 17), cada uno en su margen
  (`modelo.actuator_ctrlrange`, de −0,4 a +0,4). Escribir ahí es mandar órdenes a los motores.
- **`datos.qpos`** (posturas) y **`datos.qvel`** (velocidades) son el **estado**; la **observación**
  del humanoide se fabrica con ellos (45 números, sin la x y la y).
- El **bucle de control**: la política escribe `datos.ctrl`, `mj_step` avanza la física, se
  comprueba si el episodio ha terminado... y otra vez.
- Una **política** es una pieza intercambiable: cambiándola, el mismo robot en el mismo mundo se
  comporta de forma completamente distinta.
- `taller.video(..., control=politica)` graba lo que hace el robot con esa mente.

En la práctica del NB03b leerás los **números de MuJoCo** con ojos nuevos: en qué unidades mide
(metros, kilos, segundos... y radianes), cuánto pesa cada pieza del humanoide y cuánto mide.
"""),

md(r"""## 12 · Posdata

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
