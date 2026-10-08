"""Construye NB04b · Letras y ecuaciones (Parte 0 · lección intermedia, conceptual; código solo en la Práctica en MuJoCo, ya escrito).

Añadida tras la auditoría de 2026-10-04: el curso despejaba fórmulas,
simplificaba fracciones con letras y daba por buena la altura "exacta" de la
pelota (0,75 m) sin haber enseñado álgebra. Letras en las fórmulas, sustituir,
jerarquía de operaciones, propiedad distributiva y factor común; ecuaciones
como balanza, despejar con operaciones inversas, despejar fórmulas (v = d/t,
F = m·a); fracciones con letras: qué se puede cancelar y qué no; funciones como
máquinas, tablas, recta y parábola; la caída libre deducida (v = g·t,
velocidad media, d = ½·g·t²) y el 0,75 m del NB02; unidades que viajan con los
números.

Práctica en MuJoCo (medido, g=10, paso 0,001, radio 0,05): tabla MuJoCo vs 2−5t² dif. ≤ 3 mm
(0,5 s: 0,7475 vs 0,75); toca el suelo 0,6245 predicho / 0,6250 medido; vídeo pelotas r=0,25 caen 2 y 8 m:
0,632/1,265 predicho (doble); Luna 0,5 s → 1,797, toca 1,5516/1,5520; desde 5,05 m → 1,0000 s.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB04b · Letras y ecuaciones

**Parte 0 · El terreno — Lección intermedia (entre el NB04 y el NB05)**

> En el NB02 te dije que "la física real" ponía la pelota a **0,75 metros** a los 0,5 segundos, y te pedí que te fiaras. En el NB04 escribimos la recompensa como una receta con letras: `5 + 1,25 × velocidad − 0,1 × esfuerzo`. Más adelante tendremos que **despejar** fórmulas, **simplificar** fracciones con letras y leer ecuaciones como `a = F / m`. Hoy aprendemos el idioma en el que se escriben todas esas cosas: el **álgebra**.

Sin escribir código todavía (al final, en la **Práctica en MuJoCo**, pondrás tu fórmula a competir con MuJoCo, con código ya escrito), y con mucha calma. Al final de la lección:

- Sabrás qué significa una letra en una fórmula y cómo **usar** una fórmula.
- Sabrás **resolver ecuaciones** y **despejar** cualquier letra de una fórmula sencilla.
- Sabrás qué se puede **tachar** en una fracción con letras... y qué no (la trampa más común de las matemáticas).
- Entenderás qué es una **función** y cómo se ve en una gráfica.
- Y **deducirás tú mismo** el famoso 0,75 m de la pelota. Sin fiarte de nadie.
"""),

md(r"""## 1 · Las letras en las fórmulas

### Una letra es un hueco con nombre

Cuando escribimos la recompensa de nuestro humanoide (NB04) como

```
   recompensa = 5 + 1,25 × v − 0,1 × e
```

la **v** no es un número concreto: es un **hueco** donde va la velocidad, sea cual sea. Si el robot avanza a 1 m/s, pones 1; si va a 0,5 m/s, pones 0,5. Y la **e** es el hueco del esfuerzo. Una fórmula con letras es una **receta general**: sirve para **todos** los casos a la vez.

A las letras de una fórmula se les llama **variables** (porque su valor puede variar). Verás la misma palabra en programación (NB06), con una idea muy parecida: una caja con nombre que guarda un valor.

### Usar una fórmula: sustituir

Usar una fórmula es **sustituir** cada letra por su valor y hacer las cuentas. Con v = 1 y e = 0,2:

```
   recompensa = 5 + 1,25 × 1 − 0,1 × 0,2  =  5 + 1,25 − 0,02  =  6,23
```

### Convenios de escritura

Para escribir menos, los matemáticos usan algunos convenios que verás por todas partes:

- **El signo de multiplicar se puede omitir** entre un número y una letra, o entre dos letras: `2x` significa 2 × x, `m g` o `mg` significa m × g. También se usa un punto en vez de la cruz: `m · g`.
- **Las divisiones se escriben como fracciones**: `d / t` o con una raya horizontal, d arriba y t abajo.
- **Las letras griegas** son letras normales, solo que de otro alfabeto: θ (**theta**, muy usada para ángulos), ω (omega), α (alfa), μ (mu), σ (sigma)... Las irás conociendo.
"""),

md(r"""## 2 · El orden en que se hacen las cuentas

### La jerarquía de las operaciones

¿Cuánto es `2 + 3 × 4`? Si vas de izquierda a derecha, 5 × 4 = 20. Pero la respuesta correcta es **14**, porque **la multiplicación va antes que la suma**. Hay un orden pactado en todo el mundo (y los ordenadores lo respetan igual, como verás en el NB06):

1. **Paréntesis** primero (lo de dentro antes que lo de fuera).
2. **Potencias** y raíces (NB03b).
3. **Multiplicaciones y divisiones**, de izquierda a derecha.
4. **Sumas y restas**, de izquierda a derecha.

Así: `2 + 3 × 4 = 2 + 12 = 14`, pero `(2 + 3) × 4 = 5 × 4 = 20`. Los paréntesis sirven para **cambiar el orden** cuando lo necesitas.

Un caso que confunde a todo el mundo: `−3²`. ¿Es 9 o −9? Como la potencia va antes que el signo menos (que es como multiplicar por −1), es **−(3²) = −9**. Si quieres el cuadrado de −3, hay que escribir `(−3)² = 9`. (Lo volverás a ver en el NB06: Python hace exactamente lo mismo.)

### La propiedad distributiva

Multiplicar un número por una suma entre paréntesis es lo mismo que multiplicarlo por **cada** sumando y luego sumar:

```
   3 × (2 + 5)  =  3 × 2 + 3 × 5  =  6 + 15  =  21          (y, en efecto, 3 × 7 = 21)
   a × (b + c)  =  a·b + a·c
```

Imagina 3 bolsas, cada una con 2 manzanas y 5 peras: tienes 3 × 2 manzanas y 3 × 5 peras.

### Sacar factor común

Es la misma propiedad leída **al revés**: si todos los sumandos se multiplican por lo mismo, se puede **sacar fuera**:

```
   m·g − m·a  =  m·(g − a)
```

Lo usaremos para simplificar fórmulas de física: "sacar la masa fuera" muchas veces deja ver que la masa **no importa** (como descubrirás en el NB37 con el péndulo).
"""),

md(r"""## 3 · Ecuaciones: la balanza

### Qué es una ecuación

Una **ecuación** es una igualdad con un **hueco desconocido**, y **resolverla** es averiguar qué valor tiene que ir en el hueco para que la igualdad sea cierta. Por ejemplo:

```
   3·x + 2 = 11
```

¿Qué número, multiplicado por 3 y sumándole 2, da 11? Se puede adivinar (es 3), pero con ecuaciones más difíciles adivinar no sirve. Hay un método.

### La regla de oro: lo mismo a los dos lados

Imagina una **balanza** en equilibrio: a la izquierda, `3·x + 2`; a la derecha, `11`. Puedes hacer **cualquier cosa** a la balanza... siempre que se la hagas a **los dos platos a la vez**: así sigue en equilibrio.

El objetivo es dejar la **x sola** en un plato. Para quitar lo que le "estorba", se usa la operación **contraria** (inversa):

| Para quitar... | se hace... |
|---|---|
| un **+ 2** | **restar 2** a los dos lados |
| un **− 2** | **sumar 2** a los dos lados |
| un **× 3** | **dividir entre 3** los dos lados |
| un **÷ 3** | **multiplicar por 3** los dos lados |
| un **²** | hacer la **raíz cuadrada** de los dos lados |
| una **√** | elevar **al cuadrado** los dos lados |

Resolvamos `3·x + 2 = 11` paso a paso:

```
   3·x + 2 = 11
   3·x + 2 − 2 = 11 − 2        (quito el +2: resto 2 a los dos lados)
   3·x = 9
   3·x ÷ 3 = 9 ÷ 3             (quito el ×3: divido entre 3 los dos lados)
   x = 3
```

Y **siempre se comprueba**: 3 × 3 + 2 = 11. ✓

El orden importa: se quitan primero las sumas y restas (lo que está "más fuera") y después las multiplicaciones y divisiones. Es como quitarse la ropa: primero el abrigo, después el jersey.

### "Pasar al otro lado"

En clase quizá te hayan dicho "lo que suma pasa restando" o "lo que multiplica pasa dividiendo". Es un **atajo** de la regla de la balanza: restar 2 a los dos lados hace que el +2 "desaparezca" de la izquierda y aparezca un −2 a la derecha. Funciona, pero es mejor entender **por qué**: así no te equivocarás nunca.
"""),

md(r"""## 4 · Despejar fórmulas

### La misma técnica, con letras

**Despejar** una fórmula es reescribirla para dejar sola **otra** de sus letras. Es resolver una ecuación en la que las demás letras hacen de números. Por ejemplo, la velocidad es la distancia recorrida dividida entre el tiempo:

```
   v = d / t
```

¿Y si quiero saber la **distancia**, conociendo la velocidad y el tiempo? Despejo d: tiene un "÷ t" que le estorba, así que **multiplico por t** los dos lados:

```
   v · t = d / t · t
   v · t = d            →   d = v · t     ("distancia = velocidad × tiempo")
```

¿Y el **tiempo**? Partiendo de `d = v · t`, divido entre v los dos lados:

```
   t = d / v            ("tiempo = distancia ÷ velocidad")
```

Una sola fórmula, y tres recetas: para la velocidad, la distancia o el tiempo. Ya no hace falta memorizar tres.

### Más ejemplos que verás en el curso

- **Segunda ley de Newton** (NB37): `F = m · a` (fuerza = masa × aceleración). Despejando: `a = F / m` (la aceleración que provoca una fuerza) y `m = F / a`.
- **El peso**: `P = m · g`. Si un robot pesa 231,5 newtons (la unidad de fuerza, NB37) y g = 9,81, su masa es m = 231,5 / 9,81 ≈ **23,6 kg**.
- **Despejar con una raíz**: si `A = l²` (el área de un cuadrado de lado l), entonces `l = √A`.

### Una ecuación con la letra en dos sitios

A veces la letra aparece varias veces. La idea es **juntarlas** primero en un mismo lado:

```
   5·x = 2·x + 9
   5·x − 2·x = 9          (resto 2·x a los dos lados)
   3·x = 9                (5 equis menos 2 equis son 3 equis)
   x = 3
```
"""),

md(r"""## 5 · Fracciones con letras: qué se puede tachar

### Simplificar es tachar factores comunes

En el NB03b viste que 50/100 = 1/2 porque puedes dividir arriba y abajo por lo mismo (50). Con letras es igual: si la misma letra **multiplica** a todo lo de arriba y a todo lo de abajo, se puede **tachar** (es dividir arriba y abajo por ella):

```
   m · g · L         g
   ─────────   =   ───          (tachamos una m y una L arriba y abajo)
   m · L · L         L
```

Esta es, casi exactamente, la cuenta que harás en el NB37 con el péndulo, y que te dirá algo sorprendente: **la masa se tacha**, así que un palo pesado y uno ligero caen igual de deprisa. Las matemáticas te dirán cosas del mundo sin hacer ningún experimento.

### La trampa más común de las matemáticas

**Solo se pueden tachar cosas que MULTIPLICAN a todo, nunca cosas que SUMAN.**

```
   a · b
   ─────  =  b       ✓  (la a multiplica arriba y abajo)
     a

   a + b
   ─────  ≠  b       ✗  ¡NO! la a está SUMANDO
     a
```

Compruébalo con números: con a = 2 y b = 3, (2 · 3) / 2 = 6 / 2 = **3 = b** ✓. Pero (2 + 3) / 2 = 5 / 2 = **2,5**, que **no** es 3. Si tienes dudas, **prueba con números**: es el mejor detector de errores de álgebra que existe.

### Partir una fracción

Lo que **sí** se puede hacer con una suma de arriba es **partir** la fracción:

```
   a + b       a     b
   ─────  =   ─── + ───           (5/2 = 2/2 + 3/2 = 1 + 1,5 = 2,5 ✓)
     c         c     c
```
"""),

md(r"""## 6 · Funciones: máquinas que transforman números

### La máquina

Una **función** es una **máquina**: le metes un número (la **entrada**) y te devuelve otro (la **salida**), siempre siguiendo la misma regla. Se escribe así:

```
   f(x) = 2·x + 1          "f de x es igual a dos equis más uno"
```

`f` es el nombre de la máquina, y `x` el hueco de la entrada. Para usarla, sustituyes: f(3) = 2 · 3 + 1 = 7; f(0) = 1; f(−2) = −3.

¡Ojo con la notación! `f(3)` **no** es "f por 3": los paréntesis después del nombre de una función significan "**aplica** la máquina f al número 3". (En programación, que empieza en el NB05, las funciones se escriben exactamente igual: `print("hola")` es aplicar la función `print` al texto `"hola"`.)

### Tablas y gráficas

Para ver cómo se comporta una función, se hace una **tabla** de entradas y salidas, y se dibuja cada pareja como un punto: la entrada en el eje horizontal y la salida en el vertical (lo verás con calma en el NB12). Uniendo los puntos sale la **gráfica** de la función.

Dos formas que verás sin parar:

**La recta**: `f(x) = 2·x + 1`. Cada vez que la entrada sube 1, la salida sube **siempre** lo mismo (2). Su gráfica es una línea recta. El número que multiplica a la x (el 2) dice **cuánto se inclina**: es la **pendiente** (NB16). Las relaciones **proporcionales** del NB03b son rectas que pasan por el cero.

| x | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 2x + 1 | 1 | 3 | 5 | 7 |

**La parábola**: `f(x) = x²`. Al subir la entrada, la salida sube **cada vez más deprisa**: 0, 1, 4, 9, 16... Su gráfica es una curva con forma de U (o de cuenco). Es la forma de la trayectoria de una pelota lanzada... y la forma de la caída libre, que es lo siguiente.

| x | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| x² | 0 | 1 | 4 | 9 | 16 |
"""),

md(r"""## 7 · La caída libre: el 0,75 m, deducido

### La velocidad crece de forma proporcional

En el NB02 vimos que la gravedad **cambia la velocidad** de forma constante: cada segundo, la pelota cae **g** metros por segundo más deprisa (g ≈ 10 m/s² en la Tierra, si redondeamos 9,81). Si parte quieta, su velocidad a los t segundos es:

```
   v = g · t          (proporcional al tiempo: el doble de tiempo, el doble de velocidad)
```

A los 0,5 s, v = 10 · 0,5 = **5 m/s**.

### ¿Cuánto ha caído? La velocidad media

Si la velocidad fuera **constante**, la distancia sería `d = v · t` (sección 4). Pero no lo es: crece desde 0 hasta g·t. ¿Qué velocidad usamos? Como crece **de forma uniforme** (siempre lo mismo cada instante), la pelota recorre lo mismo que si hubiera ido todo el rato a la **velocidad media**: la de la mitad del camino entre la inicial y la final:

```
   velocidad media = (0 + g·t) / 2  =  ½ · g · t
```

(Igual que si en un viaje vas la mitad del tiempo a 0 km/h y la otra mitad a 100, es como ir todo el rato a 50. Aquí no va "a saltos", pero al crecer uniformemente, el razonamiento funciona igual.)

Y ahora sí, distancia = velocidad (media) × tiempo:

```
   d = ½ · g · t · t  =  ½ · g · t²
```

¡Una parábola! La distancia caída **no** es proporcional al tiempo: el **doble** de tiempo da **cuatro veces** más distancia (porque el tiempo va al cuadrado: 2² = 4). Por eso las cosas caen "cada vez más deprisa".

### El 0,75 m

La pelota del NB02 empezaba a 2 m de altura. Su altura a los t segundos es la altura inicial menos lo que ha caído:

```
   h = 2 − ½ · g · t²
```

A los 0,5 segundos, con g = 10:

```
   h = 2 − ½ · 10 · 0,5²  =  2 − 5 · 0,25  =  2 − 1,25  =  0,75 m
```

**0,75 metros**. El número que te pedí que creyeras en el NB02 ya no es un acto de fe: lo has deducido tú.

### ¿Por qué falló la tabla del NB02?

En la tabla del NB02 calculábamos cada paso con la velocidad **del final** del paso (velocidad nueva × 0,1). Pero durante esa décima de segundo, la pelota no fue todo el rato a esa velocidad: empezó más despacio. Al usar la velocidad del final (la más alta del tramo), contábamos **de más** en cada paso, y por eso la pelota "caía más" (0,50 m en vez de 0,75 m). Con pasos más pequeños, el error se reduce (lo comprobarás en el NB07, con código).

### En la Luna

En la Luna, la gravedad es mucho más débil: g ≈ 1,62 m/s². La misma pelota, a los 0,5 s:

```
   h = 2 − ½ · 1,62 · 0,25  =  2 − 0,2025  ≈  1,80 m
```

Apenas ha caído 20 cm. (Lo usarás en un ejercicio del NB07.)
"""),

md(r"""## 8 · Las unidades viajan con los números

En las fórmulas de física, cada número lleva su **unidad** (metros, segundos, kilos...), y **las unidades se operan igual que las letras**:

```
   d = v · t   →   (m/s) · s  =  m        (los segundos se tachan: queda una distancia, en metros) ✓
```

Esto es un **detector de errores** buenísimo: si al final de una cuenta las unidades no dan lo que esperabas (por ejemplo, te sale una distancia en "metros por segundo"), te has equivocado en algún sitio. En la caída libre: g · t² → (m/s²) · s² = m ✓. Lo verás a fondo en el NB37 (con newtons, julios y compañía).

Una regla de oro: **solo se pueden sumar cosas con la misma unidad**. 2 metros + 3 segundos no tiene sentido (como sumar peras con manzanas).
"""),

md(r"""## 9 · Resumen de la lección

1. Una **letra** en una fórmula es un hueco con nombre (una **variable**). Usar la fórmula = **sustituir**. `2x` = 2 × x; `mg` = m × g.
2. **Jerarquía**: paréntesis → potencias → × y ÷ → + y −. `−3² = −9`, `(−3)² = 9`.
3. **Distributiva**: a·(b + c) = a·b + a·c. **Factor común**: m·g − m·a = m·(g − a).
4. **Ecuación** = balanza: haz lo mismo a los dos lados. Quita lo que estorba con la operación **inversa** (primero sumas/restas, luego ×/÷). **Comprueba** siempre.
5. **Despejar** una fórmula: d = v·t, t = d/v, a = F/m, l = √A.
6. **Fracciones con letras**: solo se tacha lo que **multiplica** a todo, nunca lo que **suma**. En caso de duda, prueba con números.
7. **Función** = máquina entrada → salida: f(x). **Recta** (sube siempre lo mismo) y **parábola** (sube cada vez más deprisa).
8. **Caída libre**: v = g·t, d = ½·g·t², h = h₀ − ½·g·t². Con h₀ = 2, g = 10, t = 0,5 → **0,75 m**.
9. **Las unidades** se operan como letras y detectan errores. Solo se suman cosas con la misma unidad.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Álgebra** | Las matemáticas con letras que representan números. |
| **Variable** | Letra que representa un número que puede variar. |
| **Sustituir** | Poner el valor de cada letra en una fórmula. |
| **Jerarquía de las operaciones** | El orden pactado: paréntesis, potencias, × ÷, + −. |
| **Propiedad distributiva / factor común** | a·(b + c) = a·b + a·c, en un sentido o en el otro. |
| **Ecuación** | Igualdad con un valor desconocido. |
| **Resolver / despejar** | Encontrar el valor desconocido / dejar sola una letra de una fórmula. |
| **Operación inversa** | La que deshace a otra: restar deshace sumar, dividir deshace multiplicar... |
| **Simplificar (tachar)** | Dividir arriba y abajo de una fracción por lo mismo. |
| **Función, f(x)** | Máquina que convierte una entrada en una salida con una regla fija. |
| **Recta / parábola** | Gráfica de y = m·x + b / de y = x² (o parecidas). |
| **Caída libre** | Caer solo por la gravedad: d = ½·g·t². |
"""),

md(r"""## 10 · Preguntas de comprensión

**P1.** Calcula: `10 − 2 × 3²` y `(10 − 2) × 3²`.

**P2.** Resuelve: `4·x − 7 = 13`. Comprueba tu respuesta.

**P3.** Despeja la masa m de la fórmula de la energía de movimiento `E = ½ · m · v²`.

**P4.** Un robot recorre 3 metros en 6 segundos. ¿A qué velocidad va? ¿Cuánto tardaría en recorrer 10 metros a esa velocidad?

**P5.** Simplifica: `(m · g · h) / (m · g)`. ¿Y se puede simplificar `(m + g) / m`?

**P6.** Saca factor común: `3·a + 3·b − 3·c`.

**P7.** Con la función `f(x) = x² − 1`, calcula f(0), f(2) y f(−2). ¿Por qué f(2) y f(−2) dan lo mismo?

**P8.** Una piedra se suelta desde lo alto de un edificio. Con g = 10, ¿cuánto ha caído a los 2 segundos? ¿Y a los 4? ¿Por qué no es el doble?

**P9.** ¿Desde qué altura hay que soltar una pelota para que tarde exactamente 1 segundo en llegar al suelo? (Usa g = 10.)

**P10.** Comprueba con unidades que la fórmula `a = F / m` da una aceleración, sabiendo que la fuerza se mide en newtons y que 1 newton = 1 kg · m/s².
"""),

md(r"""<details>
<summary>▶ Solución P1</summary>

`10 − 2 × 3²`: primero la potencia (9), después la multiplicación (2 × 9 = 18), después la resta: 10 − 18 = **−8**. Con paréntesis, `(10 − 2) × 3²` = 8 × 9 = **72**. Los paréntesis lo cambian todo.
</details>

<details>
<summary>▶ Solución P2</summary>

```
   4·x − 7 = 13
   4·x = 20          (sumo 7 a los dos lados)
   x = 5             (divido entre 4)
```

Comprobación: 4 × 5 − 7 = 20 − 7 = 13 ✓.
</details>

<details>
<summary>▶ Solución P3</summary>

A la m le estorban el ½ y el v² (que la multiplican). Multiplico por 2 los dos lados: `2·E = m · v²`. Divido entre v² los dos lados: **`m = 2·E / v²`**.
</details>

<details>
<summary>▶ Solución P4</summary>

v = d / t = 3 / 6 = **0,5 m/s**. Para 10 m: t = d / v = 10 / 0,5 = **20 segundos**.
</details>

<details>
<summary>▶ Solución P5</summary>

`(m · g · h) / (m · g)` = **h** (se tachan la m y la g, que multiplican arriba y abajo). `(m + g) / m` **no** se puede simplificar tachando la m, porque arriba está **sumando**. Lo más que se puede hacer es partirla: `m/m + g/m = 1 + g/m`.
</details>

<details>
<summary>▶ Solución P6</summary>

**`3·(a + b − c)`**. (Comprueba con la distributiva: 3·a + 3·b − 3·c ✓.)
</details>

<details>
<summary>▶ Solución P7</summary>

f(0) = 0 − 1 = **−1**; f(2) = 4 − 1 = **3**; f(−2) = (−2)² − 1 = 4 − 1 = **3**. Dan lo mismo porque al elevar al cuadrado desaparece el signo: (−2)² = (+2)² = 4 (menos por menos es más, NB03b).
</details>

<details>
<summary>▶ Solución P8</summary>

A los 2 s: d = ½ · 10 · 2² = 5 · 4 = **20 m**. A los 4 s: d = ½ · 10 · 4² = 5 · 16 = **80 m**. No es el doble, sino **cuatro veces** más, porque el tiempo va al cuadrado: el doble de tiempo da 2² = 4 veces más distancia.
</details>

<details>
<summary>▶ Solución P9</summary>

La distancia caída en 1 s es d = ½ · 10 · 1² = **5 metros**. Hay que soltarla desde 5 m de altura.
</details>

<details>
<summary>▶ Solución P10</summary>

`F / m` → (kg · m/s²) / kg = **m/s²** (se tachan los kilos). Metros por segundo al cuadrado: justo la unidad de una aceleración ✓.
</details>
"""),

md(r"""## 11 · 🛠 Práctica en MuJoCo: ¿acierta tu fórmula?

En el apartado 7 **dedujiste** con letras y razonamiento la fórmula de la caída libre,
`h = 2 − ½·g·t²`. Una fórmula es una **predicción**: dice qué va a pasar antes de que pase. Y una
predicción se **comprueba**. Hoy vas a poner tu fórmula a competir con MuJoCo:

1. una **tabla** con las alturas de la fórmula y las de MuJoCo, lado a lado;
2. su **gráfica**, para ver la parábola;
3. y lo más bonito: **despejar** el tiempo de la fórmula para **predecir** cuándo toca el suelo la
   pelota... antes de simularla.

Es lo que hace un profesional con cualquier simulador nuevo: comprobarlo contra una fórmula que sabe
que es cierta. El código ya está escrito: ejecutas, miras y cambias algún número.
"""),

md(r"""### Paso 1 · La pelota del NB02, con pasos finos

Es el mismo plano de la práctica del NB02 (un suelo y una pelota de 5 cm de radio), con g = 10 y
pasos de **una milésima** de segundo. La receta `soltar(altura, g)` carga el mundo, le pone la
gravedad que digas y coloca la pelota a la altura que digas. Dos **letras** (huecos con nombre,
apartado 1) que podrás cambiar.
"""),

code(r"""import mujoco
import numpy as np
import matplotlib.pyplot as plt
import taller

PELOTA = '''
<mujoco>
  <option gravity="0 0 -10" timestep="0.001"/>
  <worldbody>
    <light pos="0 0 10"/>
    <geom type="plane" size="5 5 0.1" rgba=".8 .9 .8 1"/>
    <body name="pelota" pos="0 0 2">
      <freejoint/>
      <geom type="sphere" size="0.05" rgba="1 .3 .1 1"/>
    </body>
  </worldbody>
</mujoco>
'''

def soltar(altura, g):
    modelo, datos = taller.cargar(PELOTA)
    modelo.opt.gravity[2] = -g          # la gravedad tira hacia abajo con g
    datos.qpos[2] = altura              # la pelota empieza a esta altura
    return modelo, datos

g = 10"""),

md(r"""### Paso 2 · La tabla: fórmula contra MuJoCo

La celda suelta la pelota desde 2 metros y, cada décima de segundo, escribe tres cosas: la altura
que da **MuJoCo**, la que da **tu fórmula** (sustituyendo t en `2 − ½·g·t²`, apartado 1) y la
**diferencia** entre las dos, en milímetros.
"""),

code(r"""modelo, datos = soltar(2, g)

print("tiempo   MuJoCo    fórmula   diferencia")
for decima in range(1, 7):
    while datos.time < decima / 10 - 1e-9:       # avanza pasitos hasta la siguiente décima
        mujoco.mj_step(modelo, datos)
    t = datos.time
    formula = 2 - 0.5 * g * t**2
    print(f"{t:5.1f}   {datos.qpos[2]:6.4f}   {formula:6.4f}   {(formula - datos.qpos[2]) * 1000:5.1f} mm")"""),

md(r"""Fíjate en tres cosas:

1. **Coinciden** casi perfectamente: la mayor diferencia es de **3 milímetros**. MuJoCo no conoce tu
   fórmula (solo da pasitos, NB02), y aun así llega al mismo sitio. A los 0,5 s, el famoso **0,75**
   (MuJoCo: 0,7475). Tu deducción del apartado 7 era correcta.
2. La pequeña diferencia **crece** con el tiempo, y siempre en el mismo sentido: MuJoCo va un pelín
   **por debajo**. Es el error del apartado 7 ("¿por qué falló la tabla del NB02?"): en cada pasito
   usa la velocidad del **final** del pasito, y cuenta un poquito de más. Con pasos de una milésima,
   el error es diminuto; con los de 0,1 s del NB02, era de 25 cm.
3. **No es proporcional** al tiempo: en la primera décima cae 5 cm (de 2 a 1,95); en la sexta, de
   0,5 s a 0,6 s, cae **55 cm** (de 0,75 a 0,20). Cada vez más deprisa: es la parábola.
"""),

md(r"""### Paso 3 · La gráfica: una parábola

Ahora lo mismo en dibujo (apartado 6): tiempo en horizontal, altura en vertical. Los **puntos** son
MuJoCo (uno cada 20 milésimas) y la **línea**, tu fórmula. Simulamos hasta los 0,6 s, justo antes de
que toque el suelo.
"""),

code(r"""modelo, datos = soltar(2, g)
tiempos, alturas = [], []
while datos.time < 0.6:
    mujoco.mj_step(modelo, datos)
    if round(datos.time * 1000) % 20 == 0:          # apunta un punto cada 20 milésimas
        tiempos.append(datos.time)
        alturas.append(datos.qpos[2])

t = np.linspace(0, 0.6, 100)
plt.figure(figsize=(6, 3.5))
plt.plot(t, 2 - 0.5 * g * t**2, label="tu fórmula: 2 − ½·g·t²")
plt.plot(tiempos, alturas, "o", markersize=4, label="MuJoCo")
plt.xlabel("tiempo (s)")
plt.ylabel("altura (m)")
plt.legend()
plt.grid(alpha=0.3)
plt.show()"""),

md(r"""Los puntos caen **encima** de la línea. Y la forma es la mitad de una U puesta del revés: la
parábola de `x²` del apartado 6, pero **restada** de 2 (por eso baja en vez de subir). Arriba, casi
plana (al principio va despacio); abajo, cada vez más empinada (cada vez más deprisa).
"""),

md(r"""### Paso 4 · Despejar para predecir: ¿cuándo toca el suelo?

Ahora la pregunta al revés: no "¿dónde está a los t segundos?", sino "**¿cuántos segundos tarda en
llegar al suelo?**". Hay que **despejar t** (apartado 4).

Un detalle antes: la pelota toca el suelo cuando su **centro** está a 5 cm (su radio), no a 0. Así
que, desde 2 m, tiene que caer **d = 2 − 0,05 = 1,95 m**. Partiendo de `d = ½·g·t²`, quitamos lo que
estorba a la t con la balanza (apartado 3):

```
   d = ½ · g · t²
   2·d = g · t²            (multiplico por 2 los dos lados: se va el ½)
   2·d / g = t²            (divido entre g los dos lados)
   t = √(2·d / g)          (raíz cuadrada de los dos lados: se va el ²)
```

Primero **predecimos** con la fórmula; después simulamos hasta que el centro baje de 5 cm y miramos
el reloj de MuJoCo.
"""),

code(r"""altura = 2
d = altura - 0.05                                  # lo que tiene que caer el centro
prediccion = np.sqrt(2 * d / g)
print(f"Tu fórmula predice que toca el suelo a los {prediccion:.4f} s")

modelo, datos = soltar(altura, g)
while datos.qpos[2] > 0.05:                        # simula hasta que el centro baja de 5 cm
    mujoco.mj_step(modelo, datos)
print(f"MuJoCo dice que toca el suelo a los        {datos.time:.4f} s")"""),

md(r"""**0,6245 s** predichos, **0,6250 s** medidos: medio milisegundo de diferencia, que es justo el
tamaño del pasito (MuJoCo solo mira el reloj cada milésima, así que no puede "ver" el instante exacto
entre dos pasitos). Has **predicho el futuro** con una fórmula despejada por ti. Eso es, literalmente,
para lo que sirve el álgebra.
"""),

md(r"""### Paso 5 · Cuatro veces más alto, ¿cuatro veces más tiempo?

Una pregunta trampa: si sueltas una pelota desde **8 metros** (cuatro veces más alto), ¿tarda cuatro
veces más en llegar? Mira la fórmula despejada antes de contestar: `t = √(2·d / g)`. La altura está
**dentro de una raíz**. Cuatro veces más altura → la raíz de 4 = **2** veces más tiempo.

El vídeo suelta **dos** pelotas a la vez: la naranja desde 2 m y la azul desde 8 m (cada una en su
"carril"). Para que se vean bien desde lejos, son más gordas (25 cm de radio), y están colocadas de
forma que su **parte de abajo** empiece a 2 m y a 8 m del suelo: así cada una tiene que caer
exactamente 2 y 8 metros, y la fórmula queda limpia: `t = √(2·d / g)` con d = 2 y d = 8. Debajo del
vídeo, la predicción y el tiempo medido en MuJoCo para cada una.
"""),

code(r"""DOS_PELOTAS = '''
<mujoco>
  <option gravity="0 0 -10" timestep="0.001"/>
  <worldbody>
    <light pos="0 -4 12" dir="0 0.3 -1"/>
    <geom type="plane" size="3 3 0.1" rgba=".8 .9 .8 1"/>
    <body pos="-0.7 0 2.25"><freejoint/><geom type="sphere" size="0.25" rgba="1 .3 .1 1"/></body>
    <body pos="0.7 0 8.25"><freejoint/><geom type="sphere" size="0.25" rgba=".2 .5 1 1"/></body>
  </worldbody>
</mujoco>
'''
modelo, datos = taller.cargar(DOS_PELOTAS)
taller.video(modelo, datos, segundos=1.6, nombre="nb04b_dos_pelotas", seguir=False, distancia=14);

for d in [2, 8]:
    print(f"Caer {d} m: tu fórmula predice {np.sqrt(2 * d / g):.3f} s", end="   ")
    modelo, datos = taller.cargar(DOS_PELOTAS)
    numero = 2 if d == 2 else 9                    # dónde está la altura de esa pelota en qpos
    while datos.qpos[numero] > 0.25:               # hasta que su centro baja a 25 cm
        mujoco.mj_step(modelo, datos)
    print(f"MuJoCo mide {datos.time:.3f} s")"""),

md(r"""La de 2 m llega a los **0,63 s**; la de 8 m, a los **1,26 s**: el **doble**, no el cuádruple. (Es
la misma idea del apartado 7, leída al revés: allí, el doble de tiempo daba cuatro veces más
distancia; aquí, cuatro veces más distancia pide solo el doble de tiempo.) Por eso un salto desde un
trampolín alto no dura tanto como uno esperaría.
"""),

md(r"""### Tus retos

**Reto 1 · En la Luna.** En la celda del Paso 1, cambia `g = 10` por `g = 1.62` y vuelve a ejecutar
el Paso 1 y el Paso 2. ¿Qué altura da MuJoCo a los 0,5 s? Compárala con la cuenta del apartado 7.

**Reto 2 · Predice en la Luna.** Con `g = 1.62`, ejecuta el Paso 4. Antes, calcula tú con la fórmula
despejada cuánto tardará. ¿Acierta MuJoCo?

**Reto 3 · Un segundo exacto.** ¿Desde qué altura hay que soltar la pelota (con g = 10) para que tarde
**exactamente 1 segundo** en tocar el suelo? Despeja con lápiz y papel (¡no olvides el radio!), pon esa
altura en el Paso 4 en lugar del `2` y compruébalo.

**Reto 4 (para pensar).** En la tabla del Paso 2, ¿por qué crees que la diferencia entre MuJoCo y la
fórmula se hace más pequeña si cambias `timestep="0.001"` por `timestep="0.0001"` en el plano?

<details>
<summary>▶ Solución Reto 1</summary>

MuJoCo da **1,797 m** a los 0,5 s; la fórmula (apartado 7), 2 − ½·1,62·0,25 = **1,7975 ≈ 1,80 m**. Apenas
ha caído 20 cm: en la Luna todo cae a cámara lenta. (Acuérdate de volver a poner `g = 10` después.)
</details>

<details>
<summary>▶ Solución Reto 2</summary>

Fórmula: t = √(2 · 1,95 / 1,62) = √2,407 ≈ **1,5516 s**. MuJoCo: **1,5520 s**. Otra vez, medio milisegundo
de diferencia. En la Luna, la misma caída que en la Tierra dura 0,62 s, tarda dos veces y media más.
</details>

<details>
<summary>▶ Solución Reto 3</summary>

Con t = 1 y g = 10: d = ½ · 10 · 1² = **5 m**. Pero eso es lo que cae el **centro**, que se para a 5 cm del
suelo: la altura de partida es 5 + 0,05 = **5,05 m**. Con `altura = 5.05`, la fórmula predice **1,0000 s** y
MuJoCo dice **1,0000 s**. (Es la pregunta P9 de los ejercicios, ahora con el radio de la pelota.)
</details>

<details>
<summary>▶ Solución Reto 4</summary>

Porque el error viene de los **pasitos** (Paso 2, punto 2): en cada uno, MuJoCo usa la velocidad del
final del pasito para todo el pasito. Cuanto más corto es el pasito, menos cambia la velocidad dentro
de él y menos se equivoca. Con pasos diez veces más pequeños, el error es unas diez veces más pequeño
(a los 0,5 s, 0,25 mm en vez de 2,5 mm). Es el dilema "exacto contra rápido" del NB02.
</details>

### Qué has aprendido de MuJoCo hoy

- Una **fórmula** sirve para **verificar un simulador**: si MuJoCo y `h = 2 − ½·g·t²` coinciden, te
  fías de los dos. Es una costumbre profesional (lo harás mucho más en serio en el NB27).
- **`modelo.opt.gravity[2]`** y **`datos.qpos[2]`** se pueden cambiar antes de simular: así se monta
  un experimento con los números que quieras.
- Simular **hasta que pase algo** (`while ... mj_step`) y leer el reloj **`datos.time`**: medir
  cuándo ocurre un suceso.
- El error de MuJoCo con la caída libre depende del **paso de tiempo**, y con una milésima es de
  milímetros.
- Despejar una fórmula te deja **predecir** lo que hará la simulación antes de ejecutarla.

En la práctica del NB05 escribirás tu **primera línea de código** de verdad para MuJoCo: un `print`
con los datos del humanoide.
"""),

md(r"""## 12 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Con esta lección, y con el NB03b, tienes las herramientas de matemáticas que necesita la primera parte del curso. En el **NB05** empieza la **Parte 1**: por fin tocamos el ordenador. Y verás que mucho de lo de hoy (las variables, el orden de las operaciones, las funciones con paréntesis) reaparece casi igual en el código.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB04b_letras_y_ecuaciones.ipynb")
    build(out, cells, title="NB04b · Letras y ecuaciones")
