# Estado (2026-10-04, cierre de sesión)

Parte 6 replanificada a NB45-NB62 (plan en PROGRESO.md). HECHOS y subidos: NB45, NB46, NB47, NB48.

NB49 (integradores y rendimiento): build_parts/nb49.py ESCRITO y el notebook EJECUTA (EXIT 0), pero faltan
los textos de los marcadores: EXPLICITO_TEXTO, INTEGRADORES_TEXTO, ORDEN_TEXTO, ESTABILIDAD_TEXTO, KV_TEXTO,
ZANCUDO_TEXTO, PERFIL_TEXTO, ROLLOUT_TEXTO, PROCESOS_TEXTO y SOLUCIONES_49.
Cifras medidas (de la ejecución): explícito 4,51 → 16,5 J/kg en 20 s; semi 4,58. Péndulo: Euler/implicit/
implicitfast −4,14e-2 (dt 0,01) y −7,79e-3 (0,002); RK4 +6,4e-6 / +6,3e-8. Orden: Euler cocientes 2,0; RK4 10/13,5/14,8.
Muelle dt 0,01: k=100 ok, k=1000 ok (pasito·ω 1,37), k=5000 explota (3,06). kv≥20 Euler explota, implicitfast no.
Zancudo de pie 3 s: Euler cae desde dt 0,005; implicitfast aguanta hasta 0,02; RK4 cae en 0,01 y vuela en 0,02.
Perfil entorno: mj_step 69 % (0,151 de 0,219 s). PPO 16.384 pasos (medido aparte): mj_step 2,2 de 26,3 s (8 %).
rollout 8×10.000: 1 hilo 67k pasos/s, 4 hilos 232k. Procesos 8 episodios: 1,61 / 0,84 / 0,48 s (1/2/4).
Soluciones: script trabajo_nb44/sol_nb49_borrador.py (falla por 'zancudo' no definido: añadir la carga del modelo).
Después: NB50 MJCF profesional + MjSpec.
