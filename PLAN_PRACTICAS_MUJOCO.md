# Plan · Práctica en MuJoCo en CADA notebook (2026-10-07)

**Petición de Gregori:** lo más importante del curso es aprender a **simular y entrenar en MuJoCo**
(el simulador de Google DeepMind) desde el primer día. Cada notebook cierra con un apartado
**«🛠 Práctica en MuJoCo»** que usa lo explicado en ese notebook, a su nivel. Teoría y práctica juntas.

## Reglas
- Va **después de los Ejercicios y antes de la Posdata** (la Posdata sigue cerrando).
- **NB00–NB04b (aún no sabes Python):** el código viene **ya escrito**. Tu trabajo: ejecutar, mirar,
  y cambiar **un número** donde se indica. Cada celda se explica en castellano llano, sin exigir entenderla.
- **Desde NB05:** escribes tú cada vez más. Microdosis: una idea por celda. Retos con solución en `<details>`.
- Herramienta común: **`notebooks/taller.py`** (funciones `cargar`, `foto`, `video`, `simular`...). Al principio
  es una caja negra; en el **NB23 (funciones)** y **NB24 (clases)** la abres y la reescribes tú.
- Modelos: el **Humanoid** de Gymnasium/DeepMind (el mismo que el NB00), modelos MJCF pequeños escritos en el
  propio notebook (pelota, péndulo, palo de escoba) y, más adelante, el Zancudo.
- No se renumera nada: los notebooks de MuJoCo a fondo (NB42, NB45–NB50) pasan a ser **consolidación** de
  lo que ya habrás tocado en las prácticas.

## Itinerario (la columna «MuJoCo» es lo que dominas al acabar cada práctica)

| NB | Tema del NB | Práctica en MuJoCo | MuJoCo que aprendes |
|---|---|---|---|
| 00 | Qué vamos a hacer | Cargar el humanoide, foto, verlo caer (GIF propio) | Qué es MuJoCo; modelo → simulación → imagen |
| 01 | El cuerpo | Contar piezas, articulaciones y motores del humanoide; foto de cada pieza | `nbody`, `njnt`, `nu`; cuerpos/juntas/actuadores |
| 02 | Mundo de mentira | Soltar una pelota; cambiar gravedad (Tierra/Luna/Júpiter) y el paso de tiempo | `timestep`, `gravity`, `mj_step` |
| 03 | Mente y bucle | Humanoide quieto vs. al azar vs. «tenso»: el bucle percibir-decidir-actuar | `data.ctrl`, `qpos`, bucle de control |
| 03b | Números a fondo | Unidades de MuJoCo: metros, kg, s, radianes; leer masas y altura | `body_mass`, radianes en `qpos` |
| 04 | Recompensa | Puntuar «seguir de pie» durante una caída; la trampa de premiar altura | Medir con `xpos` de la cabeza |
| 04b | Letras y ecuaciones | Caída libre: fórmula ½gt² vs. MuJoCo | Verificar la física con una ecuación |
| 05b | Ordenador y terminal | Lanzar una simulación desde la terminal; medir pasos/segundo | `python script.py`, velocidad del simulador |
| 05 | Primer contacto | Tu primera línea: `print` de datos del modelo | Leer el modelo tú mismo |
| 06 | Variables | Guardar gravedad/masa en variables y cambiarlas | Modificar `model.opt` y `body_mass` |
| 07 | Bucles | Escribir **tu** bucle de simulación | `for … mj_step` |
| 08 | if | Detectar la caída y parar | Condición de fin de episodio |
| 09 | Listas | Registrar la altura en una lista y dibujarla | Trayectorias |
| 10 | Funciones | `def caida(gravedad)` → tiempo hasta caer | Experimentos reproducibles |
| 11b | Python que vas a ver | Leer un script MuJoCo real línea a línea | Lectura de código de MuJoCo |
| 11 | Palo de escoba | Construir el palo de escoba en MJCF y controlarlo | Primer MJCF propio (carro + palo) |
| 12 | Vectores | Posiciones 3D (`xpos`), gravedad como vector | Vectores de MuJoCo |
| 13 | Producto escalar | ¿Cuánto se inclina el torso? (eje z del torso · vertical) | `xmat`, inclinación |
| 14 | Matrices | La matriz de giro del torso; aplicar giros | `xmat` como rotación |
| 15b | Exp/log | Péndulo con rozamiento: decaimiento exponencial | `damping` |
| 15 | NumPy | Todo en arrays: registro vectorizado, foto = array | `qpos`/imagen como `ndarray` |
| 16 | Pendientes | Velocidad = pendiente de la posición (comparar con `qvel`) | `qvel` |
| 17 | Gradiente | Afinar un parámetro (lanzamiento/ganancia) por ascenso de gradiente | Optimizar sobre la simulación |
| 17b | Reglas | Energía del péndulo; derivada comprobada en MuJoCo | `mj_energy` |
| 18 | Imitar | Copiar a un «experto» que equilibra el palo de escoba | Datos de demostraciones |
| 19 | Redes | Red a mano que equilibra el palo de escoba | Política neuronal en MuJoCo |
| 20 | Texto | Generar MJCF con f-strings (robots de tamaño variable) | MJCF como texto |
| 21 | Colecciones | Diccionarios nombre→id; recorrer juntas | `mj_name2id`, `model.joint()` |
| 22 | Errores | XML roto, simulación que explota (NaN), `try/except` | Errores de MuJoCo |
| 23 | Funciones | Abrir y reescribir `taller.py` | Utilidades propias |
| 24 | Clases | Clase `Simulacion` | Envolver `model`/`data` |
| 25 | Herencia + Gymnasium | Tu entorno Gymnasium sobre tu palo de escoba MuJoCo | `gym.Env` + MuJoCo |
| 26 | Ficheros/terminal | Guardar el MJCF, cargar de fichero, script que hace vídeo | `from_xml_path` |
| 27 | NumPy/tests/git | Tests de la simulación (conservación, determinismo) | Verificar un simulador |
| 28 | Probabilidad | Estados iniciales aleatorios; distribución del tiempo de caída | Aleatoriedad/semillas |
| 28b | Mates del gradiente | Log-probabilidades de una política sobre el palo MuJoCo | Política estocástica |
| 29 | REINFORCE | REINFORCE en tu palo de escoba MuJoCo | **Primer entrenamiento en MuJoCo** |
| 30 | Crítico | Línea base y descuento en el mismo entorno | Varianza |
| 31 | PyTorch | Política en PyTorch controlando MuJoCo | Torch + MuJoCo |
| 32 | Actor-crítico | A2C en tu entorno | |
| 33 | PPO | PPO desde cero en tu entorno | |
| 34–53 | (ya usan MuJoCo) | Se añade una «🛠 Práctica en MuJoCo» final donde falte | — |

## Estado
- [ ] NB00 … (se va marcando aquí)
