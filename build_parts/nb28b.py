"""Construye NB28b · Las matemáticas del gradiente de la política (Parte 4 · lección intermedia).

Añadida tras la auditoría de 2026-10-04: el NB29 y siguientes daban por buenas
varias piezas ("los matemáticos demuestran...") sin enseñarlas. Aquí se
deducen todas, con lápiz y comprobadas con el ordenador: probabilidad de cosas
seguidas = producto (las monedas del NB14), log de un producto = suma (y por
qué el ordenador lo necesita), derivar la log-probabilidad de la campana paso a
paso (respecto a μ, a σ y a log σ), el truco ∇p = p·∇log p, la regla del
producto contra la de los logaritmos, la física que desaparece, el gradiente de
la recompensa esperada como media (Montecarlo), la línea base que no tuerce la
media, la serie geométrica 1/(1 − γ), y dividir entre n o entre n − 1.
🛠 Práctica en MuJoCo (apartado 11): política campana de una ruedecilla w sobre el
palo de escoba de MuJoCo; ln P de un episodio = suma (el producto ~1e-31);
pendiente de ln P respecto a w sin volver a simular (la física desaparece);
montaña J(w); pendiente en w=1 a lo bruto (~116) vs truco del logaritmo, sin y
con línea base (misma flecha, ~3,5× menos ruido; lotes con la flecha al revés).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB28b · Las matemáticas del gradiente de la política

**Parte 4 · Aprendizaje por refuerzo — Lección intermedia (entre el NB28 y el NB29)**

> En el NB29 vas a programar **REINFORCE**, el primer algoritmo que aprende **solo con recompensas**. Su receta tiene cuatro o cinco piezas matemáticas, y en el NB29 algunas aparecerán con un "los matemáticos demostraron que...". Hoy no te vas a creer nada: vamos a **deducir cada pieza** con lápiz y papel, y a **comprobarla** con el ordenador, como hicimos con las reglas de las pendientes en el NB17b.

No hay nada nuevo de Python. Las herramientas son las que ya tienes: la probabilidad y la campana (NB28), el logaritmo (NB15b), las reglas de las pendientes (NB17b) y NumPy (NB15).

El plan del día:

1. Por qué la probabilidad de **varias cosas seguidas** es una **multiplicación**.
2. Por qué los algoritmos usan **logaritmos** de probabilidades (y qué pasa si no).
3. La **pendiente de la log-probabilidad** de la campana, paso a paso.
4. El **truco del logaritmo**: la pieza que hace posible todo el aprendizaje por refuerzo.
5. Por qué el robot **no necesita conocer su física** para aprender.
6. Por qué restar una **línea base** no estropea nada.
7. De dónde sale el **horizonte** 1/(1 − γ) del descuento.
8. Por qué a veces se divide entre **n − 1** en vez de entre n.
"""),

code(r"""import numpy as np
import matplotlib.pyplot as plt

def pendiente(f, x, h=1e-5):
    # La pendiente numérica centrada del NB16: nuestra "verdad" para comprobar las fórmulas.
    return (f(x + h) - f(x - h)) / (2 * h)"""),

md(r"""(La misma función de ayuda del NB17b: mira la función un poquito a cada lado de x y divide. La usaremos para comprobar cada fórmula que deduzcamos.)

## 1 · Varias cosas seguidas: se multiplica

### Dos monedas

En el NB14 viste, sin demostrarlo, que la probabilidad de sacar **cara y cara** con dos monedas es 0,5 × 0,5 = 0,25. Veamos por qué.

Piensa en **400 parejas de tiradas**. Más o menos, la primera moneda sale cara en **la mitad**: 200 parejas. De esas 200, la segunda moneda sale cara en **la mitad**: 100. Total: 100 de 400, es decir, **0,25**.

Fíjate en lo que hemos hecho: tomar **la mitad de la mitad**. "La mitad de" es multiplicar por 0,5, así que hemos multiplicado dos veces: 0,5 × 0,5. Esa es toda la razón de la regla. Comprobémoslo tirando monedas de mentira:
"""),

code(r"""generador = np.random.default_rng(0)
moneda1 = generador.random(100_000) < 0.5       # True = cara, con probabilidad 0,5
moneda2 = generador.random(100_000) < 0.5
print("Proporción de 'cara y cara':", (moneda1 & moneda2).mean())"""),

md(r"""(`generador.random(n)` da n números al azar entre 0 y 1, NB28; "menor que 0,5" ocurre la mitad de las veces. `&` es el "y" de los arrays de booleanos, NB27; `.mean()` de booleanos es la proporción de `True`, porque True cuenta como 1 y False como 0.)

Sale casi exactamente 0,25. Con un dado y una moneda, la probabilidad de "un 6 **y** cara" sería 1/6 × 1/2 = 1/12: la mitad de la sexta parte.

### Cuando la segunda depende de la primera

Las monedas no se influyen entre sí: son **independientes**. Pero el robot no es así: la segunda acción depende de dónde lo dejó la primera. La regla sigue valiendo con un matiz: la segunda probabilidad es la **de después de que pase la primera**.

Ejemplo: una bolsa con 3 bolas rojas y 2 azules. Sacas una, **no la devuelves**, y sacas otra. ¿Probabilidad de roja y roja?

- La primera es roja: 3 de 5 → **3/5**.
- **Sabiendo** que la primera fue roja, quedan 2 rojas de 4 bolas → **2/4**.
- Las dos: 3/5 × 2/4 = 6/20 = **0,3**.
"""),

code(r"""aciertos = 0
for intento in range(100_000):
    bolsa = ["roja", "roja", "roja", "azul", "azul"]
    generador.shuffle(bolsa)                 # barajar la bolsa
    if bolsa[0] == "roja" and bolsa[1] == "roja":
        aciertos += 1
print("Proporción de 'roja y roja':", aciertos / 100_000)"""),

md(r"""(`shuffle` desordena una lista al azar; mirar las dos primeras es como sacar dos bolas sin devolverlas.)

Un 0,3, como decía la cuenta. A la segunda probabilidad (2/4) se le llama **probabilidad condicionada**: la probabilidad de algo **sabiendo** que ya ha pasado otra cosa.

### Un episodio entero

Ahora, el robot. Un episodio es una cadena de sucesos: el robot ve la situación, **la política sortea** una acción, **la física** decide a qué nueva situación lleva (con su pizca de azar: el viento del palo de escoba), la política sortea otra acción... La probabilidad de **un episodio concreto** es, por la regla de las cosas seguidas:

```
   P(episodio) = P(acción 1) × P(física 1) × P(acción 2) × P(física 2) × ... × P(acción N) × P(física N)
```

donde cada probabilidad está **condicionada** por todo lo anterior. Unas piezas las pone la **política** (las que el robot puede cambiar girando sus ruedecillas) y otras la **física** (que el robot no controla). Guarda esta multiplicación: es el punto de partida de todo lo que viene.
"""),

md(r"""## 2 · El logaritmo: multiplicar sin hundirse

### El problema

Un episodio del palo de escoba tiene 500 pasos. Si cada acción tiene una probabilidad de, digamos, 0,3, la probabilidad del episodio contiene 0,3 × 0,3 × ... quinientas veces (y eso sin contar la física). ¿Cuánto da?
"""),

code(r"""print("0,3 elevado a 500: ", 0.3 ** 500)
print("0,3 elevado a 1000:", 0.3 ** 1000)"""),

md(r"""El primero es un número con más de 260 ceros detrás de la coma. El segundo, el ordenador ya no puede ni escribirlo: lo **redondea a 0**. Los números decimales del ordenador tienen un límite por abajo (más o menos 10⁻³⁰⁸, en la notación científica del NB03b): por debajo, todo es 0. A esto se le llama **subdesbordamiento** (en inglés, *underflow*). Y un 0 es un desastre: todos los episodios largos tendrían "probabilidad 0", y no podríamos compararlos.

### La solución: sumar logaritmos

En el NB15b viste la regla de oro del logaritmo: **convierte multiplicaciones en sumas**:

```
   ln(a × b) = ln(a) + ln(b)
```

Recordemos por qué: ln(a) es "a qué hay que elevar e para obtener a". Si a = e^x y b = e^y, entonces a × b = e^x × e^y = e^(x + y) (al multiplicar potencias de la misma base, los exponentes se suman, NB03b). Así que ln(a × b) = x + y = ln(a) + ln(b).

Y si vale para dos, vale para quinientos: el logaritmo de un producto de muchos factores es la **suma** de sus logaritmos. En vez de un número minúsculo, una suma de números normalitos:
"""),

code(r"""print("ln(0,3) =", np.log(0.3))
print("ln(0,3 elevado a 1000) =", 1000 * np.log(0.3))"""),

md(r"""−1204, un número perfectamente manejable, cuando la probabilidad misma era "0" para el ordenador. A la suma de los logaritmos de las probabilidades se le llama **log-probabilidad** (NB28), y los algoritmos trabajan siempre con ella.

Otra ventaja: la log-probabilidad **ordena igual** que la probabilidad. El logaritmo siempre sube cuando su número sube (NB15b), así que el episodio más probable es también el de mayor log-probabilidad. Nada se pierde al cambiar una por otra.

### Las otras dos reglas que usaremos

Del NB15b, también:

- **ln(a / b) = ln(a) − ln(b)** (dividir es restar).
- **ln(aⁿ) = n · ln(a)** (una potencia baja delante).

Y un valor clave: **ln(1) = 0**.
"""),

md(r"""### Aplicado a un episodio

Con la regla de oro, la multiplicación del apartado 1 se convierte en una suma:

```
   ln P(episodio) = ln P(acción 1) + ln P(acción 2) + ... + ln P(acción N)        ← lo que pone la POLÍTICA
                  + ln P(física 1) + ln P(física 2) + ... + ln P(física N)        ← lo que pone la FÍSICA
```

Las piezas de la política y las de la física han quedado **separadas** en dos montones que se suman. En el apartado 5 veremos por qué esa separación es una suerte enorme.
"""),

md(r"""## 3 · La pendiente de la log-probabilidad de la campana

Nuestra política es la del NB28: la acción se sortea de una **campana de Gauss** con media μ y anchura σ. En el NB28 viste su log-probabilidad:

```
   ln p(a) = − (a − μ)² / (2σ²)  −  ln(σ · √(2π))
```

La pregunta del NB29 será: **¿hacia dónde mover μ para que una acción a concreta sea más probable?** Es decir: ¿cuál es la **pendiente de ln p(a) respecto a μ**? Hoy la deducimos paso a paso, con las reglas del NB17b.

### Paso 1: lo que no depende de μ desaparece

El segundo trozo, − ln(σ·√(2π)), no tiene μ por ninguna parte: para μ es una **constante**, y la pendiente de una constante es **0** (NB17b). Fuera.

### Paso 2: el número que multiplica se queda

Queda − (a − μ)² / (2σ²). Lo podemos escribir como **(−1 / (2σ²)) × (a − μ)²**. El primer factor es un número fijo (no tiene μ), y la regla de "constante por función" (NB17b) dice que se queda delante, tal cual. Solo hay que derivar **(a − μ)²**.

### Paso 3: la regla de la cadena

(a − μ)² es "algo al cuadrado", con "algo" = a − μ. Por la regla de la cadena (los engranajes del NB17b):

- Fuera: la pendiente de "algo²" es **2 × algo** = 2·(a − μ).
- Dentro: la pendiente de a − μ **respecto a μ** es **−1** (a es un número fijo; si μ sube 1, a − μ baja 1). ¡El signo del NB17b, otra vez!
- Total: 2·(a − μ) × (−1) = **−2·(a − μ)**.

### Paso 4: juntar

```
   (−1 / (2σ²)) × (−2·(a − μ))  =  2·(a − μ) / (2σ²)  =  (a − μ) / σ²
```

(Menos por menos, más; el 2 de arriba se va con el 2 de abajo.) Esta es la fórmula que verás en el NB29:

```
   pendiente de ln p(a) respecto a μ  =  (a − μ) / σ²
```

Comprobémosla contra la pendiente numérica, para una acción a = −55 con μ = −60 y σ = 5:
"""),

code(r"""def log_p(a, mu, sigma):
    # La log-probabilidad de la campana (NB28).
    return -(a - mu) ** 2 / (2 * sigma ** 2) - np.log(sigma * np.sqrt(2 * np.pi))

a, mu, sigma = -55.0, -60.0, 5.0
print("numérica:", pendiente(lambda m: log_p(a, m, sigma), mu))
print("fórmula: ", (a - mu) / sigma ** 2)"""),

md(r"""(`lambda m: log_p(a, m, sigma)` es una función de **una sola letra**, m, con a y sigma fijas: la forma de pedirle a `pendiente` la pendiente "respecto a μ", NB17b.)

Iguales: **0,2**. Positiva, porque la acción (−55) está **a la derecha** de la media (−60): subir la media acerca la campana a la acción.

### La pendiente respecto a σ

En el NB32, la política aprenderá **también cuánto explora**: σ será una ruedecilla más. Necesitaremos la pendiente respecto a σ. Ahora los dos trozos dependen de σ:

- **Primer trozo**: − (a − μ)² / (2σ²) = (−(a − μ)²/2) × σ⁻². Lo de delante es fijo; σ⁻² es una potencia, y su pendiente es −2·σ⁻³ (NB17b: "baja el exponente y réstale 1"). Total: (−(a − μ)²/2) × (−2·σ⁻³) = **(a − μ)² / σ³**.
- **Segundo trozo**: − ln(σ·√(2π)) = − ln(σ) − ln(√(2π)) (logaritmo de un producto). La pendiente de ln(σ) es 1/σ (NB17b), y ln(√(2π)) es una constante. Total: **− 1/σ**.

```
   pendiente de ln p(a) respecto a σ  =  (a − μ)² / σ³  −  1/σ
```
"""),

code(r"""print("numérica:", pendiente(lambda s: log_p(a, mu, s), sigma))
print("fórmula: ", (a - mu) ** 2 / sigma ** 3 - 1 / sigma)"""),

md(r"""Las dos dan **0**. ¿Casualidad? No: la acción estaba justo a **una σ** de la media (a − μ = 5 = σ). Mira la fórmula escrita con z = (a − μ)/σ, "a cuántas σ cayó la acción" (NB28):

```
   pendiente respecto a σ  =  (z² − 1) / σ
```

- Si la acción cayó **más lejos de una σ** (z² > 1), la pendiente es **positiva**: si esa acción salió bien, conviene **ensanchar** la campana (explorar más), porque lo bueno estaba lejos.
- Si cayó **más cerca de una σ** (z² < 1), la pendiente es **negativa**: conviene **estrechar** la campana (explorar menos), porque lo bueno estaba cerca del centro.
- Justo a una σ, da igual: pendiente 0.

Todo un razonamiento sensato, metido en una fórmula de una línea.

### Y respecto a log σ

Como verás en el NB32, en la práctica la ruedecilla no es σ sino su logaritmo, **ℓ = ln σ** (así σ = e^ℓ es siempre positiva). Regla de la cadena: la pendiente de σ = e^ℓ respecto a ℓ es e^ℓ = σ (la exponencial es su propia pendiente, NB17b). Así que:

```
   pendiente respecto a ℓ = (pendiente respecto a σ) × σ  =  (z² − 1)/σ × σ  =  z² − 1
```

¡Aún más sencilla! La comprobamos con una acción a dos σ (a = −50):
"""),

code(r"""a2 = -50.0
ell = np.log(sigma)
print("numérica:", pendiente(lambda l: log_p(a2, mu, np.exp(l)), ell))
print("fórmula: ", ((a2 - mu) / sigma) ** 2 - 1)"""),

md(r"""Iguales: **3** (z = 2, z² − 1 = 3). Ya tienes las pendientes de la política respecto a **todo** lo que el robot aprenderá: la media y la anchura.
"""),

md(r"""## 4 · El truco del logaritmo

### La pregunta de verdad

Hasta ahora hemos visto cómo hacer **una acción** más probable. Pero lo que el robot quiere es otra cosa: que su **recompensa media** (el **valor esperado** del NB28) sea lo más alta posible. Llamemos θ (la letra griega *theta*) a las ruedecillas de la política. Para una política con unas pocas acciones posibles (por ejemplo, empujar a la izquierda, no empujar, empujar a la derecha), la recompensa esperada es (NB28):

```
   J(θ) = p₁ · R₁  +  p₂ · R₂  +  p₃ · R₃
```

donde pᵢ es la probabilidad de la acción i (que depende de θ) y Rᵢ la recompensa que da. Queremos **subir por la pendiente de J** (NB17). Las R no dependen de θ (la recompensa de empujar a la derecha es la que es), así que, por la regla de la suma y de "constante por función" (NB17b):

```
   pendiente de J  =  p₁' · R₁  +  p₂' · R₂  +  p₃' · R₃
```

(La comilla significa "pendiente respecto a θ", NB17b.)

### El problema

Fórmula bonita... pero **inútil** en la práctica. En el robot hay infinitas acciones posibles (cualquier número de la campana), y los "pᵢ" de verdad son probabilidades de **episodios enteros**, con la física metida dentro, que no conocemos. No podemos recorrerlos todos.

Lo que **sí** podemos hacer es **jugar**: sortear episodios con la política y medir. Un promedio de jugadas es una **media de Montecarlo** (NB28): se acerca a un valor esperado, es decir, a una suma de la forma **p₁·(algo₁) + p₂·(algo₂) + ...**, con las **probabilidades** delante. Pero en la pendiente de J delante hay **pendientes de probabilidades**, p', no probabilidades. ¿Cómo conseguir una p delante?

### El truco

En el NB17b viste que la pendiente de ln(f) es **f' / f**. Aplícalo a una probabilidad p:

```
   (ln p)'  =  p' / p          →  multiplicando por p a los dos lados:       p'  =  p · (ln p)'
```

¡Ahí está! Una pendiente de probabilidad es **la probabilidad por la pendiente de su logaritmo**. Comprobémoslo con la campana (pendiente respecto a μ):
"""),

code(r"""def p(a, mu, sigma):
    # La campana del NB28 (la exponencial de la log-probabilidad).
    return np.exp(log_p(a, mu, sigma))

izquierda = pendiente(lambda m: p(a, m, sigma), mu)                 # p'
derecha = p(a, mu, sigma) * (a - mu) / sigma ** 2                   # p · (ln p)'
print(izquierda, "=", derecha)"""),

md(r"""Iguales. Metemos el truco en la pendiente de J:

```
   pendiente de J  =  p₁ · (ln p₁)' · R₁  +  p₂ · (ln p₂)' · R₂  +  p₃ · (ln p₃)' · R₃
```

**Ahora sí** hay una probabilidad delante de cada término: es el **valor esperado** de "(ln p)' × R". Y un valor esperado se estima **jugando y promediando**:

```
   pendiente de J  ≈  media, sobre muchas jugadas, de  [ R × (pendiente de ln p de la acción jugada) ]
```

Esta frase es **el teorema del gradiente de la política** (en inglés, *policy gradient theorem*), y es la base de REINFORCE, del actor-crítico y de PPO (NB29 a NB33). Juega, y en cada jugada pon la recompensa por la pendiente de la log-probabilidad de lo que hiciste. Promedia. Esa es la flecha cuesta arriba.

### Comprobación completa

Un caso donde conocemos la respuesta exacta. Política: campana con media μ = 0 y σ = 1. Recompensa: **R(a) = − (a − 3)²** (lo mejor es a = 3; cuanto más lejos, peor). Con algo de álgebra se puede calcular (ejercicio E5) que la recompensa esperada es J = − (μ − 3)² − σ², y su pendiente respecto a μ es **− 2·(μ − 3) = 6**: la flecha dice "sube la media", hacia el 3.

¿Lo descubre el truco, **sin saber nada de esa fórmula**, solo jugando?
"""),

code(r"""generador = np.random.default_rng(1)
mu, sigma = 0.0, 1.0
acciones = mu + sigma * generador.standard_normal(100_000)    # 100.000 jugadas de la política
R = -(acciones - 3) ** 2                                       # la recompensa de cada una
pendiente_log = (acciones - mu) / sigma ** 2                   # la pendiente de ln p de cada una (apartado 3)

print("Recompensa media (exacta: -10):", R.mean())
print("Estimación de la pendiente (exacta: 6):", (R * pendiente_log).mean())"""),

md(r"""Las dos casan con la teoría, salvo un pelín de ruido de Montecarlo. El truco ha encontrado la dirección de mejora **sin conocer la fórmula de la recompensa**: solo con jugadas, recompensas, y la pendiente de la propia política (que sí conocemos, porque la política la hemos hecho nosotros).

**Por qué esto es tan importante**: en el NB17, para medir la pendiente, movíamos cada ruedecilla un poquito y volvíamos a evaluar: 2 evaluaciones **por ruedecilla**. Con un millón de ruedecillas, dos millones de evaluaciones por paso de aprendizaje. Con el truco, un único lote de jugadas da la pendiente respecto a **todas** las ruedecillas a la vez.
"""),

md(r"""## 5 · La física desaparece

Vuelve a la suma del apartado 2, la log-probabilidad de un episodio:

```
   ln P(episodio) = [ ln P(acción 1) + ... + ln P(acción N) ]  +  [ ln P(física 1) + ... + ln P(física N) ]
```

Para usar el truco con episodios enteros, necesitamos la **pendiente de ln P(episodio) respecto a las ruedecillas** θ. La pendiente de una suma es la suma de las pendientes (NB17b). Y aquí viene la suerte: las piezas de la física **no dependen de θ** (la gravedad y el viento no saben nada de las ruedecillas del robot). Para θ son **constantes**, y su pendiente es **0**. Todo el segundo montón desaparece:

```
   pendiente de ln P(episodio)  =  pendiente de ln P(acción 1)  +  ...  +  pendiente de ln P(acción N)
```

Solo quedan las pendientes de la **política**, que conocemos exactamente (apartado 3). **El robot no necesita saber cómo funciona su física para aprender.** A los métodos que aprenden así se les llama **sin modelo** (en inglés, *model-free*): no necesitan un modelo matemático del mundo, solo poder jugar en él. Por eso funcionan con un palo de escoba, con un Hopper, o con un humanoide de verdad.

### La regla del producto llega a lo mismo

Sin logaritmos, la pendiente de un producto se calcula con la **regla del producto** (el rectángulo del NB17b): (f·g)' = f'·g + f·g'. Para un episodio de solo dos acciones, P = p₁ · p₂ (y las de la física, que son constantes y dejamos fuera):

```
   P'  =  p₁' · p₂  +  p₁ · p₂'
```

Si dividimos entre P = p₁·p₂:

```
   P' / P  =  p₁'/p₁  +  p₂'/p₂        es decir:      (ln P)'  =  (ln p₁)' + (ln p₂)'
```

¡Lo mismo que con los logaritmos! Dos caminos, el mismo resultado. Comprobémoslo con dos acciones de la misma campana:
"""),

code(r"""a1, a2 = -55.0, -63.0
mu, sigma = -60.0, 5.0

P = lambda m: p(a1, m, sigma) * p(a2, m, sigma)                # probabilidad de las dos seguidas
print("pendiente de ln P (numérica):", pendiente(lambda m: np.log(P(m)), mu))
print("suma de las de cada acción:  ", (a1 - mu) / sigma ** 2 + (a2 - mu) / sigma ** 2)"""),

md(r"""Iguales: 0,2 + (−0,12) = **0,08**. Con quinientas acciones, la regla del producto sería un monstruo de quinientos términos (cada uno con 499 factores); con logaritmos, una suma de quinientas pendientes sencillas. Por eso se usan logaritmos.
"""),

md(r"""## 6 · La línea base no tuerce la flecha

En el NB29 descubrirás que la estimación del apartado 4 es **muy ruidosa**, y que la cura es restar una **línea base** b (la recompensa "normal") a las recompensas:

```
   pendiente de J  ≈  media de  [ (R − b) × (pendiente de ln p) ]
```

¿No estamos haciendo trampa? Si cambiamos las recompensas, ¿no cambiará la dirección? Demostremos que **no**, en promedio.

### Paso 1: la media de las pendientes de ln p es 0

Calcula el valor esperado de la pendiente de ln p, para una política con tres acciones:

```
   p₁ · (ln p₁)'  +  p₂ · (ln p₂)'  +  p₃ · (ln p₃)'
     =  p₁'  +  p₂'  +  p₃'                       (el truco, al revés: p · (ln p)' = p')
     =  (p₁ + p₂ + p₃)'                            (la suma de pendientes es la pendiente de la suma)
     =  (1)'                                       (¡las probabilidades de todo lo posible suman 1!, NB28)
     =  0                                          (pendiente de una constante)
```

Cuatro líneas, y cada una es una regla que ya conoces. La idea: si haces más probable una acción, **otra tiene que hacerse menos probable**, porque el total siempre es 1. Las subidas y las bajadas se compensan exactamente.

### Paso 2: la línea base se va

```
   media de [ (R − b) × (ln p)' ]  =  media de [ R × (ln p)' ]  −  b × media de [ (ln p)' ]
                                   =  media de [ R × (ln p)' ]  −  b × 0
```

La línea base **no cambia la flecha en promedio**: se dice que **no introduce sesgo** (*sesgo* = una desviación sistemática, siempre hacia el mismo lado). Comprobemos el paso 1 con jugadas de la campana:
"""),

code(r"""print("Media de la pendiente de ln p (debería ser 0):", pendiente_log.mean())"""),

md(r"""Prácticamente 0. (`pendiente_log` son las pendientes de las 100.000 jugadas del apartado 4.)

### Entonces, ¿para qué sirve?

En promedio no cambia nada... pero **sí cambia el ruido**. Hagamos el experimento del apartado 4 muchas veces, con pocas jugadas cada vez (como en un entrenamiento real), con y sin línea base. Para exagerar el efecto, le sumamos **100** a todas las recompensas: un "premio por estar vivo" que no cambia cuál es la mejor acción.
"""),

code(r"""def estimar(con_linea_base, n_jugadas=50, repeticiones=2000):
    estimaciones = []
    for i in range(repeticiones):
        acc = mu + sigma * generador.standard_normal(n_jugadas)
        R = 100 - (acc - 3) ** 2                               # misma recompensa, +100
        if con_linea_base:
            R = R - R.mean()                                   # restar "lo normal"
        estimaciones.append((R * (acc - mu) / sigma ** 2).mean())
    return np.array(estimaciones)

mu, sigma = 0.0, 1.0
for nombre, est in [("Sin línea base", estimar(False)), ("Con línea base", estimar(True))]:
    print(f"{nombre}: media {est.mean():5.2f} | desviación {est.std():5.2f} | "
          f"flecha al revés: {(est < 0).mean():.1%}")"""),

md(r"""Las dos estimaciones apuntan, en promedio, al mismo sitio (más o menos 6, la pendiente de verdad). Pero **sin línea base**, cada estimación se dispersa **diez veces** más: con 50 jugadas, casi **un tercio** de las veces la flecha apunta **al revés** (el robot aprendería a empeorar). Con línea base, prácticamente nunca. ¿Por qué? Sin línea base, todas las recompensas rondan +90: **todas** las acciones "votan" con fuerza por hacerse más probables, y los votos se cancelan solo en promedio, a base de suerte. Con línea base, las acciones mejores de lo normal votan "sí" y las peores, "no": la información está en la **diferencia**, no en el montón común.

(¿Y por qué 5,87 y no 6 clavado? Porque la media del lote incluye la recompensa de **la propia** jugada, y esa parte sí depende de su acción. El efecto es encoger la flecha un factor (n − 1)/n = 49/50: 6 × 0,98 = 5,88. Un encogimiento minúsculo, que ni cambia la dirección; volverás a ver ese (n − 1)/n en el apartado 8.)

(Otro detalle fino: la línea base puede depender de la **situación** del robot, pero **no** de la acción que hizo. Si dependiera de la acción, el paso 2 ya no valdría. Un ejemplo extremo: si b fuera la propia recompensa R de cada acción, R − b sería siempre 0 y la flecha sería 0: ¡nunca aprendería nada! Restar la media de un lote entero de jugadas, como hacemos aquí y en el NB29, es seguro en la práctica.)

### Las recompensas de antes no cuentan

Con la misma idea se justifica otra pieza del NB29: para juzgar la acción del paso t, solo se usan las recompensas **desde t** en adelante. Las recompensas de **antes** de t ya habían ocurrido cuando se sorteó la acción: no dependen de ella, así que, para esa acción, son como una línea base. Su contribución, en promedio, es 0, y quitarlas solo quita ruido.
"""),

md(r"""## 7 · El horizonte: la serie geométrica

En el NB29 y el NB30, las recompensas futuras se **descuentan**: la de dentro de k pasos se multiplica por γᵏ (con γ = 0,99, por ejemplo). En el NB30 verás que γ fija un **horizonte** de "unos 1/(1 − γ) pasos". ¿De dónde sale?

Imagina un robot que recibe una recompensa de **1 en cada paso, para siempre**. Su retorno descontado es:

```
   S = 1 + γ + γ² + γ³ + γ⁴ + ...       (infinitos términos)
```

A una suma así, donde cada término es el anterior por el mismo número, se le llama **serie geométrica**. Parece que una suma infinita debería ser infinita, pero no siempre: si γ < 1, los términos se hacen tan pequeños que la suma se **estabiliza**. Hay un truco precioso para calcularla. Multiplica S por γ:

```
   γ · S =     γ + γ² + γ³ + γ⁴ + ...
```

Es **la misma suma, sin el 1 del principio**. Así que, si restas:

```
   S − γ · S = 1           →       S · (1 − γ) = 1           →       S = 1 / (1 − γ)
```

(Sacar S factor común y despejar, NB04b.) Con γ = 0,99: S = 1 / 0,01 = **100**. Comprobémoslo sumando muchos términos con el ordenador:
"""),

code(r"""gamma = 0.99
for n_terminos in [10, 100, 500, 2000]:
    suma = sum(gamma ** k for k in range(n_terminos))
    print(f"{n_terminos:>5} términos: {suma:8.3f}")
print("1 / (1 - γ) =", 1 / (1 - gamma))"""),

md(r"""(`sum(... for k in range(n))` suma todos los valores que salen del bucle, NB21.)

Se acerca a 100 y no pasa de ahí. (Fíjate en la fila de 100 términos: 63,4, el **63 %** del total. Ahora verás por qué.) Una recompensa descontada con 0,99 "vale" como **100 pasos** sin descontar: de ahí el horizonte. Por eso, en el NB32, el retorno del palo de escoba (recompensa como mucho 1 por paso) nunca pasa de 100.

### ¿Por qué "más o menos 100 pasos"?

¿Cuánto pesa la recompensa de dentro de 100 pasos? γ¹⁰⁰:
"""),

code(r"""print("0,99 elevado a 100:", gamma ** 100)
print("1/e:               ", 1 / np.e)"""),

md(r"""¡Casi exactamente **1/e ≈ 0,37**! Es la **constante de tiempo** del decaimiento exponencial del NB15b: tras "1/(1 − γ)" pasos, el peso ha caído al 37 % (se ha perdido el 63 %). Las recompensas más lejanas siguen contando, pero cada vez menos. Por eso decimos que al robot le importa "más o menos" lo que pasa en los próximos 1/(1 − γ) pasos: no es un corte brusco, es una **memoria que se desvanece**.

### Con un número finito de pasos

Si el episodio termina tras N pasos, el mismo truco (prueba a hacerlo en el ejercicio E7) da:

```
   1 + γ + ... + γᴺ⁻¹  =  (1 − γᴺ) / (1 − γ)
```
"""),

code(r"""N = 50
print(sum(gamma ** k for k in range(N)), "=", (1 - gamma ** N) / (1 - gamma))"""),

md(r"""## 8 · ¿Dividir entre n o entre n − 1?

En el NB28 calculaste la **varianza** de unos datos: la media de los cuadrados de las distancias a su media. Dividías entre **n**, el número de datos. Pero en muchos libros, y en PyTorch (NB31), verás que se divide entre **n − 1**. ¿Quién tiene razón?

Depende de la pregunta:

- Si tienes **todos** los datos que existen (por ejemplo, las notas de los 30 alumnos de una clase, y solo te interesa esa clase), se divide entre **n**.
- Si tus datos son una **muestra** sacada de algo más grande (50 episodios de los infinitos que podría jugar la política), y quieres **estimar** la varianza de **todo**, dividir entre n se queda **corto**, un poquito, en promedio.

¿Por qué se queda corto? Porque medimos las distancias a la media **de la muestra**, no a la de verdad. Y la media de la muestra está, por construcción, **en el centro de esos datos concretos**: más cerca de ellos que la media de verdad. Distancias un poco más cortas → varianza un poco más pequeña. Con **un solo** dato es extremo: la media de la muestra es ese dato, la distancia es 0, y la varianza "medida" es 0, aunque los datos de verdad varíen mucho.

Comprobémoslo: sacamos muchas muestras pequeñas de una campana de **varianza 1** y promediamos las varianzas calculadas de las dos formas.
"""),

code(r"""for n in [2, 5, 50]:
    muestras = generador.standard_normal((100_000, n))          # 100.000 muestras de n datos cada una
    entre_n = muestras.var(axis=1, ddof=0).mean()
    entre_n_menos_1 = muestras.var(axis=1, ddof=1).mean()
    print(f"n = {n:>2}: entre n → {entre_n:.3f} | entre n − 1 → {entre_n_menos_1:.3f}   (verdad: 1)")"""),

md(r"""(`ddof` significa *delta degrees of freedom*: cuánto se resta a n al dividir. `ddof=0`, entre n, es lo que hace NumPy si no dices nada; `ddof=1`, entre n − 1. `axis=1` calcula una varianza por fila, NB27.)

Entre n, con 2 datos, sale **0,5** en vez de 1: la mitad. Con 5 datos, 0,8. Exactamente **(n − 1)/n** de la verdad: por eso, dividir entre n − 1 lo corrige justo, y sale 1. A esta corrección se le llama **corrección de Bessel**.

¿Y en la práctica del curso? Con 50 datos, la diferencia es de un 2 %: casi nada. Con miles de jugadas por lote (NB33), nada en absoluto. Pero conviene saber que existe por una razón muy concreta: **NumPy divide entre n por defecto, y PyTorch, entre n − 1**. Si algún día comparas un número de un lado con el del otro y no casan por poquito, ya sabes por qué.
"""),

md(r"""## 9 · Resumen de la lección

1. **Cosas seguidas → se multiplica**: la mitad de la mitad es 0,5 × 0,5. Si la segunda depende de la primera, se usa su probabilidad **condicionada** (3/5 × 2/4). Un episodio es un producto de piezas de la **política** y piezas de la **física**.
2. Multiplicar cientos de probabilidades **subdesborda** a 0. Los **logaritmos** lo convierten en sumas: **ln(a·b) = ln a + ln b**. Misma ordenación, sin hundirse.
3. **Pendiente de la log-probabilidad de la campana**: respecto a μ, **(a − μ)/σ²**; respecto a σ, **(z² − 1)/σ**; respecto a ln σ, **z² − 1** (z = (a − μ)/σ). Deducidas con la regla de la cadena, la de las potencias y la del logaritmo.
4. **El truco del logaritmo**: **p' = p·(ln p)'**. Convierte la pendiente de la recompensa esperada en un **valor esperado** que se estima jugando: **media de [R × (ln p)']**. Es el **teorema del gradiente de la política**.
5. La **física desaparece** de la pendiente (no depende de las ruedecillas): aprendizaje **sin modelo**. La regla del producto llega a lo mismo, pero los logaritmos lo hacen fácil.
6. **La línea base no introduce sesgo**: la media de (ln p)' es 0, porque las probabilidades suman 1. Pero **reduce el ruido** muchísimo. Puede depender de la situación, no de la acción.
7. **Serie geométrica**: 1 + γ + γ² + ... = **1/(1 − γ)**. Con 0,99, 100 pasos; γ elevado a ese número es ≈ 1/e: la constante de tiempo.
8. Varianza de una **muestra**: entre n se queda corta un factor (n − 1)/n; entre **n − 1** (Bessel) acierta. NumPy divide entre n por defecto; PyTorch, entre n − 1.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Independientes** | Sucesos que no se influyen: la probabilidad de los dos es el producto. |
| **Probabilidad condicionada** | La probabilidad de algo **sabiendo** que ya ha pasado otra cosa. |
| **Subdesbordamiento (*underflow*)** | Un número tan pequeño que el ordenador lo redondea a 0. |
| **Truco del logaritmo** | p' = p·(ln p)': la pendiente de una probabilidad como probabilidad por algo. |
| **Teorema del gradiente de la política** | La pendiente de la recompensa esperada es la media de R × (pendiente de ln p). |
| **Sin modelo (*model-free*)** | Que aprende jugando, sin necesitar las ecuaciones del mundo. |
| **Sesgo** | Una desviación sistemática, siempre hacia el mismo lado. |
| **Serie geométrica** | Suma en la que cada término es el anterior por el mismo número. |
| **Corrección de Bessel** | Dividir entre n − 1 para estimar la varianza a partir de una muestra. |
"""),

md(r"""## 10 · Ejercicios

**E1.** Tiras un dado tres veces. ¿Probabilidad de sacar tres seises? Compruébalo con 1.000.000 de tiradas de mentira (`generador.integers(1, 7, n)` da n números enteros del 1 al 6).

**E2.** Una bolsa con 4 rojas y 1 azul. Sacas dos sin devolver. ¿Probabilidad de que **las dos** sean rojas? ¿Y de que la **segunda** sea azul? (Pista para la segunda: o la primera fue roja y la segunda azul, o... ¿puede ser la primera azul y la segunda también?)

**E3.** Calcula ln(0,5 elevado a 2000) **sin** calcular 0,5 elevado a 2000. ¿Cuánto da el ordenador si intentas calcular primero la potencia y luego el logaritmo?

**E4.** Con μ = 10 y σ = 2, la política sortea a = 7. Sin ordenador: ¿cuánto vale la pendiente de ln p respecto a μ? ¿Y respecto a ln σ? Si esa acción salió muy bien, ¿qué le pasará a la media? ¿Y a la anchura? Comprueba los números con `pendiente`.

**E5.** (Para valientes.) Demuestra que, con a sorteada de una campana de media μ y anchura σ, el valor esperado de −(a − 3)² es −(μ − 3)² − σ². Pista: escribe a − 3 = (a − μ) + (μ − 3), desarrolla el cuadrado con (x + y)² = x² + 2·x·y + y² (un cuadrado de lado x + y se parte en un cuadrado de lado x, otro de lado y y dos rectángulos x por y; compruébalo con x = 2, y = 3) y usa que la media de (a − μ) es 0 y la de (a − μ)² es σ² (NB28). Comprueba el resultado con 100.000 jugadas para μ = 1, σ = 2.

**E6.** Repite la estimación de la pendiente del apartado 4 con μ = 5 (la media está a la **derecha** del 3). ¿Qué pendiente esperas? ¿Qué signo? ¿Coincide?

**E7.** Deduce la fórmula de la serie geométrica **finita**: S = 1 + γ + ... + γᴺ⁻¹. Pista: escribe γ·S y resta, como en el apartado 7. ¿Qué términos no se cancelan?

**E8.** Para γ = 0,9, 0,99 y 0,999: calcula el horizonte 1/(1 − γ) y comprueba que γ elevado al horizonte es siempre cercano a 1/e.

**E9.** Tienes 3 episodios con retornos 10, 20 y 60. Calcula la varianza dividiendo entre n y entre n − 1, a mano y con NumPy. ¿Cuál dirías que estima mejor la varianza de la política, si esos 3 son una muestra?

---

### Soluciones

<details>
<summary>▶ Solución E1</summary>

Tres cosas seguidas e independientes: 1/6 × 1/6 × 1/6 = **1/216 ≈ 0,00463**.

```python
generador = np.random.default_rng(0)
n = 1_000_000
d1, d2, d3 = generador.integers(1, 7, n), generador.integers(1, 7, n), generador.integers(1, 7, n)
print(((d1 == 6) & (d2 == 6) & (d3 == 6)).mean(), "≈", 1 / 216)
```
</details>

<details>
<summary>▶ Solución E2</summary>

- Las dos rojas: 4/5 × 3/4 = 12/20 = **0,6**.
- Segunda azul: solo hay una azul, así que la primera tiene que ser roja (4/5) y luego, sabiéndolo, la azul es 1 de las 4 que quedan (1/4): 4/5 × 1/4 = **0,2**. (La primera azul y la segunda azul es imposible: probabilidad 0.) Curioso: 0,2 es lo mismo que la probabilidad de que la **primera** sea azul (1/5). Sin saber qué salió primero, la segunda bola es "una cualquiera".

```python
generador = np.random.default_rng(0)
dos_rojas = segunda_azul = 0
for intento in range(100_000):
    bolsa = ["roja"] * 4 + ["azul"]
    generador.shuffle(bolsa)
    dos_rojas += bolsa[0] == "roja" and bolsa[1] == "roja"
    segunda_azul += bolsa[1] == "azul"
print(dos_rojas / 100_000, segunda_azul / 100_000)
```

(Sumar un booleano suma 1 si es True y 0 si es False.)
</details>

<details>
<summary>▶ Solución E3</summary>

ln(0,5²⁰⁰⁰) = 2000 × ln(0,5) ≈ **−1386,3**. Si calculas primero la potencia, se subdesborda a 0, y ln(0) es −∞ (NumPy avisa y da `-inf`).

```python
print(2000 * np.log(0.5))
with np.errstate(divide="ignore"):          # silenciar el aviso de ln(0)
    print(np.log(0.5 ** 2000))
```
</details>

<details>
<summary>▶ Solución E4</summary>

- Respecto a μ: (a − μ)/σ² = (7 − 10)/4 = **−0,75**. Negativa: la acción está a la izquierda; si salió bien, la media **bajará** hacia 7.
- z = (7 − 10)/2 = −1,5; z² − 1 = 2,25 − 1 = **1,25**. Positiva: la acción cayó más lejos de una σ; si salió bien, la campana se **ensanchará**.

```python
a, mu, sigma = 7.0, 10.0, 2.0
print(pendiente(lambda m: log_p(a, m, sigma), mu))
print(pendiente(lambda l: log_p(a, mu, np.exp(l)), np.log(sigma)))
```
</details>

<details>
<summary>▶ Solución E5</summary>

(a − 3)² = ((a − μ) + (μ − 3))² = (a − μ)² + 2·(a − μ)·(μ − 3) + (μ − 3)². Las medias, término a término: la de (a − μ)² es σ²; la del término del medio es 2·(μ − 3) × (media de a − μ) = 2·(μ − 3) × 0 = 0; el último es fijo, (μ − 3)². Total: σ² + (μ − 3)², y con el signo menos, **−(μ − 3)² − σ²**. Con μ = 1, σ = 2: −4 − 4 = **−8**.

```python
generador = np.random.default_rng(0)
mu, sigma = 1.0, 2.0
acc = mu + sigma * generador.standard_normal(100_000)
print((-(acc - 3) ** 2).mean(), "≈", -(mu - 3) ** 2 - sigma ** 2)
```

(Fíjate en el −σ²: explorar **cuesta** recompensa, como viste en el NB28. Cuanto más ancha la campana, peor la media.)
</details>

<details>
<summary>▶ Solución E6</summary>

−2·(μ − 3) = −2·2 = **−4**: negativa, "baja la media", hacia el 3.

```python
generador = np.random.default_rng(0)
mu, sigma = 5.0, 1.0
acc = mu + sigma * generador.standard_normal(100_000)
print((-(acc - 3) ** 2 * (acc - mu) / sigma ** 2).mean(), "≈", -2 * (mu - 3))
```
</details>

<details>
<summary>▶ Solución E7</summary>

```
   S     = 1 + γ + γ² + ... + γᴺ⁻¹
   γ · S =     γ + γ² + ... + γᴺ⁻¹ + γᴺ
```

Al restar, se cancela todo menos el 1 de arriba y el γᴺ de abajo: S − γS = 1 − γᴺ, así que **S = (1 − γᴺ)/(1 − γ)**. Si N es muy grande y γ < 1, γᴺ se hace casi 0, y vuelve a salir 1/(1 − γ).

```python
gamma, N = 0.9, 20
print(sum(gamma ** k for k in range(N)), (1 - gamma ** N) / (1 - gamma))
```
</details>

<details>
<summary>▶ Solución E8</summary>

Horizontes: **10, 100 y 1000** pasos. Y γ elevado al horizonte: 0,349; 0,366; 0,368. Cada vez más cerca de 1/e = 0,3679 (cuanto más cerca de 1 está γ, mejor la aproximación).

```python
for gamma in [0.9, 0.99, 0.999]:
    H = 1 / (1 - gamma)
    print(f"γ = {gamma}: horizonte {H:.0f} | γ^H = {gamma ** H:.4f} | 1/e = {1 / np.e:.4f}")
```
</details>

<details>
<summary>▶ Solución E9</summary>

Media: (10 + 20 + 60)/3 = 30. Distancias al cuadrado: 400, 100, 900; suma 1400. Entre n: 1400/3 ≈ **466,7**. Entre n − 1: 1400/2 = **700**. Como es una muestra pequeñita, la de n − 1 es la buena estimación (la de n se queda corta, en promedio, un factor 2/3).

```python
retornos = np.array([10.0, 20.0, 60.0])
print(retornos.var(), retornos.var(ddof=1))
```
</details>
"""),

md(r"""## 11 · 🛠 Práctica en MuJoCo: el truco del logaritmo, con episodios de verdad

Hoy has deducido con lápiz cuatro piezas: la log-probabilidad de un episodio es una **suma**; la **física desaparece** de su
pendiente; el **truco del logaritmo** estima la pendiente de la recompensa esperada **jugando**; y la **línea base** no tuerce la
flecha pero quita ruido. Todas las comprobaste con campanas sueltas. Ahora vas a comprobarlas con **episodios enteros del palo de
escoba de MuJoCo** (la práctica del NB28), donde la física es de verdad y no sabemos escribir su fórmula.

La política será una **campana** (NB28) con una sola ruedecilla, **w**:

```
   media μ = w × ángulo + 0,5 × velocidad de giro        (en radianes y rad/s, como los da MuJoCo)
   acción  = μ + σ × ruido normal,  con σ = 0,3           (la orden al motor, que solo admite de −1 a 1)
```

La pregunta: **¿hacia dónde hay que mover w para que el palo aguante más?** La responderemos de dos formas (a lo bruto y con el
truco) y comprobaremos que coinciden.
"""),

md(r"""### Paso 1 · El palo y un episodio que lo apunta todo

Cargamos el palo y escribimos una función que juega **un episodio** de hasta 300 pasos (3 segundos) con la política exploradora.
Apunta lo que la política necesita para calcular sus probabilidades: el ángulo y el giro que vio en cada paso, y la acción que sorteó.
La recompensa es la del palo de siempre (1 − (ángulo/30°)² mientras siga de pie), y el episodio acaba si pasa de 30 grados.
"""),

code(r"""import mujoco
import taller

modelo, datos = taller.cargar("palo_escoba")
CAIDA = np.radians(30)
SIGMA = 0.3

def episodio(w, generador, pasos=300):
    datos = mujoco.MjData(modelo)                                  # un mundo nuevo
    datos.qpos[1] = np.radians(generador.uniform(-5, 5))           # empieza algo torcido (NB28)
    angulos, giros, acciones, retorno = [], [], [], 0.0
    for t in range(pasos):
        angulo, giro = datos.qpos[1], datos.qvel[1]
        accion = (w * angulo + 0.5 * giro) + SIGMA * generador.standard_normal()   # campana: μ + σ·ruido
        angulos.append(angulo); giros.append(giro); acciones.append(accion)
        datos.ctrl[0] = np.clip(accion, -1, 1)
        mujoco.mj_step(modelo, datos)
        if abs(datos.qpos[1]) > CAIDA:
            break
        retorno += 1 - (datos.qpos[1] / CAIDA) ** 2
    return np.array(angulos), np.array(giros), np.array(acciones), retorno"""),

md(r"""### Paso 2 · La log-probabilidad de un episodio entero (apartados 1 y 2)

Jugamos un episodio con w = 1. La probabilidad de que la política hiciera **justo esas** 300 acciones es un **producto** de 300
densidades; su logaritmo, una **suma** de 300 log-probabilidades (la función `log_p` del apartado 3):
"""),

code(r"""generador = np.random.default_rng(0)
angulos, giros, acciones, retorno = episodio(1.0, generador)
medias = 1.0 * angulos + 0.5 * giros
log_ps = log_p(acciones, medias, SIGMA)

print(f"pasos: {len(acciones)} | retorno: {retorno:.1f}")
print(f"suma de log-probabilidades: {log_ps.sum():.2f}")
print(f"producto de probabilidades: {np.prod(np.exp(log_ps)):.3e}")"""),

md(r"""El producto ya es un número con **31 ceros** detrás de la coma, y eso con un episodio cortito de 3 segundos; con uno de un
minuto (6.000 pasos) el ordenador lo redondearía a **0**. La suma, unos **−71**, es un número de lo más normal. Por eso los
algoritmos trabajan con logaritmos (apartado 2).
"""),

md(r"""### Paso 3 · La física desaparece (apartado 5)

La pendiente de ln P(episodio) respecto a w, según el apartado 5, solo necesita las piezas de la **política**. Con la regla de la
cadena (apartado 3: pendiente respecto a μ = (a − μ)/σ², y μ cambia "ángulo" por cada unidad de w):

```
   pendiente de ln P respecto a w  =  suma sobre los pasos de  (a − μ) / σ²  ×  ángulo
```

Comprobémoslo con la pendiente numérica: movemos w un poquito y recalculamos las log-probabilidades **de las mismas acciones**, en
**las mismas situaciones**. Fíjate en que **no volvemos a simular nada**: MuJoCo no aparece en la cuenta.
"""),

code(r"""ln_P = lambda w: log_p(acciones, w * angulos + 0.5 * giros, SIGMA).sum()

print("numérica:", pendiente(ln_P, 1.0))
print("fórmula: ", (((acciones - medias) / SIGMA ** 2) * angulos).sum())"""),

md(r"""Iguales. La física del carro, la gravedad, el motor... todo eso lo calcula MuJoCo, y nosotros no sabemos su fórmula. Pero
**no nos hace falta**: para saber cómo cambia la probabilidad del episodio al tocar w, basta con la campana, que la hemos hecho
nosotros. Eso es lo que significa **sin modelo** (*model-free*).
"""),

md(r"""### Paso 4 · La montaña J(w)

¿Cuánto aguanta el palo, de media, según w? Es la **recompensa esperada** J(w) (apartado 4). Estimémosla con 200 episodios para
varios w (tarda unos segundos):
"""),

code(r"""def J(w, n, semilla):
    generador = np.random.default_rng(semilla)
    return np.array([episodio(w, generador)[3] for _ in range(n)])

ws = [0, 0.5, 1, 1.5, 2, 3]
alturas = [J(w, 200, semilla=0).mean() for w in ws]
for w, a in zip(ws, alturas):
    print(f"w = {w}: retorno medio {a:6.1f}")

plt.figure(figsize=(6, 3.2))
plt.plot(ws, alturas, "o-")
plt.xlabel("w (ruedecilla del ángulo)")
plt.ylabel("J(w), retorno medio")
plt.grid(True, alpha=0.4)
plt.show()"""),

md(r"""Una cuesta: con w = 0 (la política no mira el ángulo) el palo aguanta poco (unos 106 puntos de 300); con w = 3, casi el máximo.
Desde w = 1, la flecha "cuesta arriba" apunta claramente a **subir w**. Pero ¿**cuánto** de empinada es la cuesta en w = 1?
"""),

md(r"""### Paso 5 · La pendiente, a lo bruto (NB17)

Como en el NB17: mover w un poco a cada lado y medir. Usamos la **misma semilla** en los dos lados (así los dos lotes de 1.000
episodios tienen los mismos ángulos de partida y el mismo ruido, y la resta tiene mucho menos azar):
"""),

code(r"""h = 0.25
a_lo_bruto = (J(1 + h, 1000, semilla=5).mean() - J(1 - h, 1000, semilla=5).mean()) / (2 * h)
print(f"pendiente de J en w = 1, a lo bruto: {a_lo_bruto:.1f}")"""),

md(r"""Unos **116** puntos de retorno por cada unidad de w. Ha costado **2.000 episodios**, y solo para **una** ruedecilla: con un
millón de ruedecillas serían dos mil millones.
"""),

md(r"""### Paso 6 · La pendiente, con el truco del logaritmo (apartados 4 y 6)

Ahora la forma del aprendizaje por refuerzo: jugamos episodios **solo con w = 1**, y en cada uno multiplicamos su retorno R por la
pendiente de ln P del paso 3. La media es la flecha. Y lo hacemos también restando la **línea base** (la media de los R). Con
el error típico (NB28) para saber cuánto fiarnos (unos 20 segundos):
"""),

code(r"""generador = np.random.default_rng(2)
R, pendientes_ln_P = [], []
for n in range(2000):
    angulos, giros, acciones, retorno = episodio(1.0, generador)
    R.append(retorno)
    pendientes_ln_P.append((((acciones - (angulos + 0.5 * giros)) / SIGMA ** 2) * angulos).sum())
R, pendientes_ln_P = np.array(R), np.array(pendientes_ln_P)

sin_base = R * pendientes_ln_P
con_base = (R - R.mean()) * pendientes_ln_P
for nombre, e in [("sin línea base", sin_base), ("con línea base", con_base)]:
    print(f"{nombre}: {e.mean():6.1f} ± {2 * e.std() / np.sqrt(len(e)):5.1f}  (media ± 2 errores típicos)")"""),

md(r"""Las dos casan con los **~116** a lo bruto, dentro de su margen de error: el truco funciona con física de verdad, sin saber
nada de ella. Pero mira los márgenes: **sin línea base**, ±71 (la estimación, unos 78, apenas se sabe si es 10 o 150); **con línea
base**, ±20 (unos 113). La misma flecha, con **3,5 veces menos ruido**: el apartado 6, en MuJoCo.

¿Qué significa eso para un robot que aprende con lotes pequeños? Partamos los 2.000 episodios en 40 lotes de 50 y miremos cuántas
veces la flecha de un lote apunta **al revés** (diría "baja w", cuando la cuesta sube):
"""),

code(r"""for nombre, e in [("sin línea base", sin_base), ("con línea base", con_base)]:
    por_lote = e.reshape(40, 50).mean(axis=1)                  # 40 lotes de 50 episodios (NB27)
    print(f"{nombre}: flecha al revés en {(por_lote < 0).sum()} de 40 lotes")"""),

md(r"""Sin línea base, **14 de 40** lotes empujarían al robot **cuesta abajo** (más de un tercio); con línea base, **1 de 40**. Es exactamente el fracaso y el éxito que vas a ver en el NB29.
"""),

md(r"""### Tus retos

**R1.** Calcula la pendiente de ln P del episodio del paso 2 respecto a la **otra** ruedecilla, la de la velocidad de giro (el 0,5),
con la fórmula y con `pendiente`. (Pista: ahora μ cambia "giro" por cada unidad de esa ruedecilla.)

**R2.** En el paso 6 usamos la recompensa del episodio **entero** para todas sus acciones. ¿Qué pieza del apartado 6 dice que
podríamos usar solo las recompensas **desde cada paso**? ¿Para qué serviría?

**R3.** Repite el paso 5 con w = 2,5 en vez de 1 (mira antes la montaña del paso 4: ¿qué pendiente esperas?).
"""),

md(r"""<details>
<summary>▶ Solución R1</summary>

```python
generador = np.random.default_rng(0)
angulos, giros, acciones, retorno = episodio(1.0, generador)
ln_P_giro = lambda k: log_p(acciones, 1.0 * angulos + k * giros, SIGMA).sum()
print(pendiente(ln_P_giro, 0.5))
print((((acciones - (angulos + 0.5 * giros)) / SIGMA ** 2) * giros).sum())
```

Las dos salen iguales: la fórmula es la misma de siempre, (a − μ)/σ² × **la entrada que multiplica a esa ruedecilla** (aquí, el
giro). Con vectores: (a − μ)/σ² × observación, la flecha del NB29.
</details>

<details>
<summary>▶ Solución R2</summary>

La última: **"las recompensas de antes no cuentan"**. Una acción no puede influir en las recompensas que ya pasaron, así que, para
ella, son una línea base: se pueden quitar sin torcer la flecha, y quitarlas quita ruido. En el NB29 cada acción se juzga por su
**retorno desde ese paso**, G(t).
</details>

<details>
<summary>▶ Solución R3</summary>

```python
print((J(2.5 + h, 1000, semilla=5).mean() - J(2.5 - h, 1000, semilla=5).mean()) / (2 * h))
```

En la montaña, entre w = 2 y w = 3 el retorno apenas sube (de ~287 a ~299): la cuesta casi se ha acabado, así que la pendiente
sale **pequeña**: medido, unos **8** (contra 116 en w = 1). Cerca de la cima, la flecha se acorta: el ascenso por gradiente frena solo (NB17).
</details>
"""),

md(r"""### Qué has aprendido de MuJoCo hoy

- Una **política estocástica** sobre MuJoCo: la campana decide la orden del motor, y apuntas lo que vio y lo que sorteó en cada paso.
- La **log-probabilidad de un episodio** de MuJoCo es una suma de log-probabilidades de la política; la física (MuJoCo) no entra en
  su pendiente. Por eso se puede aprender **sin conocer las ecuaciones del simulador**.
- La pendiente de la recompensa esperada se puede medir **a lo bruto** (muchos episodios por ruedecilla) o con el **truco del
  logaritmo** (un solo lote, todas las ruedecillas a la vez), y en MuJoCo coinciden.
- La **línea base** deja la flecha igual y le quita ruido (3,5 veces menos aquí).

En la práctica del **NB29** darás el paso que falta: usar esa flecha para **entrenar**. Será tu **primer entrenamiento en MuJoCo**:
REINFORCE enseñará al palo de escoba a mantenerse de pie, empezando sin saber nada.
"""),

md(r"""## 12 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **NB29**, todo esto se convierte en un algoritmo: **REINFORCE**. Reconocerás cada pieza: la pendiente (a − μ)/σ² del apartado 3, el "R × pendiente de ln p" del apartado 4, la línea base del apartado 6 y el descuento del apartado 7. Ya no habrá ningún "los matemáticos demostraron": lo has demostrado tú, y lo has comprobado con episodios de MuJoCo.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB28b_matematicas_del_gradiente.ipynb")
    build(out, cells, title="NB28b · Las matemáticas del gradiente de la política")
