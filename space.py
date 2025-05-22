from orbit import Orbit
from satellite import Satellite
import matplotlib.pyplot as plt
import matplotlib.patches as patches
class Space:
    def __init__(self):
        self.orbits=[]
        self.satellites=[]

def get_orbit(space, name):
    for orbit in space.orbits:
        if orbit.name == name:
            return orbit
    return None

def update_all_positions(space, time):
    for sat in space.satellites:
        sat.update_position(time)

def load_orbits(space, filename):
    space.orbits.clear()
    try:
        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 4:
                    continue
                name, period, epsilon, a = parts
                orbit = Orbit(name, float(period), float(epsilon), float(a))
                space.orbits.append(orbit)
    except FileNotFoundError:
        print(f"ERROR: No s'ha trobat el fitxer {filename}")
    except Exception as e:
        print(f"ERROR llegint òrbites: {e}")

def save_orbits(space, filename):
    try:
        with open(filename, "w") as f:
            for orbit in space.orbits:
                f.write(f"{orbit.name} {orbit.period} {orbit.epsilon} {orbit.a}\n")
    except Exception as e:
        print(f"ERROR escrivint òrbites: {e}")



def load_satellites(space, filename):
    space.satellites.clear()
    try:
        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 4:
                    continue
                name, orbit_name, mass, fuel = parts
                orbit = get_orbit(space, orbit_name)
                if orbit:
                    satellite = Satellite(name, orbit, float(mass), float(fuel))
                    space.satellites.append(satellite)
    except FileNotFoundError:
        print(f"ERROR: No s'ha trobat el fitxer {filename}")
    except Exception as e:
        print(f"ERROR llegint satèl·lits: {e}")

def save_satellites(space, filename):
    try:
        with open(filename, "w") as f:
            for sat in space.satellites:
                f.write(f"{sat.name} {sat.orbit.name} {sat.mass} {sat.fuel}\n")
    except Exception as e:
        print(f"ERROR escrivint satèl·lits: {e}")

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_space(space):
    fig, ax = plt.subplots(figsize=(8, 8))

    terra = patches.Circle((0, 0), 6371, color='lightblue', label='Terra')
    ax.add_patch(terra)

    for orbit in space.orbits:
        x_center = -orbit.a * orbit.epsilon
        ellipse = patches.Ellipse(
            (x_center, 0), width=2 * orbit.a, height=2 * orbit.b,
            fill=False, color='blue', linestyle='--'
        )
        ax.add_patch(ellipse)

    for sat in space.satellites:
        x, y = sat.orbit.x, sat.orbit.y
        ax.plot(x, y, 'ro')
        ax.text(x + 300, y + 300, sat.name, fontsize=8)

    ax.set_aspect('equal')
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_title("Òrbites i satèl·lits al voltant de la Terra")
    ax.grid(True)
    plt.legend()
    plt.show()

