"""Junta las 10 fechas de NDVI (data/s2ts/ndvi_*.tif, 20 m) en data/s2ts/ts.npy (float32, NaN = sin dato)."""
import numpy as np, rasterio

SLOTS = ["2025-12", "2026-01", "2026-03", "2026-04", "2026-05a", "2026-05b", "2026-06", "2026-07", "2026-08", "2026-09"]
ts = np.stack([rasterio.open(f"data/s2ts/ndvi_{s}.tif").read(1) for s in SLOTS]).astype(np.float32)
ts[ts == -32768] = np.nan
ts /= 10000
np.save("data/s2ts/ts.npy", ts)
print("ts.npy", ts.shape)
