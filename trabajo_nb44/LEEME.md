# Estado (2026-10-04)

Parte 6 replanificada a NB45-NB62 (plan en PROGRESO.md). HECHOS y subidos: NB45-NB50 (Bloque A completo).
Robot de trabajo desde ahora: notebooks/robots/zancudo_v2.xml (implicitfast, sensores tacto_d/tacto_i/cdm,
posturas agachado/colgado, weld "grua" apagado). El zancudo.xml original se conserva para los NB antiguos.

Siguiente: NB51 Bloque B · planificar pasos: LIPM analítico, punto de captura, plan de pasos, trayectorias del pie
(Py: NumPy vectorizado, matplotlib profesional).

## PUENTE DE PYTHON (pedido 2026-10-04: la transición NB27→NB45 fue demasiado brusca)
6 notebooks NB44p1-p6, entre NB44 y NB45, con laboratorio de 12 retos resueltos cada uno.
HECHOS y subidos (EXIT 0, soluciones comprobadas con scratch checksol): P1 leer código, P2 funciones, P3 clases.
P4 (iterar y recursos): build_parts/nb44p4.py ESCRITO, SIN VERIFICAR (se cortó la sesión): ejecutar, revisar salidas
contra el texto y comprobar soluciones; luego commit.
Pendientes: P5 tipos y errores (anotaciones básico→Protocol/genéricos/Self, excepciones propias, raise from, logging),
P6 NumPy intermedio para robótica (trayectorias (T,n), máscaras, lotes/broadcasting, linalg básico, vistas, isclose).
Después: añadir el Puente a PROGRESO.md y seguir con NB51.
