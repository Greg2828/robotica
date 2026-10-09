"""Configuración del entorno: dataclasses congeladas + YAML + cambios desde la línea de órdenes."""
from __future__ import annotations

import dataclasses
import difflib
import typing
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Simulacion:
    paso: float = 0.005          # s: el paso de la física (timestep de MuJoCo)
    decimacion: int = 4          # pasos de física por cada decisión de la política
    kp: float = 300.0            # rigidez de los servos (N·m/rad)
    kv: float = 10.0             # amortiguación de los servos (N·m·s/rad)
    escala_accion: float = 0.3   # rad: cuánto se aparta el objetivo de la postura por defecto con acción ±1

    def __post_init__(self):
        if self.paso <= 0 or self.decimacion < 1 or self.kp <= 0 or self.kv < 0 or self.escala_accion <= 0:
            raise ValueError(f"Simulacion: valores fuera de rango ({self})")

    @property
    def dt(self) -> float:
        """Tiempo entre dos decisiones de la política."""
        return self.paso * self.decimacion


@dataclass(frozen=True)
class Comandos:
    vx: tuple[float, float] = (-0.3, 0.6)       # m/s, hacia delante (en el marco del torso)
    vy: tuple[float, float] = (-0.2, 0.2)       # m/s, de lado
    giro: tuple[float, float] = (-0.5, 0.5)     # rad/s, alrededor del eje vertical
    prob_quieto: float = 0.1                     # fracción de episodios con la orden «quieto»

    def __post_init__(self):
        for nombre in ("vx", "vy", "giro"):
            bajo, alto = getattr(self, nombre)
            if bajo > alto:
                raise ValueError(f"Comandos.{nombre}: el mínimo ({bajo}) es mayor que el máximo ({alto})")
        if not 0.0 <= self.prob_quieto <= 1.0:
            raise ValueError("Comandos.prob_quieto debe estar entre 0 y 1")


PESOS_POR_DEFECTO = {
    "seguir_velocidad": 1.0,
    "seguir_giro": 1.0,
    "avance": 1.0,
    "vivo": 0.15,
    "contacto_fase": 0.5,
    "pie_en_el_aire": 2.0,
    "velocidad_vertical": -2.0,
    "balanceo": -0.05,
    "orientacion": -1.0,
    "altura": -10.0,
    "par": -1e-5,
    "accion_brusca": -0.01,
    "caderas": -1.0,
}


@dataclass(frozen=True)
class Recompensa:
    pesos: dict[str, float] = field(default_factory=lambda: dict(PESOS_POR_DEFECTO))
    sigma: float = 0.25              # anchura de la campana exp(−error²/σ)
    altura_objetivo: float = 0.75    # m: altura del torso que se premia
    periodo_paso: float = 0.8        # s: una vuelta del reloj de fase = dos pasos
    aire_objetivo: float = 0.3       # s: tiempo de pie en el aire que se premia

    def __post_init__(self):
        if self.sigma <= 0 or self.periodo_paso <= 0:
            raise ValueError("Recompensa: sigma y periodo_paso deben ser positivos")


@dataclass(frozen=True)
class Episodio:
    duracion: float = 10.0           # s
    altura_minima: float = 0.45      # m: por debajo, se ha caído
    inclinacion_maxima: float = 1.0  # rad: más inclinado, se ha caído
    ruido_articulaciones: float = 0.05   # rad: ruido de la postura inicial
    ruido_velocidades: float = 0.1       # rad/s y m/s: ruido de las velocidades iniciales

    def __post_init__(self):
        if self.duracion <= 0 or self.ruido_articulaciones < 0 or self.ruido_velocidades < 0:
            raise ValueError(f"Episodio: valores fuera de rango ({self})")


@dataclass(frozen=True)
class ConfigEntorno:
    nombre: str = "zancudo3d_andar"
    simulacion: Simulacion = field(default_factory=Simulacion)
    comandos: Comandos = field(default_factory=Comandos)
    recompensa: Recompensa = field(default_factory=Recompensa)
    episodio: Episodio = field(default_factory=Episodio)


# --------------------------------------------------------------------------------------------
# De diccionario (YAML) a dataclass, comprobando claves y tipos (la versión del NB53, ampliada
# con tuplas y diccionarios).

def _convertir(tipo, valor, donde: str):
    origen = typing.get_origin(tipo)
    if dataclasses.is_dataclass(tipo):
        return desde_dict(tipo, valor)
    if origen is tuple:
        if not isinstance(valor, (list, tuple)) or len(valor) != len(typing.get_args(tipo)):
            raise TypeError(f"{donde}: esperaba una lista de {len(typing.get_args(tipo))} números, llegó {valor!r}")
        return tuple(_convertir(t, v, donde) for t, v in zip(typing.get_args(tipo), valor))
    if origen is dict:
        if not isinstance(valor, dict):
            raise TypeError(f"{donde}: esperaba un diccionario, llegó {valor!r}")
        _, tipo_valor = typing.get_args(tipo)
        return {str(k): _convertir(tipo_valor, v, f"{donde}.{k}") for k, v in valor.items()}
    if tipo is float and isinstance(valor, int) and not isinstance(valor, bool):
        return float(valor)
    if not isinstance(valor, tipo) or isinstance(valor, bool) != (tipo is bool):
        raise TypeError(f"{donde}: esperaba {tipo.__name__}, llegó {valor!r} ({type(valor).__name__})")
    return valor


def desde_dict(clase, datos: dict):
    """Crea una dataclass (anidada) a partir de un diccionario, comprobando claves y tipos."""
    if not isinstance(datos, dict):
        raise TypeError(f"{clase.__name__}: esperaba un diccionario, llegó {type(datos).__name__}")
    tipos = typing.get_type_hints(clase)
    validos = {f.name for f in dataclasses.fields(clase)}
    for clave in datos:
        if clave not in validos:
            parecidas = difflib.get_close_matches(clave, validos, n=1)
            pista = f" ¿Querías decir '{parecidas[0]}'?" if parecidas else ""
            raise KeyError(f"{clase.__name__}: clave desconocida '{clave}'.{pista}")
    valores = {clave: _convertir(tipos[clave], valor, f"{clase.__name__}.{clave}") for clave, valor in datos.items()}
    return clase(**valores)


def fusionar(base: dict, cambios: dict) -> dict:
    """Copia de base con los cambios aplicados, entrando en los diccionarios anidados (NB53)."""
    resultado = dict(base)
    for clave, valor in cambios.items():
        if isinstance(valor, dict) and isinstance(resultado.get(clave), dict):
            resultado[clave] = fusionar(resultado[clave], valor)
        else:
            resultado[clave] = valor
    return resultado


def cambio_desde_texto(texto: str) -> dict:
    """'simulacion.kp=200' → {'simulacion': {'kp': 200}}. El valor se lee como YAML (¡con sus trampas!)."""
    if "=" not in texto:
        raise ValueError(f"cambio mal escrito: '{texto}' (forma: seccion.clave=valor)")
    ruta, valor = texto.split("=", 1)
    resultado: dict = yaml.safe_load(valor)
    for clave in reversed(ruta.strip().split(".")):
        resultado = {clave: resultado}
    return resultado


def a_dict(cfg: ConfigEntorno) -> dict:
    """La configuración como diccionario de tipos básicos (las tuplas, como listas), listo para YAML."""
    def limpiar(x):
        if isinstance(x, dict):
            return {k: limpiar(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [limpiar(v) for v in x]
        return x
    return limpiar(dataclasses.asdict(cfg))


def cargar_config(ruta: str | Path | None = None, cambios: list[str] | None = None) -> ConfigEntorno:
    """Configuración por defecto ← fichero YAML (opcional) ← cambios 'a.b=valor' (opcionales)."""
    datos = a_dict(ConfigEntorno())
    if ruta is not None:
        datos = fusionar(datos, yaml.safe_load(Path(ruta).read_text(encoding="utf-8")) or {})
    for cambio in cambios or []:
        datos = fusionar(datos, cambio_desde_texto(cambio))
    return desde_dict(ConfigEntorno, datos)


def guardar_config(cfg: ConfigEntorno, ruta: str | Path) -> None:
    Path(ruta).write_text(yaml.safe_dump(a_dict(cfg), sort_keys=False, allow_unicode=True), encoding="utf-8")
