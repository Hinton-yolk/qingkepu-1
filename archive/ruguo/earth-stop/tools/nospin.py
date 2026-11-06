"""Estimate where the oceans go if Earth's spin slowly stops.
Model (same idea as Fraczek/Esri): remove the centrifugal potential, keep the solid
Earth's shape and gravity, water follows the new equipotential:
    new sea level (relative to today's) S(lat) = C - (w^2 R^2 / 2g) cos^2(lat)
C is set so the ocean volume is conserved. Ignores water self-gravity, crust response,
and connectivity of basins (estimate)."""
import numpy as np, json, sys
w = 7.2921159e-5; R = 6.371e6; g = 9.81
A = w*w*R*R/(2*g)                              # metres
d = np.loadtxt(sys.argv[1] if len(sys.argv) > 1 else 'data/etopo_30m.csv', delimiter=',', skiprows=2)
lat = np.unique(d[:,0]); lon = np.unique(d[:,1])
Z = d[:,2].reshape(len(lat), len(lon))[:, :-1]; lon = lon[:-1]   # drop duplicate 180
LA = np.repeat(lat[:,None], len(lon), 1)
area = np.cos(np.radians(LA)) * (np.radians(.5)*R)**2            # cell area m^2
vol0 = np.sum(np.maximum(0, -Z) * area)
c2 = np.cos(np.radians(LA))**2
def vol(C): return np.sum(np.maximum(0, (C - A*c2) - Z) * area)
lo, hi = -2e4, 2e4
for _ in range(80):
    m = (lo+hi)/2
    (lo, hi) = (m, hi) if vol(m) < vol0 else (lo, m)
C = (lo+hi)/2
S = C - A*c2
wet0 = Z < 0; wet1 = Z < S
print(f"A (equator-pole equipotential shift) = {A/1000:.2f} km")
print(f"C (sea-level change at the poles) = {C/1000:+.2f} km; at equator {S[len(lat)//2,0]/1000:+.2f} km")
print(f"ocean fraction now {np.sum(area*wet0)/np.sum(area):.3f}, after {np.sum(area*wet1)/np.sum(area):.3f}")
for la in (0,10,20,23.1,30,31.2,39.9,45,50,55,60,70,90):
    s = C - A*np.cos(np.radians(la))**2
    print(f"  lat {la:5.1f}: sea level change {s/1000:+.2f} km")
# shoreline for land at old sea level: S=0
print("S=0 at lat", np.degrees(np.arccos(np.sqrt(C/A))))
def at(la, lo_):
    i = np.argmin(abs(lat-la)); j = np.argmin(abs(lon-lo_))
    return Z[i,j], S[i,j]
places = {'北京':(39.9,116.4,44),'上海':(31.2,121.5,4),'广州':(23.1,113.3,21),'哈尔滨':(45.75,126.6,150),'漠河':(52.97,122.5,433),
 'Chimborazo':(-1.47,-78.82,6263),'Kilimanjaro':(-3.07,37.35,5895),'伦敦':(51.5,-0.13,11),'莫斯科':(55.75,37.6,156),'纽约':(40.7,-74,10),
 '南海中部':(14,115,None),'马里亚纳海沟':(11.35,142.2,-10935),'新加坡':(1.35,103.8,15)}
for k,(la,lo_,h) in places.items():
    z,s = at(la,lo_); hh = z if h is None else h
    print(f"  {k}: elev {hh} m, new sea level {s:+.0f} m -> height above new sea {hh-s:+.0f} m")
# equatorial belt continuity: along each meridian, is the equator band dry?
dry = ~wet1
band = dry[(abs(LA)<=5)].reshape(-1, len(lon)) if False else None
eq = np.argmin(abs(lat))
print("dry fraction along equator:", dry[eq].mean())
# latitude extent of continuous land belt per longitude (from equator outwards)
ext=[]
for j in range(len(lon)):
    n=0
    while dry[eq+n, j] and eq+n < len(lat)-1: n+=1
    s_=0
    while dry[eq-s_, j] and eq-s_ > 0: s_+=1
    ext.append(((n-1)*.5 if n else -1, (s_-1)*.5 if s_ else -1))
ext=np.array(ext); print("north extent of equatorial land (deg) min/median/max", ext[:,0].min(), np.median(ext[:,0]), ext[:,0].max())
print("south extent", ext[:,1].min(), np.median(ext[:,1]), ext[:,1].max())
np.save('data/nospin_S.npy', S); np.save('data/etopo_Z.npy', Z)
json.dump({'C':C,'A':A}, open('data/nospin.json','w'))
