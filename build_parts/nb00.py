"""Construye NB00 · ¿Qué vamos a hacer y por qué es difícil?

Primer notebook de la ruta nueva: 100% conceptual, CERO código.
Todo prosa, analogías y diagramas. El robot se ve como un GIF ya hecho
(imagen en markdown), sin pedirle al lector ejecutar ni entender nada.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, build

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

En esta primera lección **no vas a tocar el ordenador para nada**. No hay código, no hay
que ejecutar, no hay que instalar. Solo se lee, como quien lee la primera página de un
libro. Lo único que quiero es que salgas de aquí entendiendo **qué vamos a hacer** y
**por qué es un problema tan bonito y tan difícil**.

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
mismo. Si en algún momento lees algo y piensas *"¿y esto qué es?"*, casi seguro que la
respuesta está una o dos líneas más abajo. Y si no está, es culpa del texto, no tuya.

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

Ya está. Con eso en la cabeza, empecemos por el principio de todo: el sueño.
"""),

md(r"""## 2 · El sueño: una máquina que anda como tú

Seguramente has visto vídeos de robots humanoides: máquinas con dos piernas, dos brazos y
una cabeza que caminan, suben escaleras, se mantienen de pie cuando alguien las empuja e
incluso corren o bailan. Parece ciencia ficción, pero es real, y cada año se acercan más a
moverse como una persona.

Detrás de cada uno de esos robots hay alguien que le ha **enseñado a moverse**. Ese
"alguien" es justo lo que tú vas a aprender a ser. No a fabricar el robot con tornillos y
cables (eso es otro oficio), sino a crear **la parte que decide cómo moverse**: su forma de
mantener el equilibrio, de dar un paso, de no caerse. Digamos que vas a construir **el
cerebro del movimiento**.

Y aquí viene la primera sorpresa: aunque tú andas sin pensar, enseñar a andar a una máquina
es uno de los problemas **más difíciles** que existen. Vamos a ver por qué.
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
aprende. Aquí el "perro" es el robot.

Y a la **manera de decidir** que el robot va afinando —su "así es como yo elijo qué hacer en
cada momento"— la llamaremos su **política**. No te preocupes por la palabra ahora; volverá
muchas veces. Quédate solo con la idea:

> **política = la forma que tiene el robot de decidir qué hacer.** Empieza siendo pésima y,
> a base de practicar, se vuelve buena.
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
gravedad lo tumba enseguida (aguantó menos de medio segundo antes de caer).

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
"""),

md(r"""## 7 · Las seis piezas, una a una (versión tranquila)

Vamos a recorrer las seis piezas sin prisa. Cada una tendrá su lección completa más
adelante; aquí solo las presentamos.

**(1) El robot.** La descripción de la máquina: qué partes rígidas tiene (tronco, muslos,
pantorrillas, pies...), cómo se unen entre sí por **articulaciones** (las juntas que giran,
como tu rodilla o tu codo) y qué **motores** mueven cada articulación. Lo veremos a fondo en
el **NB01**.

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

Por eso casi todo el aprendizaje ocurre en el mundo de mentira, y solo **al final** damos el
salto al robot físico. A ese salto se le llama **sim-to-real** ("de la simulación a lo
real"), y es la pieza (6) del mapa.
"""),

md(r"""## 9 · El plan del viaje

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

md(r"""## 10 · Preguntas de comprensión

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
cambiante para que una persona lo escriba a mano. Por eso, en vez de escribirlo, dejamos
que el robot lo **aprenda probando**.
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
corrigiendo su postura de forma útil, la gravedad lo tumba en un instante. Eso es justo lo
que se ve: no anda, convulsiona y cae.
</details>

<details>
<summary>▶ Solución P5</summary>

Cualquiera de estas dos (o más): (1) **caerse sale gratis** —en un robot real cada caída
rompe piezas caras, en el simulador no cuesta nada—; (2) **va mucho más rápido** y se pueden
entrenar muchos robots a la vez; (3) **se puede repetir exactamente** el mismo intento;
(4) es **seguro** (un robot real moviéndose al azar es peligroso).
</details>
"""),

md(r"""## 11 · Posdata

Si en algún momento te has perdido, dime el **número de apartado** y la **frase exacta**
donde te atascaste, y lo reescribo de otra manera. Recuerda: si algo no se entiende, la
culpa es del texto, no tuya.

En el **NB01** nos meteremos dentro de la primera pieza del mapa: **el cuerpo del robot**.
Veremos qué son exactamente las partes rígidas, las articulaciones y los motores, comparando
todo el rato con tu propio cuerpo. Seguirá sin haber nada de código: solo entender bien de
qué está hecho un robot antes de intentar moverlo.

Hasta aquí la primera lección. Tómate un respiro: acabas de entender, a grandes rasgos,
**todo el problema** que vas a resolver en los próximos meses. No es poco.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB00_que_vamos_a_hacer.ipynb")
    build(out, cells, title="NB00 · ¿Qué vamos a hacer y por qué es difícil?")
