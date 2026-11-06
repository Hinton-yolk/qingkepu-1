import numpy as np, sys
from PIL import Image
R=6.371e6
d=np.loadtxt('data/etopo_30m.csv',delimiter=',',skiprows=2)
lat=np.unique(d[:,0]); lon=np.unique(d[:,1])
Z=d[:,2].reshape(len(lat),len(lon))[:,:-1]; lon=lon[:-1]
LA=np.repeat(lat[:,None],len(lon),1); LO=np.repeat(lon[None,:],len(lat),0)
area=np.cos(np.radians(LA))*(np.radians(.5)*R)**2
vol0=np.sum(np.maximum(0,-Z)*area); c2=np.cos(np.radians(LA))**2
def solve(A):
    lo,hi=-3e4,3e4
    for _ in range(80):
        m=(lo+hi)/2
        v=np.sum(np.maximum(0,(m-A*c2)-Z)*area)
        (lo,hi)=(m,hi) if v<vol0 else (lo,m)
    return (lo+hi)/2
places={'北京':(39.9,116.4,44),'天津':(39.1,117.2,5),'上海':(31.2,121.5,4),'广州':(23.1,113.3,21),'哈尔滨':(45.75,126.6,150),'沈阳':(41.8,123.4,55),
 '伦敦':(51.5,-0.13,11),'莫斯科':(55.75,37.6,156),'纽约':(40.7,-74,10),'新加坡':(1.35,103.8,15),'海口':(20.0,110.3,10)}
for A in (7700.,11000.,21385.):
    C=solve(A); S=C-A*c2; wet=Z<S
    eq=np.argmin(abs(lat))
    print(f"\nA={A/1000:.1f} km: poles {C/1000:+.2f} km, equator {(C-A)/1000:+.2f} km, shoreline(lat for old 0 m) {np.degrees(np.arccos(np.sqrt(max(0,min(1,C/A))))):.1f}, ocean frac {np.sum(area*wet)/np.sum(area):.3f}, dry along equator {1-wet[eq].mean():.2f}")
    # fraction of land N of 60 flooded, ocean between 20S-20N drained
    tro=(abs(LA)<20)
    print("   tropical ocean drained frac", np.sum(area*(tro&(Z<0)&~wet))/np.sum(area*(tro&(Z<0))), " land>50N flooded frac", np.sum(area*((LA>50)&(Z>=0)&wet))/np.sum(area*((LA>50)&(Z>=0))))
    for k,(la,lo_,h) in places.items():
        s=C-A*np.cos(np.radians(la))**2
        print(f"   {k}: sea level {s:+.0f} m -> {'水下 %d m'%(s-h) if s>h else '高出海面 %d m'%(h-s)}")
    # map
    img=np.zeros(Z.shape+(3,),np.uint8)
    img[~wet]=(200,190,160); img[wet]=(40,70,120)
    img[(Z<0)&~wet]=(230,170,90)   # former seabed now dry
    img[(Z>=0)&wet]=(90,140,200)    # former land now flooded
    Image.fromarray(img[::-1]).resize((1440,720),Image.NEAREST).save(f'review/nospin_A{int(A/1000)}.png')
