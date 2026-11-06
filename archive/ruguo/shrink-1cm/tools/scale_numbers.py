"""Every number in the episode, from stated assumptions (see FACTS.md)."""
import math
H0, H1 = 1.70, 0.01; s = H1 / H0            # 170 cm -> 1 cm
M0 = 60.0                                   # kg, assumed adult
m = M0 * s**3                               # kg
print(f"scale 1/{1/s:.0f}; area 1/{1/s**2:,.0f}; volume 1/{1/s**3:,.0f}")
print(f"mass {m*1e6:.1f} mg  (rice grain ~20-30 mg -> {m*1e6/25:.2f} grain)")
# strength: force ∝ L², assume a person can lift ~ own body weight
F0 = M0 * 9.81; F = F0 * s**2
print(f"strength {F*1e3:.1f} mN = lifts {F/(m*9.81):.0f}x own weight (assumption: normal person lifts ~1x own weight)")
# terminal velocity, belly-down: frontal area 0.7 m², Cd 1, rho 1.2
A = 0.7 * s**2; vt = math.sqrt(2*m*9.81/(1.2*1.0*A)); vt0 = math.sqrt(2*M0*9.81/(1.2*1.0*0.7))
print(f"terminal velocity {vt:.1f} m/s vs normal {vt0:.0f} m/s; Reynolds {vt*0.005/1.5e-5:.0f}")
# wet film: Haldane ~1/50 inch (0.5 mm); skin area 1.8 m²
film = 1.8 * s**2 * 0.5e-3 * 1000      # kg
print(f"water film {film*1e6:.0f} mg = {film/m:.1f}x body (normal: {1.8*0.5e-3*1000:.2f} kg = {1.8*0.5e-3*1000/M0*100:.1f}% of body)")
# raindrops
for d in (2, 5):
    md = 1000 * math.pi/6 * (d*1e-3)**3
    print(f"raindrop {d} mm: {md*1e6:.1f} mg = {md/m:.1f}x you")
# heat: resting human ~100 W lost through skin at ~20 °C, heat capacity 3500 J/kg/K
P_loss = 100 * s**2          # same heat-transfer coefficient (conservative: small bodies lose heat even faster)
P_make = 100 * s**3          # same metabolism per kg
C = m * 3500
rate = (P_loss - P_make) / C
print(f"cooling {rate:.3f} K/s -> 10 K in {10/rate/60:.1f} min (conservative)")
# food: to stay warm, metabolism per kg must rise ~1/s (loss/make ratio)
need = P_loss / P_make
kcal_day = 2000 * s**3 * need     # kcal/day
for name, e in (('cooked rice', 1.3), ('dry rice/seeds', 3.6)):
    print(f"food per day ({name}, {e} kcal/g): {kcal_day/e*1000:.1f} mg = {kcal_day/e/1000/m:.1f}x body")
print(f"Etruscan shrew 1.8 g = {1.8e-3/m:.0f}x you")
# ant scaled up to 1.7 m (x170): strength/weight drops 170x
print(f"ant lifting 20x own weight, scaled up 170x -> {20/170:.2f}x own weight")
