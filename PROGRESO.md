# Progreso

## ▶ PARA RETOMAR (sesión 2026-10-01)
- Hechos y subidos a GitHub: **NB00, NB01, NB02, NB03** (Parte 0, conceptuales, 0 código, EXIT 0).
- 2026-10-01: NB00–NB02 **revisados y ampliados** con datos verificados del Humanoid-v5
  (17 motores reales sin tobillos, 3 ms/paso, 67 decisiones/s, cae en ~0,33 s al azar) y
  conceptos que faltaban (subactuación, centro de masas, sensores, inercia, pelota a mano,
  aleatorizar el mundo). Cada NB cierra con **Resumen + Palabras nuevas de hoy**.
- **NB04 HECHO** → **✅ PARTE 0 COMPLETA (NB00–NB04)**.
- **PARTE 1 en marcha:** NB05 (primer código), NB06 (variables), NB07 (bucles) HECHOS, EXIT 0.
  `nbbuild.py` tiene ahora `code_err()` (etiqueta `raises-exception`) para enseñar errores REALES
  sin romper la verificación. OJO: en Jupyter los NameError muestran `---->` (no `^^^^`) y no
  sale el "Did you mean"; verificar siempre el texto contra la salida real.
- NB08 (if), NB09 (listas), NB10 (funciones), NB11 (PROYECTO palo de escoba) HECHOS → **✅ PARTE 1 COMPLETA
  (NB05–NB11)**. NB11 = entorno de RL desde cero (ficha, random+seed, paso/episodio/evaluar, 4 políticas,
  diagnóstico por trayectoria, búsqueda aleatoria de 2 ruedecillas, generalización en semillas nuevas).
- **Siguiente: PARTE 2 · Matemáticas y herramientas para robots** (NB12+). Propuesta: NB12 flechas (vectores)
  desde cero con la observación/acción como vectores; luego NumPy (listas a toda velocidad), pendientes
  (derivadas intuitivas → "hacia dónde girar cada ruedecilla"), descenso por pendiente, y de ahí redes
  neuronales. Mismo método: teoría primero, microdosis, datos verificados.
- Para continuar, dile a Claude: **«sigamos con robótica, NB12»**.
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
- **NB04 · Premios y castigos: la recompensa y sus trampas** ✅ HECHO (EXIT 0, 21 celdas, 0 código):
  recompensa = número por paso, dice qué no cómo; retorno (+pizca de descuento); asignación del
  mérito (fútbol); escasa vs densa (frío/caliente, reward shaping); recompensa REAL Humanoid-v5
  (+5 de pie, +1,25×vel. del CdM, −0,1×Σacción², −golpes ≤10) con el cuadrado desde cero;
  cuentas medidas: azar ~98 (21 pasos), muñeco de trapo ~198 (40 pasos) — no hacer nada > azar;
  quieto 5000 vs andar ~6150 → óptimo local (montaña con niebla); sin +5 → se tira en plancha;
  reward hacking (Midas, barco CoastRunners, Tetris pausa, Lego volteado, criaturas que caen,
  fallos del simulador), ley de Goodhart, defensas del profesional; mapa de las 4 piezas.
- **── PARTE 1 · Primeros pasos con el ordenador ──**
- **NB05 · Tu primer contacto con el ordenador** ✅ (EXIT 0, 42 celdas, 11 de código): ordenador
  obediente/literal (cocinero que no sabe cocinar), programa=receta, Python, notebook/celdas/kernel,
  cómo abrir (GitHub o `jupyter lab` en la Pi, Mayúsculas+Enter); `print("hola")` desmontado;
  texto vs número; 3 errores REALES (NameError×2, SyntaxError) y cómo leerlos; comentarios `#`;
  trampa de la coma decimal `print(1,25)`; recompensa del NB04 = 7.4.
- **NB06 · Cajas con nombre: variables y números** ✅ (EXIT 0, 72 celdas, 25 de código): caja con
  etiqueta, `=` es "guarda", reescribir, memoria del kernel/orden, NameError explicado, reglas de
  nombres, int/float, `/` da decimal, `**`, ruido de decimales + `round`, orden de operaciones,
  trampa `-0.4 ** 2`, `x = x + 1`; programas: recompensa con nombres (7.4 → 4.9 quieto), esfuerzo
  de 3 motores (0.33), pelota 3 pasitos copiando celdas (→ motiva bucles).
- **NB07 · Repetir sin cansarse: el bucle for** ✅ (EXIT 0, 48 celdas, 15 de código): for/range,
  cuerpo y sangría (IndentationError real), contar desde 0, range(inicio, fin), acumulador
  (retorno robot quieto 5000), Gauss 5050, pelota con bucle (tabla NB02 con ruido 0.9999…),
  MEDIDO: paso 0.1→0.5 m, 0.01→0.725, 0.001→0.7475 (exacto 0.75): error ÷10 por paso ÷10.
- **NB08 · Tomar decisiones: `if`** ✅ (44 celdas, 13 código): comparaciones/bool, = vs == (SyntaxError
  real), if/else/elif, and/or, +5 del humanoide como if, termostato (1.ª política, 0,5/0,25 sin ruido), pelota
  que REBOTA (coef. restitución 0,8: botes en pasos 63/163/242), break = fin de episodio (terminado/truncado).
- **NB09 · Listas** ✅ (63 celdas, 20 código): índice desde 0, IndexError, -1, cambiar, for sobre lista,
  esfuerzo de 17 motores (0,67), sum/max/min/media, append (método), trayectoria de la pelota grabada (300
  fotos, bote paso 63 = índice 62, rebota a 1,24 m, 89 fotos > 1 m), porciones, listas en paralelo.
- **NB10 · Funciones** ✅ (63 celdas, 23 código): def/llamar, parámetros/argumentos, return vs print, None,
  TypeError, recompensa y esfuerzo como funciones, variables locales, devolver 2 valores (paso_pelota = step),
  POLÍTICA = función, ENTORNO = función, simular(politica) intercambiable, termostatos comparados (23 min/19,95
  vs 21 min/18,99) → diseño de recompensa.
- **NB11 · PROYECTO palo de escoba** ✅ (63 celdas, 22 código): ficha del entorno (obs 2, acción 1 ±40,
  recompensa 1−(i/30)², cae >30°, 500 pasos), import random/uniform/seed, constantes MAYÚSCULAS; nada 44,8,
  azar 43,2, solo inclinación 296 (oscila: problema de la foto), incl+vel 499,9; ruedecillas; búsqueda
  aleatoria 20 candidatos → 499,9 y generaliza a semillas 100-109; límites: motor débil (15) nada lo salva,
  ruedecilla < 10 pierde contra la gravedad.
- **── PARTE 2 · Matemáticas y herramientas ──**  ← SIGUIENTE (NB12)
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
| 2026-10-01 | NB08–NB11 → Parte 1 completa | Proyecto palo de escoba: 1.er RL desde cero |
| 2026-10-01 | NB05–NB07 (Parte 1: print, variables, bucles) | Errores reales con code_err |
| 2026-10-01 | NB04 → Parte 0 completa | Recompensa real del humanoide medida |
| 2026-10-01 | NB00–NB02 ampliados + NB03 | Datos verificados; subactuación, CoM, sensores, inercia |
