"""Construye NB30 · Domar el ruido: ventaja, normalización, crítico y descuento (Parte 4 · Lección 3).

Medir el ruido del gradiente: 40 estimaciones con los mismos pesos (−5, −3):
sin línea base la dispersión es ~3,5× mayor y ni el signo de la media es fiable.
Normalizar las ventajas (media 0, desviación 1). El CRÍTICO: la función de valor
V(s) = retorno esperado desde una situación; rasgos [1, i², v², i·v, t/500]
(por qué cuadrados: simetría; por qué el tiempo: el episodio se trunca);
ajuste por mínimos cuadrados (np.linalg.lstsq = la regresión del NB18 de un
golpe); ventaja = G − V(s). Comparación con 5 semillas (iteraciones hasta 490):
línea base media ~[53,79,95,60,47]; crítico + normalizar ~[13,17,17,66,26] (el
mejor). El descuento γ: 0,9 no aprende (miope), 0,99 bien, 1,0 algo peor.
Hacia actor-crítico y PPO.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB30 · Domar el ruido: ventaja, normalización, crítico y descuento

**Parte 4 · Aprendizaje por refuerzo de verdad — Lección 3**

> En el **NB29** el palo de escoba aprendió **solo** con REINFORCE. Y viste que una sola línea (restar la media, la **línea base**) separaba un
> algoritmo inútil de uno que funciona. Hoy entenderemos **por qué**, lo **mediremos**, y lo llevaremos más lejos.

El enemigo de todo el aprendizaje por refuerzo tiene un nombre: el **ruido** (los matemáticos lo llaman **varianza**). Cada vez que estimamos "hacia dónde
mejorar" a partir de unos pocos episodios al azar, la estimación sale distinta, y a veces apunta en la dirección equivocada. Cuanto más ruido, más episodios
hacen falta, y más inestable es el aprendizaje. Con un humanoide, eso es la diferencia entre entrenar en horas o no conseguirlo nunca.

Hoy veremos las cuatro armas contra el ruido que usan **todos** los algoritmos modernos:

1. **Medir** el ruido (para saber si una idea ayuda de verdad).
2. **Normalizar** las ventajas.
3. El **crítico**: una pieza que aprende **cuánto vale cada situación**, para comparar cada acción con lo que era "normal" **justo en ese momento**.
4. Elegir bien el **descuento**.

Con ellas daremos el paso hacia la arquitectura **actor-crítico**, la base de PPO.
"""),

md(r"""## 1 · El laboratorio

Traemos las piezas del NB29, tal cual: jugar episodios en paralelo apuntándolo todo, calcular los retornos desde cada paso y la dirección de mejora. (Si vienes del NB29 te
sonarán línea a línea; si no, allí están explicadas.)
"""),

code(r"""import numpy as np
import matplotlib.pyplot as plt

def jugar(pesos, sigma, n_episodios, generador, pasos_maximos=500):
    inclinacion = np.full(n_episodios, 2.0)
    velocidad = np.zeros(n_episodios)
    vivos = np.ones(n_episodios, dtype=bool)
    observaciones = np.zeros((pasos_maximos, n_episodios, 2))
    acciones = np.zeros((pasos_maximos, n_episodios))
    medias = np.zeros((pasos_maximos, n_episodios))
    recompensas = np.zeros((pasos_maximos, n_episodios))
    estaba_vivo = np.zeros((pasos_maximos, n_episodios), dtype=bool)
    for t in range(pasos_maximos):
        observacion = np.stack([inclinacion, velocidad], axis=1)
        media = observacion @ pesos
        accion = media + sigma * generador.standard_normal(n_episodios)
        observaciones[t], acciones[t], medias[t], estaba_vivo[t] = observacion, accion, media, vivos
        empuje = np.clip(accion, -40, 40)
        aceleracion = 10 * inclinacion + empuje + generador.uniform(-30, 30, n_episodios)
        velocidad = velocidad + aceleracion * 0.02
        inclinacion = inclinacion + velocidad * 0.02
        vivos = vivos & (np.abs(inclinacion) <= 30)
        recompensas[t] = np.where(vivos, 1 - (inclinacion / 30) ** 2, 0.0)
    return observaciones, acciones, medias, recompensas, estaba_vivo

def retornos_desde_cada_paso(recompensas, gamma=0.99):
    G = np.zeros_like(recompensas)
    acumulado = np.zeros(recompensas.shape[1])
    for t in reversed(range(recompensas.shape[0])):
        acumulado = recompensas[t] + gamma * acumulado
        G[t] = acumulado
    return G

def direccion_de_mejora(observaciones, acciones, medias, ventajas, estaba_vivo, sigma):
    hacia_mas_probable = ((acciones - medias) / sigma ** 2)[..., None] * observaciones
    votos = (ventajas * estaba_vivo)[..., None] * hacia_mas_probable
    return votos.sum(axis=0).mean(axis=0)

print("Laboratorio listo")"""),

md(r"""## 2 · Arma 1: medir el ruido

En el NB29 dijimos que REINFORCE puro "tenía mucho ruido". Un ingeniero no se queda en "mucho": **lo mide** (NB07). ¿Cómo se mide el ruido de una estimación? Como en el NB28: repitiéndola
**muchas veces** en las mismas condiciones y mirando **cuánto se dispersan** los resultados (su desviación típica).

Fijamos unos pesos cualesquiera, por ejemplo (−5, −3) (una política mediocre, a mitad de aprender), y estimamos la dirección de mejora **40 veces**, cada una con un lote nuevo de 50
episodios. Lo hacemos sin línea base y con la línea base del NB29 (la media del retorno en cada paso):
"""),

code(r"""pesos_fijos = np.array([-5.0, -3.0])

def estimar_muchas_veces(usar_linea_base, repeticiones=40):
    generador = np.random.default_rng(7)
    estimaciones = []
    for r in range(repeticiones):
        obs, acc, med, rec, vivo = jugar(pesos_fijos, 5.0, 50, generador)
        G = retornos_desde_cada_paso(rec)
        ventajas = G - G.mean(axis=1, keepdims=True) if usar_linea_base else G
        estimaciones.append(direccion_de_mejora(obs, acc, med, ventajas, vivo, 5.0))
    return np.array(estimaciones)                    # (40, 2): 40 flechas de dirección

for nombre, usar in [("sin línea base", False), ("con línea base", True)]:
    e = estimar_muchas_veces(usar)
    print(f"{nombre}: media de las 40 estimaciones {e.mean(axis=0).round(1)} | dispersión {e.std(axis=0).round(1)}")"""),

md(r"""Mira las dos columnas de números:

- **Dispersión**: sin línea base, las 40 estimaciones bailan con una desviación típica de unos **34 y 44**; con línea base, de unos **10 y 20**. **Entre dos y cuatro veces menos
  ruido** con una sola línea de código. Ahora "mucho ruido" es un número.
- **Media**: con línea base, la media de las 40 estimaciones apunta claramente hacia valores **negativos** (hacia empujar más en contra de la caída: hacia la política buena). Sin línea
  base, la media sale... ¡**positiva**! Con tanto ruido, ni siquiera 40 lotes (2.000 episodios) bastan para estar seguros de la **dirección** (fíjate: la teoría dice que la dirección
  promedio es la misma con y sin línea base; lo que pasa es que, sin ella, el error típico, NB28, es tan grande que 40 estimaciones no alcanzan para verla).

Esto explica de golpe el fracaso del NB29: con 50 episodios por paso, REINFORCE puro avanzaba **a ciegas**.
"""),

md(r"""## 3 · Arma 2: normalizar las ventajas

La segunda arma es muy sencilla, y la usa casi todo el mundo. Las ventajas (G menos la línea base) pueden ser números de cualquier tamaño: al principio del entrenamiento, cuando el palo
se cae enseguida, son pequeñas; más adelante, cuando aguanta cientos de pasos, enormes. Eso hace que el **tamaño de los pasos** de aprendizaje cambie muchísimo a lo largo del entrenamiento
(pasos minúsculos al principio, gigantescos después), y que la tasa de aprendizaje buena al principio sea malísima al final.

La solución: en cada lote, **normalizar** las ventajas como normalizamos las observaciones en el NB27: restarles su media y dividirlas entre su desviación típica. Así, en **cada** lote, las
ventajas tienen media 0 y desviación 1: la mitad de las acciones se refuerzan, la otra mitad se debilitan, y el tamaño de los pasos lo decide **solo** la tasa de aprendizaje.

```
   ventajas normalizadas = (ventajas − su media) / su desviación típica
```

Como cambia la escala de los pasos, la tasa de aprendizaje buena también cambia (ahora usaremos 0,3). Lo probaremos en el apartado 5, junto al crítico.
"""),

md(r"""## 4 · Arma 3: el crítico

La línea base del NB29 compara cada acción con **la media de todos los episodios en ese mismo paso**. Pero piensa en lo que significa: en el paso 30, un episodio puede tener el palo casi
derecho (y por delante, muchos puntos) y otro a punto de caer (y por delante, casi nada). ¿Es justo compararlos con la misma "media"? No: lo justo sería comparar cada acción con lo que era
"normal" **en su situación concreta**.

Para eso hace falta saber **cuánto vale cada situación**: "con el palo así de inclinado, girando a esta velocidad, en este momento del episodio, ¿cuántos puntos suelo sacar de aquí en adelante?".
A ese número se le llama el **valor** de la situación, y a la función que lo calcula, la **función de valor**, que se escribe **V(s)** (la *s* es de *situación*, o *state*, "estado").

```
   V(situación) = el retorno que se espera sacar desde esa situación (NB28: valor esperado)
```

¿Y cómo se conoce V? ¡**Aprendiéndola**! Tenemos muchísimos ejemplos: cada paso de cada episodio es una situación, y sabemos el retorno que vino después (su G). Aprender V es **aprendizaje
supervisado** (NB18): ajustar una "neurona" para que, a partir de la situación, **prediga** G. A esta segunda neurona se le llama el **crítico** (porque **juzga** cada situación), y a la
política, el **actor** (porque **actúa**). Juntos forman la arquitectura **actor-crítico**:

```
   ACTOR  (la política):   "en esta situación, hago esto"        → decide las acciones
   CRÍTICO (la función V):  "esta situación suele valer tanto"    → sirve de línea base para juzgar al actor

   ventaja = G (lo que pasó de verdad) − V(situación) (lo que solía pasar)
```

Una acción con ventaja positiva hizo las cosas **mejor de lo que solía salir en esa misma situación**: un juicio mucho más justo que compararla con la media de todo el lote.
"""),

md(r"""### ¿Qué necesita mirar el crítico?

El crítico tiene que predecir el valor a partir de la situación. ¿Qué datos le damos? Pensemos como un ingeniero (NB03: elegir bien la observación es parte del trabajo):

- **La inclinación, pero al cuadrado.** Lo que importa es **cuánto** está inclinado, no hacia qué lado: estar inclinado 10 grados a la derecha es igual de malo que 10 a la izquierda. Una
  neurona lineal con la inclinación tal cual no puede captar eso (daría valores opuestos a −10 y a +10); con la inclinación **al cuadrado**, sí (las dos dan 100). Lo mismo con la **velocidad
  al cuadrado**.
- **El producto inclinación × velocidad**: distingue "inclinado y cayéndose más" (los dos con el mismo signo: producto positivo, malo) de "inclinado pero volviendo" (signos opuestos:
  negativo, bueno). ¡El problema de la foto del NB03, otra vez!
- **El momento del episodio** (el paso dividido entre 500): como el episodio se corta a los 500 pasos, cerca del final quedan menos recompensas por delante, aunque el palo esté perfecto.
- Y un **1** fijo (para que el crítico tenga un sesgo, NB13).

A estos datos fabricados para una neurona se les llama **rasgos** (*features*). Elegirlos bien es un arte (y las redes neuronales del NB19 lo hacen solas: aprenden sus propios rasgos en las
capas ocultas).
"""),

code(r"""def rasgos(observaciones):
    inclinacion = observaciones[..., 0]
    velocidad = observaciones[..., 1]
    pasos, episodios = inclinacion.shape
    momento = np.repeat(np.arange(pasos)[:, None], episodios, axis=1) / pasos    # el paso de cada dato, de 0 a 1
    return np.stack([np.ones_like(inclinacion), inclinacion ** 2, velocidad ** 2,
                     inclinacion * velocidad, momento], axis=-1)                 # (pasos, episodios, 5)

print("Forma de los rasgos:", rasgos(np.zeros((500, 50, 2))).shape)"""),

md(r"""(`np.repeat` repite un array: aquí, el número de paso, una vez por episodio.)

### Ajustar el crítico de un golpe: mínimos cuadrados

El crítico es una neurona lineal sobre estos 5 rasgos: V = pesos_críticos · rasgos. Hay que encontrar los pesos que hacen que V se parezca lo más posible a los G de verdad, es decir, que
**minimicen el error cuadrático medio** (NB18). Podríamos hacerlo con descenso por gradiente, como en el NB18. Pero para una neurona **lineal** existe un atajo matemático que encuentra los pesos
**exactos** de un solo golpe, sin iterar: se llama **mínimos cuadrados**, y NumPy lo trae hecho, `np.linalg.lstsq` (de *least squares*). Es exactamente "la mejor recta" del NB19, calculada
directamente:
"""),

code(r"""def ajustar_critico(observaciones, G, estaba_vivo):
    X = rasgos(observaciones)[estaba_vivo]            # los rasgos de todas las situaciones vividas
    y = G[estaba_vivo]                                # y sus retornos de verdad
    pesos_criticos, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    return pesos_criticos

generador = np.random.default_rng(3)
obs, acc, med, rec, vivo = jugar(np.array([-12.0, -6.0]), 5.0, 50, generador)     # una política que ya va bien
G = retornos_desde_cada_paso(rec)
pesos_criticos = ajustar_critico(obs, G, vivo)
print("Pesos del crítico [1, i², v², i·v, momento]:", pesos_criticos.round(2))"""),

md(r"""(`lstsq` devuelve cuatro cosas; solo nos interesa la primera, y el resto lo recogemos en `_`, la caja "de usar y tirar" de Python. `rcond=None` es un detalle técnico que pide NumPy.)

Leamos lo que ha aprendido el crítico. El peso del **momento** es negativo y grande (unos −92): cuanto más avanzado el episodio, menos puntos quedan por delante. El de la
**inclinación²** también es negativo: cuanto más inclinado, peor. Esos dos tienen todo el sentido. Pero mira los otros dos: el de la velocidad² sale **ligeramente positivo**, y el de
inclinación × velocidad, también **positivo**. ¿Significa eso que "girar deprisa" es bueno? No necesariamente: cuando los rasgos están **relacionados entre sí** (y aquí lo están: un palo muy
inclinado suele estar también girando deprisa), los pesos se "reparten" el trabajo de formas raras, y **no se pueden leer uno por uno**. Lo que importa es lo que **predice** el conjunto.
Preguntémosle por tres situaciones:
"""),

code(r"""def valor(situacion_inclinacion, situacion_velocidad, paso):
    r = np.array([1.0, situacion_inclinacion ** 2, situacion_velocidad ** 2,
                  situacion_inclinacion * situacion_velocidad, paso / 500])
    return r @ pesos_criticos

print(f"Derecho y quieto, al principio:     V = {valor(0, 0, 0):6.1f}")
print(f"Inclinado 15 y cayendo, al principio: V = {valor(15, 40, 0):6.1f}")
print(f"Derecho y quieto, casi al final:    V = {valor(0, 0, 480):6.1f}")"""),

md(r"""Dos predicciones son razonables: la situación ideal al principio vale mucho (unos 133 puntos, todo el episodio por delante), y casi al final vale bastante menos (unos 44: solo quedan 20
pasos). Pero la del medio es **imposible**: un valor de unos **−231**, cuando las recompensas nunca son negativas (el retorno es, como mínimo, 0). ¿Qué ha pasado?

Que el crítico ha visto datos de una política que **ya va bien** (pesos −12 y −6): el palo casi nunca llega a estar inclinado 15 grados y cayéndose a 40 grados por segundo. Le hemos preguntado
por una situación **muy lejos de todo lo que vio**, y una neurona lineal, fuera de sus datos, **se inventa** cualquier cosa (prolonga sus rectas hasta valores absurdos). Es el
**desplazamiento de distribución** del NB18, otra vez.

Esta es la lección honesta de este crítico: **una neurona lineal con unos pocos rasgos hechos a mano es un juez tosco**. Sirve como línea base (y verás enseguida que ayuda de verdad, porque
compara cada acción con situaciones parecidas a las que se dan), pero se equivoca en cuanto sale de lo conocido. Los algoritmos de verdad usan como crítico una **red neuronal** (NB19), que
aprende sus propios rasgos y juzga con mucha más finura. Lo haremos en cuanto tengamos PyTorch.
"""),

md(r"""## 5 · La gran comparación

Ahora juntemos las armas en una función de entrenamiento con interruptores: qué línea base usar (la media por paso del NB29, o el crítico) y si normalizar o no las ventajas. Y, como
aprendimos en el NB29, comparamos con **5 semillas** cada combinación, mirando en qué iteración supera los 490 puntos (si lo hace). (Esta celda tarda alrededor de un minuto: son 20
entrenamientos de 7.500 episodios cada uno.)
"""),

code(r"""def entrenar(linea_base, normalizar, tasa, sigma=5.0, iteraciones=150, n_episodios=50, semilla=0, gamma=0.99):
    generador = np.random.default_rng(semilla)
    pesos = np.zeros(2)
    historial = []
    for iteracion in range(iteraciones):
        obs, acc, med, rec, vivo = jugar(pesos, sigma, n_episodios, generador)
        historial.append((rec * vivo).sum(axis=0).mean())
        G = retornos_desde_cada_paso(rec, gamma)
        if linea_base == "media":
            ventajas = G - G.mean(axis=1, keepdims=True)
        elif linea_base == "critico":
            ventajas = G - rasgos(obs) @ ajustar_critico(obs, G, vivo)     # G − V(situación)
        if normalizar:
            ventajas = (ventajas - ventajas[vivo].mean()) / (ventajas[vivo].std() + 1e-8)
        pesos = pesos + tasa * direccion_de_mejora(obs, acc, med, ventajas, vivo, sigma)
    return pesos, historial

def primera_por_encima(historial, umbral=490):
    return next((i for i, x in enumerate(historial) if x > umbral), None)

configuraciones = [("media", False, 0.05), ("media", True, 0.3), ("critico", True, 0.3)]
curvas = {}
for linea_base, normalizar, tasa in configuraciones:
    llegadas = []
    for semilla in range(5):
        pesos, historial = entrenar(linea_base, normalizar, tasa, semilla=semilla)
        llegadas.append(primera_por_encima(historial))
        if semilla == 0:
            curvas[(linea_base, normalizar)] = historial
    nombre = f"{linea_base}{' + normalizar' if normalizar else ''}"
    print(f"{nombre:>22}: supera 490 en las iteraciones {llegadas}")"""),

md(r"""(`+ 1e-8` en la división es un truco para no dividir nunca entre cero, por si alguna vez todas las ventajas fueran iguales.)

Comparemos las tres configuraciones (las cifras exactas cambian un poco de semilla en semilla, pero el patrón es claro):

- **Línea base media** (la del NB29): aprende con las 5 semillas, tardando entre unas 50 y unas 95 iteraciones.
- **Media + normalizar**: algunas semillas van rapidísimas, otras siguen tardando: más irregular.
- **Crítico + normalizar**: la más **rápida y regular**: la mayoría de las semillas aprenden en **menos de 30** iteraciones.

Juzgar cada acción **en su contexto** (el crítico), con pasos de tamaño estable (normalizar), **más que duplica** la velocidad de aprendizaje. Veámoslo en las curvas de la semilla 0:
"""),

code(r"""plt.figure(figsize=(7, 3.5))
for (linea_base, normalizar), historial in curvas.items():
    plt.plot(historial, label=f"{linea_base}{' + normalizar' if normalizar else ''}")
plt.xlabel("iteración")
plt.ylabel("retorno medio")
plt.legend()
plt.grid(True, alpha=0.4)
plt.show()"""),

md(r"""## 6 · Arma 4: el descuento, de verdad

En el NB29 pusimos γ = 0,99 "porque sí". ¿Qué pasa con otros valores? Recuerda lo que hace γ: cuánto le importa a cada acción lo que pasa **lejos** en el futuro. Con γ = 0,9, una recompensa
a 50 pasos de distancia cuenta 0,9⁵⁰ ≈ 0,005 (casi nada); con γ = 0,99, cuenta 0,99⁵⁰ ≈ 0,6. Probemos la mejor configuración (crítico + normalizar) con varios γ, con 3 semillas cada uno:
"""),

code(r"""print("Peso de una recompensa a 50 pasos:", {g: round(g ** 50, 3) for g in [0.9, 0.95, 0.99, 1.0]})
for gamma in [0.9, 0.95, 0.99, 1.0]:
    llegadas = [primera_por_encima(entrenar("critico", True, 0.3, semilla=s, gamma=gamma)[1]) for s in range(3)]
    print(f"γ = {gamma}: supera 490 en las iteraciones {llegadas}")"""),

md(r"""Un resultado muy instructivo:

- Con **γ = 0,9**, **no aprende** (ninguna semilla llega). ¿Por qué? Porque una caída del palo tarda en fraguarse: un mal empujón ahora provoca la caída **decenas** de pasos después. Con
  γ = 0,9, una acción apenas "ve" lo que pasa a más de 10 o 20 pasos, así que **no se entera** de que causó la caída. Es un robot **miope**: solo ve lo inmediato.
- Con **γ = 0,95**, va un poco mejor, pero aún le cuesta.
- Con **γ = 0,99**, aprende bien: ve lo bastante lejos.
- Con **γ = 1** (sin descuento), también aprende, pero algo más despacio: ahora cada acción carga con **todo** lo que pasa hasta el final del episodio, incluidas cosas lejanísimas en las que no
  influyó, y eso añade ruido.

**γ define el "horizonte" del robot**: más o menos, cuántos pasos hacia el futuro le importan (una regla práctica: unos 1/(1 − γ) pasos; con 0,99, unos 100 pasos, 2 segundos en el palo). Tiene
que ser lo bastante largo para **ver las consecuencias de sus actos**, pero no tanto que se llene de ruido. Para un humanoide que anda, donde un mal paso se paga un segundo después, también se
usan valores en torno a 0,99.
"""),

md(r"""## 7 · Hacia dónde vamos: actor-crítico y PPO

Recapitulemos lo que tenemos ya:

- Un **actor** (la política) que explora y se mejora con el gradiente de la política (NB29).
- Un **crítico** (la función de valor) que aprende cuánto vale cada situación, y sirve para calcular la **ventaja** de cada acción en su contexto.
- **Normalización** y un buen **descuento** para domar el ruido.

Esto ya es, casi, un algoritmo **actor-crítico** moderno. Le faltan tres cosas, que veremos en las próximas lecciones:

1. **Redes neuronales** (NB19) en vez de neuronas sueltas, para el actor y para el crítico, entrenadas con **retropropagación automática** (eso es **PyTorch**, que ya hemos instalado en el
   ordenador: el próximo notebook).
2. Un crítico que se usa **paso a paso**, sin esperar a que acabe el episodio (estimando el futuro con el propio crítico: "lo que me dieron ahora + lo que el crítico dice que vale donde he
   llegado"). Así se aprende de episodios largos, o incluso infinitos, como andar.
3. Un **freno** para los pasos de aprendizaje demasiado grandes, y la posibilidad de **reutilizar** cada lote de episodios varias veces. Eso es **PPO** (*Proximal Policy Optimization*), el
   algoritmo con el que se entrenan hoy la mayoría de los humanoides.
"""),

md(r"""## 8 · Resumen de la lección

1. El enemigo del RL es el **ruido** (varianza) de la estimación del gradiente. Se **mide** repitiendo la estimación muchas veces: sin línea base, la dispersión era unas 2-4 veces mayor, y ni
   la dirección media era fiable con 2.000 episodios.
2. **Normalizar las ventajas** (media 0, desviación 1 en cada lote) hace que el tamaño de los pasos no dependa de la escala de los retornos.
3. El **crítico** aprende la **función de valor** V(s), el retorno esperado desde cada situación (aprendizaje supervisado sobre los G). Con **rasgos** (inclinación², velocidad²,
   inclinación × velocidad, momento del episodio) y **mínimos cuadrados** (`np.linalg.lstsq`). Un crítico lineal es un juez **tosco**: fuera de sus datos predice disparates (¡valores negativos!). La **ventaja** = G − V(s) compara cada acción con lo normal **en su situación**. Actor + crítico =
   **actor-crítico**.
4. **Crítico + normalizar** fue lo más rápido y regular (la mayoría de semillas, en menos de 30 iteraciones, frente a 50-95 con la línea base media).
5. El **descuento γ** fija el horizonte (≈ 1/(1 − γ) pasos): con 0,9 el robot es **miope** y no aprende; con 0,99, bien; con 1, algo más ruidoso.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Varianza (del gradiente)** | Cuánto se dispersan las estimaciones de "hacia dónde mejorar". |
| **Normalizar ventajas** | Dejarlas con media 0 y desviación 1 en cada lote. |
| **Función de valor, V(s)** | El retorno esperado desde una situación. |
| **Crítico / actor** | La pieza que juzga situaciones (V) / la que decide acciones (la política). |
| **Actor-crítico** | Arquitectura con un actor que aprende usando las ventajas que calcula un crítico. |
| **Rasgos (*features*)** | Datos fabricados a partir de la observación para alimentar una neurona. |
| **Mínimos cuadrados (`lstsq`)** | Encontrar de golpe los pesos de una neurona lineal que minimizan el error cuadrático. |
| **Horizonte** | Cuántos pasos hacia el futuro le importan al robot (≈ 1/(1 − γ)). |
| **Miope** | Un robot (γ pequeño) que solo ve las consecuencias inmediatas. |
| **PPO** | *Proximal Policy Optimization*: el algoritmo actor-crítico más usado en robótica (llegará). |
"""),

md(r"""## 9 · Ejercicios

**E1.** ¿Por qué el crítico usa la inclinación **al cuadrado** y no la inclinación tal cual?

**E2.** Calcula el horizonte aproximado (1/(1 − γ)) para γ = 0,9, 0,99 y 0,999. ¿Cuántos segundos son en el palo de escoba (cada paso, 0,02 s)?

**E3.** Pregúntale al crítico (la función `valor`) por el palo inclinado 5 grados pero **volviendo** hacia el centro a 20 grados por segundo (velocidad −20), al principio del episodio. ¿Vale más o
menos que inclinado 5 y cayendo (velocidad +20)? ¿Por qué?

**E4.** Repite la medición del ruido del apartado 2 pero usando el **crítico** como línea base. ¿Reduce la dispersión respecto a la media por paso? (Pista: copia `estimar_muchas_veces` y cambia
la línea de las ventajas por `G - rasgos(obs) @ ajustar_critico(obs, G, vivo)`.)

**E5.** Quita el rasgo del **momento** del crítico (deja solo 4 rasgos) y entrena con crítico + normalizar. ¿Empeora?

**E6.** **Reto.** ¿Por qué crees que el crítico tiene que volver a ajustarse en **cada** iteración, y no se ajusta una vez al principio y ya está?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

Porque lo que importa para el valor es **cuánto** está inclinado el palo, no hacia qué lado: inclinado 10 grados a la derecha o a la izquierda es igual de peligroso. Con la inclinación tal cual,
una neurona lineal daría valores **opuestos** para +10 y −10 (si uno sale bueno, el otro sale malo), y no podría captar que los dos son igual de malos. Con el **cuadrado**, +10 y −10 dan lo
mismo (100). El cuadrado "se come el signo" (NB04).
</details>

<details>
<summary>▶ Solución E2</summary>

- γ = 0,9 → 1/0,1 = **10 pasos** → 0,2 segundos.
- γ = 0,99 → 1/0,01 = **100 pasos** → 2 segundos.
- γ = 0,999 → 1/0,001 = **1.000 pasos** → 20 segundos (¡más largo que el propio episodio de 10 segundos!).

Con 0,9, el robot solo "ve" dos décimas de segundo hacia delante: demasiado poco para notar que un empujón provocará una caída un segundo después.
</details>

<details>
<summary>▶ Solución E3</summary>

```python
print(valor(5, -20, 0), valor(5, 20, 0))
```

Lo lógico sería que "inclinado 5 pero **volviendo**" valiera **más** que "inclinado 5 y **cayendo**" (es el problema de la foto del NB03). Pero si lo ejecutas, verás que este crítico dice **lo
contrario**: le da más valor a "cayendo". Es un error del crítico, y tiene explicación: el peso del rasgo inclinación × velocidad le salió **positivo** (apartado 4), así que premia que la
inclinación y la velocidad tengan el mismo signo, es decir, caer. Con rasgos relacionados entre sí y datos de una sola política, una neurona lineal puede aprender relaciones absurdas que, en
los datos que vio, "casualmente" ayudaban a predecir.

La lección: **no te fíes de un modelo solo porque su error medio sea bajo; pregúntale por casos concretos y comprueba que tiene sentido**. Este es un ejemplo perfecto de por qué los críticos de
verdad son redes neuronales, y de por qué los ingenieros "interrogan" a sus modelos antes de confiar en ellos.
</details>

<details>
<summary>▶ Solución E4</summary>

```python
def estimar_con_critico(repeticiones=40):
    generador = np.random.default_rng(7)
    estimaciones = []
    for r in range(repeticiones):
        obs, acc, med, rec, vivo = jugar(pesos_fijos, 5.0, 50, generador)
        G = retornos_desde_cada_paso(rec)
        ventajas = G - rasgos(obs) @ ajustar_critico(obs, G, vivo)
        estimaciones.append(direccion_de_mejora(obs, acc, med, ventajas, vivo, 5.0))
    return np.array(estimaciones)

e = estimar_con_critico()
print(e.mean(axis=0).round(1), e.std(axis=0).round(1))
```

Con estos pesos fijos y este crítico tan sencillo, la dispersión sale **parecida** a la de la media por paso, incluso un poco **mayor** (del orden de 10 y 25, frente a 9,5 y 20). ¿Entonces por qué el crítico aprendía más rápido en el apartado 5?
Porque allí iba **junto con normalizar**, y porque un crítico mejora a medida que la política mejora y los episodios se alargan (con episodios largos y situaciones muy distintas entre sí, juzgar
"en contexto" importa cada vez más). Es una lección de método valiosa: **una idea puede no ayudar en una medición concreta y sí en el conjunto**; por eso hay que medir de varias formas.
</details>

<details>
<summary>▶ Solución E5</summary>

Cambia `rasgos` para que no incluya `momento` (quítalo de la lista de `np.stack`) y vuelve a entrenar con `entrenar("critico", True, 0.3, semilla=s)`. Sin el momento, el crítico no sabe que cerca
del final quedan pocas recompensas, y sus predicciones empeoran en esa parte del episodio: las ventajas de las acciones del final quedan sesgadas. Pruébalo con varias semillas y compara las
iteraciones hasta 490 con las del apartado 5.
</details>

<details>
<summary>▶ Solución E6</summary>

Porque el **valor de una situación depende de la política** que se está usando. Con la política del principio (que no sabe nada), una situación "algo inclinado" vale poquísimo (se caerá enseguida);
con la política ya entrenada, la misma situación vale casi 500 (la sabe corregir). Como la política cambia en cada iteración, el crítico tiene que **seguirle el ritmo**: en los algoritmos
actor-crítico, actor y crítico aprenden **a la vez**, sin parar.
</details>
"""),

md(r"""## 10 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has aprendido a medir y domar el ruido, has construido tu primer **crítico**, y has visto que el descuento define lo lejos que "ve" un robot. En el **NB31** llega la herramienta que usa toda la
industria para construir y entrenar redes neuronales: **PyTorch**. Verás que hace **sola** la retropropagación que escribiste a mano en el NB19 (se llama **autograd**), y rehicimos en unas pocas
líneas lo que nos costó una lección entera. Con PyTorch, el actor y el crítico podrán ser **redes neuronales** de verdad.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB30_ruido_critico_descuento.ipynb")
    build(out, cells, title="NB30 · Domar el ruido: ventaja, normalización, crítico y descuento")
