"""Reflectancias Sentinel-2 (20 m) de una fecha para la región: todas las bandas útiles en un GeoTIFF multibanda."""
import os, sys, numpy as np, rasterio, concurrent.futures as cf
from rasterio.windows import from_bounds
sys.path.insert(0, os.path.dirname(__file__))
from s2_series import url, X0, Y0, X1, Y1, NX, NY, TR, BAD_SCL
BANDS = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"]
def read_scene(sid):
    with rasterio.open(url(sid, "SCL")) as scl:
        b = scl.bounds
        xa, xb, ya, yb = max(b.left, X0), min(b.right, X1), max(b.bottom, Y0), min(b.top, Y1)
        if xa >= xb or ya >= yb: return sid, None
        win = from_bounds(xa, ya, xb, yb, scl.transform).round_offsets().round_lengths()
        s = scl.read(1, window=win); wtr = scl.window_transform(win)
        wb = rasterio.windows.bounds(win, scl.transform)
    out = np.zeros((len(BANDS),) + s.shape, np.uint16)
    for i, band in enumerate(BANDS):
        ds = rasterio.open(url(sid, band))
        if ds.res[0] < 15:
            ds.close(); ds = rasterio.open(url(sid, band), overview_level=0)
        w2 = from_bounds(*wb, ds.transform).round_offsets().round_lengths()
        out[i] = ds.read(1, window=w2, out_shape=s.shape)
        ds.close()
    bad = np.isin(s, BAD_SCL) | (out == 0).any(axis=0)
    out[:, bad] = 0
    col = int(round((wtr.c - X0) / 20)); row = int(round((Y1 - wtr.f) / 20))
    return sid, (row, col, out)
if __name__ == "__main__":
    name, sids = sys.argv[1], sys.argv[2:]
    mos = np.zeros((len(BANDS), NY, NX), np.uint16)
    with cf.ThreadPoolExecutor(5) as ex:
        res = dict(ex.map(read_scene, sids))
    for sid in sids:
        r = res[sid]
        if r is None: continue
        row, col, d = r
        r0, c0, r1, c1 = max(row, 0), max(col, 0), min(row + d.shape[1], NY), min(col + d.shape[2], NX)
        sub = d[:, r0 - row:r1 - row, c0 - col:c1 - col]; tgt = mos[:, r0:r1, c0:c1]
        fill = (tgt[0] == 0) & (sub[0] != 0)
        tgt[:, fill] = sub[:, fill]
    with rasterio.open(f"data/s2ts/bands_{name}.tif", "w", driver="GTiff", width=NX, height=NY, count=len(BANDS), dtype="uint16",
                       nodata=0, crs="EPSG:32613", transform=TR, compress="deflate", tiled=True) as o:
        o.write(mos)
    print(name, "ok", float((mos[0] > 0).mean()))
