"""andar: control clásico de la marcha de Zancudo (NB52).

Tubería: pisadas → ZMP de referencia → control por vista previa → CdM →
cinemática inversa → ángulos → servos de posición.
"""
import logging

from .plan import Marcha, Ganancias, zmp_de_referencia, ganancias_vista_previa, vista_previa, pies_en_el_tiempo
from .cinematica import ik_pierna, Cinematica
from .control import configurar_servos, Registro, ejecutar, Estado, PasoDeCaptura

__all__ = [
    "Marcha", "Ganancias", "zmp_de_referencia", "ganancias_vista_previa", "vista_previa", "pies_en_el_tiempo",
    "ik_pierna", "Cinematica",
    "configurar_servos", "Registro", "ejecutar", "Estado", "PasoDeCaptura",
]
__version__ = "0.1.0"

logging.getLogger(__name__).addHandler(logging.NullHandler())
