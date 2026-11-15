import numpy as np
import sys

def get_I_maks(R:int | float) -> int:
    if R > 600:
        I_maks = 130
    else:
        I_maks = 100
    return I_maks

def get_V_curve(R, h, I_maks):
    V = 0.291 * np.sqrt(R * (h + I_maks))
    return np.choose(V < 20, [V, 20])

def get_V_ramp(dh_dt_maks, h, L):
    return np.divide(dh_dt_maks * 3.6 * L, h, np.ones_like(h) * 100000, where=h!=0)

def get_L(V, dh_dt_maks, h):
    return (h * V) / (dh_dt_maks * 3.6)

def check_R(R:int | float):
    R_min = 190
    R_min_norm = 250
    if R < R_min:
        print(f"OBS: Radiusen til kurven ({R} m) er mindre enn minste krav ({R_min} m).")
    elif R < R_min_norm:
        print(f"OBS: Radiusen til kurven ({R} m) er mindre enn normale krav ({R_min_norm} m)")

def get_h(h_maks):
    h_avsp = (R - 100) / 2
    return np.minimum(h_maks, h_avsp)

def process_track(R, h_maks, I_maks, dh_dt_maks):
    h = get_h(h_maks)
    V = get_V_curve(R, h, I_maks)
    L = get_L(V, dh_dt_maks, h)
    return V, h, L

def process_track_L(R, h_maks, I_maks, dh_dt_maks, L):
    N = int(h_maks / 5 + 1)
    h_maks_values = np.linspace(0, h_maks, N)
    h_values = get_h(h_maks_values)
    V_c = get_V_curve(R, h_values, I_maks)
    V_r = get_V_ramp(dh_dt_maks, h_values, L)
    V_maks = np.minimum(V_c, V_r)
    i = np.argmax(V_maks)
    return V_maks[i], h_values[i], L

def get_angle(h):
    return np.arcsin(h / 1435) * (180 / np.pi)

def check_R_V(R_V:float | int, R_V_min:np.ndarray):
    if R_V < R_V_min[2]:
        print(f"OBS: Radiusen til vertikalkurven ({R_V} m) er mindre enn minste krav ({R_V_min[2]} m).")
    elif R < R_V_min[1]:
        print(f"OBS: Radiusen til kurven ({R_V} m) er mindre enn normale krav ({R_V_min[1]} m)")
    elif R < R_V_min[0]:
        print(f"OBS: Radiusen til kurven ({R_V} m) er mindre enn normale krav ({R_V_min[0]} m)")

def get_R_V_min(V:np.ndarray) -> np.ndarray:
    R_V_min = max(V**2 / 2.6, 4000)
    R_V_min_pers_norm = max(V**2 / 2.6, 4000)
    R_V_min_pers = max(V**2 / 3.9, 2500)
    return np.array([R_V_min, R_V_min_pers_norm, R_V_min_pers])

def get_V_vert(R_V:float|int) -> float|int:
    if R_V < 3125:
        V_vert = R_V / 20 - 25
    else:
        V_vert = R_V / 100 + 100
    return V_vert

def get_R_V(V):
    return np.maximum(np.choose(V < 131.25, [100 * (V - 100), 20 * (V + 25)]), get_R_V_min(V))

R = float(sys.argv[1])
check_R(R)

'''
try:
    L = float(sys.argv[2])
    med_L = True
except:
    med_L = False
    V, h, L = process_track(R, 150, 100, 46)
else:
    V, h, L = process_track_L(R, 150, 100, 46, L) # type: ignore
'''
if len(sys.argv) >= 3:
    L = float(sys.argv[2])
    V, h, L = process_track_L(R, 150, 100, 46, L) # type: ignore
else:
    V, h, L = process_track(R, 150, 100, 46)

'''
R_V_min = get_R_V_min(V)

try:
    R_V = float(sys.argv[3])
    med_R_V = True
except:
    med_R_V = False
    R_V = get_R_V(V)
else:
    check_R_V(R_V, R_V_min)
    V_vert = get_V_vert(R_V)
    V = np.minimum(V, V_vert)
'''

print(f"Gitt radius (R): {R} m. Høyeste tillatte hastighet (V): {V:.2f} km/h. Overhøyde (h): {h:.0f} mm (vinkel: {get_angle(h):.2f} grader). Lengde på rampe (L): {L:.2f} m.")