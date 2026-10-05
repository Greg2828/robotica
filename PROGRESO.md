# Progreso

## ▶ PARA RETOMAR (actualizado 2026-10-06)
- **Hechos, verificados (EXIT 0) y subidos: NB00–NB50 + puente P1–P7 + 10 lecciones de relleno** (todo el
  Bloque A de simulación a fondo incluido).
- **Relleno de huecos tras la auditoría del 2026-10-04 (8 revisores leyeron NB00-NB50):** checklist en
  `PLAN_HUECOS.md`. Los 10 notebooks nuevos están HECHOS (las "b" se leen justo después de su número):
  NB03b números · NB04b letras y ecuaciones · NB05b ordenador por dentro y terminal · NB11b Python que vas a ver ·
  NB15b exponencial y logaritmo · NB17b reglas de derivación · **NB28b matemáticas del gradiente de la política** ·
  **NB38b energía, trabajo y potencia** · **NB39b muelles, amortiguadores y ecuaciones diferenciales** ·
  **NB44p7 álgebra lineal para robótica** (último del puente).
- Erratas, notas breves y repaso editorial del orden nuevo (puente P1-P6 sin dar por sabido NB45-NB50;
  NB45-NB50 citando el puente como repaso): HECHOS. **Plan de huecos COMPLETO.**
- **Orden de lectura:** … NB44 → P1 … P7 → NB45 … NB50 → NB51 → NB52 → (siguiente) NB53.
- **NB51 · Planificar pasos ✅ (2026-10-06, 102 celdas, 41 de código, EXIT 0)**: LIPM resuelto a mano (cosh/sinh)
  vs Euler; DCM ξ = x + v/ω (huye del pie) y CdM que lo persigue; energía orbital = producto ξ·ζ; capturabilidad
  con N pasos (Zancudo: 0,19 / 0,61 / … límite 0,82 m/s); marcha periódica; plan de pisadas 2D + plan del DCM
  hacia atrás (Englsberger) con fase de arranque; pie en el aire (quíntico + bulto 64σ³(1−σ)³); LIPM en MuJoCo
  (bola + xfrc_applied): bucle abierto diverge (3 cm / ~300 m con empujón), realimentación del DCM k=3 → <1 mm,
  ZMP se aparta 9,7 cm. Python: NumPy vectorizado (ufuncs, timeit, broadcasting, máscaras, searchsorted,
  numpy.typing) + matplotlib OO (subplots, subplot_mosaic, colormaps, pcolormesh, patches, log, savefig).
  Figura guardada en notebooks/assets/nb51_plan_de_marcha.png.
- **NB52 · Zancudo anda sin RL ✅ (2026-10-06, 100 celdas, 41 de código, EXIT 0, ~1 min)**: ZMP con apoyo doble,
  carrito sobre la mesa, LQR/Riccati por iteración (sin SciPy), vista previa de Kajita (horizonte 1,6 s; con 0,1 s
  error 60 cm), IK analítica de la pierna (ley del coseno) + IK del CdM por la secante, servos: prealimentación de
  velocidad ctrl = q + (kv/kp)·q̇, kp=3000/kv=90 (kv=300 → temblor de 2,5 Hz quieto). Empujones: clásico en bucle
  abierto ~0,17-0,2 m/s (= tobillo del NB51); paso de captura de pie 0,30 → 0,59 m/s; más pasos a veces empeora;
  RL `completa` del NB44 aguanta siempre 0,85 m/s y a menudo 1,3-1,7. Librería **notebooks/andar/** (fuente única en
  build_parts/nb52_andar/, escrita con %%writefile): plan.py, cinematica.py, control.py (PasoDeCaptura, Enum),
  logging. GIFs nb52_zancudo_clasico.gif / nb52_paso_de_captura.gif. **→ Bloque B COMPLETO.**
- **Siguiente: NB53 · Zancudo 3D (MjSpec)**: cadera 3 GDL, tobillo 2 GDL, equilibrio lateral; Py: dataclasses +
  YAML. Para continuar, dile a Claude: **«sigamos con robótica»**.
- Rutina: tras cada notebook verificado → commit + push (repo GitHub público Greg2828/robotica).

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
- **── PARTE 2 · Matemáticas y herramientas ──**
- **NB12 · Vectores** ✅ (50 celdas, 17 código, 6 dibujos matplotlib): Hundir la flota/plano cartesiano, componentes, sumar
  (odometría), escalar, restar (B−A), Pitágoras+raíz (** 0.5), 3D/45D (distancia entre observaciones 0,057 vs 2,24), robot hacia
  la meta con viento (25 pasos, dibujado).
- **NB13 · Producto escalar** ✅ (39 celdas, 12 código): media ponderada → "pesos", política del palo = pesos·obs (política lineal),
  geometría (+/0/−), unitario/normalizar/proyección, premio por avanzar = vel·(1,0,0), a·a = longitud², NEURONA = pesos·x + sesgo,
  perceptrón (termostato = neurona), detector de caídas que anticipa (peso 0,3 en velocidad).
- **NB14 · Matrices** ✅ (43 celdas, 15 código): Segway 2×3 (giro con signos opuestos), lista de listas, bucle anidado, matriz×vector,
  regla de tamaños (IndexError), capa = M·x + b, humanoide 17×45+17 = 782 (completa 5.933), recortar, 0,5**782 = 3,9e-236
  (notación científica), capas en fila = red (avance).
- **NB15 · NumPy + humanoide real** ✅ (76 celdas, 29 código): arrays, shape, elemento a elemento vs listas (concatena/repite), @,
  ValueError de formas, default_rng/zeros/clip, cronometraje (~50-120× en la Pi), Gymnasium reset/step = reiniciar/paso del NB11,
  obs (348,) con obs[0]=1,39 altura, recompensa 1.er paso 5,002; política lineal: W=0 → 198,6 (= muñeco de trapo NB04), W azar ~58,
  mejor de 20 al azar 141,7 < 198,6 → hacen falta pendientes. E5: todo +0,4 → ~237 (tensar ayuda), todo −0,4 → ~45.
- **NB16 · Pendientes** ✅ (36 celdas, 10 código): función f(x)+gráfica, rampa, velocidad = pendiente de la posición, zoom
  (curva → recta), (f(x+h)−f(x))/h → 6 en x², a los dos lados, h=1e-12 empeora vs 1e-6, derivada de x² = 2x por tabla;
  montaña del palo con BATERÍA (coste 0,001, d=8): +27,5 en 12, ≈0 en 23,5 (cima ~462), −0,63 en 40.
- **NB17 · Ascenso por gradiente** ✅ (31 celdas, 10 código): x += tasa·pendiente; colina 10−(x−3)²: tasas 0,01/0,1/0,5/
  0,9/1,1 (lento/bien/de un salto/oscila/explota); 1 ruedecilla 12→25,8→~24,7; gradiente 2D = flecha; mapa contourf con
  camino (12,2) 416 → (22,6; 6,2) ~463; óptimo local (dos colinas, valle entre 3 y 3,5); coste 2N evaluaciones/paso.
- **NB18 · Aprender imitando (supervisado)** ✅ (37 celdas, 10 código): 300 ejemplos del maestro −30i−8v; ECM/pérdida
  (305,6 → 0); valle; REGLA DE LA CADENA (engranajes) → 2·media(error×entrada) = numérica (14,7596); tasa 0,2 →
  (−30; −8; 0), 0,25 aprende, 0,3 explota (6e18); alumno juega 499,9 (a medio aprender 499,8); maestro ±10 →
  (−29,7; −8,0); desplazamiento de distribución; imitación en humanoides.
- **NB19 · Redes neuronales** ✅ (30 celdas, 8 código): maestro que satura (clip −30i a ±40); lineal atascada 81,5;
  capas lineales apiladas = recta; ReLU = codo; 2 codos a mano = exacto; red 1→8→1 con retropropagación a mano (pendiente
  ReLU 0/1), tasa 0,003, 5000 pasos → 0; tasa 0,01 → atasco ~11 (óptimo local, NO neuronas muertas: verificado);
  aproximación universal; red de humanoide 348→256→256→17 = 159.505 pesos.
- **── PARTE 3 · PYTHON DE VERDAD ──**
- **NB20 · Texto** ✅ (74 celdas, 29 código): índices/porciones, inmutables, métodos, split/join, conversiones (ValueError),
  escapes, f-strings y formato (:.2f :, :.1% :+ :>8 :05d), proyecto parsear un log → informe alineado.
- **NB21 · Colecciones** ✅ (80/31): tuplas/desempaquetar, listas a fondo, sort vs sorted, TRAMPA DEL ALIAS (copy, is),
  enumerate/zip, comprensiones, diccionarios (KeyError, get, items, anidados, contar), info REAL del humanoide (ingredientes
  de la recompensa), conjuntos, any/all, key=, // y %, proyecto cuaderno de experimentos.
- **NB22 · Flujo, errores y depuración** ✅ (57/18): while (pelota 63 pasos), límite de seguridad, continue, for-else, pass,
  match, verdad/falsedad, excepciones y trazas (de abajo arriba), try/except/else/finally, raise (fallar pronto), inf/nan +
  math.isfinite (vigilante: explota en el paso 16), assert, depurar (f"{x=}", %debug/breakpoint/pdb, catálogo de bichos).
- **NB23 · Funciones a fondo** ✅ (57/21): defaults, por nombre, trampa del default mutable, *args/**kwargs, desempaquetar al
  llamar, ámbito (UnboundLocalError), lambda, CIERRES (fábrica de políticas), decoradores (@cronometro), recursión,
  iteradores/StopIteration, generadores (lotes; 8,4 MB vs 200 B), docstrings, type hints.
- **NB24 · Clases (I)** ✅ (54/18): clase/objeto, __init__/self, métodos, __repr__, atributos de clase, _privado, @property,
  PaloDeEscoba con reset/step estilo Gymnasium + random.Random propio, PoliticaLineal con __call__ (como PyTorch), mismo
  bucle → 44,8/296,0/499,9; @dataclass + field(default_factory).
- **NB25 · Herencia + entorno Gymnasium** ✅ (43/14): herencia, super(), polimorfismo, ABC/@abstractmethod, Vector con métodos
  especiales (así funciona NumPy), composición; PaloDeEscobaEnv(gym.Env) con spaces.Box, acción normalizada [-1,1]×40,
  check_env (avisos explicados), gym.register + gym.make (envoltorios TimeLimit...): nada 44,6 / solo incl 353,4 / a mano
  499,9; nn.Module explicado.
- **NB26 · Ficheros, módulos, scripts, terminal** ✅ (72/27): pathlib, open/with/modos, CSV (todo texto), JSON, np.save, pickle
  (peligro), módulo palo.py + sys.path + reload, script con argparse + subprocess/sys.executable, terminal (!), venv/pip/
  requirements, logging, Counter/defaultdict/datetime/itertools.product/statistics, proyecto barrido guardado y releído.
- **NB27 · NumPy a fondo, tests y Git** ✅ (76/29): dtype float32, reshape/-1/.T, índices 2D, máscaras/np.where/argsort, EJES,
  BROADCASTING (normalizar observaciones), stack, VISTAS vs copias; 1.000 palos vectorizados (solo incl ~63 % caídas; 10-20×
  más rápido); pytest (test_palo.py, caza el fallo gravedad 10→1); Git real en repo de juguete (init/add/commit/diff/
  switch -c/--decorate), .gitignore, historial del curso; PEP 8.
- **── PARTE 4 · APRENDIZAJE POR REFUERZO DE VERDAD ──**
- **NB28 · Probabilidad** ✅ (48 celdas, 16 código): frecuencia, grandes números (dado, dibujado), distribución (dos dados),
  valor esperado (producto escalar; el RL maximiza el retorno ESPERADO), varianza/σ (robots A y B), uniforme, histogramas,
  campana de Gauss (TCL, 68,4/95,5/99,7, fórmula con e/exp), error típico σ/√n (5 vs 100 episodios) e intervalo de confianza,
  política estocástica (σ: aguanta hasta 50, se desploma en 100; cruce de 400 entre σ 60 y 70), logaritmo y log-prob normal.
- **NB29 · REINFORCE** ✅ (38/11): (a−μ)/σ² comprobada; ×obs por regla de la cadena; retorno desde cada paso γ=0,99 hacia
  atrás; puro NO aprende (~30-45); línea base media → 499 (semilla 0 en la it. 53; 5 semillas 47-95); aprendida (−15,7; −20,1)
  no se cae en 1.000. E5: σ=1 aprende en 6 it (pasos 25× mayores); E7 línea base global inestable (desaprende).
- **NB30 · Ruido, crítico, descuento** ✅ (27/8, ~2 min): ruido medido (sin base desv 34/44 y media de signo erróneo; con base
  9,5/20); normalizar ventajas; crítico lineal con rasgos [1,i²,v²,i·v,t/500] por lstsq — honesto: es tosco (predice −231,
  ordena mal volviendo/cayendo); crítico+normalizar el mejor ([13,17,17,66,26] vs media [53,79,95,60,47]); γ 0,9 no aprende,
  0,99 bien, 1,0 algo peor.
- **NB31 · PyTorch** ✅ (44/16): tensores, autograd (6 en x²; 14,7596 del NB18), grafo, acumulación/zero_grad, no_grad,
  nn.Linear/ReLU/Sequential/Module (25 params), SGD vs Adam — HONESTO: con 8 neuronas Adam se atasca (29,9) y SGD llega
  (0,71); con 32, SGD 4/4 y Adam a veces; Normal.log_prob → gradiente = fórmula NB29; state_dict + weights_only; .to(cuda).
- **NB32 · Actor-crítico** ✅ (46/18, ~4 min): jugador/comentarista; pérdida truco −log_prob×ventaja (= dirección NB29, comprobado
  −0,48/−0,24); escalar entradas; log σ aprendible (0,25→0,20); DIFERENCIA TEMPORAL δ=r+γV'−V (GPS), ruido vs sesgo, reloj en el crítico;
  Actor 2→32 tanh→1 (130 params) + Crítico 3→64→1 (321); TD semilla 0 supera 490 en it. ~95 (42,6→499,6); actor satura ±40 hacia 3°;
  mapa del crítico (franja diagonal, máx ~100=1/(1−γ), esquinas negativas = extrapolación); examen en PaloDeEscoba-v0 499,6 0 caídas
  (aguanta viento ±60; falla desde ±80); TD [94,93,92,78] vs Montecarlo [None,116,100,109]; FRAGILIDAD (Adam+ventajas normalizadas;
  tasa 0,03 llega a 499 y se derrumba a ~60) → motivación de PPO.
- **NB33 · PPO desde cero** ✅ (32/11, ~3,5 min): desperdicio+fragilidad; épocas/minilotes (randperm); razón r=exp(Δlogp);
  recorte min(r·A, clip·A) con tabla de casos + dibujo; GAE λ (comprobado: λ=1 → G−V, λ=0 → δ con crítico al azar);
  PPO tasa 0,01, minilote 1024, 10 épocas: supera 490 en it. 54 (vs 78-94 del NB32), sin bajones, cambio |r−1| 2-30 %,
  r máx < 2, σ 0,25→0,18; SIN recorte: semillas 19/47/None, oscila 500↔200, termina 34-48, r máx 1.053-2.160, σ 0,03-0,05;
  examen viento ±80 0 caídas, ±100 3/20. Ejercicios medidos: λ=0 → 66, λ=1 → 376 (0,95 gana); ε=0,05 lento (90),
  ε=0,5 inestable (136, r 380); bonus de entropía sin recorte NO salva (49/122/31).
- **NB34 · Stable-Baselines3** ✅ (43/15, ~4 min; SB3 2.9.0 instalado): por qué bibliotecas + mapa (SB3/CleanRL/RSL-RL/Brax);
  check_env de SB3; DICCIONARIO NB33↔SB3 leído del modelo (n_steps 2048, batch 64, epochs 10, lr 3e-4, clip 0,2, σ inicial 1);
  make_vec_env (4 copias, autoreset, Monitor); policy 64-64 tanh separadas (8.835 params); inspect.getsource(PPO.train)
  muestra ratio/clamp/min = el NB33; palo aprendido en 49.152 pasos (NB33 propio: ~240.000); OJO learn() juega lotes
  completos (pedir múltiplos de 8.192); informe verbose=1 explicado (approx_kl, clip_fraction, explained_variance...);
  menos robusto al viento que el PPO propio; save/load .zip (pickle); **InvertedPendulum-v5 MuJoCo 1000/1000 en 65.536
  pasos + GIF assets/nb34_pendulo_ppo.gif**. Ejercicios medidos: σ0=0,25 → 51 a 50k (≈250k para aprender); estocástico
  929±164 vs 1000; Pendulum-v1 por defecto −1031 (no aprende → RL Zoo). Cifras SB3 varían un poco entre ejecuciones.
  SIGUIENTE: NB35 Hopper/Walker2d.
- **NB35 · Robots con patas** ✅ (39 celdas, EXIT 0, ~8 min de ejecución): Hopper-v5 (obs 11, 3 motores gear 200, 15,8 kg,
  dt 0,008) y Walker2d-v5 (obs 17, 6 motores gear 100, 23,7 kg); recompensa desmontada con info; trampa de sobrevivir
  (forward_reward_weight=0 → 999,8, 1000 pasos, x +0,06 m); VecNormalize (corto: sin 387 > con 301 → contado con honestidad,
  1 semilla no demuestra nada). Entrenamientos 1M con notebooks/entrenar_largo.py (4 en paralelo en la Pi, 68-91 min):
  Hopper defecto 3508±172 (mejor 3558), afinado más rápido pero inestable (acaba 2633); Walker2d defecto 696 (se lanza y cae,
  óptimo local), afinado 2500±1469 (pico 3741). Modelos en notebooks/modelos/ (Hopper defecto, Walker afinado). Examen 10 ep:
  Hopper 3559 / 969 pasos / 20,7 m / 2,67 m/s; Walker 3161 / 849 / 18,5 m / 2,73 m/s. E4 ctrl×100 → 3482 misma conducta;
  E5 sin normalizar 317; E6 healthy_reward=0 → se lanza en plancha (1,8 m). Checkpoints parciales en trabajo_nb35/.
  → **✅ PARTE 4 COMPLETA (NB28–NB35)**. SIGUIENTE: Parte 5 · La física del cuerpo.
- **── PARTE 5 · LA FÍSICA DEL CUERPO ──** (plan: NB36 ángulos/trigonometría/cinemática directa · NB37 fuerza, par y el péndulo
  de verdad (deducir el "10 × inclinación" del NB11) · NB38 centro de masas y equilibrio estático · NB39 equilibrio dinámico
  (péndulo invertido lineal, punto de captura, ZMP) · NB40 motores de verdad y control PD · NB41 sensores y ruido · NB42 MJCF:
  tu propio robot · NB43 proyecto bípedo propio).
- **NB36 · Ángulos y giros** ✅ (80 celdas, 30 de código, EXIT 0): grados/π/radianes (arco = r·θ), seno/coseno como sombras,
  trampa math.sin(90)=0,894, ondas, desde la vertical (L·sin, L·cos), Pitágoras, atan2 vs atan, cinemática directa de la
  pierna de Hopper (cadera 1,05; muslo 0,45; pierna 0,50; ángulos MuJoCo + = hacia delante) que coincide con MuJoCo
  (xanchor −0,6975/0,5213), paso con dos senos (desfase −1,5 = pie abajo yendo hacia atrás = bueno; +1,5 = al revés, E6).
- **NB37 · Fuerza, par y el péndulo de verdad** ✅ (57 celdas, 20 de código, EXIT 0): unidades SI, a = F/m, newton, peso
  (Hopper 155 N), fuerza normal, par = F·brazo·sin φ, par de la gravedad m·g·(L/2)·sin θ, inercia de giro (1.000 trocitos → 0,75
  = m·L²/3), α = (3g/2L)·sin θ (masa se cancela; escoba 9,8 vs lápiz 98,1), el "10" del NB11 = escoba de 1,47 m linealizada,
  caída 1,339 s (lineal 1,322) = MuJoCo 1,339 s exacto (péndulo MJCF from_xml_string), motor Hopper 200 N·m = 20 kg a 1 m,
  punto de no retorno (E6: 0,205 rad con motor −2).
- **NB38 · Centro de masas y equilibrio quieto** ✅ (46 celdas, 16 de código, EXIT 0): balancín/ley de la palanca, CdM = media
  ponderada (NumPy), CdM de Hopper con body_mass+xipos = subtree_com (x +0,022, altura 0,596), se mueve con la postura; base de
  apoyo (segmento / goma elástica); regla + por qué (suelo empuja, no tira); bloque MJCF freejoint: crítico 18,4°, 18° vuelve,
  19° vuelca; Hopper-estatua (jnt_stiffness 3000 + qpos_spring, apoyado a 0,0605): h 0/0,3 de pie, 0,6 (CdM 0,276) cae; límite
  real ~22 cm vs 26 geométrico → margen de seguridad; estático vs dinámico.
- **NB39 · Punto de captura y ZMP** ✅ (43 celdas, 13 de código, EXIT 0, sin MuJoCo): modelo (mapa≠territorio), LIPM por triángulos
  semejantes a = (g/z0)(x−p), z0 0,8 → ω 3,502; 3 empujones desde −0,3 (0,9 vuelve, 1,05 casi, 1,2 pasa); energía orbital
  (−0,294→−0,319 por error de Euler; dt/10 → −0,296); velocidad justa 1,051; punto de captura x+v/ω = 0,143 (±2 cm cae);
  tobillo vs paso (0,53 m/s con punta a 0,15); ZMP = x − (z0/g)ẍ (−0,082 para 1 m/s²), NB38 caso particular, ASIMO; andar
  pisando b antes de la captura: pasos 0,152/0,304/0,457 → 0,38/0,76/1,14 m/s; límites + relación con RL. E5: 1,5 m/s 2 pasos,
  2,5 → 4, 3 → no se salva.
- **NB40 · Motores y control PD** ✅ (42 celdas, 14 de código, EXIT 0): motor (rotor/estátor, par ∝ corriente), reductora N:1
  (0,5 N·m 3000 rpm 50:1 → 25 N·m 6,28 rad/s), holgura/inercia reflejada N²/retroimpulsable/cuasi-directos, límites (par,
  recta par-velocidad, calor); pierna simulada 2 kg 0,5 m: P oscila (máx ~1,48), PD Kd 0/1/3/10, error estacionario
  0,651/0,734/0,783 (Kp 20/50/200) → compensación de gravedad 0,800, saturación 2,5 N·m columpia; Hopper con PD en ctrl por
  mj_step: Kp 0/50 cae, 300/20 de pie (E5: 100 inclinado, 150+ recto); la estatua del NB38 era un PD; política→ángulos +
  PD en robots reales.
- **NB41 · Sensores y ruido** ✅ (54 celdas, 22 de código, EXIT 0): información privilegiada; codificador 4096 → 0,088°,
  velocidad por diferencias salta 0↔1,53 (derivar amplifica); ruido gaussiano, promediar → /√n (verificado), media móvil =
  retraso; IMU: acelerómetro (quieto 9,81 arriba, atan2) y giróscopo (sesgo → deriva); péndulo MJCF con site+accelerometer+
  gyro: quieto 0,2964 exacto, balanceándose el acel va en contrafase; errores acel 0,237 / giro 0,173 / complementario 0,061
  con peso 0,999 (tiempo de corrección paso/(1−peso) = 1 s; 0,98 da 0,222 aquí porque mide a 1 kHz); Kalman nombrado;
  contacto Hopper con PD 96+59,2 = 155,2 N; retraso: Kp200 ok 10 ms, oscila 20, explota 30; Kp50 aguanta 30; política NB35
  con ruido 3559/2915/798/318 (0/0,01/0,05/0,1), solo en velocidades aguanta (3446/3403/2377); remedios (ruido, DR,
  profesor-alumno).
- **NB42 · MJCF: tu propio robot** ✅ (49 celdas, 16 de código, EXIT 0): XML (etiquetas/atributos/árbol), secciones MJCF, caja
  que cae (8 kg densidad agua), posiciones relativas, tipos de geom, joints (axis 0 -1 0 = + hacia delante, range en radianes
  con compiler), raíz plana 3 joints; pierna() y motores() con f-strings → **Zancudo** (notebooks/robots/zancudo.xml: 8 bodies,
  9 joints, 6 position kp300 kv20 forcerange ±150, IMU; 23,6 kg; CdM 0,783); error real 'unknown transmission target';
  de pie con ctrl 0; empujón 0,05 s (caída = torso baja >30 cm): 180 N aguanta, 200 cae (captura ~12 cm); torso 20 kg
  aguanta 200 (cae 250); pies −0,16..0,24 aguanta 300 (cae 350); solo por delante → cae de espaldas al rebotar; agachado
  aguanta 200 resbalando 0,29 m. SIGUIENTE: NB43 entorno Gymnasium de Zancudo + PPO para andar.
- **NB43 · Zancudo aprende a andar** ✅ (42 celdas, 15 de código, EXIT 0): las 4 decisiones (obs 18 medibles + reloj de fase
  0,8 s; acción = postura base + amplitud × a a 50 Hz; recompensa avance+vida−0,01·a²; caída cadera<0,55 o |incl|>0,8; 1000 pasos),
  zancudo_env.py leído con inspect, check_env. Referencias: quieto 832,6 (se cae en 2/10: semillas 0 y 2), azar ~57. Corto en vivo
  106k: 739,8, x=−1,45 (trampa de sobrevivir). Largos (entrenar_zancudo.py): defecto sube a 5.435; los 3 afinado COLAPSAN. Campeón
  5.453, 0 caídas, 89,7 m = 4,49 m/s (corre a saltos). Empujones 200 N 5/5, 300 N 3-4/5. Ruido apenas afecta (ángulos+PD filtran).
  Ejercicios resueltos; E5 (sin reloj, 300k): 3.278 vs 2.854 con reloj → el reloj no ayudaba sin recompensa que lo use.
  → **✅ PARTE 5 COMPLETA (NB36–NB43)**.
- **NB44 · Moldear la recompensa** ✅ (49 celdas, 19 de código, EXIT 0) — abre la Parte 6. zancudo_moldeado.py (campana vel 1 m/s,
  recto, vida 0,2, vuelo, pie>15 cm, suavidad). Ablación 1M (completa/sin_vuelo/sin_pie_alto/lento; reanudadas tras reinicio de la
  Pi con `seguir`): todas a la velocidad pedida; sin_vuelo 18→40 % aire; sin_pie_alto pie 0,79 m y tirones ×4; lento atascado
  ~870 = quieto cobra e⁻¹ (ancho de campana). DESCUBRIMIENTO: todas GALOPAN (izq. siempre ~1 m detrás, arrastrada 0,85 m/s).
  zancudo_alterno.py: ZancudoAlterno (alternar apoyos con el reloj) → galope con ritmo + vuelve a levantar el pie (términos se
  pelean); ZancudoZancada (campana sobre separación de pies −0,2·cos(fase)) → se cruzan 25 veces/10 s, izq. delante 50 %,
  desliza 0,2 → ANDA (0,85 m/s, 29 % aire). Ejercicios resueltos. Modelos en notebooks/modelos/moldeado_*_mejor.
- **── PARTE 6 · SIMULACIÓN DE BÍPEDOS A FONDO ──** (REPLANIFICADA 2026-10-04 a petición del usuario: "ser experto en simular
  antes de tocar robots reales, para pasar cualquier entrevista"; Python PROFESIONAL explicado a fondo en cada NB; sin límite de
  NB ni de longitud). Cada NB = tema de MuJoCo/dinámica + tema de Python profesional. NB44 (moldear la recompensa) ✅ ya hecho.
  **Puente de Python (NB44p1-p6)** ✅ (añadido 2026-10-04: la transición NB27→NB45 fue brusca: 17 NB sin estudiar Python y luego
  4-6 conceptos profesionales por NB). Cada uno con laboratorio de 12 retos resueltos (soluciones ejecutadas):
  · P1 leer código (predice la salida, leer zancudo_env.py con método, introspección, errores de bibliotecas, documentación/firmas)
  · P2 funciones como piezas (tabla de despacho, callbacks, / y *, cierres + enlace tardío, nonlocal, decoradores escalón a escalón,
    partial, cache)
  · P3 clases intermedias (modelo de datos, Trayectoria pitónica, eq/hash, setters, classmethod, dataclasses a fondo + trampa eq con
    arrays en 3.13, Enum, NamedTuple, composición)
  · P4 iterar y recursos (iterable/iterador, generadores, simulación infinita, tuberías + trampa del filtro que cuelga, itertools,
    collections, gestores de contexto, contextmanager, ExitStack)
  · P5 tipos y errores (anotaciones, mypy REAL vía subprocess —instalado, en requirements—, Callable/type alias/Literal, Protocol,
    genéricos 3.12, excepciones propias, raise from, add_note, logging)
  · P6 NumPy para robótica (formas, trayectorias (T,n), máscaras/argmax-trampa, axis, diff vs gradient (diff exacto con el integrador),
    broadcasting, pts @ R.T, einsum, vectorizar ×14, solve vs inv (Hilbert), vistas/copias, +=, isclose, float32, NaN)
  **Bloque A · MuJoCo por dentro**
  · NB45 ✅ (111 celdas, 42 código, EXIT 0) Cómo piensa MuJoCo: mjModel/mjData, coordenadas generalizadas (nq≠nv, cuaternión de la free joint), pipeline de
    mj_step, mj_forward, M(q)q̈+c=τ+Jᵀf (mj_fullM, qfrc_bias...), energía · Py: type hints, dataclasses, __repr__, @property,
    vistas vs copias (trampa de mjData)
  · NB46 ✅ (92 celdas, 35 código, EXIT 0) Cinemática: marcos, rotaciones (matriz/cuaternión wxyz/Euler), cinemática directa, jacobianos (mj_jac*), velocidad =
    J·q̇, cinemática inversa (mínimos cuadrados amortiguados, singularidades) · Py: numpy.linalg a fondo, funciones puras,
    docstrings, typing de arrays, pytest
  · NB47 ✅ (57 celdas, 21 código, EXIT 0) Dinámica inversa y control basado en modelo: mj_inverse, compensación de gravedad, par calculado, espacio de tarea
    · Py: ABC/Protocol, composición, patrón estrategia
  · NB48 ✅ (57 celdas, 19 código, EXIT 0) Contactos a fondo: detección (contype/conaffinity, margin), solref/solimp, condim, cono de fricción, solvers,
    mj_contactForce, CoP/ZMP medidos · Py: generadores/iteradores, Enum, NamedTuple, itertools
  · NB49 ✅ (58 celdas, 21 código, EXIT 0) Integradores, paso de tiempo y rendimiento: Euler explícito vs semiimplícito a mano, Euler/implicit/implicitfast/RK4,
    orden (log-log), estabilidad (pasito·ω<2, kv), BADQACC+reinicio, Zancudo: implicitfast aguanta dt 0,02, determinismo, cProfile,
    rollout (×3,5 con 4 hilos), ProcessPoolExecutor (armature queda para NB50) · Py: decoradores, context managers, functools, multiprocessing/concurrent.futures
  · NB50 ✅ (78 celdas, 30 código, EXIT 0) MJCF profesional y MjSpec: clases de defaults (+trampa grados), keyframes, actuadores = general
    (trampa biastype, timeconst, delay+nsample), armature N²·J (estabilidad), tendones, equality (joint, weld "grúa"), sensores (touch=peso,
    noise no se aplica), mallas (envolvente convexa), MjSpec (add/attach mochila/delete/recompile/to_xml), barrido de piernas (empuje
    21→9 N) → robots/zancudo_v2.xml (implicitfast, tactos, posturas, grúa) · Py: pathlib a fondo, xml.etree, patrón constructor (Self)
  **Bloque B · Andar sin RL**
  · NB51 Planificar pasos: LIPM analítico, punto de captura, plan de pasos, trayectorias del pie · Py: numpy vectorizado,
    matplotlib profesional
  · NB52 Zancudo anda sin RL: preview control de ZMP (Kajita) + IK + PD; clásico vs RL · Py: diseñar una librería, logging
  **Bloque C · Del plano al 3D**
  · NB53 Zancudo 3D (MjSpec): cadera 3 GDL, tobillo 2 GDL, equilibrio lateral, de pie con gravedad compensada · Py: config
    con dataclasses + YAML
  · NB54 Entorno de locomoción profesional 3D: paquete, comandos de velocidad, observación (gravedad proyectada), recompensa
    modular, entrenamiento largo · Py: pyproject, CLI argparse, logging, pytest fixtures
  · NB55 Robustez: aleatorización de dominio, empujones, retrasos, currículo, barridos · Py: wrappers, callbacks,
    numpy Generator, reproducibilidad
  · NB56 Terreno: hfield, escalones, rampas, mapa de alturas con rayos, currículo de terreno · Py: generación procedural
  · NB57 Imitar movimiento: referencias, recompensa tipo DeepMimic, RSI · Py: interpolación, serialización
  **Bloque D · Escala y robots reales (en simulación)**
  · NB58 MuJoCo Menagerie: G1/H1 y otros, inspección, URDF→MJCF, PD de pie
  · NB59 JAX y MJX: programación funcional, jit/vmap/grad, pytrees, MJX vs MuJoCo
  · NB60 Entrenar a lo grande: MuJoCo Playground en Colab (miles de robots en GPU), exportar política
  · NB61 Puente sim-to-real sin hardware: identificación de sistemas, modelos de actuador, latencia, sim-to-sim, ONNX
  · NB62 La entrevista: preguntas con respuesta, ejercicios de pizarra, proyectos de portafolio
  **Parte 7 · Hardware** (después): electrónica, servos, microcontroladores, bípedo de servos barato, portafolio.
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
- **── PARTE 2 · Matemáticas y herramientas ──**
- **NB12 · Vectores** ✅ (50 celdas, 17 código, 6 dibujos matplotlib): Hundir la flota/plano cartesiano, componentes, sumar
  (odometría), escalar, restar (B−A), Pitágoras+raíz (** 0.5), 3D/45D (distancia entre observaciones 0,057 vs 2,24), robot hacia
  la meta con viento (25 pasos, dibujado).
- **NB13 · Producto escalar** ✅ (39 celdas, 12 código): media ponderada → "pesos", política del palo = pesos·obs (política lineal),
  geometría (+/0/−), unitario/normalizar/proyección, premio por avanzar = vel·(1,0,0), a·a = longitud², NEURONA = pesos·x + sesgo,
  perceptrón (termostato = neurona), detector de caídas que anticipa (peso 0,3 en velocidad).
- **NB14 · Matrices** ✅ (43 celdas, 15 código): Segway 2×3 (giro con signos opuestos), lista de listas, bucle anidado, matriz×vector,
  regla de tamaños (IndexError), capa = M·x + b, humanoide 17×45+17 = 782 (completa 5.933), recortar, 0,5**782 = 3,9e-236
  (notación científica), capas en fila = red (avance).
- **NB15 · NumPy + humanoide real** ✅ (76 celdas, 29 código): arrays, shape, elemento a elemento vs listas (concatena/repite), @,
  ValueError de formas, default_rng/zeros/clip, cronometraje (~50-120× en la Pi), Gymnasium reset/step = reiniciar/paso del NB11,
  obs (348,) con obs[0]=1,39 altura, recompensa 1.er paso 5,002; política lineal: W=0 → 198,6 (= muñeco de trapo NB04), W azar ~58,
  mejor de 20 al azar 141,7 < 198,6 → hacen falta pendientes. E5: todo +0,4 → ~237 (tensar ayuda), todo −0,4 → ~45.
- **NB16 · Pendientes** ✅ (36 celdas, 10 código): función f(x)+gráfica, rampa, velocidad = pendiente de la posición, zoom
  (curva → recta), (f(x+h)−f(x))/h → 6 en x², a los dos lados, h=1e-12 empeora vs 1e-6, derivada de x² = 2x por tabla;
  montaña del palo con BATERÍA (coste 0,001, d=8): +27,5 en 12, ≈0 en 23,5 (cima ~462), −0,63 en 40.
- **NB17 · Ascenso por gradiente** ✅ (31 celdas, 10 código): x += tasa·pendiente; colina 10−(x−3)²: tasas 0,01/0,1/0,5/
  0,9/1,1 (lento/bien/de un salto/oscila/explota); 1 ruedecilla 12→25,8→~24,7; gradiente 2D = flecha; mapa contourf con
  camino (12,2) 416 → (22,6; 6,2) ~463; óptimo local (dos colinas, valle entre 3 y 3,5); coste 2N evaluaciones/paso.
- **NB18 · Aprender imitando (supervisado)** ✅ (37 celdas, 10 código): 300 ejemplos del maestro −30i−8v; ECM/pérdida
  (305,6 → 0); valle; REGLA DE LA CADENA (engranajes) → 2·media(error×entrada) = numérica (14,7596); tasa 0,2 →
  (−30; −8; 0), 0,25 aprende, 0,3 explota (6e18); alumno juega 499,9 (a medio aprender 499,8); maestro ±10 →
  (−29,7; −8,0); desplazamiento de distribución; imitación en humanoides.
- **NB19 · Redes neuronales** ✅ (30 celdas, 8 código): maestro que satura (clip −30i a ±40); lineal atascada 81,5;
  capas lineales apiladas = recta; ReLU = codo; 2 codos a mano = exacto; red 1→8→1 con retropropagación a mano (pendiente
  ReLU 0/1), tasa 0,003, 5000 pasos → 0; tasa 0,01 → atasco ~11 (óptimo local, NO neuronas muertas: verificado);
  aproximación universal; red de humanoide 348→256→256→17 = 159.505 pesos.
- **── PARTE 3 · PYTHON DE VERDAD ──**
- **NB20 · Texto** ✅ (74 celdas, 29 código): índices/porciones, inmutables, métodos, split/join, conversiones (ValueError),
  escapes, f-strings y formato (:.2f :, :.1% :+ :>8 :05d), proyecto parsear un log → informe alineado.
- **NB21 · Colecciones** ✅ (80/31): tuplas/desempaquetar, listas a fondo, sort vs sorted, TRAMPA DEL ALIAS (copy, is),
  enumerate/zip, comprensiones, diccionarios (KeyError, get, items, anidados, contar), info REAL del humanoide (ingredientes
  de la recompensa), conjuntos, any/all, key=, // y %, proyecto cuaderno de experimentos.
- **NB22 · Flujo, errores y depuración** ✅ (57/18): while (pelota 63 pasos), límite de seguridad, continue, for-else, pass,
  match, verdad/falsedad, excepciones y trazas (de abajo arriba), try/except/else/finally, raise (fallar pronto), inf/nan +
  math.isfinite (vigilante: explota en el paso 16), assert, depurar (f"{x=}", %debug/breakpoint/pdb, catálogo de bichos).
- **NB23 · Funciones a fondo** ✅ (57/21): defaults, por nombre, trampa del default mutable, *args/**kwargs, desempaquetar al
  llamar, ámbito (UnboundLocalError), lambda, CIERRES (fábrica de políticas), decoradores (@cronometro), recursión,
  iteradores/StopIteration, generadores (lotes; 8,4 MB vs 200 B), docstrings, type hints.
- **NB24 · Clases (I)** ✅ (54/18): clase/objeto, __init__/self, métodos, __repr__, atributos de clase, _privado, @property,
  PaloDeEscoba con reset/step estilo Gymnasium + random.Random propio, PoliticaLineal con __call__ (como PyTorch), mismo
  bucle → 44,8/296,0/499,9; @dataclass + field(default_factory).
- **NB25 · Herencia + entorno Gymnasium** ✅ (43/14): herencia, super(), polimorfismo, ABC/@abstractmethod, Vector con métodos
  especiales (así funciona NumPy), composición; PaloDeEscobaEnv(gym.Env) con spaces.Box, acción normalizada [-1,1]×40,
  check_env (avisos explicados), gym.register + gym.make (envoltorios TimeLimit...): nada 44,6 / solo incl 353,4 / a mano
  499,9; nn.Module explicado.
- **NB26 · Ficheros, módulos, scripts, terminal** ✅ (72/27): pathlib, open/with/modos, CSV (todo texto), JSON, np.save, pickle
  (peligro), módulo palo.py + sys.path + reload, script con argparse + subprocess/sys.executable, terminal (!), venv/pip/
  requirements, logging, Counter/defaultdict/datetime/itertools.product/statistics, proyecto barrido guardado y releído.
- **NB27 · NumPy a fondo, tests y Git** ✅ (76/29): dtype float32, reshape/-1/.T, índices 2D, máscaras/np.where/argsort, EJES,
  BROADCASTING (normalizar observaciones), stack, VISTAS vs copias; 1.000 palos vectorizados (solo incl ~63 % caídas; 10-20×
  más rápido); pytest (test_palo.py, caza el fallo gravedad 10→1); Git real en repo de juguete (init/add/commit/diff/
  switch -c/--decorate), .gitignore, historial del curso; PEP 8.
- **── PARTE 4 · APRENDIZAJE POR REFUERZO DE VERDAD ──**
- **NB28 · Probabilidad** ✅ (48 celdas, 16 código): frecuencia, grandes números (dado, dibujado), distribución (dos dados),
  valor esperado (producto escalar; el RL maximiza el retorno ESPERADO), varianza/σ (robots A y B), uniforme, histogramas,
  campana de Gauss (TCL, 68,4/95,5/99,7, fórmula con e/exp), error típico σ/√n (5 vs 100 episodios) e intervalo de confianza,
  política estocástica (σ: aguanta hasta 50, se desploma en 100; cruce de 400 entre σ 60 y 70), logaritmo y log-prob normal.
- **NB29 · REINFORCE** ✅ (38/11): (a−μ)/σ² comprobada; ×obs por regla de la cadena; retorno desde cada paso γ=0,99 hacia
  atrás; puro NO aprende (~30-45); línea base media → 499 (semilla 0 en la it. 53; 5 semillas 47-95); aprendida (−15,7; −20,1)
  no se cae en 1.000. E5: σ=1 aprende en 6 it (pasos 25× mayores); E7 línea base global inestable (desaprende).
- **NB30 · Ruido, crítico, descuento** ✅ (27/8, ~2 min): ruido medido (sin base desv 34/44 y media de signo erróneo; con base
  9,5/20); normalizar ventajas; crítico lineal con rasgos [1,i²,v²,i·v,t/500] por lstsq — honesto: es tosco (predice −231,
  ordena mal volviendo/cayendo); crítico+normalizar el mejor ([13,17,17,66,26] vs media [53,79,95,60,47]); γ 0,9 no aprende,
  0,99 bien, 1,0 algo peor.
- **NB31 · PyTorch** ✅ (44/16): tensores, autograd (6 en x²; 14,7596 del NB18), grafo, acumulación/zero_grad, no_grad,
  nn.Linear/ReLU/Sequential/Module (25 params), SGD vs Adam — HONESTO: con 8 neuronas Adam se atasca (29,9) y SGD llega
  (0,71); con 32, SGD 4/4 y Adam a veces; Normal.log_prob → gradiente = fórmula NB29; state_dict + weights_only; .to(cuda).
- **NB32 · Actor-crítico** ✅ (46/18, ~4 min): jugador/comentarista; pérdida truco −log_prob×ventaja (= dirección NB29, comprobado
  −0,48/−0,24); escalar entradas; log σ aprendible (0,25→0,20); DIFERENCIA TEMPORAL δ=r+γV'−V (GPS), ruido vs sesgo, reloj en el crítico;
  Actor 2→32 tanh→1 (130 params) + Crítico 3→64→1 (321); TD semilla 0 supera 490 en it. ~95 (42,6→499,6); actor satura ±40 hacia 3°;
  mapa del crítico (franja diagonal, máx ~100=1/(1−γ), esquinas negativas = extrapolación); examen en PaloDeEscoba-v0 499,6 0 caídas
  (aguanta viento ±60; falla desde ±80); TD [94,93,92,78] vs Montecarlo [None,116,100,109]; FRAGILIDAD (Adam+ventajas normalizadas;
  tasa 0,03 llega a 499 y se derrumba a ~60) → motivación de PPO.
- **NB33 · PPO desde cero** ✅ (32/11, ~3,5 min): desperdicio+fragilidad; épocas/minilotes (randperm); razón r=exp(Δlogp);
  recorte min(r·A, clip·A) con tabla de casos + dibujo; GAE λ (comprobado: λ=1 → G−V, λ=0 → δ con crítico al azar);
  PPO tasa 0,01, minilote 1024, 10 épocas: supera 490 en it. 54 (vs 78-94 del NB32), sin bajones, cambio |r−1| 2-30 %,
  r máx < 2, σ 0,25→0,18; SIN recorte: semillas 19/47/None, oscila 500↔200, termina 34-48, r máx 1.053-2.160, σ 0,03-0,05;
  examen viento ±80 0 caídas, ±100 3/20. Ejercicios medidos: λ=0 → 66, λ=1 → 376 (0,95 gana); ε=0,05 lento (90),
  ε=0,5 inestable (136, r 380); bonus de entropía sin recorte NO salva (49/122/31).
- **NB34 · Stable-Baselines3** ✅ (43/15, ~4 min; SB3 2.9.0 instalado): por qué bibliotecas + mapa (SB3/CleanRL/RSL-RL/Brax);
  check_env de SB3; DICCIONARIO NB33↔SB3 leído del modelo (n_steps 2048, batch 64, epochs 10, lr 3e-4, clip 0,2, σ inicial 1);
  make_vec_env (4 copias, autoreset, Monitor); policy 64-64 tanh separadas (8.835 params); inspect.getsource(PPO.train)
  muestra ratio/clamp/min = el NB33; palo aprendido en 49.152 pasos (NB33 propio: ~240.000); OJO learn() juega lotes
  completos (pedir múltiplos de 8.192); informe verbose=1 explicado (approx_kl, clip_fraction, explained_variance...);
  menos robusto al viento que el PPO propio; save/load .zip (pickle); **InvertedPendulum-v5 MuJoCo 1000/1000 en 65.536
  pasos + GIF assets/nb34_pendulo_ppo.gif**. Ejercicios medidos: σ0=0,25 → 51 a 50k (≈250k para aprender); estocástico
  929±164 vs 1000; Pendulum-v1 por defecto −1031 (no aprende → RL Zoo). Cifras SB3 varían un poco entre ejecuciones.
  SIGUIENTE: NB35 Hopper/Walker2d.
- **NB35 · Robots con patas** ✅ (39 celdas, EXIT 0, ~8 min de ejecución): Hopper-v5 (obs 11, 3 motores gear 200, 15,8 kg,
  dt 0,008) y Walker2d-v5 (obs 17, 6 motores gear 100, 23,7 kg); recompensa desmontada con info; trampa de sobrevivir
  (forward_reward_weight=0 → 999,8, 1000 pasos, x +0,06 m); VecNormalize (corto: sin 387 > con 301 → contado con honestidad,
  1 semilla no demuestra nada). Entrenamientos 1M con notebooks/entrenar_largo.py (4 en paralelo en la Pi, 68-91 min):
  Hopper defecto 3508±172 (mejor 3558), afinado más rápido pero inestable (acaba 2633); Walker2d defecto 696 (se lanza y cae,
  óptimo local), afinado 2500±1469 (pico 3741). Modelos en notebooks/modelos/ (Hopper defecto, Walker afinado). Examen 10 ep:
  Hopper 3559 / 969 pasos / 20,7 m / 2,67 m/s; Walker 3161 / 849 / 18,5 m / 2,73 m/s. E4 ctrl×100 → 3482 misma conducta;
  E5 sin normalizar 317; E6 healthy_reward=0 → se lanza en plancha (1,8 m). Checkpoints parciales en trabajo_nb35/.
  → **✅ PARTE 4 COMPLETA (NB28–NB35)**. SIGUIENTE: Parte 5 · La física del cuerpo.
- **── PARTE 5 · LA FÍSICA DEL CUERPO ──** (plan: NB36 ángulos/trigonometría/cinemática directa · NB37 fuerza, par y el péndulo
  de verdad (deducir el "10 × inclinación" del NB11) · NB38 centro de masas y equilibrio estático · NB39 equilibrio dinámico
  (péndulo invertido lineal, punto de captura, ZMP) · NB40 motores de verdad y control PD · NB41 sensores y ruido · NB42 MJCF:
  tu propio robot · NB43 proyecto bípedo propio).
- **NB36 · Ángulos y giros** ✅ (80 celdas, 30 de código, EXIT 0): grados/π/radianes (arco = r·θ), seno/coseno como sombras,
  trampa math.sin(90)=0,894, ondas, desde la vertical (L·sin, L·cos), Pitágoras, atan2 vs atan, cinemática directa de la
  pierna de Hopper (cadera 1,05; muslo 0,45; pierna 0,50; ángulos MuJoCo + = hacia delante) que coincide con MuJoCo
  (xanchor −0,6975/0,5213), paso con dos senos (desfase −1,5 = pie abajo yendo hacia atrás = bueno; +1,5 = al revés, E6).
- **NB37 · Fuerza, par y el péndulo de verdad** ✅ (57 celdas, 20 de código, EXIT 0): unidades SI, a = F/m, newton, peso
  (Hopper 155 N), fuerza normal, par = F·brazo·sin φ, par de la gravedad m·g·(L/2)·sin θ, inercia de giro (1.000 trocitos → 0,75
  = m·L²/3), α = (3g/2L)·sin θ (masa se cancela; escoba 9,8 vs lápiz 98,1), el "10" del NB11 = escoba de 1,47 m linealizada,
  caída 1,339 s (lineal 1,322) = MuJoCo 1,339 s exacto (péndulo MJCF from_xml_string), motor Hopper 200 N·m = 20 kg a 1 m,
  punto de no retorno (E6: 0,205 rad con motor −2).
- **NB38 · Centro de masas y equilibrio quieto** ✅ (46 celdas, 16 de código, EXIT 0): balancín/ley de la palanca, CdM = media
  ponderada (NumPy), CdM de Hopper con body_mass+xipos = subtree_com (x +0,022, altura 0,596), se mueve con la postura; base de
  apoyo (segmento / goma elástica); regla + por qué (suelo empuja, no tira); bloque MJCF freejoint: crítico 18,4°, 18° vuelve,
  19° vuelca; Hopper-estatua (jnt_stiffness 3000 + qpos_spring, apoyado a 0,0605): h 0/0,3 de pie, 0,6 (CdM 0,276) cae; límite
  real ~22 cm vs 26 geométrico → margen de seguridad; estático vs dinámico.
- **NB39 · Punto de captura y ZMP** ✅ (43 celdas, 13 de código, EXIT 0, sin MuJoCo): modelo (mapa≠territorio), LIPM por triángulos
  semejantes a = (g/z0)(x−p), z0 0,8 → ω 3,502; 3 empujones desde −0,3 (0,9 vuelve, 1,05 casi, 1,2 pasa); energía orbital
  (−0,294→−0,319 por error de Euler; dt/10 → −0,296); velocidad justa 1,051; punto de captura x+v/ω = 0,143 (±2 cm cae);
  tobillo vs paso (0,53 m/s con punta a 0,15); ZMP = x − (z0/g)ẍ (−0,082 para 1 m/s²), NB38 caso particular, ASIMO; andar
  pisando b antes de la captura: pasos 0,152/0,304/0,457 → 0,38/0,76/1,14 m/s; límites + relación con RL. E5: 1,5 m/s 2 pasos,
  2,5 → 4, 3 → no se salva.
- **NB40 · Motores y control PD** ✅ (42 celdas, 14 de código, EXIT 0): motor (rotor/estátor, par ∝ corriente), reductora N:1
  (0,5 N·m 3000 rpm 50:1 → 25 N·m 6,28 rad/s), holgura/inercia reflejada N²/retroimpulsable/cuasi-directos, límites (par,
  recta par-velocidad, calor); pierna simulada 2 kg 0,5 m: P oscila (máx ~1,48), PD Kd 0/1/3/10, error estacionario
  0,651/0,734/0,783 (Kp 20/50/200) → compensación de gravedad 0,800, saturación 2,5 N·m columpia; Hopper con PD en ctrl por
  mj_step: Kp 0/50 cae, 300/20 de pie (E5: 100 inclinado, 150+ recto); la estatua del NB38 era un PD; política→ángulos +
  PD en robots reales.
- **NB41 · Sensores y ruido** ✅ (54 celdas, 22 de código, EXIT 0): información privilegiada; codificador 4096 → 0,088°,
  velocidad por diferencias salta 0↔1,53 (derivar amplifica); ruido gaussiano, promediar → /√n (verificado), media móvil =
  retraso; IMU: acelerómetro (quieto 9,81 arriba, atan2) y giróscopo (sesgo → deriva); péndulo MJCF con site+accelerometer+
  gyro: quieto 0,2964 exacto, balanceándose el acel va en contrafase; errores acel 0,237 / giro 0,173 / complementario 0,061
  con peso 0,999 (tiempo de corrección paso/(1−peso) = 1 s; 0,98 da 0,222 aquí porque mide a 1 kHz); Kalman nombrado;
  contacto Hopper con PD 96+59,2 = 155,2 N; retraso: Kp200 ok 10 ms, oscila 20, explota 30; Kp50 aguanta 30; política NB35
  con ruido 3559/2915/798/318 (0/0,01/0,05/0,1), solo en velocidades aguanta (3446/3403/2377); remedios (ruido, DR,
  profesor-alumno).
- **NB42 · MJCF: tu propio robot** ✅ (49 celdas, 16 de código, EXIT 0): XML (etiquetas/atributos/árbol), secciones MJCF, caja
  que cae (8 kg densidad agua), posiciones relativas, tipos de geom, joints (axis 0 -1 0 = + hacia delante, range en radianes
  con compiler), raíz plana 3 joints; pierna() y motores() con f-strings → **Zancudo** (notebooks/robots/zancudo.xml: 8 bodies,
  9 joints, 6 position kp300 kv20 forcerange ±150, IMU; 23,6 kg; CdM 0,783); error real 'unknown transmission target';
  de pie con ctrl 0; empujón 0,05 s (caída = torso baja >30 cm): 180 N aguanta, 200 cae (captura ~12 cm); torso 20 kg
  aguanta 200 (cae 250); pies −0,16..0,24 aguanta 300 (cae 350); solo por delante → cae de espaldas al rebotar; agachado
  aguanta 200 resbalando 0,29 m. SIGUIENTE: NB43 entorno Gymnasium de Zancudo + PPO para andar.
- **NB43 · Zancudo aprende a andar** ✅ (42 celdas, 15 de código, EXIT 0): las 4 decisiones (obs 18 medibles + reloj de fase
  0,8 s; acción = postura base + amplitud × a a 50 Hz; recompensa avance+vida−0,01·a²; caída cadera<0,55 o |incl|>0,8; 1000 pasos),
  zancudo_env.py leído con inspect, check_env. Referencias: quieto 832,6 (se cae en 2/10: semillas 0 y 2), azar ~57. Corto en vivo
  106k: 739,8, x=−1,45 (trampa de sobrevivir). Largos (entrenar_zancudo.py): defecto sube a 5.435; los 3 afinado COLAPSAN. Campeón
  5.453, 0 caídas, 89,7 m = 4,49 m/s (corre a saltos). Empujones 200 N 5/5, 300 N 3-4/5. Ruido apenas afecta (ángulos+PD filtran).
  Ejercicios resueltos; E5 (sin reloj, 300k): 3.278 vs 2.854 con reloj → el reloj no ayudaba sin recompensa que lo use.
  → **✅ PARTE 5 COMPLETA (NB36–NB43)**.
- **NB44 · Moldear la recompensa** ✅ (49 celdas, 19 de código, EXIT 0) — abre la Parte 6. zancudo_moldeado.py (campana vel 1 m/s,
  recto, vida 0,2, vuelo, pie>15 cm, suavidad). Ablación 1M (completa/sin_vuelo/sin_pie_alto/lento; reanudadas tras reinicio de la
  Pi con `seguir`): todas a la velocidad pedida; sin_vuelo 18→40 % aire; sin_pie_alto pie 0,79 m y tirones ×4; lento atascado
  ~870 = quieto cobra e⁻¹ (ancho de campana). DESCUBRIMIENTO: todas GALOPAN (izq. siempre ~1 m detrás, arrastrada 0,85 m/s).
  zancudo_alterno.py: ZancudoAlterno (alternar apoyos con el reloj) → galope con ritmo + vuelve a levantar el pie (términos se
  pelean); ZancudoZancada (campana sobre separación de pies −0,2·cos(fase)) → se cruzan 25 veces/10 s, izq. delante 50 %,
  desliza 0,2 → ANDA (0,85 m/s, 29 % aire). Ejercicios resueltos. Modelos en notebooks/modelos/moldeado_*_mejor.
- **── PARTE 6 · BÍPEDOS DE VERDAD ──** (plan): NB44 moldear la recompensa (andar bonito: velocidad objetivo con núcleo
  exponencial, torso recto, levantar los pies, tiempo en el aire alternado, suavidad, energía) · NB45 robustez (aleatorización
  de masas/rozamiento/PD/retrasos + empujones al entrenar, currículo) · NB46 obedecer órdenes (velocidad pedida, parar, atrás)
  · NB47 al 3D: el humanoide (Colab) · NB48 miles de robots en GPU: JAX/MJX + MuJoCo Playground (G1, Colab) · NB49 sim-to-real
  (identificación, latencias, seguridad, exportar ONNX). Parte 7 hardware: electrónica, servos y microcontroladores, bípedo de
  servos barato, portafolio.
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
- **── PARTE 2 · Matemáticas y herramientas ──**
- **NB12 · Vectores** ✅ (50 celdas, 17 código, 6 dibujos matplotlib): Hundir la flota/plano cartesiano, componentes, sumar
  (odometría), escalar, restar (B−A), Pitágoras+raíz (** 0.5), 3D/45D (distancia entre observaciones 0,057 vs 2,24), robot hacia
  la meta con viento (25 pasos, dibujado).
- **NB13 · Producto escalar** ✅ (39 celdas, 12 código): media ponderada → "pesos", política del palo = pesos·obs (política lineal),
  geometría (+/0/−), unitario/normalizar/proyección, premio por avanzar = vel·(1,0,0), a·a = longitud², NEURONA = pesos·x + sesgo,
  perceptrón (termostato = neurona), detector de caídas que anticipa (peso 0,3 en velocidad).
- **NB14 · Matrices** ✅ (43 celdas, 15 código): Segway 2×3 (giro con signos opuestos), lista de listas, bucle anidado, matriz×vector,
  regla de tamaños (IndexError), capa = M·x + b, humanoide 17×45+17 = 782 (completa 5.933), recortar, 0,5**782 = 3,9e-236
  (notación científica), capas en fila = red (avance).
- **NB15 · NumPy + humanoide real** ✅ (76 celdas, 29 código): arrays, shape, elemento a elemento vs listas (concatena/repite), @,
  ValueError de formas, default_rng/zeros/clip, cronometraje (~50-120× en la Pi), Gymnasium reset/step = reiniciar/paso del NB11,
  obs (348,) con obs[0]=1,39 altura, recompensa 1.er paso 5,002; política lineal: W=0 → 198,6 (= muñeco de trapo NB04), W azar ~58,
  mejor de 20 al azar 141,7 < 198,6 → hacen falta pendientes. E5: todo +0,4 → ~237 (tensar ayuda), todo −0,4 → ~45.
- **NB16 · Pendientes** ✅ (36 celdas, 10 código): función f(x)+gráfica, rampa, velocidad = pendiente de la posición, zoom
  (curva → recta), (f(x+h)−f(x))/h → 6 en x², a los dos lados, h=1e-12 empeora vs 1e-6, derivada de x² = 2x por tabla;
  montaña del palo con BATERÍA (coste 0,001, d=8): +27,5 en 12, ≈0 en 23,5 (cima ~462), −0,63 en 40.
- **NB17 · Ascenso por gradiente** ✅ (31 celdas, 10 código): x += tasa·pendiente; colina 10−(x−3)²: tasas 0,01/0,1/0,5/
  0,9/1,1 (lento/bien/de un salto/oscila/explota); 1 ruedecilla 12→25,8→~24,7; gradiente 2D = flecha; mapa contourf con
  camino (12,2) 416 → (22,6; 6,2) ~463; óptimo local (dos colinas, valle entre 3 y 3,5); coste 2N evaluaciones/paso.
- **NB18 · Aprender imitando (supervisado)** ✅ (37 celdas, 10 código): 300 ejemplos del maestro −30i−8v; ECM/pérdida
  (305,6 → 0); valle; REGLA DE LA CADENA (engranajes) → 2·media(error×entrada) = numérica (14,7596); tasa 0,2 →
  (−30; −8; 0), 0,25 aprende, 0,3 explota (6e18); alumno juega 499,9 (a medio aprender 499,8); maestro ±10 →
  (−29,7; −8,0); desplazamiento de distribución; imitación en humanoides.
- **NB19 · Redes neuronales** ✅ (30 celdas, 8 código): maestro que satura (clip −30i a ±40); lineal atascada 81,5;
  capas lineales apiladas = recta; ReLU = codo; 2 codos a mano = exacto; red 1→8→1 con retropropagación a mano (pendiente
  ReLU 0/1), tasa 0,003, 5000 pasos → 0; tasa 0,01 → atasco ~11 (óptimo local, NO neuronas muertas: verificado);
  aproximación universal; red de humanoide 348→256→256→17 = 159.505 pesos.
- **── PARTE 3 · PYTHON DE VERDAD ──**
- **NB20 · Texto** ✅ (74 celdas, 29 código): índices/porciones, inmutables, métodos, split/join, conversiones (ValueError),
  escapes, f-strings y formato (:.2f :, :.1% :+ :>8 :05d), proyecto parsear un log → informe alineado.
- **NB21 · Colecciones** ✅ (80/31): tuplas/desempaquetar, listas a fondo, sort vs sorted, TRAMPA DEL ALIAS (copy, is),
  enumerate/zip, comprensiones, diccionarios (KeyError, get, items, anidados, contar), info REAL del humanoide (ingredientes
  de la recompensa), conjuntos, any/all, key=, // y %, proyecto cuaderno de experimentos.
- **NB22 · Flujo, errores y depuración** ✅ (57/18): while (pelota 63 pasos), límite de seguridad, continue, for-else, pass,
  match, verdad/falsedad, excepciones y trazas (de abajo arriba), try/except/else/finally, raise (fallar pronto), inf/nan +
  math.isfinite (vigilante: explota en el paso 16), assert, depurar (f"{x=}", %debug/breakpoint/pdb, catálogo de bichos).
- **NB23 · Funciones a fondo** ✅ (57/21): defaults, por nombre, trampa del default mutable, *args/**kwargs, desempaquetar al
  llamar, ámbito (UnboundLocalError), lambda, CIERRES (fábrica de políticas), decoradores (@cronometro), recursión,
  iteradores/StopIteration, generadores (lotes; 8,4 MB vs 200 B), docstrings, type hints.
- **NB24 · Clases (I)** ✅ (54/18): clase/objeto, __init__/self, métodos, __repr__, atributos de clase, _privado, @property,
  PaloDeEscoba con reset/step estilo Gymnasium + random.Random propio, PoliticaLineal con __call__ (como PyTorch), mismo
  bucle → 44,8/296,0/499,9; @dataclass + field(default_factory).
- **NB25 · Herencia + entorno Gymnasium** ✅ (43/14): herencia, super(), polimorfismo, ABC/@abstractmethod, Vector con métodos
  especiales (así funciona NumPy), composición; PaloDeEscobaEnv(gym.Env) con spaces.Box, acción normalizada [-1,1]×40,
  check_env (avisos explicados), gym.register + gym.make (envoltorios TimeLimit...): nada 44,6 / solo incl 353,4 / a mano
  499,9; nn.Module explicado.
- **NB26 · Ficheros, módulos, scripts, terminal** ✅ (72/27): pathlib, open/with/modos, CSV (todo texto), JSON, np.save, pickle
  (peligro), módulo palo.py + sys.path + reload, script con argparse + subprocess/sys.executable, terminal (!), venv/pip/
  requirements, logging, Counter/defaultdict/datetime/itertools.product/statistics, proyecto barrido guardado y releído.
- **NB27 · NumPy a fondo, tests y Git** ✅ (76/29): dtype float32, reshape/-1/.T, índices 2D, máscaras/np.where/argsort, EJES,
  BROADCASTING (normalizar observaciones), stack, VISTAS vs copias; 1.000 palos vectorizados (solo incl ~63 % caídas; 10-20×
  más rápido); pytest (test_palo.py, caza el fallo gravedad 10→1); Git real en repo de juguete (init/add/commit/diff/
  switch -c/--decorate), .gitignore, historial del curso; PEP 8.
- **── PARTE 4 · APRENDIZAJE POR REFUERZO DE VERDAD ──**
- **NB28 · Probabilidad** ✅ (48 celdas, 16 código): frecuencia, grandes números (dado, dibujado), distribución (dos dados),
  valor esperado (producto escalar; el RL maximiza el retorno ESPERADO), varianza/σ (robots A y B), uniforme, histogramas,
  campana de Gauss (TCL, 68,4/95,5/99,7, fórmula con e/exp), error típico σ/√n (5 vs 100 episodios) e intervalo de confianza,
  política estocástica (σ: aguanta hasta 50, se desploma en 100; cruce de 400 entre σ 60 y 70), logaritmo y log-prob normal.
- **NB29 · REINFORCE** ✅ (38/11): (a−μ)/σ² comprobada; ×obs por regla de la cadena; retorno desde cada paso γ=0,99 hacia
  atrás; puro NO aprende (~30-45); línea base media → 499 (semilla 0 en la it. 53; 5 semillas 47-95); aprendida (−15,7; −20,1)
  no se cae en 1.000. E5: σ=1 aprende en 6 it (pasos 25× mayores); E7 línea base global inestable (desaprende).
- **NB30 · Ruido, crítico, descuento** ✅ (27/8, ~2 min): ruido medido (sin base desv 34/44 y media de signo erróneo; con base
  9,5/20); normalizar ventajas; crítico lineal con rasgos [1,i²,v²,i·v,t/500] por lstsq — honesto: es tosco (predice −231,
  ordena mal volviendo/cayendo); crítico+normalizar el mejor ([13,17,17,66,26] vs media [53,79,95,60,47]); γ 0,9 no aprende,
  0,99 bien, 1,0 algo peor.
- **NB31 · PyTorch** ✅ (44/16): tensores, autograd (6 en x²; 14,7596 del NB18), grafo, acumulación/zero_grad, no_grad,
  nn.Linear/ReLU/Sequential/Module (25 params), SGD vs Adam — HONESTO: con 8 neuronas Adam se atasca (29,9) y SGD llega
  (0,71); con 32, SGD 4/4 y Adam a veces; Normal.log_prob → gradiente = fórmula NB29; state_dict + weights_only; .to(cuda).
- **NB32 · Actor-crítico** ✅ (46/18, ~4 min): jugador/comentarista; pérdida truco −log_prob×ventaja (= dirección NB29, comprobado
  −0,48/−0,24); escalar entradas; log σ aprendible (0,25→0,20); DIFERENCIA TEMPORAL δ=r+γV'−V (GPS), ruido vs sesgo, reloj en el crítico;
  Actor 2→32 tanh→1 (130 params) + Crítico 3→64→1 (321); TD semilla 0 supera 490 en it. ~95 (42,6→499,6); actor satura ±40 hacia 3°;
  mapa del crítico (franja diagonal, máx ~100=1/(1−γ), esquinas negativas = extrapolación); examen en PaloDeEscoba-v0 499,6 0 caídas
  (aguanta viento ±60; falla desde ±80); TD [94,93,92,78] vs Montecarlo [None,116,100,109]; FRAGILIDAD (Adam+ventajas normalizadas;
  tasa 0,03 llega a 499 y se derrumba a ~60) → motivación de PPO.
- **NB33 · PPO desde cero** ✅ (32/11, ~3,5 min): desperdicio+fragilidad; épocas/minilotes (randperm); razón r=exp(Δlogp);
  recorte min(r·A, clip·A) con tabla de casos + dibujo; GAE λ (comprobado: λ=1 → G−V, λ=0 → δ con crítico al azar);
  PPO tasa 0,01, minilote 1024, 10 épocas: supera 490 en it. 54 (vs 78-94 del NB32), sin bajones, cambio |r−1| 2-30 %,
  r máx < 2, σ 0,25→0,18; SIN recorte: semillas 19/47/None, oscila 500↔200, termina 34-48, r máx 1.053-2.160, σ 0,03-0,05;
  examen viento ±80 0 caídas, ±100 3/20. Ejercicios medidos: λ=0 → 66, λ=1 → 376 (0,95 gana); ε=0,05 lento (90),
  ε=0,5 inestable (136, r 380); bonus de entropía sin recorte NO salva (49/122/31).
- **NB34 · Stable-Baselines3** ✅ (43/15, ~4 min; SB3 2.9.0 instalado): por qué bibliotecas + mapa (SB3/CleanRL/RSL-RL/Brax);
  check_env de SB3; DICCIONARIO NB33↔SB3 leído del modelo (n_steps 2048, batch 64, epochs 10, lr 3e-4, clip 0,2, σ inicial 1);
  make_vec_env (4 copias, autoreset, Monitor); policy 64-64 tanh separadas (8.835 params); inspect.getsource(PPO.train)
  muestra ratio/clamp/min = el NB33; palo aprendido en 49.152 pasos (NB33 propio: ~240.000); OJO learn() juega lotes
  completos (pedir múltiplos de 8.192); informe verbose=1 explicado (approx_kl, clip_fraction, explained_variance...);
  menos robusto al viento que el PPO propio; save/load .zip (pickle); **InvertedPendulum-v5 MuJoCo 1000/1000 en 65.536
  pasos + GIF assets/nb34_pendulo_ppo.gif**. Ejercicios medidos: σ0=0,25 → 51 a 50k (≈250k para aprender); estocástico
  929±164 vs 1000; Pendulum-v1 por defecto −1031 (no aprende → RL Zoo). Cifras SB3 varían un poco entre ejecuciones.
  SIGUIENTE: NB35 Hopper/Walker2d.
- **NB35 · Robots con patas** ⏳ EN CURSO: borrador completo en build_parts/nb35.py (con marcadores a rellenar); entrenamientos
  largos parados a medias, ver trabajo_nb35/LEEME.md. Datos ya medidos: Hopper-v5 obs 11, acción 3, gear 200, 15,8 kg, dt 0,008;
  azar 10,4 (19,6 pasos), quieto 146,1 (148,8); Walker2d-v5 obs 17, acción 6, gear 100, 23,7 kg; azar −1,3, quieto 93,5.
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
| 2026-10-05 | NB28b, NB38b, NB39b, NB44p7 + erratas y notas de la auditoría | Los 10 NB de relleno, completos |
| 2026-10-04 | Auditoría NB00-NB50 + NB03b, NB04b, NB05b, NB11b, NB15b, NB17b | Plan de huecos (PLAN_HUECOS.md) |
| 2026-09-29 | NB00–NB03 antiguos (Fase 0) | Archivados en `_archivo/` tras el giro de enfoque |
| 2026-09-30 | Giro a "nivel cero de verdad" + NB00 nuevo | Teoría primero, código en microdosis |
| 2026-10-03 | NB34 Stable-Baselines3 + 1.er robot MuJoCo | Péndulo invertido 1000/1000, GIF |
| 2026-10-03 | NB33 PPO desde cero (+GAE) | Experimento sin recorte: derrumbe medido |
| 2026-10-02 | NB32 actor-crítico (TD vs Montecarlo) | Fragilidad medida → PPO |
| 2026-10-02 | NB28–NB31 (probabilidad, REINFORCE, crítico, PyTorch) | PyTorch instalado en la Pi |
| 2026-10-02 | NB20–NB27 → Parte 3 Python de verdad completa | Pedido: no dejar nada de Python |
| 2026-10-02 | NB16–NB19 (pendientes, gradiente, imitación, redes) | Retropropagación escrita a mano |
| 2026-10-01 | NB12–NB15 (Parte 2: vectores, producto escalar, matrices, NumPy) | 1.er contacto con el humanoide real |
| 2026-10-01 | NB08–NB11 → Parte 1 completa | Proyecto palo de escoba: 1.er RL desde cero |
| 2026-10-01 | NB05–NB07 (Parte 1: print, variables, bucles) | Errores reales con code_err |
| 2026-10-01 | NB04 → Parte 0 completa | Recompensa real del humanoide medida |
| 2026-10-01 | NB00–NB02 ampliados + NB03 | Datos verificados; subactuación, CoM, sensores, inercia |
