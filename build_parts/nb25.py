"""Construye NB25 · Python de verdad (6): herencia y tu propio entorno de Gymnasium.

Herencia (class Hija(Madre)): hereda todo, añade y sobrescribe; super();
"es un" (isinstance con la madre); polimorfismo (mismo método, distinto
comportamiento); clases abstractas (abc.ABC, @abstractmethod; TypeError real al
instanciar); métodos especiales para operadores: Vector con __add__, __sub__,
__mul__, __rmul__, __eq__, __len__, __getitem__, __iter__ (así funciona NumPy);
composición ("tiene un") vs herencia ("es un"). Gran final: PaloDeEscobaEnv
hereda de gymnasium.Env, con observation_space/action_space (spaces.Box),
acción normalizada [-1, 1] (×40), reset con super().reset(seed) y
self.np_random, check_env (y sus avisos explicados), gym.register con
max_episode_steps → gym.make lo envuelve (TimeLimit...). Evaluación: nada ~44,6,
solo inclinación ~353,4, a mano ~499,9. Cómo es una red de PyTorch (nn.Module).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB25 · Python de verdad (6): herencia y tu propio entorno de Gymnasium

**Parte 3 · Python de verdad — Lección 6**

> En el **NB24** construiste tus primeras clases y convertiste el palo de escoba en un objeto con `reset` y `step`. Hoy veremos la otra
> mitad de las clases, la que hace que el código profesional sea como es: la **herencia**.

La herencia permite crear una clase **a partir de otra**, aprovechando todo lo que ya hace y cambiando solo lo necesario. Es la forma en
la que están construidos **todos** los entornos de Gymnasium (todos "heredan" de una clase madre llamada `gymnasium.Env`) y **todas** las
redes neuronales de PyTorch (todas heredan de `torch.nn.Module`).

Al final de hoy, el palo de escoba será un **entorno oficial de Gymnasium**: pasará el verificador oficial, se registrará con un nombre, y se
creará con `gym.make("PaloDeEscoba-v0")`, **exactamente igual** que el humanoide. A partir de ahí, cualquier herramienta profesional que sepa
entrenar entornos de Gymnasium sabrá entrenar **el tuyo**.
"""),

md(r"""## 1 · Herencia: una clase hecha a partir de otra

Imagina que tienes una clase `Robot` (NB24) y ahora quieres una clase para **humanoides**. Un humanoide **es un** robot: tiene nombre y motores, y
sabe describirse. Pero además tiene cosas propias (por ejemplo, una altura de torso). No tiene sentido reescribir todo lo del robot: lo
**heredamos**.

Se escribe poniendo la clase **madre** entre paréntesis después del nombre de la clase **hija**:
"""),

code(r"""class Robot:
    def __init__(self, nombre, motores):
        self.nombre = nombre
        self.motores = motores

    def describir(self):
        return f"{self.nombre}, con {self.motores} motores"

    def ruedecillas_politica_lineal(self, observaciones):
        return self.motores * observaciones + self.motores


class Humanoide(Robot):          # Humanoide HEREDA de Robot
    pass

h = Humanoide("Humanoid-v5", 17)
print(h.describir())
print(h.ruedecillas_politica_lineal(348))"""),

md(r"""¡La clase `Humanoide` está **vacía** (solo `pass`), y sin embargo sus objetos tienen `nombre`, `motores`, `describir` y `ruedecillas_politica_lineal`!
Lo han **heredado** todo de `Robot`. A la clase de la que se hereda se le llama **madre** (o *base*, o *superclase*), y a la que hereda, **hija** (o
*subclase*).
"""),

md(r"""## 2 · Añadir y cambiar: `super()`

Una clase hija puede **añadir** cosas nuevas y **cambiar** (se dice **sobrescribir**) las que hereda. Para que el humanoide tenga además su altura, hay
que escribir su propio `__init__`. Pero no queremos repetir lo que ya hace el de `Robot` (guardar nombre y motores). Para **llamar al método de la
madre** desde la hija se usa **`super()`**:
"""),

code(r"""class Humanoide(Robot):
    def __init__(self, nombre, motores, altura_torso):
        super().__init__(nombre, motores)       # que la madre haga su parte...
        self.altura_torso = altura_torso        # ...y yo añado lo mío

    def describir(self):                        # SOBRESCRIBO el de la madre
        base = super().describir()              # ...aprovechando lo que ya hacía
        return f"{base} y el torso a {self.altura_torso} m"

    def esta_caido(self):                       # un método NUEVO, solo de los humanoides
        return self.altura_torso < 1.0

h = Humanoide("Humanoid-v5", 17, 1.4)
print(h.describir())
print(h.esta_caido())"""),

md(r"""- `super().__init__(nombre, motores)` ejecuta el `__init__` de `Robot`, que guarda el nombre y los motores. Luego la hija añade su altura.
- `describir` está **sobrescrito**: los humanoides se describen a su manera, pero reutilizando la descripción de la madre con `super().describir()`.
- `esta_caido` es nuevo: solo lo tienen los humanoides.

**`super()` es importantísimo**: cuando escribas tu propio entorno de Gymnasium o tu propia red de PyTorch, **lo primero** que harás en su `__init__` será
llamar a `super().__init__()`, para que la clase madre prepare todo lo suyo. Si se te olvida, fallarán cosas de formas misteriosas.
"""),

md(r"""## 3 · "Es un": `isinstance` y la familia

Un objeto de una clase hija **es también** de la clase madre. Un humanoide **es un** robot:"""),

code(r"""print(isinstance(h, Humanoide))
print(isinstance(h, Robot))
print(isinstance(Robot("Hopper-v5", 3), Humanoide))"""),

md(r"""`True`, `True` y `False`: un humanoide es un robot, pero no todo robot es un humanoide. Por eso, todo lo que funciona con un `Robot` funciona con un `Humanoide`.
Esta idea, "**es un**", es la pista para saber cuándo usar herencia: si puedes decir "un X **es un** Y", X puede heredar de Y. (Un entorno del palo de escoba **es un**
entorno de Gymnasium; una red para el humanoide **es un** módulo de PyTorch.)
"""),

md(r"""## 4 · Polimorfismo: misma orden, distinta respuesta

Cuando varias clases de la misma familia tienen un método con el **mismo nombre**, puedes tratarlas a todas **por igual** y cada una responderá **a su manera**. Se
llama **polimorfismo** ("muchas formas"):
"""),

code(r"""class Hopper(Robot):
    def describir(self):
        return f"{self.nombre}: una pierna que salta, con {self.motores} motores"

flota = [Robot("Ant-v5", 8), Humanoide("Humanoid-v5", 17, 1.4), Hopper("Hopper-v5", 3)]
for robot in flota:
    print(robot.describir())"""),

md(r"""El bucle **no sabe ni le importa** de qué clase es cada robot: solo llama a `describir()`, y cada uno contesta con **su** versión. Esto es justo lo que permitía el
bucle de episodio del NB24: sirve para **cualquier** entorno que tenga `reset` y `step`, y para **cualquier** política que se pueda llamar. Es el polimorfismo lo que
permite que una sola biblioteca de entrenamiento funcione con miles de entornos distintos.
"""),

md(r"""## 5 · Clases abstractas: un contrato

A veces una clase madre existe solo para **definir qué métodos tienen que tener sus hijas**, sin hacer ella el trabajo. Por ejemplo: "toda política **tiene que**
saber decidir una acción a partir de una observación; cómo lo haga, depende de cada una". Es como un **contrato**: "si quieres ser una política, tienes que tener un
método `decidir`".

Python lo permite con el módulo **`abc`** (de *abstract base classes*, "clases base abstractas"). La madre hereda de `ABC`, y los métodos obligatorios llevan el decorador
`@abstractmethod`:
"""),

code(r"""from abc import ABC, abstractmethod

class Politica(ABC):
    @abstractmethod
    def decidir(self, observacion):
        ...                              # (los tres puntos significan "aquí no hay nada": lo pondrá cada hija)

    def __call__(self, observacion):     # este SÍ lo hereda todo el mundo
        return self.decidir(observacion)


class PoliticaLineal(Politica):
    def __init__(self, k, d):
        self.k, self.d = k, d

    def decidir(self, observacion):
        inclinacion, velocidad = observacion
        return -self.k * inclinacion - self.d * velocidad

p = PoliticaLineal(30, 8)
print(p((2.0, 0.0)))"""),

md(r"""`PoliticaLineal` cumple el contrato (tiene `decidir`) y hereda el `__call__` de la madre, que llama a su `decidir`. ¿Y si intentas fabricar una `Politica` a secas, sin
`decidir`?
"""),

code_err(r"""Politica()"""),

md(r"""`TypeError: Can't instantiate abstract class Politica without an implementation for abstract method 'decidir'`: "no se puede fabricar la clase abstracta `Politica`
sin una implementación del método abstracto `decidir`". Python **obliga** a cumplir el contrato. Si escribes una política hija y olvidas `decidir`, el error salta **al
crearla** (¡fallar pronto, NB22!), no a mitad de un entrenamiento.

`gymnasium.Env` funciona de una forma parecida: es la clase madre que define el "contrato" de todo entorno (`reset`, `step`, los espacios de observación y acción...).
"""),

md(r"""## 6 · Métodos especiales para operadores: tu propio vector

En el NB24 viste `__init__`, `__repr__` y `__call__`. Hay **muchos** más métodos especiales, y con ellos tus objetos pueden comportarse como los de Python: sumarse con
`+`, medirse con `len`, recorrerse con `for`, compararse con `==`... Vamos a construir una pequeña clase **`Vector`** (las flechas del NB12) que se pueda **sumar**, **restar**
y **multiplicar por un número** con los símbolos normales:
"""),

code(r"""class Vector:
    def __init__(self, *componentes):            # *args, NB23: acepta cuantas componentes le den
        self.componentes = list(componentes)

    def __repr__(self):
        return f"Vector{tuple(self.componentes)}"

    def __add__(self, otro):                     # se llama al escribir  a + b
        return Vector(*[x + y for x, y in zip(self.componentes, otro.componentes)])

    def __sub__(self, otro):                     # a - b
        return Vector(*[x - y for x, y in zip(self.componentes, otro.componentes)])

    def __mul__(self, numero):                   # a * 3
        return Vector(*[x * numero for x in self.componentes])

    def __rmul__(self, numero):                  # 3 * a  (el número a la IZQUIERDA)
        return self * numero

    def __eq__(self, otro):                      # a == b
        return self.componentes == otro.componentes

    def __len__(self):                           # len(a)
        return len(self.componentes)

    def __getitem__(self, i):                    # a[i]
        return self.componentes[i]

    def __iter__(self):                          # for x in a
        return iter(self.componentes)

    def longitud(self):                          # Pitágoras, NB12
        return sum(x ** 2 for x in self) ** 0.5"""),

md(r"""Cada símbolo de Python tiene su método especial: cuando escribes `a + b`, Python llama a `a.__add__(b)`; `len(a)` llama a `a.__len__()`; `a[0]`, a `a.__getitem__(0)`; y
así con todos. Mira cómo se usa nuestro vector, como si fuera parte del lenguaje:
"""),

code(r"""robot = Vector(2, 1)
meta = Vector(6, 4)
hacia_la_meta = meta - robot                     # __sub__

print(hacia_la_meta)
print("Distancia:", hacia_la_meta.longitud())
print("El doble:", 2 * hacia_la_meta)            # __rmul__
print("Componente x:", hacia_la_meta[0], "| dimensiones:", len(hacia_la_meta))
print("¿Igual a (4, 3)?", hacia_la_meta == Vector(4, 3))
for componente in hacia_la_meta:                 # __iter__
    print("  ", componente)"""),

md(r"""Es la resta de flechas del NB12 (de (2, 1) a (6, 4): la flecha (4, 3), de longitud 5), pero ahora con los **símbolos de verdad**.

**¡Así es exactamente cómo funciona NumPy!** Un array de NumPy es un objeto de la clase `ndarray`, cuyo `__add__` suma elemento a elemento (NB15), cuyo `__matmul__` (el método de
`@`) hace el producto escalar o de matrices, cuyo `__getitem__` permite `x[1, 2]`... Los "superpoderes" de los arrays son métodos especiales. Ya no hay magia.

(Fíjate en `__rmul__`: hace falta porque en `2 * hacia_la_meta` el número va a la **izquierda**, así que Python primero intenta `(2).__mul__(vector)`; los enteros no saben
multiplicarse por un `Vector`, así que Python prueba después con el método "por la derecha" del vector, `__rmul__`.)
"""),

md(r"""## 7 · ¿Heredar o "tener"? Composición

La herencia no es la única forma de construir clases a partir de otras. A menudo es mejor que una clase **tenga** objetos de otras clases dentro, como atributos. Se llama
**composición**. La pregunta que lo decide:

- "Un humanoide **es un** robot" → **herencia** (`class Humanoide(Robot)`).
- "Un robot **tiene** motores" → **composición** (el robot guarda una lista de objetos `Motor`).
"""),

code(r"""class Motor:
    def __init__(self, nombre, fuerza_maxima):
        self.nombre = nombre
        self.fuerza_maxima = fuerza_maxima

    def recortar(self, par):
        return max(-self.fuerza_maxima, min(self.fuerza_maxima, par))


class Pierna:
    def __init__(self):
        self.motores = [Motor("cadera", 300), Motor("rodilla", 200)]    # la pierna TIENE motores

    def aplicar(self, pares):
        return [motor.recortar(par) for motor, par in zip(self.motores, pares)]

pierna = Pierna()
print(pierna.aplicar([250, 250]))"""),

md(r"""La pierna **tiene** dos motores, y les **delega** el trabajo de recortar: la cadera deja pasar 250 (su máximo es 300); la rodilla lo recorta a 200. Cada objeto sabe hacer **su**
parte.

Una regla práctica muy extendida entre programadores: **prefiere la composición; usa la herencia solo cuando "es un" sea claramente cierto**. Las jerarquías de herencia muy
profundas (una clase que hereda de otra que hereda de otra...) se vuelven difíciles de seguir.
"""),

md(r"""## 8 · El gran final: tu propio entorno de Gymnasium

Ahora sí. Vamos a convertir el palo de escoba en un entorno **oficial** de Gymnasium. El contrato de `gymnasium.Env` pide estas cosas:

1. **Heredar** de `gym.Env`.
2. Definir **`observation_space`** y **`action_space`**: la descripción de **cómo son** las observaciones y las acciones (cuántos números, entre qué valores, de qué tipo). Se
   construyen con las clases de `gymnasium.spaces`; la más usada, **`Box`** ("caja"), describe "un array de tal forma, con cada número entre tal y tal valor".
3. Un método **`reset(self, seed=None, options=None)`** que llame a **`super().reset(seed=seed)`** (así Gymnasium prepara un generador de azar con esa semilla, llamado
   **`self.np_random`**) y devuelva `(observación, info)`.
4. Un método **`step(self, action)`** que devuelva `(observación, recompensa, terminado, truncado, info)`.
5. Las observaciones, como **arrays de NumPy** del tipo que diga el espacio.

Un detalle profesional: el verificador de Gymnasium **recomienda** que las acciones vayan **normalizadas** entre −1 y 1, porque los algoritmos de entrenamiento funcionan mejor así.
Así que nuestro entorno recibirá una acción entre −1 y 1, y **por dentro** la multiplicará por 40 para obtener el empuje. (¡Es lo mismo que hace el humanoide!: sus acciones van
entre −0,4 y 0,4, y cada motor las multiplica por su propia fuerza, NB03.)
"""),

code(r"""import gymnasium as gym
from gymnasium import spaces
import numpy as np


class PaloDeEscobaEnv(gym.Env):
    '''El palo de escoba del NB11, como entorno oficial de Gymnasium.

    Observación: [inclinación (grados), velocidad de giro (grados/s)].
    Acción: [empuje normalizado entre -1 y 1] (se multiplica por 40).
    '''

    def __init__(self, viento_maximo=30.0):
        super().__init__()
        self.viento_maximo = viento_maximo
        self.empuje_maximo = 40.0
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)
        self.inclinacion = 0.0
        self.velocidad = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)               # prepara self.np_random con la semilla
        self.inclinacion = 2.0
        self.velocidad = 0.0
        return self._observacion(), {}

    def step(self, action):
        empuje = float(np.clip(action[0], -1.0, 1.0)) * self.empuje_maximo
        viento = self.np_random.uniform(-self.viento_maximo, self.viento_maximo)
        aceleracion = 10 * self.inclinacion + empuje + viento
        self.velocidad = self.velocidad + aceleracion * 0.02
        self.inclinacion = self.inclinacion + self.velocidad * 0.02

        terminado = bool(abs(self.inclinacion) > 30)
        recompensa = 0.0 if terminado else float(1 - (self.inclinacion / 30) ** 2)
        return self._observacion(), recompensa, terminado, False, {"viento": viento}

    def _observacion(self):
        return np.array([self.inclinacion, self.velocidad], dtype=np.float32)"""),

md(r"""(El docstring va con comillas simples triples, `'''`, por cómo están construidos estos cuadernos; en tus programas puedes usar cualquiera de las dos.)

(Y el `dtype=np.float32` que aparece tres veces: le dice a NumPy en qué **formato** guardar los decimales. `float32` usa la mitad de memoria que el normal (`float64`) a cambio de menos cifras exactas (unas 7 en vez de 16), y es el que usan las redes neuronales y, por costumbre, Gymnasium. Lo verás a fondo en el NB27; por ahora, basta saber que los espacios y las observaciones tienen que usar el **mismo** formato, o el verificador de abajo se queja.)

Fíjate en lo que **no** hace: no cuenta los pasos ni trunca a los 500. Eso se lo dejaremos a Gymnasium, que tiene una herramienta para ello (lo verás en un momento).

Gymnasium trae un **verificador** oficial, `check_env`, que comprueba que el entorno cumple el contrato: que `reset` y `step` devuelven lo que deben, que las observaciones encajan
con su espacio, que la semilla funciona... Pasémoselo:
"""),

code(r"""from gymnasium.utils.env_checker import check_env

check_env(PaloDeEscobaEnv())
print("El entorno ha pasado el verificador de Gymnasium")"""),

md(r"""¡Lo ha pasado! (Si hubiera algo mal, saltaría un error.) Verás que, además, muestra algunos **avisos** (*warnings*, con fondo de color). No son errores: son **consejos**.
Vamos a leerlos como profesionales:

- *"A Box observation space minimum value is -infinity. This is probably too low"*: hemos dicho que la observación puede valer desde −infinito hasta +infinito. Es verdad que
  nuestra velocidad no tiene un límite claro, así que es razonable; el aviso solo nos recuerda que, si se conocen límites reales, es mejor ponerlos.
- *"Not able to test alternative render modes..."*: nuestro entorno no sabe **dibujarse** (no tiene modo de "render"), así que el verificador no puede probarlo. Es correcto: no lo
  hemos programado.

Y fíjate en uno que **no** sale: el que recomendaba acciones normalizadas en [−1, 1]. Lo hemos evitado a propósito. **Leer los avisos y decidir si importan** es parte del oficio.
"""),

md(r"""### Registrar el entorno y crearlo con `gym.make`

Para que se pueda crear por su nombre, como el humanoide, se **registra** con un identificador. Por convención, el nombre termina en `-v0` (versión 0). Le decimos también
`max_episode_steps=500`: así Gymnasium se encarga de **truncar** los episodios a los 500 pasos.
"""),

code(r"""gym.register(id="PaloDeEscoba-v0", entry_point=PaloDeEscobaEnv, max_episode_steps=500)

entorno = gym.make("PaloDeEscoba-v0")
print(entorno)
print("Observaciones:", entorno.observation_space)
print("Acciones:     ", entorno.action_space)
print("Una acción al azar:", entorno.action_space.sample())"""),

md(r"""¡`gym.make("PaloDeEscoba-v0")` funciona, igual que `gym.make("Humanoid-v5")`!

Mira cómo se muestra: `TimeLimit<OrderEnforcing<PassiveEnvChecker<PaloDeEscobaEnv<...>>>>`. Nuestro entorno está **envuelto** en otros tres objetos, como una muñeca rusa. Se llaman
**envoltorios** (*wrappers*), y son... **composición** (apartado 7)! Cada uno **tiene** dentro al anterior y le añade algo:

- **`TimeLimit`**: cuenta los pasos y pone `truncado = True` al llegar a 500. Por eso no lo programamos.
- **`OrderEnforcing`**: comprueba que no se llame a `step` antes de `reset`.
- **`PassiveEnvChecker`**: vigila, sin molestar, que el entorno se comporte bien.

Los envoltorios son muy usados en la práctica: hay envoltorios para grabar vídeos, para normalizar las observaciones, para apilar varias observaciones seguidas... Todos funcionan
igual: envuelven un entorno y cambian o añaden algo, sin tocar su código. (Es la misma idea que los **decoradores** del NB23, pero con objetos.)

Y `action_space.sample()` da una acción **al azar** válida: muy útil para probar un entorno o hacer una política al azar.
"""),

md(r"""### Probarlo con nuestras políticas

Las políticas tienen que dar ahora la acción **normalizada**: el empuje dividido entre 40, recortado a [−1, 1], dentro de un array. Y el bucle de episodio es **el de siempre**:"""),

code(r"""def politica_lineal(k, d):
    def politica(observacion):
        inclinacion, velocidad = observacion
        empuje = -k * inclinacion - d * velocidad
        return np.array([np.clip(empuje / 40.0, -1.0, 1.0)], dtype=np.float32)
    return politica

def evaluar(entorno, politica, semillas=range(5)):
    retornos = []
    for semilla in semillas:
        observacion, info = entorno.reset(seed=semilla)
        retorno = 0.0
        while True:
            observacion, recompensa, terminado, truncado, info = entorno.step(politica(observacion))
            retorno = retorno + recompensa
            if terminado or truncado:
                break
        retornos.append(retorno)
    return np.mean(retornos)

for nombre, k, d in [("nada", 0, 0), ("solo inclinación", 30, 0), ("a mano", 30, 8)]:
    print(f"{nombre:>17}: {evaluar(entorno, politica_lineal(k, d)):.1f}")"""),

md(r"""**Nada ≈ 44,6; solo inclinación ≈ 353,4; a mano ≈ 499,9.** El mismo comportamiento que en el NB11: no hacer nada fracasa, solo mirar la inclinación es irregular, y mirar
también la velocidad lo aguanta todo. (Los números no son **idénticos** a los del NB11 porque ahora el viento sale del generador de azar de Gymnasium, `self.np_random`, que es
distinto del de `random`. Con otros vientos, la política "solo inclinación" ha tenido algo más de suerte esta vez: es lo **irregular** que es.)

**Tu entorno ya es intercambiable con cualquier entorno de Gymnasium.** Cualquier herramienta profesional que sepa entrenar "un entorno de Gymnasium" sabe entrenar el tuyo. Lo
comprobaremos en la parte de aprendizaje por refuerzo, cuando entrenemos este mismo palo de escoba con algoritmos de verdad.

Y como todo entorno registrado, se le pueden pasar opciones al crearlo (llegan a su `__init__`, gracias a los `**kwargs`, NB23):
"""),

code(r"""entorno_ventoso = gym.make("PaloDeEscoba-v0", viento_maximo=60.0)
print(f"Con el doble de viento, a mano: {evaluar(entorno_ventoso, politica_lineal(30, 8)):.1f}")
entorno.close()
entorno_ventoso.close()"""),

md(r"""## 9 · Y así es una red de PyTorch

Para terminar, un adelanto que ya puedes **leer** entero, aunque no lo ejecutemos (PyTorch aún no está instalado; llegará en la parte de aprendizaje por refuerzo). Así se escribe una
red neuronal como la del NB19 en PyTorch:

```python
import torch
from torch import nn

class RedPolitica(nn.Module):                 # HEREDA de nn.Module (apartados 1-2)
    def __init__(self, entradas, ocultas, salidas):
        super().__init__()                    # ¡lo primero, siempre! (apartado 2)
        self.capa1 = nn.Linear(entradas, ocultas)    # COMPOSICIÓN: la red TIENE capas (apartado 7)
        self.capa2 = nn.Linear(ocultas, salidas)

    def forward(self, x):                     # el "contrato" de nn.Module: hay que escribir forward (apartado 5)
        x = torch.relu(self.capa1(x))         # capa lineal + ReLU (NB14, NB19)
        return self.capa2(x)

red = RedPolitica(348, 256, 17)
accion = red(observacion)                     # se LLAMA como una función: __call__ (NB24), que llama a forward
```

Léelo despacio: **no hay nada que no sepas ya**. Herencia de una clase madre, `super().__init__()`, atributos que son objetos (las capas), un método obligatorio (`forward`), y un objeto
que se llama como una función. Hace unas lecciones, este código habría sido magia. Ahora es una clase normal.
"""),

md(r"""## 10 · Resumen de la lección

1. **Herencia**: `class Hija(Madre):` hereda todo de la madre; la hija puede **añadir** y **sobrescribir** métodos. **`super()`** llama a los métodos de la madre (sobre todo
   `super().__init__(...)`, lo primero en el `__init__` de la hija). Un objeto hijo **es un** objeto de la madre (`isinstance`).
2. **Polimorfismo**: clases distintas con métodos del mismo nombre se usan por igual, y cada una responde a su manera (el bucle de episodio sirve para cualquier entorno).
3. **Clases abstractas** (`ABC`, `@abstractmethod`): un **contrato** de métodos obligatorios; no se pueden fabricar sin cumplirlo (`TypeError`).
4. **Métodos especiales** para operadores (`__add__`, `__sub__`, `__mul__`, `__rmul__`, `__eq__`, `__len__`, `__getitem__`, `__iter__`...): así funcionan los arrays de NumPy.
   **Composición** ("tiene un") frente a herencia ("es un"); prefiere la composición.
5. Tu **entorno de Gymnasium**: hereda de `gym.Env`, define `observation_space` y `action_space` (`spaces.Box`), `reset` con `super().reset(seed=seed)` y `self.np_random`, y `step`
   con 5 valores. Pasa **`check_env`**, se **registra** con `gym.register` y se crea con **`gym.make`**, que lo envuelve en **envoltorios** (`TimeLimit`...). Una red de PyTorch es una
   clase hija de `nn.Module`.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Herencia** | Crear una clase a partir de otra, heredando todo lo suyo. |
| **Clase madre / hija** | La clase de la que se hereda / la que hereda (base / subclase). |
| **Sobrescribir** | Que la hija tenga su propia versión de un método de la madre. |
| **`super()`** | Acceso a los métodos de la clase madre. |
| **Polimorfismo** | Usar objetos de clases distintas por igual; cada uno responde a su manera. |
| **Clase abstracta / `@abstractmethod`** | Clase madre que obliga a sus hijas a tener ciertos métodos. |
| **Composición** | Una clase que tiene objetos de otras como atributos ("tiene un"). |
| **Espacio (`spaces.Box`)** | La descripción de cómo son las observaciones o acciones de un entorno. |
| **Acción normalizada** | Acción entre −1 y 1, que el entorno escala por dentro. |
| **`check_env`** | El verificador oficial de entornos de Gymnasium. |
| **Registrar / `gym.make`** | Dar un nombre a un entorno / crearlo por su nombre. |
| **Envoltorio (*wrapper*)** | Objeto que envuelve un entorno y le añade algo (`TimeLimit`...). |
| **Aviso (*warning*)** | Un consejo del programa, que no detiene la ejecución. |
"""),

md(r"""## 11 · Ejercicios

**E1.** Crea una clase `Cuadrupedo` que herede de `Robot`, con un atributo nuevo `patas` (que valga 4) y un `describir` sobrescrito que lo mencione. Usa `super()` en los dos.

**E2.** ¿Qué pasaría si en el `__init__` de `Humanoide` olvidaras la línea `super().__init__(nombre, motores)`? ¿Qué error saltaría al llamar a `h.describir()`?

**E3.** Escribe una `PoliticaAzar(Politica)` (de la clase abstracta del apartado 5) cuyo `decidir` devuelva un número al azar entre −40 y 40. ¿Qué pasa si te equivocas y llamas
al método `decide` en vez de `decidir`?

**E4.** Añade a la clase `Vector` un método especial `__neg__` para que `-v` dé el vector al revés (NB12: multiplicar por −1). Pruébalo.

**E5.** Añade a `Vector` el método `__matmul__` para que `a @ b` sea el **producto escalar** (NB13). Comprueba que `Vector(2, 3) @ Vector(4, 1)` da 11.

**E6.** Con `gym.make("PaloDeEscoba-v0")`, evalúa una política **al azar** que use `entorno.action_space.sample()`. ¿Cuánto saca?

**E7.** **Reto.** Escribe un envoltorio `RuidoEnSensores(gym.ObservationWrapper)` que añada a cada observación un ruido al azar (NB01: los sensores reales no son perfectos). Pista:
hereda de `gym.ObservationWrapper` y escribe un método `observation(self, observacion)` que devuelva la observación con ruido, por ejemplo
`observacion + self.np_random.normal(0, 0.5, size=2).astype(np.float32)`. Evalúa la política a mano con ese envoltorio: ¿aguanta?
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
class Cuadrupedo(Robot):
    def __init__(self, nombre, motores):
        super().__init__(nombre, motores)
        self.patas = 4

    def describir(self):
        return f"{super().describir()} y {self.patas} patas"

print(Cuadrupedo("Ant-v5", 8).describir())     # Ant-v5, con 8 motores y 4 patas
```
</details>

<details>
<summary>▶ Solución E2</summary>

El `__init__` de la madre no se ejecutaría, así que el objeto **no tendría** los atributos `nombre` ni `motores`. Al llamar a `h.describir()` (que usa `self.nombre`), saltaría un
**`AttributeError`**: `'Humanoide' object has no attribute 'nombre'`. Es exactamente el tipo de fallo "misterioso" del apartado 2: el error aparece lejos de su causa (la línea que
faltaba).
</details>

<details>
<summary>▶ Solución E3</summary>

```python
import random

class PoliticaAzar(Politica):
    def decidir(self, observacion):
        return random.uniform(-40, 40)

print(PoliticaAzar()((2.0, 0.0)))
```

Si escribieras `def decide(...)` (con la errata), la clase **no cumpliría el contrato** (le faltaría `decidir`), y al hacer `PoliticaAzar()` saltaría el `TypeError` de la clase
abstracta, **al crearla**. La clase abstracta te protege de la errata.
</details>

<details>
<summary>▶ Solución E4</summary>

Dentro de la clase `Vector`:

```python
    def __neg__(self):
        return self * -1
```

Luego `-Vector(4, 3)` da `Vector(-4, -3)`.
</details>

<details>
<summary>▶ Solución E5</summary>

Dentro de la clase `Vector`:

```python
    def __matmul__(self, otro):
        return sum(x * y for x, y in zip(self, otro))
```

`Vector(2, 3) @ Vector(4, 1)` da **11**. Es el mismo método especial que usa NumPy para su `@` (NB15).
</details>

<details>
<summary>▶ Solución E6</summary>

```python
entorno = gym.make("PaloDeEscoba-v0")
def politica_azar(observacion):
    return entorno.action_space.sample()
print(f"{evaluar(entorno, politica_azar):.1f}")
```

Saca un retorno bajo, del orden de los 40-50 puntos: como en el NB11, moverse al azar no sirve de nada. (`action_space.sample()` usa su propio generador de azar, distinto del del
viento.)
</details>

<details>
<summary>▶ Solución E7</summary>

```python
class RuidoEnSensores(gym.ObservationWrapper):
    def observation(self, observacion):
        ruido = self.np_random.normal(0, 0.5, size=2).astype(np.float32)
        return observacion + ruido

entorno_ruidoso = RuidoEnSensores(gym.make("PaloDeEscoba-v0"))
print(f"{evaluar(entorno_ruidoso, politica_lineal(30, 8)):.1f}")
```

(`np_random.normal(0, 0.5, ...)` da números al azar alrededor de 0, casi siempre entre −1 y 1; es la "campana de Gauss" que veremos en la siguiente parte.) Con este ruido moderado, la
política a mano sigue aguantando perfectamente (**499,9**): es **robusta**. Pero si subes el ruido a 5 (cambiando el `0.5` por `5`), se derrumba: unos **64**
puntos, cayéndose casi enseguida. Con sensores tan malos, ya no sabe bien dónde está el palo. Este envoltorio es la semilla de la **aleatorización del mundo** del NB02:
entrenar con sensores imperfectos prepara para el mundo real.
</details>
"""),

md(r"""## 12 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Ya sabes construir jerarquías de clases, contratos, objetos que se comportan como los de Python... y has creado un **entorno oficial de Gymnasium**. En el **NB26** salimos del cuaderno:
**ficheros** (guardar y cargar datos, configuraciones y políticas entrenadas), **módulos** propios (tu código en ficheros `.py` que se importan), **scripts** que se lanzan desde la
**terminal**, y las herramientas para instalar bibliotecas (`pip`, los entornos virtuales). Es decir: cómo se organiza un proyecto de verdad.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB25_python_herencia_gymnasium.ipynb")
    build(out, cells, title="NB25 · Python de verdad (6): herencia y tu propio entorno de Gymnasium")
