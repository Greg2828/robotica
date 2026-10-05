# Estado (2026-10-04)

Parte 6 replanificada a NB45-NB62 (plan en PROGRESO.md). HECHOS: NB45-NB50 (Bloque A) + PUENTE DE PYTHON NB44p1-p6 (completo).
Robot de trabajo: notebooks/robots/zancudo_v2.xml (implicitfast, tacto_d/tacto_i/cdm, posturas agachado/colgado, weld "grua").

NB51 ✅ (2026-10-06): planificar pasos (LIPM exacto, DCM, capturabilidad N pasos, plan del DCM hacia atrás,
pie en el aire, LIPM en MuJoCo con realimentación del DCM).

Siguiente: NB52 Bloque B · Zancudo anda sin RL: preview control de ZMP (Kajita) + IK + PD; clásico vs RL
(Py: diseñar una librería, logging). Reutilizar de NB51: lipm, plan_pies, Fase, trayectoria_cdm, pie_en_vuelo,
controlador DCM p = p_plan + (1 + k/ω)(ξ − ξ_plan). z0 = 0,71 (CdM en key 'agachado' de zancudo_v2).
