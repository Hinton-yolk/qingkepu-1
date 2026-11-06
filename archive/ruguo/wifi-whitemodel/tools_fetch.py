"""Fetch PLATEAU building CityGML for one 3rd-level mesh straight out of a ward's archive (HTTP range requests)."""
import sys, json, math, os, requests
from remotezip import RemoteZip

def mesh3(lat, lon):
    p = int(lat * 1.5); a = lat * 1.5 - p
    u = int(lon - 100); b = lon - 100 - u
    q = int(a * 8); v = int(b * 8)
    r = int((a * 8 - q) * 10); w = int((b * 8 - v) * 10)
    return f'{p:02d}{u:02d}{q}{v}{r}{w}'

cat = json.load(open('/tmp/claude-0/-home-user/faab7a4b-09b3-5a37-9867-56ebe2fb302d/scratchpad/plateau_catalog.json'))
sites = {'A_takashimadaira': ('13119', 35.7895, 139.6610), 'B_koenji': ('13115', 35.7050, 139.6490), 'C_shinjuku': ('13104', 35.6900, 139.6930)}
for key, (code, lat, lon) in sites.items():
    m = mesh3(lat, lon)
    entry = [x for x in cat['citygml'] if x['city_code'] == code][0]
    url = requests.head(entry['composite_url'], allow_redirects=True, timeout=60).url
    with RemoteZip(url) as z:
        names = [n for n in z.namelist() if n.startswith('udx/bldg/') and n.endswith('.gml')]
        hit = [n for n in names if os.path.basename(n).startswith(m)]
        print(key, entry['city'], entry['year'], 'mesh', m, '->', hit, f'({len(names)} bldg files in ward)')
        for n in hit:
            info = z.getinfo(n)
            print('   ', n, round(info.compress_size / 1e6, 1), 'MB zipped', round(info.file_size / 1e6, 1), 'MB')
            z.extract(n, 'data')
