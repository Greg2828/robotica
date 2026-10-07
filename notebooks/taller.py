"""taller.py — herramientas para las prácticas de MuJoCo del curso.

Al principio del curso usas estas funciones como una caja negra: las llamas y miras
lo que pasa. En el NB23 (funciones) y el NB24 (clases) abrirás este fichero, lo
leerás línea a línea y escribirás tu propia versión.

Funciones:
    cargar(nombre_o_xml)            -> (modelo, datos)
    foto(modelo, datos)             -> enseña una imagen de la simulación
    video(modelo, datos, segundos, control=None, nombre="video") -> enseña un vídeo
    poner_angulo(modelo, datos, articulacion, grados)   -> dobla una articulación (sin física)
    al_azar(semilla)                -> un "control" que mueve los motores al azar
"""
from __future__ import annotations

import os

os.environ.setdefault("MUJOCO_GL", "egl")      # dibujar sin pantalla (también en la Pi)

import imageio
import matplotlib.pyplot as plt
import mujoco
import numpy as np
from IPython.display import Video, display

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA_VIDEOS = os.path.join(AQUI, "assets", "practicas")

# Robots que se pueden cargar por su nombre.
_MODELOS = {
    "humanoide": "humanoid.xml",          # el humanoide de DeepMind/Gymnasium (NB00)
    "hopper": "hopper.xml",
    "walker": "walker2d_v5.xml",
    "pendulo": "inverted_pendulum.xml",
    "palo_escoba": "robots/palo_escoba.xml",   # nuestro carrito con palo (NB11 en adelante)
}


def _ruta_gymnasium(fichero: str) -> str:
    import gymnasium
    return os.path.join(os.path.dirname(gymnasium.__file__), "envs", "mujoco", "assets", fichero)


def cargar(nombre_o_xml: str):
    """Devuelve (modelo, datos).

    - Si le das un nombre conocido ("humanoide", "hopper"...), carga ese robot.
    - Si le das texto que empieza por "<", lo trata como un plano MJCF escrito por ti.
    - Si no, lo trata como la ruta de un fichero .xml.
    """
    if nombre_o_xml in _MODELOS:
        fichero = _MODELOS[nombre_o_xml]
        ruta = os.path.join(AQUI, fichero) if fichero.startswith("robots/") else _ruta_gymnasium(fichero)
        modelo = mujoco.MjModel.from_xml_path(ruta)
    elif nombre_o_xml.lstrip().startswith("<"):
        modelo = mujoco.MjModel.from_xml_string(nombre_o_xml)
    else:
        modelo = mujoco.MjModel.from_xml_path(nombre_o_xml)
    datos = mujoco.MjData(modelo)
    mujoco.mj_forward(modelo, datos)       # calcula posiciones sin avanzar el tiempo
    return modelo, datos


def _dibujante(modelo, alto, ancho):
    """Crea el "dibujante" de MuJoCo sin dejar que ensucie la salida con avisos técnicos."""
    import sys
    sys.stderr.flush()
    copia = os.dup(2)
    nulo = os.open(os.devnull, os.O_WRONLY)
    os.dup2(nulo, 2)                       # tapa los avisos de la tarjeta gráfica
    try:
        return mujoco.Renderer(modelo, alto, ancho)
    finally:
        os.dup2(copia, 2)
        os.close(nulo)
        os.close(copia)


def _camara(modelo, distancia=None, seguir=True):
    """Una cámara que mira al cuerpo 1 (el tronco) desde un lado y algo desde arriba."""
    cam = mujoco.MjvCamera()
    mujoco.mjv_defaultFreeCamera(modelo, cam)
    if seguir and modelo.nbody > 1:
        cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        cam.trackbodyid = 1
    cam.distance = distancia if distancia is not None else 3.5
    cam.elevation = -15
    cam.azimuth = 90
    return cam


def _imagen(modelo, datos, dibujante, cam):
    dibujante.update_scene(datos, camera=cam)
    return dibujante.render()


def foto(modelo, datos, distancia=None, seguir=True, ancho=480, alto=360, titulo=None):
    """Enseña una foto de cómo está ahora la simulación."""
    with _dibujante(modelo, alto, ancho) as dibujante:
        img = _imagen(modelo, datos, dibujante, _camara(modelo, distancia, seguir))
    plt.figure(figsize=(ancho / 100, alto / 100))
    plt.imshow(img)
    plt.axis("off")
    if titulo:
        plt.title(titulo)
    plt.show()
    return img


def video(modelo, datos, segundos=2.0, control=None, nombre="video",
          distancia=None, seguir=True, ancho=360, alto=270, fotos_por_segundo=30):
    """Simula `segundos` y enseña un vídeo (MP4, guardado en assets/practicas/).

    `control` es opcional: una función control(modelo, datos) que, en cada paso,
    escribe las órdenes de los motores en datos.ctrl. Si no hay, los motores no hacen nada.
    Devuelve la lista de fotos (por si quieres hacer algo con ellas).
    """
    os.makedirs(CARPETA_VIDEOS, exist_ok=True)
    pasos = int(round(segundos / modelo.opt.timestep))
    cada = max(1, int(round(1 / (fotos_por_segundo * modelo.opt.timestep))))
    cam = _camara(modelo, distancia, seguir)
    fotos = []
    with _dibujante(modelo, alto, ancho) as dibujante:
        for paso in range(pasos):
            if control is not None:
                control(modelo, datos)
            mujoco.mj_step(modelo, datos)
            if paso % cada == 0:
                fotos.append(_imagen(modelo, datos, dibujante, cam))
    ruta = os.path.join(CARPETA_VIDEOS, f"{nombre}.mp4")
    fps = 1 / (cada * modelo.opt.timestep)
    imageio.mimsave(ruta, fotos, fps=fps, macro_block_size=1)
    display(Video(ruta, embed=True, html_attributes="controls loop autoplay muted"))
    return fotos


def al_azar(semilla=0):
    """Devuelve una función de control que mueve cada motor al azar (como en el NB00)."""
    azar = np.random.default_rng(semilla)

    def control(modelo, datos):
        datos.ctrl[:] = azar.uniform(-1, 1, size=modelo.nu)

    return control


def poner_angulo(modelo, datos, articulacion, grados):
    """Coloca la articulación `articulacion` en `grados` grados, sin que pase el tiempo.

    Es como colocar a mano un muñeco articulado. Avisa si te sales de sus topes.
    """
    junta = modelo.joint(articulacion)
    minimo, maximo = np.degrees(junta.range)
    if modelo.jnt_limited[junta.id] and not (minimo <= grados <= maximo):
        print(f"Ojo: {articulacion} solo va de {minimo:.0f} a {maximo:.0f} grados; "
              f"{grados} se sale de sus topes.")
    datos.joint(articulacion).qpos = np.radians(grados)
    mujoco.mj_forward(modelo, datos)        # recalcula dónde queda cada pieza
