import math
class Satellite:
    def __init__(self, name, orbit, mass, fuel):
        self.name=name
        self.orbit=orbit
        self.mass=mass
        self.fuel=fuel
        
    def update_position(self, time):
        self.orbit.new_position(time)

def relative_position_to(sat1, sat2):
    x1, y1 = sat1.orbit.x, sat1.orbit.y
    x2, y2 = sat2.orbit.x, sat2.orbit.y
    dx = x2 - x1
    dy = y2 - y1
    return (dx, dy)


def change_orbit(satellite, new_orbit, now=0):
    EARTH_R = 6371.0                      # km
    isp, g0  = 450.0, 9.80665            # s, m/s²
    mu_km    = 3.986e5                   # km³/s²

    # punt i radi actuals
    x0, y0   = satellite.orbit.x, satellite.orbit.y
    r_now    = math.hypot(x0, y0)        # km

    # garanteix perigeu ≥ max(r_now, Terra)
    r_p = new_orbit.a * (1 - new_orbit.epsilon)
    if r_p < max(r_now, EARTH_R - 1e-3):
        new_orbit.epsilon = 1.0 - r_now / new_orbit.a
        new_orbit.b       = new_orbit.a * math.sqrt(1 - new_orbit.epsilon**2)

    # Δv: un únic impuls tangencial que eleva l’apogeu
    r1 = r_now
    r2 = new_orbit.a * (1 + new_orbit.epsilon)
    if abs(r2 - r1) < 1e-6:
        delta_v_ms = 0.0
    else:
        dv1_km = math.sqrt(mu_km / r1) * (math.sqrt(2 * r2 / (r1 + r2)) - 1)
        delta_v_ms = abs(dv1_km) * 1000.0

    if delta_v_ms == 0.0:
        return True

    # combustible (Tsiolkovski)
    m0 = satellite.mass
    mf = m0 / math.exp(delta_v_ms / (isp * g0))
    fuel_needed = m0 - mf
    if satellite.fuel < fuel_needed:
        return False

    # actualitza satèl·lit
    satellite.mass  = mf
    satellite.fuel -= fuel_needed

    # fase inicial M0 perquè passi per (x0, y0) a t = now
    cosE = max(-1.0, min(1.0, x0 / new_orbit.a + new_orbit.epsilon))
    sinE = y0 / new_orbit.b
    E    = math.atan2(sinE, cosE)
    M    = E - new_orbit.epsilon * math.sin(E)
    new_orbit.M0 = M - (2 * math.pi / new_orbit.period) * now

    satellite.orbit = new_orbit
    return True
