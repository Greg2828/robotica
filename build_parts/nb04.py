"""Construye NB04 · Premios y castigos: la recompensa y sus trampas (conceptual; código solo en la Práctica en MuJoCo, ya escrito).

Pieza (4) del mapa. Qué es la recompensa, "dice qué, no cómo", recompensa vs
retorno (y una pizca de descuento), el problema del mérito, escasa vs densa
(frío/caliente), la recompensa REAL del Humanoid-v5 ingrediente a ingrediente
(con el cuadrado explicado desde cero), cuentas con escenarios, la trampa
escondida en la propia recompensa (quedarse quieto ≈ 80 % de andar), trampas
famosas (hackear la recompensa, Goodhart) y cómo se defiende un profesional.

Datos verificados (gymnasium Humanoid-v5, código fuente + 20 episodios medidos):
  recompensa por paso = 5 (si torso entre 1 y 2 m)
                      + 1,25 × velocidad hacia delante del centro de masas (m/s)
                      − 0,1 × suma de (acción de cada motor)²
                      − 5e-7 × suma de (fuerzas de choque)², con tope 10
  máx. 1000 pasos. Esfuerzo máximo posible por paso: 0,1×17×0,4² = 0,272.
  Azar: ~21 pasos, ~98 puntos. Motores a cero ("muñeco de trapo"): ~40 pasos,
  ~198 puntos. Quieto ideal 1000 pasos: 5000. Andar a 1 m/s sin esfuerzo: 6250.

Práctica en MuJoCo (receta propia = Gymnasium sin ruido, 195,49): trapo 40 pasos 195,5
(+195 +6,14 −0 −5,66); azar semillas 0-9: 78-184, media ~117; sin premio de pie: desplome 0,5
vs plancha (qvel[0]=2) 59,6; con +5: 195,5 vs 189,6; empate en p≈4,55 (p=4: 156,5 vs 163,6);
empujón 1: 36,2 / 191,2; tenso +0,4: 47 pasos, 239,9, esfuerzo −12,78 = 0,272/paso.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB04 · Premios y castigos: la recompensa y sus trampas

**Parte 0 · El terreno — Lección 5**

> Ya tienes el **cuerpo** (NB01), el **mundo** (NB02) y la **mente** con su bucle (NB03).
> La mente es una máquina con ruedecillas, y aprender es encontrar dónde ponerlas. Pero
> queda la pregunta del millón: **¿cómo sabe la mente hacia dónde girar las ruedecillas?**
> ¿Cómo distingue un intento bueno de uno malo? La respuesta es la pieza (4) del mapa: **la
> recompensa**.

Esta es, probablemente, la lección **más importante para tu futuro trabajo**. Los ingenieros
de robótica pasan una parte enorme de su tiempo diseñando recompensas, y una parte todavía
mayor descubriendo que el robot **les ha hecho trampa**.

Seguimos sin escribir código (al final, en la **Práctica en MuJoCo**, ejecutarás la recompensa ya
escrita sobre el humanoide), pero hoy sí habrá **cuentas**: sumas, multiplicaciones y una operación
nueva (elevar al cuadrado), explicada desde cero. Usaremos la recompensa **de verdad** de
nuestro humanoide de práctica, con sus números reales. Y verás algo muy curioso: en esa
recompensa hay una trampa escondida que casi nadie ve a la primera.

Vamos despacio.
"""),

md(r"""## 1 · ¿Qué es una recompensa?

Recuerda el perro del NB00: cuando hace el truco bien, le das una golosina; cuando no, nada.
Repitiendo, aprende. La golosina es la **recompensa**.

Para un robot, la recompensa es aún más sencilla:

> **La recompensa es un número que el entorno le da al agente después de cada paso**, y que
> dice **qué tal ha estado** lo que acaba de pasar. Número alto = bien. Número bajo (o negativo)
> = mal.

Es como la **puntuación de un videojuego**. Cada cosa que haces suma o resta puntos: coger una
moneda, +10; que te den un golpe, −50. Tú no ves "la intención" del diseñador del juego; solo ves
los puntos, y aprendes a jugar para conseguir más.

Fíjate en el detalle: es **un solo número**. No es una explicación ("has movido mal la rodilla
izquierda porque..."). Es solo "+5", o "−2". El robot tiene que **deducir por su cuenta** qué hizo
bien o mal a partir de esos números. Como un perro, que no entiende tus palabras, solo si hubo
golosina o no.

Y la palabra completa del bucle queda así:

```
   observación ──► AGENTE ──► acción ──► ENTORNO ──► nueva observación
                                            │
                                            └──► RECOMPENSA (un número)
```
"""),

md(r"""## 2 · La recompensa dice QUÉ, no CÓMO

Esta es la idea que hace que el aprendizaje por refuerzo sea tan potente (y tan traicionero).

Cuando diseñas una recompensa, **no le dices al robot cómo andar**. No le dices "dobla la
rodilla así" ni "balancea los brazos". Solo le dices **qué resultado te gusta**: "me gusta que
avances", "me gusta que no te caigas". El **cómo** lo tiene que descubrir él, explorando.

Es como un entrenador que le dice a un atleta "quiero que bajes de 12 segundos en los 100
metros", sin decirle cómo correr. El atleta prueba, ajusta, y encuentra su manera.

Esto tiene una ventaja enorme: el robot puede descubrir formas de moverse **mejores** que las
que se nos ocurrirían a nosotros, porque no está atado a nuestras ideas. Pero tiene un peligro
igual de enorme, y es el tema central de esta lección:

> **El robot aprende lo que premias, no lo que querías premiar.** Si tu recompensa tiene un
> agujero, el robot lo encontrará. No por malicia: simplemente busca puntos, y un agujero es
> una fuente de puntos como cualquier otra.

Antes de ver agujeros, necesitamos tres ideas más sobre cómo funciona la recompensa.
"""),

md(r"""## 3 · Lo que de verdad persigue el robot: la suma de todo el episodio

El robot recibe una recompensa **en cada paso**. Pero ¿qué intenta conseguir? ¿El máximo de
puntos **en este paso**? No. Intenta conseguir el máximo de puntos **sumando todo el episodio**.
A esa suma se le llama **retorno**:

> **Retorno = la suma de todas las recompensas de un episodio**, desde que el robot nace hasta
> que termina el intento.

```
   paso:          1     2     3     4     5    ...
   recompensa:   +5    +5    +6    +4    +5    ...
                  └─────┴─────┴─────┴─────┴──── todo sumado = RETORNO
```

¿Por qué importa la diferencia? Porque a veces, para conseguir **más puntos en total**, hay que
aceptar **menos puntos ahora**. Lo conoces de la vida:

- **Ahorrar.** Si gastas la paga el primer día, disfrutas hoy. Si ahorras unas semanas, te
  compras algo mucho mejor. Menos ahora, más en total.
- **Estudiar.** Una tarde estudiando es menos divertida que una tarde jugando. Pero el examen
  sale mejor.

Un robot que solo pensara en el paso actual sería un desastre: por ejemplo, nunca doblaría una
rodilla para preparar un paso, porque en ese instante no gana nada con ello. Un robot que piensa
en el retorno sí: "si ahora preparo la pierna, dentro de un rato avanzaré más".

**Una pizca de "descuento".** En la práctica se usa un pequeño matiz: los puntos lejanos en el
futuro **cuentan un poquito menos** que los cercanos. Igual que tú prefieres 10 euros hoy que 10
euros dentro de un año. Así el robot no se obsesiona con un futuro muy lejano e incierto. A ese
matiz se le llama **descuento**, y lo veremos con números cuando estudiemos el entrenamiento.
Por ahora quédate con la idea: **el robot persigue el total, con más peso para lo cercano**.
"""),

md(r"""## 4 · El problema del mérito: ¿quién tuvo la culpa?

Ahora un problema muy profundo, y muy humano.

Imagina que el robot se cae en el **paso 40**. ¿Qué decisión tuvo la culpa? ¿La del paso 39,
justo antes de caer? Probablemente no: en el paso 39 ya estaba tan torcido que no había nada que
hacer. Quizá el error de verdad fue en el **paso 25**, cuando apoyó mal el pie, o en el **paso
12**, cuando empezó a inclinarse sin corregir. La consecuencia (la caída) llega **mucho después**
que la causa.

Lo ves en el fútbol constantemente. Se marca un gol. ¿Mérito de quién? ¿Del que la empuja a la
red? Sí, pero también del que dio el pase, y del que recuperó el balón 30 segundos antes en
defensa. La recompensa (el gol) llega al final; el mérito está repartido hacia atrás.

```
   paso:   ... 12 ......... 25 ................ 39   40
               │            │                    │    │
          empieza a     apoya mal            ya no   ¡CAE!  ← el castigo llega aquí
          inclinarse    el pie               hay       (se acaba el episodio)
          sin corregir                       remedio
               └────────────┴──── pero la culpa está aquí atrás
```

Averiguar **qué decisiones pasadas** merecen el mérito (o la culpa) de lo que pasa ahora es uno de
los grandes problemas del aprendizaje por refuerzo. Se llama el **problema de la asignación del
mérito**. La buena noticia: los métodos de entrenamiento que estudiaremos lo resuelven
**estadísticamente**, a base de muchísimos episodios. Si apoyar mal el pie **suele** acabar en
caída, tras miles de intentos el robot lo "nota", aunque nunca nadie se lo diga directamente.
Por eso hacen falta tantos intentos.
"""),

md(r"""## 5 · Recompensa escasa o recompensa densa: el juego de "frío, caliente"

¿Te acuerdas del juego de esconder un objeto y guiar a alguien diciendo **"frío, frío... templado...
caliente, ¡caliente!"**? Piensa en dos maneras de jugarlo:

- **Versión A:** no dices nada hasta que lo encuentra. Solo un "¡bien!" al final.
- **Versión B:** vas diciendo "frío" o "caliente" a cada paso.

Con la versión A, el que busca da vueltas a ciegas, y puede tardar una eternidad. Con la B, lo
encuentra enseguida, porque **cada paso le da una pista**.

Con las recompensas pasa lo mismo:

| | Recompensa **escasa** (versión A) | Recompensa **densa** (versión B) |
|---|---|---|
| Cuándo da puntos | Solo al conseguir el objetivo | En cada paso, un poquito |
| Ejemplo | "+1000 si llegas a la meta a 10 metros; 0 en todo lo demás" | "+1 por cada centímetro que avanzas" |
| Ventaja | Imposible de malinterpretar | Da pistas constantes: se aprende rápido |
| Problema | El robot, al azar, **nunca** llega a la meta: nunca ve un punto y no aprende nada | Las pistas pueden **engañar** (y abrir agujeros) |

Piensa en la versión escasa con nuestro robot recién nacido: se cae en un tercio de segundo. ¿Qué
probabilidad hay de que, moviéndose al azar, llegue andando a una meta a 10 metros? Prácticamente
cero. Nunca verá el premio, y sin premio no hay nada que aprender.

Por eso en robótica casi siempre se usan recompensas **densas**: pistas en cada paso que guían
poco a poco. A ese arte de añadir pistas intermedias se le llama **dar forma a la recompensa**
(en inglés, *reward shaping*). Es muy útil... y es justo donde aparecen los agujeros. Vamos a
verlo con la recompensa de verdad.
"""),

md(r"""## 6 · La recompensa de verdad de nuestro humanoide

Esta es la recompensa que recibe nuestro humanoide de práctica **en cada paso** (cada decisión,
15 milésimas de segundo). Tiene cuatro ingredientes. Los he sacado directamente de su programa,
así que son los números reales:

```
   RECOMPENSA DE UN PASO =

       + 5                                   ← premio por seguir de pie
       + 1,25 × (velocidad hacia delante)    ← premio por avanzar
       − 0,1  × (esfuerzo de los motores)    ← castigo por gastar energía
       − (golpes contra el suelo)            ← castigo por chocar fuerte
```

Vamos ingrediente a ingrediente.

**Ingrediente 1 · "Sigue de pie": +5 por paso.** Si al final del paso el torso está a una altura
razonable (entre 1 y 2 metros), el robot gana 5 puntos. Es el premio por **no caerse**. Si cae
por debajo de 1 metro, no gana esos 5 y además el episodio se acaba (ya lo vimos en el NB03).

**Ingrediente 2 · "Avanza": +1,25 por cada metro por segundo.** Se mide a qué velocidad se mueve
**el centro de masas** del robot hacia delante (¡el centro de masas del NB01!). Si va a 1 metro
por segundo, gana 1,25 × 1 = 1,25 puntos ese paso. Si va a 2 m/s, gana 1,25 × 2 = 2,5. Si va
**hacia atrás**, la velocidad es negativa y **pierde** puntos: a −1 m/s, gana 1,25 × (−1) = −1,25.
(Los números negativos del NB03 vuelven a aparecer.)

**Ingrediente 3 · "No malgastes energía": −0,1 × esfuerzo.** Mover los motores a lo bestia tiene un
pequeño castigo. Así se anima al robot a moverse con **suavidad** y sin derrochar, como un buen
atleta. Para entender cómo se mide el "esfuerzo" necesitamos una operación nueva: el cuadrado.

**Ingrediente 4 · "No te des golpes": un castigo por choques fuertes.** Si alguna parte del robot
choca con mucha fuerza (por ejemplo, un pisotón brutal contra el suelo), pierde algunos puntos,
con un máximo de 10 por paso. Así se le anima a pisar con delicadeza.
"""),

md(r"""### Matemáticas desde cero: elevar al cuadrado

**Elevar un número al cuadrado** es multiplicarlo **por sí mismo**. Se escribe con un 2 pequeñito
arriba a la derecha:

```
   3² = 3 × 3 = 9           ("tres al cuadrado es nueve")
   5² = 5 × 5 = 25
   0,4² = 0,4 × 0,4 = 0,16
   0,1² = 0,1 × 0,1 = 0,01
```

(Se llama "cuadrado" porque un cuadrado de 3 de lado tiene 3 × 3 = 9 cuadraditos dentro.)

¿Y si el número es negativo? Hay una regla que quizá te suene: **menos por menos da más**.
Multiplicar dos números negativos da un número positivo. Así que:

```
   (−0,4)² = (−0,4) × (−0,4) = +0,16      ← ¡igual que 0,4²!
```

Y ahora fíjate por qué el cuadrado es **perfecto** para medir el esfuerzo de un motor:

1. **Se come el signo.** Retorcer hacia un lado (+0,4) o hacia el otro (−0,4) cuesta lo mismo:
   0,16 en ambos casos. Tiene sentido: empujar al revés también gasta energía.
2. **Castiga mucho más lo grande que lo pequeño.** Mira: 0,1² = 0,01, pero 0,4² = 0,16. El número
   es 4 veces más grande, pero su cuadrado es **16 veces** más grande. Así, un empujón brusco cuesta
   muchísimo más que varios empujoncitos suaves. Justo lo que queremos: que el robot sea suave.

**El esfuerzo del paso** es: cada uno de los 17 números de la acción, elevado al cuadrado, y todo
sumado. Por ejemplo, si todos los motores empujaran a tope (0,4 o −0,4), el esfuerzo sería 17 ×
0,16 = 2,72, y el castigo 0,1 × 2,72 = **0,272 puntos**. Si todos estuvieran en 0, el castigo
sería 0.
"""),

md(r"""### Comparemos los tamaños de los ingredientes

Antes de hacer cuentas, una observación que va a ser clave. ¿Cuánto puede pesar, como mucho, cada
ingrediente en un paso?

| Ingrediente | Valor típico en un paso |
|---|---|
| Seguir de pie | **+5** (siempre que no te caigas) |
| Avanzar (andando a 1 m/s, un buen paso humano) | +1,25 |
| Esfuerzo (incluso con todos los motores a tope) | como mucho −0,27 |
| Golpes (andando con normalidad) | casi 0 |

¿Ves algo raro? El premio por **seguir de pie** (5) es **cuatro veces mayor** que el premio por
**andar** a buen ritmo (1,25). Guárdalo en la cabeza; volveremos a ello en el apartado 8.
"""),

md(r"""## 7 · Hagamos cuentas: ¿cuántos puntos saca cada robot?

Vamos a calcular el **retorno** (la suma de todo el episodio) de varios robots imaginarios... y de
dos reales que he medido. Recuerda: un episodio dura como mucho **1.000 pasos**.

**Robot A · Se mueve al azar (medido de verdad).** Lo has visto en el GIF del NB00. Lo he puesto a
prueba 20 veces: de media aguanta **21 pasos** y saca unos **98 puntos**, casi todos del premio por
seguir de pie (unos 20 pasos × 5 = 100), menos un poquito de esfuerzo y de golpes.

**Robot B · Motores apagados, "muñeco de trapo" (medido de verdad).** Ponemos los 17 números de la
acción a 0: el robot no hace ninguna fuerza, simplemente se deja caer. Resultado medido: aguanta
unos **40 pasos** y saca unos **198 puntos**.

¡Sorpresa! **No hacer nada saca el doble de puntos que moverse al azar.** El robot al azar, con sus
convulsiones, se tira a sí mismo al suelo más deprisa que la gravedad sola. Moverse sin saber es
**peor** que no moverse. (Y aun así, ninguno de los dos llega ni a un segundo de pie.)

**Robot C · Se queda de pie, quieto, los 1.000 pasos (imaginario).** Imagina un robot que ha
aprendido a mantenerse en equilibrio sin moverse del sitio, con muy poco esfuerzo:

```
   seguir de pie:   1.000 pasos × 5         = 5.000
   avanzar:         velocidad 0 → 1,25 × 0  =     0
   esfuerzo:        casi nada               ≈     0
                                              ───────
   RETORNO                                  ≈ 5.000 puntos
```

**Robot D · Anda a 1 m/s los 1.000 pasos (imaginario).** El robot de nuestros sueños:

```
   seguir de pie:   1.000 pasos × 5            = 5.000
   avanzar:         1.000 pasos × 1,25 × 1     = 1.250
   esfuerzo:        pongamos 0,1 por paso → 1.000 × 0,1 = −100
                                                 ───────
   RETORNO                                     ≈ 6.150 puntos
```

Pongámoslos juntos:

| Robot | Qué hace | Retorno |
|---|---|---|
| A | Se mueve al azar | ~98 |
| B | Muñeco de trapo (no hace nada) | ~198 |
| C | De pie, quieto, todo el episodio | ~5.000 |
| D | Anda a 1 m/s todo el episodio | ~6.150 |
"""),

md(r"""## 8 · La trampa escondida en nuestra propia recompensa

Mira otra vez la tabla. El robot C, que **no anda en absoluto**, saca 5.000 puntos. El robot D,
que anda de maravilla, saca 6.150. Es decir:

> **Quedarse quieto de pie da más del 80 % de los puntos de andar.**

Ponte en el lugar del robot que está aprendiendo. Primero descubre que no caerse da muchísimos
puntos (5 por paso, todo el rato). Aprende a mantenerse de pie. Y entonces llega a un sitio muy
cómodo: ya saca 5.000. Para conseguir el 20 % que falta tendría que **arriesgarse** a dar pasos...
y dar pasos, al principio, significa **caerse**, perder los 5 puntos por paso y acabar el episodio.
¡Explorar le sale carísimo!

Muchos robots entrenados con esta recompensa se quedan atascados justo ahí: aprenden a estar de
pie, o a avanzar arrastrando los pies muy despacito, en vez de andar de verdad. Es como un
estudiante que descubre que con un 8 sin esforzarse ya aprueba con nota, y deja de intentar el 10.

A este tipo de trampa se le llama **óptimo local**: una solución que es **mejor que todo lo que
tiene alrededor**, pero no es la mejor de todas. Imagina que buscas el punto más alto de una
montaña, de noche y con niebla, y solo puedes ir subiendo. Llegas a una colina, miras a tu
alrededor y todo va hacia abajo: "¡ya está, la cumbre!". Pero la cumbre de verdad estaba en otro
sitio, y para llegar a ella habría que **bajar primero**.

```
                                    ★ la cumbre de verdad (andar: 6.150)
                                   / \
          una colina cómoda       /   \
          (quieto: 5.000)  ▲     /     \
                          / \   /       \
                         /   \_/         \
                        /   ↑             \
         ___(azar: 98)_/  para llegar a la cumbre
                          hay que BAJAR primero (caerse
                          al intentar dar los primeros pasos)
```
"""),

md(r"""### ¿Y por qué no quitar el premio por estar de pie?

Buena pregunta. Si el premio por seguir de pie causa el problema, ¿por qué no lo quitamos y dejamos
solo el de avanzar? Vamos a imaginarlo (esto ya es un experimento mental, no una medida).

Sin el +5, al robot **solo le importaría la velocidad hacia delante de su centro de masas**. ¿Y
cuál es la forma más fácil de que tu centro de masas vaya deprisa hacia delante? **Tirarte de
cabeza.** Un robot que se lanza en plancha hacia delante mueve su centro de masas rapidísimo
durante unos pasos. Saca más puntos que uno que intenta andar con cuidado y se cae enseguida.
Así que aprendería a... **tirarse al suelo hacia delante**. Con estilo, eso sí.

Fíjate en el dilema:

- **Mucho** premio por estar de pie → el robot aprende a quedarse quieto.
- **Poco** premio por estar de pie → el robot aprende a lanzarse de cabeza.

Encontrar el **equilibrio justo** entre los ingredientes —cuánto pesa cada uno— es exactamente el
trabajo de un diseñador de recompensas. Esos números (5, 1,25, 0,1) no los dictó la naturaleza:
los eligió una persona, probando. Y no hay una respuesta perfecta, solo compromisos mejores o
peores. Por eso los profesionales añaden con el tiempo más ingredientes (por ejemplo, premiar que
los pies se levanten del suelo de forma alterna, o castigar los movimientos bruscos), cada uno
para tapar un agujero concreto.
"""),

md(r"""## 9 · El robot tramposo: hackear la recompensa

Lo que acabamos de ver tiene nombre: cuando un agente consigue muchos puntos **sin hacer lo que
querías**, aprovechando un agujero en la recompensa, se dice que ha **hackeado la recompensa** (en
inglés, *reward hacking*).

No es un fallo raro. Es **lo normal**. Es tan normal que hay listas enteras de casos recopilados
por investigadores. Antes de ver ejemplos con máquinas, uno muy antiguo con personas.

**El rey Midas.** En el mito griego, el rey Midas pide un deseo: que todo lo que toque se convierta
en oro. Se lo conceden **al pie de la letra**. Toca una piedra: oro. Una rama: oro. Pero luego toca
su comida, y se convierte en oro. Su agua, oro. Casi muere de hambre. Midas consiguió **exactamente
lo que pidió**, que no era lo que **quería**. Un robot aprendiendo es como el genio que concede
deseos: cumple tu recompensa al pie de la letra, no tu intención.
"""),

md(r"""### Casos reales de máquinas tramposas

Estos casos son **reales**, documentados por investigadores:

**El barco que daba vueltas (2016).** Unos investigadores entrenaron a un agente en un videojuego de
carreras de barcos. La recompensa: los puntos del juego, que se ganan, entre otras cosas, chocando
con unos objetivos repartidos por el circuito. El agente descubrió una zona donde unos objetivos
reaparecían una y otra vez... y se quedó allí **dando vueltas en círculo** para siempre, chocando,
incendiándose, sin terminar nunca la carrera. Sacaba **más puntos** que los jugadores humanos que sí
la terminaban.

**El jugador de Tetris que pausaba el juego.** Un programa que aprendía a jugar a videojuegos buscaba,
a grandes rasgos, que los números del juego (como la puntuación) subieran y no se echaran a perder
con un "game over". Cuando en el Tetris iba a perder sin remedio,
descubrió una solución: **pulsar pausa y no quitarla nunca**. Si el juego nunca sigue, nunca
pierdes.

**El bloque de Lego dado la vuelta (2017).** Querían enseñar a un brazo robótico a **apilar** un
bloque rojo encima de uno azul. Para medirlo, le daban puntos según la **altura de la cara de abajo
del bloque rojo** (si está encima del azul, esa cara está alta). El brazo descubrió algo más fácil:
**darle la vuelta al bloque rojo**. Boca abajo, su "cara de abajo" queda arriba, alta. Puntos
conseguidos; bloque sin apilar.

**Las criaturas que se caían para "correr".** En experimentos de criaturas virtuales que aprendían a
moverse, cuando el premio era la velocidad, a veces aparecían criaturas **altísimas** que
simplemente **se caían**: al desplomarse, su cuerpo se movía muy rápido durante un momento. ¿Te
suena? Es justo el robot que se tira en plancha del apartado anterior.

**Aprovechar los fallos del simulador.** Y uno muy típico en robótica: ¿te acuerdas del NB02, cuando
un paso demasiado grande podía hacer que un pie se hundiera en el suelo y saliera **disparado**? Los
agentes **encuentran** esos fallos. Hay robots simulados que han aprendido a vibrar de una forma
rarísima para meter un pie en el suelo y salir impulsados, porque eso les daba velocidad. Un truco
que, por supuesto, no funcionaría jamás en el mundo real.
"""),

md(r"""### La ley que lo resume todo

Hay una frase famosa, que viene de la economía, que resume todos estos casos. Se conoce como la
**ley de Goodhart**:

> **"Cuando una medida se convierte en el objetivo, deja de ser una buena medida."**

Ejemplo humano: un colegio quiere que sus alumnos aprendan, y para medirlo usa las notas de los
exámenes. Mientras las notas sean solo una **medida**, funcionan bien. Pero si el colegio empieza
a perseguir las notas **como objetivo** a toda costa, alguien acabará enseñando solo a "aprobar
exámenes" en vez de a entender. Las notas suben; el aprendizaje, no.

Con los robots es exactamente igual. La recompensa es una **medida** de lo que queremos (que ande
bien). Pero el robot la persigue **como objetivo**, con una tenacidad absoluta y millones de
intentos. Si hay cualquier diferencia entre la medida y lo que de verdad queremos, la encontrará.

Y aquí está la gracia: **el robot no es tonto ni malo**. Es **demasiado bueno** buscando puntos. El
fallo siempre está en la recompensa, es decir, en nosotros.
"""),

md(r"""## 10 · Cómo se defiende un profesional

Si los agujeros son inevitables, ¿qué hace un ingeniero de verdad? Unas cuantas costumbres que
aprenderás a aplicar:

**1. Mirar al robot, no solo los números.** La regla de oro. Un retorno de 5.000 puede ser un robot
que anda... o uno que se queda quieto. Solo **viendo el vídeo** lo sabes. Los buenos profesionales
graban vídeos de sus robots constantemente.

**2. Medir aparte lo que de verdad quieres.** Además de la recompensa, se apuntan otras medidas que
el robot **no** persigue: ¿cuántos metros ha avanzado de verdad? ¿cuántas veces se ha caído? ¿cómo de
recto anda? Si la recompensa sube pero los metros recorridos no, hay trampa.

**3. Empezar simple e ir añadiendo de uno en uno.** Una recompensa con 20 ingredientes metidos a la
vez es imposible de entender. Se empieza con pocos, se mira qué trampa hace el robot, y se añade
**un** ingrediente para taparla. Paso a paso.

**4. Pensar como el robot tramposo.** Antes de entrenar, pregúntate: "si yo solo quisiera puntos y
me diera igual todo lo demás, ¿qué haría?". Muchos agujeros se ven así antes de gastar horas de
entrenamiento.

**5. Desconfiar del simulador.** Si el robot hace algo rarísimo que da muchos puntos, sospecha de un
fallo del mundo de mentira. (Y aquí ayuda también **aleatorizar el mundo** del NB02: un truco que
solo funciona en un mundo concreto deja de funcionar cuando el mundo cambia un poco.)

Diseñar recompensas es, en el fondo, un juego de ajedrez contra un rival que **solo** sabe hacer una
cosa —buscar puntos— pero la hace mejor que nadie.
"""),

md(r"""## 11 · El mapa completo, por fin

Con esta lección has visto las **cuatro primeras piezas** del mapa del NB00, cada una con su lección.
Ya puedes leer el bucle entero entendiendo cada palabra:

```
   (1) CUERPO      piezas rígidas, articulaciones, 17 motores, sensores; suelto
                   (subactuado), con un centro de masas que hay que mantener
                   sobre la base de apoyo                                    → NB01

   (2) MUNDO       el simulador: fuerza → velocidad → posición, choques,
                   pasitos de 3 milésimas; siempre miente un poco            → NB02

   (3) MENTE       la política: observación (45 números) → acción (17 números),
                   una máquina con ruedecillas que se ajustan; agente y
                   entorno; pasos y episodios; explorar y aprovechar          → NB03

   (4) RECOMPENSA  un número por paso; el robot persigue el retorno (la suma);
                   dice qué, no cómo; el robot aprende lo que premias, no lo
                   que querías                                               → NB04

   (5) ENTRENAMIENTO   girar las ruedecillas para que el retorno suba     → más adelante
   (6) MUNDO REAL      saltar la brecha de realidad                       → al final
```

Las piezas (5) y (6) son las más técnicas, y para entenderlas de verdad necesitamos herramientas:
algo de programación y algo de matemáticas. Ahí es justo adonde vamos.
"""),

md(r"""## 12 · Resumen de la lección

1. La **recompensa** es un número que el entorno da tras cada paso para decir qué tal ha ido. Dice
   **qué** queremos, no **cómo** conseguirlo.
2. El robot persigue el **retorno** (la suma de todo el episodio), con un pequeño **descuento** para
   lo lejano; por eso puede aceptar menos ahora para ganar más luego.
3. Saber qué decisión pasada causó un premio o un castigo es el **problema de la asignación del
   mérito**; se resuelve a base de muchísimos intentos. Las recompensas **densas** (frío/caliente)
   ayudan a aprender; las **escasas** casi nunca dan pistas.
4. Nuestro humanoide recibe **+5** por seguir de pie, **+1,25 × velocidad** por avanzar, y pequeños
   castigos por **esfuerzo** (acciones **al cuadrado**) y por golpes. Quedarse quieto ya da más del
   **80 %** de los puntos de andar: un **óptimo local**.
5. Los agentes **hackean la recompensa** constantemente (Midas, el barco, el Tetris, el Lego...): la
   **ley de Goodhart**. La defensa: mirar vídeos, medir aparte lo que de verdad quieres, empezar simple
   y pensar como el tramposo.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Recompensa** | El número que el entorno da tras cada paso: cómo de bien ha ido. |
| **Retorno** | La suma de todas las recompensas de un episodio. |
| **Descuento** | Hacer que los puntos lejanos cuenten un poco menos que los cercanos. |
| **Asignación del mérito** | Averiguar qué decisiones pasadas causaron un premio o un castigo. |
| **Recompensa escasa** | Solo da puntos al conseguir el objetivo final. |
| **Recompensa densa** | Da un poco de puntos en cada paso, como pistas. |
| **Dar forma a la recompensa** | Añadir pistas intermedias para guiar el aprendizaje (*reward shaping*). |
| **Elevar al cuadrado** | Multiplicar un número por sí mismo: 3² = 9; (−0,4)² = 0,16. |
| **Óptimo local** | Una solución mejor que todo lo de alrededor, pero no la mejor de todas. |
| **Hackear la recompensa** | Conseguir muchos puntos sin hacer lo que querías (*reward hacking*). |
| **Ley de Goodhart** | Cuando una medida se convierte en objetivo, deja de ser buena medida. |
"""),

md(r"""## 13 · Preguntas de comprensión

Responde con tus palabras antes de abrir cada solución. Hoy hay unas cuantas cuentas: hazlas con
lápiz y papel, sin prisa.

**P1.** ¿Qué es una **recompensa** y en qué se parece a la puntuación de un videojuego?

**P2.** ¿Qué diferencia hay entre la **recompensa** y el **retorno**? ¿Por qué el robot persigue el
retorno y no la recompensa de cada paso?

**P3.** Explica con el ejemplo del fútbol qué es el **problema de la asignación del mérito**.

**P4.** ¿Por qué una recompensa **escasa** ("+1000 solo si llegas a la meta") no sirve para un robot
recién nacido?

**P5.** Calcula: **4²**, **0,2²**, **(−0,3)²** y **(−1)²**.

**P6.** Un robot da un paso con los 17 motores en 0, salvo uno, que está en **−0,4**. ¿Cuánto vale su
castigo por esfuerzo (−0,1 × esfuerzo) en ese paso?

**P7.** En un paso, el robot sigue de pie, avanza a **2 m/s** y su esfuerzo total vale **1**
(ignoramos los golpes). ¿Cuánta recompensa recibe en ese paso?

**P8.** Calcula el retorno de un robot que aguanta **400 pasos** de pie, avanzando a **0,8 m/s**, con
un castigo por esfuerzo de **0,05** por paso.

**P9.** ¿Por qué decimos que quedarse quieto es un **óptimo local** para nuestro humanoide? Explícalo
con la montaña con niebla.

**P10.** ¿Qué pasaría, según el experimento mental del apartado 8, si quitáramos el premio de +5 por
seguir de pie? ¿Por qué?

**P11.** Explica con tus palabras la **ley de Goodhart** y relaciónala con el bloque de Lego.

**P12.** Imagina que diseñas una recompensa para un robot aspirador: "+1 por cada pelusa que
aspire". Piensa como el robot tramposo: ¿cómo podría hacer trampa?
"""),

md(r"""<details>
<summary>▶ Solución P1</summary>

Es un **número** que el entorno le da al agente después de cada paso, diciendo qué tal ha ido lo que
acaba de pasar (alto = bien, bajo o negativo = mal). Se parece a la puntuación de un videojuego
porque cada cosa que haces suma o resta puntos, y aprendes a jugar para conseguir más, sin que nadie
te explique con palabras qué hacer.
</details>

<details>
<summary>▶ Solución P2</summary>

La **recompensa** es el número de **un** paso; el **retorno** es la **suma** de todas las recompensas
del episodio. El robot persigue el retorno porque a veces, para ganar más en total, hay que aceptar
menos ahora (como ahorrar o estudiar). Un robot que solo mirara el paso actual nunca prepararía un
movimiento que da fruto más tarde, como doblar la rodilla para dar un paso.
</details>

<details>
<summary>▶ Solución P3</summary>

Cuando se marca un gol, la recompensa llega al final, pero el mérito no es solo del que remata: también
del que dio el pase y del que recuperó el balón 30 segundos antes. Con el robot igual: si se cae en el
paso 40, la culpa puede estar en una decisión del paso 12 o del 25. Averiguar **qué decisiones pasadas
merecen el mérito o la culpa** de lo que pasa ahora es el problema de la asignación del mérito.
</details>

<details>
<summary>▶ Solución P4</summary>

Porque un robot recién nacido se mueve al azar y se cae en un tercio de segundo: la probabilidad de que
llegue por casualidad a una meta a 10 metros es prácticamente cero. Así que **nunca** vería el premio, y
sin ver nunca un premio no tiene ninguna pista de qué hacer mejor: no aprende nada. Por eso se usan
recompensas densas, que dan pistas en cada paso (como el "frío, caliente").
</details>

<details>
<summary>▶ Solución P5</summary>

- 4² = 4 × 4 = **16**
- 0,2² = 0,2 × 0,2 = **0,04**
- (−0,3)² = (−0,3) × (−0,3) = **0,09** (menos por menos da más)
- (−1)² = (−1) × (−1) = **1**
</details>

<details>
<summary>▶ Solución P6</summary>

Los 16 motores en 0 aportan 0² = 0 cada uno. El que está en −0,4 aporta (−0,4)² = 0,16. Esfuerzo total =
**0,16**. Castigo = 0,1 × 0,16 = **0,016 puntos** (es decir, la recompensa baja 0,016). Muy poquito.
</details>

<details>
<summary>▶ Solución P7</summary>

- Seguir de pie: **+5**
- Avanzar: 1,25 × 2 = **+2,5**
- Esfuerzo: 0,1 × 1 = **−0,1**

Total: 5 + 2,5 − 0,1 = **7,4 puntos** en ese paso.
</details>

<details>
<summary>▶ Solución P8</summary>

Primero, la recompensa de **un** paso:

- De pie: +5
- Avanzar: 1,25 × 0,8 = +1
- Esfuerzo: −0,05

Un paso = 5 + 1 − 0,05 = **5,95**. Como son 400 pasos iguales: 400 × 5,95 = **2.380 puntos** de retorno.

(Comparado con el robot C, que se queda quieto 1.000 pasos y saca 5.000, este robot que anda pero se cae
a los 400 pasos saca **menos de la mitad**. ¿Ves el problema? Desde el punto de vista de los puntos,
aguantar quieto es mejor que andar y caerse.)
</details>

<details>
<summary>▶ Solución P9</summary>

Porque quedarse quieto de pie (≈5.000 puntos) es **mejor que todo lo que tiene "alrededor"**: si el
robot intenta dar pasos, al principio se cae, pierde los 5 puntos por paso y el episodio se acaba, así
que saca menos. Pero no es la mejor solución de todas: andar bien da ≈6.150. Es como estar en una colina
de noche y con niebla: a tu alrededor todo baja, así que crees estar en la cumbre, pero la cumbre de
verdad está en otro sitio y para llegar habría que **bajar primero** (caerse mientras aprende a andar).
</details>

<details>
<summary>▶ Solución P10</summary>

Al robot solo le importaría la **velocidad hacia delante de su centro de masas**. La forma más fácil de
que el centro de masas vaya deprisa hacia delante durante un momento es **tirarse de cabeza**, así que
probablemente aprendería a lanzarse en plancha hacia delante en vez de andar. Mucho premio por estar de
pie lleva a quedarse quieto; poco premio lleva a lanzarse. Hay que buscar el equilibrio.
</details>

<details>
<summary>▶ Solución P11</summary>

La ley de Goodhart dice que **cuando una medida se convierte en el objetivo, deja de ser una buena
medida**: si persigues la medida a toda costa, aparecen formas de mejorarla sin mejorar lo que de verdad
querías. En el Lego, la medida era "altura de la cara de abajo del bloque rojo", que en principio indica
que está apilado. Pero al convertirla en objetivo, el brazo encontró otra forma de subirla: **dar la
vuelta al bloque**. La medida subió; el bloque no se apiló.
</details>

<details>
<summary>▶ Solución P12</summary>

Hay varias trampas posibles (cualquiera razonable vale). Por ejemplo: **aspirar pelusa, volver a
soltarla y aspirarla otra vez**, una y otra vez, sumando +1 cada vez; o **ir a un sitio donde se acumula
mucha pelusa** (junto a la puerta de la terraza) y quedarse allí ignorando el resto de la casa; o, si
"aspirar" se mide con un sensor, **engañar al sensor**. Un buen diseñador taparía esto premiando, por
ejemplo, la **superficie limpia** en vez de las pelusas aspiradas... y luego buscaría la siguiente trampa.
</details>
"""),

md(r"""## 14 · 🛠 Práctica en MuJoCo: ponle nota al humanoide

En el apartado 6 te enseñé la recompensa **de verdad** del humanoide y en el 7 te di sus cuentas
"medidas". Ahora las vas a medir **tú**. Vas a escribir (bueno, ejecutar: ya está escrita) la
recompensa ingrediente a ingrediente sobre MuJoCo, vas a puntuar a dos robots del apartado 7, y vas
a destapar con tus propios ojos el dilema del apartado 8: **qué pasa si quitamos el premio por
seguir de pie**.

Como siempre en la Parte 0: ejecutas, miras y cambias algún número.
"""),

md(r"""### Paso 1 · El centro de masas, en números

El ingrediente "avanza" mide la velocidad del **centro de masas** (NB01) hacia delante. MuJoCo sabe
dónde está el centro de cada pieza (`datos.xipos`) y cuánto pesa (`modelo.body_mass`, NB03b). El
centro de masas del robot entero es la **media** de los centros de las piezas, pero dando más
importancia a las que pesan más (cada posición se multiplica por su masa, se suma todo y se divide
por la masa total). Lo que hace esta pequeña receta es justo eso, solo hacia delante (la "x"):
"""),

code(r"""import mujoco
import numpy as np
import taller

def centro_de_masas_x(modelo, datos):
    return np.sum(modelo.body_mass * datos.xipos[:, 0]) / np.sum(modelo.body_mass)

modelo, datos = taller.cargar("humanoide")
print("Centro de masas hacia delante:", centro_de_masas_x(modelo, datos), "m")"""),

md(r"""Unos **0,015 m** (1,5 centímetros): el robot acaba de nacer en el centro del mundo y su peso está casi
justo encima de los pies, apenas un pelín hacia delante. Y la **velocidad** se mide como en el NB02:
dónde está después de un paso, menos dónde estaba antes, y dividido por lo que ha durado el paso
(15 milésimas).
"""),

md(r"""### Paso 2 · La recompensa, ingrediente a ingrediente

Esta celda **define** la receta `puntuar`: juega un episodio con la política que le des (igual que
la receta `episodio` de la práctica del NB03) y, en cada paso, apunta los **cuatro ingredientes** del
apartado 6, con sus números reales:

```
   de pie:    + 5                si el torso está entre 1 y 2 metros
   avanzar:   + 1,25 × velocidad del centro de masas hacia delante
   esfuerzo:  − 0,1 × (suma de las 17 órdenes al cuadrado)
   golpes:    − 0,0000005 × (suma de las fuerzas de choque al cuadrado), como mucho 10
```

Al final escribe cuántos pasos ha durado, el **retorno** (todo sumado) y cuánto ha aportado cada
ingrediente. Tiene dos "mandos" que usaremos luego: `premio_de_pie` (el 5) y `empujon` (una velocidad
inicial hacia delante, en metros por segundo).

No te preocupes por entender cada línea. Solo una curiosidad: `mj_rnePostConstraint` es una orden
que le pide a MuJoCo que calcule **las fuerzas de los choques** (no las calcula siempre, para ir más
rápido). Sin ella, el ingrediente de los golpes saldría siempre cero.
"""),

code(r"""def puntuar(politica, premio_de_pie=5.0, empujon=0.0):
    modelo, datos = taller.cargar("humanoide")
    datos.qvel[0] = empujon                               # velocidad inicial hacia delante
    pie = avanzar = esfuerzo = golpes = 0.0
    for paso in range(1, 1001):
        politica(modelo, datos)
        x_antes = centro_de_masas_x(modelo, datos)
        for _ in range(5):
            mujoco.mj_step(modelo, datos)
        mujoco.mj_rnePostConstraint(modelo, datos)       # calcula las fuerzas de choque
        velocidad = (centro_de_masas_x(modelo, datos) - x_antes) / (5 * modelo.opt.timestep)
        de_pie = 1.0 < datos.qpos[2] < 2.0

        if de_pie:
            pie += premio_de_pie
        avanzar += 1.25 * velocidad
        esfuerzo -= 0.1 * np.sum(datos.ctrl ** 2)
        golpes -= min(5e-7 * np.sum(datos.cfrc_ext ** 2), 10)
        if not de_pie:
            break

    retorno = pie + avanzar + esfuerzo + golpes
    print(f"{paso} pasos · RETORNO = {retorno:.1f}   "
          f"(de pie {pie:+.1f}, avanzar {avanzar:+.2f}, esfuerzo {esfuerzo:+.2f}, golpes {golpes:+.2f})")"""),

md(r"""### Paso 3 · Robot B: el muñeco de trapo

Los 17 motores a cero, como en el apartado 7.
"""),

code(r"""def muneco_de_trapo(modelo, datos):
    datos.ctrl[:] = 0

puntuar(muneco_de_trapo)"""),

md(r"""**40 pasos y 195,5 puntos.** Mira el desglose:

- **De pie: +195** = 39 pasos × 5. (¿Por qué 39 y no 40? Porque en el paso 40 el torso ya ha bajado
  de 1 metro: ese paso no cobra el premio, y además termina el episodio.)
- **Avanzar: +6,14**. Al desplomarse, el centro de masas se ha movido un poco **hacia delante**, y eso
  ya da puntos. Recuérdalo.
- **Esfuerzo: 0**. Motores a cero: 0² = 0.
- **Golpes: −5,66**. El castañazo final contra el suelo.

Es casi exactamente el "~198" del apartado 7. (Allí era la media de 20 intentos medidos con el
programa oficial de Gymnasium, que hace nacer al robot con un temblor diminuto y distinto cada
vez; aquí nace siempre igual. He comprobado que el programa oficial, sin el temblor, da
**195,49**: nuestra receta calcula lo mismo que él.)
"""),

md(r"""### Paso 4 · Robot A: al azar

Ahora 10 robots al azar, cada uno con su semilla (de 0 a 9), para ver cuánto varía:
"""),

code(r"""for semilla in range(10):
    dados = np.random.default_rng(semilla)
    def al_azar(modelo, datos):
        datos.ctrl[:] = dados.uniform(-0.4, 0.4, size=17)
    puntuar(al_azar)"""),

md(r"""Entre **78 y 184 puntos**, unos **117 de media**, y **ninguno** llega a los 195,5 del muñeco de trapo.
Ya lo sabías del apartado 7 (allí la media de 20 intentos salía ~98: el azar varía bastante de una
tanda a otra), pero ahora lo has visto en cada desglose: el robot al azar paga algo de **esfuerzo**
(unos −2) y algo de **golpes**, y sobre todo cobra **menos premios de pie** porque se cae antes.
"""),

md(r"""### Paso 5 · La trampa: quitar el premio por estar de pie

El experimento mental del apartado 8, hecho de verdad. Ponemos `premio_de_pie=0`: al robot solo le
importa que su centro de masas vaya **hacia delante**. Comparamos dos robots:

- el **muñeco de trapo**, que se desploma sin más;
- un robot que se **lanza hacia delante**: el mismo muñeco de trapo, pero con un **empujón** inicial
  de 2 metros por segundo (como alguien que se tira en plancha a la piscina).
"""),

code(r"""print("SIN premio por estar de pie:")
puntuar(muneco_de_trapo, premio_de_pie=0)
puntuar(muneco_de_trapo, premio_de_pie=0, empujon=2)

print("CON premio por estar de pie (el de verdad):")
puntuar(muneco_de_trapo)
puntuar(muneco_de_trapo, empujon=2)"""),

md(r"""Ahí está el dilema del apartado 8, en números de MuJoCo:

| | Desplomarse | Lanzarse en plancha |
|---|---|---|
| **Sin** premio de pie | 0,5 puntos | **59,6 puntos** (¡más de 100 veces más!) |
| **Con** premio de pie (+5) | **195,5 puntos** | 189,6 puntos |

**Sin** el +5, tirarse de cabeza es, con muchísima diferencia, lo que más puntos da: un robot que
aprendiera con esa recompensa aprendería a... lanzarse al suelo. **Con** el +5, el lanzamiento ya no
compensa: se cae 13 pasos antes (27 en vez de 40) y pierde 65 puntos de premio de pie, más de lo que
gana por "avanzar". El +5 hace su trabajo... pero por **poco** (195,5 frente a 189,6). Lo afinarás en
el Reto 2.

Y ahora la **regla de oro del apartado 10**: mirar al robot, no solo los números. Esos 59,6 puntos
"de avanzar", ¿qué son en realidad?
"""),

code(r"""modelo, datos = taller.cargar("humanoide")
datos.qvel[0] = 2                                   # el empujón de 2 m/s
taller.video(modelo, datos, segundos=2, control=muneco_de_trapo, nombre="nb04_plancha");"""),

md(r"""Un robot al que se le doblan las rodillas y acaba tirado en el suelo, hacia delante. La recompensa sin el +5 lo llamaría "avanzar". Con la tabla de
números sola, nadie lo habría adivinado; con el vídeo, salta a la vista. Por eso los profesionales
graban vídeos sin parar.
"""),

md(r"""### Tus retos

**Reto 1.** En el Paso 5, cambia el empujón de `2` a `1`. ¿Sigue ganando la plancha sin el premio de
pie? ¿Y con él?

**Reto 2 · ¿Cuánto premio de pie hace falta?** Con el +5 de verdad, el muñeco de trapo gana a la
plancha por poco. Prueba `premio_de_pie=4` en las dos últimas líneas del Paso 5. ¿Quién gana ahora?
(Para pensar: ¿a partir de qué premio gana quedarse? Usa los números del desglose y un poco del
NB04b... o prueba valores.)

**Reto 3 · El precio del esfuerzo.** Puntúa a la mente "tensa" del NB03 (los 17 motores a +0,4). Añade
una celda con esto y ejecútala:

```python
def tenso(modelo, datos):
    datos.ctrl[:] = 0.4

puntuar(tenso)
```

¿Cuánto esfuerzo paga **en cada paso**? Compáralo con la cuenta del apartado 6 (todos los motores a
tope).

<details>
<summary>▶ Solución Reto 1</summary>

Con empujón 1: **sin** premio de pie, la plancha saca **36,2** puntos (frente a 0,5 del desplome):
sigue ganando con mucha diferencia. **Con** premio de pie, saca **191,2** (frente a 195,5): pierde por
poco. Un empujón más suave avanza menos pero también cae más tarde (32 pasos); el dilema es el mismo.
</details>

<details>
<summary>▶ Solución Reto 2</summary>

Con `premio_de_pie=4`: el desplome saca **156,5** y la plancha **163,6**. ¡**Gana la plancha**! Con un
premio de pie de 4 en vez de 5, el robot ya aprendería a tirarse.

Las cuentas, con los desgloses: el desplome cobra 39 premios y suma +0,48 del resto (6,14 − 5,66); la
plancha cobra 26 premios y suma +59,63 (64,30 − 4,67). Empatan cuando 39·p + 0,48 = 26·p + 59,63, es
decir, 13·p = 59,15 → **p ≈ 4,55**. Por debajo de 4,55 gana tirarse; por encima, quedarse. El 5 de
verdad está muy cerca del límite. Esto es el **equilibrio justo** del apartado 8: los números de una
recompensa no son caprichosos, y moverlos un poco cambia lo que aprende el robot.
</details>

<details>
<summary>▶ Solución Reto 3</summary>

La mente tensa aguanta **47 pasos**, saca **239,9** puntos (¡más que el muñeco de trapo, porque
aguanta más y además se cae hacia delante: +28,48 de "avanzar"!) y paga **−12,78** de esfuerzo en total. En cada paso: 12,78 ÷ 47 = **0,272**, justo la
cuenta del apartado 6 (0,1 × 17 × 0,4² = 0,272): el máximo esfuerzo posible. Aun así, el castigo por
esfuerzo es pequeñito comparado con los +5 por paso de seguir de pie (apartado 6, "compara los
tamaños").
</details>

### Qué has aprendido de MuJoCo hoy

- Una **recompensa** no es magia: son unas pocas líneas que leen números de MuJoCo y los combinan.
- **`datos.xipos`** (el centro de cada pieza) y **`modelo.body_mass`** dan el **centro de masas**.
- **`datos.cfrc_ext`**: las fuerzas de los choques, que MuJoCo solo calcula si se lo pides con
  **`mujoco.mj_rnePostConstraint`**.
- Escribir un número en **`datos.qvel`** antes de simular es dar un **empujón**: el robot arranca
  con esa velocidad.
- Cambiar **un número** de la recompensa (el 5) puede cambiar qué estrategia gana. Y un vídeo dice
  lo que los números esconden.

En la práctica del NB04b comprobarás en MuJoCo la fórmula de la caída libre que vas a deducir, y la
usarás para **predecir** cuándo llega una pelota al suelo antes de simularla.
"""),

md(r"""## 15 · Posdata: se acaba la Parte 0

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Con esta lección **termina la Parte 0, "El terreno"**. Párate un segundo a ver lo que ya sabes: qué es
un robot por dentro, por qué andar es tan difícil para él, cómo funciona un mundo de mentira, qué es la
mente de un robot y cómo se le guía con premios... y por qué esos premios son tan traicioneros. Todo eso
sin escribir tú una sola línea de código (aunque en cada práctica ya has puesto MuJoCo en marcha
con código ya escrito). Es una base muy sólida.

Antes de tocar el ordenador, una última parada técnica: en el **NB04b** aprenderemos el idioma de las fórmulas (letras, ecuaciones, despejar) y deduciremos por fin el 0,75 m de la pelota del NB02. Después, en el **NB05**, empieza la **Parte 1**: por fin vamos a tocar el ordenador. Pero con muchísima calma:
primero qué es un ordenador, qué es un programa y dónde se escribe; y después, **una sola línea** de
código, la más famosa de la historia: hacer que el ordenador diga "hola". Una idea por vez, como
prometimos en la primera lección.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB04_la_recompensa_y_sus_trampas.ipynb")
    build(out, cells, title="NB04 · Premios y castigos: la recompensa y sus trampas")
