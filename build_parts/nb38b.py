"""Construye NB38b · Energía, trabajo y potencia (Parte 5 · lección intermedia).

Añadida tras la auditoría de 2026-10-04: NB39 (energía orbital), NB40 (motores
que se calientan), NB43 (castigo de control), NB45 (la energía como detector de
errores de la simulación) y NB50 (inercia reflejada, ½·J·ω²) usaban la energía
sin haberla enseñado. Aquí: trabajo = fuerza × distancia (solo la parte en la
dirección del movimiento: el producto escalar), julios; energía cinética ½·m·v²
deducida empujando un carrito a pasitos; potencial m·g·h; conservación (caída
desde 0,75 m sin simular); el palo de escoba del NB37 con energía: ½·I·ω² y la
velocidad al llegar al suelo, comprobada con nuestra simulación y con MuJoCo;
disipación; potencia = trabajo/tiempo = F·v = par·ω (signo: dar o absorber);
por qué los motores gastan aunque estén quietos (calor ∝ par²) y el castigo
de control; coste de transporte.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB38b · Energía, trabajo y potencia

**Parte 5 · La física del cuerpo — Lección intermedia (entre el NB38 y el NB39)**

> En el NB37 aprendiste a describir el movimiento con **fuerzas** y **pares**: qué empuja, cuánto acelera. Hoy aprenderás otra forma de mirar exactamente la misma física, que a menudo es **mucho más rápida**: la **energía**.

¿Por qué hace falta otra forma? Por tres razones muy prácticas:

1. **Responde preguntas sin simular.** ¿A qué velocidad llega al suelo el palo de escoba del NB37? Con fuerzas, hay que simular pasito a pasito. Con energía, es **una línea** de cuentas.
2. **Detecta errores.** La energía total de un sistema sin rozamiento **no cambia nunca**. Si en una simulación sube sola, la simulación está mal. En el NB45 y el NB49 la usarás exactamente para eso.
3. **Los robots tienen batería.** Un robot que anda muy bien pero gasta la batería en diez minutos no sirve. ¿Cuánto gasta un motor? ¿Por qué se calienta aunque esté quieto? ¿Por qué Gymnasium castiga las acciones grandes (NB35)? La respuesta es la **potencia**.

Las palabras de hoy (**trabajo**, **energía**, **potencia**) las usas a diario con otros significados. En física cada una tiene un significado **exacto**, con su número y su unidad. Vamos a construirlas una a una.
"""),

code(r"""import math
import numpy as np
import matplotlib.pyplot as plt

g = 9.81          # la gravedad, en m/s² (NB37)"""),

md(r"""## 1 · El trabajo: fuerza por distancia

### La idea

Subir una mochila de 10 kg una planta (3 m) cansa. Subirla **dos** plantas cansa el doble. Subir **dos** mochilas una planta, también el doble. El "esfuerzo" depende de **cuánta fuerza** haces y de **cuánta distancia** la haces. En física, a ese producto se le llama **trabajo**:

```
   trabajo  =  fuerza  ×  distancia
```

Su unidad es newton por metro, N·m, que tiene nombre propio: el **julio** (J), en honor al físico inglés James Joule. **1 julio** es el trabajo de empujar con 1 newton a lo largo de 1 metro: más o menos, levantar una manzana pequeña (100 g, que pesa 0,98 N) un metro.

Para subir la mochila hay que hacer, como poco, una fuerza igual a su peso, m·g (NB37):
"""),

code(r"""masa_mochila = 10
peso = masa_mochila * g                       # la fuerza para sostenerla (N)
trabajo = peso * 3                            # a lo largo de 3 metros
print(f"peso: {peso:.1f} N  →  trabajo: {trabajo:.0f} J")"""),

md(r"""**294 julios** para subir la mochila una planta.

### Solo cuenta la parte de la fuerza que va en la dirección del movimiento

Ahora lleva la mochila en brazos **por un pasillo llano**, 10 metros. Te cansas (los músculos trabajan para sostenerla), pero en física el trabajo sobre la mochila es **cero**: la fuerza (hacia arriba) y el movimiento (horizontal) son **perpendiculares**. Sostenerla hacia arriba no la hace avanzar ni subir.

Y si empujas un carrito con la fuerza un poco inclinada hacia abajo (como un carrito de la compra), solo la parte de la fuerza que va **hacia delante** hace trabajo; la parte que aprieta contra el suelo, no.

¿Te suena "la parte de un vector que va en la dirección de otro"? Es el **producto escalar** del NB13. El trabajo, en general, es:

```
   trabajo  =  fuerza · desplazamiento         (producto escalar de los dos vectores)
```

Si van en la misma dirección, es fuerza × distancia; si son perpendiculares, 0; si van en sentidos **contrarios** (frenar algo que se mueve), el trabajo es **negativo**: le **quitas** energía.
"""),

code(r"""fuerza = np.array([30.0, -20.0])           # 30 N hacia delante, 20 N hacia abajo (contra el suelo)
desplazamiento = np.array([5.0, 0.0])      # el carrito avanza 5 m en horizontal
print("trabajo:", np.dot(fuerza, desplazamiento), "J")"""),

md(r"""**150 J** = 30 N × 5 m. Los 20 N hacia abajo no cuentan.

### El trabajo de un giro

Para los giros, lo mismo cambiando fuerza por **par** (NB37) y distancia por **ángulo** (en radianes, NB36):

```
   trabajo de un giro  =  par  ×  ángulo girado (en radianes)
```

Un motor que hace 2 N·m mientras gira media vuelta (π radianes) hace 2 × π ≈ 6,3 J de trabajo. (¿Por qué funciona? Un par es fuerza por brazo, y girar un ángulo θ con un brazo r recorre un arco de r·θ metros, NB36. Fuerza × arco = fuerza × r × θ = par × θ.)

Ojo con las unidades: el par se mide en N·m, y el julio también es N·m. No son lo mismo, aunque se escriban igual. Por eso, para el trabajo, se usa siempre la palabra **julio**.
"""),

md(r"""## 2 · La energía de movimiento: ½·m·v²

### ¿Adónde va el trabajo?

Si empujas un carrito en un suelo **sin rozamiento**, el trabajo que haces no "desaparece": el carrito **acelera**. Todo el trabajo se queda guardado en su **movimiento**. A esa energía guardada se le llama **energía cinética** ("cinética" viene del griego *kinesis*, movimiento).

¿Cuánta? Hagamos el experimento con la cadena de oro del NB07: un carrito de 2 kg, parado, empujado con 10 N durante 3 segundos. En cada pasito sumamos el trabajo (fuerza × lo que avanza en ese pasito):
"""),

code(r"""masa, fuerza, paso = 2.0, 10.0, 0.001
velocidad, posicion, trabajo = 0.0, 0.0, 0.0
for i in range(3000):                               # 3000 pasitos de 1 ms = 3 s
    velocidad = velocidad + (fuerza / masa) * paso  # Newton: a = F / m (NB37)
    avance = velocidad * paso
    posicion = posicion + avance
    trabajo = trabajo + fuerza * avance             # el trabajo de este pasito
print(f"velocidad final: {velocidad:.2f} m/s | trabajo total: {trabajo:.1f} J")"""),

md(r"""El carrito acaba a 15 m/s, y le hemos hecho unos 225 J de trabajo. ¿Hay una fórmula que dé 225 a partir de la masa (2) y la velocidad (15)? Prueba: 2 × 15 = 30, no. 2 × 15² = 450, el doble. **½ × 2 × 15² = 225**. ¡Esa!

```
   energía cinética  =  ½ · m · v²
```

### Por qué ½·m·v²

No es casualidad, y la cuenta es corta. Empujando con una fuerza F constante desde parado (NB37, NB04b):

- La aceleración es a = F/m, así que **F = m·a**.
- Tras un tiempo t, la velocidad es **v = a·t**.
- Y la distancia recorrida es **d = ½·a·t²** (la de la caída libre del NB04b, con a en vez de g).

El trabajo es F × d = m·a × ½·a·t² = ½·m·(a·t)², y como a·t = v: **trabajo = ½·m·v²**. Todo el trabajo se ha convertido en ½·m·v².

### Lo que dice la fórmula

- **El doble de masa, el doble de energía**: normal.
- **El doble de velocidad, cuatro veces más energía** (por el cuadrado). Por eso un coche a 100 km/h choca **cuatro** veces más fuerte que a 50, y necesita cuatro veces más distancia para frenar.
- La energía cinética **nunca es negativa** (un cuadrado nunca lo es): da igual hacia dónde te muevas.

### Para los giros: ½·I·ω²

Algo que **gira** también guarda energía (una peonza, un volante de inercia). La fórmula es la gemela, cambiando masa por **inercia de giro** I y velocidad por **velocidad de giro** ω (NB37):

```
   energía cinética de giro  =  ½ · I · ω²
```

La necesitarás en el NB50, para entender por qué un motor con reductora "parece" mucho más pesado de lo que es.
"""),

md(r"""## 3 · La energía de altura: m·g·h

Sube la mochila a la estantería. Has hecho 294 J de trabajo, pero la mochila está **quieta**: no tiene energía cinética. ¿Se han perdido?

No: están **guardados en la altura**. Si la mochila se cae de la estantería, llegará al suelo con velocidad: recupera el trabajo como movimiento. A esta energía "en espera" se le llama **energía potencial** (de la gravedad):

```
   energía potencial  =  m · g · h          (h = la altura, en metros)
```

Es exactamente el trabajo de subirla: peso (m·g) × altura (h).

Un detalle: ¿altura medida **desde dónde**? Desde donde tú quieras (el suelo, la mesa, el centro de la Tierra). Lo que importa nunca es la energía potencial en sí, sino **cuánto cambia**, y los cambios no dependen de dónde pongas el cero. Es como medir alturas desde el nivel del mar o desde tu calle: los edificios miden lo mismo.

Para un robot, la h es la altura de su **centro de masas** (NB38): en la energía potencial, todo el robot cuenta como si estuviera en ese punto. En el NB45 verás que MuJoCo calcula 181 J para un robot de 23,6 kg con el CdM a 0,78 m de altura: 23,6 × 9,81 × 0,783 ≈ 181.
"""),

md(r"""## 4 · La conservación de la energía

### La ley

Juntamos las dos: a la suma de cinética y potencial se le llama **energía mecánica**. Y la ley más famosa de la física dice:

> **Si no hay rozamientos ni motores, la energía mecánica total no cambia nunca.** Puede pasar de potencial a cinética y al revés, pero la suma es siempre la misma.

Es la **conservación de la energía**. Comprobémosla con una pelota de 0,5 kg que cae desde 0,75 m (la del NB02), simulada a pasitos:
"""),

code(r"""m, altura, v, paso = 0.5, 0.75, 0.0, 0.0001
for i in range(3):                                   # tres "fotos" de la caída
    print(f"h = {altura:.3f} m | cinética {0.5 * m * v ** 2:.4f} J + potencial {m * g * altura:.4f} J "
          f"= {0.5 * m * v ** 2 + m * g * altura:.4f} J")
    for j in range(1300):                            # 0,13 s de caída entre foto y foto
        v = v - g * paso                             # la gravedad acelera hacia abajo
        altura = altura + v * paso"""),

md(r"""La potencial baja, la cinética sube, y la **suma** se queda en 3,678 J (moviéndose solo en la cuarta cifra decimal: el error de los pasitos, NB07).

### La pregunta sin simular

Ahora el truco. ¿A qué velocidad llega la pelota al suelo? Toda la potencial del principio se ha convertido en cinética:

```
   ½ · m · v²  =  m · g · h           →  la m se va a los dos lados  →        v = √(2 · g · h)
```

(Despejar, NB04b: dividir entre m, multiplicar por 2, raíz cuadrada.) Sin simular nada:
"""),

code(r"""print(f"velocidad al llegar al suelo: {math.sqrt(2 * g * 0.75):.2f} m/s")"""),

md(r"""**3,84 m/s** (unos 14 km/h). Fíjate: la **masa ha desaparecido** otra vez, como en el NB37. Una pelota de hierro y una de goma llegan igual de deprisa (sin aire). Y la respuesta no depende del **camino**: si la pelota bajara 0,75 m rodando por una rampa sin rozamiento, también llegaría a 3,84 m/s (más tarde, pero igual de rápida). Las fuerzas te obligan a seguir el camino paso a paso; la energía solo mira el **principio y el final**.
"""),

md(r"""## 5 · El palo de escoba, con energía

### La pregunta

En el NB37 simulaste el palo de escoba de 1,5 m y 1 kg cayendo desde 0,05 radianes hasta el suelo. ¿A qué **velocidad de giro** llega al suelo? Con energía, sin simular:

- **Potencial**: el CdM del palo está en su mitad. Con el palo inclinado θ desde la vertical, el CdM está a una altura (L/2)·cos θ (la "sombra vertical" del NB36). Al caer de θ₀ = 0,05 a θ = π/2 (horizontal, cos = 0), la altura del CdM baja de (L/2)·cos 0,05 a 0.
- **Cinética**: el palo gira alrededor de su extremo, así que su energía cinética es de giro, ½·I·ω², con I = m·L²/3 (NB37).

Igualando lo que se pierde de potencial con lo que se gana de cinética:

```
   ½ · (m·L²/3) · ω²  =  m · g · (L/2) · cos θ₀            →       ω = √(3 · g · cos θ₀ / L)
```

(La m se va otra vez; el resto es despejar. Inténtalo tú en el ejercicio E5.)
"""),

code(r"""L, masa_palo, theta0 = 1.5, 1.0, 0.05
omega_energia = math.sqrt(3 * g * math.cos(theta0) / L)
print(f"velocidad de giro al llegar al suelo (con energía): {omega_energia:.3f} rad/s")"""),

md(r"""Unos **4,43 rad/s**. Ahora, la comprobación: la simulación del NB37 (la misma cadena de oro), devolviendo la velocidad final en lugar de los tiempos:"""),

code(r"""def caida(largo, theta_inicial=0.05, paso=0.0001):
    theta, velocidad = theta_inicial, 0.0
    while theta < math.pi / 2:
        aceleracion = 3 * g / (2 * largo) * math.sin(theta)   # la ecuación de la escoba (NB37)
        velocidad = velocidad + aceleracion * paso
        theta = theta + velocidad * paso
    return velocidad

print(f"velocidad de giro al llegar al suelo (simulando):   {caida(L):.3f} rad/s")"""),

md(r"""¡La misma, hasta la tercera cifra decimal! Y una vez más, el palo de hierro y el de madera, iguales.

### El examen de MuJoCo

El mismo palo del NB37 en MuJoCo. Esta vez, a cada paso calculamos **nosotros** su energía mecánica, con lo que MuJoCo nos da: el ángulo (`qpos`) y la velocidad de giro (`qvel`, NB36). Si MuJoCo hace bien la física, la suma no debería moverse:
"""),

code(r"""import mujoco

plano = '''
<mujoco>
  <option timestep="0.001"/>
  <worldbody>
    <body>
      <joint type="hinge" axis="0 1 0"/>
      <geom type="cylinder" fromto="0 0 0  0 0 1.5" size="0.005" mass="1"/>
    </body>
  </worldbody>
</mujoco>
'''
modelo = mujoco.MjModel.from_xml_string(plano)
datos = mujoco.MjData(modelo)
I = masa_palo * L ** 2 / 3                                  # inercia de giro sobre el extremo (NB37)"""),

md(r"""(El mismo plano del NB37: un palo de 1,5 m y 1 kg con una bisagra en su extremo de abajo.) Una función para la energía, y la caída:"""),

code(r"""def energia(theta, omega):
    cinetica = 0.5 * I * omega ** 2
    potencial = masa_palo * g * (L / 2) * math.cos(theta)
    return cinetica, potencial

datos.qpos[0] = theta0
while datos.qpos[0] < math.pi / 2:
    if round(datos.time, 3) in (0.0, 0.8, 1.2):        # tres "fotos"
        c, p = energia(datos.qpos[0], datos.qvel[0])
        print(f"t = {datos.time:.1f} s | cinética {c:.3f} + potencial {p:.3f} = {c + p:.3f} J")
    mujoco.mj_step(modelo, datos)
print(f"MuJoCo llega al suelo a {datos.qvel[0]:.3f} rad/s (con energía: {omega_energia:.3f})")"""),

md(r"""(`datos.time` es el reloj de la simulación; `round(..., 3)` lo redondea a milésimas para poder compararlo con 0,8 sin líos de decimales, NB05b.)

La energía total se queda en **7,35 J** mientras pasa de potencial a cinética (al final, 7,34: una centésima menos, el error de los pasitos de 1 ms). Y la velocidad final casa con la de nuestra cuenta de una línea. Ya tienes una herramienta para **comprobar** cualquier simulador: si la energía de algo sin rozamiento ni motores no se conserva, algo va mal.
"""),

md(r"""## 6 · Cuando la energía "se pierde": la disipación

En el mundo real, una pelota que bota no vuelve a la misma altura, y un columpio acaba parándose. ¿Se ha roto la ley?

No. La energía mecánica se convierte en **otras formas de energía** que no vemos: **calor** (frota tus manos: se calientan), **sonido** (el "plof" de la pelota), deformación. La energía total del universo se conserva siempre; la **mecánica** solo se conserva cuando no hay nada que la convierta en calor. A esa pérdida se le llama **disipación**, y las cosas que disipan energía son:

- el **rozamiento** (los pies que resbalan, los engranajes de los motores, NB40);
- los **amortiguadores** (como el de la Hopper-estatua del NB38: un amortiguador existe **para** disipar);
- los **choques**: en el NB45 verás una caja que cae y no rebota nada: toda su cinética se disipa en el contacto.

Con esto, la regla del detector de errores (NB45) queda completa:

- La energía mecánica **baja** un poco → normal: rozamientos, amortiguadores, choques (y algo de error de los pasitos).
- La energía mecánica **sube** sin que ningún motor ni empujón la meta → **la simulación está mal**.
"""),

md(r"""## 7 · La potencia: lo deprisa que se hace el trabajo

### La idea

Subir la mochila una planta son 294 J, tanto si subes andando en un minuto como si subes corriendo en diez segundos. Pero corriendo te cansas mucho más. La diferencia es la **rapidez** con la que haces el trabajo, y se llama **potencia**:

```
   potencia  =  trabajo  ÷  tiempo
```

Su unidad es el julio por segundo, que tiene nombre propio: el **vatio** (W), en honor a James Watt, el de la máquina de vapor. Una bombilla LED gasta unos 10 W; un microondas, unos 1000 W (1 kW).
"""),

code(r"""for tiempo in [60, 10]:
    print(f"subir la mochila en {tiempo:>2} s: {294 / tiempo:5.1f} W")"""),

md(r"""### Potencia = fuerza × velocidad

En un pasito muy corto, el trabajo es fuerza × lo que avanzas. Dividiendo entre el tiempo del pasito, "lo que avanzas ÷ tiempo" es la velocidad:

```
   potencia  =  fuerza × velocidad                (en un giro:   potencia  =  par × velocidad de giro)
```

La de los giros es **la fórmula de los motores**. Un motor de Hopper puede hacer 200 N·m (NB37). Si a la vez gira la rodilla a 10 rad/s (más o menos 1,6 vueltas por segundo), está dando:
"""),

code(r"""par, omega = 200, 10
print(f"potencia del motor: {par * omega} W")"""),

md(r"""**2000 W**: como dos microondas, en una sola rodilla. En el NB40 verás que ningún motor real puede dar a la vez su par máximo y su velocidad máxima, justo porque eso exigiría una potencia enorme.

### El signo de la potencia

- **Par y giro en el mismo sentido** (potencia **positiva**): el motor **da** energía. Levanta el robot, lo impulsa.
- **Par y giro en sentidos contrarios** (potencia **negativa**): el motor **frena** un movimiento: **absorbe** energía. Pasa al aterrizar de un salto, al bajar escaleras, al sentarse despacio. Esa energía, en casi todos los robots, se convierte en calor (algunos la recuperan para la batería, como los coches eléctricos al frenar).
"""),

md(r"""## 8 · Por qué los motores gastan aunque no se muevan

Una pregunta con trampa: un robot quieto, con las rodillas dobladas, sosteniendo su peso. Sus motores hacen par, pero no giran: potencia mecánica = par × 0 = **0**. ¿Gasta batería?

**Sí, y bastante.** La potencia mecánica es lo que el motor **entrega**, no lo que **consume**. Un motor eléctrico hace par haciendo pasar **corriente** por sus bobinas, y el par es proporcional a la corriente (el doble de par, el doble de corriente). Pero cualquier corriente que pasa por un cable lo **calienta**, y ese calor crece con el **cuadrado** de la corriente (el doble de corriente, cuatro veces más calor). Así que:

```
   calor perdido en el motor  ∝  par²            (∝ significa "proporcional a")
```

Aunque el motor no se mueva, sostener un par cuesta energía, y la convierte toda en calor. Es lo que viste anunciado en el NB40... y lo que les pasa a tus músculos en una sentadilla quieta.

### El castigo de control de Gymnasium

Ahora entiendes la recompensa de Hopper del NB35: castiga **0,001 × (suma de las acciones al cuadrado)**. Las acciones son pares (normalizados), así que ese término es, más o menos, **el calor que generan los motores**: un castigo por gastar batería. Al cuadrado, porque así es la física: un par doble cuesta cuatro veces más. En el NB43 y el NB44 verás qué pasa cuando este término es demasiado pequeño: el robot "corre a lo loco" sin importarle el gasto.

### El coste de transporte

¿Cómo comparar lo eficiente que es andar para un robot de 30 kg y una persona de 70? No vale comparar julios: el pesado siempre gasta más. Los ingenieros usan el **coste de transporte**:

```
   coste de transporte  =  energía gastada  ÷  (peso × distancia recorrida)
```

Es la energía gastada **por cada newton de peso y cada metro**. No tiene unidades (J ÷ (N × m) = J ÷ J), así que se puede comparar entre cualquier cosa que se mueva. Según un estudio famoso de 2005 (Collins y colegas, en la revista *Science*), una persona andando tiene un coste de transporte de más o menos **0,2**, y el robot ASIMO de Honda, de unos **3,2**: **dieciséis veces más**. Andar de forma eficiente sigue siendo uno de los grandes retos de la robótica, y uno de los motivos por los que se entrenan robots con recompensas que castigan el gasto.
"""),

code(r"""def coste_de_transporte(energia_J, masa_kg, distancia_m):
    return energia_J / (masa_kg * g * distancia_m)

# Una persona de 70 kg que anda 1 km gastando unos 140.000 J (unas 33 kilocalorías)
print(f"persona: {coste_de_transporte(140_000, 70, 1000):.2f}")"""),

md(r"""(La kilocaloría, la "caloría" de los envases de comida, son 4184 J.) Sale 0,2, como en el estudio.
"""),

md(r"""## 9 · Resumen de la lección

1. **Trabajo** = fuerza × distancia (solo la parte en la dirección del movimiento: el **producto escalar** fuerza · desplazamiento). En giros, **par × ángulo** (radianes). Unidad: **julio** (J). Negativo si frenas.
2. **Energía cinética** = **½·m·v²** (el trabajo para ponerlo en marcha); de giro, **½·I·ω²**. El doble de velocidad, cuatro veces más energía.
3. **Energía potencial** = **m·g·h** (el trabajo para subirlo); para un robot, h = la altura del CdM. Solo importan sus cambios.
4. **Conservación**: sin rozamientos ni motores, cinética + potencial no cambia. Responde sin simular: **v = √(2·g·h)**; el palo de escoba llega al suelo a ω = √(3·g·cos θ₀ / L) ≈ 4,43 rad/s, como nuestra simulación y MuJoCo.
5. **Disipación**: rozamiento, amortiguadores y choques convierten energía mecánica en calor. Energía que **baja**, normal; que **sube** sola, **simulación mal**.
6. **Potencia** = trabajo ÷ tiempo = **fuerza × velocidad** = **par × ω**. Unidad: **vatio** (W). Positiva = el motor da energía; negativa = la absorbe (frena).
7. Un motor quieto que hace par **gasta**: calor ∝ par². Por eso el **castigo de control** usa acciones **al cuadrado**.
8. **Coste de transporte** = energía ÷ (peso × distancia): persona ≈ 0,2; ASIMO ≈ 3,2.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Trabajo** | Fuerza por distancia en la dirección del movimiento (o par por ángulo). |
| **Julio (J)** | La unidad de trabajo y de energía: 1 N a lo largo de 1 m. |
| **Energía cinética** | La energía del movimiento: ½·m·v² (de giro, ½·I·ω²). |
| **Energía potencial** | La energía guardada en la altura: m·g·h. |
| **Energía mecánica** | Cinética + potencial. |
| **Conservación de la energía** | Sin rozamientos ni motores, la energía mecánica no cambia. |
| **Disipación** | Convertir energía mecánica en calor (rozamiento, amortiguadores, choques). |
| **Potencia** | Lo deprisa que se hace un trabajo: fuerza × velocidad, par × ω. |
| **Vatio (W)** | La unidad de potencia: 1 julio cada segundo. |
| **Coste de transporte** | Energía gastada por cada newton de peso y cada metro recorrido. |
"""),

md(r"""## 10 · Ejercicios

**E1.** Un robot de 30 kg sube una escalera de 2 m de altura. ¿Cuánto trabajo hace, como mínimo, contra la gravedad? Si tarda 8 s, ¿qué potencia media necesita?

**E2.** Una fuerza de 50 N tira de un trineo con la cuerda inclinada: el vector fuerza es (40, 30) (40 N hacia delante, 30 N hacia arriba). El trineo avanza 10 m en horizontal. ¿Cuánto trabajo hace la fuerza? ¿Y si el trineo avanzara 10 m **hacia atrás** (resbalando cuesta abajo)?

**E3.** Un coche de 1000 kg va a 50 km/h y otro igual a 100 km/h. Calcula sus energías cinéticas (¡pasa antes a m/s: divide entre 3,6!). ¿Cuántas veces más tiene el segundo?

**E4.** ¿Desde qué altura habría que soltar una pelota para que llegue al suelo a 10 m/s? (Despeja h de v = √(2·g·h).) Compruébalo simulando la caída a pasitos.

**E5.** Deduce ω = √(3·g·cos θ₀ / L) del apartado 5 a partir de ½·(m·L²/3)·ω² = m·g·(L/2)·cos θ₀. Luego: ¿a qué velocidad de giro llega al suelo un **lápiz** de 15 cm que cae desde la misma inclinación? ¿Y la **punta** del lápiz, en m/s? (Pista: la velocidad de un punto a distancia r del eje es r·ω, NB36.)

**E6.** Un motor hace un par de −15 N·m mientras la articulación gira a +4 rad/s. ¿Qué potencia tiene? ¿Está dando o absorbiendo energía? ¿Qué podría estar haciendo el robot?

**E7.** En una sentadilla quieta, la rodilla de un robot hace 40 N·m, y la de otro, 80 N·m. Si el calor es proporcional al par², ¿cuántas veces más se calienta el segundo motor? ¿Y si la acción de Hopper pasa de 0,5 a 1, cuántas veces crece el castigo de control?

**E8.** Un robot de 25 kg anda 100 m gastando 50.000 J de batería. ¿Cuál es su coste de transporte? ¿Más cerca de una persona o de ASIMO?

---

### Soluciones

<details>
<summary>▶ Solución E1</summary>

Trabajo = m·g·h = 30 × 9,81 × 2 ≈ **588,6 J**. Potencia media = 588,6 / 8 ≈ **73,6 W**.

```python
trabajo = 30 * g * 2
print(f"{trabajo:.1f} J, {trabajo / 8:.1f} W")
```
</details>

<details>
<summary>▶ Solución E2</summary>

Producto escalar: (40, 30) · (10, 0) = 400 + 0 = **400 J**. La parte vertical (30 N) no hace trabajo. Hacia atrás: (40, 30) · (−10, 0) = **−400 J**: la fuerza va contra el movimiento, le quita energía al trineo (lo frena).

```python
f = np.array([40.0, 30.0])
print(np.dot(f, np.array([10.0, 0.0])), np.dot(f, np.array([-10.0, 0.0])))
```
</details>

<details>
<summary>▶ Solución E3</summary>

50 km/h = 13,9 m/s → ½ × 1000 × 13,9² ≈ **96.451 J**. 100 km/h = 27,8 m/s → ≈ **385.802 J**. Exactamente **cuatro veces** más (el doble de velocidad, al cuadrado).

```python
for kmh in [50, 100]:
    v = kmh / 3.6
    print(f"{kmh} km/h: {0.5 * 1000 * v ** 2:,.0f} J")
```
</details>

<details>
<summary>▶ Solución E4</summary>

v² = 2·g·h → h = v² / (2·g) = 100 / 19,62 ≈ **5,10 m** (un segundo piso).

```python
h = 10 ** 2 / (2 * g)
altura, v, paso = h, 0.0, 0.0001
while altura > 0:
    v = v - g * paso
    altura = altura + v * paso
print(f"h = {h:.2f} m → llega a {abs(v):.2f} m/s")
```
</details>

<details>
<summary>▶ Solución E5</summary>

Tachamos m a los dos lados: ½·(L²/3)·ω² = g·(L/2)·cos θ₀. Multiplicamos por 2: (L²/3)·ω² = g·L·cos θ₀. Multiplicamos por 3 y dividimos entre L²: ω² = 3·g·cos θ₀ / L. Raíz: **ω = √(3·g·cos θ₀ / L)**.

Lápiz (L = 0,15): ω ≈ **14,0 rad/s** (√10 ≈ 3,16 veces más que la escoba, porque la L está dividiendo dentro de la raíz). La punta, a 0,15 m del eje: 0,15 × 14,0 ≈ **2,1 m/s**. La de la escoba: 1,5 × 4,43 ≈ 6,6 m/s. El lápiz gira más deprisa, pero su punta va más despacio.

```python
for nombre, largo in [("escoba", 1.5), ("lápiz", 0.15)]:
    w = math.sqrt(3 * g * math.cos(0.05) / largo)
    print(f"{nombre}: ω = {w:.2f} rad/s, punta a {largo * w:.2f} m/s")
```
</details>

<details>
<summary>▶ Solución E6</summary>

Potencia = par × ω = −15 × 4 = **−60 W**. Negativa: el motor **absorbe** energía, está **frenando** el giro. Por ejemplo: la rodilla de un robot que aterriza de un salto o que baja un escalón, cediendo poco a poco para no chocar de golpe.
</details>

<details>
<summary>▶ Solución E7</summary>

El doble de par → (80/40)² = **4 veces** más calor. Hopper: 0,5² = 0,25 → 1² = 1: también **4 veces** más castigo.
</details>

<details>
<summary>▶ Solución E8</summary>

50.000 / (25 × 9,81 × 100) ≈ **2,04**. Mucho más cerca de ASIMO (3,2) que de una persona (0,2): diez veces menos eficiente que andar como un humano.

```python
print(round(coste_de_transporte(50_000, 25, 100), 2))
```
</details>
"""),

md(r"""## 11 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **NB39** vuelve el equilibrio, ahora en movimiento: el **péndulo invertido lineal**, el **punto de captura** y el **ZMP**. Allí aparecerá una "**energía orbital**" que se conserva: no es exactamente la energía de hoy, pero es su pariente, y la usarás con el mismo truco que en el apartado 4: si algo no cambia, el principio te dice el final.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB38b_energia_trabajo_potencia.ipynb")
    build(out, cells, title="NB38b · Energía, trabajo y potencia")
