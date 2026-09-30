"""Construye NB01 · El cuerpo del robot (100% conceptual, cero código).

Pieza (1) del mapa. Piezas rígidas, articulaciones, grados de libertad, motores.
Todo con analogías con el cuerpo humano y diagramas ASCII. Sin código.
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
el tuyo. Cuando termines, sabrás qué son las **piezas rígidas**, las **articulaciones**, los
**grados de libertad** y los **motores**, que son las cuatro palabras con las que se describe
cualquier robot que se mueve.

Vamos despacio.
"""),

md(r"""## 1 · Un robot es, sobre todo, un cuerpo

Cuando pensamos en un robot solemos pensar en "la inteligencia", en la parte que decide. Pero
antes de eso hay algo más básico y más físico: **un cuerpo**. Un montón de piezas duras
unidas entre sí que se pueden mover. Sin cuerpo no hay nada que mover, así que empezamos por
ahí.

Y resulta que **tu propio cuerpo es el mejor ejemplo de robot que existe**. Piénsalo: tienes
partes duras (los huesos), sitios donde esas partes se unen y pueden girar (las
articulaciones: rodilla, codo, hombro...) y algo que las mueve (los músculos). Un robot que
anda funciona **exactamente** con esas mismas tres cosas, solo que con otros nombres:

| En tu cuerpo | En un robot | Para qué sirve |
|---|---|---|
| Huesos | **Piezas rígidas** (o "eslabones") | Las partes duras que no se doblan |
| Articulaciones | **Articulaciones** (o "juntas") | Los sitios donde dos piezas se unen y giran |
| Músculos | **Motores** (o "actuadores") | Lo que provoca el movimiento |

Vamos a ver cada una de las tres, una por una.
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
   - la cabeza
   - el torso (la pieza grande del centro)
   - los brazos, divididos en dos tramos rígidos cada uno
     (del hombro al codo, y del codo a la mano)
   - las piernas, divididas en dos tramos rígidos cada una
     (del muslo a la rodilla, y de la rodilla al pie)
   - los pies
```

Cada uno de esos tramos es una pieza dura. Por sí solas, las piezas rígidas no hacen nada
interesante: son como los huesos de un esqueleto colgado en una clase de ciencias. Lo
interesante empieza cuando las **unimos de forma que puedan moverse**. Y eso nos lleva a las
articulaciones.
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
como la bisagra de una puerta. Tu **rodilla** es así: la doblas y la estiras, y punto. No
puedes girar la pantorrilla "de lado" a la altura de la rodilla. Tu **codo**, igual.

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

Ya tenemos piezas duras (los huesos) unidas por articulaciones (los sitios que giran). Pero
nos falta poder **contar** cuánto movimiento permite un robot. Para eso está la idea más
importante de esta lección: los **grados de libertad**.
"""),

md(r"""## 4 · Grados de libertad: contar de cuántas maneras se puede mover

Esta es la idea clave de hoy, así que vamos con calma.

Un **grado de libertad** es **una forma independiente en la que algo se puede mover**. Suena
abstracto, pero es facilísimo con ejemplos:

- Una **bisagra de puerta** tiene **1 grado de libertad**: solo puede hacer una cosa, abrirse
  y cerrarse. Un único movimiento posible.
- Tu **rodilla**: **1 grado de libertad** (doblar/estirar). Igual que la puerta.
- Tu **hombro**: unos **3 grados de libertad**, porque puede moverse de varias formas
  independientes (arriba/abajo, adelante/atrás, y girar el brazo).

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
separado. Tu brazo de verdad tiene bastantes más (alrededor de 7), por eso puedes rascarte la
espalda o llevarte comida a la boca con mil posturas distintas.
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

Un detalle: **no todas las articulaciones llevan motor**. Algunas son libres (giran solas por
la física, como cuando tu pie pivota al andar). Pero las importantes para moverse sí llevan
motor, y esas son las que la mente controla.
"""),

md(r"""## 6 · Todo junto: la anatomía de un humanoide

Juntemos las tres cosas en el robot que usaremos en el curso: un **humanoide**. Aquí está su
"radiografía", con las piezas rígidas entre corchetes `[ ]` y las articulaciones señaladas:

```
                        O   (cabeza)
                  ______|______
                 |      |      |
             hombro   [TORSO]  hombro      <- hombros (rótula, ~3 grados cada uno)
                |               |
            [brazo]          [brazo]       <- piezas rígidas
                |               |
             codo            codo          <- codos (bisagra, 1 grado)
                |               |
          [antebrazo]     [antebrazo]
                        |
                     cadera / cadera        <- caderas (rótula, ~3 grados cada una)
                 _______|________
                |                |
             [muslo]          [muslo]       <- piezas rígidas
                |                |
            rodilla          rodilla        <- rodillas (bisagra, 1 grado)
                |                |
         [pantorrilla]    [pantorrilla]
                |                |
            tobillo          tobillo        <- tobillos
                |                |
             [pie]            [pie]
```

Si sumas todos los grados de libertad de todas esas articulaciones, salen unos cuantos. El
humanoide que usaremos tiene alrededor de **17 motores**: 17 "mandos" que la mente puede mover,
17 decisiones que hay que tomar coordinadas, muchas veces por segundo, para no caerse.

Y aquí está la conexión con el NB00: cuando dijimos que el robot **ordena algo a los motores**,
nos referíamos a decidir un valor para cada uno de esos ~17 motores. Y cuando dijimos que el
robot **percibe cómo está**, nos referíamos a leer los ángulos de todas esas articulaciones, sus
velocidades y su inclinación. **El cuerpo es lo que la mente lee y lo que la mente manda.**
"""),

md(r"""## 7 · ¿Y cómo "sabe" el ordenador cómo es este cuerpo?

Buena pregunta, y la respondemos sin una sola línea de código. Toda esta descripción del
cuerpo —cuántas piezas hay, qué tamaño tiene cada una, cómo se conectan, dónde están las
articulaciones y de qué tipo, dónde hay motores— se guarda en **un fichero de texto**, una
especie de **plano de montaje**.

Es como las **instrucciones de un mueble de IKEA**: una hoja que dice "esta pieza va unida a
esta otra por aquí, y esta junta gira así". El ordenador lee ese plano y ya sabe cómo es el
robot, igual que tú, leyendo las instrucciones, sabes cómo montar la estantería.

```
   PLANO DE MONTAJE (idea, no código real):

     pieza: torso        (tamaño, peso...)
     pieza: muslo_izq     unida al torso por -> articulación: cadera_izq (rótula)
     pieza: pantorrilla_izq  unida al muslo por -> articulación: rodilla_izq (bisagra)
        con motor en la rodilla_izq
     ... y así con todo el cuerpo
```

Lo bonito es que, **cambiando ese plano**, cambias el robot: puedes hacerlo más alto, darle
otro tipo de rodilla, añadirle un brazo. En el próximo notebook veremos **quién lee ese plano
y le da vida con física**: el simulador, la pieza (2) del mapa.
"""),

md(r"""## 8 · Lo que conviene tener claro antes de seguir

Dos ideas para no olvidar, porque volverán una y otra vez:

**Un robot es rígido a tramos, no flexible.** Tú tienes una columna que se curva; muchos
robots no: son tramos duros unidos por articulaciones. Todo su movimiento sale de girar esas
articulaciones. Cuando veas a un robot "doblarse", en realidad está **girando varias
articulaciones a la vez** para dar esa impresión.

**Más motores = más difícil.** Cada motor es libertad **y** es un problema. Un robot con pocos
motores es fácil de controlar pero torpe; un humanoide con muchos es capaz de moverse como una
persona, pero coordinarlos todos sin caerse es justo el reto que vamos a resolver con
*aprendizaje por refuerzo*. No se controla a mano: se aprende.

Con esto ya entiendes **de qué está hecho** un robot que anda. En las próximas lecciones
veremos el mundo donde practica (el simulador), la mente que decide (la política) y los premios
que la guían (la recompensa).
"""),

md(r"""## 9 · Preguntas de comprensión

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
motor.
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
</details>
"""),

md(r"""## 10 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo de otra
forma.

En el **NB02** conoceremos la pieza (2) del mapa: **el mundo de mentira, el simulador**. Es
quien coge este cuerpo (el plano de montaje del apartado 7), le pone gravedad, suelo y golpes,
y lo deja "cobrar vida" para que el robot pueda practicar y caerse un millón de veces sin que
pase nada. Seguiremos sin código: primero entender bien qué es y por qué es tan útil.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB01_el_cuerpo_del_robot.ipynb")
    build(out, cells, title="NB01 · El cuerpo del robot")
