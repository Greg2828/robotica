"""Construye NB15b · Funciones a fondo: mover, exponencial y logaritmo (Parte 2 · lección intermedia).

Añadida tras la auditoría de 2026-10-04: el curso usaba desplazamientos de
funciones (ReLU(x + 4/3) en el NB19), la exponencial y el número e (NB17, NB28,
NB44), la "constante de tiempo" (NB48, NB50), el logaritmo y sus reglas
(NB28-NB33) y las escalas logarítmicas (NB18) sin haberlos enseñado.
Transformaciones de una función (sumar, desplazar con el signo al revés,
estirar, reflejar), comprobadas con dibujos; potencias con exponente real;
crecimiento y decrecimiento exponencial; el número e (interés compuesto);
e^x y sus reglas; la campana e^(-x²); decaimiento exponencial y constante de
tiempo (el 63 %); el logaritmo como pregunta inversa (log10, log2 y bits, ln),
sus reglas comprobadas con números, log(0) y negativos; escalas logarítmicas.
Práctica en MuJoCo: damping = decaimiento exponencial. Disco en un raíl
(m=1, damping 0,5 → τ=2 s): a t=τ queda 36,9 % (e^−1 = 36,8 %), posición →
4·(1−e^(−t/2)); τ medida con la pendiente de ln(v) = 2,005 s. Péndulo con
damping (vídeo): cada pico 62,7 % del anterior, τ de los balanceos ≈ 4,28 s.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB15b · Funciones a fondo: moverlas, la exponencial y el logaritmo

**Parte 2 · Las matemáticas del aprendizaje — Lección intermedia (entre el NB15 y el NB16)**

> En el NB04b conociste las **funciones**: máquinas que convierten una entrada en una salida, como `f(x) = 2·x + 1`. En la Parte 2 y en las siguientes vas a encontrar funciones que **se mueven** (en el NB19 construiremos curvas desplazando "codos"), y dos funciones muy especiales que aparecen por todas partes en robótica y en aprendizaje automático: la **exponencial** y el **logaritmo**.

Hoy las conocemos a fondo, con NumPy y dibujos (NB15). Tres bloques:

1. **Mover una función**: subirla, desplazarla, estirarla, darle la vuelta. Con una trampa de signo que confunde a todo el mundo.
2. **La exponencial** y el famoso número **e**: el crecimiento que se multiplica, el decaimiento que "se apaga", y la **constante de tiempo** que aparecerá en motores, filtros y contactos.
3. **El logaritmo**: la pregunta inversa ("¿a qué exponente?"), sus reglas mágicas que convierten multiplicaciones en sumas, y las **escalas logarítmicas** de las gráficas.
"""),

code(r"""import numpy as np
import matplotlib.pyplot as plt

def dibujar(xs, curvas, titulo):
    # Dibuja varias curvas (una lista de parejas (ys, etiqueta)) sobre los mismos ejes.
    plt.figure(figsize=(6, 3.5))
    for ys, etiqueta in curvas:
        plt.plot(xs, ys, label=etiqueta)
    plt.axhline(0, color="k", lw=0.5)
    plt.axvline(0, color="k", lw=0.5)
    plt.title(titulo)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()"""),

md(r"""(Una función de ayuda para no repetir las mismas líneas de dibujo en cada celda. Recibe los valores de x, una **lista de tuplas** (NB11b) con los valores de y y su etiqueta, y un título. `plt.axhline` y `plt.axvline` dibujan una línea horizontal y una vertical en el cero, para tener los ejes de referencia.)

## 1 · Mover una función

### La función de partida

Usaremos una función muy sencilla que reaparecerá en el NB19 como pieza básica de las redes neuronales: la **rampa** (su nombre técnico es **ReLU**). Vale **0** para los números negativos y **x** para los positivos: un "codo" en el cero.

```
   rampa(x) = 0   si x < 0
   rampa(x) = x   si x ≥ 0
```

En NumPy se escribe con `np.maximum(0, x)`: el mayor entre 0 y x, elemento a elemento.
"""),

code(r"""def rampa(x):
    return np.maximum(0, x)

xs = np.linspace(-4, 4, 401)            # 401 números repartidos entre -4 y 4
dibujar(xs, [(rampa(xs), "rampa(x)")], "La rampa: un codo en el cero")"""),

md(r"""(`np.linspace(inicio, fin, cuántos)` da números **repartidos por igual** entre el inicio y el fin, ambos incluidos: perfecto para dibujar curvas suaves.)

### Sumar fuera: subir y bajar

**`f(x) + c`** sube la curva entera **c** unidades (o la baja, si c es negativo). Fácil: a cada salida se le suma c.
"""),

code(r"""dibujar(xs, [(rampa(xs), "rampa(x)"), (rampa(xs) + 1, "rampa(x) + 1"), (rampa(xs) - 1, "rampa(x) − 1")],
        "Sumar fuera: sube o baja")"""),

md(r"""### Sumar dentro: desplazar (¡con el signo al revés!)

**`f(x − a)`** desplaza la curva **a unidades hacia la DERECHA**. Y **`f(x + a)`**, hacia la **IZQUIERDA**. Sí: con el signo menos va a la derecha. Es la trampa de signo más famosa de las matemáticas. Mira:
"""),

code(r"""dibujar(xs, [(rampa(xs), "rampa(x)"), (rampa(xs - 2), "rampa(x − 2)"), (rampa(xs + 1), "rampa(x + 1)")],
        "Sumar dentro: desplaza (el signo, al revés)")"""),

md(r"""`rampa(x − 2)` tiene el codo en **x = 2** (a la derecha), y `rampa(x + 1)`, en **x = −1** (a la izquierda). ¿Por qué al revés? Piensa en **dónde está el codo**: la rampa original tiene el codo donde lo de dentro vale **0**. En `rampa(x − 2)`, lo de dentro es `x − 2`, que vale 0 cuando **x = 2**. Así que el codo está en 2. En `rampa(x + 1)`, lo de dentro vale 0 cuando x = −1.

**La regla para no equivocarse nunca: el punto especial se mueve a donde "lo de dentro" vale lo que valía antes.** Si tienes `rampa(x + 4/3)` (lo verás en el NB19), el codo está donde x + 4/3 = 0, es decir, en **x = −4/3**: despeja (NB04b) y sale.

### Multiplicar fuera: estirar en vertical

**`c · f(x)`** estira la curva en vertical (la hace c veces más alta). Con la rampa, cambia su **inclinación**: `3·rampa(x)` sube tres veces más deprisa. Y si c es **negativo**, la curva además se **da la vuelta** de arriba abajo (se refleja en el eje horizontal):
"""),

code(r"""dibujar(xs, [(rampa(xs), "rampa(x)"), (3 * rampa(xs), "3·rampa(x)"), (-rampa(xs), "−rampa(x)")],
        "Multiplicar fuera: estira, y el signo da la vuelta")"""),

md(r"""### Cambiar el signo dentro: reflejar en horizontal

**`f(−x)`** refleja la curva de izquierda a derecha (como en un espejo vertical colocado en el cero). La rampa, que "subía hacia la derecha", pasa a subir hacia la **izquierda**:
"""),

code(r"""dibujar(xs, [(rampa(xs), "rampa(x)"), (rampa(-xs), "rampa(−x)"), (rampa(-xs - 1), "rampa(−x − 1)")],
        "Signo dentro: refleja de izquierda a derecha")"""),

md(r"""`rampa(−x)` vale 0 para los positivos y crece hacia los negativos. Y `rampa(−x − 1)` es eso mismo, con el codo donde lo de dentro vale 0: −x − 1 = 0 → x = **−1**. Combinando estas piezas (desplazar, estirar, reflejar, sumar) se puede fabricar casi cualquier forma: es exactamente lo que hace una red neuronal (NB19).

### Resumen de las transformaciones

| Escribes | La curva... |
|---|---|
| `f(x) + c` | sube c (baja si c < 0) |
| `f(x − a)` | se desplaza a a la **derecha** |
| `f(x + a)` | se desplaza a a la **izquierda** |
| `c · f(x)` | se estira c veces en vertical (y se da la vuelta si c < 0) |
| `f(−x)` | se refleja de izquierda a derecha |

Las de **fuera** (después de calcular f) actúan en **vertical** y "hacen lo que dicen". Las de **dentro** (antes de calcular f) actúan en **horizontal** y "hacen lo contrario de lo que parece".
"""),

md(r"""## 2 · La exponencial

### Potencias con cualquier exponente

En el NB03b viste las potencias con exponentes enteros (2³ = 8), negativos (2⁻¹ = 0,5) y ½ (2^0,5 = √2). En realidad, el exponente puede ser **cualquier** número decimal: 2^1,5, 2^0,3, 2^π... y el resultado cambia **suavemente** entre los valores enteros. Con eso se puede dibujar la **función exponencial** `f(x) = 2ˣ` como una curva continua:
"""),

code(r"""xs = np.linspace(-3, 4, 300)
dibujar(xs, [(2.0 ** xs, "2^x"), (0.5 ** xs, "0,5^x")], "Exponenciales")
print("2^1,5 =", 2 ** 1.5, "| entre 2^1 = 2 y 2^2 = 4, como debe ser")"""),

md(r"""Tres cosas que hay que ver en esta gráfica:

1. **2ˣ crece cada vez más deprisa** (crecimiento exponencial, NB03b): cada vez que x sube 1, el valor se **multiplica por 2**. Por la izquierda se acerca a 0 sin llegar nunca.
2. **Nunca es negativa ni cero**: por pequeño que sea x, 2ˣ es positivo (2⁻¹⁰ = 1/1.024, chiquitito pero positivo). Esta propiedad la usaremos muchísimo (NB32: para que una "anchura" σ sea siempre positiva).
3. **0,5ˣ es la misma curva reflejada**: decrece, porque cada vez que x sube 1, se multiplica por 0,5 (se divide entre 2). Es el **decrecimiento exponencial** (sección 3).

### El número e

De todas las bases posibles para una exponencial (2, 10, 0,5...), hay una que los matemáticos prefieren por encima de todas: el número **e ≈ 2,71828**. Es tan importante como π, y aparece en cuanto algo **crece (o decrece) en proporción a lo que ya hay**.

¿De dónde sale? De una pregunta sobre dinero. Si el banco te da un 100 % de interés al año, tu euro se convierte en 2. Si te lo da en dos mitades (50 % cada seis meses), al final tienes 1,5 × 1,5 = 2,25 (porcentajes encadenados, NB03b). En 12 meses, un doceavo cada mes: (1 + 1/12)¹² ≈ 2,61. ¿Y si lo repartes en trocitos cada vez más pequeños?
"""),

code(r"""for n in [1, 2, 12, 365, 10_000, 1_000_000]:
    print(f"{n:>9} trocitos: (1 + 1/n)^n = {(1 + 1 / n) ** n:.6f}")
print(f"el número e:                     {np.e:.6f}")"""),

md(r"""Cuantos más trocitos, más se acerca a un número concreto, que **no** pasa de ahí: **e = 2,718281828...** (con cifras que nunca terminan, como π). Es el resultado de crecer "de forma continua", sin saltos. Por eso aparece en todo lo que cambia de forma continua: poblaciones, enfriamiento, radiactividad... y en las matemáticas de la probabilidad y del aprendizaje (NB28).

En NumPy, `np.e` es el número e, y **`np.exp(x)`** calcula eˣ (se lee "exponencial de x"). Sus reglas son las de las potencias del NB03b:

- e⁰ = 1.
- eᵃ · eᵇ = eᵃ⁺ᵇ (multiplicar = sumar exponentes).
- e⁻ˣ = 1 / eˣ.
- eˣ siempre es positivo.

### La campana

Una combinación que verás muy pronto (NB17, NB28, NB44): **e elevado a menos un cuadrado**, `e^(−x²)`. Como x² es siempre positivo, −x² es siempre negativo o cero, así que e^(−x²) vale **1** en el centro (x = 0, e⁰ = 1) y cae hacia 0 a los dos lados, cada vez más deprisa. Es la famosa **campana**:
"""),

code(r"""xs = np.linspace(-3, 3, 300)
dibujar(xs, [(np.exp(-xs ** 2), "e^(−x²)"), (np.exp(-(xs - 1) ** 2 / 0.25), "e^(−(x−1)²/0,25)")], "Campanas")"""),

md(r"""La segunda campana está **desplazada** a x = 1 (sección 1: `x − 1` → el centro donde lo de dentro vale 0) y es más **estrecha**, porque dividimos por 0,25 (que es multiplicar por 4: el cuadrado crece 4 veces más deprisa y la campana cae antes). Con dos números se controla dónde está el centro y cuánto de ancha es. En el NB44 usaremos exactamente esta campana para premiar a un robot por ir **cerca** de una velocidad objetivo; y en el NB28 descubrirás que es la forma de la distribución de probabilidad más importante que existe.
"""),

md(r"""## 3 · El decaimiento exponencial y la constante de tiempo

### Algo que se va apagando

Imagina una taza de chocolate caliente que se enfría, o un muelle que deja de vibrar, o el error de un motor que corrige su posición. En muchas cosas de la naturaleza, **la rapidez con que algo cambia es proporcional a lo que le falta**: cuando falta mucho, cambia deprisa; cuando falta poco, despacio. El resultado es una curva que **se va apagando** sin llegar nunca del todo: el **decaimiento exponencial**:

```
   lo que queda  =  e^(−t / τ)
```

La letra **τ** (tau) se llama **constante de tiempo**, y dice **lo rápido** que se apaga: con τ pequeño, rapidísimo; con τ grande, despacio.
"""),

code(r"""t = np.linspace(0, 5, 300)
dibujar(t, [(np.exp(-t / 0.5), "τ = 0,5 s"), (np.exp(-t / 1.0), "τ = 1 s"), (np.exp(-t / 2.0), "τ = 2 s")],
        "Decaimiento exponencial: e^(−t/τ)")"""),

md(r"""### El 63 %

¿Qué significa exactamente "constante de tiempo"? Calculemos cuánto queda cuando ha pasado **un τ**, dos, tres...
"""),

code(r"""for veces in [1, 2, 3, 5]:
    queda = np.exp(-veces)
    print(f"tras {veces} τ: queda un {queda:.1%}  →  ha recorrido el {1 - queda:.1%} del camino")"""),

md(r"""**Tras una constante de tiempo, queda el 37 %: se ha recorrido el 63 % del camino.** Tras tres, queda solo un 5 %; tras cinco, menos del 1 % (en la práctica, "ha terminado").

Esta es la definición que usaremos en todo el curso cuando digamos que algo tiene una "constante de tiempo de 0,02 s": que en 0,02 s recorre el 63 % del camino hacia donde va. La verás:

- en los **filtros** que suavizan las medidas de los sensores (NB41),
- en el **contacto** blando de los pies con el suelo (NB48: `timeconst`),
- en la respuesta de un **motor** que no reacciona al instante (NB50: `timeconst`),
- en el **descuento** del aprendizaje por refuerzo (NB29), que hace que las recompensas lejanas valgan cada vez menos.

### Llegar a un objetivo

Y la versión que **sube**: algo que empieza en 0 y va hacia un objetivo (como un vaso que se llena, o un motor que gira hacia su posición) sigue la curva `1 − e^(−t/τ)`: la misma, dada la vuelta (sección 1: `−f` y luego `+ 1`). En t = τ ha llegado al 63 %.
"""),

md(r"""## 4 · El logaritmo: la pregunta inversa

### ¿A qué exponente hay que elevar?

La potencia contesta: "si elevo 10 al cubo, ¿qué sale?" → 10³ = 1.000. El **logaritmo** contesta la pregunta **contraria**: "¿a qué exponente hay que elevar 10 para que salga 1.000?" → **3**. Se escribe:

```
   log₁₀(1.000) = 3       porque 10³ = 1.000
   log₁₀(100) = 2         log₁₀(10) = 1         log₁₀(1) = 0         log₁₀(0,01) = −2
```

El numerito de abajo es la **base**. Con base 10, el logaritmo de una potencia de 10 es... **su número de ceros** (con signo menos para los decimales). Para números que no son potencias exactas, sale un decimal: log₁₀(500) ≈ 2,7 (entre 2 y 3, porque 500 está entre 100 y 1.000). El logaritmo te dice, en resumen, **de qué orden de magnitud** es un número (NB03b).

### Tres bases que verás

| Base | Se escribe | En NumPy | Para qué |
|---|---|---|---|
| 10 | log₁₀ | `np.log10` | órdenes de magnitud, escalas de gráficas |
| 2 | log₂ | `np.log2` | informática: ¿cuántos bits hacen falta? |
| **e** | **ln** (o simplemente **log**) | **`np.log`** | matemáticas, probabilidad, aprendizaje |

El de base **e** se llama **logaritmo natural**, y es el que usan casi todos los matemáticos y programadores. **¡Cuidado!** En NumPy (y en casi toda la programación), **`np.log` es el natural (base e)**, no el de base 10. Es una confusión muy común.
"""),

code(r"""print("log10(1000) =", np.log10(1000))
print("log2(8)     =", np.log2(8), "  ← con 3 bits se cuentan 2³ = 8 valores (NB05b)")
print("log2(256)   =", np.log2(256), "  ← un byte: 8 bits, 256 valores")
print("ln(e)       =", np.log(np.e))
print("ln(1)       =", np.log(1))"""),

md(r"""Fíjate en el de base 2: `log₂(256) = 8`. ¿Cuántos bits hacen falta para contar 256 valores distintos? Ocho: un byte (NB05b). El logaritmo en base 2 es exactamente "cuántos bits necesito".

### El logaritmo deshace la exponencial

Como el logaritmo es la pregunta inversa de la potencia, **se deshacen** el uno al otro (son operaciones inversas, como sumar y restar, NB04b):

```
   ln(eˣ) = x          e^(ln x) = x
```
"""),

code(r"""x = 3.7
print(np.log(np.exp(x)), np.exp(np.log(x)))"""),

md(r"""### Las reglas: multiplicar se convierte en sumar

Y aquí está el superpoder del logaritmo, la razón por la que se inventó hace 400 años (para que los astrónomos y navegantes pudieran multiplicar números enormes a mano): **convierte las multiplicaciones en sumas**. Viene directamente de la regla de las potencias "multiplicar = sumar exponentes" (NB03b):

| Regla | Ejemplo con base 10 |
|---|---|
| **log(a · b) = log(a) + log(b)** | log(100 · 1.000) = 2 + 3 = 5 ✓ (100.000) |
| **log(a / b) = log(a) − log(b)** | log(1.000 / 10) = 3 − 1 = 2 ✓ (100) |
| **log(aⁿ) = n · log(a)** | log(10⁴) = 4 · log(10) = 4 ✓ |
| **log(1 / a) = −log(a)** | log(0,01) = −log(100) = −2 ✓ |

Funcionan con cualquier base (si la misma en todas partes). Comprobémoslas con el logaritmo natural y números cualesquiera:
"""),

code(r"""a, b = 3.0, 7.5
print("ln(a·b) =", np.log(a * b), "| ln(a) + ln(b) =", np.log(a) + np.log(b))
print("ln(a/b) =", np.log(a / b), "| ln(a) − ln(b) =", np.log(a) - np.log(b))
print("ln(a^4) =", np.log(a ** 4), "| 4·ln(a) =", 4 * np.log(a))"""),

md(r"""¿Por qué importa esto en robótica? En el NB28 verás que la probabilidad de que un robot haga una **secuencia** de acciones es una **multiplicación** de muchísimos números pequeños (0,3 × 0,1 × 0,2 × ...), que enseguida se vuelve tan diminuta que el ordenador la redondea a cero. Con logaritmos, esa multiplicación se convierte en una **suma** de números normales, que el ordenador maneja sin problemas. Es una de las ideas clave del aprendizaje por refuerzo.

### Lo que no tiene logaritmo

Como eˣ siempre es **positivo**, ningún exponente da 0 ni un número negativo. Así que **el logaritmo solo existe para números positivos**:
"""),

code(r"""with np.errstate(divide="ignore", invalid="ignore"):          # (evita avisos en rojo)
    print("ln(0)  =", np.log(0.0))
    print("ln(−1) =", np.log(-1.0))
    print("ln(0,001) =", np.log(0.001), "  ← negativo: los números entre 0 y 1 tienen logaritmo negativo")"""),

md(r"""- `ln(0)` da **`-inf`** (menos infinito): para "acercarse" a 0, el exponente tiene que bajar sin límite.
- `ln(−1)` da **`nan`** ("no es un número"): no existe.
- Los números **entre 0 y 1** tienen logaritmo **negativo** (porque hay que elevar e a un exponente negativo para obtenerlos).

(La línea `with np.errstate(...)` le dice a NumPy que no muestre los avisos que daría con estas cuentas imposibles; es un truco que entenderás en la Parte 3. Lo importante son los resultados.)
"""),

md(r"""## 5 · Escalas logarítmicas

### Cuando los datos abarcan muchos órdenes de magnitud

Imagina que dibujas cómo baja el error de un aprendizaje: empieza en 100, y tras un rato vale 0,001. En una gráfica normal, todo lo que pasa por debajo de 1 queda aplastado contra el suelo, invisible. La solución es una **escala logarítmica**: un eje en el que cada marca vale **10 veces** más que la anterior (0,001 - 0,01 - 0,1 - 1 - 10 - 100), en vez de sumar lo mismo cada vez.
"""),

code(r"""pasos = np.arange(0, 50)
error = 100 * 0.8 ** pasos                     # un error que baja un 20 % en cada paso

fig, ejes = plt.subplots(1, 2, figsize=(10, 3.5))
ejes[0].plot(pasos, error)
ejes[0].set_title("escala normal")
ejes[1].plot(pasos, error)
ejes[1].set_yscale("log")                      # ← el eje vertical, logarítmico
ejes[1].set_title("escala logarítmica")
for eje in ejes:
    eje.set_xlabel("paso")
    eje.grid(alpha=0.3, which="both")
plt.tight_layout()
plt.show()"""),

md(r"""(Aquí dibujamos dos gráficas una al lado de la otra con `plt.subplots(1, 2)`, que da una lista de dos "ejes"; con cada uno se dibuja por separado. Lo verás más en el NB16.)

En la escala normal, a partir del paso 15 no se ve nada: parece que el error ya es cero. En la escala logarítmica se ve todo... ¡y la curva es una **línea recta**! No es casualidad: el error se multiplica por 0,8 en cada paso (una exponencial, sección 2), y el logaritmo convierte "multiplicar por lo mismo en cada paso" en "sumar lo mismo en cada paso": una recta.

**Regla**: si en escala logarítmica ves una recta, lo que tienes es una **exponencial**. Es una forma muy rápida de reconocerlas en los datos. La usarás en el NB18 para las curvas de aprendizaje y en el NB49 (con los dos ejes logarítmicos) para medir lo rápido que mejora un simulador cuando el paso de tiempo se hace más pequeño.
"""),

md(r"""## 6 · Resumen de la lección

1. **Mover funciones**: `f(x) + c` sube; **`f(x − a)` desplaza a la derecha** (el punto especial va donde lo de dentro vale lo de antes); `c · f(x)` estira (y da la vuelta si c < 0); `f(−x)` refleja. Fuera = vertical y directo; dentro = horizontal y al revés.
2. **Exponencial**: el exponente puede ser cualquier número. aˣ crece multiplicando (a > 1) o decrece (a < 1); **siempre es positiva**.
3. **El número e ≈ 2,718**: crecimiento continuo. `np.exp(x)` = eˣ. Reglas de las potencias. **Campana** `e^(−x²)`: centro y anchura se controlan desplazando y dividiendo.
4. **Decaimiento exponencial** `e^(−t/τ)`: la **constante de tiempo τ** es lo que tarda en recorrer el **63 %** del camino (en 3τ, el 95 %). Subida: `1 − e^(−t/τ)`.
5. **Logaritmo** = "¿a qué exponente?". log₁₀ (órdenes de magnitud), log₂ (bits), **ln = log natural, `np.log`**. Deshace la exponencial: ln(eˣ) = x.
6. **Reglas**: log(a·b) = log a + log b; log(a/b) = log a − log b; log(aⁿ) = n·log a. Convierte multiplicaciones en sumas. Solo existe para positivos; ln(0) = −∞; entre 0 y 1, negativo.
7. **Escala logarítmica**: cada marca ×10. Una **recta en escala log = una exponencial**.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Desplazar / reflejar / estirar** | Mover una curva a un lado, darle la vuelta, hacerla más alta. |
| **ReLU (rampa)** | max(0, x): un codo en el cero. |
| **Función exponencial** | aˣ: el exponente es la variable. |
| **Número e** | ≈ 2,71828: la base del crecimiento continuo. |
| **Campana** | e^(−x²) y sus versiones desplazadas y estiradas. |
| **Decaimiento exponencial** | e^(−t/τ): algo que se apaga, cada vez más despacio. |
| **Constante de tiempo (τ)** | Tiempo en recorrer el 63 % del camino. |
| **Logaritmo** | El exponente al que hay que elevar la base para obtener un número. |
| **Logaritmo natural (ln)** | El de base e; `np.log` en NumPy. |
| **Escala logarítmica** | Eje en el que cada marca vale 10 veces la anterior. |
"""),

md(r"""## 7 · Ejercicios

**E1.** ¿Dónde está el codo de `rampa(x − 3)`? ¿Y el de `rampa(2·x + 1)`? (Pista: donde lo de dentro vale 0.) Compruébalo dibujando.

**E2.** Escribe con la rampa una función que valga 0 para x < 1 y que, a partir de x = 1, **baje** con pendiente 2. Dibújala.

**E3.** Calcula, sin el ordenador, 4^0,5, 8^(1/3) y 10^(−2). Comprueba con el ordenador.

**E4.** Un motor tiene una constante de tiempo de 0,05 s. ¿Qué porcentaje del camino a su objetivo ha recorrido a los 0,05 s? ¿Y a los 0,15 s? ¿Cuándo puedes decir que "ha llegado" (menos del 1 % por recorrer)?

**E5.** Sin ordenador: log₁₀(10.000), log₂(32), ln(1), log₁₀(0,001).

**E6.** Usa la regla del producto para calcular log₁₀(2) + log₁₀(5) sin calcular cada logaritmo por separado.

**E7.** La probabilidad de 100 acciones seguidas es 0,1¹⁰⁰. ¿Qué número da el ordenador? Calcula su logaritmo natural con la regla de las potencias (en vez de calcular primero 0,1¹⁰⁰). ¿Por qué es mejor así?

**E8.** Dibuja `2ˣ` y `x²` para x entre 0 y 10 en escala logarítmica vertical. ¿Cuál sale recta? ¿Por qué?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

- `rampa(x − 3)`: x − 3 = 0 → **x = 3**.
- `rampa(2·x + 1)`: 2·x + 1 = 0 → 2·x = −1 → **x = −0,5**. (Además, el 2 dentro hace que la rampa suba el doble de deprisa.)

```python
xs = np.linspace(-4, 4, 401)
dibujar(xs, [(rampa(xs - 3), "rampa(x − 3)"), (rampa(2 * xs + 1), "rampa(2x + 1)")], "E1")
```
</details>

<details>
<summary>▶ Solución E2</summary>

Codo en x = 1: `rampa(x − 1)`. Que **baje** con pendiente 2: multiplicar por **−2**:

```python
dibujar(xs, [(-2 * rampa(xs - 1), "−2·rampa(x − 1)")], "E2")
```

Vale 0 hasta x = 1 y después baja 2 unidades por cada unidad de x.
</details>

<details>
<summary>▶ Solución E3</summary>

- 4^0,5 = √4 = **2**.
- 8^(1/3) = ∛8 = **2** (porque 2 × 2 × 2 = 8; un tercio como exponente es la raíz cúbica).
- 10^(−2) = 1/100 = **0,01**.

```python
print(4 ** 0.5, 8 ** (1 / 3), 10 ** -2)       # 2.0  2.0  0.01
```

(Puede salir `1.9999999999999998` para la raíz cúbica: el ruido de los decimales del NB05b.)
</details>

<details>
<summary>▶ Solución E4</summary>

A los 0,05 s = **1 τ**: ha recorrido el **63 %**. A los 0,15 s = **3 τ**: el **95 %**. "Ha llegado" (menos del 1 % por recorrer) a partir de **5 τ = 0,25 s** (queda e⁻⁵ ≈ 0,7 %).
</details>

<details>
<summary>▶ Solución E5</summary>

- log₁₀(10.000) = **4** (cuatro ceros).
- log₂(32) = **5** (2⁵ = 32).
- ln(1) = **0** (cualquier base elevada a 0 da 1).
- log₁₀(0,001) = **−3** (0,001 = 10⁻³).
</details>

<details>
<summary>▶ Solución E6</summary>

log₁₀(2) + log₁₀(5) = log₁₀(2 · 5) = log₁₀(10) = **1**. Sin calcular ninguno de los dos por separado (que son 0,301 y 0,699).
</details>

<details>
<summary>▶ Solución E7</summary>

```python
print(0.1 ** 100)                    # 1.0000000000000056e-100: aún cabe, pero rozando el límite
print(0.1 ** 400)                    # 0.0: ¡demasiado pequeño! el ordenador lo redondea a cero
print(100 * np.log(0.1))             # ln(0,1^100) = 100 · ln(0,1) = -230.26, un número normalísimo
```

Con la regla `ln(aⁿ) = n · ln(a)`, no hace falta calcular nunca el número diminuto: se calcula directamente su logaritmo, −230,26, que el ordenador maneja sin problema. Con 400 acciones, la probabilidad directa ya sale **0** (el ordenador no puede guardar números tan pequeños), pero su logaritmo, −921, sigue siendo perfectamente manejable. Por eso, en el aprendizaje por refuerzo, siempre se trabaja con **logaritmos de probabilidades** (NB28).
</details>

<details>
<summary>▶ Solución E8</summary>

```python
xs = np.linspace(0.1, 10, 200)
plt.figure(figsize=(6, 3.5))
plt.plot(xs, 2 ** xs, label="2^x")
plt.plot(xs, xs ** 2, label="x²")
plt.yscale("log")
plt.legend()
plt.grid(alpha=0.3, which="both")
plt.show()
```

**2ˣ** sale recta: es una exponencial (se multiplica por 2 cada vez que x sube 1), y en escala logarítmica las exponenciales son rectas. **x²** sale curvada: no se multiplica por lo mismo en cada paso (de 1 a 2 se multiplica por 4; de 9 a 10, solo por 1,23). Y fíjate en que, aunque al principio x² es mayor, la exponencial acaba **adelantándola** muchísimo: el crecimiento exponencial siempre gana a largo plazo.
</details>
"""),

md(r"""## 8 · 🛠 Práctica en MuJoCo: lo que se apaga (y cómo medirlo con un logaritmo)

En el apartado 3 dijimos que, cuando **la rapidez con que algo cambia es proporcional a lo que le queda**, sale un
**decaimiento exponencial**. En el mundo de los robots hay un ejemplo por todas partes: el **rozamiento viscoso**
(en inglés, *damping*), un freno que es más fuerte cuanto más deprisa te mueves, como meter la mano en la miel. MuJoCo lo
tiene incorporado: es el atributo **`damping`** de una articulación.

En esta práctica vas a:

1. Lanzar un disco por un raíl con rozamiento y comprobar que su velocidad se apaga **exactamente** como e^(−t/τ).
2. **Medir** τ con un logaritmo, como hacen los ingenieros con datos reales.
3. Ver un **péndulo** que se va parando, y medir lo rápido que se apagan sus balanceos.
"""),

md(r"""### Paso 1 · Un disco en un raíl con rozamiento

Un plano MJCF pequeño (como la pelota del NB02): un disco de **1 kg** que solo puede deslizarse a lo largo del eje x (una
articulación `slide`, como el carrito del palo de escoba), con **`damping="0.5"`**. Lo de `contype="0" conaffinity="0"` le
dice a MuJoCo que el disco no choque con nada (flota un pelín por encima del suelo, para que el único freno sea el damping).

La física dice que, con este freno, la velocidad se apaga como e^(−t/τ) con una constante de tiempo **τ = masa / damping**
= 1 / 0,5 = **2 segundos**. Vamos a comprobarlo. Lanzamos el disco a **2 m/s** escribiendo su velocidad inicial en
`datos.qvel[0]`:
"""),

code(r"""import mujoco
import taller

DISCO = '''
<mujoco>
  <option timestep="0.01"/>
  <worldbody>
    <light pos="0 0 3"/>
    <geom type="plane" size="6 1 0.1" rgba=".8 .9 .8 1"/>
    <body name="disco" pos="0 0 0.05">
      <joint name="rail" type="slide" axis="1 0 0" damping="0.5"/>
      <geom type="cylinder" size="0.1 0.03" mass="1" rgba=".9 .2 .2 1" contype="0" conaffinity="0"/>
    </body>
  </worldbody>
</mujoco>
'''

modelo, datos = taller.cargar(DISCO)
datos.qvel[0] = 2.0                     # ¡lanzado a 2 m/s!
print("Velocidad inicial:", datos.qvel[0], "m/s")"""),

md(r"""### Paso 2 · Registrar y comparar con la fórmula

Simulamos **10 segundos** (1.000 pasitos de 0,01 s) y registramos tiempo, velocidad y posición en arrays (como en la
práctica del NB15):
"""),

code(r"""tiempos = np.zeros(1000)
velocidades = np.zeros(1000)
posiciones = np.zeros(1000)

for paso in range(1000):
    mujoco.mj_step(modelo, datos)
    tiempos[paso] = datos.time
    velocidades[paso] = datos.qvel[0]
    posiciones[paso] = datos.qpos[0]

tau = 2.0
paso_tau = 199                          # el paso número 199 es el instante t = 2,00 s
print("Tiempo:", round(tiempos[paso_tau], 2), "s")
print("Velocidad que le queda:", round(velocidades[paso_tau] / 2.0 * 100, 1), "% de la inicial")
print("La fórmula e^(−1) dice: ", round(np.exp(-1) * 100, 1), "%")"""),

md(r"""**36,9 % contra 36,8 %**: tras una constante de tiempo le queda el 37 %, como prometía el apartado 3. Dibujemos la
velocidad de MuJoCo encima de la fórmula 2 · e^(−t/2), con la función `dibujar` del principio del notebook:
"""),

code(r"""dibujar(tiempos, [(velocidades, "MuJoCo"), (2.0 * np.exp(-tiempos / tau), "fórmula 2·e^(−t/2)")],
        "Velocidad del disco frenado por el damping")"""),

md(r"""Las dos curvas van **una encima de otra**: no se distinguen. Un simulador de física y una fórmula de una línea cuentan la
misma historia.

¿Y la **posición**? El disco no recorre una distancia infinita: se va parando, y se acerca a un límite. Es la curva "que
sube" del apartado 3, 1 − e^(−t/τ), estirada: el límite es **velocidad inicial × τ = 2 × 2 = 4 metros**:
"""),

code(r"""dibujar(tiempos, [(posiciones, "MuJoCo"), (4 * (1 - np.exp(-tiempos / tau)), "fórmula 4·(1 − e^(−t/2))")],
        "Posición del disco: se acerca a 4 m sin llegar")
print("Posición a los 10 s:", round(posiciones[-1], 3), "m")"""),

md(r"""A los 10 s (5 τ) está en **3,973 m**: le falta menos del 1 % para los 4 m (el "ha terminado" de los 5 τ).
"""),

md(r"""### Paso 3 · Medir τ con un logaritmo

Ahora el truco de verdad. Imagina que **no** conoces la fórmula τ = masa / damping: tienes un robot real, mides su
velocidad, y quieres saber su constante de tiempo. ¿Cómo?

Con el **logaritmo**. Si v = 2 · e^(−t/τ), sus reglas (apartado 4) dicen:

```
   ln(v) = ln(2) + ln(e^(−t/τ)) = ln(2) − t/τ
```

¡Una **recta** (NB04b) con pendiente **−1/τ**! Es la regla del apartado 5: una exponencial, mirada con logaritmo, es una
recta. Dibujemos ln(v):
"""),

code(r"""dibujar(tiempos, [(np.log(velocidades), "ln(velocidad)")], "El logaritmo convierte la exponencial en una recta")"""),

md(r"""Una recta perfecta. Su pendiente (NB04b: lo que sube ÷ lo que avanza) la medimos con dos puntos cualesquiera, por
ejemplo t = 1 s (paso 99) y t = 4 s (paso 399). Y τ es menos uno dividido por la pendiente:
"""),

code(r"""a, b = 99, 399
pendiente_log = (np.log(velocidades[b]) - np.log(velocidades[a])) / (tiempos[b] - tiempos[a])
print("Pendiente de la recta:", round(pendiente_log, 4))
print("τ medida:", round(-1 / pendiente_log, 3), "s   (la física decía 2)")"""),

md(r"""**τ = 2,005 s**, medida solo con los datos. (El 0,005 de diferencia viene de los pasitos de 0,01 s: el simulador hace la
cuenta a saltos, NB02, y se separa un pelín de la curva perfecta.) Esta es exactamente la forma en que un ingeniero mide la
constante de tiempo de un motor o de un sensor: graba datos, toma logaritmos y mide una pendiente.
"""),

md(r"""### Paso 4 · Un péndulo que se va parando

Ahora un péndulo: una bola de 1 kg al final de una varilla de 1 m, colgada de una bisagra con **`damping="0.5"`**. Lo soltamos
desde **0,5 radianes** (unos 29 grados). El poste gris es solo decorado (no choca con nada, por el `contype="0"`).
Primero, a verlo:
"""),

code(r"""PENDULO = '''
<mujoco>
  <option timestep="0.002"/>
  <worldbody>
    <light pos="0 -2 3"/>
    <geom type="plane" size="2 2 0.1" rgba=".8 .9 .8 1"/>
    <geom type="capsule" fromto="0 0.3 0 0 0.3 1.5" size="0.03" rgba=".4 .4 .4 1" contype="0" conaffinity="0"/>
    <geom type="capsule" fromto="0 0.3 1.5 0 0 1.5" size="0.02" rgba=".4 .4 .4 1" contype="0" conaffinity="0"/>
    <body name="pendulo" pos="0 0 1.5">
      <joint name="eje" type="hinge" axis="0 1 0" damping="0.5"/>
      <geom type="capsule" fromto="0 0 0 0 0 -1" size="0.02" mass="0.2"/>
      <geom type="sphere" pos="0 0 -1" size="0.08" mass="1" rgba=".2 .4 .9 1"/>
    </body>
  </worldbody>
</mujoco>
'''

modelo, datos = taller.cargar(PENDULO)
datos.qpos[0] = 0.5
taller.video(modelo, datos, segundos=8, nombre="nb15b_pendulo", seguir=False, distancia=3);"""),

md(r"""Cada balanceo es más corto que el anterior. ¿Cómo de deprisa se apagan? Medimos los **picos**: el ángulo máximo de cada ida
y vuelta. Un pico es el instante en que el péndulo deja de subir y empieza a bajar, es decir, cuando su velocidad pasa de
**positiva** a **negativa** (o cero). Lo detectamos con un `if` que compara la velocidad de ahora con la del pasito anterior:
"""),

code(r"""modelo, datos = taller.cargar(PENDULO)
datos.qpos[0] = 0.5

picos = []
tiempos_picos = []
anterior = datos.qvel[0]
for paso in range(6000):                 # 12 segundos de pasitos de 0,002 s
    mujoco.mj_step(modelo, datos)
    if anterior > 0 and datos.qvel[0] <= 0:
        picos.append(datos.qpos[0])
        tiempos_picos.append(datos.time)
    anterior = datos.qvel[0]

picos = np.array(picos)
tiempos_picos = np.array(tiempos_picos)
print("Tiempos de los picos:", np.round(tiempos_picos, 2))
print("Ángulos de los picos:", np.round(picos, 4))
print("Cada pico / el anterior:", np.round(picos[1:] / picos[:-1], 3))"""),

md(r"""Un pico cada **2 segundos** (lo que tarda una ida y vuelta), y cada uno es **el 63 %** del anterior (de 62,7 % a 62,9 %): siempre la misma
proporción. "Multiplicar por lo mismo en cada paso": ¡una exponencial! Así que sus logaritmos forman una recta, y su pendiente
da la constante de tiempo de los balanceos:
"""),

code(r"""logs = np.log(picos)
pendiente_log = (logs[-1] - logs[0]) / (tiempos_picos[-1] - tiempos_picos[0])
print("τ de los balanceos:", round(-1 / pendiente_log, 2), "s")
dibujar(tiempos_picos, [(logs, "ln(pico)")], "Los picos del péndulo, con logaritmo: una recta")"""),

md(r"""**τ ≈ 4,28 s**: cada 4,28 segundos, los balanceos se quedan en el 37 % de lo que eran. Aquí no te he dado ninguna fórmula
(la de un péndulo es más complicada que la del disco): la has **medido**, como se mide en un laboratorio. En el NB39b verás de
dónde sale.
"""),

md(r"""### Tus retos

**Reto 1 · Más freno.** Cambia el damping del disco a **1,0** (el doble). Según τ = masa / damping, ¿cuál será la nueva τ?
¿Y hasta dónde llegará el disco? Compruébalo midiendo τ con el logaritmo y mirando la posición final.

**Reto 2 · Más pesado.** Vuelve a damping 0,5, pero pon `mass="4"`. ¿Qué τ esperas? ¿Se para antes o después?

**Reto 3 · ¿Cuándo baja de 0,05?** Con la τ del péndulo, calcula con un logaritmo **cuánto tiempo** tardan los balanceos en
bajar de 0,5 a 0,05 radianes (diez veces menos). Pista: e^(−t/τ) = 0,1 → t = τ · ln(10). Compruébalo con la lista de picos.

<details>
<summary>▶ Solución Reto 1</summary>

τ = 1 / 1,0 = **1 s** (la mitad), y el disco llega a 2 × 1 = **2 m**. Cambia `damping="0.5"` por `damping="1.0"` en `DISCO`,
vuelve a ejecutar las celdas del Paso 1, del registro del Paso 2 y de la medida del Paso 3: la pendiente sale ≈ −1 → **τ ≈ 1,01 s**,
y la posición final ≈ **2,0 m**. Doble freno, la mitad de tiempo y de distancia.
</details>

<details>
<summary>▶ Solución Reto 2</summary>

τ = 4 / 0,5 = **8 s**: cuatro veces más. Un disco más pesado tiene más **inercia** (NB02): el mismo freno le cuesta más
pararlo, así que se apaga **más despacio** y llega mucho más lejos (2 × 8 = 16 m... ¡el suelo solo mide 12, pero como no choca
con nada, sigue flotando!). En 10 s solo habrá pasado 1,25 τ: va por 11,4 m y aún le queda un 29 % de la velocidad, así que la recta del
logaritmo da τ = 8,005 igual (la recta existe desde el principio).
</details>

<details>
<summary>▶ Solución Reto 3</summary>

t = 4,28 × ln(10) = 4,28 × 2,303 ≈ **9,85 s**. En la lista de picos: el de 7,97 s vale 0,0772 (aún por encima de 0,05) y el de
**9,96 s** vale **0,0486** (ya por debajo). El logaritmo lo había predicho: entre 9,85 y 9,96. Esta es la pregunta típica que se
contesta con un logaritmo: "¿**cuánto tiempo** tarda en bajar tanto?".
</details>

### Qué has aprendido de MuJoCo hoy

- **`damping`** en una articulación es un freno proporcional a la velocidad (rozamiento viscoso). Produce **decaimiento
  exponencial**; en una articulación que desliza, τ = masa / damping.
- Puedes dar una **velocidad inicial** escribiendo en `datos.qvel` antes de simular.
- Con `contype="0" conaffinity="0"` una forma no choca con nada.
- **Medir con logaritmos**: ln de algo que decae exponencialmente es una recta, y su pendiente es −1/τ. Así se mide la
  constante de tiempo de cualquier cosa simulada (o real).

En la práctica del NB16 verás que la velocidad que te da MuJoCo en `qvel` es, exactamente, la **pendiente** de la posición.
"""),

md(r"""## 9 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **NB16**, las **pendientes**: cuánto sube una curva en cada punto. Es la herramienta con la que un robot sabrá hacia dónde mover sus ruedecillas para mejorar. Y las curvas de hoy (la rampa, la exponencial, la campana) serán perfectas para practicar.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB15b_funciones_exponencial_logaritmo.ipynb")
    build(out, cells, title="NB15b · Funciones a fondo: moverlas, la exponencial y el logaritmo")
