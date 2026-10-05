# Estado (2026-10-04)

Parte 6 replanificada a NB45-NB62 (plan en PROGRESO.md). HECHOS: NB45-NB50 (Bloque A) + PUENTE DE PYTHON NB44p1-p6 (completo).
Robot de trabajo: notebooks/robots/zancudo_v2.xml (implicitfast, tacto_d/tacto_i/cdm, posturas agachado/colgado, weld "grua").

NB51 ✅ (2026-10-06): planificar pasos (LIPM exacto, DCM, capturabilidad N pasos, plan del DCM hacia atrás,
pie en el aire, LIPM en MuJoCo con realimentación del DCM).

NB52 ✅ (2026-10-06): Zancudo anda sin RL (vista previa de Kajita + IK + servos rígidos con prealimentación;
paso de captura; comparación con RL). Librería notebooks/andar/ (fuente: build_parts/nb52_andar/).
Bloque B completo.

NB53 ✅ (2026-10-06): Zancudo 3D con MjSpec desde config YAML (robots/zancudo3d.yaml/.xml), de pie con reparto
de fuerzas, a la pata coja, equilibrio lateral medido.

Siguiente: NB54 Bloque C · entorno de locomoción profesional 3D (usar robots/zancudo3d.xml; observación con gravedad
proyectada, comandos de velocidad, recompensa modular; Py: paquete + pyproject, argparse, logging, pytest fixtures).
Ojo: entrenar en 3D en la Pi será lento → plantear corto en la Pi + largo en script/Colab.
