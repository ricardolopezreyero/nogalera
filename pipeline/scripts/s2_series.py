"""Serie de NDVI Sentinel-2 L2A (20 m) para la región, mosaico de teselas FJ/FH/GJ por fecha."""
import os, sys, numpy as np, rasterio, concurrent.futures as cf
from rasterio.windows import from_bounds, Window
from pyproj import Transformer
os.environ.update(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
                  GDAL_HTTP_MULTIRANGE="YES", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", GDAL_HTTP_MAX_RETRY="5", GDAL_HTTP_RETRY_DELAY="2")
B = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/13/R"
W_, S_, E_, N_ = -104.00, 25.15, -102.60, 26.30
t = Transformer.from_crs(4326, 32613, always_xy=True)
xs, ys = zip(*[t.transform(x, y) for x in (W_, E_) for y in (S_, N_)])
X0, X1 = np.floor(min(xs) / 20) * 20, np.ceil(max(xs) / 20) * 20
Y0, Y1 = np.floor(min(ys) / 20) * 20, np.ceil(max(ys) / 20) * 20
NX, NY = int((X1 - X0) / 20), int((Y1 - Y0) / 20)
TR = rasterio.Affine(20, 0, X0, 0, -20, Y1)
BAD_SCL = np.array([0, 1, 3, 8, 9, 10])

SLOTS = {
 "2025-12": ["S2C_13RFJ_20251227_0_L2A", "S2C_13RFH_20251227_0_L2A", "S2C_13RGJ_20251227_0_L2A", "S2C_13RFK_20251227_0_L2A", "S2C_13RGK_20251227_0_L2A"],
 "2026-01": ["S2C_13RFJ_20260126_0_L2A", "S2C_13RFH_20260126_0_L2A", "S2C_13RGJ_20260126_0_L2A", "S2C_13RFK_20260126_0_L2A", "S2C_13RGK_20260126_0_L2A"],
 "2026-03": ["S2C_13RFJ_20260317_0_L2A", "S2C_13RFH_20260317_0_L2A", "S2C_13RGJ_20260317_0_L2A", "S2C_13RFK_20260317_0_L2A", "S2C_13RGK_20260317_0_L2A"],
 "2026-04": ["S2C_13RFJ_20260416_0_L2A", "S2C_13RFH_20260416_0_L2A", "S2C_13RGJ_20260416_0_L2A", "S2C_13RFK_20260416_0_L2A", "S2C_13RGK_20260416_0_L2A"],
 "2026-05a": ["S2C_13RFJ_20260506_0_L2A", "S2C_13RFH_20260506_0_L2A", "S2C_13RGJ_20260506_0_L2A", "S2C_13RFK_20260506_0_L2A", "S2C_13RGK_20260506_0_L2A"],
 "2026-05b": ["S2A_13RFJ_20260528_0_L2A", "S2A_13RFH_20260528_0_L2A", "S2A_13RGJ_20260528_0_L2A", "S2A_13RFK_20260528_0_L2A", "S2A_13RGK_20260528_0_L2A"],
 "2026-06": ["S2C_13RFJ_20260625_0_L2A", "S2C_13RFH_20260625_0_L2A", "S2C_13RGJ_20260625_0_L2A", "S2C_13RFK_20260625_0_L2A", "S2C_13RGK_20260625_0_L2A"],
 "2026-07": ["S2B_13RFJ_20260730_0_L2A", "S2B_13RFH_20260730_0_L2A", "S2B_13RGJ_20260730_0_L2A", "S2B_13RFK_20260730_0_L2A", "S2B_13RGK_20260730_0_L2A"],
 "2026-08": ["S2C_13RFJ_20260824_0_L2A", "S2C_13RFH_20260824_0_L2A", "S2C_13RGJ_20260824_0_L2A", "S2C_13RFK_20260824_0_L2A", "S2C_13RGK_20260824_0_L2A"],
 "2026-09": ["S2C_13RFJ_20260913_0_L2A", "S2C_13RFH_20260913_0_L2A", "S2C_13RGJ_20260903_0_L2A", "S2C_13RFK_20260903_0_L2A", "S2C_13RGK_20260903_0_L2A"],
}

def url(sid, band):
    tile = sid.split("_")[1]  # 13RFJ
    y, m = sid.split("_")[2][:4], int(sid.split("_")[2][4:6])
    return f"/vsicurl/{B}/{tile[3]}{tile[4]}/{y}/{m}/{sid}/{band}.tif".replace(f"{B}/{tile[3]}{tile[4]}", f"{B}/{tile[3:5]}")

def read_scene(sid):
    out = {}
    with rasterio.open(url(sid, "SCL")) as scl:
        b = scl.bounds
        xa, xb = max(b.left, X0), min(b.right, X1)
        ya, yb = max(b.bottom, Y0), min(b.top, Y1)
        if xa >= xb or ya >= yb: return sid, None
        win = from_bounds(xa, ya, xb, yb, scl.transform).round_offsets().round_lengths()
        s = scl.read(1, window=win)
        wtr = scl.window_transform(win)
    bands = {}
    for band in ("B04", "B08"):
        with rasterio.open(url(sid, band), overview_level=0) as ds:  # vista 20 m
            w2 = from_bounds(*rasterio.windows.bounds(win, scl.transform), ds.transform).round_offsets().round_lengths()
            bands[band] = ds.read(1, window=w2, out_shape=s.shape).astype(np.float32)
    r, n = bands["B04"], bands["B08"]  # los COG de Earth Search ya traen el offset BOA aplicado
    ndvi = (n - r) / np.maximum(n + r, 1)
    bad = np.isin(s, BAD_SCL) | (bands["B04"] == 0) | (bands["B08"] == 0)
    nd = np.where(bad, -32768, np.clip(ndvi * 10000, -10000, 10000)).astype(np.int16)
    col = int(round((wtr.c - X0) / 20)); row = int(round((Y1 - wtr.f) / 20))
    return sid, (row, col, nd)

if __name__ == "__main__":
    os.makedirs("data/s2ts", exist_ok=True)
    print("grid", NX, NY, X0, Y0, X1, Y1, flush=True)
    for slot, sids in SLOTS.items():
        dst = f"data/s2ts/ndvi_{slot}.tif"
        if os.path.exists(dst): continue
        mos = np.full((NY, NX), -32768, np.int16)
        with cf.ThreadPoolExecutor(5) as ex:
            res = dict(ex.map(read_scene, sids))
        for sid in sids:  # FJ primero
            r = res[sid]
            if r is None: continue
            row, col, nd = r
            r0, c0 = max(row, 0), max(col, 0)
            r1, c1 = min(row + nd.shape[0], NY), min(col + nd.shape[1], NX)
            sub = nd[r0 - row:r1 - row, c0 - col:c1 - col]
            tgt = mos[r0:r1, c0:c1]
            fill = (tgt == -32768) & (sub != -32768)
            tgt[fill] = sub[fill]
        with rasterio.open(dst, "w", driver="GTiff", width=NX, height=NY, count=1, dtype="int16", nodata=-32768,
                           crs="EPSG:32613", transform=TR, compress="deflate", tiled=True) as o:
            o.write(mos, 1)
        print(slot, "valid", round(float((mos != -32768).mean()), 4), flush=True)
