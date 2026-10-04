# zancudo_alterno.py — Zancudo que debe TURNARSE las piernas (NB44, sección 9)
# Hereda todo de ZancudoMoldeado (y este, de Zancudo) y solo AÑADE un término a la recompensa.
import numpy as np
import gymnasium as gym

from zancudo_moldeado import ZancudoMoldeado


class ZancudoAlterno(ZancudoMoldeado):

    def __init__(self, peso_alterna=1.0, **kwargs):
        super().__init__(**kwargs)
        self.peso_alterna = peso_alterna

    def pies_deseados(self):
        # el mismo reloj que ve la política (NB43): una vuelta cada 0,8 s
        seno = np.sin(2 * np.pi * self.pasos * self.dt / 0.8)
        if seno > 0.3:
            return [True, False]       # media vuelta: apoya el derecho, el izquierdo en el aire
        if seno < -0.3:
            return [False, True]       # la otra media: al revés
        return None                    # en los cambios, los dos valen (apoyo doble)

    def step(self, accion):
        observacion, recompensa, caido, truncado, info = super().step(accion)
        deseados = self.pies_deseados()
        if deseados is None:
            r_alterna = 1.0
        else:
            tocan = self.pies_en_el_suelo()
            r_alterna = np.mean([t == d for t, d in zip(tocan, deseados)])   # 1, 0,5 o 0
        recompensa = recompensa + self.peso_alterna * r_alterna
        info.update(r_alterna=r_alterna)
        return observacion, recompensa, caido, truncado, info


gym.register(id="ZancudoAlterno-v0", entry_point=ZancudoAlterno)


class ZancudoZancada(ZancudoAlterno):
    # NB44, sección 8, segundo intento: el pie que vuela debe ADELANTAR al que apoya

    def __init__(self, peso_zancada=1.0, peso_alterna=0.5, **kwargs):
        super().__init__(peso_alterna=peso_alterna, **kwargs)
        self.peso_zancada = peso_zancada

    def separacion_deseada(self):
        # distancia (izquierdo − derecho) que queremos ahora: de −0,2 m a +0,2 m en la primera
        # media vuelta (el izquierdo vuela y adelanta) y de vuelta a −0,2 m en la segunda
        fase = 2 * np.pi * self.pasos * self.dt / 0.8
        return -0.2 * np.cos(fase)

    def step(self, accion):
        observacion, recompensa, caido, truncado, info = super().step(accion)
        x_der, x_izq = [self.datos.geom_xpos[pie][0] for pie in self.pies]
        separacion = x_izq - x_der
        r_zancada = np.exp(-((separacion - self.separacion_deseada()) ** 2) / 0.02)    # la campana, otra vez
        recompensa = recompensa + self.peso_zancada * r_zancada
        info.update(r_zancada=r_zancada, separacion=separacion)
        return observacion, recompensa, caido, truncado, info


gym.register(id="ZancudoZancada-v0", entry_point=ZancudoZancada)
