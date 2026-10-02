# Trabajo en curso del NB35 (Hopper/Walker2d) — parado el 2026-10-03 01:22

Entrenamientos largos (largo.py, 4 en paralelo, ~8-12 min/100k pasos cada uno) PARADOS a medias:
- Hopper defecto   425.984 pasos → nota 1173,7
- Walker2d defecto 425.984 pasos → nota 429,6
- Hopper afinado   200.704 pasos → nota 951,7
- Walker2d afinado 200.704 pasos → nota 882,1
(los log_*.txt tienen el registro tramo a tramo; los .zip + _norm.pkl son el último checkpoint)

Para reanudar: o reiniciar desde cero (`python largo.py Hopper-v5 defecto 1000000`, el registro sale limpio
para el notebook) o continuar con PPO.load(...) + VecNormalize.load(...) y learn(..., reset_num_timesteps=False).

Luego: copiar los modelos finales a notebooks/modelos/ (nombres <Env>_<cfg>.zip y <Env>_<cfg>_norm.pkl),
rellenar en build_parts/nb35.py los marcadores REGISTRO_HOPPER, REGISTRO_WALKER, MEJOR_HOPPER, MEJOR_WALKER,
ANALISIS_CURVAS_*, EXAMEN_HOPPER, GIF_*, RESULTADO_VIDA, RESULTADO_NORM, RESULTADO_E4/E5/E6 con cifras reales,
construir y verificar con nbconvert (EXIT 0), commit+push.
