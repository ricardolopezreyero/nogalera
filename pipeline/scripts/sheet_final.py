import sys, json
sys.path.insert(0, "scripts")
from sheet import render
from shapely.geometry import shape
from shapely.ops import transform as stf
from pyproj import Transformer
to_utm = Transformer.from_crs(4326, 32613, always_xy=True).transform
d = json.load(open("data/nogaleras_full.geojson"))
ids = [int(x) for x in sys.argv[2].split(",")]
byid = {f["properties"]["id"]: f for f in d["features"]}
items = []
for i in ids:
    f = byid[i]; p = f["properties"]
    items.append((f"N{i} {p['estado'][:4]} {p['area_m2']/1e4:.1f}ha ${p.get('precio_m2','-')}/m2 {p['municipio'][:10]}", stf(to_utm, shape(f["geometry"]))))
render(items, sys.argv[1])
print("ok")
