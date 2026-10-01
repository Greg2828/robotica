# Progreso

## ▶ PARA RETOMAR (sesión 2026-10-01)
- Hechos y subidos a GitHub: **NB00, NB01, NB02, NB03** (Parte 0, conceptuales, 0 código, EXIT 0).
- 2026-10-01: NB00–NB02 **revisados y ampliados** con datos verificados del Humanoid-v5
  (17 motores reales sin tobillos, 3 ms/paso, 67 decisiones/s, cae en ~0,33 s al azar) y
  conceptos que faltaban (subactuación, centro de masas, sensores, inercia, pelota a mano,
  aleatorizar el mundo). Cada NB cierra con **Resumen + Palabras nuevas de hoy**.
- **Siguiente: NB04 · Premios y castigos: la recompensa y sus trampas** (recompensa real del
  Humanoid-v5: +5 por seguir de pie, +1,25 × velocidad hacia delante, −0,1 × esfuerzo² de
  motores; trampas/reward hacking). Luego NB05 (primer código, microdosis).
- Para continuar, dile a Claude: **«sigamos con robótica, NB04»**.
- Rutina activa: tras cada notebook verificado → commit + push (repo privado Greg2828/robotica).

## ⚠ GIRO DE ENFOQUE (2026-09-30)
Gregori leyó los NB00–NB01 antiguos y le parecieron **demasiado código, demasiado pronto**:
no eran de nivel cero. Norma nueva del curso:
- **Teoría, contexto, mecánicas y herramientas PRIMERO.** El código llega después y en
  **microdosis** (una idea nueva por celda, gota a gota, empezando por lo más simple).
- **Cero conocimientos supuestos**: Python, matemáticas y física se explican también desde
  cero. La robótica es el contexto/objetivo.
- **Nivel de referencia: alguien de 14 años.** Da igual que los notebooks se alarguen mucho.
- Los 4 notebooks antiguos están **archivados** en `_archivo/`. Secuencia nueva desde cero.

## Secuencia nueva — Parte 0 · El terreno (todo conceptual primero, cero código)
- **NB00 · ¿Qué vamos a hacer y por qué es difícil?** ✅ HECHO (EXIT 0, 14 celdas, 0 código):
  el sueño, andar=inestable (palo de escoba), aprender probando, GIF del robot al azar como
  resultado ya hecho (imagen markdown), mapa de 6 piezas, por qué mundo de mentira, plan.
- **NB01 · El cuerpo del robot** ✅ HECHO (EXIT 0, 13 celdas, 0 código): piezas rígidas=huesos,
  articulaciones bisagra/rótula, grados de libertad (=nº de mandos, más=más ágil pero más
  difícil), motores=músculos + par de giro, anatomía del humanoide (~17 motores), plano de
  montaje tipo IKEA. Todo con analogías con el cuerpo humano y diagramas ASCII.
- **NB02 · El mundo de mentira: qué es un simulador** ✅ HECHO (EXIT 0, 12 celdas, 0 código):
  qué es un simulador (videojuego preciso), física desde cero (fuerza/gravedad/choque/
  rozamiento), el tiempo a saltitos = paso de simulación (analogía flip-book/cine), qué pasa en
  un pasito, el bucle con el simulador dentro, ventajas, MuJoCo (solo nombre), reality gap.
- **NB03 · La mente y el bucle** ✅ HECHO (EXIT 0, 19 celdas, 0 código): política = caja que
  convierte números en números; observación (45 números: postura+velocidades; problema de la
  foto; sin posición x,y; observación ≠ estado, niebla); acción (17 números en ±0,4, números
  negativos desde cero con recta numérica); 3 maneras: reglas a mano (termostato, escoba,
  control clásico) / tabla gigante (maldición de la dimensionalidad, 10^45 vs átomos de la
  Tierra) / máquina con ruedecillas = parámetros (red neuronal, solo el nombre); agente vs
  entorno (el cuerpo es entorno); paso y episodio (cae si torso < 1 m, o 1000 decisiones);
  explorar vs aprovechar (restaurantes).
- **NB04 · Premios y castigos: la recompensa y sus trampas** (cero código).  ← SIGUIENTE
- **NB05 · Tu primer contacto con el ordenador** → aquí empieza `print("hola")` y la
  microdosis de código, gota a gota.
- (luego) Python desde cero, matemáticas desde cero, física desde cero, siempre al servicio
  de la robótica.

## Formato
- Notebooks que Gregori lee a su ritmo; ejercicios **resueltos inline** bajo `<details>`.
- Tema oscuro vía `build_parts/nbbuild.py` (`md()/code()/build()`, kernel `robotica`).
- El robot se muestra como GIF/imagen ya generada (markdown `![](assets/...)`), sin pedir
  ejecutar código en los notebooks conceptuales.
- Verificar cada notebook con nbconvert `--execute` (los conceptuales pasan trivial: 0 código).

## GitHub
- Repo **privado**: https://github.com/Greg2828/robotica (cuenta Greg2828), rama `main`.
- `venv/` y cachés van en `.gitignore` (no se suben). `_archivo/` sí se sube.
- **Rutina:** tras terminar y verificar cada notebook (EXIT 0), `git add -A && git commit && git push`
  para que Gregori pueda leerlo desde otro dispositivo. Los .ipynb se renderizan en la web de GitHub.

## Entorno verificado
- Raspberry Pi 5, aarch64, Python 3.13, venv en `robotica/venv`, kernel Jupyter `robotica`.
- MuJoCo 3.14 renderiza sin pantalla con `MUJOCO_GL=egl`. Assets reutilizables en
  `notebooks/assets/` (p.ej. `nb00_humanoide_azar.gif`).

## Historial
| Fecha | Hito | Nota |
|---|---|---|
| 2026-09-29 | NB00–NB03 antiguos (Fase 0) | Archivados en `_archivo/` tras el giro de enfoque |
| 2026-09-30 | Giro a "nivel cero de verdad" + NB00 nuevo | Teoría primero, código en microdosis |
| 2026-10-01 | NB00–NB02 ampliados + NB03 | Datos verificados; subactuación, CoM, sensores, inercia |
