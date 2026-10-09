"""Pruebas del entorno: la API de Gymnasium, la observación, las semillas y la recompensa."""
import numpy as np
import pytest

from locomocion import TERMINOS, ZancudoLocomocion
from locomocion.config import cargar_config


def test_check_env_gymnasium(entorno):
    from gymnasium.utils.env_checker import check_env
    check_env(entorno, skip_render_check=True)


def test_check_env_sb3(entorno):
    sb3 = pytest.importorskip("stable_baselines3")   # si SB3 no está instalado, la prueba se salta
    from stable_baselines3.common.env_checker import check_env
    check_env(entorno, warn=True)


def test_forma_observacion(quieto):
    entorno, obs = quieto
    assert obs.shape == entorno.observation_space.shape == (50,)
    assert obs.dtype == np.float32


def test_gravedad_de_pie(quieto):
    entorno, obs = quieto
    assert obs[:3] == pytest.approx([0.0, 0.0, -1.0], abs=0.02)


def test_gravedad_inclinado(entorno):
    entorno.reset(seed=0)
    angulo = 0.3                                          # giramos el torso 0,3 rad alrededor de x
    entorno.datos.qpos[3:7] = [np.cos(angulo / 2), np.sin(angulo / 2), 0, 0]
    import mujoco
    mujoco.mj_forward(entorno.modelo, entorno.datos)
    gravedad = entorno._medir()["gravedad"]
    assert gravedad == pytest.approx([0.0, -np.sin(angulo), -np.cos(angulo)], abs=1e-9)


@pytest.mark.parametrize("semilla", [0, 1, 42])
def test_determinismo(config, acciones, semilla):
    resultados = []
    for _ in range(2):
        env = ZancudoLocomocion(config)
        obs, _ = env.reset(seed=semilla)
        recorrido = [obs]
        for accion in acciones:
            obs, r, terminado, truncado, _ = env.step(accion)
            recorrido.append(obs)
            if terminado or truncado:
                break
        resultados.append(np.array(recorrido))
        env.close()
    np.testing.assert_array_equal(resultados[0], resultados[1])


def test_semillas_distintas_dan_comandos_distintos(entorno):
    comandos = {tuple(entorno.reset(seed=s)[1]["comando"].round(6)) for s in range(10)}
    assert len(comandos) > 5


def test_comandos_dentro_de_rango(entorno):
    c = entorno.config.comandos
    for s in range(50):
        vx, vy, giro = entorno.reset(seed=s)[1]["comando"]
        assert c.vx[0] <= vx <= c.vx[1] and c.vy[0] <= vy <= c.vy[1] and c.giro[0] <= giro <= c.giro[1]


def test_accion_cero_es_postura_por_defecto(quieto):
    entorno, _ = quieto
    entorno.step(np.zeros(12, dtype=np.float32))
    np.testing.assert_allclose(entorno.datos.ctrl, entorno.ind.postura_defecto)


def test_terminos_registrados(config):
    assert set(config.recompensa.pesos) <= set(TERMINOS)


def test_peso_desconocido_avisa():
    config = cargar_config(cambios=["recompensa.pesos.velocida_vertical=-1.0"])
    with pytest.raises(KeyError, match="velocidad_vertical"):
        ZancudoLocomocion(config)


def test_suma_de_terminos(quieto):
    entorno, _ = quieto
    _, r, *_, info = entorno.step(np.zeros(12, dtype=np.float32))
    assert r == pytest.approx(sum(info["terminos"].values()))
