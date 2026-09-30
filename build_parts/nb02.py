"""Construye NB02 · El mundo de mentira: qué es un simulador (conceptual, 0 código).

Pieza (2) del mapa. Qué es un simulador, física desde cero (fuerza, gravedad,
choque, rozamiento), el tiempo a saltitos (paso de simulación), por qué es tan
útil, MuJoCo (solo el nombre) y el "reality gap". Analogías y diagramas ASCII.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, build

cells = [

md(r"""# NB02 · El mundo de mentira: qué es un simulador

**Parte 0 · El terreno — Lección 3**

> En el **NB00** viste el mapa entero. En el **NB01** desmontaste el **cuerpo** del robot:
> piezas rígidas, articulaciones, grados de libertad y motores, y viste que todo eso se
> guarda en un "plano de montaje". Hoy toca la pieza (2): **quién coge ese plano y le da
> vida** poniéndole gravedad, suelo y golpes. Eso es el **simulador**.

Como siempre en esta Parte 0, **cero código**. Solo entender. De paso vamos a explicar desde
cero un poco de **física** (qué es una fuerza, la gravedad, el rozamiento) y una idea muy
importante: que en el simulador **el tiempo avanza a saltitos**. Tranquilo, todo con
ejemplos de la vida diaria.
"""),

md(r"""## 1 · ¿Qué es un simulador?

Un **simulador** es un programa que **imita la física del mundo real dentro del ordenador**.
Es, literalmente, un **mundo de mentira**: hay gravedad, hay un suelo, las cosas chocan, se
caen, ruedan y rozan, igual que en la realidad... pero todo ocurre en números, dentro de la
máquina.

Seguro que ya conoces uno sin saberlo: **cualquier videojuego** donde una pelota rueda por
una cuesta, un coche derrapa o un personaje salta y cae. Detrás de eso hay un simulador
calculando cómo se mueven las cosas. Nosotros usaremos uno mucho más preciso, pensado para
robots, pero la idea es la misma: **un mundo falso que se comporta como el de verdad**.

¿Y para qué queremos un mundo falso? Recuerda el NB00: para que el robot pueda **practicar y
caerse un millón de veces sin que pase nada**. En el mundo real, cada caída rompe piezas
caras; en el mundo de mentira, caerse no cuesta absolutamente nada. Ese es el superpoder del
simulador, y por eso es una de las seis piezas del mapa.

De hecho, aquel robot que viste desplomarse en el GIF del NB00 **estaba dentro de un
simulador**. Lo que viste era, precisamente, un mundo de mentira en marcha.
"""),

md(r"""## 2 · Un poco de física, desde cero

Para entender qué "imita" el simulador, hace falta saber qué imita. Cuatro ideas de física,
explicadas como si nunca hubieras oído hablar de ellas (porque no hace falta).

**Fuerza = un empujón o un tirón.** Una fuerza es cualquier cosa que empuja o tira de un
objeto y cambia cómo se mueve. Cuando empujas una puerta, aplicas una fuerza. Cuando tiras de
una cuerda, también. Sin fuerzas, nada se movería ni se pararía.

**Gravedad = el tirón hacia el suelo.** La gravedad es una fuerza especial: **tira de todo
hacia abajo**, hacia el suelo, sin parar. Es la razón de que las cosas caigan cuando las
sueltas y de que tú no salgas flotando. Para un robot es su gran enemiga: la gravedad está
siempre intentando tumbarlo.

**Choque (colisión) = dos cosas sólidas no se atraviesan.** Cuando dos objetos duros se
encuentran, **chocan**: no pueden ocupar el mismo sitio, así que se frenan o rebotan. Esto es
importantísimo para un robot: su **pie choca con el suelo** y se apoya en él en vez de
atravesarlo. Sin choques, el robot se hundiría en el suelo como un fantasma.

**Rozamiento (fricción) = la resistencia al resbalar.** Cuando dos superficies se tocan y una
intenta deslizarse sobre la otra, aparece una resistencia que lo dificulta: el **rozamiento**.
Es lo que hace que tus zapatos **agarren** el suelo y no resbales al andar. Sobre hielo hay
poquísimo rozamiento, y por eso patinas. Para un robot, el rozamiento entre el pie y el suelo
es lo que le permite empujar para avanzar sin que el pie se le vaya.

Un simulador, en el fondo, no es más que un programa que **tiene en cuenta estas cuatro cosas
(y algunas más) para calcular qué le pasa al robot en cada momento**.
"""),

md(r"""## 3 · La idea clave: el tiempo avanza "a saltitos"

Aquí viene una idea nueva y muy importante, así que vamos despacio.

En el mundo real, el tiempo fluye de forma **continua**, sin cortes. Pero un ordenador no
puede calcular "todos los instantes", porque son infinitos. ¿Qué hace entonces? Un truco muy
inteligente: **avanza el mundo a saltitos pequeñísimos**.

La mejor analogía es un **cuaderno de dibujos animados** (un *flip-book*): esos cuadernos con
un dibujo en cada página, casi igual al anterior, que al pasar las páginas rápido **parecen
moverse**. Los dibujos animados y el cine funcionan igual: son muchas **fotos fijas**
seguidas que, al pasar deprisa, nuestro ojo ve como movimiento.

El simulador hace exactamente eso con el robot:

```
   El mundo NO avanza de golpe, sino en saltitos minúsculos:

   estado 0  --pasito-->  estado 1  --pasito-->  estado 2  --pasito-->  ...
    (foto)                 (foto)                  (foto)

   Como un cuaderno de dibujos: muchas fotos casi iguales que,
   una detrás de otra, forman el movimiento.
```

A cada uno de esos saltitos se le llama un **paso de simulación** (en inglés, *timestep*).
Cada paso suele representar una fracción minúscula de segundo (por ejemplo, la centésima parte
de un segundo). Guarda esta palabra, **paso**, porque va a aparecer constantemente: entrenar
será, literalmente, dar millones de estos pasitos.
"""),

md(r"""### Qué ocurre en un solo pasito

¿Y qué calcula el simulador en cada uno de esos saltitos? Esto:

```
   UN PASO DE SIMULACIÓN (lo que pasa en un saltito):

   1. Mira todas las fuerzas que actúan sobre el robot AHORA mismo:
        - la gravedad, tirando hacia abajo
        - lo que empujan los motores en cada articulación
        - los choques (el pie contra el suelo)
        - el rozamiento
   2. Con esas fuerzas, calcula cómo se mueve cada pieza durante
      ese instante minúsculo (cuánto gira cada articulación, etc.)
   3. Actualiza la postura del robot  ->  ese es el nuevo estado
   4. Vuelta a empezar con el siguiente pasito
```

Fíjate en lo bonito que es: el simulador no necesita saber "cómo andar". Solo sabe de física.
Le dices cuánto empuja cada motor, y él te contesta, pasito a pasito, cómo queda el robot. Si
los motores empujan bien, el robot andará; si empujan al azar, se caerá (como en el GIF del
NB00). **La inteligencia no está en el simulador; está en quién decide cuánto empuja cada
motor.** Y eso, ¿quién es? La mente, la política. Justo la pieza del próximo notebook.
"""),

md(r"""## 4 · El bucle, ahora con el simulador dentro

En el NB00 hablamos del **bucle**: percibir → decidir → actuar → recompensa. Ahora ya
entiendes dónde encaja el simulador en ese bucle. Es quien recibe la acción (cuánto empuja
cada motor) y devuelve el nuevo estado del robot:

```
        la mente decide                el simulador da un pasito
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

Este bucle se repite un paso tras otro, muchísimas veces por segundo. El simulador es la mitad
de abajo de ese bucle: la parte de "la física decide qué pasa". La mente es la mitad de
arriba: la parte de "yo decido qué hacer". En este curso, casi todo tu trabajo será construir
y entrenar **la mente**; el simulador ya nos lo dan hecho.
"""),

md(r"""## 5 · Por qué un simulador es tan valioso

Ya vimos en el NB00 que caerse sale gratis. Pero hay más ventajas, y merece la pena tenerlas
todas juntas, porque explican por qué **toda** la robótica moderna se apoya en simuladores:

- **Caerse no cuesta nada.** Ni piezas rotas, ni dinero, ni peligro. El robot puede fallar
  millones de veces.
- **Va mucho más rápido que el tiempo real.** El ordenador puede dar los pasitos más deprisa
  que la vida real, y simular **muchos robots a la vez**, cada uno practicando por su cuenta.
- **Se puede repetir exactamente.** Puedes rebobinar y repetir el mismo intento clavado, para
  entender qué pasó. En la realidad, cada intento es distinto.
- **Lo ves todo.** En el simulador conoces *con exactitud* la postura, la velocidad y la
  posición de cada pieza. En un robot real solo sabes lo que sus sensores te dicen, y con
  errores.
- **Puedes cambiar las reglas.** ¿Y si hubiera menos gravedad? ¿Y si el suelo resbalara más?
  En el simulador cambias un número y pruebas. En la realidad, no puedes cambiar la gravedad.

Por todo esto, la receta general de la robótica con aprendizaje es: **entrena en el simulador
(barato, rápido, seguro) y solo al final da el salto al robot real.**
"""),

md(r"""## 6 · El simulador que usaremos: MuJoCo

Existen varios simuladores buenos. Nosotros usaremos uno que se llama **MuJoCo**, que es el
**estándar en la investigación de robots**: lo usan universidades y empresas de todo el mundo.
No necesitas recordar el nombre ahora ni saber nada técnico de él; solo que es la herramienta
concreta con la que trabajaremos más adelante.

Lo importante conceptualmente es que MuJoCo hace justo lo que hemos descrito:

- **Lee el "plano de montaje"** del robot (el fichero del NB01 que describe piezas,
  articulaciones y motores).
- Le pone **física**: gravedad, suelo, choques, rozamiento.
- Avanza el mundo **a pasitos**, y en cada uno te dice cómo queda el robot.

Cuando llegue el momento de tocar código (dentro de varios notebooks), MuJoCo será una de las
primeras herramientas que aprendamos a manejar. Por ahora, quédate con la imagen: **MuJoCo es
el mundo de mentira donde nuestros robots vivirán y practicarán.**
"""),

md(r"""## 7 · Lo que sale mal: el mundo de mentira NO es el mundo real

Y aquí está la trampa más importante de todo este notebook, la que da sentido a la última
pieza del mapa (el salto al mundo real). Escúchala bien:

> Un simulador es una **imitación** de la realidad, no la realidad. Por muy bueno que sea,
> **siempre miente un poco**.

Piensa en un mapa de una ciudad: es utilísimo, pero no es la ciudad. Le faltan detalles, hay
cosas que simplifica, y si te fías del mapa al 100% acabarás dándote contra una obra que no
estaba dibujada. Con los simuladores pasa igual.

¿En qué "miente" un simulador respecto al robot real?

- Los **motores reales** tienen pequeños retardos, se calientan, no empujan exactamente lo
  que se les pide.
- El **suelo real** tiene polvo, baches, zonas más resbaladizas; el simulado es más perfecto.
- Los **sensores reales** (los "sentidos" del robot) traen errores y ruido; en el simulador
  la información es perfecta.
- Mil detalles diminutos del mundo real que ningún simulador reproduce del todo.

A esa diferencia entre el mundo de mentira y el mundo real se le llama la **brecha de
realidad** (en inglés, *reality gap*). Es la razón por la que una mente entrenada solo en
simulación, al meterla en un robot de metal, a veces **falla**: el robot real no se comporta
igual que el simulado. Cerrar esa brecha es, precisamente, el gran reto de la pieza (6) del
mapa, el **sim-to-real**, una de las cosas más valiosas que aprenderás.

No es un problema para asustarse ahora; es un problema para **tenerlo presente**. El simulador
es nuestro mejor amigo para aprender, pero nunca hay que olvidar que es una imitación.
"""),

md(r"""## 8 · Preguntas de comprensión

Responde con tus palabras antes de abrir cada solución.

**P1.** ¿Qué es un simulador y para qué nos sirve principalmente en este curso?

**P2.** Explica con tus palabras qué es el **rozamiento** y por qué le importa a un robot que
anda.

**P3.** ¿Qué significa que el simulador avanza "a saltitos"? Usa la analogía del cuaderno de
dibujos o el cine.

**P4.** En un solo **paso de simulación**, ¿qué cosas tiene en cuenta el simulador para
calcular cómo queda el robot?

**P5.** Da **tres** ventajas de entrenar en un simulador en vez de en un robot real.

**P6.** ¿Qué es la "brecha de realidad" (*reality gap*) y por qué existe?
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

El rozamiento es la **resistencia que aparece cuando dos superficies rozan** e intentan
deslizarse una sobre otra. Le importa al robot porque es lo que hace que su **pie agarre el
suelo** y no resbale: gracias al rozamiento puede empujar contra el suelo para avanzar. Sin
rozamiento (como sobre hielo) el pie patinaría y no podría andar.
</details>

<details>
<summary>▶ Solución P3</summary>

Significa que el mundo simulado no avanza de forma continua, sino en **pasos minúsculos**, uno
tras otro. Es como un cuaderno de dibujos o el cine: muchas **fotos fijas** casi iguales que,
al pasar rápido una tras otra, forman el movimiento. Cada foto es el estado del robot en ese
instante, y cada salto de una a la siguiente es un "paso de simulación".
</details>

<details>
<summary>▶ Solución P4</summary>

Tiene en cuenta todas las **fuerzas** que actúan en ese instante: la **gravedad** (tira hacia
abajo), lo que **empujan los motores** en cada articulación, los **choques** (por ejemplo, el
pie contra el suelo) y el **rozamiento**. Con todo eso calcula cómo se mueve cada pieza durante
ese instante minúsculo y actualiza la postura del robot.
</details>

<details>
<summary>▶ Solución P5</summary>

Cualesquiera tres de estas: (1) **caerse sale gratis** (sin roturas, sin gasto, sin peligro);
(2) **va más rápido** que el tiempo real y permite entrenar **muchos robots a la vez**; (3) se
puede **repetir exactamente** el mismo intento; (4) **lo ves todo** con exactitud (postura,
velocidad, posición de cada pieza); (5) puedes **cambiar las reglas** (gravedad, rozamiento)
con solo cambiar un número.
</details>

<details>
<summary>▶ Solución P6</summary>

Es la **diferencia entre el mundo simulado y el mundo real**. Existe porque el simulador es
una **imitación** de la realidad, no la realidad: los motores reales tienen retardos y se
calientan, el suelo real tiene imperfecciones, los sensores reales traen errores... mil
detalles que el simulador no reproduce exactamente. Por eso una mente entrenada solo en
simulación puede fallar al pasarla a un robot de verdad.
</details>
"""),

md(r"""## 9 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Ya tienes tres piezas del mapa: el **cuerpo** (NB01), el **mundo** donde vive (este NB02) y la
idea del **bucle**. En el **NB03** entramos en la pieza que de verdad decide: **la mente, la
política**. Veremos con calma qué es exactamente eso de "percibir" (la observación) y "actuar"
(la acción), y cómo una simple caja que convierte lo uno en lo otro puede acabar sabiendo
andar. Seguiremos sin código.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB02_el_mundo_de_mentira.ipynb")
    build(out, cells, title="NB02 · El mundo de mentira: qué es un simulador")
