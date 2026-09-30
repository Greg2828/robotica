# Glosario

Cada término nuevo, explicado en una o dos líneas la primera vez que aparece.
Ordenado por aparición aproximada en la ruta.

## Fase 0 · Probar el plato entero

- **Robot bípedo:** robot que se sostiene y se desplaza sobre dos piernas, como una persona.
- **Humanoide:** robot con forma de cuerpo humano (torso, dos brazos, dos piernas).
- **Simulador:** programa que imita las leyes de la física para que un robot "virtual" se
  mueva como lo haría uno real, pero sin construirlo.
- **MuJoCo:** simulador de física para robots, rápido y gratuito, muy usado en investigación.
- **Política (*policy*):** la "mente" del robot; una función que, dado lo que el robot
  percibe, decide qué hacer con sus motores. En este curso será una red neuronal.
- **Observación:** lo que el robot percibe en un instante (ángulos de sus articulaciones,
  velocidades, inclinación…). Es la entrada de la política.
- **Acción:** lo que la política ordena a los motores (por ejemplo, a qué ángulo ir cada
  articulación). Es la salida de la política.
- **Recompensa (*reward*):** un número que le dice al robot cómo de bien lo está haciendo.
  Entrenar = buscar la política que consigue más recompensa.
- **Aprendizaje por refuerzo (RL, *reinforcement learning*):** forma de aprender probando:
  el robot actúa, recibe recompensa y ajusta su política para ganar más la próxima vez.
- **Entrenamiento:** el proceso de repetir millones de veces "actuar → recompensa → ajustar"
  hasta que la política se vuelve buena.
- **Episodio:** un intento completo, desde que el robot empieza hasta que se cae o se acaba
  el tiempo.
- **Paso de tiempo (*timestep*):** un "fotograma" de la simulación; el simulador avanza el
  mundo un instante pequeño (por ejemplo 2 milisegundos) en cada paso.
- **Sim-to-real:** llevar una política entrenada en el simulador a un robot físico real.
- **GPU (tarjeta gráfica):** procesador con miles de núcleos que hace muchísimas cuentas a la
  vez; por eso acelera el entrenamiento, que consiste en repetir la misma cuenta muchas veces.
- **CPU:** el procesador principal del ordenador; pocos núcleos pero muy flexibles.
- **Colab (Google Colaboratory):** servicio gratuito de Google que ejecuta notebooks en sus
  ordenadores y te presta una GPU por un rato.
- **Notebook (cuaderno):** documento que mezcla texto explicativo y celdas de código que se
  ejecutan una a una y muestran su resultado debajo.
- **Celda:** cada bloque de un notebook; puede ser de texto (markdown) o de código.
- **Vectorizar:** hacer una operación sobre muchos datos a la vez (en bloque) en lugar de uno
  por uno con un bucle; es la idea que hace rápida a la GPU y a NumPy.
- **Reward hacking (trampa de la recompensa):** cuando el robot encuentra una forma de ganar
  mucha recompensa que **no** es lo que queríamos (por ejemplo, vibrar en el sitio en vez de
  andar). Señal de que la recompensa está mal diseñada.
