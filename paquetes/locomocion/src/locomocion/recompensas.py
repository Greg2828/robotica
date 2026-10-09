"""Recompensa modular: cada término es una función pequeña, registrada con un nombre.

La recompensa total = Σ peso[nombre] · término[nombre] · dt. Los pesos viven en la configuración.
"""
from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Callable

import numpy as np

from .config import Recompensa


@dataclass
class Medidas:
    """Todo lo que los términos necesitan saber de un paso (se calcula una vez y se comparte)."""
    comando: np.ndarray            # (vx, vy, giro) pedidos
    vel_lineal: np.ndarray         # velocidad del torso en SU marco (3)
    vel_angular: np.ndarray        # velocidad angular del torso en su marco (3)
    gravedad: np.ndarray           # gravedad proyectada en el marco del torso (3)
    altura: float                  # altura del torso (m)
    pares: np.ndarray              # pares de los motores (12)
    accion: np.ndarray             # acción de este paso (12)
    accion_anterior: np.ndarray    # acción del paso anterior (12)
    articulaciones: np.ndarray     # ángulos relativos a la postura por defecto (12)
    contacto: np.ndarray           # ¿pie en el suelo? (2, bool)
    primer_contacto: np.ndarray    # ¿acaba de aterrizar? (2, bool)
    tiempo_aire: np.ndarray        # cuánto llevaba en el aire al aterrizar (2, s)
    fase: float                    # reloj de la marcha, de 0 a 1


Termino = Callable[[Medidas, Recompensa], float]
TERMINOS: dict[str, Termino] = {}


def termino(nombre: str) -> Callable[[Termino], Termino]:
    """Decorador que registra una función como término de la recompensa."""
    def registrar(funcion: Termino) -> Termino:
        if nombre in TERMINOS:
            raise ValueError(f"término repetido: {nombre}")
        TERMINOS[nombre] = funcion
        return funcion
    return registrar


# --- lo que se premia ------------------------------------------------------------------------
@termino("seguir_velocidad")
def _seguir_velocidad(m: Medidas, cfg: Recompensa) -> float:
    error = np.sum((m.comando[:2] - m.vel_lineal[:2]) ** 2)
    return float(np.exp(-error / cfg.sigma))


@termino("seguir_giro")
def _seguir_giro(m: Medidas, cfg: Recompensa) -> float:
    return float(np.exp(-(m.comando[2] - m.vel_angular[2]) ** 2 / cfg.sigma))


@termino("vivo")
def _vivo(m: Medidas, cfg: Recompensa) -> float:
    return 1.0


@termino("avance")
def _avance(m: Medidas, cfg: Recompensa) -> float:
    """Cuánto se avanza EN LA DIRECCIÓN de la orden, en fracción de lo pedido (de −1 a 1)."""
    pedida = m.comando[:2]
    rapidez = float(np.linalg.norm(pedida))
    if rapidez < 0.1:
        return 0.0
    hacia = float(np.dot(m.vel_lineal[:2], pedida)) / rapidez        # proyección sobre la dirección pedida
    return float(np.clip(hacia / rapidez, -1.0, 1.0))


@termino("contacto_fase")
def _contacto_fase(m: Medidas, cfg: Recompensa) -> float:
    """+1 por cada pie que está donde dice el reloj: derecho apoyado en la 1.ª mitad, izquierdo en la 2.ª."""
    if np.linalg.norm(m.comando) < 0.1:
        return float(np.sum(m.contacto))                      # orden «quieto»: los dos pies en el suelo
    debe_apoyar = np.array([m.fase < 0.55, m.fase >= 0.45])   # un poco de apoyo doble
    return float(np.sum(m.contacto == debe_apoyar))


@termino("pie_en_el_aire")
def _pie_en_el_aire(m: Medidas, cfg: Recompensa) -> float:
    """Al aterrizar: premio si el pie ha estado en el aire más que aire_objetivo (pasos de verdad)."""
    if np.linalg.norm(m.comando[:2]) < 0.1:
        return 0.0
    return float(np.sum((m.tiempo_aire - cfg.aire_objetivo) * m.primer_contacto))


# --- lo que se castiga (pesos negativos) -------------------------------------------------------
@termino("velocidad_vertical")
def _velocidad_vertical(m: Medidas, cfg: Recompensa) -> float:
    return float(m.vel_lineal[2] ** 2)


@termino("balanceo")
def _balanceo(m: Medidas, cfg: Recompensa) -> float:
    return float(np.sum(m.vel_angular[:2] ** 2))


@termino("orientacion")
def _orientacion(m: Medidas, cfg: Recompensa) -> float:
    return float(np.sum(m.gravedad[:2] ** 2))


@termino("altura")
def _altura(m: Medidas, cfg: Recompensa) -> float:
    return float((m.altura - cfg.altura_objetivo) ** 2)


@termino("par")
def _par(m: Medidas, cfg: Recompensa) -> float:
    return float(np.sum(m.pares ** 2))


@termino("accion_brusca")
def _accion_brusca(m: Medidas, cfg: Recompensa) -> float:
    return float(np.sum((m.accion - m.accion_anterior) ** 2))


CADERAS_GIRO_LADO = [0, 1, 6, 7]   # cadera_giro y cadera_lado de las dos piernas


@termino("caderas")
def _caderas(m: Medidas, cfg: Recompensa) -> float:
    return float(np.sum(m.articulaciones[CADERAS_GIRO_LADO] ** 2))


# ----------------------------------------------------------------------------------------------
def comprobar_pesos(pesos: dict[str, float]) -> None:
    """Error claro si la configuración nombra un término que no existe (con pista si es una errata)."""
    for nombre in pesos:
        if nombre not in TERMINOS:
            parecidas = difflib.get_close_matches(nombre, TERMINOS, n=1)
            pista = f" ¿Querías decir '{parecidas[0]}'?" if parecidas else ""
            raise KeyError(f"término de recompensa desconocido: '{nombre}'.{pista}")


def calcular(m: Medidas, cfg: Recompensa, dt: float) -> tuple[float, dict[str, float]]:
    """Recompensa total y cada término por separado (ya multiplicado por su peso y por dt)."""
    partes = {nombre: peso * TERMINOS[nombre](m, cfg) * dt for nombre, peso in cfg.pesos.items() if peso != 0.0}
    return sum(partes.values()), partes
