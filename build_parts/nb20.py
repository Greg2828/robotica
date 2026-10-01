"""Construye NB20 · Python de verdad (1): el texto a fondo.

Abre el bloque "Python de verdad" (NB20-NB27), antes del RL. Cadenas a fondo:
índices y porciones, inmutabilidad (TypeError real), len/in, métodos (upper,
lower, strip, replace, startswith/endswith, find, count, split, join),
conversiones str/int/float (ValueError real), concatenar y repetir, caracteres
especiales (\n, \t, comillas), cadenas multilínea, f-strings y formato
(decimales, ancho, alineación, miles, signo, porcentaje), comparar texto.
Proyecto: parsear un registro de entrenamiento ("episodio=12 retorno=455.3
pasos=500") y producir un informe alineado.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from nbbuild import md, code, code_err, build

cells = [

md(r"""# NB20 · Python de verdad (1): el texto a fondo

**Parte 3 · Python de verdad — Lección 1**

> Hasta aquí has aprendido el Python **justo** para entender las ideas de la robótica: variables, bucles, decisiones,
> listas, funciones y algo de NumPy. Con eso has llegado lejísimos: has entrenado una red neuronal escribiendo tú mismo su
> retropropagación. Pero si quieres **trabajar** de esto, hace falta más.

Empieza un bloque de **ocho lecciones** dedicado a convertirte en alguien que **programa en Python con soltura**, como un
profesional. Esto es lo que vamos a ver:

| Lección | Tema |
|---|---|
| **NB20** | El texto a fondo (hoy) |
| NB21 | Colecciones: tuplas, listas a fondo, diccionarios, conjuntos |
| NB22 | Control de flujo y errores: `while`, excepciones, depurar |
| NB23 | Funciones a fondo: parámetros, `lambda`, cierres, decoradores, generadores |
| NB24 | Clases y objetos (I): construir tus propias "cosas" |
| NB25 | Clases y objetos (II): herencia y tu propio entorno de Gymnasium |
| NB26 | Ficheros, módulos, scripts y la terminal |
| NB27 | NumPy a fondo, tests y Git |

¿Por qué ahora, antes del aprendizaje por refuerzo de verdad? Porque las herramientas profesionales (PyTorch, Stable-Baselines3,
MuJoCo) están escritas usando **todo** esto. Si no lo dominas, su código te parecerá magia y solo podrás copiarlo. Si lo dominas,
podrás **leerlo, entenderlo y cambiarlo**, que es lo que te pedirán en un trabajo.

Mismo método de siempre: una idea nueva por celda, ejemplos de robots, y muchos ejercicios resueltos al final. Hoy, el **texto**.
"""),

md(r"""## 1 · ¿Por qué importa tanto el texto?

Podría parecer que en robótica todo son números. Pero un ingeniero se pasa el día rodeado de **texto**:

- **Mensajes de progreso** mientras entrena: "episodio 1500 | retorno 455,3 | 12 minutos".
- **Nombres de archivos**: `politica_paso_01500.npy`, `video_semilla_3.mp4`.
- **Registros** (*logs*): ficheros enormes con una línea por episodio, que luego hay que **leer** y **analizar**.
- **Configuraciones**: `"Humanoid-v5"`, `"relu"`, `"cuda"`.
- **Mensajes de error**, que hay que leer y entender (desde el NB05).

Desde el NB05 sabes que un texto entre comillas es una **cadena** (*string*). Hoy aprenderás a **trabajar** con cadenas: cortarlas,
buscarlas, transformarlas, construirlas y darles formato. Al final, harás algo muy real: leer un registro de entrenamiento y producir un
informe ordenado.
"""),

md(r"""## 2 · Una cadena es una secuencia de caracteres

Una cadena se parece mucho a una **lista** (NB09), pero de **caracteres** (letras, números, espacios, signos). Por eso funcionan muchas
cosas que ya conoces. `len` dice cuántos caracteres tiene:
"""),

code(r"""entorno = "Humanoid-v5"
print(len(entorno))"""),

md(r"""**11** caracteres: H, u, m, a, n, o, i, d, -, v y 5 (el guion también cuenta). Y cada carácter tiene su **índice**, empezando en 0,
igual que en las listas:
"""),

code(r"""print(entorno[0])
print(entorno[-1])"""),

md(r"""`entorno[0]` es la primera letra, **H**, y `entorno[-1]` la última, **5** (los índices negativos cuentan desde el final, NB09). Y
también funcionan las **porciones** `[inicio:fin]`, que paran **antes** del fin:
"""),

code(r"""print(entorno[0:8])
print(entorno[9:])"""),

md(r"""`[0:8]` da **Humanoid** (índices 0 a 7) y `[9:]` da **v5** (desde el 9 hasta el final; si no se pone el fin, se entiende "hasta el
final", igual que `[:5]` se entiende "desde el principio", NB15).
"""),

md(r"""## 3 · Las cadenas no se pueden cambiar

Una diferencia importante con las listas: una cadena, una vez creada, **no se puede modificar**. Si intentas cambiar una letra, Python
se queja:
"""),

code_err(r"""entorno[0] = "h"
"""),

md(r"""`TypeError: 'str' object does not support item assignment`: "un objeto `str` (cadena) no permite asignar elementos". Se dice que las
cadenas son **inmutables** ("que no cambian").

¿Entonces cómo se "cambia" un texto? **Creando una cadena nueva** a partir de la vieja, y guardándola (si quieres, en la misma caja).
Todo lo que veremos hoy (pasar a minúsculas, reemplazar, recortar...) funciona así: **nunca cambia la cadena original; devuelve una
nueva**. Recuérdalo, porque es un despiste muy común (llamar a un método y olvidar guardar el resultado).
"""),

md(r"""## 4 · ¿Está dentro? La palabra `in`

Para preguntar si un trozo de texto aparece dentro de otro, se usa **`in`** (que da `True` o `False`, NB08):"""),

code(r"""print("v5" in entorno)
print("Walker" in entorno)"""),

md(r"""Muy útil para revisar textos: por ejemplo, ¿el mensaje de un error contiene la palabra `"shape"`? Entonces es un problema de tamaños
(NB15). (`in` también funciona con listas: `3 in [1, 2, 3]` es `True`.)
"""),

md(r"""## 5 · Los métodos de las cadenas

Las cadenas traen **montones de métodos** (órdenes que les pertenecen y se escriben con un punto, como el `append` de las listas, NB09).
Vamos con los más útiles, uno por celda.

**Mayúsculas y minúsculas**, con `upper` y `lower` (muy útil para comparar textos sin que importe cómo los escribió alguien):
"""),

code(r"""print(entorno.upper())
print(entorno.lower())
print(entorno)"""),

md(r"""Fíjate en la tercera línea: `entorno` **sigue igual**. `upper` y `lower` devuelven una cadena **nueva** (apartado 3).

**Quitar espacios sobrantes** de los extremos, con `strip`. Muy útil al leer texto de ficheros, que a menudo trae espacios o saltos de
línea "invisibles" al principio o al final:
"""),

code(r"""sucio = "   relu   "
print("[" + sucio + "]")
print("[" + sucio.strip() + "]")"""),

md(r"""(Hemos puesto corchetes alrededor para que se vean los espacios.) `strip` ha quitado los espacios de los dos lados. (También existen
`lstrip` y `rstrip`, que quitan solo los de la izquierda o la derecha.)

**Reemplazar** un trozo por otro, con `replace`:
"""),

code(r"""print(entorno.replace("v5", "v4"))"""),

md(r"""**¿Empieza o termina por...?**, con `startswith` y `endswith`. Perfecto para filtrar archivos por su tipo:"""),

code(r"""archivo = "politica_paso_01500.npy"
print(archivo.startswith("politica"))
print(archivo.endswith(".npy"))
print(archivo.endswith(".mp4"))"""),

md(r"""**Buscar dónde está** un trozo, con `find` (devuelve el índice donde empieza, o **−1** si no lo encuentra), y **contar** cuántas veces
aparece, con `count`:
"""),

code(r"""print(archivo.find("paso"))
print(archivo.find("video"))
print(archivo.count("_"))"""),

md(r"""`"paso"` empieza en el índice **9**; `"video"` no está (**−1**); y hay **2** guiones bajos.
"""),

md(r"""## 6 · Partir y unir: `split` y `join`

Estos dos son, probablemente, los métodos más usados de todos.

**`split`** ("partir") corta una cadena en trozos, usando un **separador**, y devuelve una **lista** con los trozos. Por ejemplo, partir el
nombre del archivo por los guiones bajos:
"""),

code(r"""trozos = archivo.split("_")
print(trozos)"""),

md(r"""Una lista con tres trozos: `'politica'`, `'paso'` y `'01500.npy'`. Si no le das separador, `split()` corta por los **espacios** (y
se salta los espacios repetidos), que es justo lo que se necesita para separar las palabras de una frase:
"""),

code(r"""linea = "episodio 12   retorno 455.3"
print(linea.split())"""),

md(r"""**`join`** ("unir") hace lo contrario: junta una lista de cadenas en una sola, poniendo un separador entre cada una. Se escribe de una
forma un poco curiosa: **el separador primero**, y luego `.join(lista)`:
"""),

code(r"""partes = ["politica", "paso", "01500"]
print("_".join(partes))
print(" -> ".join(["observar", "decidir", "actuar"]))"""),

md(r"""Se lee: "une estas partes **con** guiones bajos". La segunda línea dibuja el bucle del NB03 en una línea.
"""),

md(r"""## 7 · Convertir entre texto y números

Un problema que te encontrarás **constantemente**: cuando lees un número de un texto (de un fichero, de un registro), lo que tienes es...
**texto**. `"455.3"` no es un número; es una cadena de 5 caracteres. Si intentas sumarle algo, falla. Para convertirla en número se usan
**`float`** (decimal) e **`int`** (entero):
"""),

code(r"""texto = "455.3"
numero = float(texto)
print(numero + 10)
print(int("500") * 2)"""),

md(r"""Ahora sí: 465.3 y 1000. Y al revés, **`str`** (que ya usaste en el NB16) convierte un número en texto.

¿Y si el texto no es un número? Python se queja con un error nuevo:
"""),

code_err(r"""print(float("cuatrocientos"))"""),

md(r"""`ValueError: could not convert string to float: 'cuatrocientos'`: "**error de valor**: no se pudo convertir la cadena a decimal". El
`ValueError` ya lo viste en el NB15 con las formas de NumPy; en general significa "**el tipo está bien, pero el valor no tiene sentido**".
(Un detalle: `int("455.3")` también falla, porque `int` solo acepta textos de números **enteros**. Para eso, primero `float` y luego `int`.)
"""),

md(r"""## 8 · Pegar y repetir texto

Con cadenas, **`+`** pega una detrás de otra (como con las listas, NB15) y **`*`** repite:"""),

code(r"""print("paso_" + str(1500))
print("=" * 30)"""),

md(r"""La segunda línea es un truco muy usado para dibujar una **línea separadora** en los mensajes. Fíjate en la primera: para pegar un
número a un texto con `+`, hay que convertirlo antes con `str` (si no, `TypeError`: no se puede sumar un texto y un número). Por eso existe
una forma mucho mejor de construir textos con números dentro, que veremos en el apartado 10.
"""),

md(r"""## 9 · Caracteres especiales y textos largos

Algunos caracteres no se pueden escribir directamente dentro de unas comillas. Para ellos existen las **secuencias de escape**, que empiezan
con una barra invertida **`\`**:

| Secuencia | Significa |
|---|---|
| `\n` | **salto de línea** (*new line*) |
| `\t` | **tabulador** (un hueco grande, para alinear) |
| `\"` | unas comillas dentro de una cadena con comillas |
| `\\` | una barra invertida de verdad |
"""),

code(r"""print("Línea 1\nLínea 2")
print("motor\tvalor")
print("cadera\t0.3")"""),

md(r"""El `\n` ha partido el texto en dos líneas, y el `\t` ha separado las columnas con un hueco.

Y para textos **largos**, de varias líneas, se pueden usar **comillas triples**: tres comillas seguidas, dobles o simples
(aquí usamos tres simples, `'''`). Todo lo que va dentro, saltos de línea incluidos, forma parte de la cadena:
"""),

code(r"""ficha = '''Entorno: palo de escoba
Observación: inclinación y velocidad
Acción: empuje entre -40 y 40'''
print(ficha)"""),

md(r"""(¿Recuerdas que en el NB10 dijimos que dentro del código de este curso usaríamos comentarios `#` y no comillas triples? Era solo por cómo
están fabricados estos cuadernos; en tus programas puedes usarlas sin problema.)
"""),

md(r"""## 10 · Las f-strings: la forma profesional de construir textos

Construir mensajes con `+` y `str` es incómodo. La forma moderna, y la que verás en **todo** el código profesional, son las **f-strings**: se
pone una **`f`** justo antes de las comillas, y dentro del texto se escriben **variables o cuentas entre llaves `{ }`**. Python las sustituye
por su valor:
"""),

code(r"""episodio = 12
retorno = 455.3456
print(f"Episodio {episodio}: retorno {retorno}")"""),

md(r"""Mucho más limpio que `"Episodio " + str(episodio) + ": retorno " + str(retorno)`. Y dentro de las llaves puede ir **cualquier expresión**,
no solo variables:
"""),

code(r"""print(f"El doble del retorno es {retorno * 2}")
print(f"¿Ha superado los 400? {retorno > 400}")"""),

md(r"""### Dar formato a los números

Lo mejor de las f-strings es que se puede decir **cómo** mostrar cada número, poniendo **dos puntos** y un **código de formato** después del
valor. El más usado: **cuántos decimales**, con `.Nf` (la `f` significa "número decimal"):
"""),

code(r"""print(f"Retorno: {retorno:.2f}")
print(f"Retorno: {retorno:.0f}")"""),

md(r"""`:.2f` muestra **2 decimales** (455.35, redondeando) y `:.0f`, ninguno (455). Adiós a muchos `round` para mostrar números (NB06).

Otros códigos muy útiles:
"""),

code(r"""pasos_totales = 10000000
exito = 0.8734
print(f"Pasos: {pasos_totales:,}")          # separador de miles
print(f"Éxito: {exito:.1%}")                # como porcentaje, con 1 decimal
print(f"Cambio: {12.5:+.1f} y {-3.2:+.1f}")  # con signo siempre"""),

md(r"""- `:,` pone **comas de miles** (al estilo inglés): 10,000,000.
- `:.1%` multiplica por 100 y añade el **%**: 87.3%.
- `:+` muestra **siempre el signo**: +12.5 y −3.2.

### Alinear en columnas

Para hacer **tablas** bonitas, se puede pedir que un valor ocupe un **ancho** fijo de caracteres, y alinearlo a la izquierda (`<`), a la derecha
(`>`) o al centro (`^`). Por ejemplo, `:>8.2f` es "a la derecha, en 8 caracteres, con 2 decimales":
"""),

code(r"""print(f"{'política':<12}|{'retorno':>10}")
print(f"{'nada':<12}|{44.8:>10.1f}")
print(f"{'a mano':<12}|{499.9:>10.1f}")"""),

md(r"""Una tabla perfectamente alineada: los nombres a la izquierda en 12 caracteres, y los números a la derecha en 10, con un decimal.

| Código | Significa | Ejemplo | Resultado |
|---|---|---|---|
| `:.2f` | 2 decimales | `f"{3.14159:.2f}"` | `3.14` |
| `:,` | miles | `f"{1500000:,}"` | `1,500,000` |
| `:.1%` | porcentaje | `f"{0.5:.1%}"` | `50.0%` |
| `:+` | con signo | `f"{5:+}"` | `+5` |
| `:>8` | derecha, ancho 8 | `f"{42:>8}"` | `      42` |
| `:<8` | izquierda, ancho 8 | `f"{'a':<8}"` | `a       ` |
| `:05d` | entero con ceros delante | `f"{42:05d}"` | `00042` |

El último es justo el que se usa para nombres de archivo como `politica_paso_01500.npy`: así los archivos se ordenan bien (el 00200 va antes
que el 01500; sin ceros, "200" iría **después** de "1500" al ordenar como texto).
"""),

md(r"""## 11 · Comparar textos

Los textos se comparan con `==` (NB08), y la comparación **distingue mayúsculas** (para Python, "Relu" y "relu" son distintos). Por eso, para
comparar lo que escribe una persona, se suele pasar todo a minúsculas antes:
"""),

code(r"""activacion = "ReLU"
print(activacion == "relu")
print(activacion.lower() == "relu")"""),

md(r"""Y `<` y `>` comparan por **orden alfabético** (como en un diccionario de papel), lo que permite **ordenar** textos. Cuidado con un detalle: para
el ordenador, las mayúsculas van **antes** que las minúsculas, y los números como texto se ordenan **carácter a carácter** (por eso `"200" > "1500"`
es `True`: compara el "2" con el "1"). Es la razón del truco de los ceros delante del apartado anterior.
"""),

code(r"""print("200" > "1500")
print("00200" > "01500")"""),

md(r"""## 12 · Proyecto: leer un registro de entrenamiento

Un caso real. Mientras se entrena un robot, es muy habitual que el programa vaya escribiendo una línea por episodio en un **registro** (*log*).
Luego, el ingeniero lo **lee** para analizar cómo ha ido. Aquí tienes un trozo de registro (lo escribimos como una cadena multilínea; en el NB26
lo leeremos de un fichero de verdad):
"""),

code(r"""registro = '''episodio=1 retorno=44.8 pasos=50
episodio=2 retorno=97.2 pasos=104
episodio=3 retorno=213.5 pasos=231
episodio=4 retorno=455.3 pasos=500
episodio=5 retorno=499.9 pasos=500'''

lineas = registro.split("\n")
print(f"El registro tiene {len(lineas)} líneas")
print(lineas[0])"""),

md(r"""Partiendo por los saltos de línea (`\n`) tenemos una lista con una línea por episodio. Ahora hay que **sacar los números** de cada línea. Una línea
como `"episodio=4 retorno=455.3 pasos=500"` se puede partir primero por los espacios, y cada trozo, por el `=`:
"""),

code(r"""linea = lineas[3]
for trozo in linea.split():
    nombre, valor = trozo.split("=")
    print(nombre, "->", valor)"""),

md(r"""¿Has visto `nombre, valor = trozo.split("=")`? `split` devuelve una lista de **dos** trozos, y los guardamos en **dos** cajas a la vez (como el
`return` de dos valores del NB10; en el NB21 veremos que esto se llama **desempaquetar**).

Ahora juntemos todo en una función que lee **una línea** y devuelve sus tres números, ya convertidos (¡cuidado: el episodio y los pasos son enteros,
y el retorno, decimal!):
"""),

code(r"""def leer_linea(linea):
    episodio = retorno = pasos = None
    for trozo in linea.split():
        nombre, valor = trozo.split("=")
        if nombre == "episodio":
            episodio = int(valor)
        elif nombre == "retorno":
            retorno = float(valor)
        elif nombre == "pasos":
            pasos = int(valor)
    return episodio, retorno, pasos

print(leer_linea(lineas[3]))"""),

md(r"""(`episodio = retorno = pasos = None` pone las tres cajas a `None`, "nada" (NB10), de una vez: si alguna no aparece en la línea, se quedará en `None`.)

Y ahora, el **informe**: una tabla alineada con las f-strings, más un resumen al final:
"""),

code(r"""print(f"{'episodio':>8} | {'retorno':>8} | {'pasos':>5} | {'¿completo?':^10}")
print("-" * 42)

retornos = []
for linea in lineas:
    episodio, retorno, pasos = leer_linea(linea)
    retornos.append(retorno)
    completo = "sí" if pasos == 500 else "no"
    print(f"{episodio:>8} | {retorno:>8.1f} | {pasos:>5} | {completo:^10}")

print("-" * 42)
print(f"Retorno medio: {sum(retornos) / len(retornos):.1f}  |  mejor: {max(retornos):.1f}")"""),

md(r"""Un informe limpio y profesional, a partir de un texto en bruto.

(Una pequeña novedad: `completo = "sí" if pasos == 500 else "no"` es un **if en una sola línea**: "vale `"sí"` si los pasos son 500, y si no,
`"no"`". Se llama **expresión condicional** y es muy cómoda para elegir entre dos valores. La veremos más en el NB22.)

Esto que acabas de hacer, **leer un texto con una estructura, sacarle los datos y presentarlos**, se llama **analizar** o, en jerga, **parsear**
(del inglés *parse*). Es una de las tareas más comunes de cualquier programador.
"""),

md(r"""## 13 · Resumen de la lección

1. Una cadena es una secuencia de caracteres: `len`, índices (`[0]`, `[-1]`), porciones (`[0:8]`, `[9:]`) e `in` funcionan como en las listas. Pero es
   **inmutable**: no se puede cambiar una letra (`TypeError`); los métodos **devuelven una cadena nueva**.
2. Métodos clave: `upper`/`lower`, `strip`, `replace`, `startswith`/`endswith`, `find`/`count`, y los dos más usados: **`split`** (cadena → lista) y
   **`join`** (lista → cadena, con el separador delante: `"_".join(...)`).
3. Convertir: `float("455.3")`, `int("500")`, `str(1500)`. Si el texto no es un número: `ValueError`. `+` pega textos y `*` los repite.
4. Secuencias de escape (`\n`, `\t`, `\"`, `\\`) y cadenas multilínea con comillas triples.
5. **f-strings** (`f"... {valor:formato} ..."`): decimales (`:.2f`), miles (`:,`), porcentaje (`:.1%`), signo (`:+`), ancho y alineación (`:>8`, `:<12`,
   `:^10`), ceros delante (`:05d`). Con ellas hicimos un **parseador** de registros y un informe alineado.

### Palabras nuevas de hoy

| Palabra | Qué significa |
|---|---|
| **Inmutable** | Que no se puede cambiar una vez creado (como las cadenas). |
| **`split` / `join`** | Partir una cadena en una lista / unir una lista en una cadena. |
| **`strip`** | Quitar espacios y saltos de línea de los extremos. |
| **Secuencia de escape** | Combinación con `\` para caracteres especiales, como `\n`. |
| **f-string** | Cadena con `f` delante, con valores entre llaves que se sustituyen. |
| **Código de formato** | Lo que va tras los dos puntos en una f-string: `.2f`, `>8`... |
| **Registro (*log*)** | Fichero de texto donde un programa va apuntando lo que hace. |
| **Parsear** | Leer un texto con estructura y sacar sus datos. |
| **Expresión condicional** | Un if de una línea: `a if condición else b`. |
| **`ValueError`** | Error por un valor que no tiene sentido (como convertir "hola" en número). |
"""),

md(r"""## 14 · Ejercicios

**E1.** Con `nombre = "Walker2d-v5"`, saca con porciones el texto `"Walker"` y el texto `"v5"`.

**E2.** ¿Qué devuelve `"  Humanoid  ".strip().lower()`? (Fíjate en que se pueden **encadenar** métodos.)

**E3.** Convierte la frase `"observar decidir actuar"` en `"observar -> decidir -> actuar"` usando `split` y `join`.

**E4.** Escribe una f-string que muestre `"Paso 0042 de 1000 (4.2%)"` a partir de `paso = 42` y `total = 1000`.

**E5.** Fabrica, con un bucle y f-strings, los nombres de archivo `video_semilla_00.mp4` hasta `video_semilla_04.mp4`.

**E6.** De la lista `["politica_paso_00200.npy", "notas.txt", "politica_paso_01500.npy", "video.mp4"]`, quédate solo con los archivos de políticas (los que
empiezan por `"politica"` y terminan en `".npy"`), y extrae el número de paso de cada uno como **entero**.

**E7.** ¿Por qué `int("455.3")` da error? ¿Cómo conviertes `"455.3"` en el entero 455?

**E8.** **Reto.** El registro de un compañero viene "sucio": `"  Episodio=7 ;  RETORNO=301.25;pasos=320  "`. Escribe código que lo limpie y saque los tres
números. (Pista: `strip`, `lower`, `replace` y `split` encadenados.)
"""),

md(r"""<details>
<summary>▶ Solución E1</summary>

```python
nombre = "Walker2d-v5"
print(nombre[0:6])     # Walker
print(nombre[-2:])     # v5
```

`[-2:]` significa "desde el penúltimo hasta el final": muy práctico para coger el final de un texto sin contar su longitud.
</details>

<details>
<summary>▶ Solución E2</summary>

Devuelve **`"humanoid"`**. Primero `strip()` quita los espacios (dando `"Humanoid"`), y sobre ese resultado, `lower()` lo pasa a minúsculas. Se pueden
encadenar porque cada método devuelve una cadena nueva, que a su vez tiene métodos.
</details>

<details>
<summary>▶ Solución E3</summary>

```python
frase = "observar decidir actuar"
print(" -> ".join(frase.split()))
```

`split()` da `['observar', 'decidir', 'actuar']`, y `join` las une con `" -> "`.
</details>

<details>
<summary>▶ Solución E4</summary>

```python
paso = 42
total = 1000
print(f"Paso {paso:04d} de {total} ({paso / total:.1%})")
```

`:04d` rellena con ceros hasta 4 cifras (0042), y `:.1%` muestra 42/1000 = 0,042 como 4.2%.
</details>

<details>
<summary>▶ Solución E5</summary>

```python
for semilla in range(5):
    print(f"video_semilla_{semilla:02d}.mp4")
```

`:02d` = entero con al menos 2 cifras, rellenando con ceros.
</details>

<details>
<summary>▶ Solución E6</summary>

```python
archivos = ["politica_paso_00200.npy", "notas.txt", "politica_paso_01500.npy", "video.mp4"]
for archivo in archivos:
    if archivo.startswith("politica") and archivo.endswith(".npy"):
        numero_texto = archivo.split("_")[2].replace(".npy", "")
        print(archivo, "-> paso", int(numero_texto))
```

`archivo.split("_")[2]` es el tercer trozo (`"00200.npy"`), le quitamos el `".npy"` con `replace`, y `int("00200")` da **200** (los ceros de delante desaparecen
al convertir a número). Salen los pasos 200 y 1500.
</details>

<details>
<summary>▶ Solución E7</summary>

Porque `int` solo entiende textos de números **enteros**, y `"455.3"` tiene un punto decimal (`ValueError`). Se convierte en dos pasos: `int(float("455.3"))` da
**455** (`int` sobre un decimal **corta** la parte decimal, sin redondear: `int(455.9)` también da 455; si quieres redondear, `round(455.9)` da 456).
</details>

<details>
<summary>▶ Solución E8</summary>

```python
sucio = "  Episodio=7 ;  RETORNO=301.25;pasos=320  "
limpio = sucio.strip().lower().replace(" ", "")
print(limpio)                       # episodio=7;retorno=301.25;pasos=320
for trozo in limpio.split(";"):
    nombre, valor = trozo.split("=")
    print(nombre, "->", float(valor))
```

Primero se quitan los espacios de los extremos, todo a minúsculas, y se eliminan **todos** los espacios con `replace(" ", "")`. Queda un texto separado por `;`,
que se parte igual que antes. En el mundo real, limpiar datos "sucios" como este es una parte enorme del trabajo.
</details>
"""),

md(r"""## 15 · Posdata

Si algo no ha quedado claro, dime el **apartado** y la **frase exacta** y lo reescribo.

Hoy has aprendido a manejar texto como un profesional: cortarlo, buscarlo, transformarlo, convertirlo y darle formato, y has parseado un registro de entrenamiento.
En el **NB21** vamos a por las **colecciones**: las listas a fondo (con una trampa muy famosa que hay que conocer), las **tuplas**, los **conjuntos** y, sobre todo,
los **diccionarios**, la estructura con la que se guardan todas las configuraciones de un entrenamiento.
"""),

]

if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "notebooks", "NB20_python_texto.ipynb")
    build(out, cells, title="NB20 · Python de verdad (1): el texto a fondo")
