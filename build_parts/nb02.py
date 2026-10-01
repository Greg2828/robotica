"""Construye NB02 · El mundo de mentira: qué es un simulador (conceptual, 0 código).

Pieza (2) del mapa. Qué es un simulador, física desde cero (fuerza, masa e inercia,
velocidad y aceleración, gravedad, choque, rozamiento), el tiempo a saltitos (paso
de simulación) con una pelota calculada a mano (Euler semi-implícito, g≈10), por
qué el paso debe ser pequeño, dos ritmos (física vs decisiones), ventajas, MuJoCo
y la brecha de realidad con sus remedios (aleatorizar el mundo).

Datos verificados del Humanoid-v5: paso de física 0,003 s, decide cada 5 pasos
(0,015 s ≈ 67 decisiones/s).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, build

cells = [

md(r"""# NB02 · El mundo de mentira: qué es un simulador

**Parte 0 · El terreno — Lección 3**

> En el **NB00** viste el mapa entero. En el **NB01** desmontaste el **cuerpo** del robot:
> piezas rígidas, articulaciones, motores, sensores; descubriste que está suelto
> (subactuado) y que su equilibrio depende del centro de masas; y viste que todo eso se
> guarda en un "plano de montaje". Hoy toca la pieza (2): **quién coge ese plano y le da
> vida** poniéndole gravedad, suelo y golpes. Eso es el **simulador**.

Como siempre en esta Parte 0, **cero código**. Solo entender. De paso vamos a explicar desde
cero un poco de **física** (qué es una fuerza, por qué las cosas que se mueven siguen
moviéndose, qué es la velocidad, la gravedad, el rozamiento) y una idea muy importante: que en
el simulador **el tiempo avanza a saltitos**. Incluso vamos a hacer, a mano y con sumas
sencillas, exactamente lo mismo que hace un simulador por dentro. Tranquilo: todo con ejemplos
de la vida diaria, y las cuentas son de primaria.
"""),

md(r"""## 1 · ¿Qué es un simulador?

Un **simulador** es un programa que **imita la física del mundo real dentro del ordenador**.
Es, literalmente, un **mundo de mentira**: hay gravedad, hay un suelo, las cosas chocan, se
caen, ruedan y rozan, igual que en la realidad... pero todo ocurre en números, dentro de la
máquina.

Seguro que ya conoces uno sin saberlo: **cualquier videojuego** donde una pelota rueda por
una cuesta, un coche derrapa o un personaje salta y cae. Detrás de eso hay un simulador
calculando cómo se mueven las cosas (en los videojuegos se le llama "motor de física"). Nosotros
usaremos uno mucho más preciso, pensado para robots, pero la idea es la misma: **un mundo falso
que se comporta como el de verdad**.

¿Y para qué queremos un mundo falso? Recuerda el NB00: para que el robot pueda **practicar y
caerse un millón de veces sin que pase nada**. En el mundo real, cada caída rompe piezas
caras; en el mundo de mentira, caerse no cuesta absolutamente nada. Ese es el superpoder del
simulador, y por eso es una de las seis piezas del mapa.

De hecho, aquel robot que viste desplomarse en el GIF del NB00 **estaba dentro de un
simulador**. Lo que viste era, precisamente, un mundo de mentira en marcha.
"""),

md(r"""## 2 · Un poco de física, desde cero (primera parte)

Para entender qué "imita" el simulador, hace falta saber qué imita. Empezamos por las tres
ideas que explican **por qué y cómo se mueven las cosas**. Explicadas como si nunca hubieras
oído hablar de ellas (porque no hace falta).

**Fuerza = un empujón o un tirón.** Una fuerza es cualquier cosa que empuja o tira de un
objeto y **cambia cómo se mueve**. Cuando empujas una puerta, aplicas una fuerza. Cuando tiras
de una cuerda, también. Un motor del robot, al retorcer una articulación, también aplica
fuerzas.

**Velocidad = lo deprisa que vas, y hacia dónde.** Es lo que marca el velocímetro de un coche:
"voy a 50 kilómetros por hora". Pero ojo, la velocidad tiene también **dirección**: no es lo
mismo ir a 50 hacia el norte que a 50 hacia el sur. En este curso la mediremos casi siempre en
**metros por segundo** (cuántos metros avanzas en un segundo). Andando, una persona va a algo
más de 1 metro por segundo.

**Masa = cuánta "cosa" tiene un objeto, cuánto cuesta moverlo.** Empujar un carrito de la
compra vacío es fácil; empujarlo lleno de botellas de agua cuesta mucho más. El carrito lleno
tiene más **masa**. (En el día a día decimos "peso", y se mide en kilos; para nosotros, por
ahora, es lo mismo.)
"""),

md(r"""### La inercia: las cosas son "perezosas"

Ahora la idea de física más importante de hoy. Prepárate, porque va en contra de lo que parece.

Piensa en estas tres situaciones:

- Vas de pie en un **autobús** y el conductor frena de golpe. ¿Qué te pasa? Te vas **hacia
  delante**. Nadie te ha empujado hacia delante: es tu cuerpo, que **quería seguir moviéndose**
  a la misma velocidad que el autobús.
- El autobús arranca de golpe. Te vas **hacia atrás**. Tu cuerpo **quería seguir quieto**.
- Lanzas una pelota en una pista de hielo. Se desliza y se desliza, y tarda muchísimo en pararse.
  Si no hubiera **nada** que la frenara, **no se pararía nunca**.

Esa "pereza" de las cosas a cambiar su movimiento se llama **inercia**, y es una de las leyes
fundamentales de la física (la descubrió Isaac Newton hace más de 300 años):

> **Un objeto sigue haciendo lo que estaba haciendo** —quedarse quieto, o moverse en línea recta
> a la misma velocidad— **a menos que una fuerza lo obligue a cambiar.**

¿Y por qué en la vida diaria parece que las cosas "se paran solas"? Porque casi siempre hay
alguna fuerza frenándolas que no vemos: el rozamiento con el suelo, el aire... En el hielo hay
muy poco rozamiento, y por eso ahí se ve tan claro.

Y cuanta más **masa** tiene algo, más perezoso es: más cuesta ponerlo en marcha y más cuesta
pararlo. Parar una bici es fácil; parar un camión, no.

**Para el robot esto es crucial.** Su torso pesa mucho. Si empieza a caerse hacia un lado, la
inercia hace que **siga cayendo** aunque los motores ya estén intentando corregir. Por eso hay
que corregir **pronto**, antes de que la caída coja velocidad. Es exactamente lo que sentías
con la escoba en la mano: si la corriges tarde, ya no hay quien la pare.
"""),

md(r"""### Fuerza → velocidad → posición: la cadena de oro

Juntemos las piezas. Esta cadena es, ni más ni menos, **lo que calcula un simulador**:

```
     FUERZA  ───cambia───►  VELOCIDAD  ───cambia───►  POSICIÓN
   (empujón)               (lo deprisa que           (dónde está)
                            va y hacia dónde)
```

- Una **fuerza no mueve las cosas directamente**: lo que hace es **cambiar su velocidad**
  (acelerarlas, frenarlas o desviarlas). A ese cambio de velocidad se le llama **aceleración**.
  Cuando pisas el acelerador de un coche, no lo "mueves": cambias su velocidad.
- La **velocidad** es la que va cambiando la **posición**: si vas a 2 metros por segundo, cada
  segundo estás 2 metros más allá.
- Y la **masa** decide cuánto cambia la velocidad con una misma fuerza: el mismo empujón acelera
  mucho un carrito vacío y poquito un carrito lleno.

Si una fuerza deja de actuar, la velocidad **no vuelve a cero**: se queda como estaba (inercia).
Lo que desaparece es el *cambio*.

Quédate con la cadena; dentro de un momento la vamos a usar con números.
"""),

md(r"""## 3 · Un poco de física, desde cero (segunda parte)

Ahora las fuerzas concretas que más le importan a un robot que anda.

**Gravedad = el tirón hacia el suelo.** La gravedad es una fuerza especial: **tira de todo
hacia abajo**, hacia el suelo, sin parar. Es la razón de que las cosas caigan cuando las
sueltas y de que tú no salgas flotando. Para un robot es su gran enemiga: la gravedad está
siempre intentando tumbarlo.

Un dato para dentro de un rato: en la Tierra, la gravedad hace que cualquier cosa que cae (si
el aire no la frena mucho) **gane unos 10 metros por segundo de velocidad cada segundo**. Al
soltar una piedra: al cabo de 1 segundo cae a 10 m/s; al cabo de 2, a 20 m/s; y así. (El número
exacto es 9,8, pero 10 es más cómodo para hacer cuentas de cabeza.)

**Choque (colisión) = dos cosas sólidas no se atraviesan.** Cuando dos objetos duros se
encuentran, **chocan**: no pueden ocupar el mismo sitio, así que se frenan o rebotan. Esto es
importantísimo para un robot: su **pie choca con el suelo** y se apoya en él en vez de
atravesarlo. Sin choques, el robot se hundiría en el suelo como un fantasma. Y recuerda del
NB01: como el robot está suelto, **el suelo empujando sus pies es lo único que puede mover su
cuerpo**. El choque pie-suelo no es un detalle; es el centro de todo.

**Rozamiento (fricción) = la resistencia al resbalar.** Cuando dos superficies se tocan y una
intenta deslizarse sobre la otra, aparece una resistencia que lo dificulta: el **rozamiento**.
Es lo que hace que tus zapatos **agarren** el suelo y no resbales al andar. Sobre hielo hay
poquísimo rozamiento, y por eso patinas. Para un robot, el rozamiento entre el pie y el suelo
es lo que le permite empujar para avanzar sin que el pie se le vaya.

Un simulador, en el fondo, no es más que un programa que **tiene en cuenta todas estas cosas
(y algunas más) para calcular qué le pasa al robot en cada momento**.
"""),

md(r"""## 4 · La idea clave: el tiempo avanza "a saltitos"

Aquí viene una idea nueva y muy importante, así que vamos despacio.

En el mundo real, el tiempo fluye de forma **continua**, sin cortes. Pero un ordenador no
puede calcular "todos los instantes", porque son infinitos. ¿Qué hace entonces? Un truco muy
inteligente: **avanza el mundo a saltitos pequeñísimos**.

La mejor analogía es un **cuaderno de dibujos animados** (un *flip-book*): esos cuadernos con
un dibujo en cada página, casi igual al anterior, que al pasar las páginas rápido **parecen
moverse**. Los dibujos animados y el cine funcionan igual: son muchas **fotos fijas**
seguidas que, al pasar deprisa, nuestro ojo ve como movimiento (el cine usa 24 fotos por
segundo).

El simulador hace exactamente eso con el robot:

```
   El mundo NO avanza de golpe, sino en saltitos minúsculos:

   estado 0  --pasito-->  estado 1  --pasito-->  estado 2  --pasito-->  ...
    (foto)                 (foto)                  (foto)

   Como un cuaderno de dibujos: muchas fotos casi iguales que,
   una detrás de otra, forman el movimiento.
```

A cada una de esas "fotos" se le llama el **estado** del mundo: la descripción completa de cómo
está todo en ese instante (dónde está cada pieza, cuánto está doblada cada articulación y a qué
velocidad se mueve todo). Y a cada salto de una foto a la siguiente se le llama un **paso de
simulación** (en inglés, *timestep*). Guarda esta palabra, **paso**, porque va a aparecer
constantemente: entrenar será, literalmente, dar millones de estos pasitos.

¿Y cómo de pequeño es un pasito? **Muy** pequeño. En el humanoide de práctica del curso, cada
paso representa **3 milésimas de segundo**. Es decir, para simular **un solo segundo** de vida
del robot, el simulador calcula unas **333 fotos**. ¡Catorce veces más que el cine!
"""),

md(r"""## 5 · Calculemos el futuro a mano: una pelota que cae

Vamos a hacer, con lápiz y papel, **exactamente** lo que hace un simulador por dentro. Así
perderás el miedo para siempre: un simulador no es magia, es la cadena de oro aplicada una y
otra vez.

**El problema.** Soltamos una pelota desde **2 metros** de altura. Queremos saber dónde está en
cada momento. Para que las cuentas salgan fáciles usaremos:

- Gravedad: la pelota gana **10 m/s** de velocidad hacia abajo cada segundo.
- Pasos **grandes**, de **0,1 segundos** (una décima). En cada pasito la pelota gana, por tanto,
  10 × 0,1 = **1 m/s** más de velocidad.

**La receta de cada pasito** (la cadena de oro):

1. La fuerza (gravedad) cambia la velocidad: **velocidad nueva = velocidad + 1**.
2. La velocidad cambia la posición: en 0,1 segundos baja **velocidad × 0,1** metros. Así que
   **altura nueva = altura − velocidad nueva × 0,1**.

**Empezamos:** en el instante 0, la pelota está a 2 m y quieta (velocidad 0). Y ahora, pasito
a pasito:

| Paso | Tiempo (s) | Velocidad (m/s) | Cuánto baja en este paso (m) | Altura (m) |
|---|---|---|---|---|
| 0 | 0,0 | 0 | — | **2,00** |
| 1 | 0,1 | 0 + 1 = 1 | 1 × 0,1 = 0,10 | 2,00 − 0,10 = **1,90** |
| 2 | 0,2 | 1 + 1 = 2 | 2 × 0,1 = 0,20 | 1,90 − 0,20 = **1,70** |
| 3 | 0,3 | 2 + 1 = 3 | 3 × 0,1 = 0,30 | 1,70 − 0,30 = **1,40** |
| 4 | 0,4 | 3 + 1 = 4 | 4 × 0,1 = 0,40 | 1,40 − 0,40 = **1,00** |
| 5 | 0,5 | 4 + 1 = 5 | 5 × 0,1 = 0,50 | 1,00 − 0,50 = **0,50** |
| 6 | 0,6 | 5 + 1 = 6 | 6 × 0,1 = 0,60 | 0,50 − 0,60 = **−0,10** ⚠ |

Mira la tabla con calma, fila a fila. Solo hay **sumas y multiplicaciones por 0,1**. Y sin
embargo, acabas de **predecir el futuro** de una pelota. Fíjate también en la inercia
funcionando: la velocidad **nunca vuelve atrás**, solo se va acumulando, y por eso la pelota
cae cada vez más deprisa (baja 10 cm en el primer paso y 60 cm en el sexto).

Pero hay **dos cosas raras** en la tabla. ¿Las ves? Vamos con ellas.
"""),

md(r"""### Rareza 1: ¡la pelota ha atravesado el suelo!

En el paso 6, la altura sale **−0,10 metros**: diez centímetros **por debajo del suelo**. Las
cuentas, a ciegas, no saben que existe un suelo. Por eso el simulador, en cada paso, además de
la cadena de oro, hace otra cosa: **comprueba si algo se está metiendo dentro de otra cosa**.
Si la pelota ha entrado en el suelo, la saca y aplica la fuerza del **choque** (y la frena o la
hace rebotar). Es la parte del simulador que se encarga de las **colisiones**, y en un robot
que anda está trabajando sin parar: cada vez que un pie toca el suelo.

### Rareza 2: los números no son exactos

La física real (la que estudiarías en el instituto con una fórmula) dice que a los **0,5
segundos** la pelota debería estar a **0,75 metros**. Nuestra tabla dice **0,50**. ¡Hemos
fallado por 25 centímetros!

¿Por qué? Porque dimos **saltos demasiado grandes**. En la realidad, la velocidad crece poco a
poco, de forma continua, durante toda la décima de segundo. Nosotros hicimos como si cambiara
de golpe al principio de cada paso. Con pasos grandes, ese "redondeo" se nota mucho.

¿La solución? **Pasos más pequeños.** Si en vez de pasos de una décima usáramos pasos de una
**milésima** de segundo (haría falta una tabla con 500 filas, por eso no la hacemos a mano), a
los 0,5 segundos la pelota estaría a **0,7475 metros**: a solo 2,5 milímetros de la respuesta
exacta. **Cuanto más pequeño es el paso, más se parece el mundo de mentira al de verdad.**

Estas dos rarezas no son defectos de nuestra tabla: son **los dos problemas de verdad** con los
que lucha cualquier simulador. Y explican por qué los pasos son tan pequeñitos.
"""),

md(r"""### Por qué el paso tiene que ser pequeño (pero no demasiado)

Con lo que acabamos de ver, ya entiendes el dilema de cualquier simulador:

```
   PASO GRANDE                              PASO PEQUEÑO

   ✓ pocas cuentas: va rápido               ✗ muchas cuentas: va más lento
   ✗ poco exacto (como nuestra tabla)       ✓ muy exacto
   ✗ las cosas "atraviesan" el suelo        ✓ los choques se detectan a tiempo
     antes de que dé tiempo a verlas
   ✗ a veces el mundo "explota":            ✓ estable
     las piezas salen disparadas
```

Ese último punto es muy famoso: si el paso es demasiado grande, un pie que se ha hundido mucho
en el suelo recibe de golpe un empujón enorme para sacarlo, y sale **disparado**. Seguro que
has visto en algún videojuego un objeto que, por un fallo, de repente sale volando por los
aires sin motivo. Muchas veces es justo esto.

Los simuladores de robots buscan un paso **lo bastante pequeño para ser exactos y estables, y
lo bastante grande para ir rápido**. Por eso nuestro humanoide usa 3 milésimas: es un buen
compromiso.
"""),

md(r"""## 6 · Qué ocurre en un solo pasito (la versión completa)

Ahora que conoces la cadena de oro y los choques, este resumen se entiende del todo:

```
   UN PASO DE SIMULACIÓN (lo que pasa en un saltito):

   1. Mira todas las fuerzas que actúan sobre el robot AHORA mismo:
        - la gravedad, tirando hacia abajo
        - lo que retuercen los motores en cada articulación
        - los choques (el pie contra el suelo)
        - el rozamiento
   2. Con esas fuerzas y la masa de cada pieza, calcula cuánto
      cambia la velocidad de cada pieza            (fuerza → velocidad)
   3. Con las velocidades nuevas, calcula cuánto se mueve y gira
      cada pieza en ese instante minúsculo          (velocidad → posición)
   4. Comprueba los choques: ¿algo se ha metido dentro de otra cosa?
   5. Guarda el nuevo estado (la nueva "foto")
   6. Vuelta a empezar con el siguiente pasito
```

Es la tabla de la pelota, pero con 13 piezas a la vez, unidas por articulaciones, y 333 veces
por cada segundo simulado. El ordenador hace las mismas sumas que tú, solo que muchísimas y muy
deprisa.

Fíjate en lo bonito que es: el simulador no necesita saber "cómo andar". Solo sabe de física.
Le dices cuánto retuerce cada motor, y él te contesta, pasito a pasito, cómo queda el robot. Si
los motores empujan bien, el robot andará; si empujan al azar, se caerá (como en el GIF del
NB00). **La inteligencia no está en el simulador; está en quién decide cuánto empuja cada
motor.** Y eso, ¿quién es? La mente, la política. Justo la pieza del próximo notebook.
"""),

md(r"""## 7 · El bucle, ahora con el simulador dentro

En el NB00 hablamos del **bucle**: percibir → decidir → actuar → recompensa. Ahora ya
entiendes dónde encaja el simulador en ese bucle. Es quien recibe la acción (cuánto empuja
cada motor) y devuelve el nuevo estado del robot:

```
        la mente decide                el simulador da pasitos
        cuánto empuja      ─────────►  de física con esos empujes
        cada motor                             │
             ▲                                 ▼
             │                        el robot queda en una
             │                        postura nueva (nuevo estado)
             │                                 │
             └───────── la mente lee ──────────┘
                        ese nuevo estado
                        y vuelve a decidir
```

Fíjate en que arriba pone "pasitos", en plural. Hay un detalle que se suele pasar por alto.
"""),

md(r"""### Dos ritmos distintos: el de la física y el de la mente

La física necesita pasos **muy** pequeños para ser exacta (3 milésimas). Pero la mente **no
necesita decidir tan a menudo**: tú tampoco cambias de idea 333 veces por segundo. Así que se
hace una cosa muy práctica: **la mente decide, y luego el simulador da varios pasitos seguidos
manteniendo esa misma orden**.

En nuestro humanoide, la mente decide una vez y el simulador da **5 pasitos** con esa orden
antes de volver a preguntar:

```
   tiempo ──────────────────────────────────────────────────────────►

   física:   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·     (cada · = 3 milésimas)
   mente:    ▲              ▲              ▲                 (cada ▲ = una decisión)
             └── 5 pasitos ─┘└── 5 pasitos ─┘

   5 × 3 milésimas = 15 milésimas entre decisión y decisión
   →  unas 67 decisiones por segundo
```

Por eso en el NB00 decíamos que el robot decide "unas 67 veces por segundo": son las 333 fotos
de la física agrupadas de 5 en 5.

¿Te parecen muchas 67 decisiones por segundo? Tu cuerpo también es rapidísimo: los reflejos
que te mantienen de pie reaccionan a un tropiezo en unas pocas **centésimas** de segundo, sin
que te dé tiempo ni a pensarlo. Y ya viste en el NB00
que el robot al azar se cae en **un tercio de segundo**: si decidiera solo una vez por segundo,
estaría en el suelo antes de su segunda decisión.

En resumen: el simulador es la mitad de abajo del bucle ("la física decide qué pasa"); la mente
es la mitad de arriba ("yo decido qué hacer"). En este curso, casi todo tu trabajo será
construir y entrenar **la mente**; el simulador ya nos lo dan hecho.
"""),

md(r"""## 8 · Por qué un simulador es tan valioso

Ya vimos en el NB00 que caerse sale gratis. Pero hay más ventajas, y merece la pena tenerlas
todas juntas, porque explican por qué **toda** la robótica moderna se apoya en simuladores:

- **Caerse no cuesta nada.** Ni piezas rotas, ni dinero, ni peligro. El robot puede fallar
  millones de veces.
- **Va mucho más rápido que el tiempo real.** El ordenador puede dar los pasitos más deprisa
  que la vida real, y simular **muchos robots a la vez**, cada uno practicando por su cuenta.
  Con una buena tarjeta gráfica se llegan a simular **miles** de robots en paralelo.
- **Se puede repetir exactamente.** Puedes rebobinar y repetir el mismo intento clavado, para
  entender qué pasó. En la realidad, cada intento es distinto.
- **Lo ves todo.** En el simulador conoces *con exactitud* la postura, la velocidad y la
  posición de cada pieza. En un robot real solo sabes lo que sus sensores te dicen, y con
  errores (el "ruido" del NB01).
- **Puedes cambiar las reglas.** ¿Y si hubiera menos gravedad? ¿Y si el suelo resbalara más?
  En el simulador cambias un número y pruebas. En la realidad, no puedes cambiar la gravedad.

Por todo esto, la receta general de la robótica con aprendizaje es: **entrena en el simulador
(barato, rápido, seguro) y solo al final da el salto al robot real.**
"""),

md(r"""## 9 · El simulador que usaremos: MuJoCo

Existen varios simuladores buenos. Nosotros usaremos uno que se llama **MuJoCo** (se pronuncia
más o menos "mu-yó-co"), que es el **estándar en la investigación de robots**: lo usan
universidades y empresas de todo el mundo. Su nombre viene del inglés *Multi-Joint dynamics
with Contact*, que significa algo así como "el movimiento de cosas con muchas articulaciones y
con choques". O sea: justo lo que es un robot que anda. Es **gratuito** y lo mantiene hoy
Google DeepMind.

No necesitas recordar nada técnico de él; solo que es la herramienta concreta con la que
trabajaremos más adelante. Lo importante es que MuJoCo hace justo lo que hemos descrito:

- **Lee el "plano de montaje"** del robot (el fichero del NB01 que describe piezas,
  articulaciones, motores y sensores).
- Le pone **física**: gravedad, masa e inercia, suelo, choques, rozamiento.
- Avanza el mundo **a pasitos** (la cadena de oro + los choques), y en cada uno te dice cómo
  queda el robot.

Cuando llegue el momento de tocar código (dentro de varios notebooks), MuJoCo será una de las
primeras herramientas que aprendamos a manejar. Por ahora, quédate con la imagen: **MuJoCo es
el mundo de mentira donde nuestros robots vivirán y practicarán.**
"""),

md(r"""## 10 · Lo que sale mal: el mundo de mentira NO es el mundo real

Y aquí está la trampa más importante de todo este notebook, la que da sentido a la última
pieza del mapa (el salto al mundo real). Escúchala bien:

> Un simulador es una **imitación** de la realidad, no la realidad. Por muy bueno que sea,
> **siempre miente un poco**.

Ya lo has visto con tus propios ojos en la tabla de la pelota: con pasos grandes, el mundo de
mentira se equivocaba en 25 centímetros. Con pasos pequeños el error se hace minúsculo... pero
ese es solo **uno** de los errores posibles, y el más fácil de arreglar.

Piensa en un mapa de una ciudad: es utilísimo, pero no es la ciudad. Le faltan detalles, hay
cosas que simplifica, y si te fías del mapa al 100% acabarás dándote contra una obra que no
estaba dibujada. Con los simuladores pasa igual.

¿En qué "miente" un simulador respecto al robot real?

- Los **motores reales** tienen pequeños retardos, se calientan, no empujan exactamente lo
  que se les pide.
- Las **piezas reales** no pesan exactamente lo que dice el plano (un cable por aquí, un
  tornillo por allá).
- El **suelo real** tiene polvo, baches, zonas más resbaladizas; el simulado es más perfecto.
- Los **sensores reales** traen errores y ruido; en el simulador la información es perfecta.
- Mil detalles diminutos del mundo real que ningún simulador reproduce del todo.

A esa diferencia entre el mundo de mentira y el mundo real se le llama la **brecha de
realidad** (en inglés, *reality gap*). Es la razón por la que una mente entrenada solo en
simulación, al meterla en un robot de metal, a veces **falla**: el robot real no se comporta
igual que el simulado.
"""),

md(r"""### Una idea genial para saltar la brecha: entrenar en muchos mundos distintos

¿Cómo se lucha contra la brecha de realidad? Lo veremos a fondo al final del curso, pero hay
una idea tan bonita y tan sencilla que merece la pena conocerla ya.

Piensa en un futbolista que **solo** ha entrenado en un campo perfecto, con césped impecable y
sin viento. El día que juega en un campo embarrado y con vendaval, lo pasa fatal. En cambio, uno
que ha entrenado en **campos de todo tipo** —embarrados, secos, con viento, con lluvia— se adapta
a cualquiera, porque **ningún campo le pilla por sorpresa**.

Con los robots se hace lo mismo. En vez de entrenar en **un** mundo de mentira, se entrena en
**miles de mundos ligeramente distintos**: en uno el suelo resbala un poco más, en otro las
piernas pesan un poco más, en otro los motores son un poco más débiles, en otro los sensores
tiemblan más... Como en el simulador cambiar esas cosas es **cambiar un número**, es fácil.

```
   mundo 1: suelo normal, motores normales
   mundo 2: suelo resbaladizo, piernas algo más pesadas
   mundo 3: motores un 10% más débiles, sensores con más ruido
   mundo 4: suelo pegajoso, torso más ligero
   ...      (miles de variaciones)
                       │
                       ▼
   la mente aprende a andar en TODOS ellos a la vez
                       │
                       ▼
   el mundo real es, para ella, "un mundo más del montón"
```

A esta técnica se le llama **aleatorizar el mundo** (en inglés, *domain randomization*). La
mente que aprende así no se fía de ningún detalle concreto, y por eso aguanta mejor las
sorpresas del mundo real. Es uno de los grandes trucos que permiten que hoy los robots
entrenados en simulación anden en la realidad.

No es un problema para asustarse ahora; es un problema para **tenerlo presente**. El simulador
es nuestro mejor amigo para aprender, pero nunca hay que olvidar que es una imitación.
"""),

md(r"""## 11 · Resumen de la lección

1. Un **simulador** es un mundo de mentira que imita la física; el nuestro se llama **MuJoCo**.
2. La física que imita se resume en la **cadena de oro**: las **fuerzas** cambian la
   **velocidad**, y la velocidad cambia la **posición**. Las cosas son perezosas (**inercia**):
   siguen haciendo lo que hacían hasta que una fuerza las cambia.
3. El simulador avanza el tiempo a **pasitos** minúsculos (3 milésimas en nuestro humanoide),
   aplicando la cadena de oro y comprobando los **choques** en cada uno. Lo hiciste a mano con
   la pelota.
4. Pasos pequeños = más exactitud y estabilidad, pero más cálculo. La mente decide más despacio
   que la física: en nuestro humanoide, cada 5 pasitos (unas **67 veces por segundo**).
5. El simulador siempre miente un poco (**brecha de realidad**); un gran remedio es entrenar en
   miles de mundos ligeramente distintos (**aleatorizar el mundo**).

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Simulador** | Programa que imita la física del mundo real (un "mundo de mentira"). |
| **Fuerza** | Un empujón o un tirón que cambia cómo se mueve algo. |
| **Velocidad** | Lo deprisa que va algo y hacia dónde (en metros por segundo). |
| **Aceleración** | El cambio de la velocidad (acelerar, frenar o desviarse). |
| **Masa** | Cuánta "cosa" tiene un objeto; cuánto cuesta cambiar su movimiento. |
| **Inercia** | La tendencia de las cosas a seguir haciendo lo que hacían. |
| **Gravedad** | La fuerza que tira de todo hacia el suelo. |
| **Colisión / choque** | Dos sólidos que se encuentran y no se atraviesan. |
| **Rozamiento / fricción** | La resistencia a resbalar entre dos superficies. |
| **Estado** | La "foto" completa del mundo en un instante: posiciones y velocidades. |
| **Paso de simulación** | Cada saltito de tiempo con el que avanza el simulador. |
| **MuJoCo** | El simulador de robots que usaremos. |
| **Brecha de realidad** | La diferencia entre el mundo simulado y el real. |
| **Aleatorizar el mundo** | Entrenar en muchos mundos ligeramente distintos para aguantar la realidad. |
"""),

md(r"""## 12 · Preguntas de comprensión

Responde con tus palabras antes de abrir cada solución.

**P1.** ¿Qué es un simulador y para qué nos sirve principalmente en este curso?

**P2.** Explica con tus palabras qué es la **inercia**, con un ejemplo de tu vida diaria. ¿Por
qué le importa a un robot que se está cayendo?

**P3.** Explica con tus palabras qué es el **rozamiento** y por qué le importa a un robot que
anda.

**P4.** ¿Qué significa que el simulador avanza "a saltitos"? Usa la analogía del cuaderno de
dibujos o el cine.

**P5.** Continúa la tabla de la pelota **como si no hubiera suelo**: calcula la velocidad y la
altura en el paso 7 (tiempo 0,7 s).

**P6.** En la tabla de la pelota, ¿qué dos "rarezas" aparecían y qué hace un simulador para
resolver cada una?

**P7.** Si el robot decide cada 5 pasitos y cada pasito dura 3 milésimas de segundo, ¿cuántas
milésimas pasan entre una decisión y la siguiente? Y si un día hiciéramos que decidiera cada 10
pasitos, ¿decidiría más o menos veces por segundo?

**P8.** Da **tres** ventajas de entrenar en un simulador en vez de en un robot real.

**P9.** ¿Qué es la "brecha de realidad" (*reality gap*) y por qué existe?

**P10.** Explica con la analogía del futbolista qué es **aleatorizar el mundo** y por qué ayuda
a saltar la brecha de realidad.
"""),

md(r"""<details>
<summary>▶ Solución P1</summary>

Un simulador es un programa que **imita la física del mundo real dentro del ordenador** (un
"mundo de mentira" con gravedad, suelo, choques y rozamiento). Nos sirve, sobre todo, para que
el robot pueda **practicar y caerse un millón de veces sin que pase nada**: sin romper piezas,
sin gasto y sin peligro.
</details>

<details>
<summary>▶ Solución P2</summary>

La inercia es la **tendencia de las cosas a seguir haciendo lo que hacían**: si están quietas,
a seguir quietas; si se mueven, a seguir moviéndose igual, hasta que una fuerza las cambia.
Ejemplo: en un autobús que frena de golpe te vas hacia delante, porque tu cuerpo quiere seguir
a la velocidad que llevaba. Al robot le importa porque, si empieza a caerse, **la caída tiende
a continuar** aunque los motores ya estén corrigiendo, y cuanto más pesado es el torso, más
cuesta pararla. Por eso hay que corregir **pronto**, antes de que la caída coja velocidad.
</details>

<details>
<summary>▶ Solución P3</summary>

El rozamiento es la **resistencia que aparece cuando dos superficies rozan** e intentan
deslizarse una sobre otra. Le importa al robot porque es lo que hace que su **pie agarre el
suelo** y no resbale: gracias al rozamiento puede empujar contra el suelo para avanzar. Sin
rozamiento (como sobre hielo) el pie patinaría y no podría andar.
</details>

<details>
<summary>▶ Solución P4</summary>

Significa que el mundo simulado no avanza de forma continua, sino en **pasos minúsculos**, uno
tras otro. Es como un cuaderno de dibujos o el cine: muchas **fotos fijas** casi iguales que,
al pasar rápido una tras otra, forman el movimiento. Cada foto es el **estado** del robot en ese
instante, y cada salto de una a la siguiente es un "paso de simulación".
</details>

<details>
<summary>▶ Solución P5</summary>

Se aplica la misma receta a partir del paso 6 (velocidad 6, altura −0,10):

- Velocidad: 6 + 1 = **7 m/s**.
- Cuánto baja: 7 × 0,1 = 0,70 m.
- Altura: −0,10 − 0,70 = **−0,80 m**.

Es decir, sin suelo la pelota seguiría cayendo, cada vez más deprisa, 80 cm por debajo del
nivel del suelo. Justo por eso el simulador **tiene que** comprobar los choques en cada paso.
</details>

<details>
<summary>▶ Solución P6</summary>

**Rareza 1:** la pelota atravesaba el suelo (altura −0,10). El simulador lo resuelve
**comprobando choques en cada paso**: si algo se mete dentro de otra cosa, lo saca y aplica la
fuerza del choque. **Rareza 2:** los números no eran exactos (0,50 m en vez de 0,75 m a los 0,5
s), por usar pasos demasiado grandes. El simulador lo resuelve usando **pasos muy pequeños**
(milésimas de segundo), que hacen el error minúsculo.
</details>

<details>
<summary>▶ Solución P7</summary>

5 × 3 = **15 milésimas** entre una decisión y la siguiente (unas 67 decisiones por segundo). Si
decidiera cada 10 pasitos, pasarían 10 × 3 = 30 milésimas entre decisiones, así que decidiría
**menos** veces por segundo (unas 33, la mitad). Tendría menos ocasiones de corregir, lo cual
para un bípedo inestable puede ser un problema.
</details>

<details>
<summary>▶ Solución P8</summary>

Cualesquiera tres de estas: (1) **caerse sale gratis** (sin roturas, sin gasto, sin peligro);
(2) **va más rápido** que el tiempo real y permite entrenar **muchos robots a la vez**; (3) se
puede **repetir exactamente** el mismo intento; (4) **lo ves todo** con exactitud (postura,
velocidad, posición de cada pieza); (5) puedes **cambiar las reglas** (gravedad, rozamiento)
con solo cambiar un número.
</details>

<details>
<summary>▶ Solución P9</summary>

Es la **diferencia entre el mundo simulado y el mundo real**. Existe porque el simulador es
una **imitación** de la realidad, no la realidad: los motores reales tienen retardos y se
calientan, las piezas no pesan exactamente lo que dice el plano, el suelo real tiene
imperfecciones, los sensores reales traen errores... mil detalles que el simulador no reproduce
exactamente. Por eso una mente entrenada solo en simulación puede fallar al pasarla a un robot
de verdad.
</details>

<details>
<summary>▶ Solución P10</summary>

Un futbolista que solo entrena en un campo perfecto se ve perdido en uno embarrado; uno que
entrena en campos de todo tipo se adapta a cualquiera. **Aleatorizar el mundo** es lo mismo:
entrenar al robot en **miles de mundos de mentira ligeramente distintos** (suelo más o menos
resbaladizo, piezas más o menos pesadas, motores más o menos fuertes, sensores con más o menos
ruido). Así la mente no se fía de ningún detalle concreto, y el mundo real le parece "uno más
del montón", en vez de una sorpresa.
</details>
"""),

md(r"""## 13 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Ya tienes dos piezas del mapa bien entendidas, el **cuerpo** (NB01) y el **mundo** donde vive
(este NB02), y has visto el **bucle** que las une. En el **NB03** entramos en la pieza que de
verdad decide: **la mente, la política**. Veremos con calma qué es exactamente eso de "percibir"
(la observación) y "actuar" (la acción), y cómo una simple caja que convierte lo uno en lo otro
puede acabar sabiendo andar. Seguiremos sin código.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB02_el_mundo_de_mentira.ipynb")
    build(out, cells, title="NB02 · El mundo de mentira: qué es un simulador")
