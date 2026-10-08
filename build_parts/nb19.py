"""Construye NB19 · Redes neuronales: el codo que lo cambia todo (Parte 2 · Lección 8).

Un maestro con límite (su motor satura): empuje = recortar(−30·i, ±40), en 61
inclinaciones de −3 a 3. La neurona lineal no puede doblarse (mejor recta:
pendiente ≈ −18,4, pérdida 81,5). Apilar capas lineales sigue dando una recta
(engranajes: se multiplican). La activación ReLU = max(0, x): el codo. Con dos
codos, a mano, el maestro exacto: 40 − 30·relu(i + 4/3) + 30·relu(i − 4/3). Una
red 1 → 8 → 1 con ReLU entrenada con retropropagación escrita a mano (la regla de
la cadena con un eslabón más; la pendiente del codo es 0 o 1): tasa 0,003, 5.000
pasos, semilla 0 → pérdida ≈ 0. Con tasa 0,01 se atasca (~11: óptimo local, codos mal colocados).
Aproximación universal (idea). La red típica de un humanoide: 348 → 256 → 256 →
17 = 159.505 pesos.
Práctica en MuJoCo: el ctrlrange del palo de escoba recorta (pides 3 → 10 N);
el maestro real = clip(s, ±1) con s = (3; 0,8; 0,1; 0,2)·obs. Red a mano de 2
neuronas: −1 + ReLU(s + 1) − ReLU(s − 1), idéntica al maestro en ~2.800
demostraciones, aguanta 10 s desde 0,2-0,4 rad (vídeo). Neurona lineal: pesos
más cortos (2,55; 0,51...), pérdida 0,009, pero aguanta todo. Red 4 → 8 → 1
entrenada con la retropropagación a mano (tasa 0,2, 3.000 pasos, semilla 0):
pérdida 0,00019 (~50× menor) pero se cae desde 0,4 rad (2,15 s, vídeo): imitar
mejor ≠ conducir mejor fuera de los datos (2,6 % en el límite). Retos: semillas
1-3 aguantan todo, motor ±0,5 (cae desde 0,3), sin ReLU (orden constante 1).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB19 · Redes neuronales: el codo que lo cambia todo

**Parte 2 · Matemáticas y herramientas para robots — Lección 8**

> En el **NB18** una neurona aprendió a imitar al maestro del palo de escoba, bajando por la pendiente de su error con la **regla de la
> cadena**. Pero aquel maestro era fácil: su regla era una **suma con pesos** (−30 × inclinación − 8 × velocidad), justo lo que una neurona
> sabe hacer.

¿Y si el maestro hace algo **más complicado**? Una neurona sola es **lineal**: su respuesta, dibujada, es siempre una **recta**. No puede
**doblarse**. Y el mundo real está lleno de cosas que se doblan: motores que llegan a su límite, robots que reaccionan suave a un empujón
pequeño y fortísimo a uno grande, pasos que empiezan y terminan...

Hoy descubrirás el **ingrediente que falta**, el que anunciamos en el NB13 y el NB14: la **función de activación**. Es un "codo" diminuto que se
pone a la salida de cada neurona. Parece una tontería, pero es lo que convierte un montón de neuronas en una **red neuronal**: una máquina capaz
de aprender **casi cualquier forma**.

Al final de la lección habrás construido y entrenado tu propia red neuronal, escribiendo **a mano** su retropropagación. Y entenderás cómo es la
red que mueve a un humanoide de verdad.
"""),

md(r"""## 1 · Un maestro que no es una recta

Imagina un maestro más realista para el palo de escoba. Sigue la regla de siempre (empujar −30 por cada grado de inclinación), pero su motor
tiene un **límite**: nunca puede empujar más de 40 hacia ningún lado (NB01, NB11: los motores no son superhéroes). Así que, cuando la inclinación es
grande, el empuje se queda **plano** en el máximo. (Para poder dibujarlo, esta vez el maestro solo mira la inclinación.)

Le pedimos al maestro que diga qué empuje usaría en **61 inclinaciones** distintas, desde −3 hasta +3 grados. `np.linspace(-3, 3, 61)` fabrica
esos 61 números repartidos por igual entre −3 y 3 (*linspace* = "espacio lineal"), y `np.clip` (NB15) aplica el límite:
"""),

code(r"""import numpy as np
import matplotlib.pyplot as plt

inclinaciones = np.linspace(-3, 3, 61)
empujes_del_maestro = np.clip(-30 * inclinaciones, -40, 40)

plt.figure(figsize=(6, 3.5))
plt.plot(inclinaciones, empujes_del_maestro, "o", color="tab:orange", markersize=4, label="maestro")
plt.grid(True, alpha=0.4)
plt.xlabel("inclinación")
plt.ylabel("empuje")
plt.legend()
plt.show()"""),

md(r"""(`label` y `plt.legend()` ponen una pequeña leyenda que dice qué es cada cosa.)

La forma tiene **tres tramos**: plana arriba (empujando +40 cuando el palo se inclina mucho hacia un lado), una rampa en el medio (la regla −30 ×
inclinación), y plana abajo (−40). La rampa termina en dos **esquinas**, donde el motor llega a su límite: en ±4/3 de grado (porque 30 × 4/3 = 40).

¿Puede una neurona lineal imitar esto?
"""),

md(r"""## 2 · La neurona lineal no puede doblarse

Entrenemos una neurona lineal (un peso y un sesgo) con el descenso por gradiente del NB18, exactamente igual que entonces:"""),

code(r"""w, b = 0.0, 0.0
for paso in range(2000):
    errores = (w * inclinaciones + b) - empujes_del_maestro
    w = w - 0.05 * 2 * np.mean(errores * inclinaciones)
    b = b - 0.05 * 2 * np.mean(errores)

perdida_lineal = np.mean(((w * inclinaciones + b) - empujes_del_maestro) ** 2)
print("Peso aprendido:", round(w, 2), "| sesgo:", round(b, 2), "| pérdida:", round(perdida_lineal, 1))

plt.figure(figsize=(6, 3.5))
plt.plot(inclinaciones, empujes_del_maestro, "o", color="tab:orange", markersize=4, label="maestro")
plt.plot(inclinaciones, w * inclinaciones + b, color="tab:blue", label="neurona lineal")
plt.grid(True, alpha=0.4)
plt.legend()
plt.show()"""),

md(r"""La neurona ha hecho lo mejor que puede: una **recta** con pendiente −18,4, que pasa "por en medio" de los puntos. Pero no puede seguir la forma: se
queda **corta** en el centro (donde el maestro tiene pendiente −30) y **se pasa** en los extremos (donde el maestro está plano). La pérdida se atasca en
**81,5**, y por mucho que entrenemos, **no bajará más**: no hay ninguna recta que pase por esos tres tramos.

No es un problema de entrenar más, ni de la tasa. Es un **límite de la máquina**: una neurona lineal **solo sabe hacer rectas**.
"""),

md(r"""## 3 · ¿Y si apilamos neuronas lineales?

Una idea natural: si una neurona no basta, pongamos **muchas**, en **capas** (NB14). Una capa de 3 neuronas que reciben la inclinación, y luego una
neurona final que combina sus 3 salidas. Con pesos al azar, a ver qué forma sale:
"""),

code(r"""generador = np.random.default_rng(7)
pesos_capa1 = generador.uniform(-2, 2, size=3)       # 3 neuronas, cada una con 1 peso...
sesgos_capa1 = generador.uniform(-2, 2, size=3)      # ...y su sesgo
pesos_capa2 = generador.uniform(-2, 2, size=3)       # la neurona final combina las 3

def dos_capas_lineales(x):
    salida = 0
    for j in range(3):
        intermedio = pesos_capa1[j] * x + sesgos_capa1[j]     # neurona j de la capa 1
        salida = salida + pesos_capa2[j] * intermedio          # la capa 2 los combina
    return salida

for x in [-2, 0, 2]:
    pendiente_aqui = (dos_capas_lineales(x + 0.001) - dos_capas_lineales(x - 0.001)) / 0.002
    print("en x =", x, "-> pendiente", round(pendiente_aqui, 4))"""),

md(r"""La pendiente es **la misma en todas partes**. Es decir: ¡dos capas lineales siguen dando **una recta**!

¿Por qué? Por los **engranajes** del NB18. La entrada pasa por un eslabón que multiplica (y suma algo), y luego por otro que multiplica (y suma algo).
Multiplicar y luego multiplicar es lo mismo que **multiplicar una sola vez** (por el producto de los dos). Por muchas capas lineales que apiles, el
resultado es siempre equivalente a **una sola** capa lineal: una recta. Una torre de neuronas lineales es tan "tiesa" como una sola.

Para poder **doblarse**, necesitamos algo que **no sea** multiplicar y sumar.
"""),

md(r"""## 4 · El ingrediente que faltaba: el codo (ReLU)

El ingrediente es ridículamente sencillo. A la salida de cada neurona se le aplica esta regla:

> **Si el número es positivo, déjalo pasar. Si es negativo, conviértelo en 0.**

En Python: `max(0, x)`. Con NumPy, para un array entero: `np.maximum(0, x)`. Esta regla se llama **ReLU** (de las siglas en inglés de "unidad lineal
rectificada", un nombre muy pomposo para algo tan simple). Es una **función de activación**: decide cuánto se "activa" la neurona. Dibujémosla:
"""),

code(r"""def relu(x):
    return np.maximum(0, x)

xs = np.linspace(-3, 3, 61)
plt.figure(figsize=(5, 3))
plt.plot(xs, relu(xs), color="tab:green")
plt.grid(True, alpha=0.4)
plt.title("ReLU: max(0, x)")
plt.show()"""),

md(r"""Plana en 0 a la izquierda, rampa hacia arriba a la derecha, y en medio... **un codo**. Como una **bisagra** (NB01): dos tramos rectos unidos por una
articulación. Y esa bisagra es justo lo que no tenían las neuronas lineales: un sitio donde **doblarse**.

Recuerda también el perceptrón del NB13: "si el resultado es mayor que 0, se activa". La ReLU es su versión suave: si es mayor que 0, deja pasar **cuánto**;
si no, nada. Una neurona con activación funciona así:

```
   neurona con activación  =  ReLU( pesos · entradas + sesgo )
                                    └── la neurona del NB13 ──┘
```
"""),

md(r"""## 5 · Construir la curva del maestro con codos

¿Cómo se usan los codos para construir formas? Igual que con piezas de LEGO: cada neurona con ReLU aporta **un codo** en el sitio que digan su peso y su
sesgo, y la neurona final los **suma**, cada uno con su peso. Sumando codos colocados en sitios distintos se puede construir **cualquier forma hecha de
tramos rectos**.

De hecho, la forma del maestro se puede construir **exactamente** con solo **dos codos**. Te enseño la receta (pensada a mano):

```
   empuje = 40  −  30 × ReLU(inclinación + 4/3)  +  30 × ReLU(inclinación − 4/3)
```

- El **40** es el tramo plano de la izquierda.
- El primer codo "se enciende" en la inclinación −4/3 y, a partir de ahí, va restando 30 por cada grado: la **rampa**.
- El segundo codo se enciende en +4/3 y suma 30 por cada grado, **cancelando** la rampa: el tramo **plano** de la derecha.

Comprobémoslo:
"""),

code(r"""red_a_mano = 40 - 30 * relu(inclinaciones + 4/3) + 30 * relu(inclinaciones - 4/3)

print("Mayor diferencia con el maestro:", np.max(np.abs(red_a_mano - empujes_del_maestro)))"""),

md(r"""(`np.abs` quita el signo a cada número: es el "valor absoluto", la distancia al cero.)

La mayor diferencia es un número minúsculo (ruido de decimales): **¡imitación perfecta!** Con **dos** neuronas con ReLU y una neurona final, hemos hecho lo
que ninguna cantidad de neuronas lineales podía hacer. Eso es una **red neuronal**:

```
                      ┌─► neurona 1 → ReLU ─┐
   inclinación ───────┤                      ├──► neurona final ──► empuje
                      └─► neurona 2 → ReLU ─┘
      ENTRADA            CAPA OCULTA            SALIDA
```

A la capa del medio se le llama **capa oculta** (porque sus números no se ven desde fuera: ni son la entrada ni la salida). Y aquí está la gran pregunta:
yo he diseñado los pesos a mano, pensando. **¿Puede la red encontrarlos sola, aprendiendo de los ejemplos?**
"""),

md(r"""## 6 · La red aprende sola: retropropagación con un eslabón más

Vamos a construir una red con **8 neuronas** en la capa oculta (más de las 2 necesarias, para darle margen), empezar con pesos **al azar**, y entrenarla con
descenso por gradiente, como en el NB18. Solo necesitamos las pendientes de **todos** los pesos. Y para eso, la **regla de la cadena** (NB18), con la cadena un
poco más larga.

Para un peso de la **capa oculta** (por ejemplo, el peso de entrada de la neurona j), la cadena de engranajes es:

```
   peso ──► z (lo que suma la neurona) ──► ReLU(z) ──► predicción ──► error ──► error²
            × inclinación                  × (0 o 1)    × peso de        × 1       × 2 × error
                                                          salida de j
```

Todos los eslabones ya los conoces, menos uno: **la pendiente de la ReLU**. Y es facilísima, mirando su dibujo: a la izquierda del codo es plana (pendiente
**0**), y a la derecha es una rampa de pendiente **1**. Así que:

> **pendiente de la ReLU = 1 si la neurona estaba "encendida" (z > 0), y 0 si estaba "apagada".**

Tiene un sentido precioso: si una neurona estaba apagada para un ejemplo, **no influyó** en la predicción, así que no tiene culpa de ese error y sus pesos de
entrada no se tocan. Multiplicando los eslabones, para cada ejemplo:

```
   pendiente del peso de entrada de j = 2 × error × (peso de salida de j) × (1 si encendida, si no 0) × inclinación
   pendiente del sesgo de j           = 2 × error × (peso de salida de j) × (1 si encendida, si no 0)
   pendiente del peso de salida de j  = 2 × error × ReLU(z de j)
```

(y luego, la **media** sobre todos los ejemplos).

### Primero, con una sola neurona y un solo ejemplo

Antes de lanzarnos con 8 neuronas y 61 ejemplos, comprobemos la cadena en el caso más pequeño posible: **una** neurona oculta y **un** ejemplo inventado. La
inclinación es 5, el maestro querría un empuje de −20, y los pesos son números cualesquiera. Calculamos la pendiente del peso de entrada con la fórmula, eslabón
a eslabón:
"""),

code(r"""x, objetivo = 5.0, -20.0                     # un ejemplo inventado
w_entrada, b_oculto, w_salida, b_salida = 0.5, -1.0, 2.0, 0.0

z = w_entrada * x + b_oculto                    # lo que suma la neurona: 1,5
activacion = relu(z)                            # encendida: 1,5
prediccion_1 = w_salida * activacion + b_salida # 3,0
error_1 = prediccion_1 - objetivo               # 23,0
encendida_1 = 1 if z > 0 else 0

formula = 2 * error_1 * w_salida * encendida_1 * x
print("pendiente con la cadena:", formula)"""),

md(r"""2 × 23 × 2 × 1 × 5 = **460**. ¿Es verdad? Comprobémoslo "a lo bruto", como en el NB16: movemos el peso de entrada un poquito a cada lado y miramos cuánto cambia el
error al cuadrado:
"""),

code(r"""def error_cuadrado(w):
    return (w_salida * relu(w * x + b_oculto) + b_salida - objetivo) ** 2

h = 0.0001
print("pendiente medida:      ", (error_cuadrado(w_entrada + h) - error_cuadrado(w_entrada - h)) / (2 * h))"""),

md(r"""**460** también. La cadena funciona con la ReLU dentro. (Prueba a cambiar `b_oculto` a −3: la neurona queda apagada, z < 0, y las dos pendientes valen **0**: un
peso que no influyó no tiene culpa.)

Ahora sí: lo mismo para 8 neuronas y los 61 ejemplos a la vez. Lo escribimos con un bucle sobre las 8 neuronas (NumPy hace los 61 ejemplos a la vez). Es la celda
más larga del curso hasta ahora, pero cada línea es algo que ya conoces; léela con los comentarios:
"""),

code(r"""ocultas = 8
generador = np.random.default_rng(0)
pesos_entrada = generador.uniform(-1, 1, size=ocultas)     # un peso por neurona oculta
sesgos_ocultos = generador.uniform(-1, 1, size=ocultas)    # un sesgo por neurona oculta
pesos_salida = generador.uniform(-1, 1, size=ocultas)      # cómo combina la salida a cada una
sesgo_salida = 0.0

def predecir(x):
    total = sesgo_salida
    for j in range(ocultas):
        total = total + pesos_salida[j] * relu(pesos_entrada[j] * x + sesgos_ocultos[j])
    return total

tasa = 0.003
historial = []
for paso in range(5000):
    # 1. hacia delante: lo que suma cada neurona (z), su activación, y la predicción
    zs = []
    activaciones = []
    for j in range(ocultas):
        z = pesos_entrada[j] * inclinaciones + sesgos_ocultos[j]
        zs.append(z)
        activaciones.append(relu(z))
    prediccion = sesgo_salida
    for j in range(ocultas):
        prediccion = prediccion + pesos_salida[j] * activaciones[j]
    errores = prediccion - empujes_del_maestro
    historial.append(np.mean(errores ** 2))

    # 2. hacia atrás: la regla de la cadena para cada neurona (la retropropagación)
    for j in range(ocultas):
        encendida = zs[j] > 0                                    # True/False para cada ejemplo (vale 1 o 0)
        culpa = 2 * errores * pesos_salida[j] * encendida        # la parte común de la cadena
        pendiente_entrada = np.mean(culpa * inclinaciones)
        pendiente_sesgo = np.mean(culpa)
        pendiente_salida = np.mean(2 * errores * activaciones[j])
        pesos_entrada[j] = pesos_entrada[j] - tasa * pendiente_entrada
        sesgos_ocultos[j] = sesgos_ocultos[j] - tasa * pendiente_sesgo
        pesos_salida[j] = pesos_salida[j] - tasa * pendiente_salida
    sesgo_salida = sesgo_salida - tasa * np.mean(2 * errores)

print("Pérdida al empezar:", round(historial[0], 1))
print("Pérdida al terminar:", round(historial[-1], 3))
print("(La neurona lineal se quedaba en", round(perdida_lineal, 1), ")")"""),

md(r"""(Un detalle: `encendida` es un array de `True` y `False`, uno por ejemplo. Al multiplicarlo por números, Python trata `True` como **1** y `False` como **0**:
justo la pendiente de la ReLU.)

**De 1.118 a prácticamente 0.** La red ha aprendido a imitar al maestro **perfectamente**, algo que la neurona lineal (atascada en 81,5) jamás podría. Y lo ha
hecho **sola**, desde pesos al azar, con la regla de la cadena y el descenso por gradiente. Miremos el resultado:
"""),

code(r"""plt.figure(figsize=(11, 3.5))

plt.subplot(1, 2, 1)
plt.plot(inclinaciones, empujes_del_maestro, "o", color="tab:orange", markersize=4, label="maestro")
plt.plot(inclinaciones, w * inclinaciones + b, color="tab:blue", label="neurona lineal")
plt.plot(inclinaciones, predecir(inclinaciones), color="tab:red", linewidth=2, label="red neuronal")
plt.grid(True, alpha=0.4)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(historial, color="tab:red")
plt.yscale("log")
plt.grid(True, alpha=0.4)
plt.title("curva de aprendizaje de la red")
plt.xlabel("paso")

plt.show()"""),

md(r"""A la izquierda, la red (en rojo) pasa **exactamente** por los puntos del maestro, con sus dos esquinas, mientras la neurona lineal (en azul) se queda tiesa. A la
derecha, la curva de aprendizaje (en escala logarítmica, NB18): baja y baja hasta casi cero.

**Acabas de entrenar una red neuronal escribiendo tú mismo su retropropagación.** La mayoría de la gente que usa redes neuronales nunca lo ha hecho a mano: usa
bibliotecas que lo hacen solas (como PyTorch, que aprenderemos más adelante). Tú ya sabes qué hacen por dentro.
"""),

md(r"""### Cuidado: a veces la red se atasca

Entrenar redes neuronales no siempre sale tan bien. Si repites el entrenamiento con una tasa un poco más alta, **0,01** (está en los ejercicios), la
pérdida **se queda atascada en torno a 11**, en vez de bajar a 0.

¿Qué pasa? Con pasos más bruscos al principio, los codos de las neuronas se colocan en **sitios poco útiles** (por ejemplo, varios codos casi en el mismo
lugar, y ninguno en una de las dos esquinas que hacen falta). Desde ahí, cualquier pequeño cambio empeora un poco las cosas antes de mejorarlas, y el
descenso por gradiente, que solo ve la pendiente bajo sus pies, **no sabe salir**. ¿Te suena? Es un **óptimo local** (NB04, NB17): un valle que no es el
más profundo.

Hay otro problema famoso, emparentado: las **neuronas muertas**. Si una neurona recibe un empujón tan fuerte que queda **apagada para todos los ejemplos**,
su pendiente es siempre 0 (la ReLU es plana a la izquierda), sus pesos ya no se mueven nunca, y la red pierde ese codo para siempre.

Las soluciones de los profesionales: tasas más prudentes, mejores formas de elegir los pesos iniciales, más neuronas de las estrictamente necesarias (para tener
codos de sobra), y variantes de la ReLU que no son del todo planas a la izquierda. Lo importante: **entrenar redes es un poco arte**, y la curva de aprendizaje es
tu mejor amiga para darte cuenta de que algo va mal.

## 7 · ¿Hasta dónde llega esto?

Con 2 codos construimos una forma de 3 tramos. Con más codos, formas más complicadas: cada codo nuevo añade una "esquina" donde la curva puede cambiar de
dirección. Con **suficientes** codos, se puede imitar **casi cualquier curva** tan bien como se quiera, igual que se puede dibujar un círculo con muchos trocitos
de recta muy cortos.

Los matemáticos lo demostraron en los años 80-90 con un resultado que se conoce como **teorema de aproximación universal**: una red con una capa oculta de
neuronas con activación puede aproximar casi cualquier función, si tiene neuronas suficientes. En la práctica, en vez de una capa oculta enorme, se usan
**varias capas** (redes "profundas", de ahí el nombre **aprendizaje profundo**, *deep learning*), que aprenden formas complicadas con muchas menos neuronas.

Y ahora une todas las piezas de la Parte 2:

- La **observación** es un vector (NB12). Cada **neurona** hace un producto escalar más un sesgo (NB13). Una **capa** es una matriz de pesos (NB14), y NumPy la
  calcula de golpe (NB15).
- Entre capa y capa va la **ReLU**: el codo que permite doblarse (hoy).
- Los pesos se ajustan **bajando por la pendiente** de la pérdida (NB16-17), calculando todas las pendientes de golpe con la **regla de la cadena** (NB18-19).
"""),

md(r"""## 8 · La red de un humanoide de verdad

¿Cómo es la red neuronal que controla un humanoide entrenado con aprendizaje por refuerzo? Muy a menudo, algo así (las medidas exactas cambian de un proyecto a
otro, pero el tamaño típico es este):

```
   observación ──► capa 1 ──► ReLU ──► capa 2 ──► ReLU ──► capa de salida ──► acciones
     (348)        (256)                 (256)                    (17)
```

Contemos sus ruedecillas, con la regla del NB14 (salidas × entradas + salidas):
"""),

code(r"""capa1 = 256 * 348 + 256
capa2 = 256 * 256 + 256
capa_salida = 17 * 256 + 17
print("Capa 1:", capa1, "| Capa 2:", capa2, "| Salida:", capa_salida)
print("Ruedecillas en total:", capa1 + capa2 + capa_salida)"""),

md(r"""**159.505 ruedecillas.** Frente a las 2 del palo de escoba, las 782 de la política lineal (NB14) o las 25 de la red de hoy (8 + 8 + 8 + 1).

Es una red "pequeña" para los estándares actuales (las redes que generan texto o imágenes tienen **miles de millones**), y sin embargo es capaz de aprender a
mantener en equilibrio y hacer andar a un cuerpo de 17 motores. Y todas sus ruedecillas se ajustan exactamente como hoy: hacia delante para predecir, hacia atrás
con la regla de la cadena para repartir la culpa, y un pasito cuesta abajo. Solo que hechas por una biblioteca, a toda velocidad, millones de veces.

Ya tienes todas las piezas matemáticas. Lo que falta es la última: cómo se calcula "la pérdida" cuando **no hay un maestro**, solo una recompensa. Eso es el
**aprendizaje por refuerzo** de verdad, y hacia allí vamos.
"""),

md(r"""## 9 · Resumen de la lección

1. Una neurona lineal (y cualquier torre de capas lineales, porque multiplicar y multiplicar es multiplicar) **solo hace rectas**. Con el maestro que satura, se
   atasca en una pérdida de 81,5.
2. La **función de activación ReLU**, max(0, x), añade un **codo** a cada neurona. Sumando codos se construyen formas con esquinas: con **dos**, a mano, el maestro
   **exacto**.
3. Una **red neuronal**: entrada → **capa oculta** con ReLU → salida. Se entrena con descenso por gradiente y **retropropagación** (la regla de la cadena con un
   eslabón más: la pendiente de la ReLU es **1 si la neurona está encendida, 0 si apagada**). Nuestra red de 8 neuronas bajó la pérdida de 1.118 a casi 0.
4. Con una tasa demasiado alta (0,01), la red se atasca en un **óptimo local** (~11): los codos quedan mal colocados. Otro peligro conocido son las
   **neuronas muertas**. Entrenar es un poco arte: vigila la curva de aprendizaje.
5. Con suficientes codos se aproxima casi cualquier curva (**aproximación universal**); con varias capas, **aprendizaje profundo**. La red típica de un humanoide (348
   → 256 → 256 → 17) tiene **159.505** ruedecillas.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Lineal** | Que solo hace rectas: multiplicar y sumar. |
| **Función de activación** | La regla que se aplica a la salida de cada neurona para que la red pueda doblarse. |
| **ReLU** | La activación max(0, x): deja pasar lo positivo, convierte lo negativo en 0. Un "codo". |
| **Red neuronal** | Capas de neuronas con activación, una detrás de otra. |
| **Capa oculta** | Una capa entre la entrada y la salida. |
| **Neurona encendida / apagada** | Con z > 0 (deja pasar) / con z ≤ 0 (da 0). |
| **Neuronas muertas** | Neuronas apagadas para todos los ejemplos, que ya no aprenden. |
| **Valor absoluto (`np.abs`)** | Un número sin su signo: la distancia al cero. |
| **Aproximación universal** | Con suficientes neuronas, una red imita casi cualquier curva. |
| **Aprendizaje profundo (*deep learning*)** | Aprender con redes de muchas capas. |
"""),

md(r"""## 10 · Ejercicios

**E1.** Calcula a mano: ReLU(5), ReLU(−3), ReLU(0), ReLU(2 − 7).

**E2.** En la red a mano del apartado 5, calcula el empuje para una inclinación de **0**, de **2** y de **−2**. ¿Coinciden con el maestro (−30 × inclinación,
recortado a ±40)?

**E3.** Una red tiene 10 entradas, una capa oculta de 32 neuronas y 4 salidas. ¿Cuántas ruedecillas tiene?

**E4.** Repite el entrenamiento de la red con tasa **0,01** (cambia `tasa = 0.003` por `tasa = 0.01` y vuelve a ejecutar la celda; ojo, también hay que volver a
crear los pesos al azar, que están en la misma celda). ¿En cuánto se queda la pérdida final?

**E5.** ¿Qué crees que pasaría si quitáramos la ReLU de la red (es decir, si usáramos `z` en vez de `relu(z)`)? ¿Podría bajar la pérdida de 81,5? Razónalo con el
apartado 3.

**E6.** **Reto.** Construye a mano, con codos, una red que imite al maestro "**tímido**": no empuja nada si la inclinación está entre −1 y 1 (zona muerta), y fuera
de ahí empuja −20 por cada grado que se pase. (Pista: necesitas un codo en +1 y otro en −1. Para el de −1, puedes usar ReLU(−inclinación − 1).)
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

- ReLU(5) = **5** (positivo: pasa).
- ReLU(−3) = **0** (negativo: se convierte en 0).
- ReLU(0) = **0**.
- ReLU(2 − 7) = ReLU(−5) = **0**.
</details>

<details>
<summary>▶ Solución E2</summary>

- Inclinación 0: 40 − 30 × ReLU(4/3) + 30 × ReLU(−4/3) = 40 − 30 × 4/3 + 0 = 40 − 40 = **0**. Maestro: −30 × 0 = 0. ✓
- Inclinación 2: 40 − 30 × ReLU(10/3) + 30 × ReLU(2/3) = 40 − 100 + 20 = **−40**. Maestro: −60, recortado a −40. ✓
- Inclinación −2: 40 − 30 × ReLU(−2/3) + 30 × ReLU(−10/3) = 40 − 0 + 0 = **40**. Maestro: +60, recortado a 40. ✓
</details>

<details>
<summary>▶ Solución E3</summary>

Capa oculta: 32 × 10 + 32 = 352. Salida: 4 × 32 + 4 = 132. Total: **484** ruedecillas.
</details>

<details>
<summary>▶ Solución E4</summary>

Con tasa 0,01, la pérdida final se queda en torno a **11**, en vez de bajar a casi 0. Los primeros pasos, demasiado bruscos, colocan los codos en sitios poco
útiles, y la red cae en un **óptimo local** del que el descenso por gradiente no sabe salir (apartado 6). Curiosamente, ninguna neurona ha muerto (si lo
compruebas, todas siguen encendidas para algunos ejemplos): simplemente están **mal colocadas**. Vuelve a poner 0,003 para recuperar el buen resultado.
</details>

<details>
<summary>▶ Solución E5</summary>

Sin la ReLU, cada neurona oculta sería lineal, y la red entera sería una torre de capas lineales: **una recta** (apartado 3). Así que la mejor pérdida posible sería la
de la mejor recta: **81,5**, igual que la neurona lineal. Toda la capacidad de doblarse viene de la activación. Sin codos, da igual cuántas neuronas pongas.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
timido = -20 * relu(inclinaciones - 1) + 20 * relu(-inclinaciones - 1)

maestro_timido = np.where(inclinaciones > 1, -20 * (inclinaciones - 1),
                 np.where(inclinaciones < -1, -20 * (inclinaciones + 1), 0))
print(np.max(np.abs(timido - maestro_timido)))
```

- `-20 * relu(inclinaciones - 1)`: el codo en **+1**; a partir de ahí, empuja −20 por cada grado de más.
- `+20 * relu(-inclinaciones - 1)`: el codo en **−1**; por debajo de −1, ReLU(−i − 1) crece, y con el +20 empuja hacia el lado positivo (para enderezar).
- Entre −1 y 1, los dos codos están apagados: empuje 0, la zona muerta.

(`np.where(condición, a, b)` elige `a` donde la condición es cierta y `b` donde no: aquí solo sirve para fabricar el maestro y comparar.) La diferencia máxima sale 0:
imitación exacta, con dos codos.
</details>
"""),

md(r"""## 11 · 🛠 Práctica en MuJoCo: una red neuronal al volante del palo de escoba

En la práctica del NB18 una neurona lineal aprendió a imitar al maestro del palo de escoba de MuJoCo. Pero hicimos una pequeña trampa: apuntábamos lo que el maestro
"pensaba", **sin** el límite de su motor. Hoy toca el maestro de verdad, el que tiene **límite**, exactamente como el del apartado 1. Y harás las dos cosas de la
lección, en el simulador:

1. Construir **a mano**, con dos codos, una red neuronal que es **exactamente** el maestro, y darle el mando del palo.
2. Entrenar una red de **8 neuronas** con tu retropropagación del apartado 6, a partir de demostraciones, y ver qué tal conduce.
"""),

md(r"""### Paso 1 · El motor de MuJoCo también tiene límite

En el plano del palo, el motor tiene `ctrlrange="-1 1"`: por mucho que le pidas, **nunca** empuja más que con una orden de 1 (que, con `gear="10"`, son 10 newtons). Pidámosle
**3** y miremos la fuerza que llega al carro (`datos.qfrc_actuator`: la fuerza que los motores aplican en cada junta):
"""),

code(r"""import mujoco
import taller

modelo, datos = taller.cargar("palo_escoba")
datos.ctrl[0] = 3
mujoco.mj_forward(modelo, datos)
print("Orden pedida:", datos.ctrl[0], "| fuerza en el carro:", datos.qfrc_actuator[0], "newtons")"""),

md(r"""Pides 3 (que serían 30 N) y llegan **10 N**: MuJoCo recorta solo. Así que el maestro del NB18, mirado de verdad, es **recortar(3 × inclinación + 0,8 × velocidad del palo + 0,1 ×
posición del carro + 0,2 × velocidad del carro, ±1)**: una rampa con dos tramos planos, la misma forma de tres tramos del apartado 1. Llamemos **s** a esa suma con
pesos (lo que el maestro "piensa" antes del límite):
"""),

code(r"""def observar(datos):
    return np.array([datos.qpos[1], datos.qvel[1], datos.qpos[0], datos.qvel[0]])

PESOS_MAESTRO = np.array([3, 0.8, 0.1, 0.2])

def maestro(obs):
    s = PESOS_MAESTRO @ obs              # el producto escalar del NB13
    return np.clip(s, -1, 1)             # el límite del motor

ss = np.linspace(-3, 3, 61)
plt.figure(figsize=(6, 3.5))
plt.plot(ss, np.clip(ss, -1, 1), color="tab:orange")
plt.grid(True, alpha=0.4)
plt.xlabel("s (lo que piensa el maestro)")
plt.ylabel("orden que llega al motor")
plt.show()"""),

md(r"""### Paso 2 · La red a mano

En el apartado 5 construiste el maestro con límite con dos codos: 40 − 30 × ReLU(i + 4/3) + 30 × ReLU(i − 4/3). Aquí la misma receta, con los números de este motor:

```
   orden = −1 + ReLU(s + 1) − ReLU(s − 1)
```

- Si s es muy negativo (menor que −1), los dos codos están apagados: orden **−1** (el tramo plano de abajo).
- Entre −1 y 1, el primer codo se enciende: −1 + (s + 1) = **s** (la rampa).
- Por encima de 1, se enciende también el segundo y cancela la rampa: −1 + (s + 1) − (s − 1) = **1** (el tramo plano de arriba).

Pero s no es un número suelto: es una suma con pesos de las **4** entradas. Así que cada codo es una **neurona** completa, con 4 pesos (los del maestro) y su sesgo (+1 y
−1). Como red neuronal:

```
                     ┌─► neurona 1: ReLU(3·i + 0,8·v + 0,1·x + 0,2·u + 1) ─┐  × (+1)
   observación  ─────┤                                                      ├──► −1 + ... ──► orden
   (4 números)       └─► neurona 2: ReLU(3·i + 0,8·v + 0,1·x + 0,2·u − 1) ─┘  × (−1)
       ENTRADA                        CAPA OCULTA (2 neuronas)                    SALIDA
```

Con matrices (NB14): la capa oculta es una matriz de pesos de 2 × 4 (una fila por neurona) y un vector de 2 sesgos; la salida, un vector de 2 pesos y un sesgo:
"""),

code(r"""W_mano = np.array([[3, 0.8, 0.1, 0.2],
                   [3, 0.8, 0.1, 0.2]])
b_mano = np.array([1.0, -1.0])
v_mano = np.array([1.0, -1.0])
c_mano = -1.0

def red_a_mano(obs):
    ocultas = relu(W_mano @ obs + b_mano)     # la capa oculta: matriz × vector, más sesgos, y el codo
    return v_mano @ ocultas + c_mano          # la neurona de salida"""),

md(r"""### Paso 3 · ¿Es de verdad el maestro?

Lo comprobamos con muchas situaciones del palo. Grabamos demostraciones como en la práctica del NB18 (episodios que empiezan al azar, maestro con el pulso tembloroso,
apuntando lo que quería hacer), pero ahora con el palo un poco más inclinado al empezar (hasta 0,4 rad) para que el límite entre en juego, y parando el episodio si
el palo se cae (más de 0,5 rad):
"""),

code(r"""def grabar_demostraciones(temblor, episodios=10, semilla=0):
    azar = np.random.default_rng(semilla)
    ejemplos = []
    etiquetas = []
    for episodio in range(episodios):
        mujoco.mj_resetData(modelo, datos)
        datos.qpos[1] = azar.uniform(-0.4, 0.4)
        datos.qpos[0] = azar.uniform(-1, 1)
        for paso in range(300):
            obs = observar(datos)
            quiere = maestro(obs)
            ejemplos.append(obs)
            etiquetas.append(quiere)
            datos.ctrl[0] = np.clip(quiere + azar.uniform(-temblor, temblor), -1, 1)
            mujoco.mj_step(modelo, datos)
            if abs(datos.qpos[1]) > 0.5:
                break
    return np.array(ejemplos), np.array(etiquetas)

ejemplos, etiquetas = grabar_demostraciones(temblor=1)
print("Ejemplos:", ejemplos.shape)
print("Ejemplos en los que el motor va al límite:", round(np.mean(np.abs(etiquetas) >= 1) * 100, 1), "%")

diferencias = []
for k in range(len(ejemplos)):
    diferencias.append(abs(red_a_mano(ejemplos[k]) - etiquetas[k]))
print("Mayor diferencia entre la red a mano y el maestro:", max(diferencias))"""),

md(r"""(`np.abs(etiquetas) >= 1` da un array de `True`/`False`, y su media es la fracción de `True`, porque cuentan como 1 y 0: el truco del apartado 6.)

Unos 2.800 ejemplos (un episodio se cortó porque el temblor tumbó el palo), y en un **2,6 %** de ellos el motor va al límite. La mayor diferencia es 0 o un ruido de
decimales minúsculo: **la red a mano es el maestro**, con sus esquinas incluidas.
"""),

md(r"""### Paso 4 · La red a mano, al volante

Ahora le damos el mando. Fíjate en que ya no hace falta `np.clip`: la red **lleva el límite dentro**, su salida nunca pasa de ±1. Una función que cuenta los segundos
que aguanta una política (cualquier función que reciba la observación y devuelva la orden) empezando con el palo inclinado:
"""),

code(r"""def segundos_de_pie(politica, inclinacion):
    mujoco.mj_resetData(modelo, datos)
    datos.qpos[1] = inclinacion
    for paso in range(1000):
        datos.ctrl[0] = politica(observar(datos))
        mujoco.mj_step(modelo, datos)
        if abs(datos.qpos[1]) > 0.5:
            break
    return round(datos.time, 2)

INCLINACIONES = [0.2, 0.3, 0.35, 0.4]
print("Red a mano:", [segundos_de_pie(red_a_mano, i) for i in INCLINACIONES])

def control_red_a_mano(modelo, datos):
    datos.ctrl[0] = red_a_mano(observar(datos))

mujoco.mj_resetData(modelo, datos)
datos.qpos[1] = 0.4
taller.video(modelo, datos, segundos=4, control=control_red_a_mano, nombre="nb19_red_a_mano", distancia=3);"""),

md(r"""Los **10 segundos** desde todas las inclinaciones, también desde 0,4 rad (23 grados), donde el motor pasa los primeros instantes a tope. Una red neuronal de 2 neuronas, con
pesos puestos por ti, está equilibrando un palo con física de verdad.
"""),

md(r"""### Paso 5 · La neurona lineal se queda corta... pero conduce

¿Y si un alumno **lineal** (el del NB18) intenta imitar a este maestro con límite? Le pasa lo del apartado 2: no puede doblarse.
"""),

code(r"""pesos = np.zeros(4)
sesgo = 0.0
for paso in range(2000):
    errores = ejemplos @ pesos + sesgo - etiquetas
    for k in range(4):
        pesos[k] = pesos[k] - 0.5 * 2 * np.mean(errores * ejemplos[:, k])
    sesgo = sesgo - 0.5 * 2 * np.mean(errores)

def lineal(obs):
    return np.clip(obs @ pesos + sesgo, -1, 1)

print("Pesos de la neurona lineal:", np.round(pesos, 2), "| pérdida:", round(np.mean((ejemplos @ pesos + sesgo - etiquetas) ** 2), 5))
print("Neurona lineal:", [segundos_de_pie(lineal, i) for i in INCLINACIONES])"""),

md(r"""Sus pesos salen **más pequeños** que los del maestro (**2,55** en vez de 3 para la inclinación, 0,51 en vez de 0,8...): igual que la recta del apartado 2 tenía pendiente
−18,4 en vez de −30. Para no pasarse en los ejemplos donde el maestro está "plano" en el límite, la recta se queda corta en el centro, y su pérdida no baja de **0,009**.

Y sin embargo, al volante, **aguanta los 10 segundos desde todas las inclinaciones**. Dos razones: MuJoCo recorta su orden igualmente (el límite lo pone el motor, no
la política), y en este palo unos pesos algo más pequeños también sirven (recuerda el NB18: había muchas combinaciones que funcionaban). Imitar peor no siempre es
conducir peor.
"""),

md(r"""### Paso 6 · Una red de 8 neuronas aprende sola

Ahora, lo gordo: la red del apartado 6, con 8 neuronas ocultas y pesos al azar, aprendiendo de las demostraciones con **tu** retropropagación. Solo cambia una cosa:
cada neurona oculta tiene ahora **4** pesos de entrada (uno por número de la observación), así que `pesos_entrada` es una matriz de 8 × 4, y la pendiente de cada uno
de esos pesos lleva su entrada, `ejemplos[:, k]`. Lo demás, idéntico. Tarda unos segundos:
"""),

code(r"""ocultas = 8
generador = np.random.default_rng(0)
pesos_entrada = generador.uniform(-1, 1, size=(ocultas, 4))
sesgos_ocultos = generador.uniform(-1, 1, size=ocultas)
pesos_salida = generador.uniform(-1, 1, size=ocultas)
sesgo_salida = 0.0

tasa = 0.2
historial = []
for paso in range(3000):
    # 1. hacia delante
    zs = []
    activaciones = []
    for j in range(ocultas):
        z = ejemplos @ pesos_entrada[j] + sesgos_ocultos[j]
        zs.append(z)
        activaciones.append(relu(z))
    prediccion = sesgo_salida
    for j in range(ocultas):
        prediccion = prediccion + pesos_salida[j] * activaciones[j]
    errores = prediccion - etiquetas
    historial.append(np.mean(errores ** 2))

    # 2. hacia atrás (la regla de la cadena)
    for j in range(ocultas):
        culpa = 2 * errores * pesos_salida[j] * (zs[j] > 0)
        for k in range(4):
            pesos_entrada[j, k] = pesos_entrada[j, k] - tasa * np.mean(culpa * ejemplos[:, k])
        sesgos_ocultos[j] = sesgos_ocultos[j] - tasa * np.mean(culpa)
        pesos_salida[j] = pesos_salida[j] - tasa * np.mean(2 * errores * activaciones[j])
    sesgo_salida = sesgo_salida - tasa * np.mean(2 * errores)

def red_aprendida(obs):
    return pesos_salida @ relu(pesos_entrada @ obs + sesgos_ocultos) + sesgo_salida

print("Pérdida al empezar:", round(historial[0], 4), "| al terminar:", round(historial[-1], 5))"""),

md(r"""La pérdida baja de 0,32 a **0,00019**: unas **cincuenta veces menor** que la de la neurona lineal. La red sí puede doblarse y ha aprendido las esquinas. ¿Y al volante?
Probamos las cuatro inclinaciones, y en vídeo, la más difícil, 0,4 rad:
"""),

code(r"""print("Red aprendida:", [segundos_de_pie(red_aprendida, i) for i in INCLINACIONES])

def control_red_aprendida(modelo, datos):
    datos.ctrl[0] = np.clip(red_aprendida(observar(datos)), -1, 1)

mujoco.mj_resetData(modelo, datos)
datos.qpos[1] = 0.4
taller.video(modelo, datos, segundos=4, control=control_red_aprendida, nombre="nb19_red_aprendida", distancia=3);"""),

md(r"""Aguanta los 10 segundos desde 0,2, 0,3 y 0,35... pero desde **0,4 se cae** a los 2,15 s: en el vídeo, el carro corre pero no consigue meterse debajo del palo.
Comparando las tres políticas:

| Empezando en... | 0,2 | 0,3 | 0,35 | 0,4 | Pérdida |
|---|---|---|---|---|---|
| Red a mano (2 neuronas, el maestro exacto) | 10 s | 10 s | 10 s | 10 s | 0 |
| Neurona lineal | 10 s | 10 s | 10 s | 10 s | 0,009 |
| Red aprendida (8 neuronas) | 10 s | 10 s | 10 s | **2,15 s** | 0,0002 |

¡La que **mejor imita** los ejemplos es la que **peor conduce** en el caso difícil! Es justo el aviso del apartado 9 del NB18: una neurona lineal "extiende" su regla de
forma razonable a situaciones que no vio, pero una red con codos puede hacer **cualquier cosa** fuera de sus ejemplos. Y con el palo a 0,4 rad la red está casi fuera:
solo un **2,6 %** de los ejemplos tenían el motor al límite, y muy pocos un palo tan inclinado. Allí un pequeño error suyo lleva a una situación aún más rara, y así
hasta tirar el palo (el **desplazamiento de distribución**). Tú, en cambio, sabías la receta exacta.

La lección de ingeniero: **una pérdida pequeña en los ejemplos no garantiza conducir bien en todas partes**. Por eso las políticas se juzgan siempre **en el
simulador**, probando situaciones difíciles, y no solo mirando su pérdida.
"""),

md(r"""### Tus retos

**Reto 1 · Otros pesos iniciales.** Repite el Paso 6 con `np.random.default_rng(1)`, `(2)` y `(3)` (y vuelve a ejecutar la celda de la prueba). ¿Aguanta alguna desde 0,4?

**Reto 2 · Un motor más débil.** Cambia la red a mano para un motor cuyo límite fuera **±0,5** en vez de ±1 (pista: los codos deben estar en s = −0,5 y s = 0,5, y el tramo
plano de abajo en −0,5). ¿Desde qué inclinación ya no puede salvar el palo?

**Reto 3 · Sin la ReLU.** En `red_a_mano`, quita la `relu` (deja solo `W_mano @ obs + b_mano`). ¿Qué orden da la red, sea cual sea la situación? ¿Por qué?

<details>
<summary>▶ Solución Reto 1</summary>

Con las semillas **1, 2 y 3**, la red aprendida aguanta los 10 s desde **todas** las inclinaciones, también desde 0,4 (con pérdidas finales parecidas: 0,00026, 0,00016
y 0,0001). La semilla 0 tuvo **mala suerte**: con los mismos
datos y el mismo entrenamiento, los pesos iniciales deciden dónde acaban los codos, y eso cambia cómo conduce la red en las zonas con pocos ejemplos. Entrenar redes es
un poco arte (apartado 6): los profesionales entrenan varias veces con distintas semillas y se quedan con la mejor **en el simulador**.
</details>

<details>
<summary>▶ Solución Reto 2</summary>

```python
b_mano = np.array([0.5, -0.5])
c_mano = -0.5
print([segundos_de_pie(red_a_mano, i) for i in [0.1, 0.2, 0.3]])
```

Con medio motor, aguanta desde 0,1 y 0,2 rad, pero desde **0,3 se cae** (a los 1,54 s): el motor no tiene fuerza suficiente para meter el carro debajo del palo a tiempo.
Ninguna política, por lista que sea, puede pedir más de lo que el motor da. (Vuelve a poner `b_mano = np.array([1.0, -1.0])` y `c_mano = -1.0` después.)
</details>

<details>
<summary>▶ Solución Reto 3</summary>

Sin la ReLU: −1 + (s + 1) − (s − 1) = **1**, siempre. Las dos neuronas tienen los mismos pesos, y al restarlas se cancelan: la red lineal se queda en una constante, y el
carro empuja a tope siempre hacia +x (con `segundos_de_pie`, el palo cae en menos de 0,6 s desde cualquiera de las cuatro inclinaciones; desde 0,2, a los 0,36 s). Toda la "inteligencia" de la red a mano está en los codos: sin activación, las capas solo
multiplican y suman (apartado 3).
</details>

### Qué has aprendido de MuJoCo hoy

- `ctrlrange` recorta la orden del motor: es una no linealidad de verdad (pides 3, llegan 10 N, no 30). **`datos.qfrc_actuator`** muestra la fuerza que el motor aplica.
- Una **política neuronal** en MuJoCo es una función observación → orden: `v @ relu(W @ obs + b) + c`. La red a mano de 2 neuronas **es** el maestro con límite y
  equilibra el palo desde 0,4 rad.
- Una red de 8 neuronas entrenada con tu retropropagación imita las demostraciones 50 veces mejor que una neurona lineal, pero (con la semilla 0) se cae desde
  0,4 rad, donde casi no hubo ejemplos, mientras la lineal aguanta: una política se juzga **en el simulador**, no por su pérdida.

En la práctica del NB20 empezarás a **escribir planos MJCF con Python**: robots de tamaño variable fabricados con texto.
"""),

md(r"""## 12 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Con esta lección tienes **todas las piezas matemáticas** de una red neuronal: vectores, productos escalares, matrices, pendientes, gradientes, la regla de la cadena y
las activaciones. Y has entrenado una red escribiendo tú mismo cada línea de su aprendizaje. Eso es más de lo que entiende mucha gente que trabaja con inteligencia
artificial.

Antes de seguir, haremos una parada importante: un bloque de **ocho lecciones de Python "de verdad"** (NB20-NB27), para que domines el lenguaje como un profesional
(clases, ficheros, errores, tests, Git...), porque las herramientas que vienen están escritas con todo eso. Después, el siguiente paso será juntar las dos mitades del curso: las **redes neuronales** (lo que sabe hacer la mente) y el **aprendizaje por refuerzo** (cómo aprende sin maestro,
solo con recompensas). La gran pregunta será: si no hay un maestro que diga "aquí había que empujar tanto", **¿de dónde sale la pérdida?** La respuesta tiene que ver
con algo que ya intuyes desde el NB03: **hacer más probables las acciones que salieron bien**.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB19_redes_neuronales.ipynb")
    build(out, cells, title="NB19 · Redes neuronales: el codo que lo cambia todo")
