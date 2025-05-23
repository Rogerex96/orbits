class Satellite:
    def __init__(self, name, orbit, mass, fuel):
        self.name=name
        self.orbit=orbit
        self.mass=mass
        self.fuel=fuel
        
        
    def update_position(self, time):
        self.orbit.new_position(time)

def change_orbit(satellite, new_orbit):
    satellite.orbit = new_orbit

def relative_position_to(sat1, sat2):
    x1, y1 = sat1.orbit.x, sat1.orbit.y
    x2, y2 = sat2.orbit.x, sat2.orbit.y
    dx = x2 - x1
    dy = y2 - y1
    return (dx, dy)

import math

def change_orbit(satellite, new_orbit):
    isp=450
    g0=9.81
    mu=398600
    a1 = satellite.orbit.a
    a2 = new_orbit.a

    if a1 == a2:
        return True

    #Hohmann
    sqrt_mu_a1 = math.sqrt(mu / a1)
    sqrt_mu_a2 = math.sqrt(mu / a2)
    dv1 = sqrt_mu_a1 * (math.sqrt(2 * a2 / (a1 + a2)) - 1)
    dv2 = sqrt_mu_a2 * (1 - math.sqrt(2 * a1 / (a1 + a2)))
    delta_v = abs(dv1) + abs(dv2)

    #Tsiolkovsky
    m0 = satellite.mass
    exponent = delta_v / (isp * g0)
    mf = m0 / math.exp(exponent)
    fuel_needed = m0 - mf

    if satellite.fuel >= fuel_needed:
        satellite.mass = mf
        satellite.fuel -= fuel_needed
        satellite.orbit = new_orbit
        return True
    else:
        return False
