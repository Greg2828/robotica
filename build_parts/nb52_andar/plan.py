"""Plan de la marcha: pisadas, ZMP de referencia y control por vista previa (Kajita, 2003)."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

G = 9.81
CENTRO_PIE = 0.04          # el centro de la planta está 4 cm por delante del tobillo
ALTURA_TOBILLO = 0.065     # altura del tobillo con el pie apoyado

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Marcha:
    """Parámetros de una marcha en línea recta (todo en metros y segundos)."""
    largo: float = 0.15
    n_pasos: int = 4
    t_simple: float = 0.5
    t_doble: float = 0.1
    t_inicio: float = 1.0
    t_final: float = 1.5
    altura_paso: float = 0.04
    z0: float = 0.71
    dt: float = 0.01

    def pisadas(self) -> NDArray[np.float64]:
        """Centros de las pisadas: la 0 es el pie derecho donde ya está; la última junta los pies."""
        xs = np.arange(self.n_pasos + 1) * self.largo
        return np.append(xs, xs[-1]) + CENTRO_PIE


@dataclass(frozen=True)
class Ganancias:
    A: NDArray[np.float64]
    B: NDArray[np.float64]
    C: NDArray[np.float64]
    k_integral: float
    k_estado: NDArray[np.float64]
    vista: NDArray[np.float64]


def _tramos(m: Marcha) -> list[tuple[float, float, float]]:
    """(ZMP al empezar, ZMP al acabar, duración) de cada tramo de la marcha."""
    p = m.pisadas()
    tramos = [(p[0], p[0], m.t_inicio)]
    for k in range(len(p) - 1):
        tramos.append((p[k], p[k], m.t_simple))       # apoyo simple sobre el pie k
        tramos.append((p[k], p[k + 1], m.t_doble))    # apoyo doble: el ZMP pasa al pie k + 1
    tramos.append((p[-1], p[-1], m.t_final))
    return tramos


def zmp_de_referencia(m: Marcha) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Instantes y ZMP de referencia, con rampas en los apoyos dobles."""
    trozos = []
    for inicio, fin, duracion in _tramos(m):
        n = round(duracion / m.dt)
        trozos.append(inicio + (fin - inicio) * np.arange(n) / n)
    zmp = np.concatenate(trozos)
    return np.arange(len(zmp)) * m.dt, zmp


def ganancias_vista_previa(z0: float, dt: float, n_vista: int, q: float = 1.0, r: float = 1e-6,
                           tolerancia: float = 1e-10, max_iter: int = 100_000) -> Ganancias:
    """Ganancias del control por vista previa: Riccati resuelta por iteración."""
    A = np.array([[1, dt, dt ** 2 / 2], [0, 1, dt], [0, 0, 1]])
    B = np.array([[dt ** 3 / 6], [dt ** 2 / 2], [dt]])
    C = np.array([[1, 0, -z0 / G]])
    Aa = np.zeros((4, 4)); Aa[0, 0] = 1; Aa[0, 1:] = C @ A; Aa[1:, 1:] = A
    Ba = np.vstack([C @ B, B])
    Q = np.diag([q, 0.0, 0.0, 0.0])
    R = np.array([[r]])
    P = Q.copy()
    for vuelta in range(max_iter):
        S = R + Ba.T @ P @ Ba
        P_nueva = Q + Aa.T @ P @ Aa - Aa.T @ P @ Ba @ np.linalg.solve(S, Ba.T @ P @ Aa)
        cambio = np.abs(P_nueva - P).max()
        P = P_nueva
        if cambio < tolerancia * np.abs(P).max():
            break
    else:
        raise RuntimeError("la iteración de Riccati no ha convergido")
    logger.debug("Riccati: %d vueltas", vuelta + 1)
    S = R + Ba.T @ P @ Ba
    K = np.linalg.solve(S, Ba.T @ P @ Aa)
    cerrado = Aa - Ba @ K
    vista = np.zeros(n_vista)
    vista[0] = -K[0, 0]
    X = -cerrado.T @ P @ np.array([[1.0], [0], [0], [0]])
    for j in range(1, n_vista):
        vista[j] = np.linalg.solve(S, Ba.T @ X)[0, 0]
        X = cerrado.T @ X
    return Ganancias(A, B, C, K[0, 0], K[0, 1:], vista)


def vista_previa(zmp_ref: NDArray[np.float64], g: Ganancias, x0: float | None = None
                 ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Estados del CdM (posición, velocidad, aceleración) y ZMP resultante, para un ZMP de referencia."""
    n_vista = len(g.vista)
    futuro = np.concatenate([zmp_ref, np.full(n_vista, zmp_ref[-1])])
    estado = np.array([zmp_ref[0] if x0 is None else x0, 0.0, 0.0])
    suma_error = 0.0
    estados, zmps = np.zeros((len(zmp_ref), 3)), np.zeros(len(zmp_ref))
    for k in range(len(zmp_ref)):
        zmp = (g.C @ estado)[0]
        suma_error += zmp - zmp_ref[k]
        sacudida = -g.k_integral * suma_error - g.k_estado @ estado - g.vista @ futuro[k + 1:k + 1 + n_vista]
        estado = g.A @ estado + g.B[:, 0] * sacudida
        estados[k], zmps[k] = estado, zmp
    return estados, zmps


def _quintico(s):
    return 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5


def pies_en_el_tiempo(m: Marcha) -> NDArray[np.float64]:
    """Tobillos (x, z) de los dos pies en cada instante: forma (n, 2, 2) = (instante, pie, coordenada)."""
    p = m.pisadas() - CENTRO_PIE
    n = round(sum(d for _, _, d in _tramos(m)) / m.dt)
    pies = np.zeros((n, 2, 2))
    pies[:, :, 0] = p[0]
    pies[:, :, 1] = ALTURA_TOBILLO
    inicio = m.t_inicio
    for k in range(len(p) - 1):
        vuela = 1 - k % 2                                   # paso 0: apoya el derecho, vuela el izquierdo
        i0, i1 = round(inicio / m.dt), round((inicio + m.t_simple) / m.dt)
        s = np.arange(i1 - i0) / (i1 - i0)
        desde = pies[i0 - 1, vuela, 0]
        pies[i0:i1, vuela, 0] = desde + (p[k + 1] - desde) * _quintico(s)
        pies[i0:i1, vuela, 1] = ALTURA_TOBILLO + m.altura_paso * 64 * s ** 3 * (1 - s) ** 3
        pies[i1:, vuela, 0] = p[k + 1]
        inicio += m.t_simple + m.t_doble
    return pies
