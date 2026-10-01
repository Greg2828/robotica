"""Construye NB13 · El producto escalar: la operación de las neuronas (Parte 2 · Lección 2).

El patrón "multiplica por parejas y suma" (política del palo, recompensa del
humanoide, nota media). Definición y función; media ponderada → "pesos";
la política del palo como producto escalar; significado geométrico (misma
dirección +, perpendicular 0, opuesta −); vector unitario (normalizar);
proyección: cuánto de una flecha va en una dirección; el premio por avanzar
del humanoide = velocidad · (1,0,0); acercarse a la meta; v·v = longitud² =
esfuerzo; la neurona artificial (pesos · entradas + sesgo, y umbral =
perceptrón); el termostato es una neurona; detector de caídas que anticipa.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB13 · El producto escalar: la operación de las neuronas

**Parte 2 · Matemáticas y herramientas para robots — Lección 2**

> En el **NB12** aprendiste a pensar en **flechas** (vectores): sumarlas, estirarlas, restarlas y medirlas, en 2,
> en 3 o en 45 dimensiones. Hoy aprenderás la operación con flechas más importante de toda la inteligencia
> artificial.

Se llama **producto escalar**, y es tan sencilla que ya la has hecho varias veces **sin saber que tenía nombre**.
Al terminar esta lección entenderás tres cosas que parecen muy distintas y son la misma:

- Cómo calcula tu profesor la **nota media** cuando el examen cuenta más que los trabajos.
- Cómo decidía la **política del palo de escoba** del NB11.
- Qué hace, por dentro, una **neurona artificial**, la pieza básica de las redes neuronales que moverán al humanoide.

Primero la idea, luego el código. Como siempre.
"""),

md(r"""## 1 · Un patrón que ya has visto tres veces

Mira estas tres cuentas, que salieron en lecciones distintas:

```
   La política del palo de escoba (NB11):
       empuje = −30 × inclinación  +  (−8) × velocidad

   La recompensa del humanoide (NB04):
       recompensa = 5 × (¿de pie? 1 o 0)  +  1,25 × velocidad  +  (−0,1) × esfuerzo

   La nota final de una asignatura (en muchos colegios):
       nota = 0,6 × examen  +  0,4 × trabajos
```

¿Ves lo que tienen en común? En las tres hay **dos listas de números**:

- Una lista de **datos** (inclinación y velocidad; de pie, velocidad y esfuerzo; examen y trabajos).
- Una lista de **pesos** que dicen **cuánto importa** cada dato (−30 y −8; 5, 1,25 y −0,1; 0,6 y 0,4).

Y la cuenta siempre es la misma: **multiplica cada dato por su peso, y suma todo**. Eso, exactamente eso, es el
**producto escalar**.
"""),

md(r"""## 2 · La definición

El **producto escalar** de dos flechas del mismo tamaño se calcula así: **multiplica las componentes por parejas
(la primera con la primera, la segunda con la segunda...) y suma todos los resultados**. Se escribe con un puntito
entre las dos flechas: **a · b**.

```
   a = (2, 3)
   b = (4, 1)

   a · b  =  2 × 4  +  3 × 1  =  8 + 3  =  11
             ─────     ─────
           primeras   segundas
```

Fíjate en algo importante: el resultado **no es una flecha**, es **un solo número** (un **escalar**, NB12: por eso
se llama producto *escalar*). Dos flechas entran, un número sale.

En Python, con lo que ya sabes (las listas en paralelo del NB09 y un acumulador del NB07):
"""),

code(r"""def producto_escalar(a, b):
    total = 0
    for i in range(len(a)):
        total = total + a[i] * b[i]
    return total

print(producto_escalar([2, 3], [4, 1]))"""),

md(r"""**11**, como a mano. Y funciona con flechas de cualquier tamaño, igual que las funciones del NB12. Con tres
componentes:
"""),

code(r"""print(producto_escalar([1, 2, 3], [4, 5, 6]))"""),

md(r"""**32**: 1 × 4 + 2 × 5 + 3 × 6 = 4 + 10 + 18 = 32.
"""),

md(r"""## 3 · Primer significado: una suma con pesos

La nota de la asignatura es el ejemplo más fácil de entender. Si el examen cuenta un 60 % y los trabajos un 40 %, y has
sacado un 7 en el examen y un 9 en los trabajos:
"""),

code(r"""pesos = [0.6, 0.4]       # cuánto importa cada cosa
notas = [7, 9]           # examen, trabajos

print("Nota final:", round(producto_escalar(pesos, notas), 2))"""),

md(r"""**7,8**. No es la media normal (que sería 8), porque el examen, donde has sacado menos, **pesa más**.

A esto se le llama una **media ponderada** ("ponderar" significa "dar a cada cosa su peso"). Y aquí aparece una palabra
que vas a oír **miles** de veces en este curso: **pesos**. En una media ponderada, los pesos dicen **cuánto influye**
cada dato en el resultado:

- Un peso **grande** → ese dato influye mucho.
- Un peso **pequeño** (cerca de 0) → ese dato apenas importa.
- Un peso **negativo** → ese dato **resta**: cuanto más grande es, más baja el resultado (como el esfuerzo en la
  recompensa del humanoide, que tiene peso −0,1).

¿Recuerdas que en el NB03 dijimos que a las "ruedecillas" de la máquina de convertir se les llama **parámetros** o
**pesos**? Ahora sabes por qué: son, literalmente, los **pesos de productos escalares**.
"""),

md(r"""## 4 · La política del palo de escoba era un producto escalar

Volvamos al proyecto del NB11. La política ganadora era:

```
   empuje = −30 × inclinación − 8 × velocidad
```

que es lo mismo que **−30 × inclinación + (−8) × velocidad**: un producto escalar entre los **pesos** (−30, −8) y la
**observación** (inclinación, velocidad). Comprobémoslo con una observación concreta: el palo inclinado 2 grados y
cayendo hacia ese lado a 5 grados por segundo:
"""),

code(r"""pesos_politica = [-30, -8]
observacion = [2.0, 5.0]       # inclinación, velocidad de giro

print("Empuje (producto escalar):", producto_escalar(pesos_politica, observacion))
print("Empuje (fórmula del NB11): ", -30 * 2.0 - 8 * 5.0)"""),

md(r"""Lo mismo: **−100** (que luego el motor limitaría a −40, NB11). La política era un producto escalar, y sus dos
"ruedecillas" eran los dos **pesos**. Cuando la búsqueda aleatoria del NB11 probaba ruedecillas, estaba probando
**listas de pesos**.

Esto nos da una forma muy elegante de escribir **cualquier** política de este tipo:

```
   acción = pesos · observación
```

A una política así se le llama **política lineal**. Es la política más sencilla que existe... y, como verás, es el
ladrillo con el que se construyen las demás.
"""),

md(r"""## 5 · Segundo significado: ¿apuntan hacia el mismo sitio?

El producto escalar tiene también un significado **geométrico**, con flechas dibujadas, que es igual de importante.
Mira qué pasa con estas parejas de flechas:
"""),

code(r"""delante = [1, 0]

print("delante · delante        =", producto_escalar(delante, [1, 0]))
print("delante · diagonal       =", producto_escalar(delante, [1, 1]))
print("delante · izquierda      =", producto_escalar(delante, [0, 1]))
print("delante · atrás          =", producto_escalar(delante, [-1, 0]))"""),

md(r"""Fíjate en el **signo** del resultado:

```
   misma dirección       →   POSITIVO                   ──►  ──►
   en diagonal           →   positivo                   ──►  ↗
   formando una esquina  →   CERO                       ──►  ▲
   en sentidos opuestos  →   NEGATIVO                   ──►  ◄──
```

Esta es la regla de oro del significado geométrico:

(Ojo: "delante · diagonal" ha dado 1, lo mismo que "delante · delante", porque la flecha diagonal (1, 1) es más
**larga** —mide 1,41—. El producto escalar depende de las dos cosas: de cuánto se parecen las direcciones **y** de lo
largas que son las flechas. Si las dos midieran 1, la diagonal daría menos, como verás en el apartado 6.)

> **El producto escalar mide cuánto "van en la misma dirección" dos flechas.** Positivo si apuntan hacia el mismo
> lado, cero si forman una esquina (se dice que son **perpendiculares**), negativo si apuntan hacia lados opuestos.

Es como dos personas empujando un coche averiado: si empujan en la misma dirección, sus esfuerzos se ayudan; si una
empuja de lado, no ayuda nada a la otra; si empujan en sentidos opuestos, se estorban.
"""),

md(r"""## 6 · ¿Cuánto de una flecha va en una dirección?

El producto escalar responde a una pregunta muy práctica: **¿qué parte de una flecha va en una dirección concreta?**
Por ejemplo, sopla un viento (3, 4): ¿cuánto de ese viento empuja **hacia delante**?

Para preguntar por una **dirección** (sin importar cuánto mide), se usa una flecha de **longitud 1** que apunte hacia
allí. Se llama **vector unitario** ("de una unidad"). Hacia delante, es (1, 0). Y la respuesta es el producto escalar:
"""),

code(r"""viento = [3, 4]
hacia_delante = [1, 0]
print("Parte del viento que empuja hacia delante:", producto_escalar(viento, hacia_delante))"""),

md(r"""**3**: el viento (3, 4) empuja 3 hacia delante (y 4 hacia la izquierda). A esto se le llama **proyectar** la flecha
sobre una dirección, como la **sombra** que deja la flecha sobre el suelo cuando el sol está justo encima.

¿Y para una dirección que no es tan sencilla, como "hacia la meta"? Hay que **fabricar** su vector unitario: coger la
flecha hacia la meta y encogerla hasta que mida 1, dividiéndola entre su longitud (es lo que hicimos en el
mini-proyecto del NB12 para dar pasos de 0,5). A esto se le llama **normalizar**. Traemos las funciones `escalar` y
`longitud` del NB12:
"""),

code(r"""def escalar(numero, a):
    resultado = []
    for x in a:
        resultado.append(numero * x)
    return resultado

def longitud(a):
    return producto_escalar(a, a) ** 0.5

def normalizar(a):
    return escalar(1 / longitud(a), a)

print(normalizar([3, 4]))
print("Longitud tras normalizar:", longitud(normalizar([3, 4])))"""),

md(r"""(3, 4) normalizada es **(0,6; 0,8)** (con un pelín de ruido de decimales en el 0,6, nuestro viejo conocido
del NB06), que mide exactamente **1**: misma dirección, tamaño unidad.

¿Has visto un detalle en `longitud`? La hemos escrito como `producto_escalar(a, a) ** 0.5`. ¡Funciona porque **el
producto escalar de una flecha consigo misma es su longitud al cuadrado**! Mira: (3, 4) · (3, 4) = 9 + 16 = 25 = 5². Es
Pitágoras (NB12), disfrazado de producto escalar.

Y otra sorpresa: el **esfuerzo** de los motores del NB04 (cada acción al cuadrado, todo sumado) era **acción · acción**.
El producto escalar estaba escondido por todas partes.
"""),

md(r"""## 7 · El premio por avanzar del humanoide, por dentro

Con esto ya puedes entender un detalle de la recompensa del humanoide. En el NB04 dijimos que el premio era "1,25 ×
la velocidad **hacia delante** del centro de masas". Pero el centro de masas se mueve en **tres** dimensiones: puede ir
hacia delante, de lado, o arriba y abajo. ¿Cómo se queda solo con la parte "hacia delante"?

Con un **producto escalar** con la dirección "delante", (1, 0, 0): exactamente la proyección del apartado anterior.

```
   premio por avanzar = 1,25 × (velocidad del centro de masas · (1, 0, 0))
```

Veamos qué premio recibe el robot en tres situaciones:
"""),

code(r"""hacia_delante = [1, 0, 0]       # (delante, izquierda, arriba)

andando_recto = [1.0, 0.0, 0.0]
andando_en_diagonal = [0.8, 0.6, 0.0]
andando_de_lado = [0.0, 1.0, 0.0]
andando_hacia_atras = [-1.0, 0.0, 0.0]

print("Recto:       ", 1.25 * producto_escalar(andando_recto, hacia_delante))
print("En diagonal: ", 1.25 * producto_escalar(andando_en_diagonal, hacia_delante))
print("De lado:     ", 1.25 * producto_escalar(andando_de_lado, hacia_delante))
print("Hacia atrás: ", 1.25 * producto_escalar(andando_hacia_atras, hacia_delante))"""),

md(r"""Los cuatro robots van **igual de rápido** (las cuatro velocidades miden 1 m/s; compruébalo con Pitágoras), pero:

- **Recto**: 1,25 puntos, el premio completo.
- **En diagonal**: 1,0. Solo cuenta la parte que avanza.
- **De lado**: **0**. Por muy rápido que corra de lado, no gana ni un punto por avanzar.
- **Hacia atrás**: **−1,25**. ¡Le quita puntos!

Así, el producto escalar hace que la recompensa diga exactamente lo que queremos: "**avanza hacia delante**", no
"muévete mucho". (Imagina el robot tramposo del NB04 si el premio fuera la **rapidez** —la longitud de la velocidad—:
aprendería a correr en círculos a toda velocidad, como el barco que daba vueltas.)
"""),

md(r"""## 8 · La neurona artificial

Y llegamos a la gran revelación de la lección. Vamos a ver qué es una **neurona artificial**, la pieza con la que se
construyen las redes neuronales que, más adelante, controlarán al humanoide.

**Primero, la inspiración: las neuronas de tu cerebro.** Tu cerebro tiene unos 86.000 millones de neuronas. Cada una
recibe **señales** de muchas otras. Algunas conexiones son **fuertes** (esa señal influye mucho) y otras **débiles**;
algunas **animan** a la neurona a activarse y otras la **frenan**. La neurona, en el fondo, "suma" todo lo que le llega,
teniendo en cuenta cuánto pesa cada conexión, y si el total es suficientemente alto, **se activa** y manda su propia
señal a otras neuronas.

**La neurona artificial copia esa idea, muy simplificada:**

```
   entradas            pesos
   (x1, x2, x3)  ·  (w1, w2, w3)   +   sesgo    →   salida
   └───────────── producto escalar ───┘
```

1. Recibe una lista de **entradas** (por ejemplo, la observación de un robot).
2. Cada entrada tiene su **peso**: cuánto influye y si anima (positivo) o frena (negativo).
3. Calcula el **producto escalar** de pesos y entradas: la "suma con pesos".
4. Le suma un número fijo, el **sesgo** (en inglés, *bias*), que la hace más o menos "fácil de activar" (ahora vemos
   para qué sirve).

**Eso es todo.** Una neurona artificial es, en su corazón, **un producto escalar más un número**. (Le falta un último
ingrediente, que veremos cuando construyamos redes; pero lo esencial es esto.)
"""),

code(r"""def neurona(entradas, pesos, sesgo):
    return producto_escalar(entradas, pesos) + sesgo"""),

md(r"""Fíjate: la política del palo de escoba era una neurona con pesos (−30, −8) y sesgo 0. **La política del NB11 era una
neurona artificial.** Tu primer robot que aprendió, aprendió los pesos de **una** neurona.
"""),

md(r"""### El termostato también era una neurona

Las primeras neuronas artificiales, inventadas en los años 50 y llamadas **perceptrones**, añadían una decisión al
final: si el resultado es **mayor que 0**, la neurona "se activa" (sí); si no, no. Un producto escalar, un sesgo, y un
`if` (NB08).

Mira cómo el **termostato** (NB08, NB10) es un perceptrón. Una sola entrada (la temperatura), peso **−1** y sesgo
**20**: la salida es 20 − temperatura, que es **positiva** justo cuando la temperatura está **por debajo de 20**:
"""),

code(r"""def termostato_neurona(temperatura):
    salida = neurona([temperatura], [-1], 20)
    if salida > 0:
        return "encendida"
    else:
        return "apagada"

for t in [18, 19.5, 20, 21]:
    print(t, "grados ->", termostato_neurona(t))"""),

md(r"""Exactamente la política del termostato: enciende por debajo de 20 y apaga a partir de 20. Y aquí se ve **para qué sirve
el sesgo**: es el **umbral**, el punto en el que la neurona cambia de opinión. Con sesgo 19, tendríamos el termostato
ahorrador del NB10; con 21, el caluroso. **Cambiar el sesgo es girar otra ruedecilla.**
"""),

md(r"""## 9 · Mini-proyecto: una neurona que avisa antes de caer

Construyamos una neurona útil para un robot: un **detector de caídas**, que levante la alarma cuando el robot está a
punto de caerse... **antes** de que sea tarde.

La neurona recibe dos entradas: la **inclinación** del torso (en grados) y su **velocidad de giro** (grados por
segundo). Daremos la alarma si la "suma con pesos" supera un umbral.

Una primera versión, ingenua, solo mira la inclinación (peso 1 para la inclinación, 0 para la velocidad) y avisa a
partir de 10 grados (sesgo −10):
"""),

code(r"""def alarma(inclinacion, velocidad, pesos, sesgo):
    return neurona([inclinacion, velocidad], pesos, sesgo) > 0

casos = [
    [5, 0],      # algo inclinado, quieto
    [5, 30],     # algo inclinado, pero cayéndose deprisa
    [12, 0],     # bastante inclinado, quieto
    [12, -30],   # bastante inclinado, pero recuperándose deprisa
]

print("SOLO INCLINACIÓN (pesos [1, 0], sesgo -10):")
for caso in casos:
    print("  inclinación", caso[0], "| velocidad", caso[1], "-> ¿alarma?", alarma(caso[0], caso[1], [1, 0], -10))"""),

md(r"""(¿Has visto el `return ... > 0`? Como en el ejercicio E5 del NB10, una comparación ya es `True` o `False`, y se puede
devolver directamente.)

Funciona... a medias. Mira los casos 2 y 4:

- **5 grados cayéndose deprisa** → **no** avisa. ¡Pero se está cayendo a toda velocidad! Cuando llegue a 10 grados,
  quizá sea tarde.
- **12 grados recuperándose deprisa** → **sí** avisa. ¡Pero se está enderezando solo! Es una falsa alarma.

¿Te suena? **Es el problema de la foto** otra vez (NB03, NB11): mirar solo dónde está, sin mirar hacia dónde va. Démosle
peso a la velocidad: por ejemplo, 0,3. Así, cada grado por segundo de caída "cuenta" como 0,3 grados de inclinación
extra:
"""),

code(r"""print("INCLINACIÓN + VELOCIDAD (pesos [1, 0.3], sesgo -10):")
for caso in casos:
    print("  inclinación", caso[0], "| velocidad", caso[1], "-> ¿alarma?", alarma(caso[0], caso[1], [1, 0.3], -10))"""),

md(r"""Ahora la neurona **anticipa**:

| Caso | Solo inclinación | Inclinación + velocidad |
|---|---|---|
| 5°, quieto | no | no |
| 5°, cayéndose deprisa | **no** (¡tarde!) | **sí** (avisa a tiempo) |
| 12°, quieto | sí | sí |
| 12°, recuperándose | **sí** (falsa alarma) | **no** (bien visto) |

Con solo **cambiar un peso** (de 0 a 0,3), la neurona ha pasado de reaccionar tarde a **anticiparse**. Esos pesos los
hemos elegido nosotros pensando. En una red neuronal de verdad, los pesos **se aprenden** probando y guiándose por la
recompensa. Y en vez de una neurona con 2 pesos, hay **miles** de neuronas con **miles** de pesos.
"""),

md(r"""## 10 · Resumen de la lección

1. El **producto escalar** de dos flechas: multiplicar las componentes por parejas y sumar. Dos flechas entran, **un
   número** sale. Se escribe a · b.
2. Primer significado: una **suma con pesos** (media ponderada). Los **pesos** dicen cuánto influye cada dato; negativos,
   restan. La política del palo de escoba era **pesos · observación**: una **política lineal**.
3. Segundo significado: **cuánto apuntan en la misma dirección** (positivo, cero si son **perpendiculares**, negativo si
   son opuestas). Con un **vector unitario** (longitud 1, obtenido al **normalizar**), da **cuánto de una flecha va en esa
   dirección** (proyección).
4. El premio por avanzar del humanoide es velocidad · (1, 0, 0): solo cuenta avanzar hacia delante. Y a · a es la
   **longitud al cuadrado** (el esfuerzo era acción · acción).
5. Una **neurona artificial** = pesos · entradas + **sesgo**. Con un umbral (`> 0`) es un **perceptrón**: el termostato lo
   era. Un detector de caídas con peso en la velocidad **anticipa** en vez de reaccionar tarde.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Producto escalar (a · b)** | Multiplicar por parejas y sumar: dos flechas dan un número. |
| **Media ponderada** | Una media en la que cada dato cuenta según su peso. |
| **Pesos** | Los números que dicen cuánto influye cada dato; las "ruedecillas" de una neurona. |
| **Política lineal** | Una política que es un producto escalar: acción = pesos · observación. |
| **Perpendiculares** | Dos flechas que forman una esquina recta; su producto escalar es 0. |
| **Vector unitario** | Una flecha de longitud 1: solo indica una dirección. |
| **Normalizar** | Encoger o estirar una flecha hasta que mida 1. |
| **Proyección** | La parte de una flecha que va en una dirección dada (su "sombra"). |
| **Neurona artificial** | Pesos · entradas + sesgo. |
| **Sesgo (*bias*)** | El número que se suma en una neurona; hace de umbral. |
| **Perceptrón** | Una neurona con decisión: se activa si su resultado es mayor que 0. |
"""),

md(r"""## 11 · Ejercicios

**E1.** Calcula a mano: (1, 2) · (3, 4); (2, 0, −1) · (1, 5, 3); (5, 5) · (−1, 1).

**E2.** En tu colegio, el examen final cuenta un 50 %, los parciales un 30 % y los deberes un 20 %. Si sacas 6 en el final,
8 en los parciales y 10 en los deberes, ¿qué nota media ponderada tienes? Escríbelo como producto escalar.

**E3.** Sin calcular nada, di si el producto escalar será positivo, cero o negativo: (3, 0) · (0, 5); (2, 2) · (1, 3);
(1, −1) · (−2, 2).

**E4.** Normaliza la flecha (0, −5). ¿Qué vector unitario sale? ¿Hacia dónde apunta?

**E5.** Un robot camina con velocidad (0,6; 0,8; 0) (en m/s: delante, izquierda, arriba). ¿Cuánto premio por avanzar
recibe en un paso (1,25 × la parte hacia delante)? ¿Qué rapidez lleva?

**E6.** Escribe la recompensa del humanoide como un producto escalar entre pesos (5; 1,25; −0,1) y datos (de pie como 1 o 0,
velocidad, esfuerzo). Calcula la recompensa para (1; 2; 1). ¿Coincide con el 7,4 de siempre?

**E7.** Con el detector de caídas (pesos [1, 0.3], sesgo −10), ¿salta la alarma para una inclinación de 2 grados cayéndose a
40 grados por segundo? ¿Y para 0 grados a 20 grados por segundo? Calcula la salida de la neurona a mano.

**E8.** **Reto.** Escribe un termostato-neurona para una nevera: tiene que **encender el motor de frío** cuando la temperatura
está **por encima** de 5 grados. ¿Qué peso y qué sesgo necesitas?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

- (1, 2) · (3, 4) = 1 × 3 + 2 × 4 = 3 + 8 = **11**.
- (2, 0, −1) · (1, 5, 3) = 2 + 0 − 3 = **−1**.
- (5, 5) · (−1, 1) = −5 + 5 = **0** (son perpendiculares: una apunta en diagonal hacia arriba-derecha y la otra hacia
  arriba-izquierda).
</details>

<details>
<summary>▶ Solución E2</summary>

Pesos (0,5; 0,3; 0,2) y notas (6, 8, 10): 0,5 × 6 + 0,3 × 8 + 0,2 × 10 = 3 + 2,4 + 2 = **7,4**.

```python
print(round(producto_escalar([0.5, 0.3, 0.2], [6, 8, 10]), 2))
```

Los pesos suman 1 (el 100 %), como en toda media ponderada.
</details>

<details>
<summary>▶ Solución E3</summary>

- (3, 0) · (0, 5): una apunta hacia delante y otra hacia la izquierda, forman una esquina → **cero**.
- (2, 2) · (1, 3): las dos apuntan "hacia arriba a la derecha" → **positivo** (2 + 6 = 8).
- (1, −1) · (−2, 2): apuntan en sentidos **opuestos** (la segunda es la primera multiplicada por −2) → **negativo** (−2 − 2 = −4).
</details>

<details>
<summary>▶ Solución E4</summary>

La longitud de (0, −5) es 5. Dividiendo: (0/5, −5/5) = **(0, −1)**. Mide 1 y apunta **hacia la derecha del robot**
(y negativa = lo contrario de "hacia la izquierda").
</details>

<details>
<summary>▶ Solución E5</summary>

Parte hacia delante: (0,6; 0,8; 0) · (1, 0, 0) = 0,6. Premio: 1,25 × 0,6 = **0,75** puntos. Rapidez: √(0,36 + 0,64) = √1 = **1
m/s**. Va a buen ritmo, pero como va en diagonal (más hacia la izquierda que hacia delante), solo cobra el 60 % del premio.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
pesos_recompensa = [5, 1.25, -0.1]
datos = [1, 2, 1]        # de pie (sí = 1), velocidad 2, esfuerzo 1
print(producto_escalar(pesos_recompensa, datos))
```

5 × 1 + 1,25 × 2 + (−0,1) × 1 = 5 + 2,5 − 0,1 = **7,4**. ¡La de siempre! La recompensa del humanoide es una media
ponderada de sus ingredientes, y sus pesos son las decisiones del diseñador (NB04).
</details>

<details>
<summary>▶ Solución E7</summary>

- 2 grados a 40 °/s: 1 × 2 + 0,3 × 40 − 10 = 2 + 12 − 10 = **4** > 0 → **sí** salta. Casi derecho, pero cayéndose tan rápido
  que hay que avisar ya.
- 0 grados a 20 °/s: 0 + 6 − 10 = **−4** → **no** salta. Va algo deprisa, pero está derecho y aún hay margen.
</details>

<details>
<summary>▶ Solución E8</summary>

Queremos que la salida sea **positiva cuando la temperatura pasa de 5**. Con peso **+1** y sesgo **−5**: salida = temperatura
− 5, que es positiva justo por encima de 5 grados.

```python
def nevera(temperatura):
    if neurona([temperatura], [1], -5) > 0:
        return "frío encendido"
    else:
        return "frío apagado"

print(nevera(7), "|", nevera(3))
```

Fíjate: el termostato de la calefacción tenía peso **−1** (enciende cuando hace **poco** calor) y la nevera, peso **+1** (enciende
cuando hace **mucho**). El signo del peso decide si una entrada **anima** o **frena** a la neurona.
</details>
"""),

md(r"""## 12 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Has descubierto que una neurona es un producto escalar con un sesgo, y que tu política del palo de escoba era **una** neurona.
Pero el humanoide tiene **17 motores**: necesita **17 salidas** a la vez, una por motor. ¿Y eso? Pues **17 neuronas**, cada una
con sus 45 pesos. En el **NB14** veremos cómo se organizan todos esos pesos en una **tabla de números**, una **matriz**, y
contaremos cuántas ruedecillas tiene la política más sencilla posible del humanoide. Spoiler: muchas más de 2.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB13_producto_escalar.ipynb")
    build(out, cells, title="NB13 · El producto escalar: la operación de las neuronas")
