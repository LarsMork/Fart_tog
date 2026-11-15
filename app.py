import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    R_mo = mo.ui.number(start=0, stop=10000, label="Radius (R)")
    med_L_mo = checkbox = mo.ui.checkbox(label="Gitt lengde L.")
    L_mo = mo.ui.number(start=0, stop=10000, label="Lengde (L)")
    mo.vstack([R_mo, med_L_mo, L_mo])
    return L_mo, R_mo, med_L_mo, mo


@app.cell
def _(L_mo, R_mo, med_L_mo):
    import numpy as np

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

    '''
    def check_R(R:int | float):
        R_min = 190
        R_min_norm = 250
        if R < R_min:
            print(f"OBS: Radiusen til kurven ({R} m) er mindre enn minste krav ({R_min} m).")
        elif R < R_min_norm:
            print(f"OBS: Radiusen til kurven ({R} m) er mindre enn normale krav ({R_min_norm} m)")
    '''

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
    R = R_mo.value
    #check_R(R)

    med_L = med_L_mo.value

    if med_L:
        L = L_mo.value
        V, h, L = process_track_L(R, 150, 100, 46, L) # type: ignore
    else:
        V, h, L = process_track(R, 150, 100, 46)

    V = np.floor(V / 5) * 5

    #mo.md(f"Gitt radius (R): {R} m. Høyeste tillatte hastighet (V): {V:.0f} km/h. Overhøyde (h): {h:.0f} mm (vinkel: {get_angle(h):.2f}$^\circ$). Lengde på rampe (L): {L:.2f} m.")
    return L, R, V, get_angle, h


@app.cell
def _(R, mo):
    R_min = 190
    R_min_norm = 250
    if R < R_min:
        warning = f"OBS: Radiusen til kurven ({R} m) er mindre enn minste krav ({R_min} m)."
    elif R < R_min_norm:
        warning = f"OBS: Radiusen til kurven ({R} m) er mindre enn normale krav ({R_min_norm} m)"

    mo.md(warning)
    return


@app.cell(hide_code=True)
def _(L, R, V, get_angle, h, mo):
    mo.md(rf"""
    Gitt radius (R): {R} m. Høyeste tillatte hastighet (V): {V:.0f} km/h. Overhøyde (h): {h:.0f} mm (vinkel: {get_angle(h):.2f}$^\circ$). Lengde på rampe (L): {L:.2f} m.
    """)
    return


if __name__ == "__main__":
    app.run()
