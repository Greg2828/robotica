"""Construye NB03b · Números a fondo (Parte 0 · lección intermedia, conceptual, 0 código).

Añadida tras la auditoría de 2026-10-04: el curso usaba porcentajes, decimales
pequeños, potencias con exponente negativo, raíces y notación científica sin
haberlos enseñado. Valor posicional, mover la coma, multiplicar por decimales,
fracciones como divisiones, porcentajes (calcular, subir y bajar, encadenar,
qué % es), negativos y signos, potencias (de 10, exponente 0, negativos, reglas,
crecimiento exponencial), raíces (y exponente ½), notación científica y la "e"
del ordenador, prefijos (kilo...nano), orden de magnitud, redondeo y error
absoluto/relativo, proporcionalidad y regla de tres.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, build

cells = [

md(r"""# NB03b · Números a fondo

**Parte 0 · El terreno — Lección intermedia (entre el NB03 y el NB04)**

> Un robot vive entre números raros: pasos de tiempo de **0,002** segundos, motores un **10 %** más débiles, errores de **0,00001**, robots que pesan **40** kilos y redes con **159.505** números dentro. Si esos números te dan un poco de miedo, es normal: casi nadie te ha explicado con calma cómo funcionan. Hoy lo hacemos.

En esta lección **no hay código** ni robots nuevos: solo **números**, contados despacio. Es la caja de herramientas que vas a usar en todo el curso:

- Los **decimales**: qué significa cada cifra después de la coma, y cómo multiplicar y dividir con ellos.
- Los **porcentajes**: el "10 %" de todas partes, y sus trampas.
- Las **potencias** (multiplicar un número por sí mismo muchas veces) y las **raíces** (deshacerlo).
- La **notación científica**: cómo escribir números enormes o diminutos sin volverte loco, y cómo los escribe el ordenador.
- Los **prefijos** (kilo, mili, micro...), el **redondeo** y la **proporcionalidad**.

Si alguna parte ya la sabes del colegio, léela igualmente por encima: aparecen trucos y trampas que usaremos más adelante. Y si alguna te cuesta, no pasa nada: vuelve a ella cuando la necesites. Al final hay preguntas con su solución.
"""),

md(r"""## 1 · Los decimales: cada cifra tiene su sitio

### El valor posicional

En el número **352**, el 3 no vale 3: vale **300**, porque está en el puesto de las centenas. El 5 vale 50 (decenas) y el 2 vale 2 (unidades). Cada puesto vale **10 veces más** que el de su derecha. A esto se le llama **valor posicional**: lo que vale una cifra depende del **sitio** donde está.

Los decimales son, simplemente, **seguir esa regla hacia la derecha de la coma**. Cada puesto vale **10 veces menos** que el de su izquierda:

```
     3     5     2   ,   7       4        1
   cent.  dec.  unid.  décimas  centésimas  milésimas
   300  + 50  +  2   +  0,7   +  0,04   +  0,001
```

- Una **décima** es una parte de 10: 0,1 = 1/10.
- Una **centésima** es una parte de 100: 0,01 = 1/100.
- Una **milésima** es una parte de 1.000: 0,001 = 1/1.000.

Así que **0,002 segundos** (el paso de tiempo de nuestro simulador) son **2 milésimas de segundo**: dividir un segundo en mil trocitos y coger dos.

(En español se escribe **coma** decimal: 0,002. Los ordenadores y casi todo el mundo de la programación usan **punto**: 0.002. En el curso verás las dos: la coma en el texto y el punto en el código. Significan lo mismo.)

### Comparar decimales: cuidado con la trampa

¿Qué es mayor, **0,5** o **0,45**? Mucha gente dice 0,45 porque "45 es más que 5". Pero no: hay que comparar **puesto a puesto**, empezando por la izquierda. Las décimas: 5 frente a 4. Gana 0,5. Un truco: rellena con ceros para que tengan las mismas cifras: **0,50** frente a **0,45**. Ahora se ve claro: 50 centésimas frente a 45.
"""),

md(r"""## 2 · Mover la coma: multiplicar y dividir por 10, 100, 1.000

### El truco más útil de todos

Como cada puesto vale 10 veces más que el de su derecha:

- **Multiplicar por 10** = mover la coma **un** puesto a la **derecha**: 3,52 × 10 = 35,2.
- **Multiplicar por 100** = **dos** puestos a la derecha: 3,52 × 100 = 352.
- **Multiplicar por 1.000** = **tres** puestos: 3,52 × 1.000 = 3.520 (rellenando con un cero).
- **Dividir por 10, 100, 1.000** = lo mismo, pero hacia la **izquierda**: 3,52 ÷ 10 = 0,352; 3,52 ÷ 1.000 = 0,00352.

Un ejemplo robótico: si el simulador da un paso de 0,002 s, ¿cuánto tiempo pasa en **1.000** pasos? 0,002 × 1.000 → coma tres puestos a la derecha → **2** segundos.

### Multiplicar por un decimal

Multiplicar por un número **menor que 1** hace el resultado **más pequeño**. Eso sorprende al principio ("¡multiplicar siempre hacía crecer!"), pero tiene sentido si lo lees como "**coger una parte**":

- **× 0,5** = coger la **mitad**: 40 × 0,5 = 20.
- **× 0,1** = coger la **décima parte** = dividir entre 10: 40 × 0,1 = 4.
- **× 0,8** = coger **8 décimas**: 40 × 0,8 = 32.
- **× 1** = todo, sin cambios. **× 1,5** = una vez y media: 40 × 1,5 = 60.

### Dividir por un decimal

Y al revés: dividir por un número **menor que 1** hace el resultado **más grande**. ¿Cuántas veces cabe 0,5 en 3? Seis veces (3 ÷ 0,5 = 6). La pregunta "¿cuántos pasos de 0,002 s caben en 1 segundo?" es 1 ÷ 0,002 = **500** pasos. En el NB02, con un paso de 0,003 s, salían 1 ÷ 0,003 ≈ **333** pasos por segundo.

(¿Cómo se calcula 1 ÷ 0,002 de cabeza? Un truco: multiplica **los dos** números por 1.000, que no cambia el resultado de una división: 1.000 ÷ 2 = 500.)
"""),

md(r"""## 3 · Fracciones: divisiones sin hacer

### Una fracción es una división

La fracción **3/4** ("tres cuartos") significa: divide algo en **4** partes iguales y coge **3**. Y también es, simplemente, la división 3 ÷ 4 = **0,75**. Toda fracción se puede convertir en decimal dividiendo:

| Fracción | Decimal | Cómo se lee |
|---|---|---|
| 1/2 | 0,5 | un medio, la mitad |
| 1/4 | 0,25 | un cuarto |
| 3/4 | 0,75 | tres cuartos |
| 1/10 | 0,1 | una décima |
| 1/3 | 0,333... | un tercio (¡no se acaba nunca!) |
| 2/3 | 0,666... | dos tercios |

### Decimales que no terminan

Fíjate en 1/3: 0,3333333... con treses **para siempre**. Ningún número de cifras lo escribe exacto. Si lo cortas en 0,333, te equivocas un poquito. Esto parece una curiosidad, pero es la razón de un fenómeno que verás en el NB06: el ordenador también tiene que **cortar** los números, y por eso a veces calcula `0.1 + 0.2` y le sale `0.30000000000000004`. No es que se equivoque: es que, como tú con 1/3, no puede guardar infinitas cifras.

### Fracciones con el mismo valor

1/2, 2/4, 5/10 y 50/100 son **el mismo número** (0,5). Si multiplicas o divides arriba y abajo por lo mismo, el valor no cambia. Eso se llama **simplificar** (dividir arriba y abajo: 50/100 → 1/2) y es un truco que usaremos para hacer cuentas más fáciles.
"""),

md(r"""## 4 · Porcentajes

### "Por ciento" = "de cada cien"

**Por ciento** significa literalmente "**de cada cien**". "El 30 % de los alumnos" = 30 de cada 100 alumnos. Así que un porcentaje es una fracción con 100 abajo, y por tanto un decimal:

```
   30 %  =  30/100  =  0,30          5 %  =  0,05          100 %  =  1          150 %  =  1,5
```

**La regla de oro: para usar un porcentaje en una cuenta, conviértelo en decimal** (divídelo entre 100, es decir, mueve la coma dos puestos a la izquierda).

### Calcular un porcentaje de algo

¿Cuánto es el **10 %** de un motor que da 40 N·m (no te preocupes por la unidad, la verás en el NB37)? 10 % = 0,10, así que 40 × 0,10 = **4**. ¿Y el 25 % de 40? 40 × 0,25 = 10.

### Subir o bajar un porcentaje

Aquí está el truco que más se usa (y que el curso usa sin parar):

- **Bajar un 10 %** = quedarse con el 90 % = **multiplicar por 0,9**. Un motor "un 10 % más débil" que daba 40: 40 × 0,9 = 36.
- **Subir un 10 %** = tener el 110 % = **multiplicar por 1,1**: 40 × 1,1 = 44.
- **Perder un 20 %** = quedarse con el 80 % = **multiplicar por 0,8**. Así rebotará la pelota del NB08: en cada bote conserva el 80 % de su velocidad.

### Porcentajes encadenados: la trampa

Si la pelota pierde un 20 % en cada bote, ¿cuánto le queda tras **dos** botes? La tentación es decir "pierde un 40 %, le queda un 60 %". **Falso.** Tras el primer bote le queda el 80 %; y el segundo bote le quita el 20 % **de lo que quedaba**:

```
   1 × 0,8 × 0,8  =  0,64   →   le queda el 64 %  (ha perdido un 36 %, no un 40 %)
```

Los porcentajes encadenados se **multiplican**, no se suman. La misma trampa con dinero: si algo baja un 50 % y luego sube un 50 %, **no** vuelve a su precio: 100 × 0,5 = 50, y 50 × 1,5 = 75.

### ¿Qué porcentaje es una parte?

Al revés: si de 6,25 puntos, 5 vienen de "estar de pie", ¿qué porcentaje es? **Parte ÷ total**, y multiplicado por 100 para pasarlo a porcentaje: 5 ÷ 6,25 = 0,8 → **80 %**. Es justo la cuenta de la trampa escondida del NB04.
"""),

md(r"""## 5 · Números negativos y sus signos

### Repaso

En el NB03 conociste los **números negativos**: los que están por debajo de cero, como las temperaturas bajo cero o una velocidad **hacia atrás**. En la **recta numérica**, los negativos van a la izquierda del cero:

```
   ... −3   −2   −1    0    1    2    3 ...
```

### Sumar y restar

- **Sumar** un número = moverse a la **derecha** en la recta. **Restar** = moverse a la **izquierda**. 2 − 5 = −3 (desde el 2, cinco pasos a la izquierda).
- **Restar un negativo** = sumar: 5 − (−3) = 5 + 3 = 8. (Quitar una deuda es como darte dinero.)

### Multiplicar: la regla de los signos

| | × positivo | × negativo |
|---|---|---|
| **positivo** | positivo (3 × 2 = 6) | negativo (3 × −2 = −6) |
| **negativo** | negativo (−3 × 2 = −6) | **positivo** (−3 × −2 = 6) |

Signos iguales dan positivo; signos distintos, negativo. Lo de "menos por menos es más" se puede ver así: multiplicar por −1 es **dar la vuelta** en la recta (de la derecha a la izquierda). Dar la vuelta dos veces te deja mirando como al principio. La división sigue las mismas reglas. (En el NB04 lo usaremos para entender por qué un número al cuadrado nunca es negativo.)

### Cambiar de sentido

Multiplicar una velocidad por **−1** le cambia el **sentido** sin cambiar su tamaño: de +3 (hacia abajo, por ejemplo) a −3 (hacia arriba). Y multiplicar por **−0,8** cambia el sentido **y** se queda con el 80 %: exactamente lo que le pasa a una pelota al rebotar (NB08).
"""),

md(r"""## 6 · Potencias: multiplicar un número por sí mismo

### La idea

Una **potencia** es una forma corta de escribir una multiplicación repetida:

```
   2³  =  2 × 2 × 2  =  8          ("dos elevado a tres", o "dos al cubo")
   5²  =  5 × 5  =  25             ("cinco al cuadrado")
   10⁴ =  10 × 10 × 10 × 10  =  10.000
```

El número de abajo (2) es la **base**; el pequeño de arriba (3), el **exponente**: cuántas veces se multiplica la base por sí misma. Al cuadrado (exponente 2) se le llama así porque 5² es el área de un **cuadrado** de lado 5; al cubo (exponente 3), porque 2³ es el volumen de un **cubo** de lado 2.

(Los ordenadores no saben escribir el exponente pequeño arriba. En Python, que verás desde el NB05, se escribe con dos asteriscos: `2 ** 3`. En muchos textos se ve también `2^3`.)

### Las potencias de 10

Son las más importantes, porque son las que usamos para contar:

| Potencia | Valor | Truco |
|---|---|---|
| 10¹ | 10 | un cero |
| 10² | 100 | dos ceros |
| 10³ | 1.000 | tres ceros (mil) |
| 10⁶ | 1.000.000 | seis ceros (un millón) |
| 10⁹ | 1.000.000.000 | nueve ceros (mil millones) |

**El exponente es el número de ceros.** Así de fácil.

### Exponente 0 y exponentes negativos

¿Qué podría ser 10⁰? ¿Y 10⁻¹? Fíjate en lo que pasa al **bajar** el exponente de uno en uno en la tabla:

```
   10³ = 1.000
   10² = 100        (÷ 10)
   10¹ = 10         (÷ 10)
   10⁰ = 1          (÷ 10)
   10⁻¹ = 0,1       (÷ 10)
   10⁻² = 0,01      (÷ 10)
   10⁻³ = 0,001     (÷ 10)
```

Cada vez que el exponente baja 1, el número se **divide entre 10**. Siguiendo el patrón sin pararse:

- **Cualquier número elevado a 0 vale 1.** (2⁰ = 1, 10⁰ = 1, 7⁰ = 1.)
- **Un exponente negativo significa "uno partido por"**: 10⁻³ = 1/10³ = 1/1.000 = 0,001. Y 2⁻¹ = 1/2 = 0,5.

Con los negativos, **el exponente dice cuántos puestos va la coma a la izquierda**: 10⁻⁶ = 0,000001 (seis puestos: una millonésima).

### Dos reglas que ahorran trabajo

- **Multiplicar potencias de la misma base = sumar exponentes**: 10² × 10³ = 10⁵. (Cien por mil son cien mil: 2 ceros + 3 ceros = 5 ceros.)
- **Dividir = restar exponentes**: 10⁵ ÷ 10² = 10³.

### Crecimiento exponencial

Hay una vieja leyenda: el inventor del ajedrez pidió como premio un grano de trigo en la primera casilla, 2 en la segunda, 4 en la tercera, y así, **doblando** en cada una de las 64 casillas. El rey se rio... hasta que vio que en la última casilla tocaban 2⁶³ granos: unos **9 trillones**, más trigo del que ha producido la humanidad en toda su historia.

Cuando algo se **multiplica** por lo mismo en cada paso (en vez de sumarse), crece de forma **exponencial**: al principio despacio, y luego de forma explosiva. Ya lo viste en el NB03 (la "maldición de la dimensionalidad": las posibilidades de una tabla se multiplican con cada motor), y lo verás en el NB49 (una simulación que "explota").
"""),

md(r"""## 7 · Raíces: deshacer una potencia

### La raíz cuadrada

La **raíz cuadrada** es la operación contraria a elevar al cuadrado. La pregunta que contesta es: **¿qué número, multiplicado por sí mismo, da este?**

```
   √25 = 5,  porque 5 × 5 = 25          √100 = 10          √9 = 3          √1 = 1
```

El símbolo **√** se llama "raíz". Si el área de un cuadrado es 25 m², su lado es √25 = 5 m: la raíz "deshace" el cuadrado.

### Raíces que no son exactas

¿Y √2? No hay ningún número "bonito" que multiplicado por sí mismo dé 2: 1 × 1 = 1 (poco), 2 × 2 = 4 (mucho). Está entre 1 y 2, más cerca de 1,4 (porque 1,4 × 1,4 = 1,96). Con más precisión, **√2 ≈ 1,41421...**, con cifras que nunca terminan ni se repiten. Para estas raíces se usa la calculadora (o el ordenador). Lo importante es saber **qué significan** y estimarlas: √50 está entre 7 (√49) y 8 (√64), muy cerca de 7.

### La raíz como exponente ½

Un dato curioso que usarás en código: la raíz cuadrada es lo mismo que **elevar a ½** (o a 0,5): √25 = 25^0,5 = 5. ¿Por qué? Por la regla de sumar exponentes: 25^0,5 × 25^0,5 = 25^(0,5 + 0,5) = 25¹ = 25. Así que 25^0,5 es "un número que multiplicado por sí mismo da 25": justo la raíz. En Python, `25 ** 0.5` da 5.0 (lo verás en el NB12).

(Existe también la **raíz cúbica**, ∛, que deshace el cubo: ∛8 = 2, porque 2 × 2 × 2 = 8. Se usa mucho menos.)
"""),

md(r"""## 8 · Notación científica: números gigantes y diminutos

### El problema

La masa de la Tierra son unos **5.970.000.000.000.000.000.000.000** kg. El diámetro de un átomo, unos **0,0000000001** metros. Contar los ceros es un suplicio, y es facilísimo equivocarse en uno.

### La solución

La **notación científica** escribe cualquier número como **un número entre 1 y 10, multiplicado por una potencia de 10**:

```
   5.970.000.000.000.000.000.000.000  =  5,97 × 10²⁴     (la coma se mueve 24 puestos)
   0,0000000001                      =  1 × 10⁻¹⁰       (la coma se mueve 10 puestos a la derecha)
   159.505                           ≈  1,6 × 10⁵
   0,002                             =  2 × 10⁻³
```

El exponente dice **cuántos puestos hay que mover la coma**, y su signo, **hacia dónde**: positivo = número grande (mueve a la derecha); negativo = número pequeño (mueve a la izquierda).

### Cómo lo escribe el ordenador: la "e"

Los ordenadores tampoco saben escribir "× 10" con un exponente arriba, así que usan una **e** (de "exponente"):

```
   5.97e24     significa  5,97 × 10²⁴
   2e-3        significa  2 × 10⁻³ = 0,002
   1e-8        significa  1 × 10⁻⁸ = 0,00000001
   6.4e-06     significa  6,4 × 10⁻⁶ = 0,0000064
```

**¡Ojo!** Esa "e" **no** tiene nada que ver con el número e ≈ 2,718 que verás más adelante (NB15b). Es solo una abreviatura de "por diez elevado a". La verás constantemente en las salidas del curso: cuando el ordenador imprime `1.5e-05`, está diciendo 0,000015.

### Orden de magnitud

El exponente de la potencia de 10 da el **orden de magnitud** de un número: si es de las decenas, de los miles, de las milésimas... Decir que dos números "se diferencian en tres órdenes de magnitud" significa que uno es unas **mil** veces mayor que el otro (10³). Es una forma rápida de comparar: un error de 10⁻¹³ frente a uno de 10⁻² no es "un poco más pequeño": es **cien mil millones** de veces más pequeño.
"""),

md(r"""## 9 · Prefijos: kilo, mili, micro...

Para no escribir potencias todo el rato, las unidades usan **prefijos**, que son potencias de 10 con nombre:

| Prefijo | Símbolo | Vale | Ejemplo |
|---|---|---|---|
| giga | G | 10⁹ (mil millones) | un gigabyte |
| mega | M | 10⁶ (un millón) | un megapíxel |
| kilo | k | 10³ (mil) | un kilómetro = 1.000 m; un kilogramo = 1.000 g |
| — | — | 1 | un metro, un segundo |
| centi | c | 10⁻² (una centésima) | un centímetro = 0,01 m |
| mili | m | 10⁻³ (una milésima) | un milisegundo (ms) = 0,001 s |
| micro | µ | 10⁻⁶ (una millonésima) | un microsegundo (µs) = 0,000001 s |
| nano | n | 10⁻⁹ (una milmillonésima) | un nanómetro |

Así que **2 ms** son 0,002 s (un paso de nuestra simulación), y **15 µs** son 0,000015 s (lo que tarda el ordenador en calcular ese paso, como medirás en el NB49). La letra **µ** es la "mu" griega.

Convertir es mover la coma: de milisegundos a segundos, tres puestos a la izquierda (34 ms = 0,034 s); de metros a milímetros, tres a la derecha (0,005 m = 5 mm).
"""),

md(r"""## 10 · Redondear y equivocarse un poco

### Redondear

**Redondear** es quitar cifras que no necesitas, eligiendo el número más cercano. Para redondear 3,1416 a dos decimales, miras la **tercera** cifra decimal (un 1): si es 5 o más, la segunda sube; si es menos de 5, se queda. 3,1416 → **3,14**. Y 2,678 → **2,68** (el 8 hace subir el 7).

El símbolo **≈** significa "aproximadamente igual a": π ≈ 3,14.

### Error absoluto y error relativo

Si mides algo y te equivocas, hay dos formas de decir **cuánto**:

- **Error absoluto**: la diferencia, sin más. Si la pelota debía caer 0,75 m y tu simulador dice 0,725 m, el error absoluto es 0,025 m (2,5 cm).
- **Error relativo**: el error **comparado con el tamaño** de lo que mides, normalmente en porcentaje: 0,025 ÷ 0,75 ≈ 0,033 → un **3,3 %**.

¿Por qué hacen falta los dos? Equivocarse en 1 cm es muchísimo si mides una hormiga, y nada si mides la distancia a la Luna. El error relativo lo pone en contexto. Los usaremos para decidir si un simulador es "suficientemente bueno" (NB02, NB07).
"""),

md(r"""## 11 · Proporcionalidad y regla de tres

### Proporcional: el doble da el doble

Dos cosas son **proporcionales** (o "directamente proporcionales") si al multiplicar una por algo, la otra se multiplica por lo mismo. Si 1 paso de simulación dura 0,002 s, 10 pasos duran 0,02 s, y 1.000 pasos, 2 s: el tiempo es proporcional al número de pasos.

### La regla de tres

Con dos cosas proporcionales, la **regla de tres** saca un dato que falta. Si 500 pasos son 1 segundo, ¿cuántos pasos son 3,4 segundos?

```
   500 pasos   →   1 s
     ?  pasos  →   3,4 s           ? = 500 × 3,4 ÷ 1 = 1.700 pasos
```

"Multiplica en cruz y divide por el que queda."

### Inversamente proporcional: el doble da la mitad

Dos cosas son **inversamente proporcionales** si al multiplicar una por algo, la otra se **divide** por lo mismo. Si el paso de tiempo se hace el **doble** de grande, hacen falta la **mitad** de pasos para simular un segundo. Pasos por segundo = 1 ÷ paso de tiempo.

Reconocer si dos cosas son proporcionales, inversamente proporcionales... o **ninguna de las dos** (como la altura de una pelota y el tiempo que lleva cayendo: lo verás en el NB04b) es una de las habilidades más útiles en ciencia e ingeniería.
"""),

md(r"""## 12 · Resumen de la lección

1. **Decimales**: cada puesto a la derecha de la coma vale 10 veces menos (décimas, centésimas, milésimas). Para comparar, rellena con ceros.
2. **Mover la coma**: × 10, 100, 1.000 → a la derecha; ÷ → a la izquierda. Multiplicar por un número menor que 1 = coger una parte; dividir por él = cuántas veces cabe (el resultado crece).
3. **Fracciones** = divisiones (3/4 = 0,75). Algunas dan decimales infinitos (1/3 = 0,333...).
4. **Porcentajes**: pásalos a decimal (30 % = 0,3). Bajar un 10 % = × 0,9; subir un 10 % = × 1,1. **Encadenados se multiplican** (× 0,8 × 0,8 = × 0,64). Qué % es: parte ÷ total × 100.
5. **Negativos**: restar un negativo es sumar; signos iguales dan +, distintos dan −. × (−1) cambia el sentido.
6. **Potencias**: multiplicación repetida (base y exponente). 10ⁿ = n ceros; a⁰ = 1; 10⁻ⁿ = 1/10ⁿ. Multiplicar = sumar exponentes. Crecimiento exponencial = multiplicar por lo mismo en cada paso.
7. **Raíces**: √ deshace el cuadrado (√25 = 5). √x = x^0,5.
8. **Notación científica**: número entre 1 y 10 × potencia de 10. En el ordenador, `2e-3` = 2 × 10⁻³. Esa "e" no es el número e. Orden de magnitud = el exponente.
9. **Prefijos**: kilo (10³), mili (10⁻³), micro µ (10⁻⁶)...
10. **Redondear**, ≈, error **absoluto** (diferencia) y **relativo** (comparado con el tamaño, en %).
11. **Proporcional** (doble → doble) y **regla de tres**; **inversamente proporcional** (doble → mitad).

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Valor posicional** | Lo que vale una cifra depende del puesto donde está. |
| **Décima, centésima, milésima** | 0,1; 0,01; 0,001. |
| **Porcentaje (%)** | "De cada cien": 30 % = 0,3. |
| **Potencia, base, exponente** | 2³: base 2, exponente 3 = 2 × 2 × 2. |
| **Raíz cuadrada (√)** | El número que, multiplicado por sí mismo, da el de dentro. |
| **Notación científica** | 5,97 × 10²⁴; en el ordenador, `5.97e24`. |
| **Orden de magnitud** | El exponente de la potencia de 10: si un número es de las decenas, los miles, las milésimas... |
| **Prefijo** | Potencia de 10 con nombre: kilo, mili, micro... |
| **Error absoluto / relativo** | La diferencia / la diferencia comparada con el tamaño. |
| **Proporcional / inversamente proporcional** | Doble → doble / doble → mitad. |
"""),

md(r"""## 13 · Preguntas de comprensión

Intenta cada una con papel y lápiz (o de cabeza) antes de abrir la solución.

**P1.** Ordena de menor a mayor: 0,3; 0,25; 0,305; 0,03.

**P2.** El simulador da pasos de 0,005 s. ¿Cuántos pasos hacen falta para simular 2 segundos?

**P3.** Un motor da 120 de fuerza. Si se calienta, pierde un 15 %. ¿Cuánto da caliente?

**P4.** Una pelota conserva el 80 % de su velocidad en cada bote. ¿Qué porcentaje le queda tras **3** botes?

**P5.** Calcula: 10² × 10⁻⁵. Escríbelo como potencia de 10 y como decimal.

**P6.** ¿Entre qué dos números enteros está √30? ¿Más cerca de cuál?

**P7.** Traduce lo que dice el ordenador: `3.2e-04` y `1.5e6`.

**P8.** Un cálculo tarda 250 µs. ¿Cuántos segundos son? ¿Y milisegundos?

**P9.** Un robot debería avanzar 2 m y avanza 1,9 m. Calcula el error absoluto y el relativo.

**P10.** Si un paso de simulación de 0,002 s tarda en calcularse 15 µs, ¿cuántas veces más rápido que la realidad simula el ordenador?
"""),

md(r"""<details>
<summary>▶ Solución P1</summary>

Rellenando con ceros hasta tres decimales: 0,300; 0,250; 0,305; 0,030. Ordenados: **0,03 < 0,25 < 0,3 < 0,305**. (La trampa: 0,305 es mayor que 0,3 aunque "parezca" que tiene más cifras raras.)
</details>

<details>
<summary>▶ Solución P2</summary>

2 ÷ 0,005. Multiplicando los dos por 1.000: 2.000 ÷ 5 = **400 pasos**.
</details>

<details>
<summary>▶ Solución P3</summary>

Perder un 15 % = quedarse con el 85 % = × 0,85. 120 × 0,85 = **102**.
</details>

<details>
<summary>▶ Solución P4</summary>

0,8 × 0,8 × 0,8 = 0,8³ = **0,512 → un 51,2 %**. (No un 40 %: los porcentajes encadenados se multiplican.)
</details>

<details>
<summary>▶ Solución P5</summary>

Sumando exponentes: 10^(2 + (−5)) = **10⁻³ = 0,001**. (Cien por una cienmilésima es una milésima.)
</details>

<details>
<summary>▶ Solución P6</summary>

5² = 25 y 6² = 36, así que √30 está **entre 5 y 6**. 30 está más cerca de 25 que de 36, así que la raíz está más cerca de **5** (en realidad, √30 ≈ 5,48).
</details>

<details>
<summary>▶ Solución P7</summary>

`3.2e-04` = 3,2 × 10⁻⁴ = **0,00032** (la coma cuatro puestos a la izquierda). `1.5e6` = 1,5 × 10⁶ = **1.500.000** (un millón y medio).
</details>

<details>
<summary>▶ Solución P8</summary>

250 µs = 250 × 10⁻⁶ s = **0,00025 s**. En milisegundos: 1 ms = 1.000 µs, así que 250 µs = **0,25 ms**.
</details>

<details>
<summary>▶ Solución P9</summary>

Error absoluto: 2 − 1,9 = **0,1 m** (10 cm). Error relativo: 0,1 ÷ 2 = 0,05 → **5 %**.
</details>

<details>
<summary>▶ Solución P10</summary>

0,002 s de realidad ÷ 0,000015 s de cálculo ≈ **133 veces** más rápido que la realidad. (Con notación científica: 2 × 10⁻³ ÷ 1,5 × 10⁻⁵ = (2 ÷ 1,5) × 10^(−3 − (−5)) ≈ 1,33 × 10² = 133.) Por eso se puede entrenar a un robot durante "años" de experiencia en unas horas de ordenador.
</details>
"""),

md(r"""## 14 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **NB04** vuelve la robótica: la **recompensa**, la pieza (4) del mapa. Y verás que ya tienes todo lo que hace falta para sus cuentas: decimales, porcentajes, negativos... y una operación que hoy has visto de pasada, **elevar al cuadrado**, que allí cobrará un sentido muy especial.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB03b_numeros_a_fondo.ipynb")
    build(out, cells, title="NB03b · Números a fondo")
