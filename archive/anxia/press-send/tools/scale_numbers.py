"""Every number in 「你按下『发送』之后」, from stated assumptions (see FACTS.md)."""
c = 299792.458            # km/s
n = 1.47                  # typical refractive index of silica fiber core (assumption)
v = c / n
print(f"light in fiber {v:,.0f} km/s ({v/c:.2f} c)")
for route in (1900, 2200, 2500):      # Beijing–Guangzhou: ~1,900 km straight line; cable routes follow roads/rail, assume 2,000–2,500 km
    print(f"  {route} km of fiber: {route/v*1000:.1f} ms")
air = (0.2, 1.0)           # phone→base station at each end, km (urban: hundreds of metres; assume 0.1–0.5 km each end)
for a in air:
    print(f"  wireless {a} km vs fiber 2000 km -> {a/2000*100:.3f}% of the path")
blink = (100, 400)         # ms (Harvard BioNumbers)
print(f"fiber leg ~10–12 ms is {blink[0]/12:.0f}–{blink[1]/10:.0f}x shorter than a blink")
L = 7499e4; earth = 40075
print(f"cable routes {L/1e4:.0f} 万 km = {L/earth:.0f} times round the Earth")
