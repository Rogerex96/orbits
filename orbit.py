import math
#KSA
class Orbit:
    def __init__(self, name, period, epsilon, a):
        self.name = name
        self.period = period
        self.epsilon = epsilon
        self.a = a
        #Semi-minor axis
        self.b = a * (1 - epsilon**2) ** 0.5
        self.x = 0
        self.y = 0

    def kepler_E(self, M):
        E = M
        for _ in range(20):
            f = E - self.epsilon * math.sin(E) - M
            f_prime = 1 - self.epsilon * math.cos(E)
            if f_prime != 0:
                E = E - f / f_prime
        return E

    def new_position(self, time):
        M = (2 * math.pi / self.period) * time
        E = self.kepler_E(M)
        self.x = self.a * (math.cos(E) - self.epsilon)
        self.y = self.b * math.sin(E)
