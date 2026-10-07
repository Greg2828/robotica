"""Construye NB00 · ¿Qué vamos a hacer y por qué es difícil?

Primer notebook de la ruta nueva: conceptual; el único código es la Práctica en MuJoCo
del final (ya escrita: solo ejecutar y mirar).
Todo prosa, analogías, experimentos con el propio cuerpo y diagramas. El robot se
ve como un GIF ya hecho (imagen en markdown), sin pedir ejecutar nada.

Dato verificado (Humanoid-v5, acciones al azar, 20 intentos): aguanta de media
~22 decisiones ≈ 0,33 s antes de caer.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB00 · ¿Qué vamos a hacer y por qué es difícil?

**Parte 0 · El terreno — Lección 1**

> Bienvenido. Esto es el comienzo de un viaje largo que va **de cero a profesional**. Al
> final del camino sabrás **enseñar a andar a un robot de dos piernas**, como esos
> humanoides que salen en los vídeos de las empresas de robótica.
>
> No necesitas saber **nada** de antemano. Ni programar, ni matemáticas, ni física. De
> verdad: nada. Todo lo que haga falta lo iremos construyendo aquí desde el principio, con
> calma y con ejemplos de la vida diaria.

Casi toda esta primera lección **se lee**, como quien lee la primera página de un libro.
Solo al final, en la **Práctica en MuJoCo**, pulsarás un botón para poner en marcha un robot
de verdad dentro del ordenador (sin escribir nada: el código ya viene hecho). Bueno, y alguna vez te pediré que te levantes de la silla para hacer un pequeño
experimento con tu propio cuerpo, porque tu cuerpo es el mejor laboratorio de robótica que
existe.

Lo único que quiero es que salgas de aquí entendiendo **qué vamos a hacer** y **por qué es un
problema tan bonito y tan difícil**.

Ponte cómodo. Vamos despacio.
"""),

md(r"""## 1 · Cómo funciona este curso (léelo una vez, con atención)

Antes de empezar, cinco reglas del juego. Son importantes porque marcan el ritmo de todo
lo que viene.

**1. Se lee como un libro, sin prisa.** Cada notebook (cada uno de estos documentos) es una
lección larga. Primero te cuento el problema con palabras normales, luego la idea con algún
ejemplo cotidiano, y solo mucho más adelante —cuando ya se entienda— aparecerá algo de
código. No hay ninguna prisa. Si un día lees solo la mitad, perfecto.

**2. Nada se da por sabido.** La primera vez que aparezca una palabra nueva, se explica ahí
mismo, y además la encontrarás al final de cada lección en una cajita llamada **"Palabras
nuevas de hoy"**. Si en algún momento lees algo y piensas *"¿y esto qué es?"*, casi seguro
que la respuesta está una o dos líneas más abajo. Y si no está, es culpa del texto, no tuya.

**3. Las matemáticas y la física también empiezan de cero.** Cuando más adelante necesitemos
un poco de matemáticas (sumar flechas, medir velocidades, calcular probabilidades) o de
física (qué es una fuerza, qué es la gravedad), **no daré por hecho que las sabes**. Las
explicaré desde el principio, con dibujos y analogías. La robótica es nuestro *objetivo*;
todo lo demás son herramientas que iremos afilando por el camino.

**4. El código llegará poco a poco, en gotas.** Programar es darle instrucciones a un
ordenador. Al principio del curso apenas verás código, y cuando empiece a aparecer será
**una idea nueva por vez**, la más pequeña posible. Nada de muros de texto raro. Primero se
entiende la idea; después se traduce a código. Nunca al revés.

**5. Los ejercicios van resueltos.** Al final de cada lección habrá unas preguntas. Debajo
de cada una está la respuesta, escondida en un desplegable **"▶ Solución"**. La gracia está
en que intentes contestar tú primero, aunque te equivoques. Equivocarte y luego ver la
solución es la mejor forma de que se te quede.

**6. Cada lección termina con una práctica en MuJoCo.** MuJoCo es el **simulador** (el "mundo
de mentira" dentro del ordenador) que usan Google DeepMind y muchísimos laboratorios para
entrenar robots. Es la herramienta principal de este curso, y no vas a esperar meses para
tocarla: **desde hoy mismo**, cada lección acaba con un apartado **"🛠 Práctica en MuJoCo"**
donde usas lo que acabas de aprender, a tu nivel. Las primeras prácticas traen el código ya
escrito (tú solo ejecutas, miras y cambias algún número); poco a poco irás escribiéndolo tú.

Ya está. Con eso en la cabeza, empecemos por el principio de todo: el sueño.
"""),

md(r"""## 2 · El sueño: una máquina que anda como tú

Seguramente has visto vídeos de robots humanoides: máquinas con dos piernas, dos brazos y
una cabeza que caminan, suben escaleras, se mantienen de pie cuando alguien las empuja e
incluso corren o bailan. Parece ciencia ficción, pero es real, y cada año se acercan más a
moverse como una persona.

Si un día quieres buscarlos en internet, algunos nombres conocidos son el **Atlas** de Boston
Dynamics, el **G1** y el **H1** de la empresa china Unitree, el **Digit** de Agility Robotics o
los robots de **Figure**. No hace falta que te los aprendas; solo que sepas que esto no es un
juguete de laboratorio: hay empresas enteras dedicadas a ello, y buscan gente que sepa hacer
justo lo que vas a aprender.

Detrás de cada uno de esos robots hay alguien que le ha **enseñado a moverse**. Ese
"alguien" es justo lo que tú vas a aprender a ser. No a fabricar el robot con tornillos y
cables (eso es otro oficio), sino a crear **la parte que decide cómo moverse**: su forma de
mantener el equilibrio, de dar un paso, de no caerse. Digamos que vas a construir **el
cerebro del movimiento**.
"""),

md(r"""### ¿Y por qué con forma de persona?

Es una pregunta muy buena. Un robot con ruedas es mucho más fácil de hacer: no se cae, es
barato y es rápido. Entonces, ¿por qué tanto empeño en darle **dos piernas**?

Por una razón sencilla: **el mundo está construido para personas.** Mira a tu alrededor:

- Hay **escaleras**, bordillos y escalones. Las ruedas se atascan; las piernas los suben.
- Las **puertas**, los pomos, los grifos y los interruptores están a la altura de una mano
  humana.
- Las **herramientas** (un taladro, una llave, una caja) están pensadas para manos humanas.
- Los **pasillos**, los coches, las fábricas, las cocinas... todo tiene medidas de persona.

En vez de rehacer el mundo entero para que lo usen los robots, es más práctico hacer robots
que encajen en el mundo que ya existe. Y para eso, la forma humana es la que mejor encaja.

El precio a pagar es que andar sobre dos piernas es **dificilísimo**. Aunque tú andas sin
pensar, enseñar a andar a una máquina es uno de los problemas **más difíciles** que existen.
Vamos a ver por qué.
"""),

md(r"""## 3 · Por qué andar es dificilísimo (aunque a ti te salga solo)

Haz una prueba mental. Intenta escribir, con **instrucciones exactas**, cómo se da **un
solo paso**. No vale decir "pues... adelantas una pierna". Tienen que ser órdenes precisas,
como una receta de cocina milimétrica:

> *"Dobla la rodilla derecha 30 grados. Empuja con el tobillo izquierdo con tanta fuerza.
> Inclina el tronco un poco hacia delante, pero no demasiado o te caes de morros. Si el
> suelo está algo inclinado, corrige así. Si notas que te vas de lado, mueve el brazo
> asá..."*

¿Cuántas instrucciones harían falta para cubrir **todas** las situaciones? ¿Y si el suelo
resbala? ¿Y si alguien te da un empujón? ¿Y si hay un escalón? Son **millones** de
detalles, cambian **a cada instante**, y dependen unos de otros. **Nadie sabe escribir esa
receta a mano.** Es sencillamente demasiado grande y demasiado cambiante.

Y lo más curioso: **tú tampoco sabes escribirla**, y eso que andas todos los días. Tu cuerpo
sabe hacerlo, pero tú no sabrías explicarlo con palabras. Es un conocimiento que está "en
los músculos", no en las frases. Aprendiste a andar con un año, a base de caerte, mucho antes
de saber hablar bien. Guarda esta idea, porque es una pista enorme de cómo vamos a resolver el
problema.

Y hay un problema aún más gordo: un cuerpo de dos piernas es **inestable por naturaleza**.
"""),

md(r"""### El palo de escoba en la palma de la mano

Coge (de verdad, o imagínalo) un palo de escoba y ponlo de pie sobre la palma de tu mano.
Para que no se caiga tienes que mover la mano **todo el rato**, corrigiendo sin parar. En
cuanto te distraes un segundo, ¡al suelo!

Un robot de dos piernas es exactamente eso: un montón de peso arriba (el tronco, la cabeza)
sostenido sobre una base minúscula (dos pies, y a veces **un solo pie** mientras da un
paso). La gravedad tira de él hacia el suelo sin descanso. Si no corrige su postura
**muchísimas veces por segundo**, se cae.

```
     bípedo                        coche parado

       O   <- peso alto              [=======]
      /|\                            o       o   <- ruedas separadas,
       |   <- todo apoyado          ---------      peso bajo, base ancha
      / \     sobre una              se queda quieto él solo,
     _pie pie_  base pequeña          sin hacer nada
     ~~~~~~~~~                       ~~~~~~~~~~~~~~~
  INESTABLE: hay que                ESTABLE: no necesita
  corregir sin parar                corregir nada
```

Un coche con cuatro ruedas se queda quieto solo: tiene la base ancha y el peso bajo. Un
bípedo, no: necesita **corregir activamente y sin parar**, como tu mano con la escoba. Por
eso es tan difícil.
"""),

md(r"""### Experimento con tu cuerpo: la pata coja

Ahora sí, levántate un momento. Tres pruebas cortas, de menos de un minuto en total. (Hazlas
cerca de una pared o una silla, por si acaso.)

**Prueba 1 — De pie, normal.** Quédate quieto con los dos pies en el suelo, separados más o
menos a la anchura de tus hombros. Fácil, ¿verdad? Casi no notas nada.

**Prueba 2 — A la pata coja.** Levanta un pie y aguanta unos 20 segundos sobre el otro.
Fíjate en tu **tobillo**: está haciendo pequeñas correcciones todo el rato, temblando un poco
a un lado y a otro. Nadie le ha dicho que lo haga; tu cuerpo corrige solo, sin que lo pienses.
Eso es exactamente lo que hacía tu mano con la escoba.

**Prueba 3 — A la pata coja con los ojos cerrados.** Lo mismo, pero cerrando los ojos. Casi
seguro que ahora es **muchísimo** más difícil, y te tambaleas o tienes que apoyar el pie.

¿Qué hemos aprendido con esto? Tres cosas que serán importantísimas durante todo el curso:

1. **Cuanto más pequeña es la base, más difícil es el equilibrio.** Dos pies es fácil; uno
   solo, difícil. Y al andar, ¡te pasas la mitad del tiempo sobre un solo pie!
2. **El equilibrio es corregir sin parar**, con pequeños ajustes muy rápidos.
3. **Para corregir hay que saber cómo estás.** Al cerrar los ojos pierdes información y el
   equilibrio empeora. Un robot igual: necesita "sentidos" que le digan cómo está su cuerpo.
   Hablaremos de esos sentidos más adelante.
"""),

md(r"""### Una idea sorprendente: andar es caerse con estilo

Una última cosa sobre por qué andar es especial. Fíjate en lo que haces cuando das un paso:
**te inclinas hacia delante**, empiezas a caer... y justo a tiempo **pones el otro pie
delante** para pararte. Luego vuelves a inclinarte, vuelves a empezar a caer, y vuelves a
poner el pie. Y así todo el rato.

```
    1. de pie        2. me inclino      3. empiezo a     4. pongo el pie
                        hacia delante      caer...          delante: ¡salvado!

       O                 O                   O                  O
      /|\               /|\                 /|\                /|\
       |                 /                   /                  |\
      / \               / \                 /  \               /  \
```

Sí: **andar es una caída hacia delante que vas parando a cada paso**. Por eso un robot que
anda no puede ser "rígido y prudente" como una estatua. Tiene que **dejarse caer un poco, a
propósito**, y recogerse a tiempo. Es un equilibrio en movimiento, no un equilibrio quieto, y
eso lo hace aún más delicado.

Entonces, si la receta de andar no se puede escribir a mano... ¿de dónde sale?
"""),

md(r"""## 4 · La idea que lo cambia todo: aprender probando

Piensa en cómo aprendiste tú a montar en bici. ¿Te dieron una hoja con la fórmula exacta
del equilibrio? No. Te subiste, te tambaleaste, te caíste, lo intentaste otra vez, y otra,
y otra... hasta que un día, sin saber muy bien cómo, **te salió**. Nadie te *escribió* cómo
montar en bici. Lo **aprendiste probando**.

Con los robots hacemos justo eso. Y esta es **la idea central de todo el curso**, así que
léela dos veces:

> **En vez de *escribir* cómo andar, dejamos que el robot lo *aprenda probando*, una y otra
> vez, millones de veces.** Al principio lo hace fatal, se cae constantemente. Pero cada
> intento le da pistas de qué funciona un poco mejor, y poco a poco va mejorando solo,
> hasta que anda.

A esa forma de aprender —probando, equivocándose y mejorando con la experiencia— se le
llama **aprendizaje por refuerzo**. Es la misma idea que usas para enseñar un truco a un
perro: cuando lo hace bien, premio; cuando no, nada. Repítelo suficientes veces y el perro
aprende. Aquí el "perro" es el robot, y el "premio" es un número que le damos: más puntos
cuanto mejor lo hace.

Y a la **manera de decidir** que el robot va afinando —su "así es como yo elijo qué hacer en
cada momento"— la llamaremos su **política**. No te preocupes por la palabra ahora; volverá
muchas veces. Quédate solo con la idea:

> **política = la forma que tiene el robot de decidir qué hacer.** Empieza siendo pésima y,
> a base de practicar, se vuelve buena.

(Ojo: aquí "política" no tiene nada que ver con los políticos ni las elecciones. Es una
palabra que viene del inglés *policy*, que significa algo así como "norma de conducta" o
"forma de actuar". Una tienda tiene una *política de devoluciones*; un robot tiene una
*política de movimientos*.)
"""),

md(r"""### ¿Cómo se ve "aprender probando"?

Para que te hagas una idea del proceso, imagina que vamos espiando al robot mientras
practica. Los números de esta tabla son **inventados, solo para que veas la forma** que tiene
el aprendizaje (más adelante veremos números reales):

| Cuánto ha practicado | Qué hace el robot | Cuánto aguanta de pie |
|---|---|---|
| Nada (recién nacido) | Tiembla al azar y se desploma | Menos de medio segundo |
| Un poco | Ha "descubierto" que tensar las piernas ayuda; se queda rígido y cae algo más tarde | 1 o 2 segundos |
| Bastante | Mantiene el equilibrio quieto, pero aún no avanza | Mucho rato |
| Mucho | Da pasos torpes, a trompicones | Avanza unos metros |
| Muchísimo | Anda de forma estable y aguanta empujoncitos | Indefinidamente |

Fíjate en dos cosas. Primera: **nadie le dice qué descubrir**; solo le damos puntos por lo
que hace bien, y él va encontrando qué movimientos dan más puntos. Segunda: el camino es
**largo**. Para pasar de la primera fila a la última hacen falta **millones de intentos**.
Ningún robot real aguantaría millones de caídas... y por eso necesitaremos un truco que verás
en el apartado 8.
"""),

md(r"""## 5 · Míralo con tus propios ojos: un robot que aún NO sabe andar

Basta de palabras. Quiero enseñarte **qué aspecto tiene un robot que todavía no ha
aprendido nada**. Aquí abajo hay un humanoide dentro de un ordenador. Nadie le ha enseñado
a moverse todavía, así que hace lo único que puede hacer sin haber aprendido: **mover sus
motores al azar**, a lo loco, sin ton ni son.

No tienes que ejecutar nada. Es una animación ya grabada. Solo míralo:

![Un humanoide moviéndose al azar y desplomándose](assets/nb00_humanoide_azar.gif)

¿Lo ves? No anda: **convulsiona y se desploma** en un instante. Mover los motores al azar
no tiene nada que ver con mantener el equilibrio. Es puro temblor descoordinado, y la
gravedad lo tumba enseguida.

Para que tengas un número: lo he medido con este mismo robot moviéndose al azar, veinte veces
seguidas. **De media aguanta un tercio de segundo** antes de caerse. En ese tiempo le da tiempo
a tomar unas **22 decisiones** (este robot decide unas 67 veces por segundo), y las 22 son
completamente al azar. Ni una le sirve para nada.

Y esta es la lección de fondo, la que da sentido a todo lo que viene:

> El robot y su mundo nos los podemos dar hechos. La gravedad es la que es. Lo **único** que
> convierte a ese montón de motores temblorosos en algo que **anda de verdad** es una buena
> **política**, una buena forma de decidir. Y esa política no se escribe a mano: se
> **aprende**. Enseñarle a aprenderla es, literalmente, tu futuro trabajo.
"""),

md(r"""## 6 · El mapa completo: las seis piezas

Todo el proceso, de principio a fin, se puede dividir en **seis piezas**. Este es el mapa
de todo el curso. **No hace falta que lo entiendas del todo ahora mismo** —volverás a este
dibujo muchísimas veces, y cada pieza tendrá su propia lección—. Solo quiero que veas el
plato entero antes de empezar a cocinar.

```
   ┌────────────────────────────────────────────────────────────────┐
   │                    EL PLATO ENTERO (todo el curso)               │
   └────────────────────────────────────────────────────────────────┘

   (1) EL ROBOT                      (2) EL MUNDO DE MENTIRA
   ┌───────────────┐                 ┌────────────────────────────┐
   │      O cabeza │                 │  un mundo simulado, con     │
   │     /|\ brazos│   metido en →   │  gravedad, suelo y golpes.  │
   │      |  torso │                 │  Aquí caerse no rompe nada  │
   │     / \       │                 │  ni cuesta dinero: puede    │
   │   pie   pie   │                 │  fallar un millón de veces. │
   └───────────────┘                 └────────────────────────────┘

          ┌──────────── EL BUCLE (se repite sin parar) ────────────┐
          │                                                        │
          │  lo que percibe     (3) LA MENTE      lo que ordena    │
          │  (cómo está: ─────► (la política): ─► (a los motores:  │
          │   ángulos, si        decide qué        muévete así)    │
          │   está torcido)      hacer                 │           │
          │        ▲                                   ▼           │
          │        │        (2) el mundo aplica la física un       │
          │        │            pasito y dice cómo queda el robot  │
          │        └───────────────────────────────────┘          │
          │                          │                             │
          │                          ▼                             │
          │            (4) LA RECOMPENSA: un número que dice        │
          │                "esto lo has hecho bien / mal"          │
          └────────────────────────────────────────────────────────┘
                                     │
                                     ▼
   (5) EL ENTRENAMIENTO              (6) EL SALTO AL MUNDO REAL
   ┌────────────────────────────┐   ┌────────────────────────────┐
   │ repetir el bucle millones   │   │ coger la mente ya entrenada │
   │ de veces y, con las         │ → │ y meterla en un robot de    │
   │ recompensas, ir MEJORANDO   │   │ metal de VERDAD. La pieza   │
   │ poco a poco la política.    │   │ más difícil... y la más     │
   │                             │   │ valiosa de todas.           │
   └────────────────────────────┘   └────────────────────────────┘
```

Léelo otra vez, despacio, siguiendo las flechas. Fíjate en que el corazón de todo es **el
bucle** del medio: el robot **percibe** cómo está, la **mente** decide qué hacer, el
**mundo** aplica esa decisión y devuelve una **recompensa** que dice si estuvo bien o mal.
Ese bucle, repetido millones de veces, es lo que hace que el robot aprenda.

¿Te suena? Es lo mismo que hacías tú a la pata coja con los ojos abiertos: **notabas** que te
ibas hacia un lado (percibir), tu cuerpo **decidía** corregir (la mente), el tobillo
**empujaba** (ordenar a los músculos) y la física hacía el resto. Muchas veces por segundo.
"""),

md(r"""## 7 · Las seis piezas, una a una (versión tranquila)

Vamos a recorrer las seis piezas sin prisa. Cada una tendrá su lección completa más
adelante; aquí solo las presentamos.

**(1) El robot.** La descripción de la máquina: qué partes rígidas tiene (tronco, muslos,
pantorrillas, pies...), cómo se unen entre sí por **articulaciones** (las juntas que giran,
como tu rodilla o tu codo), qué **motores** mueven cada articulación y qué **sentidos** tiene
para notar cómo está. Lo veremos a fondo en el **NB01**.

**(2) El mundo de mentira (el simulador).** Un programa que imita la física de verdad:
gravedad, suelo, golpes, rozamiento. Le dices "los motores empujan así" y te responde
"entonces el robot queda inclinado así y el pie toca el suelo aquí". Su magia: **caerse ahí
dentro no rompe nada ni cuesta dinero**, así que el robot puede fallar millones de veces sin
problema. Es el **NB02**.

**(3) La mente (la política).** La forma de decidir del robot. Recibe lo que **percibe**
(cómo está: ángulos, velocidades, si está torcido) y responde con lo que **ordena** a los
motores. Es el **NB03**.

**(4) La recompensa.** Un número que puntúa cada instante. Por ejemplo: "+1 punto por cada
ratito que sigas de pie, más puntos si avanzas hacia delante, menos puntos si malgastas
energía". Aprender es, literalmente, **buscar la forma de decidir que consigue más puntos**.
Diseñar bien esos puntos es todo un arte, y es facilísimo que el robot te haga trampa: eso
es el **NB04**.

**(5) El entrenamiento.** Repetir el bucle un número enorme de veces y, mirando las
recompensas, **ir mejorando** poco a poco la política. Esto es lo que consume mucha potencia
de cálculo. Lo estudiaremos más adelante en el curso.

**(6) El salto al mundo real.** Coger la mente ya entrenada en el mundo de mentira y meterla
en un robot **físico**, de metal. Es la pieza más difícil (el mundo real nunca es idéntico a
la simulación) y la más valiosa para demostrar lo que sabes hacer. Es de las últimas etapas.
"""),

md(r"""## 8 · ¿Por qué en un "mundo de mentira" y no directamente en un robot real?

Es una pregunta muy razonable. Si el objetivo es un robot de verdad, ¿por qué no le
enseñamos directamente con el robot de verdad? Por cuatro motivos de peso:

- **Caerse sale gratis.** Aprender exige fallar muchísimo. En un robot real, cada caída
  puede romper piezas que cuestan mucho dinero. En el mundo de mentira, el robot se cae un
  millón de veces y no pasa absolutamente nada.
- **Va mucho más rápido que la vida real.** El ordenador puede simular horas de práctica en
  segundos, y hacer practicar a **muchos robots a la vez**.
- **Se puede repetir igual.** Puedes rebobinar y repetir exactamente el mismo intento para
  entender qué pasó. En la vida real eso es imposible.
- **Es seguro.** Un robot pesado moviéndose al azar es peligroso. En simulación no hay
  riesgo para nadie.

Para que veas la diferencia de escala: si un robot real se cayera una vez cada 10 segundos y
tuviera que hacerlo un millón de veces, necesitaría unos **115 días** practicando sin parar ni
un minuto (y estaría destrozado mucho antes). En simulación, con miles de robots de mentira
practicando a la vez y más deprisa que el tiempo real, ese millón de caídas puede llevar
**minutos**.

Por eso casi todo el aprendizaje ocurre en el mundo de mentira, y solo **al final** damos el
salto al robot físico. A ese salto se le llama **sim-to-real** ("de la simulación a lo
real"), y es la pieza (6) del mapa.
"""),

md(r"""## 9 · ¿Y en qué consiste el trabajo, en el día a día?

Quizá te preguntes qué hace exactamente una persona que se dedica a esto. Spoiler: casi
**nunca** escribe "dobla la rodilla 30 grados". Su trabajo se parece más al de un
**entrenador deportivo** que al de alguien que da órdenes. Cosas que hace a diario:

- **Preparar el entrenamiento**: elegir qué robot, en qué mundo, con qué suelo, con qué
  empujones.
- **Diseñar los premios**: decidir qué cosas dan puntos y cuáles los quitan, para que el
  robot aprenda lo que queremos (y no una trampa).
- **Mirar vídeos de fallos**: ver cómo se cae el robot, entender por qué, y cambiar algo.
- **Medir**: comprobar con números si el robot de hoy es mejor que el de ayer.
- **Llevarlo a la realidad**: hacer que lo aprendido en el ordenador funcione en el robot de
  metal.

Es un trabajo de **paciencia, observación y experimentos**, más que de genialidad. Y todo eso
se aprende.
"""),

md(r"""## 10 · El plan del viaje

Para que veas que hay un camino ordenado por delante, aquí tienes las grandes etapas. No
te aprendas esto; es solo para que sepas que cada pieza del mapa tiene su momento.

| Etapa | Qué conseguirás |
|---|---|
| **Ahora** (Parte 0) | Entender de qué va todo esto, sin código: el robot, el mundo, la mente, la recompensa. |
| Después | Dar tus primeros pasos con el ordenador y con las matemáticas, desde cero y en gotas. |
| Más adelante | Construir "mentes" (redes neuronales) y enseñarlas a decidir (aprendizaje por refuerzo). |
| Luego | El cuerpo del robot a fondo, y entrenar de verdad a un bípedo a andar. |
| Al final | El salto al mundo real y un portafolio con el que demostrar lo que sabes hacer. |

Lo importante ahora no es la tabla, sino esto: **empezamos por entenderlo todo con calma, y
el código y las matemáticas vendrán poco a poco, cuando ya tengas claro para qué sirven.**
"""),

md(r"""## 11 · Resumen de la lección

Si solo te quedaras con cinco frases de hoy, que sean estas:

1. Vas a aprender a crear **la parte que decide cómo se mueve** un robot de dos piernas.
2. Andar es difícil porque un bípedo es **inestable** (como una escoba en la mano) y tiene que
   **corregir sin parar**; además, andar es una **caída controlada**.
3. La receta de andar **no se puede escribir a mano**: es demasiado grande y cambiante.
4. Por eso el robot **aprende probando** (aprendizaje por refuerzo), guiado por **premios**, y
   lo que aprende es su **política**: su forma de decidir.
5. Practica en un **mundo de mentira** (simulador) porque allí caerse es gratis, rápido y
   seguro; al final se da el **salto al mundo real**.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Humanoide** | Robot con forma de persona: dos piernas, dos brazos, tronco y cabeza. |
| **Bípedo** | Que anda sobre dos piernas. |
| **Inestable** | Que se cae solo si no se corrige sin parar (la escoba en la mano). |
| **Aprendizaje por refuerzo** | Aprender probando, guiado por premios y castigos. |
| **Política** | La forma que tiene el robot de decidir qué hacer en cada momento. |
| **Recompensa** | El número (los "puntos") que le dice al robot si lo está haciendo bien. |
| **Simulador** | Un "mundo de mentira" dentro del ordenador que imita la física. |
| **Sim-to-real** | El salto de lo aprendido en simulación a un robot real. |
"""),

md(r"""## 12 · Preguntas de comprensión

Intenta responder con tus propias palabras **antes** de abrir cada solución. Una respuesta
tuya, aunque esté a medias, vale mucho más que una copiada.

**P1.** ¿Por qué decimos que un robot de dos piernas es "inestable por naturaleza"? Usa la
comparación con el coche parado.

**P2.** ¿Por qué no se puede simplemente *escribir a mano* la receta de cómo andar?

**P3.** Explica con tus palabras qué es la **política** (la "mente") de un robot.

**P4.** En la animación del apartado 5, el robot movía sus motores al azar. ¿Por qué se
caía enseguida?

**P5.** Da **dos** razones por las que entrenamos al robot en un "mundo de mentira" en vez
de en un robot real desde el principio.

**P6.** En el experimento de la pata coja, ¿por qué crees que cuesta mucho más mantener el
equilibrio con los ojos cerrados? ¿Qué nos dice eso sobre lo que necesita un robot?

**P7.** Si un robot de ruedas es más fácil y más barato, ¿por qué se insiste tanto en hacer
robots con dos piernas?

**P8.** ¿Qué significa la frase "andar es caerse con estilo"?
"""),

md(r"""<details>
<summary>▶ Solución P1</summary>

Porque tiene casi todo su peso arriba (tronco, cabeza) apoyado sobre una base muy pequeña
(dos pies, o incluso uno solo al dar un paso). La gravedad tiende a tumbarlo, así que
necesita **corregir su postura sin parar**, como el palo de escoba sobre la palma de la
mano. Un coche parado, en cambio, tiene el peso bajo y una base ancha (cuatro ruedas
separadas): se queda quieto él solo, sin corregir nada. El bípedo necesita control
constante; el coche no.
</details>

<details>
<summary>▶ Solución P2</summary>

Porque harían falta **millones** de instrucciones para cubrir todas las situaciones
posibles (suelo liso, resbaladizo, con escalones, con empujones...), esas instrucciones
**cambian a cada instante** y dependen unas de otras. Es demasiado grande y demasiado
cambiante para que una persona lo escriba a mano. Ni siquiera tú sabrías escribirla, aunque
andes todos los días. Por eso, en vez de escribirlo, dejamos que el robot lo **aprenda
probando**.
</details>

<details>
<summary>▶ Solución P3</summary>

La política es la **forma que tiene el robot de decidir qué hacer** en cada momento. Recibe
información de cómo está (lo que percibe) y decide qué órdenes dar a sus motores. Al
principio decide fatal (por eso se cae); a base de practicar millones de veces, va decidiendo
cada vez mejor, hasta que anda.
</details>

<details>
<summary>▶ Solución P4</summary>

Porque mover los motores al azar no tiene ninguna relación con mantener el equilibrio ni con
avanzar. Es puro temblor descoordinado. Como el robot es inestable por naturaleza y no está
corrigiendo su postura de forma útil, la gravedad lo tumba en un instante (de media, en un
tercio de segundo). Eso es justo lo que se ve: no anda, convulsiona y cae.
</details>

<details>
<summary>▶ Solución P5</summary>

Cualquiera de estas dos (o más): (1) **caerse sale gratis** —en un robot real cada caída
rompe piezas caras, en el simulador no cuesta nada—; (2) **va mucho más rápido** y se pueden
entrenar muchos robots a la vez; (3) **se puede repetir exactamente** el mismo intento;
(4) es **seguro** (un robot real moviéndose al azar es peligroso).
</details>

<details>
<summary>▶ Solución P6</summary>

Porque al cerrar los ojos **pierdes información** sobre cómo está tu cuerpo respecto al
mundo: ya no ves si te estás inclinando. Te quedan otros sentidos (el oído interno, la planta
del pie), pero con menos información corriges peor. La lección para el robot es que, para
mantener el equilibrio, **necesita sentidos** que le digan cómo está (si se inclina, cómo
están sus articulaciones, si el pie toca el suelo). Sin buena información, no hay buena
decisión.
</details>

<details>
<summary>▶ Solución P7</summary>

Porque **el mundo está construido para personas**: escaleras, bordillos, puertas, pomos,
herramientas, pasillos... Las ruedas se atascan en un escalón; las piernas lo suben. En vez de
rehacer el mundo para los robots, es más práctico hacer robots con forma humana que encajen en
el mundo tal como es. El precio es que andar sobre dos piernas es mucho más difícil.
</details>

<details>
<summary>▶ Solución P8</summary>

Que al andar no estás todo el rato en equilibrio quieto, sino que **te inclinas hacia
delante, empiezas a caer y pones el otro pie justo a tiempo** para recogerte, una y otra vez.
Cada paso es una pequeña caída controlada. Por eso un robot que anda tiene que atreverse a
"caerse un poco a propósito" y recogerse a tiempo, lo cual es todavía más delicado que estar
quieto de pie.
</details>
"""),

md(r"""## 13 · 🛠 Práctica en MuJoCo: enciende tu primer robot

Hasta ahora solo has leído. Ahora vas a **poner en marcha un robot de verdad** dentro del
ordenador. No vas a escribir nada: el código ya está escrito. Tu trabajo es **ejecutarlo,
mirar lo que pasa y cambiar un número**. Entender cada palabra del código vendrá más adelante;
hoy basta con saber **qué hace** cada trozo, y eso te lo cuento en castellano.

### ¿Qué es MuJoCo?

**MuJoCo** (se pronuncia *mu-yó-co*) es un **simulador de física**: un programa que calcula,
paso a paso, cómo se mueven unos cuerpos que tienen peso, articulaciones y motores, y que
chocan con el suelo. Es exactamente el "mundo de mentira" de la sección 8. El nombre viene del
inglés *Multi-Joint dynamics with Contact*: "movimiento de cosas con muchas articulaciones que
se tocan".

Un poco de historia, para que sepas con qué estás trabajando:

- Lo creó el investigador **Emo Todorov** hacia 2012, precisamente para estudiar cómo
  controlar cuerpos con articulaciones (personas, animales, robots).
- En **2021 lo compró DeepMind** (el laboratorio de inteligencia artificial de Google) y en
  **2022 lo liberó gratis y con el código abierto**, para que cualquiera pueda usarlo.
- Hoy es **el simulador más usado** para enseñar a robots a moverse con aprendizaje por
  refuerzo. El humanoide que viste en la sección 5 es, de hecho, un robot de MuJoCo.

Dominar MuJoCo es la habilidad central de este curso. Empezamos ya.

### Cómo se ejecuta una celda de código

Las cajas grises de abajo son **celdas de código**. Para ejecutar una:

1. Haz clic dentro de la celda.
2. Pulsa **Mayúsculas + Intro** (Shift + Enter) a la vez.
3. Mientras trabaja, a la izquierda aparece `[*]`. Cuando termina, sale un número, como `[1]`,
   y **debajo de la celda** aparece el resultado.

Ejecútalas **en orden, de arriba abajo**: cada una usa cosas que preparó la anterior.
"""),

md(r"""### Paso 1 · Despertar a MuJoCo

Esta primera celda **carga las herramientas**: MuJoCo y un ayudante llamado `taller` que he
preparado para que las prácticas sean cómodas (sacar fotos, hacer vídeos...). Al ejecutarla
debería decirte qué versión de MuJoCo tienes. Si sale un número, **todo funciona**.
"""),

code(r"""import mujoco
import taller

print("MuJoCo está listo. Versión:", mujoco.__version__)"""),

md(r"""### Paso 2 · Cargar el robot: el plano y el estado

Ahora cargamos el **humanoide**. Aquí aparece la idea más importante de MuJoCo, y la vas a ver
en **todas** las lecciones del curso. Para simular algo, MuJoCo guarda dos cosas separadas:

- **El modelo** (`modelo`): el **plano** del robot. Qué piezas tiene, cuánto pesa cada una,
  cómo se unen, qué motores lleva. Es como las instrucciones de montaje de un mueble: **no
  cambia** mientras simulas.
- **Los datos** (`datos`): el **estado de ahora mismo**. Dónde está cada pieza en este
  instante, a qué velocidad se mueve, qué están haciendo los motores, qué hora marca el reloj
  de la simulación. Esto **cambia en cada instante**.

Una forma de recordarlo: el modelo es **la partitura**; los datos son **por qué nota va la
orquesta ahora**.
"""),

code(r"""modelo, datos = taller.cargar("humanoide")

print("Robot cargado.")"""),

md(r"""### Paso 3 · Una foto

Esta celda le hace una **foto** al humanoide tal como está ahora: recién colocado, de pie, con
el reloj de la simulación a cero. Todavía no ha pasado ni un instante.
"""),

code(r"""taller.foto(modelo, datos, titulo="El humanoide, antes de empezar");"""),

md(r"""### Paso 4 · Que pase el tiempo: el robot "desmayado"

Simular es **hacer avanzar el reloj** y dejar que MuJoCo calcule qué pasa. La celda de abajo
avanza **3 segundos** con los motores **apagados** (como una persona que se desmaya) y graba
un vídeo.

Fíjate en lo que **nadie** ha programado: nadie le ha dicho "cae hacia aquí" ni "dobla esta
rodilla". MuJoCo solo conoce el plano (pesos, articulaciones) y la gravedad, y de ahí **sale
solo** cómo se derrumba. Eso es un simulador de física.
"""),

code(r"""modelo, datos = taller.cargar("humanoide")          # robot nuevo, recién colocado

taller.video(modelo, datos, segundos=3, nombre="nb00_desmayado");"""),

md(r"""### Paso 5 · Motores al azar: tu propia versión del GIF de la sección 5

Ahora el mismo experimento, pero con los **17 motores moviéndose al azar**, como el robot de
la sección 5. La diferencia es que **ese vídeo lo estás fabricando tú**, ahora, en tu ordenador.

El número `semilla=0` decide **qué** azar le toca: con la misma semilla, el "azar" sale siempre
igual (por eso se puede repetir un experimento exactamente, ¿recuerdas la sección 8?).
"""),

code(r"""modelo, datos = taller.cargar("humanoide")

taller.video(modelo, datos, segundos=3, control=taller.al_azar(semilla=0), nombre="nb00_al_azar");"""),

md(r"""### Tus retos

Solo tienes que **cambiar un número** dentro de la celda y volver a ejecutarla
(Mayúsculas + Intro). No puedes romper nada: si algo sale raro, vuelve a poner el número de
antes.

**Reto 1.** En la celda del Paso 5, cambia `semilla=0` por `semilla=7`. ¿Cae igual?

**Reto 2.** En la celda del Paso 4, cambia `segundos=3` por `segundos=1`. ¿Qué ves al final
del vídeo?

**Reto 3 (para pensar).** Comparando los dos vídeos: ¿quién cae **antes**, el robot
"desmayado" o el que mueve los motores al azar? ¿Por qué crees que pasa?

<details>
<summary>▶ Solución Reto 1</summary>

Cae **de otra manera**: con otra semilla los motores reciben otras órdenes al azar, así que
convulsiona distinto y acaba en otra postura. Pero el final es el mismo: **al suelo**. Y si
vuelves a poner `semilla=7`, sale **exactamente** el mismo vídeo otra vez. En MuJoCo, el mismo
plano + el mismo punto de partida + las mismas órdenes = el mismo resultado, siempre.
</details>

<details>
<summary>▶ Solución Reto 2</summary>

El vídeo dura solo un segundo y se corta **a mitad de la caída**: el robot todavía no ha
llegado al suelo. Con los motores apagados, la cabeza tarda unos **0,6 segundos** en bajar de
1 metro de altura, y un poco más en tumbarse del todo. `segundos` es simplemente **cuánto
tiempo de mundo de mentira** le pides a MuJoCo que calcule.
</details>

<details>
<summary>▶ Solución Reto 3</summary>

Lo he medido: el "desmayado" baja de 1 metro a los **0,6 s**; el que se mueve al azar, a los
**0,26-0,31 s** (según la semilla). ¡El azar cae **el doble de rápido**! Moverse al azar no
solo no ayuda: **empuja** el cuerpo en direcciones absurdas y lo tira antes. Es la lección de
la sección 5 vista con números: sin una buena **política**, mover los motores es peor que no
moverlos. El trabajo de todo el curso es encontrar esa política.
</details>

### Qué has aprendido de MuJoCo hoy

- **MuJoCo** es el simulador de física de Google DeepMind: el mundo de mentira donde entrenaremos.
- Todo en MuJoCo se apoya en dos piezas: **el modelo** (el plano, fijo) y **los datos** (el
  estado de ahora, que cambia).
- **Simular** = hacer avanzar el reloj y dejar que la física decida qué pasa.
- La misma **semilla** da el mismo resultado: los experimentos se pueden repetir.

En la práctica del NB01 abrirás el **modelo** del humanoide y contarás sus piezas, sus
articulaciones y sus motores, uno a uno.
"""),


md(r"""## 14 · Posdata

Si en algún momento te has perdido, dime el **número de apartado** y la **frase exacta**
donde te atascaste, y lo reescribo de otra manera. Recuerda: si algo no se entiende, la
culpa es del texto, no tuya.

En el **NB01** nos meteremos dentro de la primera pieza del mapa: **el cuerpo del robot**.
Veremos qué son exactamente las partes rígidas, las articulaciones, los motores y los
sentidos, comparando todo el rato con tu propio cuerpo. Y descubriremos un detalle que
explica, por fin, por qué andar es tan difícil: **el robot no está atornillado a nada**.
La lección seguirá sin código, salvo su práctica en MuJoCo: allí **desmontarás el humanoide de
hoy** y contarás sus piezas, sus articulaciones y sus motores.

Hasta aquí la primera lección. Tómate un respiro: acabas de entender, a grandes rasgos,
**todo el problema** que vas a resolver en los próximos meses. No es poco.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB00_que_vamos_a_hacer.ipynb")
    build(out, cells, title="NB00 · ¿Qué vamos a hacer y por qué es difícil?")
