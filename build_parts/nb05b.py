"""Construye NB05b · Tu ordenador por dentro y la terminal (Parte 1 · lección intermedia).

Añadida tras la auditoría de 2026-10-04: el NB05 daba la terminal, el entorno
virtual y Jupyter como "palabras mágicas", y el curso usaba después binario,
bytes, núcleos, hilos y procesos sin explicarlos. Las piezas del ordenador
(CPU y núcleos, RAM, disco, GPU) con la analogía de la cocina; todo son
números: bits, contar en binario, bytes, texto como números, KB/MB/GB; por qué
0,1 no es exacto; programas, procesos e hilos; archivos, carpetas, rutas
(absolutas, relativas, ~, extensiones, directorio de trabajo); la terminal y
sus órdenes básicas (con ! en Jupyter); las tres palabras mágicas explicadas
(cd, entorno virtual, Jupyter como servidor local); instalar el curso en tu
propio ordenador.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, build

cells = [

md(r"""# NB05b · Tu ordenador por dentro y la terminal

**Parte 1 · Primeros pasos con Python — Lección intermedia (entre el NB05 y el NB06)**

> En el NB05 te pedí que escribieras tres "palabras mágicas" en una ventana negra para abrir el cuaderno, y te prometí explicarlas "más adelante". Ese momento es hoy. Y de paso vamos a abrir la caja del ordenador: qué piezas tiene, cómo guarda las cosas (todo, absolutamente todo, son números), qué es un archivo, qué es una carpeta... y cómo se le habla escribiendo.

Esta lección es casi toda **teoría**, con solo un par de órdenes para probar. Pero es teoría que usarás durante todo el curso y toda tu vida profesional: cuando un programa vaya lento (NB49), cuando un número decimal salga "raro" (NB06), cuando algo diga "file not found" (NB26), o cuando quieras instalar el curso en tu propio ordenador (sección 7).
"""),

md(r"""## 1 · Las piezas del ordenador: una cocina

### La analogía

Un ordenador se parece mucho a una **cocina de restaurante**:

| Pieza del ordenador | En la cocina | Qué hace |
|---|---|---|
| **Procesador (CPU)** | el **cocinero** | hace todas las cuentas, una detrás de otra, rapidísimo |
| **Núcleos** de la CPU | **varios cocineros** | cada núcleo es un cocinero independiente; pueden trabajar a la vez |
| **Memoria RAM** | la **encimera** | donde se ponen las cosas con las que se está trabajando ahora mismo: muy rápida de alcanzar, pero no muy grande, y **se vacía** al apagar |
| **Disco** (almacenamiento) | la **despensa** | donde se guarda todo de forma **permanente**: mucho más grande, pero más lenta de alcanzar |
| **Tarjeta gráfica (GPU)** | un **equipo de pinches** | cientos o miles de ayudantes que solo saben hacer cosas sencillas, pero todos a la vez |

Tu Raspberry Pi 5, por ejemplo, tiene una CPU con **4 núcleos** (4 cocineros), unos pocos gigas de RAM y una tarjeta de memoria como disco. No tiene una GPU potente: por eso, para los entrenamientos gigantes del final del curso, usaremos ordenadores de internet que sí la tienen (Google Colab).

### Por qué importa la diferencia entre RAM y disco

Cuando abres un cuaderno, Python va guardando tus variables en la **RAM** (la encimera). Si cierras el cuaderno o se apaga el ordenador, **desaparecen**. Para que algo sobreviva, hay que guardarlo en el **disco** (la despensa), en un **archivo**. Por eso, cuando entrenemos un robot durante horas, lo primero será **guardar** lo aprendido en un archivo (NB26, NB34): si no, al apagar, se perdería todo.
"""),

md(r"""## 2 · Todo son números: bits y bytes

### El bit

Dentro del ordenador no hay letras, ni imágenes, ni robots: solo hay **interruptores**. Miles de millones de interruptores diminutos, cada uno **encendido o apagado**. Un interruptor puede guardar **dos** valores, que se escriben **1** (encendido) y **0** (apagado). Esa unidad mínima de información se llama **bit** (de *binary digit*, "dígito binario").

### Contar en binario

Con un bit solo hay dos posibilidades (0 y 1). Con dos bits, cuatro: 00, 01, 10, 11. Con tres, ocho. Cada bit que añades **dobla** las posibilidades (crecimiento exponencial, NB03b): n bits dan 2ⁿ combinaciones.

Y con ellas se puede **contar**, igual que con nuestras cifras del 0 al 9, pero usando solo 0 y 1. Recuerda el **valor posicional** (NB03b): en nuestro sistema, cada puesto vale 10 veces más que el de su derecha (unidades, decenas, centenas). En **binario**, cada puesto vale **2** veces más:

```
   puesto:     8    4    2    1
              ───  ───  ───  ───
   0101   =    0  + 4  + 0  + 1   =  5
   1010   =    8  + 0  + 2  + 0   =  10
   1111   =    8  + 4  + 2  + 1   =  15
```

Así que "101" en binario es el 5 de toda la vida. El ordenador guarda **todos** los números así.

### El byte

Los bits se agrupan de 8 en 8: un grupo de 8 bits se llama **byte**. Con 8 bits hay 2⁸ = **256** combinaciones, así que un byte puede guardar un número del 0 al 255.

Y los tamaños de las cosas se miden en bytes, con los prefijos del NB03b:

| Unidad | Aproximadamente | Ejemplo |
|---|---|---|
| 1 byte (B) | 8 bits | una letra |
| 1 kilobyte (KB) | mil bytes | una página de texto |
| 1 megabyte (MB) | un millón de bytes | una foto |
| 1 gigabyte (GB) | mil millones de bytes | una película |

(Un detalle que verás algún día: como los ordenadores cuentan en potencias de 2, a veces "kilo" significa 1.024 = 2¹⁰ en vez de 1.000. La diferencia es pequeña, y no la necesitarás en el curso.)

### El texto también son números

¿Y las letras? Se guardan con una **tabla** que asigna un número a cada carácter. Es un acuerdo mundial: la **A** es el 65, la **B** el 66, la **a** minúscula el 97, el espacio el 32, la **ñ** el 241... (El sistema que se usa hoy se llama **Unicode**, y tiene números para las letras de todos los idiomas, los símbolos y hasta los emojis.) Cuando escribes "hola", el ordenador guarda cuatro números. Esto explicará más adelante algunas rarezas, como que al ordenar palabras las mayúsculas vayan antes que las minúsculas (NB20: 65 es menor que 97).

### Por qué los decimales a veces salen raros

Y aquí está la explicación prometida para el NB06. En el NB03b viste que 1/3 = 0,333... no se puede escribir exacto con nuestras cifras, porque no termina nunca. En **binario** pasa lo mismo con números que a nosotros nos parecen sencillísimos, como **0,1**: en binario es 0,000110011001100110011... **para siempre**. El ordenador tiene que **cortarlo** en algún sitio (guarda unas 16 cifras), así que su 0,1 es **casi** 0,1, pero no exactamente. Por eso, en el NB06, verás que `0.1 + 0.2` da `0.30000000000000004`. No es un error del ordenador: es lo mismo que te pasaría a ti escribiendo 1/3 con cifras.
"""),

md(r"""## 3 · Programas, procesos e hilos

### Del programa al proceso

Un **programa** es una lista de instrucciones guardada en el disco (como una receta en un libro). Cuando lo **pones en marcha**, el ordenador lo copia a la RAM y empieza a ejecutarlo: a ese programa en marcha se le llama **proceso** (el plato que se está cocinando ahora).

Tu ordenador tiene **muchísimos procesos** a la vez: el navegador, el reproductor de música, el propio Jupyter, el kernel de Python... El **sistema operativo** (Linux en tu Raspberry Pi; Windows o macOS en otros ordenadores) es el "jefe de cocina": reparte los núcleos entre todos los procesos, saltando de uno a otro tan deprisa que parece que todos funcionan a la vez.

Cada proceso tiene **su propia encimera** (su zona de RAM): un proceso no puede tocar la memoria de otro. Eso es bueno (si un programa falla, no estropea a los demás), pero significa que, para pasarse datos, tienen que **copiárselos**.

### Hilos: varios trabajadores en la misma cocina

A veces, un mismo proceso quiere hacer varias cosas a la vez (por ejemplo, simular 4 robots). Para eso puede crear varios **hilos** (*threads*): trabajadores que comparten **la misma encimera** (la misma memoria) y pueden ir cada uno en un núcleo distinto.

- **Varios procesos**: cocinas separadas, cada una con su encimera. Muy seguros, pero pasarse cosas es lento (hay que copiarlas).
- **Varios hilos**: varios cocineros en la misma cocina, compartiendo encimera. Rápido para compartir, pero tienen que tener cuidado de no pisarse (dos cocineros cogiendo el mismo cuchillo).

Con una CPU de 4 núcleos, como mucho 4 cosas pueden ocurrir **de verdad** a la vez. En el NB49 aprovecharemos esto para simular varios robots en paralelo, y verás una peculiaridad muy famosa de Python (el "GIL") que hace que con sus hilos no siempre se gane velocidad.
"""),

md(r"""## 4 · Archivos y carpetas

### El árbol de carpetas

Lo que hay en el disco se organiza en **archivos** (también llamados ficheros), que se guardan dentro de **carpetas** (o directorios), que pueden estar dentro de otras carpetas... formando un **árbol**, como el de los cuerpos de un robot (NB01). Por ejemplo, el curso está organizado así:

```
/                                   ← la raíz: la carpeta que lo contiene todo
└── home
    └── gregori                     ← la carpeta personal del usuario
        └── dev
            └── robotica            ← la carpeta del curso
                ├── notebooks       ← los cuadernos
                │   ├── NB05_primer_contacto.ipynb
                │   ├── zancudo_env.py
                │   └── robots
                │       └── zancudo.xml
                ├── requirements
                └── venv            ← el entorno virtual (sección 7)
```

### Rutas

Para decirle al ordenador **dónde** está un archivo, se escribe su **ruta**: el camino de carpetas hasta él, separadas por barras `/`:

- **Ruta absoluta**: el camino completo **desde la raíz** `/`. Empieza siempre por `/`: `/home/gregori/dev/robotica/notebooks/robots/zancudo.xml`. Funciona desde cualquier sitio.
- **Ruta relativa**: el camino **desde donde estás ahora**. Si estás en la carpeta `notebooks`, el mismo archivo es simplemente `robots/zancudo.xml`. Es más corta, pero solo funciona si estás en el sitio correcto.

Tres atajos que verás mucho:

- **`~`** (la "virgulilla", la tilde de la ñ sola): tu **carpeta personal**. `~/dev/robotica` = `/home/gregori/dev/robotica`.
- **`.`** (un punto): la carpeta **actual**.
- **`..`** (dos puntos): la carpeta **de arriba** (la "madre").

(En Windows las rutas se escriben con la barra al revés, `\`, y empiezan por una letra de disco, como `C:\`. La idea es la misma.)

### El directorio de trabajo

Todo programa en marcha "está" en alguna carpeta: su **directorio de trabajo**. Las rutas relativas se buscan **desde ahí**. Cuando un cuaderno de este curso abre `robots/zancudo.xml`, funciona porque el cuaderno trabaja desde la carpeta `notebooks`. Si lo ejecutaras desde otra carpeta, Python no lo encontraría (y te diría `FileNotFoundError`, "archivo no encontrado": lo verás en el NB26).

### Extensiones

El final del nombre de un archivo, tras el último punto, es su **extensión**, y dice **de qué tipo** es: `.py` (programa de Python), `.ipynb` (cuaderno de Jupyter), `.xml` (el formato en que se describen los robots, NB42), `.txt` (texto), `.png` (imagen)... Es solo parte del nombre, pero los programas la usan para saber cómo abrir cada archivo.
"""),

md(r"""## 5 · La terminal: hablar con el ordenador escribiendo

### Qué es

Normalmente usas el ordenador con el ratón: haces clic en iconos, arrastras ventanas. Pero hay otra forma, más antigua y mucho más potente: **escribirle órdenes**. La **terminal** (también llamada consola o línea de comandos) es esa ventana, normalmente negra, donde escribes una orden, pulsas Enter, y el ordenador la ejecuta y te contesta con texto.

¿Por qué usarla, si existe el ratón? Porque casi todas las herramientas de programación funcionan así, porque se puede **automatizar** (una lista de órdenes se puede repetir mil veces), y porque los ordenadores donde se entrenan los robots de verdad (servidores en internet) **no tienen pantalla**: solo se puede hablar con ellos escribiendo.

### El indicador

Al abrir una terminal verás algo como:

```
gregori@raspberrypi:~/dev/robotica $
```

Es el **indicador** (*prompt*): te dice quién eres (`gregori`), en qué ordenador estás (`raspberrypi`), en qué carpeta (`~/dev/robotica`) y que está esperando una orden (`$`). Tú escribes después del `$`.

### Las órdenes básicas

| Orden | Significa | Qué hace |
|---|---|---|
| `pwd` | *print working directory* | dice en qué carpeta estás |
| `ls` | *list* | lista lo que hay en la carpeta |
| `cd carpeta` | *change directory* | entra en una carpeta |
| `cd ..` | | sube a la carpeta de arriba |
| `cd ~` | | vuelve a tu carpeta personal |
| `mkdir nombre` | *make directory* | crea una carpeta |
| `cat archivo` | *concatenate* | muestra lo que hay dentro de un archivo de texto |

Y tres trucos que ahorran muchísimo tiempo:

- **Tabulador**: empieza a escribir un nombre y pulsa la tecla Tab: la terminal lo **completa** sola.
- **Flecha arriba**: recupera la orden anterior (para repetirla o corregirla).
- **Ctrl + C**: **interrumpe** la orden que se está ejecutando (si algo se queda colgado).

### Probarlo desde el cuaderno

Desde una celda de Jupyter se pueden ejecutar órdenes de la terminal poniendo una **exclamación** `!` delante. Probemos dos: ¿en qué carpeta trabaja este cuaderno?, y ¿qué hay en su carpeta `robots`?
"""),

code(r"""!pwd"""),

code(r"""!ls robots"""),

md(r"""La primera dice la ruta **absoluta** de la carpeta donde trabaja el cuaderno (la carpeta `notebooks`). La segunda lista lo que hay en la subcarpeta `robots` (una ruta **relativa**): los archivos que describen nuestros robots (los conocerás en el NB42).

(El `!` es un truco de Jupyter, no de Python: le dice "esto no es Python, pásaselo a la terminal". En un programa de Python normal no funciona.)
"""),

md(r"""## 6 · Las palabras mágicas, explicadas

Ya podemos leer las tres líneas del NB05, una a una:

```
cd ~/dev/robotica
source venv/bin/activate
jupyter lab
```

### 1. `cd ~/dev/robotica`

"Entra en la carpeta `robotica`, que está en `dev`, dentro de mi carpeta personal". Después de esta orden, el directorio de trabajo de la terminal es la carpeta del curso.

### 2. `source venv/bin/activate`

Esta es la más interesante. Para entenderla hace falta una idea nueva: el **entorno virtual**.

Python, por sí solo, sabe hacer pocas cosas. Para simular robots, dibujar gráficas o entrenar redes, usa **bibliotecas** (*libraries*): paquetes de código que han escrito otras personas (NumPy, MuJoCo, PyTorch...). Se instalan con una herramienta llamada **pip**.

El problema: cada proyecto necesita **sus** bibliotecas, en **sus** versiones concretas. El curso necesita MuJoCo 3.14; quizá otro proyecto tuyo necesite una versión más vieja. Si todo se instalara en el mismo sitio, se pisarían.

La solución es un **entorno virtual** (*virtual environment*): una **caja de herramientas separada** para cada proyecto, con su propio Python y sus propias bibliotecas. La del curso está en la carpeta `venv` (que viste en el árbol de la sección 4). **Activarla** (`source venv/bin/activate`) significa decirle a la terminal: "a partir de ahora, cuando diga `python` o `pip`, usa los de esta caja". Lo notarás porque el indicador cambia y aparece `(venv)` delante.

(`source` es la orden que ejecuta el archivo `activate`, que está en la carpeta `bin` del entorno virtual. Se repite en cada terminal nueva: la activación solo dura mientras la terminal está abierta.)

### 3. `jupyter lab`

Pone en marcha **Jupyter Lab**, el programa de los cuadernos. Lo curioso es cómo funciona: Jupyter arranca un pequeño **servidor** (un programa que espera peticiones) en tu propio ordenador, y lo "visitas" con el **navegador**, como si fuera una página web, en una dirección como `http://localhost:8888`. **`localhost`** significa "este mismo ordenador": la página no viene de internet, la sirve tu Raspberry Pi para ti. Por eso la terminal tiene que quedarse **abierta** mientras usas los cuadernos: si la cierras (o pulsas Ctrl+C en ella), el servidor se apaga.

Y cuando ejecutas una celda, Jupyter se la pasa al **kernel** (NB05): un proceso de Python (sección 3) que la ejecuta y devuelve el resultado. El kernel "Python (robotica)" es un Python que usa la caja de herramientas del curso.
"""),

md(r"""## 7 · Instalar el curso en tu propio ordenador

Si no usas la Raspberry Pi donde se preparó el curso, puedes instalarlo en cualquier ordenador con Linux, macOS o Windows. Necesitas tener instalados **Python** (versión 3.12 o más nueva; el curso usa la 3.13) y **Git** (un programa para descargar y guardar versiones de código, que verás a fondo en el NB27). Después, en una terminal:

```
git clone https://github.com/Greg2828/robotica.git          # descarga el curso
cd robotica                                                  # entra en su carpeta
python3 -m venv venv                                         # crea la caja de herramientas
source venv/bin/activate                                     # la activa (en Windows: venv\Scripts\activate)
pip install -r requirements/fase0.txt                        # instala las bibliotecas del curso
python -m ipykernel install --user --name robotica --display-name "Python (robotica)"   # registra el kernel
jupyter lab                                                  # abre los cuadernos
```

Línea a línea:

- **`git clone`** copia el curso entero desde internet a una carpeta nueva llamada `robotica`.
- **`python3 -m venv venv`** crea un entorno virtual nuevo en la carpeta `venv` (el `-m` significa "ejecuta el módulo `venv` de Python").
- **`pip install -r requirements/fase0.txt`** instala todas las bibliotecas que aparecen en ese archivo, en las versiones exactas con las que se verificó el curso (`-r` = "lee la lista de este archivo"). Tarda un rato.
- **`ipykernel install`** registra un kernel llamado "Python (robotica)" que usa esta caja de herramientas, para que Jupyter lo ofrezca.

Un aviso sobre MuJoCo: los cuadernos que dibujan robots empiezan con la línea `os.environ["MUJOCO_GL"] = "egl"`, que le dice a MuJoCo cómo dibujar en un ordenador **sin pantalla**, como la Raspberry Pi del curso. En un ordenador normal con pantalla, si esa línea diera error, se puede cambiar `"egl"` por `"glfw"` (en Windows y macOS suele hacer falta).

Y si no quieres instalar nada: los cuadernos ya vienen **ejecutados**, así que se pueden **leer** enteros en la web de GitHub (la "Manera 1" del NB05).
"""),

md(r"""## 8 · Resumen de la lección

1. **Piezas**: CPU (el cocinero; con varios **núcleos**), RAM (la encimera: rápida, se vacía al apagar), disco (la despensa: grande, permanente), GPU (muchos pinches a la vez).
2. **Todo son números**: un **bit** es un 0 o un 1; **binario** = contar con potencias de 2 (101 = 5); un **byte** = 8 bits (0-255); KB, MB, GB. El texto es una tabla de números (A = 65). **0,1 no es exacto en binario**: por eso los decimales a veces salen raros.
3. **Programa** (receta en el disco) → **proceso** (en marcha, con su propia memoria). **Hilos**: trabajadores del mismo proceso que comparten memoria. El **sistema operativo** reparte los núcleos.
4. **Archivos y carpetas** forman un árbol. **Ruta absoluta** (desde `/`) y **relativa** (desde donde estás); `~` = carpeta personal, `..` = la de arriba. **Directorio de trabajo**. **Extensiones**: `.py`, `.ipynb`, `.xml`...
5. **Terminal**: órdenes escritas. `pwd`, `ls`, `cd`, `mkdir`, `cat`; Tab, flecha arriba, Ctrl+C. En Jupyter, con `!`.
6. **Las palabras mágicas**: `cd` entra en la carpeta del curso; `source venv/bin/activate` activa el **entorno virtual** (la caja de herramientas del proyecto, con sus **bibliotecas** instaladas con **pip**); `jupyter lab` arranca un **servidor** local que ves en el navegador (`localhost`).
7. **Instalar** en tu ordenador: `git clone`, `python3 -m venv venv`, activar, `pip install -r requirements/fase0.txt`, registrar el kernel, `jupyter lab`.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **CPU / núcleo** | El procesador / cada una de sus unidades independientes de cálculo. |
| **RAM** | Memoria de trabajo: rápida, se vacía al apagar. |
| **Disco** | Almacenamiento permanente. |
| **GPU** | Tarjeta gráfica: miles de cálculos sencillos a la vez. |
| **Bit / byte** | Un 0 o un 1 / un grupo de 8 bits. |
| **Binario** | Sistema de numeración con solo dos cifras, 0 y 1. |
| **Unicode** | La tabla mundial que asigna un número a cada carácter. |
| **Proceso / hilo** | Programa en marcha con su memoria / trabajador dentro de un proceso. |
| **Sistema operativo** | El programa que gestiona el ordenador (Linux, Windows, macOS). |
| **Archivo, carpeta, ruta** | Un dato guardado, un contenedor de archivos, el camino hasta ellos. |
| **Directorio de trabajo** | La carpeta desde la que se buscan las rutas relativas. |
| **Terminal** | Ventana para dar órdenes escritas al ordenador. |
| **Biblioteca** | Paquete de código hecho por otros, listo para usar. |
| **pip** | La herramienta que instala bibliotecas de Python. |
| **Entorno virtual** | Caja de herramientas separada para cada proyecto. |
| **Servidor / localhost** | Programa que atiende peticiones / "este mismo ordenador". |
"""),

md(r"""## 9 · Preguntas de comprensión

**P1.** Has estado trabajando dos horas en un cuaderno y se va la luz. ¿Qué se ha perdido y qué no? ¿Por qué?

**P2.** ¿Qué número es `1100` en binario? ¿Y cómo se escribe el 7 en binario?

**P3.** ¿Cuántos valores distintos se pueden guardar con 16 bits?

**P4.** Estás en la carpeta `/home/gregori/dev/robotica/notebooks`. Escribe la ruta relativa y la absoluta del archivo `PROGRESO.md`, que está en la carpeta `robotica`.

**P5.** Un compañero escribe `cd robots` y la terminal le contesta `No such file or directory`. ¿Qué crees que ha pasado?

**P6.** ¿Para qué sirve un entorno virtual? ¿Qué pasaría si todos tus proyectos compartieran las mismas bibliotecas?

**P7.** Si tienes Jupyter abierto en el navegador y cierras la ventana de la terminal desde la que lo lanzaste, ¿qué pasa? ¿Por qué?

**P8.** Tu ordenador tiene 4 núcleos. ¿Cuántos robots, como mucho, podría simular **a la vez de verdad**? ¿Y si lanzas 8 simulaciones?
"""),

md(r"""<details>
<summary>▶ Solución P1</summary>

Se pierde todo lo que estaba en la **RAM**: las variables que había calculado el kernel, los resultados que no se hayan guardado. **No** se pierde lo guardado en el **disco**: el propio cuaderno, si lo habías guardado (Jupyter guarda automáticamente cada poco), y cualquier archivo que hubieras escrito. La RAM se vacía al apagar; el disco no. Al volver, tendrás que **volver a ejecutar** las celdas para recalcular las variables.
</details>

<details>
<summary>▶ Solución P2</summary>

`1100` = 8 + 4 + 0 + 0 = **12**. El 7 = 4 + 2 + 1 = **`111`**.
</details>

<details>
<summary>▶ Solución P3</summary>

2¹⁶ = **65.536** valores (cada bit dobla las posibilidades: 2 × 2 × ... dieciséis veces).
</details>

<details>
<summary>▶ Solución P4</summary>

Relativa: **`../PROGRESO.md`** (sube una carpeta con `..` y ahí está). Absoluta: **`/home/gregori/dev/robotica/PROGRESO.md`**.
</details>

<details>
<summary>▶ Solución P5</summary>

Que **no hay** una carpeta llamada `robots` en el sitio donde está. `cd robots` es una ruta **relativa**: busca `robots` dentro del directorio de trabajo actual. Probablemente estaba en otra carpeta (por ejemplo, en `robotica` en vez de en `notebooks`). Con `pwd` vería dónde está, y con `ls` qué hay.
</details>

<details>
<summary>▶ Solución P6</summary>

Para que cada proyecto tenga **sus** bibliotecas, en **sus** versiones, sin interferir con los demás. Si todos compartieran las mismas, actualizar una biblioteca para un proyecto podría **romper** otro que necesitaba la versión antigua. Además, un entorno virtual se puede **reconstruir** en otro ordenador con la lista de `requirements`, y así el proyecto funciona igual en todas partes.
</details>

<details>
<summary>▶ Solución P7</summary>

El servidor de Jupyter **se apaga** (era un proceso lanzado desde esa terminal), y el navegador se queda "sin conexión": no podrás ejecutar celdas ni guardar. La página que ves en el navegador no es más que una ventana hacia el servidor que corría en tu ordenador.
</details>

<details>
<summary>▶ Solución P8</summary>

Como mucho **4** a la vez de verdad: una por núcleo. Si lanzas 8, el sistema operativo las **reparte**: cada núcleo va saltando entre dos simulaciones, así que avanzan todas, pero cada una a la mitad de velocidad. En total no ganas nada frente a lanzar 4 (incluso pierdes un poco, por los saltos). Lo medirás de verdad en el NB49.
</details>
"""),

md(r"""## 10 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

En el **NB06** volvemos a Python: las **variables**, cajas con nombre donde guardar números (¡en la RAM, ahora ya sabes dónde!), y los dos tipos de números del ordenador. Y verás con tus propios ojos el 0,1 que no es exacto.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB05b_ordenador_por_dentro_y_terminal.ipynb")
    build(out, cells, title="NB05b · Tu ordenador por dentro y la terminal")
