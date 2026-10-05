# Plan de relleno

HECHO (2026-10-04): NB03b números (era "NB04b" en el plan), NB04b álgebra (era "NB04c"), NB05b, NB11b, NB15b, NB17b + arreglos NB01/02/03/04/05/06/08/11/14/15/17/18.
HECHO (2026-10-05): NB28b (+ enlaces desde NB28/NB29/NB30, quitados los "los matemáticos demostraron").
HECHO (2026-10-05): NB38b (+ enlaces NB38/NB39, NB45 energía "NB37"→NB38b).
HECHO (2026-10-05): NB39b (+ enlaces NB39/NB40/NB49; P3 ω/ζ→NB39b y NB49 regla pasito·ω<2→NB39b ya arreglados).
HECHO (2026-10-05): NB44p7 álgebra lineal (+ P6 ahora "6 de 7" y apunta a P7; NB45 eigvalsh y NB46 determinante citan P7).
→ LOS 10 NB NUEVOS ESTÁN HECHOS. SIGUIENTE: los ARREGLOS pendientes de abajo.
Verificar cada NB con nbconvert --execute y las soluciones con el script checksol (extrae bloques ```python de los <details>).

 de huecos (auditoría 2026-10-04, 8 revisores leyeron NB00-NB50 completos)

## Notebooks NUEVOS (en orden de lectura)
- [x] NB04b · Números a fondo: porcentajes, decimales, potencias (negativas, fraccionarias), raíces, notación científica (sin código)
- [x] NB04c · Letras y ecuaciones: fórmulas, despejar, fracciones con letras, cancelar, caída libre h=h0−½gt² (el 0,75 m del NB02) (sin código)
- [x] NB05b · Tu ordenador por dentro y la terminal: binario/bits/bytes, CPU/núcleos/memoria/disco, carpetas/rutas, terminal, venv, pip, instalar en tu máquina, procesos e hilos
- [x] NB11b · Python que vas a ver: argumentos con nombre, tuplas, atributo vs método, `in`, listas de listas, import/from/as
- [x] NB15b · Funciones a fondo: desplazar/reflejar/escalar, exponencial y e, logaritmo y sus reglas, escalas log, decaimiento exponencial y constante de tiempo (63 %)
- [x] NB17b · Reglas de derivación: potencia, suma, cadena, producto, exp, log, segunda derivada, parciales (comprobadas numéricamente)
- [x] NB28b · Las matemáticas del gradiente de la política: regla del producto, log de productos, derivar log N paso a paso, ∇p = p∇log p, línea base sin sesgo, serie geométrica 1/(1−γ), n vs n−1
- [x] NB38b · Energía, trabajo y potencia (cinética, potencial, conservación, potencia = par·ω)
- [x] NB39b · Muelles, amortiguadores y ecuaciones diferenciales: derivadas de sen/cos, oscilador, ω, ζ, sub/crítico/sobre, simular con Euler y estabilidad (x' = −λx → pasito·λ < 2)
- [x] NB44p7 · Álgebra lineal para robótica: traspuesta, identidad, inversa, A·x=b, det, rango, valores/vectores propios, definida positiva, SVD, condición, pseudoinversa, producto vectorial

## ARREGLOS en notebooks existentes
- [ ] Puente P1-P6: quitar/parafrasear referencias a NB45-NB50 como sabidas (van ANTES del NB45)
- [ ] NB45-NB50: lo enseñado en el puente citarlo como repaso (P2/P3/P4), no "a fondo en NB48/49"
- [ ] Errores: NB03 "1 seguido de 50 átomos"; NB01 hombro; NB36 θ="zeta"→theta; NB37 "newton por metro"→"newton metro"; NB34 nan "del NB33"; NB38 euler en grados; NB39 Kajita 1991/2001; NB46 Hilbert 12×12 (n=10); NB49 "PPO (NB47)"; NB48 refs falsas a NB17 (convexidad, Newton, bisección) y §2 "nuevo"→repaso; NB43/NB44 refs caducadas a NB45/NB46; P2 "paso bajo (NB41)"; P1 inspect NB34 vs NB43
- [ ] Notas breves: NB34/NB35 radianes y par (→NB36/NB37); NB14 0,5×0,5 (aplazar a NB28b); NB17 E1 (→NB17b); NB02/NB07 0,75 (→NB04c); NB06-08 criterio de signo; NB08 texto en variable; NB25 dtype/float32 y conversiones; NB19 retropropagación con 1 neurona antes de 8
- [ ] Actualizar PROGRESO.md, README, memoria
