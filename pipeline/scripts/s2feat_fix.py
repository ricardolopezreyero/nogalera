"""Asigna rasgos S2 por objeto usando la etiqueta raster bajo un punto interior del polígono (no el orden de la lista)."""
import json, numpy as np, rasterio, warnings
from shapely.geometry import shape
warnings.filterwarnings("ignore")
d = json.load(open("data/objects2_utm.geojson")); F = d["features"]
ref = rasterio.open("data/l10_c2.tif"); TR = ref.transform
ts = np.load("data/s2ts/ts.npy")
act = np.load("data/obj2_act.npy"); lost = np.load("data/obj2_lost.npy")
nd10 = rasterio.open("data/s2ts/ndvi10_2026-08.tif").read(1).astype(np.float32) / 10000
stats = {}
for name, lab in (("activa", act), ("perdida", lost)):
    n = int(lab.max())
    l20 = lab[::2, ::2][:ts.shape[1], :ts.shape[2]]
    cnt = np.bincount(l20.ravel(), minlength=n + 1).astype(np.float64)
    def mean20(a):
        a = np.nan_to_num(a, nan=0.0)
        return np.bincount(l20.ravel(), weights=a.ravel(), minlength=n + 1) / np.maximum(cnt, 1)
    win = mean20((ts[0] + ts[1]) / 2); spr = mean20(ts[3]); smin = mean20(np.nanmin(ts[3:10], 0)); smean = mean20(np.nanmean(ts[3:10], 0))
    c10 = np.bincount(lab.ravel(), minlength=n + 1).astype(np.float64)
    s1 = np.bincount(lab.ravel(), weights=nd10.ravel(), minlength=n + 1); s2 = np.bincount(lab.ravel(), weights=(nd10 ** 2).ravel(), minlength=n + 1)
    nstd = np.sqrt(np.maximum(s2 / np.maximum(c10, 1) - (s1 / np.maximum(c10, 1)) ** 2, 0))
    stats[name] = (lab, c10, win, spr, smin, smean, nstd)
bad = 0
for f in F:
    p = f["properties"]
    lab, c10, win, spr, smin, smean, nstd = stats[p["kind"]]
    g = shape(f["geometry"])
    pt = g.representative_point()
    col, row = ~TR * (pt.x, pt.y)
    k = int(lab[int(row), int(col)])
    if k == 0 or abs(c10[k] - p["cells"]) > 0.5:
        bad += 1; continue
    p.update(lab=k, win=float(win[k]), spr=float(spr[k]), smin=float(smin[k]), smean=float(smean[k]), nstd=float(nstd[k]))
json.dump(d, open("data/objects2_utm.geojson", "w"))
print("ok", len(F), "sin coincidencia", bad)
