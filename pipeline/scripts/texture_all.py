import sys, json, numpy as np, concurrent.futures as cf
sys.path.insert(0, "scripts")
from shapely.geometry import shape
d = json.load(open("data/objects2_utm.geojson")); F = d["features"]
def work(i):
    from lattice import texture
    try: return i, texture(shape(F[i]["geometry"]))
    except Exception: return i, (np.nan, np.nan, np.nan)
with cf.ProcessPoolExecutor(4) as ex:
    for i, (con, f5, hs) in ex.map(work, range(len(F)), chunksize=8):
        F[i]["properties"].update(con=con, f5=f5, hstd=hs)
json.dump(d, open("data/objects2_utm.geojson", "w"))
print("ok", len(F))
