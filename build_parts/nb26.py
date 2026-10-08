"""Construye NB26 · Python de verdad (7): ficheros, módulos, scripts y la terminal.

Memoria vs disco. pathlib (Path, /, mkdir, exists, name/stem/suffix/parent,
cwd, iterdir, glob). open + with (modos w/a/r, encoding), write/read, recorrer
líneas, FileNotFoundError real, write_text/read_text. CSV (csv.DictWriter /
DictReader: todo vuelve como texto). JSON (configuración; dataclasses.asdict).
np.save / np.load / np.savez (pesos de una política). pickle (y por qué NUNCA
cargar uno de origen dudoso). Módulos propios (escribir palo.py, sys.path,
import, importlib.reload). Scripts: if __name__ == "__main__", argparse,
ejecutar con subprocess + sys.executable. La terminal (! en Jupyter, tabla de
órdenes). Entornos virtuales y pip (requirements.txt; las "palabras mágicas"
del NB05 explicadas). logging. Biblioteca estándar: collections (Counter,
defaultdict), datetime, itertools.product, statistics. Proyecto: barrido de
ruedecillas (rejilla) guardado en una carpeta con fecha: config JSON +
resultados CSV + mejores pesos .npy, y vuelta a leerlo todo.
Todo se hace dentro de notebooks/practica_nb26/ (en .gitignore).
Práctica en MuJoCo (§18), en notebooks/practica_mujoco/nb26_* (generado al ejecutar,
también ignorado por git): MJCF del palo largo a fichero + from_xml_path,
mj_saveLastXML (lo que MuJoCo entendió), config JSON + trayectoria np.savez (qpos.copy),
script nb26_video.py con argparse + MUJOCO_GL=egl lanzado con ! y subprocess que graba un MP4.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB26 · Python de verdad (7): ficheros, módulos, scripts y la terminal

**Parte 3 · Python de verdad — Lección 7**

> Hasta ahora, todo lo que has programado **vive y muere dentro del cuaderno**. Cuando cierras Jupyter (o reinicias el kernel),
> todas tus variables desaparecen: los retornos que mediste, las ruedecillas que aprendió el palo de escoba... **todo**.

En un proyecto de verdad eso es inaceptable. Un entrenamiento de horas tiene que **guardar** la política que aprende, los resultados,
la configuración que se usó. Y el código no vive en celdas sueltas, sino en **ficheros** organizados, que se **importan** unos a otros y
se lanzan desde la **terminal**.

Hoy salimos del cuaderno. Veremos:

1. **Ficheros**: guardar y leer texto, tablas (CSV), configuraciones (JSON) y arrays de NumPy.
2. **Módulos**: tu propio código en ficheros `.py` que se importan.
3. **Scripts** que se lanzan desde la **terminal**, con opciones.
4. Los **entornos virtuales** y **`pip`**: por fin entenderás las "palabras mágicas" del NB05.
5. Una visita a la **biblioteca estándar**: herramientas que Python trae de serie.

Todo lo que hagamos hoy irá a una carpeta de prácticas, `practica_nb26`, al lado de este cuaderno, para no desordenar nada.
"""),

md(r"""## 1 · Memoria y disco

El ordenador guarda las cosas en dos sitios muy distintos:

- La **memoria** (RAM): rapidísima, pero **volátil**: se borra al apagar o al cerrar el programa. Ahí viven tus variables.
- El **disco** (o la tarjeta SD de la Raspberry Pi): mucho más lento, pero **permanente**. Ahí viven los **ficheros** (o **archivos**).

Guardar en un fichero es pasar algo de la memoria al disco para que sobreviva; leerlo es traerlo de vuelta. Los ficheros se organizan en
**carpetas** (o **directorios**), unas dentro de otras, como un árbol. La "dirección" de un fichero dentro de ese árbol es su **ruta**, por
ejemplo `notebooks/practica_nb26/registro.txt`.
"""),

md(r"""## 2 · Rutas con `pathlib`

Python trae un módulo para trabajar con rutas cómodamente, **`pathlib`**. Su pieza central es la clase **`Path`** ("ruta"). Creemos la ruta de
nuestra carpeta de prácticas y **fabriquemos la carpeta** en el disco:
"""),

code(r"""from pathlib import Path

carpeta = Path("practica_nb26")
carpeta.mkdir(exist_ok=True)          # crea la carpeta (y no se queja si ya existía)
print(carpeta, "| ¿existe?", carpeta.exists())
print("Estamos en:", Path.cwd().name)"""),

md(r"""`mkdir` (de *make directory*, "crear directorio") ha creado la carpeta. `exist_ok=True` evita un error si ya estaba creada (por ejemplo, la segunda vez que
ejecutes el cuaderno). `Path.cwd()` es el **directorio de trabajo actual** (*current working directory*): la carpeta "en la que está" el programa, desde la que
se buscan las rutas relativas. Al ejecutar un cuaderno, es la carpeta del propio cuaderno, `notebooks`.

Lo más elegante de `Path`: las rutas se **unen** con la barra **`/`**, como se escriben:
"""),

code(r"""ruta = carpeta / "politicas" / "politica_paso_01500.npy"
print(ruta)
print("nombre:   ", ruta.name)
print("sin final:", ruta.stem)
print("extensión:", ruta.suffix)
print("carpeta:  ", ruta.parent)"""),

md(r"""¿Una barra que une rutas? ¡Es un **método especial** (NB25)! La clase `Path` define `__truediv__`, el método del símbolo `/`, para que signifique "unir rutas".
Y `name`, `stem`, `suffix` y `parent` son **propiedades** (NB24) que separan las partes de la ruta, mucho más seguro que hacerlo a mano con `split` (NB20). Además,
`Path` se encarga de usar la barra correcta en cada sistema operativo (Windows usa `\` en vez de `/`).
"""),

md(r"""## 3 · Escribir un fichero de texto: `open` y `with`

Para escribir en un fichero, se **abre** con `open(ruta, modo)` y se **escribe** en él. La forma correcta de hacerlo es con **`with`**:
"""),

code(r"""ruta_registro = carpeta / "registro.txt"

with open(ruta_registro, "w", encoding="utf-8") as fichero:
    fichero.write("episodio=1 retorno=44.8 pasos=50\n")
    fichero.write("episodio=2 retorno=97.2 pasos=104\n")

print("Escrito:", ruta_registro, "| ¿existe?", ruta_registro.exists())"""),

md(r"""Pieza a pieza:

- **`open(ruta, "w", encoding="utf-8")`** abre el fichero. El **modo** `"w"` (de *write*) significa **escribir**: crea el fichero, y si ya existía, **lo borra y empieza
  de cero**. `encoding="utf-8"` dice cómo guardar las letras (con UTF-8, las tildes y la ñ se guardan bien; ponlo siempre).
- **`with ... as fichero:`** guarda el fichero abierto en la caja `fichero`, y lo **cierra automáticamente** al salir del bloque, **pase lo que pase**, incluso si hay un
  error (como el `finally` del NB22). Un fichero sin cerrar puede quedarse a medio escribir. A esto se le llama un **gestor de contexto**, y `with` es la forma de usarlo.
- **`fichero.write(texto)`** escribe el texto. **No añade salto de línea** solo: hay que ponerlo con `\n` (NB20).

Los modos más usados:

| Modo | Significa | Si el fichero existe... | Si no existe... |
|---|---|---|---|
| `"r"` | leer (*read*) — el modo por defecto | lo lee | `FileNotFoundError` |
| `"w"` | escribir (*write*) | **lo borra** y escribe desde cero | lo crea |
| `"a"` | añadir al final (*append*) | escribe **detrás** de lo que había | lo crea |

¡Cuidado con `"w"`! Abrir un fichero importante en modo `"w"` por error lo vacía al instante. Para ir añadiendo líneas a un registro mientras se entrena, el modo es `"a"`:
"""),

code(r"""with open(ruta_registro, "a", encoding="utf-8") as fichero:
    fichero.write("episodio=3 retorno=213.5 pasos=231\n")"""),

md(r"""## 4 · Leer un fichero de texto

Con el modo `"r"` (o sin poner modo, porque es el de por defecto). Se puede leer **todo de golpe** con `read`:"""),

code(r"""with open(ruta_registro, encoding="utf-8") as fichero:
    contenido = fichero.read()
print(contenido)"""),

md(r"""Las tres líneas, incluida la que añadimos con `"a"`. Pero lo más habitual (y lo mejor para ficheros grandes) es recorrerlo **línea a línea** con un `for`: un fichero
abierto es un **iterable** (NB23), que va entregando las líneas de una en una, sin cargar el fichero entero en memoria:
"""),

code(r"""with open(ruta_registro, encoding="utf-8") as fichero:
    for numero, linea in enumerate(fichero, start=1):
        print(numero, repr(linea))"""),

md(r"""(`repr` muestra la cadena tal cual, con sus comillas.) ¿Ves el `\n` al final de cada línea? Las líneas leídas **conservan su salto de línea**. Por eso, al leer un fichero,
casi siempre se hace **`linea.strip()`** (NB20) antes de usar la línea.

¿Y si el fichero no existe?
"""),

code_err(r"""with open(carpeta / "no_existo.txt", encoding="utf-8") as fichero:
    print(fichero.read())"""),

md(r"""`FileNotFoundError: [Errno 2] No such file or directory`: "no existe ese fichero o directorio" (estaba en la tabla del NB22). Las causas típicas: una errata en el nombre, o
que el **directorio de trabajo** no es el que crees (la ruta relativa se busca desde `Path.cwd()`).

Para textos cortos, `Path` tiene dos atajos que abren, escriben o leen y cierran en una línea:
"""),

code(r"""nota = carpeta / "nota.txt"
nota.write_text("Probar tasa 0.001 mañana\n", encoding="utf-8")
print(nota.read_text(encoding="utf-8"))"""),

md(r"""## 5 · Tablas: ficheros CSV

Un **CSV** (de *comma-separated values*, "valores separados por comas") es la forma más común de guardar **tablas**: cada línea es una fila, y los valores van separados por
comas. Lo abre cualquier programa, incluidas las hojas de cálculo. Python trae el módulo **`csv`** para leerlos y escribirlos sin errores (por ejemplo, si un texto contiene una coma).

Lo más cómodo es trabajar con **diccionarios** (NB21): `DictWriter` escribe una fila por diccionario, y `DictReader` lee cada fila **como** un diccionario:
"""),

code(r"""import csv

episodios = [
    {"episodio": 1, "retorno": 44.8, "pasos": 50},
    {"episodio": 2, "retorno": 97.2, "pasos": 104},
    {"episodio": 3, "retorno": 499.9, "pasos": 500},
]

ruta_csv = carpeta / "episodios.csv"
with open(ruta_csv, "w", encoding="utf-8", newline="") as fichero:
    escritor = csv.DictWriter(fichero, fieldnames=["episodio", "retorno", "pasos"])
    escritor.writeheader()            # la primera fila: los nombres de las columnas
    escritor.writerows(episodios)

print(ruta_csv.read_text(encoding="utf-8"))"""),

md(r"""Una tabla en texto plano, con una fila de **cabecera** con los nombres de las columnas. (`newline=""` es un detalle que pide el módulo `csv` al escribir, para no duplicar los
saltos de línea en algunos sistemas.) Y para leerla:
"""),

code(r"""with open(ruta_csv, encoding="utf-8") as fichero:
    filas = list(csv.DictReader(fichero))

print(filas[0])
print(type(filas[0]["retorno"]))"""),

md(r"""Cada fila vuelve como un diccionario... ¡pero fíjate en el tipo!: **`str`**. En un CSV **todo es texto**; el `44.8` que guardamos como número vuelve como la cadena `"44.8"`. Hay que
**convertirlo** (NB20):
"""),

code(r"""retornos = [float(fila["retorno"]) for fila in filas]
print(retornos, "| media:", sum(retornos) / len(retornos))"""),

md(r"""## 6 · Configuraciones: ficheros JSON

Para guardar **estructuras** (diccionarios dentro de diccionarios, listas...), como la configuración de un entrenamiento (NB21), el formato más usado es **JSON** (se pronuncia "yeison",
de *JavaScript Object Notation*). Es texto, se parece muchísimo a los diccionarios y listas de Python, y **conserva los tipos** (números como números, `true`/`false`, listas...). El módulo
**`json`**: `dump` guarda, `load` carga.
"""),

code(r"""import json

configuracion = {
    "entorno": "PaloDeEscoba-v0",
    "semillas": [0, 1, 2, 3, 4],
    "politica": {"tipo": "lineal", "k": 30, "d": 8},
    "con_viento": True,
}

ruta_json = carpeta / "configuracion.json"
with open(ruta_json, "w", encoding="utf-8") as fichero:
    json.dump(configuracion, fichero, indent=2, ensure_ascii=False)

print(ruta_json.read_text(encoding="utf-8"))"""),

md(r"""(`indent=2` lo escribe con sangría, para que se lea bien; `ensure_ascii=False` guarda las tildes tal cual.) Fíjate en que `True` se escribe `true`: es el JSON "de verdad". Para cargarlo:"""),

code(r"""with open(ruta_json, encoding="utf-8") as fichero:
    cargada = json.load(fichero)

print(cargada["politica"]["k"], type(cargada["politica"]["k"]))
print(cargada == configuracion)"""),

md(r"""El 30 vuelve como **entero** (no como texto, al contrario que en CSV), y la configuración cargada es **idéntica** a la original.

Si tu configuración es una `@dataclass` (NB24), `dataclasses.asdict(objeto)` la convierte en diccionario para guardarla con `json`.

**JSON solo entiende** diccionarios, listas, textos, números, `True`/`False` y `None`. Un array de NumPy, por ejemplo, no se puede guardar directamente en JSON (habría que convertirlo con
`.tolist()`). Para arrays, hay algo mejor.
"""),

md(r"""## 7 · Arrays de NumPy: `np.save` y `np.load`

Los pesos de una política (NB14-15) son arrays de NumPy. NumPy trae su propio formato, **`.npy`**, que guarda un array **exactamente** como está (forma, tipo y todos los números, sin
perder ni un decimal), y es muy rápido:
"""),

code(r"""import numpy as np

generador = np.random.default_rng(0)
pesos = generador.uniform(-0.1, 0.1, size=(17, 348))      # una política lineal del humanoide (NB15)

ruta_pesos = carpeta / "pesos.npy"
np.save(ruta_pesos, pesos)

recuperados = np.load(ruta_pesos)
print("Forma:", recuperados.shape, "| ¿idénticos?", np.array_equal(pesos, recuperados))"""),

md(r"""¡Idénticos! (`np.array_equal` compara dos arrays enteros.) Así se guarda una política entrenada para usarla otro día, o en otro ordenador, o **en el robot de verdad**. Para guardar
**varios** arrays en un solo fichero existe `np.savez(ruta, pesos=W, sesgos=b)`, que se carga con `np.load` y se lee por nombre: `datos["pesos"]`.
"""),

md(r"""## 8 · Guardar cualquier objeto: `pickle` (y su gran peligro)

¿Y si quieres guardar un objeto **cualquiera**, por ejemplo una `PoliticaLineal` del NB24? Python trae el módulo **`pickle`** ("encurtir": conservar algo en vinagre), que convierte casi
cualquier objeto en bytes y lo guarda:
"""),

code(r"""import pickle

class PoliticaLineal:
    def __init__(self, k, d):
        self.k, self.d = k, d
    def __repr__(self):
        return f"PoliticaLineal(k={self.k}, d={self.d})"

ruta_pickle = carpeta / "politica.pkl"
with open(ruta_pickle, "wb") as fichero:              # "wb": escribir en BINARIO (bytes, no texto)
    pickle.dump(PoliticaLineal(30, 8), fichero)

with open(ruta_pickle, "rb") as fichero:              # "rb": leer en binario
    print(pickle.load(fichero))"""),

md(r"""Cómodo... pero con un **peligro enorme** que debes conocer:

> **Nunca cargues con `pickle` un fichero de alguien en quien no confíes plenamente.** Un fichero pickle puede contener **instrucciones** que se ejecutan al cargarlo. Alguien malicioso
> puede fabricar un `.pkl` que, al hacer `pickle.load`, borre tus archivos o robe tus datos. **Cargar un pickle es como ejecutar un programa.**

Este peligro es muy real en el mundo de la inteligencia artificial, donde se comparten modelos entrenados por internet: muchos formatos antiguos de modelos usan pickle por dentro. Por eso hoy
se usan formatos que **solo** contienen números (como `.npy` o el formato *safetensors*), que no pueden ejecutar nada. Regla práctica: **para tus propios datos, en tu ordenador, pickle está
bien; para cualquier cosa descargada, desconfía.**
"""),

md(r"""## 9 · Listar ficheros

Para ver qué hay en una carpeta, `iterdir` recorre todo lo que contiene, y `glob` busca por un **patrón** (el asterisco `*` significa "cualquier cosa"):"""),

code(r"""print("Todo lo que hay:")
for ruta in sorted(carpeta.iterdir()):
    print("  ", ruta.name)

print("Solo los .json y los .csv:", sorted(r.name for r in carpeta.glob("*.json")) + sorted(r.name for r in carpeta.glob("*.csv")))"""),

md(r"""`carpeta.glob("*.npy")` daría todos los ficheros de pesos; `carpeta.glob("politica_paso_*.npy")`, solo los de políticas. Es la forma de encontrar, por ejemplo, el último punto de guardado de
un entrenamiento. (Ordenarlos bien es la razón de los ceros delante de los números, NB20.)
"""),

md(r"""## 10 · Tus propios módulos

Hasta ahora todo el código está en celdas. Pero imagina que quieres usar la clase del palo de escoba en **varios** cuadernos y programas. ¿Copiarla en cada uno? No: se guarda **una vez** en un
**fichero `.py`** (un **módulo**, NB11) y se **importa** desde donde haga falta, igual que `import random` o `import numpy`.

Vamos a escribir un módulo `palo.py` con el entorno y una función para evaluar políticas. Lo escribimos desde aquí con `write_text` (normalmente lo escribirías en un editor de código):
"""),

code(r"""codigo_del_modulo = '''# palo.py: el palo de escoba como módulo reutilizable.
import random


class PaloDeEscoba:
    def __init__(self, viento_maximo=30):
        self.viento_maximo = viento_maximo
        self._azar = random.Random(0)
        self.inclinacion = 0.0
        self.velocidad = 0.0
        self.pasos = 0

    def reset(self, seed=None):
        if seed is not None:
            self._azar = random.Random(seed)
        self.inclinacion, self.velocidad, self.pasos = 2.0, 0.0, 0
        return (self.inclinacion, self.velocidad), {}

    def step(self, empuje):
        empuje = max(-40, min(40, empuje))
        viento = self._azar.uniform(-self.viento_maximo, self.viento_maximo)
        aceleracion = 10 * self.inclinacion + empuje + viento
        self.velocidad += aceleracion * 0.02
        self.inclinacion += self.velocidad * 0.02
        self.pasos += 1
        terminado = abs(self.inclinacion) > 30
        truncado = self.pasos >= 500
        recompensa = 0.0 if terminado else 1 - (self.inclinacion / 30) ** 2
        return (self.inclinacion, self.velocidad), recompensa, terminado, truncado, {}


def evaluar(k, d, semillas=range(5), viento_maximo=30):
    entorno = PaloDeEscoba(viento_maximo)
    retornos = []
    for semilla in semillas:
        (inclinacion, velocidad), info = entorno.reset(seed=semilla)
        retorno = 0.0
        while True:
            empuje = -k * inclinacion - d * velocidad
            (inclinacion, velocidad), r, terminado, truncado, info = entorno.step(empuje)
            retorno += r
            if terminado or truncado:
                break
        retornos.append(retorno)
    return sum(retornos) / len(retornos)
'''

(carpeta / "palo.py").write_text(codigo_del_modulo, encoding="utf-8")
print("Módulo escrito")"""),

md(r"""(Fíjate en `self.velocidad += ...`: **`+=`** es la forma abreviada de `self.velocidad = self.velocidad + ...`. Existen igual `-=`, `*=` y `/=`. Las verás muchísimo.)

Ahora, para **importarlo**, Python tiene que saber **dónde buscarlo**. Busca en una lista de carpetas que se llama **`sys.path`**; como nuestro módulo está en `practica_nb26`, la añadimos a esa
lista. (Si el módulo estuviera en la misma carpeta que el programa, no haría falta.)
"""),

code(r"""import sys
sys.path.insert(0, str(carpeta))

import palo

print(round(palo.evaluar(30, 8), 1))
print(palo.PaloDeEscoba)"""),

md(r"""¡Importado! `palo.evaluar(30, 8)` da **499,9**, y la clase está disponible como `palo.PaloDeEscoba`. Cualquier cuaderno o programa que pueda importar `palo` tiene ya el entorno, **sin copiar
ni una línea**. Y si mañana corriges un fallo en `palo.py`, se corrige en todos a la vez.

Una trampa de Jupyter: **un módulo solo se importa una vez por sesión**. Si cambias `palo.py` y vuelves a hacer `import palo`, Python **no** lee los cambios (usa la versión que ya tenía en memoria).
Para recargarlo: `import importlib` y `importlib.reload(palo)`. (O reiniciar el kernel.)

Las formas de importar:

| Forma | Se usa como |
|---|---|
| `import palo` | `palo.evaluar(...)` |
| `import numpy as np` | `np.array(...)` (con apodo) |
| `from palo import evaluar` | `evaluar(...)` (sin el `palo.` delante) |
| `from palo import evaluar, PaloDeEscoba` | varias cosas a la vez |

Y cuando un proyecto crece, los módulos se agrupan en **paquetes**: carpetas con varios `.py` (y normalmente un fichero `__init__.py`), que se importan con puntos: `from robotica.entornos import palo`.
Así están organizadas todas las bibliotecas que usas (por ejemplo, `gymnasium.utils.env_checker`, NB25).
"""),

md(r"""## 11 · Scripts: programas que se lanzan desde la terminal

Un **script** es un fichero `.py` pensado para **ejecutarse** de principio a fin, como un programa, en vez de importarse. Los entrenamientos de verdad se lanzan así, desde la terminal (no desde un cuaderno):
pueden durar horas, y una terminal (o un servidor remoto) los aguanta mejor.

Dos piezas clave de cualquier script:

**`if __name__ == "__main__":`**. Cada módulo tiene una variable especial, `__name__`. Si el fichero se **ejecuta directamente**, vale `"__main__"`; si se **importa**, vale el nombre del módulo. Así, el código
dentro de ese `if` se ejecuta **solo** al lanzar el script, y no al importarlo. (¡Es la última línea de todos los scripts que construyen estos cuadernos!)

**`argparse`**: el módulo para que el script acepte **opciones** desde la terminal, como `--k 30 --d 8`, en vez de tener los números fijos en el código.
"""),

code(r"""codigo_del_script = '''# evaluar_politica.py: evalúa una política lineal del palo de escoba.
import argparse
from palo import evaluar


def main():
    parser = argparse.ArgumentParser(description="Evalúa una política lineal en el palo de escoba.")
    parser.add_argument("--k", type=float, default=30, help="ruedecilla de inclinación")
    parser.add_argument("--d", type=float, default=8, help="ruedecilla de velocidad")
    parser.add_argument("--viento", type=float, default=30, help="viento máximo")
    args = parser.parse_args()

    retorno = evaluar(args.k, args.d, viento_maximo=args.viento)
    print(f"k={args.k}, d={args.d}, viento={args.viento} -> retorno medio {retorno:.1f}")


if __name__ == "__main__":
    main()
'''
(carpeta / "evaluar_politica.py").write_text(codigo_del_script, encoding="utf-8")
print("Script escrito")"""),

md(r"""Para lanzarlo, en una **terminal** escribirías (estando en la carpeta del script):

```
python evaluar_politica.py --k 30 --d 0
```

Desde un cuaderno se puede lanzar un programa externo con el módulo **`subprocess`** ("subproceso"). Usamos `sys.executable`, que es **la ruta del Python que está ejecutando este cuaderno** (el del
entorno virtual del proyecto), para asegurarnos de que el script use el mismo Python, con NumPy y todo lo demás instalado:
"""),

code(r"""import subprocess

def lanzar(*opciones):
    resultado = subprocess.run([sys.executable, "evaluar_politica.py", *opciones],
                               cwd=carpeta, capture_output=True, text=True)
    print(resultado.stdout.strip() or resultado.stderr.strip())

lanzar("--k", "30", "--d", "0")
lanzar("--k", "30", "--d", "8", "--viento", "60")
lanzar("--help")"""),

md(r"""Las dos primeras llamadas lanzan el script con distintas opciones (296,0 y 499,9, los números de siempre). Y la tercera, **`--help`**, muestra una **ayuda** que `argparse` ha escrito **solo**, a
partir de las descripciones que pusimos: todo script profesional responde a `--help`.

(`cwd=carpeta` lanza el script **desde** la carpeta de prácticas, para que encuentre `palo.py` a su lado; `capture_output=True` y `text=True` recogen lo que escribe el script, como texto, para mostrarlo.)
"""),

md(r"""## 12 · La terminal

La **terminal** (o **consola**, o **línea de órdenes**) es esa ventana donde se escriben órdenes de texto en vez de hacer clic. Asusta un poco al principio, pero es **la herramienta** de cualquier
ingeniero: para lanzar entrenamientos, manejar ficheros, conectarse a otros ordenadores (como los de las empresas, que no tienen pantalla) o instalar programas.

En Jupyter, se puede ejecutar una orden de terminal poniendo un **`!`** delante:
"""),

code(r"""!ls practica_nb26"""),

md(r"""`ls` (de *list*) lista lo que hay en una carpeta. Estas son las órdenes que más usarás (en Linux y Mac, que es lo que tiene la Raspberry Pi):

| Orden | Qué hace | Ejemplo |
|---|---|---|
| `pwd` | Dice en qué carpeta estás | `pwd` |
| `ls` | Lista lo que hay en una carpeta | `ls notebooks` |
| `cd` | Cambia de carpeta | `cd ~/dev/robotica` (`~` = tu carpeta personal; `cd ..` = subir un nivel) |
| `mkdir` | Crea una carpeta | `mkdir resultados` |
| `cp` / `mv` | Copia / mueve (o renombra) | `mv viejo.txt nuevo.txt` |
| `rm` | **Borra** (¡sin papelera, para siempre!) | `rm nota.txt` |
| `cat` / `head` | Muestra un fichero / sus primeras líneas | `head registro.txt` |
| `python script.py` | Ejecuta un script | `python evaluar_politica.py --k 30` |

Tres trucos que te ahorrarán horas: la tecla **Tabulador** completa nombres de ficheros y carpetas; la **flecha arriba** recupera las órdenes anteriores; y **Ctrl + C** para un programa que no
termina (NB22).

Y una advertencia: **`rm` no tiene papelera**. Lo que borras, se pierde. Antes de borrar, mira bien qué es.
"""),

md(r"""## 13 · Entornos virtuales y `pip`: las palabras mágicas, por fin

¿Recuerdas las tres "palabras mágicas" del NB05 para abrir el cuaderno?

```
cd ~/dev/robotica
source venv/bin/activate
jupyter lab
```

Ya entiendes la primera (`cd`: ir a la carpeta del proyecto). La segunda es la interesante. Cada proyecto necesita **sus** bibliotecas, en **sus** versiones: este curso usa NumPy 2.5 y Gymnasium 1.3;
otro proyecto tuyo podría necesitar versiones distintas. Si todo se instalara en el mismo sitio, los proyectos se pisarían unos a otros.

La solución es el **entorno virtual**: una carpeta (aquí, `venv`) con **su propio Python y sus propias bibliotecas**, separadas de todo lo demás. Se crea una vez con `python -m venv venv`, y
**`source venv/bin/activate`** lo **activa**: a partir de ahí, en esa terminal, `python` y todo lo que instales usan el del proyecto. (Por eso `sys.executable`, en el apartado 11, apuntaba dentro de
`venv`.)

Las bibliotecas se instalan con **`pip`**, el instalador de paquetes de Python, que las descarga de un almacén público en internet (PyPI):

| Orden | Qué hace |
|---|---|
| `pip install numpy` | Instala una biblioteca (y lo que ella necesite) |
| `pip install numpy==2.5.3` | Instala una versión concreta |
| `pip list` | Lista lo instalado |
| `pip freeze > requirements.txt` | Apunta en un fichero **todas** las versiones instaladas |
| `pip install -r requirements.txt` | Instala exactamente lo apuntado en ese fichero |

El fichero **`requirements.txt`** es clave para trabajar en equipo: cualquier persona puede **reproducir** tu entorno exacto con una orden. Este proyecto tiene uno en `requirements/`. Por ejemplo,
para preguntarle a `pip` por NumPy, desde el cuaderno:
"""),

code(r"""salida = subprocess.run([sys.executable, "-m", "pip", "show", "numpy"], capture_output=True, text=True).stdout
print("\n".join(salida.splitlines()[:3]))"""),

md(r"""(`python -m pip` ejecuta `pip` como un módulo del Python que le digas: así te aseguras de que instala en el entorno correcto. Y `splitlines()` parte un texto por sus saltos de línea.)

Y la tercera palabra mágica, `jupyter lab`, simplemente lanza el programa Jupyter, que está instalado dentro del entorno virtual.

**Una costumbre profesional:** nunca subas la carpeta `venv` a GitHub (pesa muchísimo y solo sirve para tu ordenador); sube el `requirements.txt`. Mira el fichero `.gitignore` de este proyecto: la
primera línea que ignora es, justamente, `venv/`. Lo veremos en el NB27.
"""),

md(r"""## 14 · Registrar lo que pasa: `logging`

`print` está bien para cuadernos, pero los programas largos usan el módulo **`logging`** ("registro"): escribe mensajes con **hora** y **nivel de importancia**, a la pantalla o a un fichero, y
permite **subir o bajar** cuánto detalle se muestra sin tocar el código:
"""),

code(r"""import logging

registrador = logging.getLogger("entrenamiento")
registrador.setLevel(logging.INFO)
manejador = logging.FileHandler(carpeta / "entrenamiento.log", mode="w", encoding="utf-8")
manejador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
registrador.addHandler(manejador)

registrador.info("Empieza el entrenamiento")
registrador.debug("Este mensaje de detalle NO se guarda (el nivel es INFO)")
registrador.warning("La pérdida ha subido tres pasos seguidos")
manejador.close()

print((carpeta / "entrenamiento.log").read_text(encoding="utf-8"))"""),

md(r"""Cada mensaje lleva la fecha y la hora y su nivel. Los niveles, de menos a más grave: `DEBUG` (detalles para depurar), `INFO` (lo normal), `WARNING` (algo raro), `ERROR` y `CRITICAL`. Con el nivel en
`INFO`, los `DEBUG` no aparecen; para depurar, bajas el nivel a `DEBUG` y salen todos. Así es como los entrenamientos de verdad dejan su "diario".
"""),

md(r"""## 15 · La biblioteca estándar: lo que Python trae de serie

Python viene con **cientos** de módulos incluidos (la **biblioteca estándar**). Ya has usado `math`, `random`, `time`, `pathlib`, `csv`, `json`, `pickle`... Unos cuantos más que te encontrarás a menudo:"""),

code(r"""from collections import Counter, defaultdict

finales = ["caída", "tiempo", "caída", "caída", "tiempo", "caída"]
print(Counter(finales))                               # contar, en una línea (NB21)
print(Counter(finales).most_common(1))                # el más frecuente

por_tipo = defaultdict(list)                          # un diccionario que crea solo la lista si no existe
for tipo, retorno in [("lineal", 499.9), ("azar", 43.2), ("lineal", 296.0)]:
    por_tipo[tipo].append(retorno)
print(dict(por_tipo))"""),

md(r"""`Counter` es el contador del NB21 hecho; `defaultdict(list)` es un diccionario que, si pides una clave que no existe, la crea con una lista vacía (adiós al `KeyError` y a los `get`).
"""),

code(r"""from datetime import datetime
import itertools
import statistics

ahora = datetime.now()
print("Marca de tiempo para un nombre de carpeta:", ahora.strftime("%Y%m%d_%H%M%S")[:8] + "_...")

for k, d in itertools.product([10, 30], [0, 8]):      # todas las combinaciones
    print("  probar", k, d)

datos = [499.9, 296.0, 44.8]
print("media:", round(statistics.mean(datos), 1), "| desviación típica:", round(statistics.stdev(datos), 1))"""),

md(r"""- **`datetime`**: fechas y horas. `strftime` las convierte en texto con el formato que digas (`%Y` año, `%m` mes, `%d` día, `%H%M%S` hora): perfecto para nombrar carpetas de experimentos, que así se
  ordenan solas por fecha. (Mostramos solo la parte de la fecha, porque la hora cambia cada vez.)
- **`itertools.product`**: **todas las combinaciones** de varias listas. Es exactamente lo que hace falta para probar una **rejilla** de ruedecillas (la búsqueda del NB16, en dos dimensiones).
- **`statistics`**: media, mediana y **desviación típica** (cuánto se dispersan los datos alrededor de la media; la veremos con calma en la siguiente parte, con la probabilidad).

Antes de programar algo "básico", pregúntate: **¿no lo traerá ya Python?** Muy a menudo, sí.
"""),

md(r"""## 16 · Proyecto: un experimento bien guardado

Juntemos todo en algo que harás en tu trabajo: un **barrido de ruedecillas** (probar una rejilla de combinaciones) cuyo resultado queda **guardado de forma ordenada** en una carpeta con su fecha:
la configuración (JSON), los resultados (CSV) y la mejor política (`.npy`). Así, dentro de un mes, sabrás **exactamente** qué probaste y qué salió.
"""),

code(r"""# 1. Una carpeta para este experimento, con la fecha en el nombre
experimento = carpeta / f"barrido_{datetime.now():%Y%m%d}"
experimento.mkdir(exist_ok=True)

# 2. La configuración, guardada ANTES de empezar
config = {"valores_k": [5, 10, 20, 30, 45], "valores_d": [0, 4, 8], "semillas": 5, "viento_maximo": 30}
(experimento / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

# 3. El barrido: todas las combinaciones, evaluadas con nuestro módulo
resultados = []
for k, d in itertools.product(config["valores_k"], config["valores_d"]):
    retorno = palo.evaluar(k, d, semillas=range(config["semillas"]), viento_maximo=config["viento_maximo"])
    resultados.append({"k": k, "d": d, "retorno": round(retorno, 2)})

# 4. Los resultados, en CSV
with open(experimento / "resultados.csv", "w", encoding="utf-8", newline="") as fichero:
    escritor = csv.DictWriter(fichero, fieldnames=["k", "d", "retorno"])
    escritor.writeheader()
    escritor.writerows(resultados)

# 5. La mejor política, en .npy
mejor = max(resultados, key=lambda fila: fila["retorno"])
np.save(experimento / "mejor_politica.npy", np.array([mejor["k"], mejor["d"]], dtype=float))

print(f"Probadas {len(resultados)} combinaciones. La mejor: {mejor}")
print("Ficheros guardados:", sorted(r.name for r in experimento.iterdir()))"""),

md(r"""(`json.dumps`, con `s` al final, convierte a texto JSON sin escribir en un fichero; y `f"{datetime.now():%Y%m%d}"` usa el formato de fecha directamente dentro de una f-string.)

15 combinaciones probadas y tres ficheros guardados. Y ahora la prueba de que todo sirve: imagina que es otro día, en otra sesión. **Solo con los ficheros**, sin ninguna variable del barrido, recuperamos
la configuración, los resultados y la mejor política:
"""),

code(r"""config_leida = json.loads((experimento / "config.json").read_text(encoding="utf-8"))
with open(experimento / "resultados.csv", encoding="utf-8") as fichero:
    filas = list(csv.DictReader(fichero))
mejor_k, mejor_d = np.load(experimento / "mejor_politica.npy")

print("Se probaron k =", config_leida["valores_k"], "y d =", config_leida["valores_d"])
print(f"{'k':>4} {'d':>3} {'retorno':>8}")
for fila in sorted(filas, key=lambda f: float(f["retorno"]), reverse=True)[:5]:
    print(f"{fila['k']:>4} {fila['d']:>3} {float(fila['retorno']):>8.1f}")
print(f"La mejor política guardada (k={mejor_k}, d={mejor_d}) da hoy: {palo.evaluar(mejor_k, mejor_d):.1f}")"""),

md(r"""Todo recuperado desde el disco, y la mejor política vuelve a dar el mismo retorno. **Esto es reproducibilidad**: cualquiera con esos ficheros (y el módulo `palo.py`) puede comprobar tus resultados.
Es lo que distingue un experimento profesional de "lo probé y me salió bien, pero no sé con qué números".

(Fíjate en `float(fila["retorno"])` al ordenar: del CSV todo vuelve como **texto**, y ordenar textos de números da resultados raros, NB20.)
"""),

md(r"""## 17 · Resumen de la lección

1. **`pathlib.Path`**: rutas que se unen con `/`, con `.name`, `.stem`, `.suffix`, `.parent`, `mkdir`, `exists`, `iterdir`, `glob`. **`open` + `with`** abre y cierra solo: modo `"w"` (borra y escribe),
   `"a"` (añade), `"r"` (lee); siempre `encoding="utf-8"`. Un fichero se recorre línea a línea (cada línea con su `\n`). `FileNotFoundError` si no existe.
2. Formatos: **CSV** para tablas (`csv.DictWriter`/`DictReader`; ¡todo vuelve como texto!), **JSON** para configuraciones (`json.dump`/`load`; conserva los tipos), **`.npy`** para arrays (`np.save`/
   `np.load`), y **pickle** para cualquier objeto (**nunca** cargues uno de origen dudoso: puede ejecutar código).
3. **Módulos** propios: código en un `.py` que se **importa** (Python lo busca en `sys.path`; `importlib.reload` si cambia). Varios módulos en una carpeta forman un **paquete**.
4. **Scripts**: `if __name__ == "__main__":` y **`argparse`** para las opciones (y `--help` gratis). Se lanzan desde la **terminal** (`python script.py --k 30`), o desde Python con `subprocess` y
   `sys.executable`. Órdenes básicas de terminal: `pwd`, `ls`, `cd`, `mkdir`, `cp`, `mv`, `rm` (¡sin papelera!), `cat`.
5. **Entorno virtual** (`venv`, `source venv/bin/activate`) y **`pip`** (`install`, `freeze`, `requirements.txt`). **`logging`** para registrar con hora y nivel. Biblioteca estándar: `Counter`,
   `defaultdict`, `datetime`, `itertools.product`, `statistics`. Proyecto: un barrido guardado y recuperado: **reproducibilidad**.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Fichero / archivo** | Datos guardados en el disco, que sobreviven al programa. |
| **Ruta** | La "dirección" de un fichero en el árbol de carpetas. |
| **Directorio de trabajo** | La carpeta desde la que se buscan las rutas relativas (`Path.cwd()`). |
| **Gestor de contexto / `with`** | Algo que se abre y se cierra solo, pase lo que pase. |
| **CSV / JSON** | Formatos de texto para tablas / para estructuras anidadas. |
| **`.npy`** | El formato de NumPy para guardar arrays exactos. |
| **pickle** | Guarda cualquier objeto... y cargar uno es como ejecutar un programa. |
| **Módulo / paquete** | Un fichero `.py` que se importa / una carpeta de módulos. |
| **Script** | Un `.py` pensado para ejecutarse como programa. |
| **`__name__ == "__main__"`** | Cierto solo si el fichero se ejecuta directamente (no si se importa). |
| **`argparse`** | El módulo para que un script acepte opciones (`--k 30`). |
| **Terminal** | La ventana para dar órdenes de texto al ordenador. |
| **Entorno virtual** | Un Python con sus propias bibliotecas, solo para un proyecto. |
| **`pip` / `requirements.txt`** | El instalador de bibliotecas / la lista de versiones de un proyecto. |
| **`logging`** | El módulo para registrar mensajes con hora y nivel. |
| **Reproducibilidad** | Que otro pueda repetir tu experimento y obtener lo mismo. |
| **`+=`** | Forma corta de `x = x + ...` (y `-=`, `*=`, `/=`). |
"""),

md(r"""## 18 · Ejercicios

**E1.** Con `Path`, construye la ruta `practica_nb26/videos/semilla_03.mp4` y muestra su nombre, su extensión y su carpeta. (No hace falta crear el fichero.)

**E2.** Escribe en `practica_nb26/numeros.txt` los números del 1 al 5, uno por línea. Luego léelo y calcula su suma (¡recuerda `strip` y `int`!).

**E3.** ¿Qué diferencia hay entre abrir un fichero con `"w"` y con `"a"`? ¿Cuál usarías para ir apuntando un episodio por línea durante un entrenamiento de horas?

**E4.** Guarda en JSON el diccionario `{"red": [256, 256], "tasa": 0.0003}`, cárgalo y comprueba que la tasa vuelve como número (no como texto).

**E5.** ¿Por qué es peligroso hacer `pickle.load` de un fichero descargado de internet? ¿Qué formato usarías para compartir pesos de una red?

**E6.** Lanza el script `evaluar_politica.py` (con `lanzar`) con k = 8 y d = 8. ¿Qué retorno sale? ¿Por qué tan bajo? (Pista: NB11, E2.)

**E7.** Con `Counter`, cuenta las letras de la palabra `"aprendizaje"` y di cuál se repite más.

**E8.** **Reto.** Añade al script un argumento `--semillas` (entero, por defecto 5) que diga con cuántas semillas evaluar, y lánzalo con `--semillas 20`.
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
ruta = Path("practica_nb26") / "videos" / "semilla_03.mp4"
print(ruta.name, ruta.suffix, ruta.parent)
```

Salida: `semilla_03.mp4 .mp4 practica_nb26/videos`. Una ruta es solo una "dirección": puede existir o no en el disco.
</details>

<details>
<summary>▶ Solución E2</summary>

```python
ruta = carpeta / "numeros.txt"
with open(ruta, "w", encoding="utf-8") as fichero:
    for n in range(1, 6):
        fichero.write(f"{n}\n")

with open(ruta, encoding="utf-8") as fichero:
    print(sum(int(linea.strip()) for linea in fichero))
```

Salida: **15**. Cada línea leída es un texto como `"3\n"`: `strip` quita el salto de línea e `int` lo convierte en número.
</details>

<details>
<summary>▶ Solución E3</summary>

`"w"` **borra** el contenido anterior y empieza de cero; `"a"` **añade** al final, conservando lo que había. Para un registro que crece durante horas, **`"a"`**: cada episodio se añade detrás del
anterior, y si el programa se corta, lo apuntado hasta ese momento se conserva.
</details>

<details>
<summary>▶ Solución E4</summary>

```python
ruta = carpeta / "red.json"
ruta.write_text(json.dumps({"red": [256, 256], "tasa": 0.0003}), encoding="utf-8")
cargado = json.loads(ruta.read_text(encoding="utf-8"))
print(cargado["tasa"], type(cargado["tasa"]))      # 0.0003 <class 'float'>
```

JSON conserva los tipos: la tasa vuelve como `float` y las capas como lista de enteros (al contrario que CSV, donde todo vuelve como texto).
</details>

<details>
<summary>▶ Solución E5</summary>

Porque un fichero pickle puede llevar **instrucciones** que se ejecutan al cargarlo: un `.pkl` malicioso podría borrar tus archivos o robar datos en el mismo momento del `pickle.load`. Para compartir
pesos, mejor un formato que **solo** contenga números y no pueda ejecutar nada, como `.npy` (NumPy) o *safetensors* (el estándar actual para modelos de redes neuronales).
</details>

<details>
<summary>▶ Solución E6</summary>

```python
lanzar("--k", "8", "--d", "8")
```

Sale un retorno bajo, de unos **182** puntos (como en el NB23). La ruedecilla de inclinación (8) es **menor que la "gravedad"** del palo (10): el motor no empuja lo bastante para vencerla, y el palo
acaba cayendo (NB11, ejercicio E2).
</details>

<details>
<summary>▶ Solución E7</summary>

```python
from collections import Counter
print(Counter("aprendizaje").most_common(3))
```

La **a** y la **e** aparecen 2 veces cada una (a-pr-e-ndiz-a-j-e). `Counter` funciona con cualquier iterable, también con una cadena, que se recorre letra a letra.
</details>

<details>
<summary>▶ Solución E8</summary>

En `codigo_del_script`, añade junto a los otros argumentos:

```python
    parser.add_argument("--semillas", type=int, default=5, help="número de semillas")
```

y cambia la llamada a `evaluar(args.k, args.d, semillas=range(args.semillas), viento_maximo=args.viento)`. Vuelve a ejecutar la celda que escribe el script y lanza `lanzar("--semillas", "20")`. Con
más semillas, el retorno medio es más **fiable** (está medido en más mundos distintos).
</details>
"""),

md(r"""## 18 · 🛠 Práctica en MuJoCo: tu robot en un fichero y un script que graba vídeos

Hasta hoy, tus planos MJCF vivían **dentro del cuaderno**, como cadenas de texto. Pero los robots de verdad (el humanoide, el Zancudo que construirás
en la Parte 5) viven en **ficheros `.xml`**, y los vídeos y entrenamientos de verdad se lanzan con **scripts** desde la terminal. Hoy vas a cerrar
ese círculo:

1. Fabricar un palo de escoba **más largo** con una f-string (NB20) y **guardarlo en un fichero** `.xml`.
2. Cargarlo **desde el fichero** con `mujoco.MjModel.from_xml_path`.
3. Pedirle a MuJoCo que **escriba** el plano tal y como lo ha entendido (`mj_saveLastXML`).
4. Guardar una **trayectoria** simulada con `np.savez` y la **configuración** del experimento en JSON.
5. Escribir un **script** que, lanzado desde la terminal con sus opciones (`argparse`), carga el fichero, simula y **graba un vídeo él solo**.

Todo irá a una carpeta nueva, `practica_mujoco`, al lado de este cuaderno (como `practica_nb26`, se crea al ejecutar y Git la ignora), con nombres
que empiezan por `nb26_`.
"""),

md(r"""### Paso 1 · El plano, al disco

La carpeta, con `Path` y `mkdir` (apartado 2):
"""),

code(r"""from pathlib import Path
import mujoco
import numpy as np

carpeta_mj = Path("practica_mujoco")
carpeta_mj.mkdir(exist_ok=True)"""),

md(r"""Ahora la plantilla del palo de escoba del NB20 (la de `robots/palo_escoba.xml` con un hueco para el largo), y la escribimos en un fichero con
`write_text` (apartado 4). Un palo de **1,5 m**:
"""),

code(r"""def palo_xml(largo):
    return f'''<mujoco model="palo_{largo}">
  <option timestep="0.01"/>
  <worldbody>
    <light pos="0 0 4"/>
    <geom type="plane" size="4 2 0.1" rgba=".8 .9 .8 1"/>
    <geom type="capsule" fromto="-2 0 0.5 2 0 0.5" size="0.02" rgba=".4 .4 .4 1" contype="0" conaffinity="0"/>
    <body name="carro" pos="0 0 0.5">
      <joint name="deslizar" type="slide" axis="1 0 0" range="-1.8 1.8" limited="true" damping="0.1"/>
      <geom type="box" size="0.15 0.1 0.05" mass="1" rgba=".2 .4 .9 1" contype="0" conaffinity="0"/>
      <body name="palo">
        <joint name="bisagra" type="hinge" axis="0 1 0" damping="0.01"/>
        <geom type="capsule" fromto="0 0 0 0 0 {largo}" size="0.03" mass="0.5" rgba="1 .5 .1 1" contype="0" conaffinity="0"/>
      </body>
    </body>
  </worldbody>
  <actuator>
    <motor name="empuje" joint="deslizar" gear="10" ctrlrange="-1 1" ctrllimited="true"/>
  </actuator>
</mujoco>
'''

ruta_xml = carpeta_mj / "nb26_palo_largo.xml"
ruta_xml.write_text(palo_xml(1.5), encoding="utf-8")
print(ruta_xml, "->", ruta_xml.stat().st_size, "bytes")"""),

md(r"""(`ruta.stat().st_size` es el tamaño del fichero en bytes: una propiedad más de `Path`.) Comprobémoslo desde la **terminal**, con `!` y `head`
(apartado 12), que enseña sus primeras líneas:
"""),

code(r"""!head -4 practica_mujoco/nb26_palo_largo.xml"""),

md(r"""### Paso 2 · Cargar desde el fichero

Hasta ahora usabas `from_xml_string` (desde un texto). Para un fichero, **`from_xml_path`** (desde una ruta). Ojo: MuJoCo quiere la ruta como
**texto**, así que convertimos el `Path` con `str` (NB20):
"""),

code(r"""modelo = mujoco.MjModel.from_xml_path(str(ruta_xml))
datos = mujoco.MjData(modelo)
print("Cargado:", modelo.nbody, "piezas,", modelo.njnt, "articulaciones,", modelo.nu, "motor")
print("Largo del palo (mitad de la cápsula x 2):", 2 * modelo.geom_size[3][1], "m")"""),

md(r"""¿Por qué usar ficheros si `from_xml_string` funciona igual? Por tres razones: el plano se puede **compartir** y reutilizar desde cualquier
programa (como `robots/palo_escoba.xml`, que usan todas las prácticas); se puede abrir con un **editor**; y los robots de verdad usan **mallas**
(ficheros `.stl` con la forma 3D de cada pieza) que el plano nombra **por su ruta, relativa a la carpeta del `.xml`**. Con `from_xml_string`,
MuJoCo no sabría dónde buscarlas.

Y si la ruta está mal, el error del NB22, ahora con fichero:
"""),

code(r"""try:
    mujoco.MjModel.from_xml_path("practica_mujoco/no_existe.xml")
except ValueError as e:
    print("ValueError:", str(e).split("\n")[0])"""),

md(r"""### Paso 3 · Lo que MuJoCo ha entendido

MuJoCo puede hacer el viaje de vuelta: **escribir en un fichero** el plano del último modelo que ha cargado, con `mujoco.mj_saveLastXML`. Lo
interesante es que no escribe **tu** texto, sino **lo que ha entendido**:
"""),

code(r"""ruta_entendido = carpeta_mj / "nb26_palo_entendido.xml"
mujoco.mj_saveLastXML(str(ruta_entendido), modelo)
print(ruta_entendido.read_text(encoding="utf-8"))"""),

md(r"""Compara con tu plano y verás que MuJoCo lo ha "traducido" a su forma interna:

- Tu `fromto="0 0 0 0 0 1.5"` (de un punto a otro) se ha convertido en un **centro** (`pos="0 0 0.75"`), un **giro** (`quat`: cuatro números para
  un giro, como los 4 de la articulación `root` del humanoide que viste en el NB21) y un **tamaño** (`size="0.03 0.75"`: radio y **media** longitud).
- Tu `<motor>` es ahora un `<general>`: `motor` era un **atajo** para el actuador general con unas opciones concretas.
- Ha añadido `<compiler angle="radian"/>`: deja claro que los ángulos están en radianes.

Es muy útil para **depurar** (NB22): si un robot no se comporta como esperas, mira lo que MuJoCo ha entendido, no lo que tú crees que escribiste.
"""),

md(r"""### Paso 4 · Guardar un experimento: configuración y trayectoria

Un experimento bien guardado (apartado 16) lleva su **configuración** en JSON y sus **resultados**. Simulamos el palo largo inclinado 10° con el
controlador PD del NB23-NB25 durante 5 s, y apuntamos el reloj y las posiciones de cada paso:
"""),

code(r"""import json

config = {"plano": ruta_xml.name, "inclinacion_grados": 10, "k": 3, "d": 0.8, "segundos": 5}
(carpeta_mj / "nb26_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

mujoco.mj_resetData(modelo, datos)
datos.qpos[1] = np.radians(config["inclinacion_grados"])
tiempos, posiciones = [], []
for _ in range(round(config["segundos"] / modelo.opt.timestep)):
    x, angulo = datos.qpos
    vx, vel_angulo = datos.qvel
    datos.ctrl[0] = np.clip(config["k"] * angulo + config["d"] * vel_angulo + 0.1 * x + 0.2 * vx, -1, 1)
    mujoco.mj_step(modelo, datos)
    tiempos.append(datos.time)
    posiciones.append(datos.qpos.copy())          # ¡copy! (la trampa del alias, NB21)

np.savez(carpeta_mj / "nb26_trayectoria.npz", t=np.array(tiempos), qpos=np.array(posiciones))
print("Guardados:", sorted(p.name for p in carpeta_mj.glob("nb26_*")))"""),

md(r"""Un detalle **importantísimo**: `datos.qpos.copy()`. `datos.qpos` es **siempre el mismo array**, que MuJoCo va sobrescribiendo en cada paso.
Si guardaras `datos.qpos` a secas, tu lista tendría 500 **alias** del mismo array (NB21), y al final todos valdrían lo del último paso.

Ahora, como si fuera otro día y otro programa, lo leemos todo de vuelta:
"""),

code(r"""config_leida = json.loads((carpeta_mj / "nb26_config.json").read_text(encoding="utf-8"))
tray = np.load(carpeta_mj / "nb26_trayectoria.npz")

print("Configuración:", config_leida)
print("Forma de qpos:", tray["qpos"].shape)
angulos = np.degrees(tray["qpos"][:, 1])
print(f"Ángulo: empieza en {angulos[0]:.1f}°, el más lejano {abs(angulos).max():.1f}°, acaba en {angulos[-1]:.2f}°")"""),

md(r"""500 filas (una por paso) y 2 columnas (carro y palo). El palo de 1,5 m empieza a 10°, el controlador lo endereza y acaba prácticamente vertical.
Todo leído **del disco**: si reinicias el kernel, sigue ahí.
"""),

md(r"""### Paso 5 · Un script que graba vídeos

Ahora, lo más profesional de la práctica: un **script** que se lanza desde la terminal. Recibe con `argparse` (apartado 11) la ruta del plano, los
segundos, las ganancias del controlador y dónde guardar el vídeo; carga el fichero, simula, fotografía con `mujoco.Renderer` (como tu `mi_video` del
NB23) y guarda el MP4 con `imageio`. Fíjate en tres cosas:

- La **primera línea de código** pone `MUJOCO_GL=egl` **antes** de importar MuJoCo: en la Pi no hay pantalla, y así MuJoCo dibuja "a ciegas".
  (En el cuaderno lo hacía `taller` por ti.)
- Todo va en funciones, y al final el `if __name__ == "__main__":` (apartado 11).
- Al terminar, escribe una línea de **resumen**: es lo que verás en la terminal.
"""),

code(r"""codigo_script = '''# nb26_video.py: carga un palo de escoba desde un fichero MJCF, lo controla con un PD y graba un vídeo.
import os
os.environ.setdefault("MUJOCO_GL", "egl")          # dibujar sin pantalla

import argparse
import imageio
import mujoco
import numpy as np


def simular_y_grabar(ruta_xml, segundos, k, d, grados, salida):
    modelo = mujoco.MjModel.from_xml_path(ruta_xml)
    datos = mujoco.MjData(modelo)
    datos.qpos[1] = np.radians(grados)
    camara = mujoco.MjvCamera()
    mujoco.mjv_defaultFreeCamera(modelo, camara)
    camara.distance, camara.azimuth, camara.elevation = 5.0, 90, -15
    cada = max(1, round(1 / (30 * modelo.opt.timestep)))
    fotos = []
    with mujoco.Renderer(modelo, 270, 360) as dibujante:
        for paso in range(round(segundos / modelo.opt.timestep)):
            x, angulo = datos.qpos
            vx, vel_angulo = datos.qvel
            datos.ctrl[0] = np.clip(k * angulo + d * vel_angulo + 0.1 * x + 0.2 * vx, -1, 1)
            mujoco.mj_step(modelo, datos)
            if paso % cada == 0:
                dibujante.update_scene(datos, camera=camara)
                fotos.append(dibujante.render())
    imageio.mimsave(salida, fotos, fps=1 / (cada * modelo.opt.timestep), macro_block_size=1)
    return np.degrees(datos.qpos[1]), len(fotos)


def main():
    parser = argparse.ArgumentParser(description="Simula un palo de escoba MJCF con un PD y graba un vídeo.")
    parser.add_argument("xml", help="ruta del fichero MJCF")
    parser.add_argument("--segundos", type=float, default=4.0, help="duración simulada")
    parser.add_argument("--k", type=float, default=3.0, help="ganancia de inclinación")
    parser.add_argument("--d", type=float, default=0.8, help="ganancia de velocidad")
    parser.add_argument("--grados", type=float, default=10.0, help="inclinación inicial")
    parser.add_argument("--salida", default="video.mp4", help="fichero MP4 de salida")
    args = parser.parse_args()

    angulo_final, n_fotos = simular_y_grabar(args.xml, args.segundos, args.k, args.d, args.grados, args.salida)
    print(f"{args.xml}: {args.segundos} s, k={args.k}, d={args.d} -> palo a {angulo_final:.1f} grados; "
          f"{n_fotos} fotos en {args.salida}")


if __name__ == "__main__":
    main()
'''
(carpeta_mj / "nb26_video.py").write_text(codigo_script, encoding="utf-8")
print("Script escrito:", carpeta_mj / "nb26_video.py")"""),

md(r"""Primero, la ayuda que `argparse` fabrica sola. Lo lanzamos con `!` como si estuviéramos en la terminal. (`{sys.executable}` entre llaves en una
orden con `!` es un truco de Jupyter: escribe ahí el valor de la variable de Python, la ruta del Python del proyecto, apartado 11.)
"""),

code(r"""import sys
!{sys.executable} practica_mujoco/nb26_video.py --help"""),

md(r"""Fíjate en `xml` sin guiones: es un argumento **obligatorio** y **posicional** (va el primero, sin nombre). Los que llevan `--` son opcionales y
tienen su valor por defecto.

Y ahora, a grabar. Lo lanzamos con `subprocess` (apartado 11), para recoger su resumen, y guardamos el vídeo en la carpeta de vídeos de las prácticas:
"""),

code(r"""import subprocess

salida = Path("assets") / "practicas" / "nb26_script.mp4"
salida.parent.mkdir(parents=True, exist_ok=True)
resultado = subprocess.run(
    [sys.executable, "practica_mujoco/nb26_video.py", "practica_mujoco/nb26_palo_largo.xml",
     "--segundos", "4", "--grados", "10", "--salida", str(salida)],
    capture_output=True, text=True)
print(resultado.stdout.strip() or resultado.stderr.strip())"""),

md(r"""El script ha trabajado **él solo**, en otro proceso, sin saber nada de este cuaderno: ha leído el fichero, simulado, dibujado y guardado. Veamos su
vídeo:
"""),

code(r"""from IPython.display import Video
Video(str(salida), embed=True, html_attributes="controls loop autoplay muted")"""),

md(r"""El palo de 1,5 m, con la misma receta que sostenía el de 1 m. Ese script lo podrías lanzar igual desde una terminal de la Pi, por SSH desde otro
ordenador, o cien veces seguidas con distintas opciones desde un bucle. Así se trabaja en un laboratorio.

### Tus retos

**Reto 1.** Lanza el script con `--k 0 --d 0` (sin control) y `--salida` a otro fichero. ¿A qué ángulo acaba el palo? ¿Por qué no se queda en 90°?

**Reto 2.** Con un bucle, fabrica y guarda **tres** ficheros, `nb26_palo_1.0.xml`, `nb26_palo_2.0.xml` y `nb26_palo_3.0.xml` (con `palo_xml` y f-strings
para el nombre), y luego lista con `glob` (apartado 9) todos los `.xml` de la carpeta.

**Reto 3.** Lanza el script sobre los ficheros del Reto 2 con `subprocess` en un bucle, con `--segundos 4 --grados 20`, y mira su línea de resumen.
¿Qué palos aguanta el controlador?

<details>
<summary>▶ Solución Reto 1</summary>

```python
r = subprocess.run([sys.executable, "practica_mujoco/nb26_video.py", "practica_mujoco/nb26_palo_largo.xml",
                    "--k", "0", "--d", "0", "--salida", "assets/practicas/nb26_sin_control.mp4"],
                   capture_output=True, text=True)
print(r.stdout)
```

El resumen dice **1236,3 grados**: ¡más de **tres vueltas** completas! Como el palo no choca con nada (`contype="0"`), cae, pasa por debajo del
carro y, como casi no hay rozamiento en la bisagra, llega con fuerza para subir por el otro lado y seguir dando vueltas, como un molinillo. Y el
ángulo de MuJoCo no vuelve a 0 al pasar de 360°: **cuenta las vueltas**. (Míralo en el vídeo que ha grabado.)
</details>

<details>
<summary>▶ Solución Reto 2</summary>

```python
for largo in [1.0, 2.0, 3.0]:
    (carpeta_mj / f"nb26_palo_{largo}.xml").write_text(palo_xml(largo), encoding="utf-8")

for ruta in sorted(carpeta_mj.glob("*.xml")):
    print(ruta.name)
```

Salen los tres nuevos más los del Paso 1 y el Paso 3. `glob("*.xml")` es "todo lo que termine en `.xml`".
</details>

<details>
<summary>▶ Solución Reto 3</summary>

```python
for largo in [1.0, 2.0, 3.0]:
    r = subprocess.run([sys.executable, "practica_mujoco/nb26_video.py", f"practica_mujoco/nb26_palo_{largo}.xml",
                        "--segundos", "4", "--grados", "20", "--salida", f"assets/practicas/nb26_palo_{largo}.mp4"],
                       capture_output=True, text=True)
    print(r.stdout.strip())
```

Con 20° de partida, el controlador `k=3, d=0,8` sostiene los palos de **1 m** (acaba a 2,7°) y de **2 m** (a 3,9°; a los 4 s aún están
corrigiendo). Pero el de **3 m** acaba a **354°**: ¡ha caído y ha dado casi una vuelta entera! ¿No decía el NB20 que los palos largos son más
fáciles? Para **ti** sí, porque tú adaptas tus reflejos a cada palo. Este controlador tiene sus números **fijos**, pensados para el de 1 m, y no se
adapta. Cada robot necesita su propio ajuste: justo lo que hará por ti el aprendizaje por refuerzo.
</details>

### Qué has aprendido de MuJoCo hoy

- Un robot es un **fichero `.xml`**: se escribe con `write_text` y se carga con **`mujoco.MjModel.from_xml_path(str(ruta))`**. Los ficheros permiten
  compartir el robot y usar mallas con rutas relativas.
- **`mujoco.mj_saveLastXML(ruta, modelo)`** escribe lo que MuJoCo ha **entendido** de tu plano (`fromto` → `pos`/`quat`/`size`, `motor` → `general`).
- Para guardar una trayectoria, **copia** `datos.qpos` en cada paso (`.copy()`): MuJoCo reutiliza siempre el mismo array.
- Un **script** con `argparse` y `MUJOCO_GL=egl` simula y graba vídeos sin cuaderno ni pantalla, y se lanza desde la terminal o con `subprocess`.

En la práctica del NB27 harás que el ordenador **compruebe solo** que tu simulación es correcta: escribirás **tests** de MuJoCo (determinismo,
conservación de la energía) y los pasarás con `pytest`.
"""),

md(r"""## 20 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has salido del cuaderno: ficheros, módulos, scripts, la terminal, `pip`... y tu robot de MuJoCo vive ya en un fichero y se graba con un script. Ya sabes cómo se **organiza** y se **guarda** un proyecto de verdad. En el **NB27**, la última lección del bloque de
Python, cerramos con tres herramientas imprescindibles en cualquier trabajo: **NumPy a fondo** (para que nunca más te atasques con las formas de los arrays, y para simular **cien robots a la vez**),
los **tests** (programas que comprueban que tu código funciona) y **Git** (el control de versiones con el que se trabaja en equipo, y con el que este mismo curso se sube a GitHub).
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB26_python_ficheros_terminal.ipynb")
    build(out, cells, title="NB26 · Python de verdad (7): ficheros, módulos, scripts y la terminal")
