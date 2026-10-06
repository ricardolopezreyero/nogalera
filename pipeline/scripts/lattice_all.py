import sys, json, numpy as np, concurrent.futures as cf
sys.path.insert(0, "scripts")
from shapely.geometry import shape
d = json.load(open("data/objects2_utm.geojson")); F = d["features"]
def work(i):
    from lattice import score
    try:
        return i, score(shape(F[i]["geometry"]))
    except Exception as e:
        return i, (np.nan, np.nan, np.nan)
with cf.ProcessPoolExecutor(4) as ex:
    for i, (s, sp, pm) in ex.map(work, range(len(F)), chunksize=8):
        F[i]["properties"].update(lat=s, lat_sp=sp, lat_pm=pm)
json.dump(d, open("data/objects2_utm.geojson", "w"))
lat = np.array([f["properties"]["lat"] for f in F], dtype=float)
print("n", len(F), "nan", np.isnan(lat).sum(), "pct", np.nanpercentile(lat, [10, 25, 50, 75, 90]).round(3))
