"""Construye NB17b · Las reglas de las pendientes (Parte 2 · lección intermedia).

Añadida tras la auditoría de 2026-10-04: el curso usaba derivadas de
(x − 3)², de la exponencial, del logaritmo, de sen y cos, segundas derivadas y
la regla del producto sin haberlas enseñado (NB17 E1, NB19, NB29, NB33, NB47,
NB48). Notación f'(x) y df/dx; cada regla con intuición y comprobada contra la
pendiente numérica centrada del NB16: constante, recta, potencias (también
1/x y √x), constante por función, suma, regla de la cadena (engranajes, el
signo de −x), producto (el rectángulo), exponencial (e^x es su propia
pendiente), logaritmo (1/x; la de ln f es f'/f), la rampa (0 o 1); tabla;
segunda derivada (aceleración, cima o valle, el método de Newton);
derivadas parciales con reglas.
Práctica en MuJoCo: la energía (flag energy → datos.energy, mj_energyPos/Vel).
Pelota en caída libre (RK4): altura, qvel = −9,81·t y qacc = −9,81 coinciden
con las reglas; energía total 9,81 constante; pendientes de U y K = ∓48,118·t
(cadena) y del total 0. Péndulo 1 kg/1 m desde 60°: sin damping 9,81 fija;
con damping 0,1 baja a 7,88 en 5 s en escalones, pendiente = −b·ω² (vídeo).
Retos: sin RK4 se pierde 0,24 J/s; lanzada a 5 m/s (16,06); damping 0,3.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB17b · Las reglas de las pendientes

**Parte 2 · Las matemáticas del aprendizaje — Lección intermedia (entre el NB17 y el NB18)**

> En el NB16 aprendiste a **calcular** una pendiente con el ordenador: mirar la función un poquito a la izquierda y un poquito a la derecha, y dividir. Funciona siempre, pero tiene dos pegas: hay que calcular la función **dos veces** por cada pendiente (con millones de ruedecillas, eso es lentísimo, NB17), y no te dice nada de **por qué** la pendiente vale lo que vale.

Los matemáticos descubrieron hace más de 300 años unas pocas **reglas** que dan la pendiente **exacta** de casi cualquier función, con una fórmula, sin calcular nada dos veces. En el NB16 viste la primera: la pendiente de x² es 2·x. Hoy veremos todas las que necesita el curso, **una a una**, y cada una la **comprobaremos** con la pendiente numérica del NB16, para que no tengas que creerte nada.

Al terminar, sabrás calcular a mano la pendiente de funciones como (x − 3)², e^(−x²) o ln(x² + 1). Y entenderás de dónde salen las fórmulas que usaremos en el NB18 (la pendiente del error), en el NB19 (la retropropagación) y en el NB29 (cómo aprende un robot por refuerzo).
"""),

code(r"""import numpy as np
import matplotlib.pyplot as plt

def pendiente(f, x, h=1e-5):
    # La pendiente numérica centrada del NB16: nuestra "verdad" para comprobar las reglas.
    return (f(x + h) - f(x - h)) / (2 * h)

def comprobar(f, regla, puntos=(-1.5, 0.3, 2.0)):
    # Compara la pendiente numérica con la que da una regla, en varios puntos.
    for x in puntos:
        print(f"  x = {x:+.1f}: numérica {pendiente(f, x):+.5f} | regla {regla(x):+.5f}")"""),

md(r"""(Dos funciones de ayuda. `pendiente` es la del NB16, con un valor por defecto para h (NB11b). `comprobar` recibe una función y una "regla" (otra función, que da la pendiente según la fórmula que estemos probando), y las compara en tres puntos. Si las columnas coinciden, la regla es correcta.)

## 1 · Notación

La pendiente de una función f en cada punto es, a su vez, **otra función** (NB16: la pendiente de x² es la función 2·x). Se le llama la **derivada** de f, y se escribe de dos formas:

- **f'(x)** (se lee "f prima de x"): la derivada de f.
- **df/dx** (se lee "de efe de equis"): "lo que cambia f cuando cambia x, un poquito". Recuerda la definición del NB16: un cambio pequeñito de f dividido por un cambio pequeñito de x.

Las dos significan lo mismo. La segunda es útil cuando hay varias letras, porque dice **respecto a qué** letra se mide la pendiente.
"""),

md(r"""## 2 · Las reglas fáciles

### Una constante: pendiente 0

Si f(x) = 5 (una línea horizontal), la función no sube ni baja nunca: **su pendiente es 0** en todas partes.

### Una recta: su inclinación

Si f(x) = m·x + b (una recta, NB04b), su pendiente es **m** en todas partes: la recta sube m por cada unidad que avanzas, siempre igual. El `+ b` (que solo la sube o la baja, NB15b) no cambia la pendiente.

### Las potencias

La regla que viste en el NB16 para x² es un caso de una regla general para **cualquier potencia**:

```
   la pendiente de xⁿ es  n · xⁿ⁻¹         ("baja el exponente delante y réstale 1")
```

- x² → 2·x¹ = **2·x** (la del NB16).
- x³ → **3·x²**.
- x¹ = x → 1·x⁰ = **1** (la recta de pendiente 1, ✓).

Y funciona también con exponentes negativos y fraccionarios (NB03b):

- 1/x = x⁻¹ → −1·x⁻² = **−1/x²**.
- √x = x^0,5 → 0,5·x^(−0,5) = **1 / (2·√x)**.

Comprobémoslas:
"""),

code(r"""print("x³:")
comprobar(lambda x: x ** 3, lambda x: 3 * x ** 2)
print("1/x:")
comprobar(lambda x: 1 / x, lambda x: -1 / x ** 2)
print("√x:")
comprobar(lambda x: np.sqrt(x), lambda x: 1 / (2 * np.sqrt(x)), puntos=(0.5, 1.0, 4.0))"""),

md(r"""Coinciden en todos los puntos (hasta la quinta cifra decimal: lo que queda es el pequeño error de la pendiente numérica, NB16). (Las `lambda` son funciones de una línea, que verás a fondo en el NB23: `lambda x: x ** 3` es lo mismo que `def f(x): return x ** 3`. Aquí sirven para escribir cada función y su regla en el sitio, sin ponerles nombre.)

### Un número multiplicando: se queda

Si multiplicas una función por un número, su pendiente se multiplica por ese número: **la pendiente de c·f(x) es c·f'(x)**. Tiene sentido: si una curva es el triple de alta (NB15b), sube el triple de deprisa. Así, la pendiente de 5·x² es 5·2·x = **10·x**, y la de −x² es **−2·x**.

### Una suma: suma de pendientes

**La pendiente de una suma es la suma de las pendientes**: (f + g)' = f' + g'. Si una cosa sube 3 por segundo y otra 2, juntas suben 5. Así se deriva cualquier polinomio, término a término:

```
   f(x) = 4·x³ − 2·x² + 7·x − 1
   f'(x) = 12·x² − 4·x + 7
```
"""),

code(r"""comprobar(lambda x: 4 * x ** 3 - 2 * x ** 2 + 7 * x - 1, lambda x: 12 * x ** 2 - 4 * x + 7)"""),

md(r"""## 3 · La regla de la cadena: engranajes

### Una función dentro de otra

Muchas funciones son **una función dentro de otra**. Por ejemplo, (x − 3)²: primero se calcula **x − 3** (la de dentro) y después se eleva **al cuadrado** (la de fuera). ¿Cómo se calcula su pendiente?

Imagina dos **engranajes**: el primero (la función de dentro) gira **2 vueltas** por cada vuelta que le das; el segundo (la de fuera) gira **3 vueltas** por cada vuelta del primero. Si giras una vuelta, el segundo da 2 × 3 = **6** vueltas. Los efectos se **multiplican**:

```
   pendiente de f(g(x))  =  (pendiente de la de fuera, en g(x))  ×  (pendiente de la de dentro)
                         =  f'(g(x)) · g'(x)
```

Es la **regla de la cadena**, la regla más importante de este notebook: es la base de todo el aprendizaje de las redes neuronales (NB18, NB19).

### Paso a paso con (x − 3)²

1. La de **dentro**: g(x) = x − 3. Su pendiente es **1** (una recta).
2. La de **fuera**: el cuadrado, f(u) = u². Su pendiente es **2·u**, y hay que calcularla **en lo de dentro**, u = x − 3: **2·(x − 3)**.
3. Se multiplican: 2·(x − 3) · 1 = **2·(x − 3)**.

Y si la función es **−(x − 3)²** (la colina del NB17), el signo menos de fuera se queda delante (regla de la constante): **−2·(x − 3)**. Esta es la pendiente que el NB17 usaba en su ejercicio E1: ahora sabes de dónde sale.

### Cuando lo de dentro tiene pendiente distinta de 1

Con **(2·x + 1)²**, la de dentro (2·x + 1) tiene pendiente **2**. Así que: 2·(2·x + 1) · **2** = **4·(2·x + 1)**. Y una trampa muy común: con **(3 − x)²**, la de dentro, 3 − x, tiene pendiente **−1** (baja). Resultado: 2·(3 − x)·(−1) = **−2·(3 − x)**. ¡Olvidar ese −1 es el error más típico de la regla de la cadena!
"""),

code(r"""print("(x − 3)²:")
comprobar(lambda x: (x - 3) ** 2, lambda x: 2 * (x - 3))
print("(2x + 1)²:")
comprobar(lambda x: (2 * x + 1) ** 2, lambda x: 4 * (2 * x + 1))
print("(3 − x)²  (¡cuidado con el −1!):")
comprobar(lambda x: (3 - x) ** 2, lambda x: -2 * (3 - x))"""),

md(r"""¿Te has fijado en que (3 − x)² da las mismas pendientes que (x − 3)²? Es lógico: las dos son **la misma función** (un número y su opuesto tienen el mismo cuadrado, NB03b), así que tienen que tener la misma pendiente. Y efectivamente, −2·(3 − x) = 2·(x − 3). Sin el −1 de lo de dentro, te habría salido justo la pendiente cambiada de signo: un error que la comprobación numérica caza al instante.

### Cadenas más largas

Si hay tres funciones una dentro de otra, se multiplican **tres** pendientes (tres engranajes), y así sucesivamente. En una red neuronal hay **cientos** de funciones encadenadas, y la regla de la cadena permite calcular la pendiente de todas ellas multiplicando pendientes pequeñas, una detrás de otra. A eso se le llama **retropropagación** (NB18, NB19).
"""),

md(r"""## 4 · La regla del producto: el rectángulo

¿Y si dos funciones se **multiplican**, como x² · x³ o x · e^x? La pendiente **no** es el producto de las pendientes. La regla es:

```
   pendiente de f·g  =  f'·g  +  f·g'
```

La intuición es un **rectángulo** de lados f y g, cuya área es f·g. Si los dos lados crecen un poquito, el área crece por dos sitios: una tira a lo largo (lo que crece f, por el otro lado g: f'·g) y otra tira a lo ancho (f por lo que crece g: f·g'). (Y una esquinita minúscula, que con cambios pequeñitos es despreciable.)

```
   ┌────────────── g ──────────────┬─┐
   │                               │ │  ← f·g' (crece g)
   f          área f·g             │ │
   │                               │ │
   ├───────────────────────────────┼─┤
   └─── f'·g (crece f) ────────────┴─┘
```

Ejemplo: x² · x³. Con la regla: 2·x · x³ + x² · 3·x² = 2·x⁴ + 3·x⁴ = **5·x⁴**. Y efectivamente, x² · x³ = x⁵, cuya pendiente es 5·x⁴ ✓.
"""),

code(r"""comprobar(lambda x: x ** 2 * x ** 3, lambda x: 2 * x * x ** 3 + x ** 2 * 3 * x ** 2)"""),

md(r"""## 5 · La exponencial y el logaritmo

### e^x es su propia pendiente

La función exponencial e^x (NB15b) tiene una propiedad única, que es la razón de que e sea tan especial: **su pendiente es ella misma**.

```
   la pendiente de eˣ es eˣ
```

En cada punto, la curva sube exactamente tanto como lo alta que está. Es la definición matemática de "crecer en proporción a lo que ya hay" (NB15b). Con la regla de la cadena salen todas sus variantes:

- e^(k·x) → e^(k·x) · **k** (la de dentro, k·x, tiene pendiente k). Por ejemplo, e^(−t/τ) → **−(1/τ)·e^(−t/τ)**: el decaimiento del NB15b baja más deprisa al principio, cuando queda mucho.
- La **campana** e^(−x²) → e^(−x²) · (−2·x) = **−2·x·e^(−x²)**: pendiente 0 en el centro (la cima), positiva a la izquierda, negativa a la derecha.
"""),

code(r"""print("eˣ:")
comprobar(np.exp, np.exp)
print("e^(−x²):")
comprobar(lambda x: np.exp(-x ** 2), lambda x: -2 * x * np.exp(-x ** 2))"""),

md(r"""### La pendiente del logaritmo es 1/x

Para el logaritmo natural (NB15b):

```
   la pendiente de ln(x) es  1/x
```

Para x grande, la pendiente es pequeña (el logaritmo crece cada vez más despacio); para x cercano a 0, enorme (cae en picado hacia −∞).

Y con la regla de la cadena sale una forma que aparecerá en el corazón del aprendizaje por refuerzo (NB29, NB33):

```
   la pendiente de ln(f(x)) es  f'(x) / f(x)          ("la pendiente de f, dividida por f")
```

Es decir: la pendiente del **logaritmo** de algo es la pendiente de ese algo **dividida por su valor**. Mide el cambio **relativo** (en proporción, como un porcentaje, NB03b), no el absoluto.
"""),

code(r"""print("ln(x):")
comprobar(np.log, lambda x: 1 / x, puntos=(0.5, 1.0, 4.0))
print("ln(x² + 1)  →  2x / (x² + 1):")
comprobar(lambda x: np.log(x ** 2 + 1), lambda x: 2 * x / (x ** 2 + 1))"""),

md(r"""### La rampa: 0 o 1

Y una muy sencilla que usaremos en el NB19: la **rampa** (ReLU, NB15b), max(0, x). A la izquierda del codo es plana (**pendiente 0**); a la derecha, una recta de inclinación 1 (**pendiente 1**). Justo en el codo, la pendiente no está bien definida (cambia de golpe), pero en la práctica se toma 0 o 1 y no pasa nada.
"""),

md(r"""## 6 · La tabla de las reglas

| Función | Su pendiente | Ejemplo |
|---|---|---|
| c (constante) | 0 | 5 → 0 |
| m·x + b | m | 3·x + 1 → 3 |
| xⁿ | n·xⁿ⁻¹ | x³ → 3·x²;  1/x → −1/x² |
| c·f(x) | c·f'(x) | 5·x² → 10·x |
| f + g | f' + g' | x² + x → 2·x + 1 |
| f(g(x)) **(cadena)** | f'(g(x)) · g'(x) | (x − 3)² → 2·(x − 3) |
| f · g **(producto)** | f'·g + f·g' | x²·x³ → 5·x⁴ |
| eˣ | eˣ | e^(k·x) → k·e^(k·x) |
| ln(x) | 1/x | ln(f) → f'/f |
| rampa(x) | 0 (izquierda) o 1 (derecha) | |

Con estas diez reglas se pueden derivar a mano casi todas las funciones del curso. (Las de **seno** y **coseno**, que necesitarán los péndulos y los muelles, las verás cuando lleguen esas funciones, en el NB39b.)
"""),

md(r"""## 7 · La pendiente de la pendiente: la segunda derivada

### Derivar dos veces

La derivada de una función es otra función... que también tiene pendiente. A la pendiente de la pendiente se le llama **segunda derivada**, y se escribe **f''(x)** ("f dos primas"). Por ejemplo, para x³: la primera derivada es 3·x², y la segunda, 6·x.

### Qué significa: la aceleración

Ya lo viste en el NB16 sin este nombre: la **velocidad** es la pendiente de la **posición**, y la **aceleración** es la pendiente de la velocidad. Así que **la aceleración es la segunda derivada de la posición**. En la caída libre (NB04b), la posición es h = 2 − ½·g·t²; su primera derivada (la velocidad) es −g·t, y su segunda (la aceleración), **−g**: constante, la gravedad. Toda la física de los robots (NB37 en adelante) se escribe con segundas derivadas: "la fuerza decide la **aceleración**".

### Cima o valle

La segunda derivada también dice **qué forma** tiene la curva:

- **f'' > 0**: la pendiente va **aumentando**: la curva se dobla hacia **arriba**, como un cuenco (un **valle**).
- **f'' < 0**: la pendiente va **disminuyendo**: se dobla hacia **abajo**, como una montaña (una **cima**).

En un punto donde la pendiente es 0 (NB17: en lo alto o en lo bajo), la segunda derivada te dice si es una cima (f'' < 0) o un valle (f'' > 0). En la colina −(x − 3)², f' = −2·(x − 3) se anula en x = 3, y f'' = **−2** < 0: es una cima ✓.

### El método de Newton (una idea para más adelante)

El ascenso por gradiente del NB17 da pasos de tamaño fijo (la tasa). Pero si conoces también la segunda derivada (cuánto se curva el terreno), puedes **calcular** el tamaño de paso ideal: donde el terreno se curva mucho, pasos cortos; donde casi no se curva, pasos largos. Esa es la idea del **método de Newton**, mucho más rápido cerca de la cima. Lo verás nombrado en el NB46 (para la cinemática inversa) y en el NB48 (uno de los "solucionadores" de MuJoCo usa segundas derivadas).
"""),

code(r"""f = lambda x: x ** 3
f1 = lambda x: pendiente(f, x)              # primera derivada (numérica)
f2 = lambda x: pendiente(f1, x, h=1e-3)     # segunda derivada: la pendiente de la pendiente
for x in [-1.0, 0.5, 2.0]:
    print(f"x = {x:+.1f}: f'' numérica {f2(x):+.4f} | regla 6·x = {6 * x:+.4f}")"""),

md(r"""(Para la segunda derivada numérica usamos un h más grande, 0,001: al derivar dos veces, los errores de los decimales se amplifican, NB16, y un h demasiado pequeño los haría visibles.)

## 8 · Derivadas parciales

En el NB17 viste las **derivadas parciales**: si una función depende de **varias** ruedecillas, f(x, y), su pendiente "respecto a x" se calcula moviendo **solo x** y dejando y quieta. Ahora puedes calcularlas con las reglas: **se deriva respecto a una letra tratando las demás como si fueran números fijos**. Se escribe con una "d" redondeada, **∂f/∂x**.

Por ejemplo, f(x, y) = x²·y + 3·y:

- **∂f/∂x**: y es un número fijo. x²·y es "un número (y) por x²" → 2·x·y. Y 3·y no tiene x: es una constante → 0. Total: **∂f/∂x = 2·x·y**.
- **∂f/∂y**: x es un número fijo. x²·y es "un número (x²) por y" → x². Y 3·y → 3. Total: **∂f/∂y = x² + 3**.

Juntas forman el **gradiente** (NB17): la flecha (2·x·y, x² + 3) que apunta hacia donde la función sube más deprisa.
"""),

code(r"""f = lambda x, y: x ** 2 * y + 3 * y
x, y = 1.5, -2.0
print("∂f/∂x numérica:", pendiente(lambda t: f(t, y), x), "| regla 2·x·y:", 2 * x * y)
print("∂f/∂y numérica:", pendiente(lambda t: f(x, t), y), "| regla x² + 3:", x ** 2 + 3)"""),

md(r"""(El truco para la parcial numérica: `lambda t: f(t, y)` es una función de **una** sola letra, t, con y fija: justo "mover solo x". Es la "función envoltorio" del NB17.)
"""),

md(r"""## 9 · Resumen de la lección

1. La **derivada** f'(x) (o df/dx) es la función pendiente. Las **reglas** la dan exacta, sin calcular la función dos veces.
2. Constante → 0; recta m·x + b → m; **xⁿ → n·xⁿ⁻¹** (vale para 1/x y √x); c·f → c·f'; suma → suma de pendientes.
3. **Regla de la cadena** (engranajes): f(g(x)) → f'(g(x))·g'(x). ¡No olvides la pendiente de lo de dentro (el −1 de (3 − x)²)! Base de la retropropagación.
4. **Producto** (el rectángulo): f·g → f'·g + f·g'.
5. **eˣ es su propia pendiente**; e^(k·x) → k·e^(k·x); campana e^(−x²) → −2·x·e^(−x²).
6. **ln(x) → 1/x**; **ln(f) → f'/f** (cambio relativo). Rampa → 0 o 1.
7. **Segunda derivada** f'': pendiente de la pendiente. La aceleración es la segunda derivada de la posición. f'' < 0 → cima; f'' > 0 → valle. Método de Newton.
8. **Derivadas parciales** ∂f/∂x: deriva respecto a una letra con las demás fijas. Juntas, el gradiente.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Derivada, f'(x), df/dx** | La función que da la pendiente de f en cada punto. |
| **Regla de la cadena** | La pendiente de una función dentro de otra es el producto de sus pendientes. |
| **Regla del producto** | (f·g)' = f'·g + f·g'. |
| **Segunda derivada, f''(x)** | La pendiente de la pendiente: cómo se curva una función. |
| **Método de Newton** | Buscar cimas o valles usando también la segunda derivada. |
| **Derivada parcial, ∂f/∂x** | Pendiente respecto a una letra, con las demás fijas. |
"""),

md(r"""## 10 · Ejercicios

Calcula cada pendiente **a mano** con las reglas, y después compruébala con `comprobar`.

**E1.** f(x) = 3·x⁴ − x² + 5.

**E2.** f(x) = (x² + 1)³. (Cadena: la de fuera es el cubo.)

**E3.** f(x) = (5 − 2·x)². ¡Cuidado con lo de dentro!

**E4.** f(x) = x · eˣ. (Producto.)

**E5.** f(x) = e^(−(x − 1)² / 2). (La campana del NB15b centrada en 1.)

**E6.** f(x) = ln(3·x). ¿Por qué sale lo mismo que la pendiente de ln(x)? (Pista: la regla del producto de los logaritmos, NB15b.)

**E7.** El error cuadrático de una predicción, como el que usarás en el NB18, es E(w) = (w·x − y)², donde w es la ruedecilla, y x e y son números fijos. Calcula dE/dw.

**E8.** Para f(x, y) = x·y² − 2·x, calcula ∂f/∂x y ∂f/∂y, y el gradiente en el punto (1, 2).
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

Término a término: 3·4·x³ − 2·x + 0 = **12·x³ − 2·x**.

```python
comprobar(lambda x: 3 * x ** 4 - x ** 2 + 5, lambda x: 12 * x ** 3 - 2 * x)
```
</details>

<details>
<summary>▶ Solución E2</summary>

Fuera, el cubo: u³ → 3·u², en u = x² + 1: 3·(x² + 1)². Dentro, x² + 1 → 2·x. Multiplicando: **6·x·(x² + 1)²**.

```python
comprobar(lambda x: (x ** 2 + 1) ** 3, lambda x: 6 * x * (x ** 2 + 1) ** 2)
```
</details>

<details>
<summary>▶ Solución E3</summary>

Fuera: 2·(5 − 2·x). Dentro, 5 − 2·x tiene pendiente **−2**. Total: 2·(5 − 2·x)·(−2) = **−4·(5 − 2·x)**.

```python
comprobar(lambda x: (5 - 2 * x) ** 2, lambda x: -4 * (5 - 2 * x))
```
</details>

<details>
<summary>▶ Solución E4</summary>

f = x (pendiente 1), g = eˣ (pendiente eˣ). Producto: 1·eˣ + x·eˣ = **(1 + x)·eˣ**.

```python
comprobar(lambda x: x * np.exp(x), lambda x: (1 + x) * np.exp(x))
```
</details>

<details>
<summary>▶ Solución E5</summary>

Fuera, e^u → e^u. Dentro, u = −(x − 1)²/2, cuya pendiente es −2·(x − 1)/2 = −(x − 1). Total: **−(x − 1)·e^(−(x − 1)²/2)**. Vale 0 en x = 1 (la cima de la campana), como debe ser.

```python
comprobar(lambda x: np.exp(-(x - 1) ** 2 / 2), lambda x: -(x - 1) * np.exp(-(x - 1) ** 2 / 2))
```
</details>

<details>
<summary>▶ Solución E6</summary>

Con la cadena: (1/(3·x)) · 3 = **1/x**. Sale lo mismo que ln(x) porque ln(3·x) = ln(3) + ln(x) (NB15b), y ln(3) es una **constante** (pendiente 0): las dos funciones son la misma curva, solo desplazada hacia arriba (NB15b), así que tienen la misma pendiente en cada punto.

```python
comprobar(lambda x: np.log(3 * x), lambda x: 1 / x, puntos=(0.5, 1.0, 4.0))
```
</details>

<details>
<summary>▶ Solución E7</summary>

Fuera, el cuadrado: 2·(w·x − y). Dentro, w·x − y como función de **w** (x e y son números fijos) es una recta de pendiente **x**. Total: **dE/dw = 2·(w·x − y)·x**: "dos por el error por la entrada". En el NB18 encontrarás exactamente esta fórmula (con una media de muchos ejemplos), con los engranajes como explicación.

```python
x_dato, y_dato = 2.0, 3.0
comprobar(lambda w: (w * x_dato - y_dato) ** 2, lambda w: 2 * (w * x_dato - y_dato) * x_dato)
```
</details>

<details>
<summary>▶ Solución E8</summary>

- ∂f/∂x (y fija): y² − 2.
- ∂f/∂y (x fija): x · 2·y = 2·x·y.

En (1, 2): ∂f/∂x = 4 − 2 = **2**; ∂f/∂y = 2·1·2 = **4**. Gradiente: **(2, 4)**.

```python
f = lambda x, y: x * y ** 2 - 2 * x
print(pendiente(lambda t: f(t, 2.0), 1.0), pendiente(lambda t: f(1.0, t), 2.0))    # 2.0  4.0
```
</details>
"""),

md(r"""## 11 · 🛠 Práctica en MuJoCo: la energía de una pelota y de un péndulo

Hoy has aprendido reglas que dan pendientes **exactas** sobre el papel. La pregunta de un ingeniero es: ¿y el simulador está de acuerdo? Vamos a comprobarlo con dos
experimentos en MuJoCo:

1. Una **pelota que cae**. Con las reglas de las potencias sacarás su velocidad y su aceleración a partir de la fórmula de la altura (NB04b), y MuJoCo te dirá si aciertas.
2. Su **energía**. Es una idea nueva, muy importante en física, que MuJoCo sabe calcular. Con la regla de la cadena descubrirás que, mientras cae, la energía **no
   cambia**: su pendiente es 0. Y luego lo verás en un **péndulo**, donde el rozamiento sí se la come, y a qué ritmo.
"""),

md(r"""### Paso 1 · ¿Qué es la energía?

Antes de tocar código, la idea. La **energía** es como la "batería" de un objeto: cuánto trabajo podría hacer. Un objeto que se mueve tiene dos tipos:

- **Energía de altura** (los físicos la llaman **potencial**): una pelota en lo alto "guarda" energía, que se convierte en velocidad si la sueltas. Vale
  **m · g · h**: masa por gravedad por altura. Una pelota de 0,5 kg a 2 m de altura: 0,5 · 9,81 · 2 = **9,81** (se mide en **julios**).
- **Energía de movimiento** (la **cinética**): cuanto más deprisa va, más tiene. Vale **½ · m · v²**: la mitad de la masa por la velocidad al cuadrado. Parada, 0.

Cuando la pelota cae, pierde altura y gana velocidad: una energía se convierte en la otra, como agua que pasa de un vaso a otro. ¿Se pierde algo por el camino? Si
no hay rozamiento, los físicos dicen que **no**: la suma se **conserva**. Lo vas a comprobar.

### Paso 2 · Una pelota que lleva la cuenta de su energía

Un plano MJCF de una pelota de 0,5 kg que solo puede moverse arriba y abajo (una junta `slide` vertical, como el carro del palo de escoba pero de pie). Dos
novedades, las dos en `<option>`:

- `<flag energy="enable"/>` le pide a MuJoCo que, en cada paso, calcule la energía y la guarde en **`datos.energy`**: dos números, `[potencial, cinética]`. (Por
  dentro usa dos funciones suyas, `mj_energyPos` y `mj_energyVel`: una para cada tipo.)
- `integrator="RK4"` le pide una forma de dar los pasitos **más precisa** que la normal. Con ella, la caída libre sale exacta, sin el pequeño error de la cadena de oro
  que viste en el NB16. (Qué es eso de "integrador" lo verás a fondo en el NB49; en el Reto 1 verás qué pasa sin él.)
"""),

code(r"""import mujoco
import taller

PELOTA = '''
<mujoco>
  <option timestep="0.01" integrator="RK4">
    <flag energy="enable"/>
  </option>
  <worldbody>
    <light pos="0 -2 4"/>
    <geom type="plane" size="2 2 0.1" rgba=".8 .9 .8 1"/>
    <body name="pelota" pos="0 0 0">
      <joint name="altura" type="slide" axis="0 0 1"/>
      <geom type="sphere" size="0.1" mass="0.5" rgba=".9 .2 .2 1" contype="0" conaffinity="0"/>
    </body>
  </worldbody>
</mujoco>
'''
modelo, datos = taller.cargar(PELOTA)
datos.qpos[0] = 2.0                     # la subimos a 2 metros
mujoco.mj_forward(modelo, datos)        # que MuJoCo recalcule todo en esa posición
print("Energía al empezar [potencial, cinética]:", datos.energy)"""),

md(r"""**[9,81, 0]**: justo el 0,5 · 9,81 · 2 que calculaste a mano, y nada de energía de movimiento (está quieta). (`mj_forward` recalcula todo, también la energía,
sin avanzar el tiempo: lo necesitamos porque hemos movido la pelota "a mano".)
"""),

md(r"""### Paso 3 · Grabar la caída

Dejamos caer la pelota **0,6 segundos** (60 pasitos) y apuntamos en arrays (NB15) el tiempo, la altura (`qpos`), la velocidad (`qvel`), la **aceleración**
(`datos.qacc`, que MuJoCo también te da) y las dos energías. Usamos 61 casillas: la casilla 0 es el instante inicial, sin dar ningún paso (por eso el `if n > 0`):
"""),

code(r"""tiempos = np.zeros(61)
alturas = np.zeros(61)
velocidades = np.zeros(61)
aceleraciones = np.zeros(61)
potencial = np.zeros(61)
cinetica = np.zeros(61)

for n in range(61):
    if n > 0:
        mujoco.mj_step(modelo, datos)
    tiempos[n] = datos.time
    alturas[n] = datos.qpos[0]
    velocidades[n] = datos.qvel[0]
    aceleraciones[n] = datos.qacc[0]
    potencial[n] = datos.energy[0]
    cinetica[n] = datos.energy[1]

print("Altura a los", round(tiempos[60], 2), "s:", round(alturas[60], 4), "m")"""),

md(r"""### Paso 4 · Las reglas contra MuJoCo

La fórmula de la caída libre (NB04b, y el apartado 7 de hoy) es **h(t) = 2 − ½ · 9,81 · t² = 2 − 4,905 · t²**. Con las reglas:

- **Velocidad = pendiente de la altura.** El 2 es una constante (pendiente 0); t² tiene pendiente 2·t, y el número de delante se queda: −4,905 · 2·t = **−9,81 · t**.
- **Aceleración = pendiente de la velocidad** (la segunda derivada de la altura). −9,81 · t es una recta: su pendiente es **−9,81**, siempre.

Tres instantes, fórmula contra simulador:
"""),

code(r"""print(" t   | altura MuJoCo  fórmula | velocidad MuJoCo  regla −9,81·t | aceleración MuJoCo")
for n in [20, 40, 60]:
    t = tiempos[n]
    print(f" {t:.1f} |   {alturas[n]:.4f}     {2 - 4.905 * t ** 2:.4f}  |     {velocidades[n]:.4f}        {-9.81 * t:.4f}      |     {aceleraciones[n]:.4f}")"""),

md(r"""**Coinciden en todas las cifras.** A los 0,6 s la pelota está a 0,2342 m, va a −5,886 m/s (hacia abajo), y su aceleración es −9,81: la gravedad. Lo que dicen
las reglas de las pendientes es exactamente lo que hace el simulador.
"""),

md(r"""### Paso 5 · La energía se conserva

Ahora la suma de las dos energías, en cada uno de los 61 instantes. Si se conserva, debería valer siempre 9,81:
"""),

code(r"""total = potencial + cinetica

plt.figure(figsize=(6, 3.5))
plt.plot(tiempos, potencial, label="de altura (potencial)")
plt.plot(tiempos, cinetica, label="de movimiento (cinética)")
plt.plot(tiempos, total, "k--", label="total")
plt.xlabel("tiempo (s)")
plt.ylabel("energía (julios)")
plt.legend()
plt.grid(alpha=0.3)
plt.show()
print("Energía total: mínima", round(total.min(), 6), "| máxima", round(total.max(), 6))"""),

md(r"""Una energía baja, la otra sube, y la línea discontinua de la suma se queda **plana en 9,81**: el agua pasa de un vaso al otro sin derramarse ni una gota.

### Paso 6 · La pendiente de la energía, con la regla de la cadena

¿Por qué se conserva? Las reglas de hoy lo explican. Llamemos U a la energía de altura y K a la de movimiento:

- **U = m · g · h.** m · g es un número (0,5 · 9,81 = 4,905), así que su pendiente es m · g · (pendiente de h) = 4,905 · (−9,81 · t) = **−48,118 · t**.
- **K = ½ · m · v².** Es una función dentro de otra: el **cuadrado** (fuera) de la **velocidad** (dentro). Regla de la cadena: ½ · m · **2·v** · (pendiente de v) =
  m · v · (−9,81). Con v = −9,81 · t: 0,5 · (−9,81 · t) · (−9,81) = **+48,118 · t**.

La pendiente de la suma es la suma de las pendientes (apartado 2): −48,118 · t + 48,118 · t = **0**. La energía total tiene pendiente cero en todo momento: no sube
ni baja. Lo comprobamos con la pendiente numérica, usando los datos grabados (h = un pasito, 0,01 s, a los dos lados):
"""),

code(r"""for n in [20, 40]:
    t = tiempos[n]
    pend_U = (potencial[n + 1] - potencial[n - 1]) / 0.02
    pend_K = (cinetica[n + 1] - cinetica[n - 1]) / 0.02
    pend_total = (total[n + 1] - total[n - 1]) / 0.02
    print(f"t = {t:.1f} s | U: medida {pend_U:+.4f}, regla {-48.118 * t:+.4f} | K: medida {pend_K:+.4f}, regla {48.118 * t:+.4f} | total: {pend_total:+.6f}")"""),

md(r"""A los 0,2 s, la energía de altura se va a −9,6236 julios por segundo y la de movimiento llega a +9,6236: lo que pierde una lo gana la otra, al ritmo exacto que
predice la regla de la cadena. Y la pendiente del total sale **+0,000000**: cero, hasta la sexta cifra decimal.
"""),

md(r"""### Paso 7 · El péndulo y el rozamiento

Ahora un **péndulo**: una bola de 1 kg colgada de una varilla de 1 m (sin peso) que gira en una bisagra a 1,5 m de altura. La soltamos a **60 grados**. El
`damping` de la bisagra es el rozamiento (NB15b): de momento, 0.
"""),

code(r"""PENDULO = '''
<mujoco>
  <option timestep="0.01" integrator="RK4">
    <flag energy="enable"/>
  </option>
  <worldbody>
    <light pos="0 -2 4"/>
    <geom type="plane" size="2 2 0.1" rgba=".8 .9 .8 1"/>
    <body name="bola" pos="0 0 1.5">
      <joint name="giro" type="hinge" axis="0 1 0" damping="0"/>
      <geom type="capsule" fromto="0 0 0 0 0 -1" size="0.02" mass="0" rgba=".4 .4 .4 1"/>
      <geom type="sphere" pos="0 0 -1" size="0.08" mass="1" rgba="1 .5 .1 1"/>
    </body>
  </worldbody>
</mujoco>
'''

def energia_del_pendulo(rozamiento):
    # Suelta el péndulo a 60 grados y devuelve la energía total y la velocidad de giro en 501 instantes (5 s).
    modelo, datos = taller.cargar(PENDULO)
    modelo.dof_damping[0] = rozamiento
    datos.qpos[0] = np.radians(60)
    mujoco.mj_forward(modelo, datos)
    energias = np.zeros(501)
    giros = np.zeros(501)
    for n in range(501):
        if n > 0:
            mujoco.mj_step(modelo, datos)
        energias[n] = datos.energy[0] + datos.energy[1]
        giros[n] = datos.qvel[0]
    return energias, giros

energias, giros = energia_del_pendulo(0)
print("Sin rozamiento: energía al empezar", round(energias[0], 5), "| mínima", round(energias.min(), 5), "| máxima", round(energias.max(), 5))"""),

md(r"""(`modelo.dof_damping[0]` es el damping de la bisagra, guardado en el modelo: así podemos cambiarlo sin reescribir el plano, como cambiabas la gravedad en el NB06.)

Sin rozamiento, el péndulo va y viene durante 5 segundos y la energía no se mueve de **9,81**. (¿Por qué 9,81? La bola empieza a 1,5 − 0,5 = 1 m de altura, porque
la varilla inclinada 60 grados "sube" medio metro, y 1 · 9,81 · 1 = 9,81.)

Ahora con un poco de rozamiento, **0,1**:
"""),

code(r"""energias, giros = energia_del_pendulo(0.1)
for n in [0, 100, 200, 500]:
    print(f"a los {n / 100:.0f} s: energía {energias[n]:.4f} julios")

plt.figure(figsize=(6, 3.5))
plt.plot(np.arange(501) * 0.01, energias)
plt.xlabel("tiempo (s)")
plt.ylabel("energía total (julios)")
plt.grid(alpha=0.3)
plt.show()"""),

md(r"""Ahora la energía **baja**: 9,81 → 9,33 → 8,90 → ... → 7,88 a los 5 s. El rozamiento se la come (la convierte en calor, que MuJoCo no cuenta). Fíjate en la forma
de la curva: **escalones**. Baja deprisa en unos momentos y casi nada en otros.

La física (lo verás en el NB38b) dice exactamente a qué ritmo: el rozamiento se come **b · ω²** julios por segundo, donde b es el damping y ω la velocidad de giro.
Es decir: **la pendiente de la energía es −b · ω²**. Comprobémoslo en tres instantes:
"""),

code(r"""for n in [50, 123, 200]:
    medida = (energias[n + 1] - energias[n - 1]) / 0.02
    print(f"t = {n / 100:.2f} s | giro {giros[n]:+.3f} rad/s | pendiente medida {medida:+.4f} | −b·ω² = {-0.1 * giros[n] ** 2:+.4f}")"""),

md(r"""Coinciden (hasta la tercera cifra; la pequeña diferencia es la pendiente numérica, que usa pasitos de 0,01 s). Y la fórmula explica los escalones: ω² es **grande**
cuando el péndulo pasa por abajo a toda velocidad (la energía cae deprisa) y **0** en los extremos, donde se para un instante para darse la vuelta (la energía
casi no cambia). Además, ω² nunca es negativo: **el rozamiento nunca da energía**, solo la quita.

Y para verlo, el péndulo con rozamiento (cada vez llega menos alto):
"""),

code(r"""modelo, datos = taller.cargar(PENDULO)
modelo.dof_damping[0] = 0.1
datos.qpos[0] = np.radians(60)
taller.video(modelo, datos, segundos=5, nombre="nb17b_pendulo", seguir=False, distancia=3.5);"""),

md(r"""### Tus retos

**Reto 1 · Sin RK4.** En el plano de la pelota, borra `integrator="RK4"` (MuJoCo usará su forma normal de dar pasitos, la del NB16) y repite los Pasos 2 a 5. ¿Se
conserva la energía? ¿Cuánto vale al final?

**Reto 2 · Lanzada hacia arriba.** Repite la pelota (con RK4) dándole además `datos.qvel[0] = 5.0` antes del `mj_forward`: lanzada hacia arriba a 5 m/s. ¿Cuánta energía
tiene al empezar? ¿Se conserva? Con las reglas, ¿cuál es ahora la fórmula de la velocidad?

**Reto 3 · Más rozamiento.** Llama a `energia_del_pendulo(0.3)`. ¿Cuánta energía queda a los 5 s? ¿Sigue valiendo la regla −b · ω²?

<details>
<summary>▶ Solución Reto 1</summary>

```python
modelo, datos = taller.cargar(PELOTA.replace(' integrator="RK4"', ''))
```

(`.replace` cambia un trozo de texto por otro: lo verás en el NB20. También puedes borrarlo a mano en el plano.) Después, las mismas celdas. La energía total ya **no**
se conserva: baja poquito a poco, de 9,81 a **9,668** a los 0,6 s (un 1,4 % menos). Y si calculas su pendiente con el Paso 6, sale **−0,2406** julios por segundo,
siempre la misma. No es un rozamiento (no hay): es el pequeño error de la forma normal de dar pasitos (la "pendiente hacia atrás" del NB16), que en cada pasito
coloca la pelota un poco más abajo de lo que dice la fórmula (a los 0,6 s, a 0,2048 m en vez de 0,2342). Comprobar la energía es la forma clásica de pillar
estos errores en un simulador. Con pasitos más pequeños, el error se reduce (NB49).
</details>

<details>
<summary>▶ Solución Reto 2</summary>

Al empezar: potencial 9,81 y cinética ½ · 0,5 · 5² = **6,25**: total **16,06**, y se queda en 16,06 todo el rato (se conserva). La altura es ahora
h = 2 + 5·t − 4,905·t², y con las reglas (suma, recta, potencia): **v = 5 − 9,81·t**. A los 0,4 s, 5 − 3,924 = 1,076 m/s, que es lo que da MuJoCo (aún sube, pero
ya despacio); a los 0,6 s ya baja: −0,886 m/s. La aceleración sigue siendo −9,81: la gravedad no sabe si la lanzaste.
</details>

<details>
<summary>▶ Solución Reto 3</summary>

```python
energias, giros = energia_del_pendulo(0.3)
print(round(energias[500], 4))
n = 50
print((energias[n + 1] - energias[n - 1]) / 0.02, -0.3 * giros[n] ** 2)    # −2,506 y −2,507
```

Con el triple de rozamiento queda bastante menos energía a los 5 s (**5,98 julios**, frente a 7,88), y la regla −b · ω² sigue cumpliéndose, ahora con b = 0,3.
</details>

### Qué has aprendido de MuJoCo hoy

- `<flag energy="enable"/>` hace que MuJoCo calcule en cada paso la energía en **`datos.energy`** = [potencial, cinética] (con `mj_energyPos` y `mj_energyVel`).
- **`datos.qacc`** es la aceleración: la segunda derivada de la posición. Con la pelota, −9,81 exactos.
- `integrator="RK4"` da pasitos más precisos; con el integrador normal, la energía de una caída libre se "escapa" un poquito (Reto 1).
- **`modelo.dof_damping`** es el rozamiento de cada junta, y se puede cambiar desde Python.
- Las reglas de las pendientes (potencias, cadena, suma) predicen exactamente lo que hace el simulador: la energía de una caída se conserva (pendiente 0) y el
  rozamiento se la come a ritmo −b · ω².

En la práctica del NB18 grabarás las **demostraciones** de un "maestro" que equilibra el palo de escoba de MuJoCo, y una neurona aprenderá a imitarlo.
"""),

md(r"""## 12 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **NB18**, el aprendizaje **supervisado**: enseñar a una máquina con ejemplos resueltos. Usarás la regla de la cadena (el ejercicio E7 de hoy) para calcular de golpe, y de forma exacta, hacia dónde mover sus ruedecillas.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB17b_reglas_de_las_pendientes.ipynb")
    build(out, cells, title="NB17b · Las reglas de las pendientes")
