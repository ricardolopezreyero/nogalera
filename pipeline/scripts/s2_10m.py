"""Mosaico 10 m de la región para una fecha: NDVI (int16 x10000) y color verdadero (TCI, 3 bandas)."""
import os, sys, numpy as np, rasterio, concurrent.futures as cf
from rasterio.windows import from_bounds
sys.path.insert(0, os.path.dirname(__file__))
from s2_series import url, X0, Y0, X1, Y1, BAD_SCL
NX, NY = int((X1 - X0) / 10), int((Y1 - Y0) / 10)
TR = rasterio.Affine(10, 0, X0, 0, -10, Y1)
def read_scene(sid):
    with rasterio.open(url(sid, "B04")) as r:
        b = r.bounds
        xa, xb, ya, yb = max(b.left, X0), min(b.right, X1), max(b.bottom, Y0), min(b.top, Y1)
        if xa >= xb or ya >= yb: return sid, None
        win = from_bounds(xa, ya, xb, yb, r.transform).round_offsets().round_lengths()
        red = r.read(1, window=win).astype(np.float32); wtr = r.window_transform(win); rtr = r.transform
    with rasterio.open(url(sid, "B08")) as n:
        nir = n.read(1, window=win).astype(np.float32)
    with rasterio.open(url(sid, "TCI")) as t:
        tci = t.read(window=win)
    with rasterio.open(url(sid, "SCL")) as s:
        w2 = from_bounds(*rasterio.windows.bounds(win, rtr), s.transform)
        scl = s.read(1, window=w2.round_offsets().round_lengths(), out_shape=red.shape, resampling=rasterio.enums.Resampling.nearest)
    bad = np.isin(scl, BAD_SCL) | (red == 0) | (nir == 0)
    nd = np.where(bad, -32768, np.clip((nir - red) / np.maximum(nir + red, 1) * 10000, -10000, 10000)).astype(np.int16)
    tci[:, bad & (red == 0)] = 0
    col = int(round((wtr.c - X0) / 10)); row = int(round((Y1 - wtr.f) / 10))
    return sid, (row, col, nd, tci)
if __name__ == "__main__":
    name, sids = sys.argv[1], sys.argv[2:]
    ndm = np.full((NY, NX), -32768, np.int16); tcm = np.zeros((3, NY, NX), np.uint8)
    with cf.ThreadPoolExecutor(5) as ex:
        res = dict(ex.map(read_scene, sids))
    for sid in sids:
        r = res[sid]
        if r is None: continue
        row, col, nd, tci = r
        r0, c0, r1, c1 = max(row, 0), max(col, 0), min(row + nd.shape[0], NY), min(col + nd.shape[1], NX)
        sub = nd[r0-row:r1-row, c0-col:c1-col]; st = tci[:, r0-row:r1-row, c0-col:c1-col]
        tgt = ndm[r0:r1, c0:c1]; tt = tcm[:, r0:r1, c0:c1]
        fill = (tgt == -32768) & (sub != -32768)
        tgt[fill] = sub[fill]; tt[:, fill] = st[:, fill]
    prof = dict(driver="GTiff", width=NX, height=NY, crs="EPSG:32613", transform=TR, compress="deflate", tiled=True)
    with rasterio.open(f"data/s2ts/ndvi10_{name}.tif", "w", count=1, dtype="int16", nodata=-32768, **prof) as o: o.write(ndm, 1)
    with rasterio.open(f"data/s2ts/tci10_{name}.tif", "w", count=3, dtype="uint8", nodata=0, **prof) as o: o.write(tcm)
    print(name, "ok", float((ndm != -32768).mean()))
