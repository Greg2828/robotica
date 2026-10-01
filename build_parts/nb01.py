"""Construye NB01 · El cuerpo del robot (100% conceptual, cero código).

Pieza (1) del mapa. Piezas rígidas, articulaciones, grados de libertad, motores,
el cuerpo suelto en el espacio (base flotante, subactuación), peso y centro de
masas, y los sentidos (sensores). Analogías con el cuerpo humano y ASCII.

Datos verificados del Humanoid-v5 de Gymnasium (el robot de práctica del curso):
  13 piezas, ~40 kg (torso 8,9 kg; pelvis 6,6; muslo 4,75; brazo 1,66...),
  17 motores = abdomen 3 + caderas 3+3 + rodillas 1+1 + hombros 2+2 + codos 1+1,
  SIN tobillo (el pie va pegado a la pantorrilla) y sin cuello (la cabeza es parte
  del torso). Junta raíz libre: 17 + 6 = 23 grados de libertad.
  Multiplicador de los motores: cadera(flexión) 300, rodilla 200, hombros/codos 25.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, build

cells = [

md(r"""# NB01 · El cuerpo del robot

**Parte 0 · El terreno — Lección 2**

> En el **NB00** viste el mapa entero: las seis piezas, la idea de *aprender probando* y un
> robot que aún no sabía andar y se caía. Hoy nos metemos dentro de la **primera pieza del
> mapa: el robot**. Antes de enseñarle a moverse, hay que entender **de qué está hecho**.

Igual que en el NB00, aquí **no hay nada de código**. No toques el ordenador. Solo vamos a
mirar cómo es un robot por dentro, comparándolo todo el rato con el cuerpo que mejor conoces:
el tuyo. Y de nuevo te pediré algún experimento con tu propio cuerpo.

Cuando termines, sabrás qué son las **piezas rígidas**, las **articulaciones**, los **grados
de libertad**, los **motores** y los **sensores**. Y entenderás tres ideas que explican, por
fin, *por qué* andar es tan difícil para un robot: que **no está atornillado a nada**, que
todo depende de dónde está su **centro de masas**, y que solo sabe de sí mismo lo que le
cuentan sus **sentidos**.

Es una lección más larga que la anterior. Vamos despacio; puedes leerla en dos o tres ratos.
"""),

md(r"""## 1 · Un robot es, sobre todo, un cuerpo

Cuando pensamos en un robot solemos pensar en "la inteligencia", en la parte que decide. Pero
antes de eso hay algo más básico y más físico: **un cuerpo**. Un montón de piezas duras
unidas entre sí que se pueden mover. Sin cuerpo no hay nada que mover, así que empezamos por
ahí.

Y resulta que **tu propio cuerpo es el mejor ejemplo de robot que existe**. Piénsalo: tienes
partes duras (los huesos), sitios donde esas partes se unen y pueden girar (las
articulaciones: rodilla, codo, hombro...), algo que las mueve (los músculos) y algo que te
cuenta cómo está todo (los sentidos). Un robot que anda funciona **exactamente** con esas
mismas cuatro cosas, solo que con otros nombres:

| En tu cuerpo | En un robot | Para qué sirve |
|---|---|---|
| Huesos | **Piezas rígidas** (o "eslabones") | Las partes duras que no se doblan |
| Articulaciones | **Articulaciones** (o "juntas") | Los sitios donde dos piezas se unen y giran |
| Músculos | **Motores** (o "actuadores") | Lo que provoca el movimiento |
| Sentidos | **Sensores** | Lo que le dice al robot cómo está |

Vamos a ver cada una de las cuatro, una por una.
"""),

md(r"""## 2 · Las piezas rígidas: los "huesos" del robot

Una **pieza rígida** es una parte del robot que **no se dobla ni se estira**: es dura, mantiene
su forma pase lo que pase. Se llama "rígida" precisamente por eso. También la verás llamada
**eslabón** (como los eslabones de una cadena, que son piezas duras enganchadas unas a otras).

Piensa en tu brazo. De la mano al codo hay un tramo que no se dobla por el medio: es rígido
(ahí dentro está el hueso del antebrazo). Del codo al hombro, otro tramo rígido (el hueso del
brazo). Tu brazo **no** es una manguera flexible; es una serie de **tramos duros** unidos por
sitios que giran.

Un robot humanoide es igual. Sus piezas rígidas típicas son:

```
   - el torso (la pieza grande del centro; en muchos robots la cabeza
     va pegada a él, como una sola pieza)
   - la cintura y la pelvis (la "caja" de donde salen las piernas)
   - los brazos, divididos en dos tramos rígidos cada uno
     (del hombro al codo, y del codo a la mano)
   - las piernas, divididas en dos tramos rígidos cada una
     (el muslo, de la cadera a la rodilla, y la pantorrilla, de la rodilla abajo)
   - los pies
```

Cada pieza rígida tiene, además, dos propiedades que importarán muchísimo:

- **Una forma y un tamaño.** Es lo que choca con el suelo o con otras piezas.
- **Un peso.** Las piezas no pesan lo mismo: el torso es lo más pesado y una mano casi no
  pesa nada. (Enseguida veremos por qué importa tanto *dónde* está el peso.)

Por sí solas, las piezas rígidas no hacen nada interesante: son como los huesos de un
esqueleto colgado en una clase de ciencias. Lo interesante empieza cuando las **unimos de
forma que puedan moverse**. Y eso nos lleva a las articulaciones.
"""),

md(r"""## 3 · Las articulaciones: los sitios donde el robot se dobla

Una **articulación** (o "junta") es el punto donde **dos piezas rígidas se unen y pueden
girar** una respecto de la otra. Es lo que permite el movimiento. Sin articulaciones, el robot
sería una estatua.

Otra vez tu cuerpo lo explica solo: tu **rodilla** es una articulación (une el muslo con la
pantorrilla y les permite doblarse), tu **codo** es otra, tu **hombro** otra, tu **tobillo**
otra. Cada una une dos piezas duras y les deja moverse de cierta manera.

Y aquí viene un detalle importante: **no todas las articulaciones se mueven igual**. Hay,
sobre todo, dos tipos, y los conoces bien:

**Tipo bisagra (como una puerta).** Gira solo en **un** sentido, hacia delante y hacia atrás,
como la bisagra de una puerta. Tu **rodilla** es así (casi del todo): la doblas y la estiras,
y punto. No puedes girar la pantorrilla "de lado" a la altura de la rodilla. Tu **codo**, igual.

```
   articulación de bisagra (rodilla, codo):

        pieza de arriba
             |
            [·]  <- gira solo en un sentido
           /
          /          (como abrir y cerrar una puerta)
        pieza de abajo
```

**Tipo rótula (como una palanca de videojuego).** Gira en **muchos** sentidos a la vez. Tu
**hombro** es así: puedes mover el brazo arriba, abajo, a los lados y girarlo. Tu **cadera**,
igual. Es como la palanca (el "joystick") de un mando, que se inclina en cualquier dirección.

```
   articulación de rótula (hombro, cadera):

             [O]  <- gira en varios sentidos
            / | \     a la vez
           /  |  \
      (arriba, abajo, a los lados, girar...)
```
"""),

md(r"""### Las articulaciones tienen topes

Haz la prueba: estira el brazo del todo e intenta doblar el codo **hacia el otro lado**. No
puedes (¡y no fuerces!). Tu codo tiene un **tope**: gira, pero solo dentro de un margen. Lo
mismo tu rodilla: se dobla hacia atrás mucho, pero hacia delante no pasa de recta.

Los robots también tienen topes en sus articulaciones, y por la misma razón: para que la pieza
no se rompa ni choque consigo misma. Por ejemplo, la rodilla del humanoide de práctica que
usaremos se puede doblar unos **160 grados** hacia atrás, pero hacia delante no pasa de estar
prácticamente recta, igual que la tuya. A esos márgenes se les llama **límites** o **rango**
de la articulación.

(Si no tienes claro qué es un "grado" al medir un giro: imagina una vuelta completa sobre ti
mismo; eso son 360 grados. Media vuelta, 180. Un cuarto de vuelta —una esquina, como la de un
folio—, 90. Lo veremos con calma cuando lleguen las matemáticas.)

Ya tenemos piezas duras (los huesos) unidas por articulaciones (los sitios que giran), con sus
topes. Pero nos falta poder **contar** cuánto movimiento permite un robot. Para eso está la
idea más importante de esta lección: los **grados de libertad**.
"""),

md(r"""## 4 · Grados de libertad: contar de cuántas maneras se puede mover

Esta es la idea clave de hoy, así que vamos con calma.

Un **grado de libertad** es **una forma independiente en la que algo se puede mover**.
"Independiente" quiere decir que puedes hacerla **sin tener que hacer las otras**. Suena
abstracto, pero es facilísimo con ejemplos:

- Una **bisagra de puerta** tiene **1 grado de libertad**: solo puede hacer una cosa, abrirse
  y cerrarse. Un único movimiento posible.
- Tu **rodilla**: **1 grado de libertad** (doblar/estirar). Igual que la puerta.
- Tu **hombro**: unos **3 grados de libertad**, porque puede moverse de varias formas
  independientes (arriba/abajo, adelante/atrás, y girar el brazo sobre sí mismo).

> **La regla:** los grados de libertad de un robot entero son **la suma** de los grados de
> libertad de todas sus articulaciones. Es, básicamente, **cuántas cosas distintas puede
> decidir mover el robot al mismo tiempo**.

Contémoslo con un brazo de robot muy sencillo, de solo dos articulaciones de bisagra (un
hombro que sube y baja, y un codo que dobla):

```
   hombro (bisagra, 1 grado)  ──►  puede subir/bajar el brazo entero
        \
         \  [tramo rígido]
          \
         codo (bisagra, 1 grado) ──►  puede doblar el antebrazo
            \
             \ [tramo rígido]
              \
             (mano)

   TOTAL del brazo = 1 + 1 = 2 grados de libertad
```

Ese brazo tan simple tiene **2 grados de libertad**: dos "mandos" que se pueden mover por
separado. Tu brazo de verdad tiene bastantes más (alrededor de 7, contando hombro, codo y
muñeca), por eso puedes rascarte la espalda o llevarte comida a la boca con mil posturas
distintas.
"""),

md(r"""### Un truco de los robots: la rótula es "tres bisagras apiladas"

Fabricar una rótula de verdad (una bola dentro de un hueco, como tu cadera) es complicado, y
además es difícil ponerle motores. Así que los robots suelen hacer un truco muy ingenioso:
**ponen tres bisagras seguidas, muy juntitas, cada una girando en una dirección distinta**.

```
   una rótula "de verdad"            la versión robot: 3 bisagras juntas

          [O]                          bisagra 1: inclina adelante/atrás
        gira en                        bisagra 2: inclina a los lados
       cualquier                       bisagra 3: gira como una peonza
       dirección
                                       → juntas, cubren casi todo lo que
                                         hace la rótula
```

La ventaja es enorme: cada bisagra lleva **su propio motor**, y así cada grado de libertad
tiene un "mando" separado. Por eso, cuando más adelante leas que la cadera de un robot tiene
"3 articulaciones", no te extrañes: es una rótula construida con tres bisagras. Cada una cuenta
como **1 grado de libertad**, y suman 3.
"""),

md(r"""### Por qué los grados de libertad importan tanto

Cuantos **más** grados de libertad tiene un robot, **más ágil** es: puede adoptar más posturas
y moverse de más maneras. Suena bien... pero tiene un precio, y es un precio que pagaremos todo
el curso:

> Cada grado de libertad es **una decisión más** que hay que tomar, muchas veces por segundo.
> Más grados de libertad = un cuerpo más capaz, pero **muchísimo más difícil de controlar**.

Piénsalo así: mantener en equilibrio una puerta (1 grado de libertad) es trivial. Mantener en
equilibrio y coordinar un cuerpo humanoide con **decenas** de grados de libertad, todos a la
vez, sin caerse, es de lo más difícil que existe. Por eso andar es tan complicado: no es un
mando, son decenas de mandos que hay que mover **coordinados y sin parar**.

Y "coordinados" es la palabra clave. Las decisiones **no son independientes en su efecto**:
si doblas la cadera, cambia dónde queda el pie; si mueves un brazo, cambia el equilibrio de
todo el cuerpo. Es como tocar el piano con 17 dedos: no basta con que cada dedo sepa moverse,
tienen que moverse **juntos y en el momento justo**.

Esta tensión —más capacidad pero más difícil de controlar— es una de las grandes ideas de la
robótica. Guárdala.
"""),

md(r"""## 5 · Los motores: lo que de verdad mueve las piezas

Ya tenemos el esqueleto (piezas rígidas + articulaciones), pero un esqueleto no se mueve solo.
Hace falta algo que **empuje**. En ti son los **músculos**; en un robot son los **motores**
(su nombre técnico es **actuadores**, es decir, "los que actúan / mueven").

Un motor se coloca **en una articulación** y su trabajo es hacerla girar. Cuando la "mente"
del robot decide "quiero doblar la rodilla", lo que hace en realidad es **darle una orden al
motor de la rodilla**.

¿Y qué "empuje" da exactamente un motor? Da lo que se llama un **par de giro** (o "torque",
que quizá hayas oído). No te asustes por la palabra; la idea es de andar por casa:

> **Par de giro = fuerza para hacer girar algo.** Es lo que notas al abrir un bote de mermelada
> muy apretado, o al girar el pomo de una puerta dura: no empujas en línea recta, **retuerces**.
> Cuanto más fuerte retuerces, más "par" aplicas.

```
   abrir un bote apretado:            un motor en la rodilla:

        ↻ retuerces la tapa               ↻ el motor retuerce la
        con fuerza                          articulación para doblar
                                            o estirar la pierna
   eso es "par de giro"               mismo concepto
```

Un par de giro grande mueve la articulación con fuerza y rápido; uno pequeño, con suavidad. El
robot controla sus movimientos, en el fondo, **decidiendo cuánto par aplica cada motor en cada
instante**. Eso es, ni más ni menos, lo que significaba en el NB00 "ordenar algo a los motores".
"""),

md(r"""### Los motores no son superhéroes

Dos detalles sobre los motores que conviene saber desde ya:

**1. Cada motor tiene un máximo.** Igual que tú no puedes levantar un coche, un motor no puede
dar más par del que da de sí. Si la mente le pide más, se queda en su máximo. Esto importa:
a veces el robot "sabe" lo que tendría que hacer, pero no tiene fuerza para hacerlo.

**2. No todos los motores son igual de fuertes.** Igual que en tu cuerpo los músculos de las
piernas son muchísimo más potentes que los del brazo (sostienen todo tu peso), en un robot
humanoide los motores de las piernas son los más fuertes. En el humanoide de práctica del
curso, el motor que dobla la cadera es **12 veces más fuerte** que el del hombro. Tiene
sentido: las piernas cargan con todo el cuerpo; los brazos casi solo se balancean.

¿Y todas las articulaciones llevan motor? En un robot bien hecho, las importantes sí. Pero en
los modelos sencillos de práctica a veces se **simplifica** el cuerpo quitando articulaciones
para que sea más fácil de entrenar. Lo verás enseguida en nuestro humanoide: **no tiene
tobillos**.
"""),

md(r"""## 6 · Todo junto: la anatomía de nuestro humanoide de práctica

Juntemos todo en el robot con el que practicaremos durante buena parte del curso: un
**humanoide simplificado**, muy usado en todo el mundo para aprender e investigar. Es el mismo
que viste desplomarse en el GIF del NB00. Aquí está su "radiografía":

```
                          (O)            cabeza: va pegada al torso (sin cuello)
                    ┌──────┴──────┐
     hombro (2) ────┤   [TORSO]   ├──── hombro (2)
          │         └──────┬──────┘          │
      [brazo]              │             [brazo]
          │           abdomen (3)            │
      codo (1)             │             codo (1)
          │          [cintura y                │
    [antebrazo]       pelvis]            [antebrazo]
                     ┌─────┴─────┐
              cadera (3)       cadera (3)
                 │                 │
              [muslo]           [muslo]
                 │                 │
             rodilla (1)       rodilla (1)
                 │                 │
           [pantorrilla]     [pantorrilla]
                 │                 │
              [pie] <── pegado: SIN tobillo ──> [pie]

   [ ]  = pieza rígida          (n) = articulación con n motores
```

Vamos a contar sus motores, uno por uno:

| Zona | Articulaciones | Motores |
|---|---|---|
| Abdomen (la "cintura") | 1 rótula hecha con 3 bisagras | 3 |
| Caderas | 2 rótulas, de 3 bisagras cada una | 3 + 3 = 6 |
| Rodillas | 2 bisagras | 1 + 1 = 2 |
| Hombros | 2 articulaciones de 2 bisagras | 2 + 2 = 4 |
| Codos | 2 bisagras | 1 + 1 = 2 |
| **Total** | | **17** |

**17 motores**: 17 "mandos" que la mente puede mover, 17 decisiones que hay que tomar
coordinadas, unas 67 veces por segundo, para no caerse. El robot entero pesa unos **40 kilos**
(más o menos como un chaval de 12 o 13 años), y casi la mitad de ese peso está en el torso y
la pelvis.

**¿Y los tobillos?** Este modelo no los tiene: el pie va pegado a la pantorrilla, como si
llevara una bota de escayola. Es una simplificación para que sea más fácil de entrenar. Los
humanoides de verdad (los de las empresas del NB00) **sí** tienen tobillos con motor, muñecas
y a veces hasta dedos, y llegan a tener **20, 30 o más** motores. Empezaremos por el sencillo
y subiremos.
"""),

md(r"""### La conexión con el bucle del NB00

Ahora puedes entender el bucle del NB00 con mucha más precisión:

- Cuando dijimos que el robot **ordena algo a los motores**, nos referíamos a decidir **un
  valor de par para cada uno de esos 17 motores**, en cada instante.
- Cuando dijimos que el robot **percibe cómo está**, nos referíamos a leer los ángulos de sus
  articulaciones, lo deprisa que se mueven, si está inclinado... (enseguida veremos con qué
  "sentidos" lo lee).

> **El cuerpo es lo que la mente lee y lo que la mente manda.**

Pero aún nos falta la pieza que de verdad explica por qué todo esto es tan difícil. Y es una
pieza que... no tiene motor.
"""),

md(r"""## 7 · La gran trampa: el robot no está atornillado a nada

Esta es, probablemente, **la idea más importante de toda la lección**. Vamos a llegar a ella
comparando dos robots.

**Robot A: un brazo de fábrica.** Seguro que has visto vídeos de fábricas de coches con
brazos robóticos naranjas soldando o pintando. Fíjate en un detalle: **su base está atornillada
al suelo**. El brazo no se puede caer. Si quiere poner la mano en un punto, mueve sus motores y
listo: la mano llega allí. Todo lo que se mueve en él lo mueve un motor.

**Robot B: nuestro humanoide.** No está atornillado a nada. Está **suelto**, de pie, apoyado en
el suelo. Y eso cambia todo.

Piensa en su torso. ¿Qué cosas puede hacer el torso **en el espacio**, como un todo? Puede:

```
   MOVERSE (desplazarse)                  GIRAR (cambiar su orientación)

   1. adelante / atrás                    4. inclinarse adelante / atrás
   2. a la izquierda / a la derecha          (como al hacer una reverencia)
   3. arriba / abajo                      5. inclinarse a un lado / al otro
                                             (como una torre que se ladea)
                                          6. girar sobre sí mismo
                                             (como una peonza)
```

Son **6 grados de libertad más**: tres de moverse y tres de girar. Son los mismos 6 que tiene
cualquier objeto que suelta por el aire, como una pelota o un avión. Y aquí viene la trampa:

> **Ninguno de esos 6 tiene motor.** No hay ningún motor que empuje el torso hacia delante, ni
> que lo enderece cuando se inclina. El robot **no puede mover su torso directamente**.

Entonces, ¿cómo avanza? ¿cómo se endereza? **Solo de una forma: empujando el suelo con los
pies.** El robot mueve sus piernas, los pies empujan contra el suelo, el suelo "devuelve el
empujón", y eso es lo que mueve el cuerpo entero. Si el pie no toca el suelo (o resbala), el
robot no tiene **nada** con lo que corregirse.
"""),

md(r"""### Piénsalo como un astronauta

Imagina a un astronauta flotando en mitad de la estación espacial, sin tocar ninguna pared.
Puede mover los brazos y las piernas todo lo que quiera... pero **no puede ir a ninguna
parte**. Necesita agarrarse a algo o empujar una pared para desplazarse.

Un robot humanoide está en una situación parecida: puede mover sus 17 articulaciones a su
antojo, pero su cuerpo como un todo **solo se mueve gracias a lo que empuje contra el suelo**.
Y el suelo solo puede empujar mientras el pie está apoyado.

Hagamos la cuenta completa del humanoide:

```
     17   grados de libertad CON motor   (las articulaciones)
   +  6   grados de libertad SIN motor   (el cuerpo suelto en el espacio)
   ────
     23   grados de libertad en total
```

Cuando un robot tiene **más grados de libertad que motores**, se dice que está
**subactuado** ("sub" = por debajo; tiene menos actuadores de los que haría falta para mover
todo directamente). El brazo de fábrica no lo está; el humanoide, sí. Y esa es la razón de
fondo por la que el brazo de fábrica es "fácil" y el humanoide es dificilísimo:

| | Brazo de fábrica | Humanoide |
|---|---|---|
| ¿Atornillado al suelo? | Sí | No, está suelto |
| ¿Se puede caer? | No | Sí, constantemente |
| ¿Todo tiene motor? | Sí | No: faltan 6 grados de libertad |
| ¿Cómo mueve su cuerpo? | Directamente, con sus motores | **Indirectamente**, empujando el suelo |

Guarda esta palabra, **subactuado**, porque es la explicación más precisa de por qué un bípedo
es difícil. Lo de la escoba del NB00 era la versión intuitiva; esta es la versión de experto.
"""),

md(r"""## 8 · Dónde está el peso: el centro de masas

Ahora una idea de física que lo une todo. Tranquilo: no hay fórmulas, solo un experimento.

### Experimento 1: equilibra una regla en tu dedo

Coge una regla (o un lápiz largo) y ponla **tumbada** sobre tu dedo índice, buscando el punto
en el que se queda en equilibrio sin caer hacia ningún lado. Lo encontrarás: más o menos en el
medio. Ese punto mágico se llama **centro de masas** (también lo oirás como "centro de
gravedad").

> **Centro de masas = el punto donde podrías imaginar que se concentra todo el peso de un
> objeto.** Si lo sostienes justo por ahí, se queda en equilibrio.

Ahora pega una goma de borrar (o una moneda) en una punta de la regla y vuelve a buscar el
equilibrio. ¿Qué pasa? El punto de equilibrio **se ha movido hacia la goma**. Cuando el peso no
está repartido igual, el centro de masas se va hacia donde hay más peso.

### Tu cuerpo también tiene centro de masas

Cuando estás de pie, tu centro de masas está más o menos **a la altura del ombligo, un poco por
debajo, por dentro del cuerpo**. Y, lo más importante: **se mueve cuando te mueves**. Si
levantas los brazos, sube un poco. Si te inclinas hacia delante, se va hacia delante. Si
levantas una pierna hacia un lado, se va hacia ese lado.
"""),

md(r"""### La base de apoyo y la regla de oro del equilibrio

Ahora la segunda mitad de la idea. Mira el suelo bajo tus pies. La zona que ocupan tus pies, más
el hueco que queda entre ellos, se llama **base de apoyo** (o "polígono de apoyo"):

```
    visto desde arriba:

    de pie, pies separados          a la pata coja

    ┌───────────────────┐
    │ ▓▓▓          ▓▓▓  │               ┌─────┐
    │ ▓▓▓          ▓▓▓  │               │ ▓▓▓ │
    │ ▓▓▓   base   ▓▓▓  │               │ ▓▓▓ │  <- base minúscula:
    │ ▓▓▓  grande  ▓▓▓  │               │ ▓▓▓ │     solo un pie
    └───────────────────┘               └─────┘
     pie izq.      pie der.
```

Y ahora, **la regla de oro del equilibrio quieto**:

> **Mientras la vertical de tu centro de masas (la línea que baja de él hasta el suelo) caiga
> DENTRO de la base de apoyo, no te caes. En cuanto cae FUERA, te caes.**

```
       centro de masas                      centro de masas
            (●)                                    (●)
             │  línea                                \  te has inclinado
             │  vertical                              \  demasiado...
             │                                         │
             ▼                                         ▼
       ┌───────────┐                       ┌───────────┐
       │   base    │  ← cae DENTRO         │   base    │ ✗ ← cae FUERA
       └───────────┘    estable            └───────────┘      ¡te caes!
```

Esto explica de golpe muchas cosas del NB00:

- Por qué el **coche** es estable: base enorme (las cuatro ruedas) y centro de masas bajo.
- Por qué la **pata coja** es difícil: base minúscula; un pelín de inclinación y el centro de
  masas se sale.
- Por qué un robot **tiene que mover el cuerpo antes de levantar un pie**: para llevar su centro
  de masas encima del pie que se queda en el suelo.
"""),

md(r"""### Experimento 2: la pared (este es famoso)

Ponte de **lado** junto a una pared, con el hombro, la cadera y el lateral del pie **pegados a
la pared**. Ahora intenta levantar la pierna que está **lejos** de la pared, sin despegarte.

¿Puedes? Casi seguro que **no**. Y ahora sabes por qué: para levantar esa pierna, tu cuerpo
necesita desplazar el centro de masas hacia el pie que se queda en el suelo, es decir, hacia la
pared... y la pared no te deja. Sin poder llevar el centro de masas encima del pie de apoyo, la
regla de oro dice que te caerías, así que tu cuerpo, muy listo, ni lo intenta.

**Lo que esto significa para el robot.** Antes de dar un paso, el robot tiene que **desplazar su
peso** encima de la pierna de apoyo. Tú lo haces sin pensar (cuando andas, tu cuerpo se balancea
un poquito de lado a lado). El robot tendrá que **descubrirlo** practicando.

Y ahora une las dos ideas de esta lección: el robot no puede mover su centro de masas
directamente (está **subactuado**); solo puede moverlo **empujando el suelo con los pies**... y
solo con los pies que estén apoyados, dentro de una base de apoyo que, al andar, a ratos es de un
solo pie. Esa es la dificultad de andar, explicada del todo.

(Una nota para más adelante: la regla de oro es para estar **quieto**. Al andar, ya viste en el
NB00 que el cuerpo se deja caer un poco a propósito. Ahí la regla se "estira" de formas más
sutiles, que veremos cuando lleguemos a la física del movimiento.)
"""),

md(r"""## 9 · Los sentidos del robot: los sensores

Recuerda el experimento de la pata coja con los ojos cerrados: sin información, no hay buen
equilibrio. Un robot necesita **sentidos** que le digan cómo está. A esos "sentidos" se les
llama **sensores**: aparatos que **miden algo** y le pasan el número al cerebro del robot.

Lo bonito es que los sensores importantes de un robot que anda tienen un primo hermano en tu
cuerpo. Vamos con los cuatro principales:

**1. Medidores de ángulo en cada articulación** (en inglés, *encoders*). Dicen **cuánto está
doblada cada articulación** y a qué velocidad gira. En ti: cierra los ojos y tócate la nariz.
Lo consigues porque **sabes dónde está tu brazo sin mirarlo**. Ese sentido "oculto" se llama
**propiocepción** (sentir la postura del propio cuerpo).

**2. El sensor de inclinación** (en inglés, *IMU*, unas siglas que significan "unidad de medida
inercial"). Va en el torso y dice **si el cuerpo está inclinado, hacia dónde, y si está girando
o acelerando**. En ti: el **oído interno**, un órgano dentro del oído que funciona como un nivel
de burbuja. Es el que se marea cuando das muchas vueltas. Para un bípedo es el sensor más
importante: es el que nota "¡me estoy cayendo!".

**3. Sensores de contacto o de fuerza en los pies.** Dicen **si el pie toca el suelo y con
cuánta fuerza** apoya. En ti: la **planta del pie**, que nota el suelo y cómo se reparte tu peso
entre el talón y los dedos.

**4. Cámaras y otros sensores de distancia.** Son los "ojos": ven el terreno, los obstáculos,
los escalones. En ti, obviamente, los ojos.

| Sensor del robot | Qué mide | Su "primo" en tu cuerpo |
|---|---|---|
| Medidores de ángulo (encoders) | Cuánto está doblada cada articulación | Propiocepción |
| Sensor de inclinación (IMU) | Inclinación, giros y sacudidas del torso | Oído interno |
| Sensores de los pies | Si el pie apoya y con cuánta fuerza | Planta del pie |
| Cámaras | El terreno y los obstáculos | Ojos |
"""),

md(r"""### Un dato que sorprende: muchos robots andan "a ciegas"

¿Sabes cuál de esos cuatro sentidos **no** es imprescindible para andar por suelo llano? Las
**cámaras**. Muchos de los robots que aprenden a andar con aprendizaje por refuerzo lo hacen
**solo con los tres primeros**: ángulos, inclinación y pies. Igual que tú puedes andar por tu
casa a oscuras (con cuidado), notando el suelo y tu propio cuerpo.

Las cámaras se añaden cuando hace falta **anticipar** el terreno (ver un escalón antes de
tropezar). Al principio del curso trabajaremos sin ellas.

Y un aviso que conecta con el NB02: **los sensores reales no son perfectos**. Dan medidas con
pequeños errores y temblores (lo que se llama **ruido**), a veces llegan con un poco de
retraso... Igual que tu oído interno se confunde después de dar vueltas. El robot tiene que
aprender a decidir bien **aunque su información no sea perfecta**. Volveremos a esto cuando
hablemos del salto al mundo real.

Con esto ya tenemos el **cuerpo completo**: piezas, articulaciones, motores... y los sentidos con
los que el robot se entera de cómo está.
"""),

md(r"""## 10 · ¿Y cómo "sabe" el ordenador cómo es este cuerpo?

Buena pregunta, y la respondemos sin una sola línea de código. Toda esta descripción del
cuerpo —cuántas piezas hay, qué tamaño y qué peso tiene cada una, cómo se conectan, dónde
están las articulaciones y de qué tipo, con qué topes, dónde hay motores y cómo de fuertes
son, y qué sensores lleva— se guarda en **un fichero de texto**, una especie de **plano de
montaje**.

Es como las **instrucciones de un mueble de IKEA**: una hoja que dice "esta pieza va unida a
esta otra por aquí, y esta junta gira así". El ordenador lee ese plano y ya sabe cómo es el
robot, igual que tú, leyendo las instrucciones, sabes cómo montar la estantería.

```
   PLANO DE MONTAJE (idea, no código real):

     pieza: torso            peso 9 kg
       pieza: muslo_izq       peso 4,75 kg
         unida al torso por -> articulación: cadera_izq (3 bisagras)
         pieza: pantorrilla_izq
           unida al muslo por -> articulación: rodilla_izq (bisagra, tope 160 grados)
     motor en la rodilla_izq:   fuerza máxima tal
     sensor de inclinación:     en el torso
     ... y así con todo el cuerpo
```

Fíjate en que el plano tiene forma de **árbol**: el torso es el tronco; de él cuelgan las
piernas y los brazos; de cada muslo cuelga su pantorrilla... Cada pieza está "colgada" de su
pieza madre. Esa forma de árbol la volverás a ver muchas veces.

Lo bonito es que, **cambiando ese plano**, cambias el robot: puedes hacerlo más alto, darle
otro tipo de rodilla, añadirle tobillos. En el próximo notebook veremos **quién lee ese plano
y le da vida con física**: el simulador, la pieza (2) del mapa.
"""),

md(r"""## 11 · Lo que conviene tener claro antes de seguir

Tres ideas para no olvidar, porque volverán una y otra vez:

**Un robot es rígido a tramos, no flexible.** Tú tienes una columna que se curva; muchos
robots no: son tramos duros unidos por articulaciones. Todo su movimiento sale de girar esas
articulaciones. Cuando veas a un robot "doblarse", en realidad está **girando varias
articulaciones a la vez** para dar esa impresión.

**Más motores = más difícil.** Cada motor es libertad **y** es un problema. Un robot con pocos
motores es fácil de controlar pero torpe; un humanoide con muchos es capaz de moverse como una
persona, pero coordinarlos todos sin caerse es justo el reto que vamos a resolver con
*aprendizaje por refuerzo*. No se controla a mano: se aprende.

**El cuerpo se mueve "de rebote".** El robot está suelto (subactuado): no puede empujar su
propio cuerpo, solo el suelo. Para no caerse tiene que mantener su centro de masas sobre su
base de apoyo, y para enterarse de cómo va solo cuenta con lo que le digan sus sensores.

Con esto ya entiendes **de qué está hecho** un robot que anda. En las próximas lecciones
veremos el mundo donde practica (el simulador), la mente que decide (la política) y los premios
que la guían (la recompensa).
"""),

md(r"""## 12 · Resumen de la lección

1. Un robot tiene **piezas rígidas** (huesos), **articulaciones** (que giran, con topes),
   **motores** (músculos) y **sensores** (sentidos).
2. Las articulaciones son sobre todo **bisagras** (1 grado de libertad) o **rótulas** (3), y los
   robots construyen las rótulas con **tres bisagras apiladas**.
3. Los **grados de libertad** cuentan de cuántas formas independientes se puede mover algo; más
   grados = más ágil, pero mucho más difícil de controlar.
4. Nuestro humanoide de práctica tiene **17 motores** y pesa unos 40 kg. Además está **suelto**:
   tiene 6 grados de libertad sin motor, así que está **subactuado** y solo se mueve empujando
   el suelo.
5. Para no caerse quieto, la vertical de su **centro de masas** tiene que caer dentro de su
   **base de apoyo**; y se entera de cómo está gracias a sus **sensores** (ángulos,
   inclinación, pies).

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Pieza rígida / eslabón** | Parte dura del robot que no se dobla (como un hueso). |
| **Articulación / junta** | Unión entre dos piezas que les deja girar. |
| **Bisagra** | Articulación que gira en un solo sentido (rodilla, codo). |
| **Rótula** | Articulación que gira en varios sentidos (hombro, cadera). |
| **Límites / rango** | Los topes hasta donde puede girar una articulación. |
| **Grado de libertad** | Una forma independiente en la que algo se puede mover. |
| **Motor / actuador** | Lo que hace girar una articulación (como un músculo). |
| **Par de giro / torque** | La "fuerza de retorcer" que da un motor. |
| **Subactuado** | Que tiene más grados de libertad que motores; no puede moverlo todo directamente. |
| **Centro de masas** | El punto donde se puede imaginar concentrado todo el peso. |
| **Base de apoyo** | La zona del suelo que ocupan los pies (y el hueco entre ellos). |
| **Sensor** | Aparato que mide algo y se lo cuenta al cerebro del robot. |
| **IMU** | El sensor de inclinación del torso (como tu oído interno). |
| **Ruido** | Los pequeños errores y temblores de las medidas de un sensor. |
"""),

md(r"""## 13 · Preguntas de comprensión

Responde con tus palabras antes de abrir cada solución.

**P1.** ¿Qué es una **pieza rígida** y qué parte de tu cuerpo se le parece?

**P2.** Explica la diferencia entre una articulación de **bisagra** y una de **rótula**, con
un ejemplo de tu cuerpo de cada tipo.

**P3.** ¿Cuántos **grados de libertad** tiene una bisagra de puerta? ¿Y por qué tu hombro
tiene más?

**P4.** Se dice que "más grados de libertad es un arma de doble filo". ¿Cuál es la ventaja y
cuál el inconveniente?

**P5.** Un motor de una articulación aplica un "par de giro". Explica qué es eso con un ejemplo
cotidiano.

**P6.** Une cada parte del robot con su equivalente en tu cuerpo: pieza rígida, articulación,
motor, sensor de inclinación (IMU).

**P7.** ¿Por qué un brazo robótico de fábrica es mucho más fácil de controlar que un humanoide,
aunque tengan un número parecido de motores?

**P8.** El humanoide tiene 17 motores pero 23 grados de libertad. ¿De dónde salen los 6 que
faltan y qué tienen de especial?

**P9.** Explica con la idea del **centro de masas** y la **base de apoyo** por qué no puedes
levantar la pierna en el experimento de la pared.

**P10.** ¿Por qué muchos robots pueden aprender a andar sin cámaras? ¿Qué sentidos usan en su
lugar?

**P11.** Una persona propone construir un rótula para la cadera del robot "con tres bisagras".
¿Es una locura? ¿Cuántos motores llevaría?
"""),

md(r"""<details>
<summary>▶ Solución P1</summary>

Una pieza rígida (o eslabón) es una parte del robot que **no se dobla ni se estira**: mantiene
su forma. Se parece a un **hueso** (por ejemplo, el hueso del antebrazo, el tramo del codo a la
muñeca, que es duro y no se dobla por el medio).
</details>

<details>
<summary>▶ Solución P2</summary>

Una **bisagra** gira solo en **un** sentido (adelante/atrás), como la bisagra de una puerta;
ejemplo en tu cuerpo: la **rodilla** o el **codo**. Una **rótula** gira en **muchos** sentidos
a la vez, como la palanca de un mando; ejemplo en tu cuerpo: el **hombro** o la **cadera**.
</details>

<details>
<summary>▶ Solución P3</summary>

Una bisagra de puerta tiene **1 grado de libertad**: solo puede abrirse y cerrarse, un único
movimiento. Tu hombro tiene más (unos 3) porque puede moverse de varias formas independientes a
la vez: subir/bajar el brazo, llevarlo adelante/atrás y girarlo. Cada una de esas formas cuenta
como un grado de libertad.
</details>

<details>
<summary>▶ Solución P4</summary>

**Ventaja:** más grados de libertad = más agilidad, el robot puede adoptar más posturas y
moverse de más maneras (como una persona). **Inconveniente:** cada grado de libertad es una
decisión más que hay que tomar, coordinada con las demás y muchas veces por segundo, así que el
robot se vuelve **mucho más difícil de controlar**. Por eso un humanoide es capaz pero
complicadísimo de manejar.
</details>

<details>
<summary>▶ Solución P5</summary>

El par de giro es la **fuerza para hacer girar algo** (no para empujarlo en línea recta, sino
para **retorcerlo**). Ejemplo cotidiano: abrir un bote de mermelada muy apretado o girar un
pomo duro: cuanto más fuerte retuerces, más par aplicas. Un motor hace lo mismo con una
articulación: la retuerce para doblarla o estirarla.
</details>

<details>
<summary>▶ Solución P6</summary>

- Pieza rígida ↔ **hueso**
- Articulación ↔ **articulación** (rodilla, codo, hombro...)
- Motor ↔ **músculo**
- Sensor de inclinación (IMU) ↔ **oído interno**
</details>

<details>
<summary>▶ Solución P7</summary>

Porque el brazo de fábrica está **atornillado al suelo**: no se puede caer y **todo** lo que se
mueve en él lo mueve directamente un motor. El humanoide está **suelto**: tiene 6 grados de
libertad extra (su cuerpo moviéndose y girando en el espacio) que **no tienen motor**. Solo
puede controlarlos de forma indirecta, empujando el suelo con los pies, y solo mientras los pies
estén apoyados. Está **subactuado**, y eso lo hace muchísimo más difícil.
</details>

<details>
<summary>▶ Solución P8</summary>

Salen de que el robot está **suelto en el espacio**: su torso puede **desplazarse** en 3
direcciones (adelante/atrás, izquierda/derecha, arriba/abajo) y **girar** de 3 formas
(inclinarse adelante/atrás, ladearse, girar como una peonza). 3 + 3 = 6. Lo especial es que
**ninguno tiene motor**: el robot no puede moverlos directamente, solo de rebote, empujando el
suelo con los pies. 17 con motor + 6 sin motor = 23.
</details>

<details>
<summary>▶ Solución P9</summary>

Para quedarte sobre una sola pierna, la vertical de tu **centro de masas** tiene que caer dentro
de la **base de apoyo**, que pasa a ser solo el pie que queda en el suelo. Para conseguirlo,
tienes que desplazar el cuerpo hacia ese pie, es decir, hacia la pared. Pero la pared te lo
impide. Si levantaras la pierna sin desplazarte, tu centro de masas quedaría fuera de la base y
te caerías hacia fuera; por eso tu cuerpo no te deja hacerlo.
</details>

<details>
<summary>▶ Solución P10</summary>

Porque para andar por suelo llano no hace falta *ver* el terreno: basta con **sentir el propio
cuerpo**. Usan los **medidores de ángulo** de las articulaciones (como tu propiocepción), el
**sensor de inclinación** del torso (como tu oído interno) y los **sensores de los pies** (como
la planta del pie). Igual que tú puedes andar por casa a oscuras. Las cámaras sirven para
anticipar obstáculos y escalones.
</details>

<details>
<summary>▶ Solución P11</summary>

No es ninguna locura: es justo **lo que se hace** en robótica. Una rótula de verdad es difícil
de fabricar y de motorizar, así que se ponen **tres bisagras seguidas**, cada una girando en una
dirección distinta (adelante/atrás, a los lados, y como una peonza). Llevaría **tres motores**,
uno por bisagra, y la cadera tendría 3 grados de libertad. Es exactamente como están hechas las
caderas de nuestro humanoide de práctica.
</details>
"""),

md(r"""## 14 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo de otra
forma.

En el **NB02** conoceremos la pieza (2) del mapa: **el mundo de mentira, el simulador**. Es
quien coge este cuerpo (el plano de montaje del apartado 10), le pone gravedad, suelo y golpes,
y lo deja "cobrar vida" para que el robot pueda practicar y caerse un millón de veces sin que
pase nada. Allí aprenderás también un poco más de física: qué es exactamente una fuerza, por qué
las cosas que se mueven tienden a seguir moviéndose, y cómo hace un ordenador para "calcular el
futuro". Seguiremos sin código: primero entender bien qué es y por qué es tan útil.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB01_el_cuerpo_del_robot.ipynb")
    build(out, cells, title="NB01 · El cuerpo del robot")
