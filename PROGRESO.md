# Progreso

## ▶ PARA RETOMAR (sesión guardada 2026-09-30)
- Hechos y subidos a GitHub: **NB00, NB01, NB02** (Parte 0, conceptuales, 0 código, EXIT 0).
- **Siguiente: NB03 · La mente y el bucle** (observación, decisión, acción = la política).
  Mismo estilo: conceptual, cero código, nivel "14 años", analogías + diagramas ASCII,
  preguntas resueltas. Luego NB04 (recompensa y sus trampas) y NB05 (primer código, microdosis).
- Para continuar, dile a Claude: **«sigamos con robótica, NB03»**.
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
- **NB03 · La mente y el bucle: observación, decisión, acción** (cero código).  ← SIGUIENTE
- **NB04 · Premios y castigos: la recompensa y sus trampas** (cero código).
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
