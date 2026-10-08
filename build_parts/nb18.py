"""Construye NB18 · Aprender imitando: el aprendizaje supervisado (Parte 2 · Lección 7).

Aprender de un maestro (conducir, cocinar): ejemplos (observación, acción del
maestro). Grabar 300 ejemplos de la política a mano (−30·i − 8·v) en el palo de
escoba (3 episodios × 100 pasos). Neurona alumna (w1, w2, b). Error, error al
cuadrado y ERROR CUADRÁTICO MEDIO = la pérdida (305,6 con todo a 0; 0 con
−30/−8). La pérdida como valle (gráfica vs w1). Descenso con gradiente numérico.
La regla de la cadena con engranajes → el gradiente exacto
2·media(error × entrada), que coincide con el numérico (14,7596) y calcula
todas las pendientes de golpe. Entrenamiento: tasa 0,2 → (−30,0; −8,0; 0,0) y
curva de la pérdida; tasa 0,3 → explota (6e18). El alumno juega: 499,9. Maestro
con ruido ±10 → (−29,7; −8,0). Límites: el alumno solo ve lo que ve el maestro
(desplazamiento de distribución). Imitación en humanoides reales.
Práctica en MuJoCo: maestro PD (3; 0,8; 0,1; 0,2) en el palo de escoba de
MuJoCo (vídeo); 10 demostraciones × 300 pasos al azar → 3.000 ejemplos (matriz
3000×4); alumno lineal con la regla de la cadena (1.000 pasos, tasa 0,5). Datos
limpios: pérdida baja pero pesos (1,51; −0,24; ...) y se cae en 0,81 s (valle
alargado, desplazamiento de distribución). Con temblor ±1 al ejecutar
(etiqueta = lo que quería): redescubre (2,994; 0,799; 0,099; 0,2), 10 s (vídeo,
idea tipo DART). Retos: 3.000 pasos limpios, temblor 0,3, solo 2 episodios.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB18 · Aprender imitando: el aprendizaje supervisado

**Parte 2 · Matemáticas y herramientas para robots — Lección 7**

> En el **NB17** escribiste el algoritmo más importante de la inteligencia artificial: **seguir el gradiente**. Lo usaste para que el palo de
> escoba subiera por la montaña de su retorno. Pero viste el problema: cada paso cuesta **2 evaluaciones por ruedecilla**, y con miles de
> ruedecillas eso es carísimo.

Hoy vamos a ver una forma de aprender **distinta**, muy potente, y en la que ese problema **desaparece**: aprender **imitando** a un maestro.

En vez de que el robot pruebe y se guíe por la recompensa, le enseñaremos **ejemplos** de lo que hace alguien que ya sabe: "en esta situación,
el maestro empujó tanto". Y el robot ajustará sus ruedecillas para **parecerse** al maestro lo más posible. A esto se le llama **aprendizaje
supervisado** (porque hay un "supervisor" que dice la respuesta correcta), y es la forma en la que aprenden la mayoría de las inteligencias
artificiales que conoces.

En esta lección:

- Grabarás ejemplos de la política buena del palo de escoba.
- Medirás cuánto se equivoca una neurona con un número: el **error cuadrático medio**.
- Descubrirás la **regla de la cadena**, que permite calcular **todas las pendientes de golpe**.
- Y verás a la neurona **redescubrir sola** los números −30 y −8.
"""),

md(r"""## 1 · Dos formas de aprender

Piensa en cómo aprendes las cosas en la vida:

- **Probando** (aprendizaje por refuerzo): aprendes a montar en bici cayéndote y volviendo a subir. Nadie te dice qué hacer en cada
  instante; solo sabes si te caes o no (la recompensa). Lento, pero no necesitas a nadie.
- **Imitando** (aprendizaje supervisado): aprendes a cocinar viendo a alguien que sabe, o a conducir mirando a tu padre o a tu madre, y
  luego intentando hacer **lo mismo** que ellos. Mucho más rápido... pero necesitas un **maestro** que ya sepa.

| | Aprender probando (refuerzo) | Aprender imitando (supervisado) |
|---|---|---|
| ¿Qué recibe el robot? | Una **recompensa**: "bien" o "mal" | La **respuesta correcta**: "aquí había que hacer esto" |
| ¿Necesita un maestro? | No | Sí |
| ¿Puede superar al maestro? | Sí | Difícilmente: como mucho, lo iguala |
| Velocidad | Lento (millones de intentos) | Rápido |

En robótica se usan **las dos**, y muchas veces **juntas**: primero el robot imita (por ejemplo, grabaciones de personas andando) para
empezar con una política razonable, y luego practica con refuerzo para mejorarla. Hoy vamos a por la imitación.

¿Y quién es nuestro maestro? La política **escrita a mano** del NB11, la que mantenía el palo de pie: empuje = −30 × inclinación − 8 ×
velocidad. El alumno será una neurona (NB13) que **no sabe** esos números. Si aprende bien, debería descubrirlos.
"""),

md(r"""## 2 · Grabar los ejemplos del maestro

Primero necesitamos **ejemplos**: situaciones (observaciones) y lo que el maestro hizo en cada una. Pondremos al maestro a jugar 3 episodios
del palo de escoba, de 100 pasos cada uno, y en cada paso apuntaremos tres números en tres listas: la **inclinación**, la **velocidad** y el
**empuje** que decidió el maestro.

El mundo es el del NB11 (sin batería, como en el original). El código ya lo conoces; lo nuevo son solo las tres listas:
"""),

code(r"""import random
import numpy as np

def maestro(inclinacion, velocidad):
    return -30 * inclinacion - 8 * velocidad

inclinaciones = []
velocidades = []
empujes_del_maestro = []

for semilla in range(3):
    random.seed(semilla)
    inclinacion = 2.0
    velocidad = 0.0
    for n in range(100):
        empuje = maestro(inclinacion, velocidad)
        # apuntamos el ejemplo: la situación y lo que hizo el maestro
        inclinaciones.append(inclinacion)
        velocidades.append(velocidad)
        empujes_del_maestro.append(empuje)
        # y el mundo avanza, como en el NB11
        empuje = max(-40, min(40, empuje))
        aceleracion = 10 * inclinacion + empuje + random.uniform(-30, 30)
        velocidad = velocidad + aceleracion * 0.02
        inclinacion = inclinacion + velocidad * 0.02

inclinaciones = np.array(inclinaciones)
velocidades = np.array(velocidades)
empujes_del_maestro = np.array(empujes_del_maestro)
print("Ejemplos grabados:", len(empujes_del_maestro))"""),

md(r"""(Una pequeña novedad: `max(-40, min(40, empuje))` recorta el empuje a ±40 en una sola línea: `min` se queda con el menor entre 40 y el
empuje, y `max`, con el mayor entre −40 y eso. Es lo mismo que los dos `if` del NB11.)

**300 ejemplos**, y al final los hemos convertido en arrays de NumPy (NB15) para calcular cómodamente. A este conjunto de ejemplos se le llama
**datos de entrenamiento** (o **conjunto de datos**, en inglés *dataset*). Miremos los cinco primeros:
"""),

code(r"""for k in range(5):
    print("inclinación", round(inclinaciones[k], 3), "| velocidad", round(velocidades[k], 3),
          "| el maestro empujó", round(empujes_del_maestro[k], 2))"""),

md(r"""Cada fila es un ejemplo: "en **esta** situación, el maestro empujó **esto**". Al principio el palo está inclinado 2 grados y el maestro empuja
con fuerza (−60) para enderezarlo; enseguida el palo empieza a moverse y el maestro ajusta. Al empuje del maestro, que es "la respuesta
correcta", se le llama **etiqueta** (como la etiqueta de la solución pegada a cada ejercicio).
"""),

md(r"""## 3 · El alumno, y cuánto se equivoca

El **alumno** es una neurona (NB13) con dos pesos, `w1` (para la inclinación) y `w2` (para la velocidad), y un sesgo `b`. Su respuesta, para
cada ejemplo, es su **predicción**: lo que **él** empujaría.

```
   predicción = w1 × inclinación + w2 × velocidad + b
```

Al principio no sabe nada: todo a 0. Así que siempre predice "empuja 0". ¿Cómo de mal lo hace? Para cada ejemplo, el **error** es la
diferencia entre lo que predice y lo que hizo el maestro:

```
   error = predicción − lo que hizo el maestro
```

Pero tenemos 300 ejemplos, y queremos **un solo número** que diga "cuánto se equivoca en total". Podríamos hacer la media de los errores... pero
hay un problema: unos errores son positivos (empujó de más) y otros negativos (empujó de menos), y **se compensarían**, dando una media
engañosamente pequeña. La solución ya la conoces del NB04: **elevar al cuadrado**. El cuadrado se come el signo y además castiga mucho más los
errores grandes que los pequeños. Así que:

> **Error cuadrático medio** = la **media** de los **errores al cuadrado** de todos los ejemplos.

Es el número que mide "cuánto se equivoca el alumno", y al que se le llama **pérdida** (en inglés, *loss*). **Cuanto más pequeña, mejor**: una
pérdida de 0 significaría que el alumno imita **perfectamente** al maestro. Con NumPy (NB15) se calcula en una línea, para los 300 ejemplos a la
vez:
"""),

code(r"""def perdida(w1, w2, b):
    predicciones = w1 * inclinaciones + w2 * velocidades + b
    errores = predicciones - empujes_del_maestro
    return np.mean(errores ** 2)

print("Pérdida del alumno que no sabe nada (todo a 0):", round(perdida(0, 0, 0), 1))
print("Pérdida si acertara los pesos del maestro:     ", round(perdida(-30, -8, 0), 1))"""),

md(r"""El alumno ignorante tiene una pérdida de **305,6**. Y si tuviera exactamente los pesos del maestro (−30, −8, 0), la pérdida sería **0**: imitación
perfecta. **El objetivo del aprendizaje es bajar la pérdida de 305,6 a 0.** Y para bajar... ¡descenso por gradiente (NB17)!
"""),

md(r"""## 4 · La pérdida es un valle

En el NB17 subíamos una **montaña** (el retorno: cuanto más, mejor). Ahora queremos **bajar a un valle** (la pérdida: cuanto menos, mejor). Es lo
mismo con el signo cambiado: en vez de x + tasa × pendiente, **x − tasa × pendiente** (ir **en contra** de la pendiente es ir cuesta abajo; ejercicio
E2 del NB17).

Dibujemos el valle. Dejamos `w2` en −8 y `b` en 0, y miramos cómo cambia la pérdida al mover solo `w1`:
"""),

code(r"""import matplotlib.pyplot as plt

valores_w1 = []
perdidas = []
for i in range(-60, 1):
    valores_w1.append(i)
    perdidas.append(perdida(i, -8, 0))

plt.figure(figsize=(6, 3.5))
plt.plot(valores_w1, perdidas, color="tab:blue")
plt.grid(True, alpha=0.4)
plt.xlabel("peso w1 (inclinación)")
plt.ylabel("pérdida")
plt.show()"""),

md(r"""¡Una parábola (NB16), con el fondo **justo en −30**! Ahí la pérdida es 0. Si el peso es menor o mayor, el alumno empuja de más o de menos, y la
pérdida sube. Encontrar el fondo de este valle es encontrar el peso del maestro.

Podríamos bajar con el **gradiente numérico** del NB17 (moviendo cada ruedecilla un poquito a cada lado). Funcionaría. Pero hoy vamos a aprender
algo mucho mejor: calcular la pendiente **exacta**, de **todas** las ruedecillas, **de golpe**. Para eso necesitamos una idea nueva.
"""),

md(r"""## 5 · La regla de la cadena: engranajes

En el NB17b viste la regla de la cadena con funciones sueltas. Aquí la vamos a aplicar a algo de verdad: el error de una máquina que aprende. Recordemos la idea con tres **engranajes** conectados: A mueve a B, y B mueve a C.

```
       A ────► B ────► C
     (si A gira 1 vuelta, B gira 2)    (si B gira 1 vuelta, C gira 3)

     ¿Cuánto gira C si A gira 1 vuelta?   →   2 × 3 = 6 vueltas
```

Si cada vuelta de A da **2** vueltas de B, y cada vuelta de B da **3** de C, entonces cada vuelta de A da **2 × 3 = 6** vueltas de C. Para saber
cuánto afecta A a C, **se multiplican** los efectos de cada eslabón de la cadena.

Eso es la **regla de la cadena**, una de las reglas más importantes del cálculo: **cuando una cosa afecta a otra a través de pasos intermedios,
la pendiente total es el producto de las pendientes de cada paso.**

Apliquémosla a nuestra pérdida. ¿Cómo afecta el peso `w1` a la pérdida? A través de una cadena:

```
   w1  ────►  predicción  ────►  error  ────►  error al cuadrado (la pérdida de ese ejemplo)
```

Eslabón a eslabón:

1. **w1 → predicción.** La predicción es w1 × inclinación + ... Si w1 aumenta 1, la predicción aumenta **inclinación** (lo que valga la inclinación
   de ese ejemplo). Pendiente de este eslabón: **la inclinación**.
2. **predicción → error.** El error es predicción − maestro. Si la predicción sube 1, el error sube 1. Pendiente: **1**.
3. **error → error al cuadrado.** ¡Esto lo descubriste en el NB16! La pendiente de x² es **2x**. Así que la pendiente de error² es **2 × error**.

Multiplicando los eslabones, como los engranajes:

```
   pendiente de la pérdida respecto a w1 (en un ejemplo)  =  inclinación × 1 × 2 × error  =  2 × error × inclinación
```

Y como la pérdida total es la **media** de todos los ejemplos, su pendiente es la **media** de las pendientes de cada ejemplo:

> **pendiente respecto a w1 = 2 × media( error × inclinación )**
> **pendiente respecto a w2 = 2 × media( error × velocidad )**
> **pendiente respecto a b  = 2 × media( error )** (el sesgo no se multiplica por nada: su "entrada" es siempre 1)

Fíjate en lo que dice la fórmula, porque tiene todo el sentido: **cada ejemplo empuja cada peso en proporción a su error y a su entrada**. Si en
un ejemplo el alumno empujó de más (error positivo) y la inclinación era grande, ese peso tiene mucha "culpa" y hay que corregirlo bastante. Si la
inclinación era casi 0, ese peso apenas influyó en el error, y apenas se toca. **Es la asignación del mérito del NB04, resuelta con matemáticas.**
"""),

md(r"""### Comprobémoslo

Una regla nueva no se cree: se **comprueba** (NB07). Calculemos la pendiente respecto a w1 de las dos maneras, en un punto cualquiera (por
ejemplo, w1 = −10, w2 = −2, b = 0): con el gradiente numérico del NB17, y con la fórmula de la regla de la cadena:
"""),

code(r"""w1, w2, b = -10.0, -2.0, 0.0

# Forma 1: gradiente numérico (mover w1 un poquito a cada lado, NB16-17)
h = 0.0001
numerica = (perdida(w1 + h, w2, b) - perdida(w1 - h, w2, b)) / (2 * h)

# Forma 2: la regla de la cadena
errores = (w1 * inclinaciones + w2 * velocidades + b) - empujes_del_maestro
exacta = 2 * np.mean(errores * inclinaciones)

print("Pendiente numérica:            ", round(numerica, 4))
print("Pendiente con regla de cadena: ", round(exacta, 4))"""),

md(r"""**¡Idénticas!** (14,7596 las dos.) La regla de la cadena funciona.

¿Y cuál es la gran ventaja? Mira la **forma 2**: con **una sola** pasada por los datos (calcular los errores una vez) obtenemos la pendiente de w1;
y con esos **mismos** errores, multiplicando por las velocidades, la de w2; y haciendo su media, la de b. **Todas las pendientes de golpe**, sin
tener que mover cada ruedecilla por separado. Con 3 ruedecillas no se nota mucho. Con 5.933 (o con los millones de una red grande), la diferencia
es la que hay entre **posible** e **imposible**.

Esta idea, aplicar la regla de la cadena hacia atrás, eslabón a eslabón, para calcular de golpe las pendientes de todos los pesos, es la famosa
**retropropagación** que anunciamos en el NB17 (en inglés, *backpropagation*: "propagar hacia atrás"). En una red de varias capas la cadena es más
larga, pero la idea es exactamente la de los engranajes.
"""),

md(r"""## 6 · ¡A entrenar!

Ya tenemos todo. El bucle de entrenamiento: empezar con todo a 0, y en cada paso, calcular los errores, las tres pendientes con la regla de la
cadena, y **bajar** (restar tasa × pendiente). Guardamos la pérdida de cada paso para dibujarla después:
"""),

code(r"""w1, w2, b = 0.0, 0.0, 0.0
tasa = 0.2
historial = []

for paso in range(200):
    # 1. lo que predice el alumno, y cuánto se equivoca en cada ejemplo
    errores = (w1 * inclinaciones + w2 * velocidades + b) - empujes_del_maestro
    historial.append(np.mean(errores ** 2))
    # 2. todas las pendientes de golpe (regla de la cadena)
    pendiente_w1 = 2 * np.mean(errores * inclinaciones)
    pendiente_w2 = 2 * np.mean(errores * velocidades)
    pendiente_b = 2 * np.mean(errores)
    # 3. un paso cuesta ABAJO (descenso por gradiente)
    w1 = w1 - tasa * pendiente_w1
    w2 = w2 - tasa * pendiente_w2
    b = b - tasa * pendiente_b

print("Pesos aprendidos: w1 =", round(w1, 3), "| w2 =", round(w2, 3), "| b =", round(b, 3))
print("Pérdida final:", perdida(w1, w2, b))"""),

md(r"""**w1 = −30, w2 = −8, b = 0.** ¡El alumno ha **redescubierto** exactamente los números del maestro! Nadie se los ha dicho: solo ha visto 300
ejemplos de lo que hacía el maestro, y ha bajado por la pendiente de su error hasta imitarlo perfectamente. La pérdida final es un número minúsculo
(en notación científica, NB14: prácticamente 0).

Esta es la **curva de aprendizaje**, la pérdida paso a paso:
"""),

code(r"""plt.figure(figsize=(6, 3.5))
plt.plot(historial, color="tab:red")
plt.grid(True, alpha=0.4)
plt.xlabel("paso de entrenamiento")
plt.ylabel("pérdida")
plt.yscale("log")         # escala especial: cada raya es 10 veces menos que la anterior
plt.show()"""),

md(r"""La pérdida **baja sin parar**, de 305 a casi cero. (Hemos usado una **escala logarítmica** en el eje vertical, NB15b: en vez de ir de 10 en 10, cada raya
es **10 veces** más pequeña que la anterior, 100, 10, 1, 0,1... Así se ve bien una caída tan enorme. Es la escala que usan los profesionales para
mirar curvas de aprendizaje.)

**Mirar esta curva es lo primero que hace cualquier ingeniero** mientras entrena una red: si baja, todo va bien; si se estanca, algo falla; y si
**sube**... cuidado.
"""),

md(r"""### La tasa, otra vez

¿Recuerdas que en el NB17 una tasa demasiado grande hacía **explotar** el ascenso? Probemos aquí con tasa **0,3** en vez de 0,2. Una función que
entrena con la tasa que le digamos y devuelve los pesos y la pérdida final:
"""),

code(r"""def entrenar(tasa, pasos):
    w1, w2, b = 0.0, 0.0, 0.0
    for paso in range(pasos):
        errores = (w1 * inclinaciones + w2 * velocidades + b) - empujes_del_maestro
        w1 = w1 - tasa * 2 * np.mean(errores * inclinaciones)
        w2 = w2 - tasa * 2 * np.mean(errores * velocidades)
        b = b - tasa * 2 * np.mean(errores)
    return w1, w2, b

for tasa in [0.01, 0.2, 0.3]:
    w1, w2, b = entrenar(tasa, 200)
    print("tasa", tasa, "-> w1 =", round(w1, 2), "| w2 =", round(w2, 2), "| pérdida =", perdida(w1, w2, b))"""),

md(r"""- Con **0,01**, tras 200 pasos aún va por la mitad del camino (w1 ≈ −18): demasiado lenta.
- Con **0,2**, perfecta.
- Con **0,3**, ¡**explota**! Los pesos se disparan a cientos de millones y la pérdida a un número con **18 cifras** (`e+18`). Con solo subir la tasa
  de 0,2 a 0,3.

La frontera entre "aprende perfectamente" y "explota" puede ser **así de fina**. Por eso los profesionales vigilan la curva de aprendizaje y, si
ven que la pérdida se dispara, lo primero que hacen es **bajar la tasa**.
"""),

md(r"""## 7 · El alumno juega

Que el alumno imite al maestro **en los ejemplos** está muy bien. Pero lo que de verdad importa es: **¿sabe mantener el palo de pie?** Vamos a
ponerlo a jugar en el mundo del NB11, con sus pesos aprendidos como política (y otra vez la media de 5 episodios, como en el NB11):
"""),

code(r"""def evaluar(w1, w2, b):
    total = 0
    for semilla in range(5):
        random.seed(semilla)
        inclinacion = 2.0
        velocidad = 0.0
        for n in range(500):
            empuje = w1 * inclinacion + w2 * velocidad + b        # LA POLÍTICA DEL ALUMNO
            empuje = max(-40, min(40, empuje))
            aceleracion = 10 * inclinacion + empuje + random.uniform(-30, 30)
            velocidad = velocidad + aceleracion * 0.02
            inclinacion = inclinacion + velocidad * 0.02
            if inclinacion > 30 or inclinacion < -30:
                break
            total = total + 1 - (inclinacion / 30) ** 2
    return total / 5

w1, w2, b = entrenar(0.2, 200)
print("El alumno bien entrenado:", round(evaluar(w1, w2, b), 1), "puntos")

w1, w2, b = entrenar(0.01, 200)
print("El alumno a medio aprender (w1 =", round(w1, 1), ", w2 =", round(w2, 1), "):", round(evaluar(w1, w2, b), 1), "puntos")"""),

md(r"""El alumno bien entrenado saca **499,9**, exactamente como el maestro (lógico: tiene sus mismos pesos). Y fíjate en el segundo: el alumno **a medio
aprender**, con unos pesos que aún están lejos de los del maestro, ¡**también** mantiene el palo de pie (499,8)! No hace falta imitar al maestro
perfectamente; basta con parecerse **lo suficiente**. (Recuerda el NB11: había muchísimas combinaciones de ruedecillas que funcionaban.)

**Ha aprendido a mantener el palo de pie sin jugar ni un solo episodio**, solo mirando cómo lo hacía otro. Esa es la fuerza de la imitación.
"""),

md(r"""## 8 · Un maestro que no es perfecto

En la vida real, los maestros se equivocan. Si grabas a una persona manejando un robot con un mando, a veces empujará un poco de más y a veces un
poco de menos. ¿Qué aprende el alumno de un maestro imperfecto?

Vamos a "estropear" las etiquetas: a cada empuje del maestro le sumamos un error al azar entre −10 y +10, como si tuviera el pulso tembloroso. Y
entrenamos otra vez, con más pasos:
"""),

code(r"""random.seed(99)
empujes_limpios = empujes_del_maestro.copy()          # guardamos los buenos para luego
temblores = []
for k in range(len(empujes_del_maestro)):
    temblores.append(random.uniform(-10, 10))
empujes_del_maestro = empujes_limpios + np.array(temblores)

w1, w2, b = entrenar(0.2, 500)
print("Con un maestro tembloroso: w1 =", round(w1, 2), "| w2 =", round(w2, 2), "| b =", round(b, 2))
print("Pérdida final:", round(perdida(w1, w2, b), 1))

empujes_del_maestro = empujes_limpios                  # dejamos los datos como estaban"""),

md(r"""(`.copy()` hace una **copia** del array, para poder recuperar los datos buenos al final. Si no, `empujes_limpios` y `empujes_del_maestro` serían el
mismo array con dos nombres, y al cambiar uno cambiaría el otro.)

El alumno aprende **w1 ≈ −29,7 y w2 ≈ −8,0**: muy cerca de los −30 y −8 de verdad, aunque **ningún** ejemplo tenía el empuje exacto. Los temblores son
al azar, unos hacia arriba y otros hacia abajo, y al hacer la media de muchos ejemplos **se compensan**. El alumno ha aprendido "lo que el maestro
**quería** hacer", no sus temblores. (La pérdida ya no baja a 0, sino a unos 31: es el error que no se puede eliminar, porque los temblores son puro
azar.) Por eso, en aprendizaje supervisado, **más datos** suelen dar mejores resultados: más ejemplos, más se compensan los errores.
"""),

md(r"""## 9 · El punto débil de imitar

La imitación tiene un problema famoso, y es importante que lo conozcas. Fíjate en los datos que hemos grabado: el maestro es **muy bueno**, así que el
palo casi siempre estuvo **casi derecho**. El alumno solo ha visto situaciones "tranquilas".

¿Qué pasa si el alumno, por un pequeño error, llega a una situación que el maestro **nunca** vivió (por ejemplo, el palo inclinado 20 grados)? No ha
visto ningún ejemplo así. En nuestro caso tenemos suerte: la política es una simple neurona lineal, y "extiende" su regla de forma razonable. Pero con
una política compleja (una red neuronal grande), el alumno podría hacer **cualquier disparate** en situaciones nuevas, que lo llevarían a situaciones
aún más raras, y así hasta caerse. Los errores se **acumulan**, como el ruido de los pasos del NB07.

A esto se le llama **desplazamiento de distribución** (en inglés, *distribution shift*): el alumno se encuentra con situaciones **distintas** de las que
vio al aprender. Es una de las razones por las que, en robótica, la imitación **se combina** con el aprendizaje por refuerzo: imitar da un buen punto de
partida, y practicar (refuerzo) enseña a recuperarse de los propios errores. (Y es pariente de la brecha de realidad del NB02: el mundo real también es
"una situación que no se vio al entrenar".)
"""),

md(r"""## 10 · La imitación en los humanoides de verdad

Lo que has hecho hoy, a pequeña escala, se usa muchísimo con humanoides reales:

- Se **graban personas** moviéndose (andando, corriendo, bailando) con trajes llenos de sensores o con cámaras, y el robot aprende a **imitar** esos
  movimientos. A esto se le llama **imitación de movimiento**, y es una de las razones por las que algunos humanoides andan de una forma tan "humana".
- Se **manejan robots a distancia** (teleoperación: una persona controla el robot con un mando o con su propio cuerpo) mientras se graba todo, y luego el
  robot aprende de esas grabaciones a hacer la tarea **él solo**.
- Y casi siempre, después de imitar, el robot **practica con refuerzo** para mejorar y para aprender a recuperarse de sus propios errores.

El "maestro" cambia, la red neuronal es mucho más grande, pero el corazón es **exactamente** lo de hoy: ejemplos, una pérdida, la regla de la cadena y
el descenso por gradiente.
"""),

md(r"""## 11 · Resumen de la lección

1. **Aprendizaje supervisado** (imitación): el alumno aprende de **ejemplos** con la respuesta correcta (**etiquetas**), en vez de una recompensa. Rápido,
   pero necesita un maestro. Grabamos **300 ejemplos** (datos de entrenamiento) de la política a mano del palo de escoba.
2. La **pérdida** mide cuánto se equivoca el alumno: el **error cuadrático medio** (media de los errores al cuadrado). Todo a 0: 305,6; con los pesos del
   maestro: 0. Aprender es **bajar al valle** de la pérdida (descenso por gradiente).
3. La **regla de la cadena** (engranajes: las pendientes de cada eslabón **se multiplican**) da las pendientes exactas: pendiente de w = **2 × media(error ×
   entrada)**. Coincide con la numérica y calcula **todas las pendientes de golpe**: es la base de la **retropropagación**.
4. Entrenando con tasa 0,2, el alumno **redescubre −30 y −8**, y mantiene el palo (499,9) sin haber jugado nunca. Con tasa 0,3, **explota**. La **curva de
   aprendizaje** (en escala logarítmica) muestra cómo baja la pérdida.
5. Con un maestro tembloroso, los errores al azar **se compensan** (aprende ≈ −29,7 y −8,0). El punto débil: el **desplazamiento de distribución** (el
   alumno solo sabe de las situaciones que vio). Por eso se combina con el refuerzo.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Aprendizaje supervisado** | Aprender de ejemplos con la respuesta correcta. |
| **Datos de entrenamiento (*dataset*)** | El conjunto de ejemplos para aprender. |
| **Etiqueta** | La respuesta correcta de cada ejemplo (aquí, el empuje del maestro). |
| **Predicción** | Lo que responde el alumno para un ejemplo. |
| **Error cuadrático medio** | La media de los errores al cuadrado. |
| **Pérdida (*loss*)** | El número que mide cuánto se equivoca el alumno; hay que hacerlo pequeño. |
| **Regla de la cadena** | Las pendientes de una cadena de pasos se multiplican (como engranajes). |
| **Retropropagación** | Aplicar la regla de la cadena hacia atrás para tener todas las pendientes de golpe. |
| **Curva de aprendizaje** | La pérdida dibujada paso a paso durante el entrenamiento. |
| **Escala logarítmica** | Un eje donde cada raya es 10 veces la anterior. |
| **Desplazamiento de distribución** | Encontrarse situaciones distintas de las vistas al aprender. |
| **Imitación de movimiento** | Robots que aprenden a moverse imitando grabaciones de personas. |
"""),

md(r"""## 12 · Ejercicios

**E1.** Un alumno predice 10, 20 y 30 en tres ejemplos cuyas etiquetas son 12, 20 y 25. Calcula a mano su error cuadrático medio.

**E2.** ¿Por qué no usamos simplemente la media de los errores (sin elevar al cuadrado)? Pon un ejemplo con dos errores en el que la media de los
errores sea 0 aunque el alumno se equivoque mucho.

**E3.** Con los engranajes: si A → B tiene un efecto de 4 y B → C un efecto de 0,5, ¿cuánto se mueve C cuando A se mueve 1? ¿Y si B → C fuera −2?

**E4.** Entrena con tasa **0,25**. ¿Aprende o explota? (Pista: está entre 0,2 y 0,3.)

**E5.** Entrena con tasa 0,2 pero solo **10** pasos. ¿Qué pesos aprende? ¿Mantiene el palo de pie? Usa `evaluar`.

**E6.** **Reto.** Graba ejemplos de un maestro **distinto**: `-50 * inclinacion - 12 * velocidad`. (Tendrás que cambiar la función `maestro` y volver a
ejecutar la celda de grabar los ejemplos.) ¿Descubre el alumno los nuevos números?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

Errores: 10 − 12 = −2; 20 − 20 = 0; 30 − 25 = 5. Al cuadrado: 4, 0, 25. Media: (4 + 0 + 25) / 3 = 29 / 3 ≈ **9,67**.
</details>

<details>
<summary>▶ Solución E2</summary>

Porque los errores positivos y negativos **se compensan**. Ejemplo: el alumno predice 0 donde la etiqueta es 100 (error −100) y 200 donde la etiqueta es 100
(error +100). La media de los errores es (−100 + 100) / 2 = **0**: ¡parece perfecto! Pero se ha equivocado en 100 las dos veces. Con los cuadrados: (10.000 +
10.000) / 2 = 10.000, que sí refleja lo mal que lo hace.
</details>

<details>
<summary>▶ Solución E3</summary>

Se multiplican: 4 × 0,5 = **2**. Si A se mueve 1, C se mueve 2. Con B → C = −2: 4 × (−2) = **−8**: C se mueve 8, pero **al revés**. (Un engranaje con efecto
negativo invierte el sentido, como dos ruedas dentadas que encajan y giran en sentidos opuestos.)
</details>

<details>
<summary>▶ Solución E4</summary>

```python
w1, w2, b = entrenar(0.25, 200)
print(w1, w2, perdida(w1, w2, b))
```

Con **0,25** todavía **aprende**: llega a w1 = −30 y w2 = −8, con una pérdida minúscula. Así que la frontera entre "aprende" y "explota"
está entre **0,25 y 0,3**. Este tipo de prueba ("¿qué tasa es la más grande que no explota?") es algo que los profesionales hacen constantemente.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
w1, w2, b = entrenar(0.2, 10)
print(round(w1, 2), round(w2, 2), round(b, 2))
print(round(evaluar(w1, w2, b), 1))
```

Con solo 10 pasos, el alumno aprende algo como **w1 ≈ −18,9, w2 ≈ −5,2 y b ≈ −4,2**: aún lejos de −30 y −8. ¡Y sin embargo saca **499,8**
puntos! Como vimos en el apartado 7, no hace falta imitar perfectamente: basta con que el peso de la inclinación sea lo bastante grande (en negativo)
para vencer a la gravedad (NB11: la ruedecilla tiene que pasar de 10) y que frene la velocidad. Diez pasos de entrenamiento, una fracción de segundo,
y el palo ya no se cae.
</details>

<details>
<summary>▶ Solución E6</summary>

Cambia la función:

```python
def maestro(inclinacion, velocidad):
    return -50 * inclinacion - 12 * velocidad
```

vuelve a ejecutar la celda que graba los ejemplos (y las que convierten a arrays), y entrena. El alumno debería encontrar **w1 ≈ −50 y w2 ≈ −12**: aprende al maestro
que tenga delante, sea cual sea. (Si con tasa 0,2 explota, prueba a bajarla: con un maestro distinto, los datos cambian, y la frontera de la tasa también.) Es la
idea central del aprendizaje supervisado: **el mismo método aprende cualquier cosa que le enseñes con ejemplos**.
</details>
"""),

md(r"""## 13 · 🛠 Práctica en MuJoCo: imitar a un maestro de verdad

Hoy la neurona ha imitado al maestro del palo de escoba **de juguete** (el de las fórmulas del NB11). Ahora, lo mismo con el palo de escoba **de MuJoCo**, con física de
verdad: un carro de 1 kg sobre un raíl, un palo de 0,5 kg y 1 m en una bisagra, y un motor que empuja el carro. Harás las tres cosas de la lección:

1. Poner a un **maestro** a equilibrar el palo y **grabar sus demostraciones** (situación → lo que decidió).
2. Entrenar a una **neurona alumna** con el descenso por gradiente y la regla de la cadena del apartado 6.
3. Darle el mando del palo al alumno.

Y te llevarás una sorpresa sobre **qué demostraciones** hay que grabar.
"""),

md(r"""### Paso 1 · El maestro

El palo de MuJoCo tiene **cuatro** números que mirar (no dos, como el de juguete), porque ahora el carro también cuenta: si se va muy lejos, choca con el final del
raíl. Una función los junta en un array, la **observación**:

- `qpos[1]`: la inclinación del palo (en radianes; positiva = inclinado hacia +x),
- `qvel[1]`: lo deprisa que se inclina,
- `qpos[0]`: dónde está el carro (en metros; 0 = el centro),
- `qvel[0]`: lo deprisa que va el carro.

El palo es el que conociste en la práctica del NB11. El maestro es una neurona con pesos elegidos a mano, como el del NB11, pero escrita directamente en las
unidades de MuJoCo (radianes, metros, y la orden del motor, que va de −1 a 1):

```
   orden = 3 × inclinación + 0,8 × velocidad del palo + 0,1 × posición del carro + 0,2 × velocidad del carro
```

Los signos son al revés que en el palo de juguete (en el NB11 dábamos la vuelta al ángulo para que encajara con él). Aquí "positivo" significa "hacia +x" en los dos sitios: si el palo se inclina hacia +x, el carro tiene que
correr hacia +x para meterse debajo (como cuando equilibras una escoba en la mano). El motor solo acepta órdenes entre −1 y 1, así que la recortamos con `np.clip` (NB15):
"""),

code(r"""import mujoco
import taller

modelo, datos = taller.cargar("palo_escoba")

def observar(datos):
    return np.array([datos.qpos[1], datos.qvel[1], datos.qpos[0], datos.qvel[0]])

def maestro_pd(obs):
    return 3 * obs[0] + 0.8 * obs[1] + 0.1 * obs[2] + 0.2 * obs[3]

def control_maestro(modelo, datos):
    datos.ctrl[0] = np.clip(maestro_pd(observar(datos)), -1, 1)

datos.qpos[1] = 0.2              # el palo empieza inclinado 0,2 rad (unos 11 grados)
taller.video(modelo, datos, segundos=4, control=control_maestro, nombre="nb18_maestro", distancia=3);"""),

md(r"""El carro da un tirón hacia el lado al que cae el palo, lo endereza y vuelve poco a poco al centro. Un maestro competente.
"""),

md(r"""### Paso 2 · Grabar las demostraciones

Como en el apartado 2: ponemos al maestro a jugar y apuntamos cada situación (la observación, 4 números) y lo que decidió (su **etiqueta**). Esta vez, **10
episodios de 3 segundos** (300 pasitos), y cada uno empieza en una situación distinta al azar: el palo inclinado entre −0,3 y 0,3 rad, y el carro en cualquier sitio
entre −1 y 1 m. (`np.random.default_rng(semilla)` es el generador de números al azar de NumPy que ya viste en el NB15, y `mj_resetData` deja todo a cero, NB11.)

La función tiene un parámetro raro, `temblor`, que de momento valdrá 0. Sirve para que el maestro **ejecute** su orden con el pulso tembloroso: se le suma un
número al azar entre −temblor y +temblor antes de mandarla al motor. Pero, ojo, lo que **apuntamos** como etiqueta es siempre la orden **limpia**, la que el maestro
**quería** dar. (Y apuntamos la orden antes de recortarla a ±1: lo que el maestro "piensa", como en el apartado 2.)
"""),

code(r"""def grabar_demostraciones(temblor, episodios=10, semilla=0):
    azar = np.random.default_rng(semilla)
    ejemplos = []
    etiquetas = []
    for episodio in range(episodios):
        mujoco.mj_resetData(modelo, datos)
        datos.qpos[1] = azar.uniform(-0.3, 0.3)       # palo inclinado al azar
        datos.qpos[0] = azar.uniform(-1, 1)           # carro en un sitio al azar
        for paso in range(300):
            obs = observar(datos)
            quiere = maestro_pd(obs)
            ejemplos.append(obs)                      # la situación...
            etiquetas.append(quiere)                  # ...y lo que el maestro QUERÍA hacer
            datos.ctrl[0] = np.clip(quiere + azar.uniform(-temblor, temblor), -1, 1)
            mujoco.mj_step(modelo, datos)
    return np.array(ejemplos), np.array(etiquetas)

ejemplos, etiquetas = grabar_demostraciones(temblor=0)
print("Forma de los ejemplos:", ejemplos.shape, "| forma de las etiquetas:", etiquetas.shape)
print("Primer ejemplo:", np.round(ejemplos[0], 3), "-> el maestro quería", round(etiquetas[0], 3))"""),

md(r"""**3.000 ejemplos.** `ejemplos` es una **matriz** (NB14) de 3.000 filas y 4 columnas: cada fila, una situación. Es exactamente lo que guarda un laboratorio de
robótica cuando graba demostraciones, solo que con más columnas.
"""),

md(r"""### Paso 3 · La neurona alumna

El alumno es una neurona con **4 pesos** (uno por número de la observación) y un sesgo. Su predicción para los 3.000 ejemplos a la vez es `ejemplos @ pesos + sesgo`:
la matriz por el vector (NB14-15), un producto escalar por fila.

Y el entrenamiento es el del apartado 6, con la fórmula de la regla de la cadena: la pendiente de cada peso es **2 × media(error × su entrada)**, y "su entrada"
es su **columna** de la matriz, `ejemplos[:, k]` (NB15). Un bucle recorre las 4 columnas:
"""),

code(r"""def entrenar_alumno(ejemplos, etiquetas, pasos=1000, tasa=0.5):
    pesos = np.zeros(4)
    sesgo = 0.0
    for paso in range(pasos):
        errores = ejemplos @ pesos + sesgo - etiquetas
        for k in range(4):
            pesos[k] = pesos[k] - tasa * 2 * np.mean(errores * ejemplos[:, k])
        sesgo = sesgo - tasa * 2 * np.mean(errores)
    return pesos, sesgo

def perdida_alumno(pesos, sesgo, ejemplos, etiquetas):
    return np.mean((ejemplos @ pesos + sesgo - etiquetas) ** 2)"""),

md(r"""Y una prueba de fuego: darle el mando al alumno durante **10 segundos**, empezando con el palo inclinado 0,2, y contar cuánto aguanta antes de que el palo pase de
0,5 rad (caído):
"""),

code(r"""def segundos_de_pie(pesos, sesgo, inclinacion=0.2):
    mujoco.mj_resetData(modelo, datos)
    datos.qpos[1] = inclinacion
    for paso in range(1000):
        datos.ctrl[0] = np.clip(observar(datos) @ pesos + sesgo, -1, 1)
        mujoco.mj_step(modelo, datos)
        if abs(datos.qpos[1]) > 0.5:
            break
    return round(datos.time, 2)

print("El maestro aguanta:", segundos_de_pie(np.array([3, 0.8, 0.1, 0.2]), 0), "s")"""),

md(r"""El maestro (sus pesos metidos en la misma función) aguanta los 10 segundos enteros, claro.
"""),

md(r"""### Paso 4 · Primer intento: demostraciones limpias

Entrenamos al alumno con las demostraciones del Paso 2 (temblor 0): 1.000 pasos, tasa 0,5. Tarda un par de segundos.
"""),

code(r"""pesos, sesgo = entrenar_alumno(ejemplos, etiquetas)
print("Pesos aprendidos:", np.round(pesos, 3), "| sesgo:", round(sesgo, 4))
print("Pérdida:", round(perdida_alumno(pesos, sesgo, ejemplos, etiquetas), 5), "(la de un alumno que no sabe nada:", round(np.mean(etiquetas ** 2), 5), ")")
print("Aguanta:", segundos_de_pie(pesos, sesgo), "s")"""),

md(r"""¡Sorpresa! La pérdida ha bajado mucho (de 0,0215 a 0,0016: una catorceava parte), pero los pesos, **(1,51; −0,24; −0,02; −0,07)**, no se parecen a los del maestro
(3; 0,8; 0,1; 0,2), y el palo **se cae en 0,81 segundos**. ¿Qué ha pasado, si el alumno imita bien los ejemplos?

El problema está en los **datos**. El maestro es tan bueno que siempre hace lo mismo: endereza el palo de la misma manera, y en sus demostraciones los cuatro números
se mueven **siempre en equipo** (cuando el palo cae hacia un lado, la velocidad, el carro... cambian todos a la vez, en las mismas proporciones). Con datos así, hay
**muchísimas** combinaciones de pesos que dan casi la misma predicción en esos ejemplos: el valle de la pérdida (apartado 4) tiene un fondo **alargado y casi plano**,
y el descenso por gradiente avanza por él muy despacio. El alumno se queda en una combinación que imita bien **por donde pasó el maestro**... y en cuanto él mismo
se desvía un poco de ese camino, está en una situación que nunca vio, y hace disparates. Es el **desplazamiento de distribución** del apartado 9, en directo.
"""),

md(r"""### Paso 5 · Segundo intento: un maestro con el pulso tembloroso

La solución es contraintuitiva: que el maestro conduzca **un poco mal**. Con `temblor=1`, a cada orden se le suma un empujón al azar de hasta ±1, así que el palo se
tuerce de muchas formas distintas... y el maestro tiene que **corregir** desde situaciones variadas. Como apuntamos lo que **quería** hacer (no el empujón tembloroso),
las etiquetas siguen siendo las del maestro perfecto, pero ahora cubren **muchas más situaciones**, incluidas las de "me he desviado, ¿cómo vuelvo?".
"""),

code(r"""ejemplos, etiquetas = grabar_demostraciones(temblor=1)
pesos, sesgo = entrenar_alumno(ejemplos, etiquetas)
print("Pesos aprendidos:", np.round(pesos, 3), "| sesgo:", round(sesgo, 4))
print("Pérdida:", perdida_alumno(pesos, sesgo, ejemplos, etiquetas))
print("Aguanta:", segundos_de_pie(pesos, sesgo), "s")"""),

md(r"""**(2,994; 0,799; 0,099; 0,2)**: el alumno ha **redescubierto** los pesos del maestro, con el mismo entrenamiento (1.000 pasos, tasa 0,5) y el mismo número de
ejemplos. Solo han cambiado las demostraciones. La pérdida es diminuta (0,0000002) y el palo aguanta los **10 segundos**.

Este truco existe de verdad: en los laboratorios se **añade ruido a propósito** mientras un experto hace las demostraciones, para que el robot aprenda también a
recuperarse (uno de los métodos se llama DART). La lección para la vida: **los datos importan tanto como el algoritmo**.

El alumno, al volante:
"""),

code(r"""def control_alumno(modelo, datos):
    datos.ctrl[0] = np.clip(observar(datos) @ pesos + sesgo, -1, 1)

mujoco.mj_resetData(modelo, datos)
datos.qpos[1] = 0.2
taller.video(modelo, datos, segundos=4, control=control_alumno, nombre="nb18_alumno", distancia=3);"""),

md(r"""Igual que el maestro. **Ha aprendido a equilibrar un palo con física de verdad sin jugar ni un solo episodio por su cuenta**: solo mirando 3.000 decisiones de otro.
"""),

md(r"""### Tus retos

**Reto 1 · Paciencia.** Con las demostraciones **limpias** (`temblor=0`), entrena 3.000 pasos en vez de 1.000 (`entrenar_alumno(ejemplos, etiquetas, pasos=3000)`). ¿Qué
pesos aprende? ¿Aguanta el palo?

**Reto 2 · Poco temblor.** Graba con `temblor=0.3` y entrena 1.000 pasos. ¿Basta un temblor pequeño para que aguante?

**Reto 3 · Pocos ejemplos.** Graba con `temblor=1` pero solo **2 episodios** (`grabar_demostraciones(temblor=1, episodios=2)`): 600 ejemplos. ¿Qué pasa?

<details>
<summary>▶ Solución Reto 1</summary>

```python
ejemplos, etiquetas = grabar_demostraciones(temblor=0)
pesos, sesgo = entrenar_alumno(ejemplos, etiquetas, pasos=3000)
print(np.round(pesos, 3), segundos_de_pie(pesos, sesgo))
```

Aprende **(2,40; 0,38; 0,05; 0,09)** y ahora **sí** aguanta los 10 s. El valle alargado no era imposible, solo **lentísimo**: con el triple de pasos, el alumno avanza
lo suficiente por su fondo casi plano. Pero aún está lejos del maestro (0,38 en vez de 0,8 de velocidad). Con datos variados (Paso 5) llegaba exacto en 1.000 pasos:
mejores datos ahorran entrenamiento.
</details>

<details>
<summary>▶ Solución Reto 2</summary>

```python
ejemplos, etiquetas = grabar_demostraciones(temblor=0.3)
pesos, sesgo = entrenar_alumno(ejemplos, etiquetas)
print(np.round(pesos, 3), segundos_de_pie(pesos, sesgo))
```

Aprende **(2,29; 0,39; 0,04; 0,09)** y aguanta los **10 s**. Con un poco de temblor ya basta para que el alumno sepa recuperarse, aunque no llega a los pesos exactos
del maestro en 1.000 pasos: cuanto más variadas las demostraciones, más rápido y más exacto aprende.
</details>

<details>
<summary>▶ Solución Reto 3</summary>

```python
ejemplos, etiquetas = grabar_demostraciones(temblor=1, episodios=2)
pesos, sesgo = entrenar_alumno(ejemplos, etiquetas)
print(np.round(pesos, 3), round(sesgo, 3), segundos_de_pie(pesos, sesgo))
```

Aprende (2,47; 0,77; −0,01; 0,18) con un sesgo de −0,054, y el palo **se cae a los 3,48 s**. Con solo dos episodios no hay ejemplos suficientes para separar bien el
efecto de la **posición del carro** (su peso sale incluso con el signo cambiado) ni para saber que el sesgo debe ser 0: el carro se va desplazando hasta que todo se
estropea. **Más datos, mejor alumno** (apartado 8).
</details>

### Qué has aprendido de MuJoCo hoy

- Una **observación** del palo de MuJoCo son 4 números (`qpos` y `qvel` del palo y del carro), juntados en un array con una función `observar`.
- **Grabar demostraciones** en MuJoCo: un bucle de episodios con `mj_resetData` y situación inicial al azar; en cada paso se apunta la observación y la orden del maestro.
  Se guardan como una matriz de ejemplos y un vector de etiquetas.
- Un alumno entrenado con la regla de la cadena puede **controlar el simulador**: la política es `observar(datos) @ pesos + sesgo`.
- Las demostraciones **perfectas y monótonas** enseñan mal (el alumno se cae en 0,81 s); con **ruido al ejecutar** (apuntando lo que el maestro quería) el alumno
  redescubre los pesos exactos.

En la práctica del NB19 le pondrás al maestro el **límite** real de su motor (±1), lo construirás con dos codos como una **red neuronal a mano**, y entrenarás una
red de verdad que equilibre el palo de MuJoCo.
"""),

md(r"""## 14 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has entrenado tu primera neurona con **datos**, has descubierto la **regla de la cadena** (el secreto de la retropropagación), y has visto a una neurona
redescubrir sola los números de su maestro. Es, a pequeña escala, exactamente lo que hacen las redes neuronales gigantes.

Pero nuestro alumno tiene un límite: es **una** neurona **lineal**. Solo sabe aprender reglas del tipo "empuja tanto por cada grado". ¿Y si el maestro hiciera
algo más complicado, que no se puede escribir como una suma con pesos? En el **NB19** descubriremos el ingrediente que le falta: la **función de activación**, el
pequeño "codo" que, puesto entre capa y capa, convierte un montón de neuronas lineales en una **red neuronal** capaz de aprender casi cualquier cosa.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB18_aprender_imitando.ipynb")
    build(out, cells, title="NB18 · Aprender imitando: el aprendizaje supervisado")
