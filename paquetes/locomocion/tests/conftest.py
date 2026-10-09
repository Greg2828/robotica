"""Fixtures compartidas por todas las pruebas (pytest las encuentra solo por el nombre del fichero)."""
import numpy as np
import pytest

from locomocion import ConfigEntorno, ZancudoLocomocion


@pytest.fixture(scope="session")
def config():
    """La configuración por defecto (una para toda la sesión: está congelada, nadie la puede estropear)."""
    return ConfigEntorno()


@pytest.fixture
def entorno(config):
    """Un entorno nuevo para cada prueba, que se cierra al terminar aunque la prueba falle."""
    env = ZancudoLocomocion(config)
    yield env
    env.close()


@pytest.fixture
def quieto(entorno):
    """El entorno reiniciado con la orden «quieto» y semilla 0."""
    obs, info = entorno.reset(seed=0, options={"comando": [0.0, 0.0, 0.0]})
    return entorno, obs


@pytest.fixture
def acciones():
    """Una secuencia fija de acciones al azar (siempre la misma)."""
    return np.random.default_rng(0).uniform(-1, 1, size=(50, 12)).astype(np.float32)
