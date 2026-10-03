# Estado al cerrar (2026-10-03 ~20:30)

- NB43 (Zancudo aprende a andar): build_parts/nb43.py casi completo. Quedan 3 marcadores: PENDIENTE_REF (referencias
  quieto/azar, salen al ejecutar), PENDIENTE_CORTO (entrenamiento corto en vivo) y PENDIENTE_GIF (describir el GIF del
  campeón). Pasos: construir, ejecutar con nbconvert (timeout 3000), leer las salidas, rellenar los 3 textos, reconstruir y
  verificar EXIT 0, commit + push. Modelos ya en notebooks/modelos/zancudo_{defecto,afinado,ruido}_mejor.*
  Cifras medidas: campeón 5452,9 / 1000 pasos / 89,72 m; empujones -300 4/5, -200 5/5, 200 5/5, 300 3/5, 400 3/5;
  ruido 0/0,02/0,05: afinado 2881/2827/3052, ruido 2745/2680/2546, campeón 5453/5108/5300.
- NB44 (moldear la recompensa): borrador build_parts/nb44.py con marcadores; entorno notebooks/zancudo_moldeado.py;
  entrenamientos en trabajo_nb44/ (completa, sin_vuelo, sin_pie_alto, lento; 1M) lanzados con nohup: mirar log_*.txt.
  Si se cortaron, relanzar: cd trabajo_nb44 && nohup ../venv/bin/python entrenar_moldeado.py <variante> 1000000 > log_<variante>.txt &
  A los 213k estaban todos en la trampa de sobrevivir (de pie, ~1000 pasos, poca distancia).
  Al acabar: copiar moldeado_*_mejor(.zip,_norm.pkl) y zancudo_defecto_mejor como MEJOR_NB43 a notebooks/modelos/.
