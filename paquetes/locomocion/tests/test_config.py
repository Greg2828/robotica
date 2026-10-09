"""Pruebas de la configuración: YAML de ida y vuelta, cambios desde texto y errores claros."""
import pytest
import yaml

from locomocion.config import ConfigEntorno, a_dict, cargar_config, cambio_desde_texto, desde_dict, guardar_config


def test_ida_y_vuelta_yaml(config):
    texto = yaml.safe_dump(a_dict(config))
    assert desde_dict(ConfigEntorno, yaml.safe_load(texto)) == config


def test_guardar_y_cargar(config, tmp_path):
    ruta = tmp_path / "config.yaml"           # tmp_path: una carpeta temporal nueva para cada prueba
    guardar_config(config, ruta)
    assert cargar_config(ruta) == config


def test_cambio_desde_texto():
    assert cambio_desde_texto("simulacion.kp=200") == {"simulacion": {"kp": 200}}


def test_cambios_se_aplican():
    config = cargar_config(cambios=["simulacion.kp=200", "recompensa.pesos.par=-1.0e-4"])
    assert config.simulacion.kp == 200.0
    assert config.recompensa.pesos["par"] == -1e-4
    assert config.recompensa.pesos["vivo"] == ConfigEntorno().recompensa.pesos["vivo"]   # el resto, igual


@pytest.mark.parametrize("cambio, error", [
    ("simulacion.kpp=200", KeyError),            # errata
    ("simulacion.kp=1e-3", TypeError),           # la trampa de YAML 1.1: «1e-3» es texto
    ("simulacion.decimacion=0", ValueError),     # fuera de rango
    ("comandos.vx=[0.5, 0.1]", ValueError),      # mínimo > máximo
])
def test_cambios_malos(cambio, error):
    with pytest.raises(error):
        cargar_config(cambios=[cambio])
