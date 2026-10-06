"""Capas a 10 m (UTM 13N) alineadas con ndvi10: c2, c5 (fracción x255), altura media (m x4), prob. árbol 2026 (x255)."""
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling
ref = rasterio.open("data/s2ts/ndvi10_2026-08.tif")
H, W, TR, CRS = ref.height, ref.width, ref.transform, ref.crs
prof = dict(driver="GTiff", width=W, height=H, crs=CRS, transform=TR, compress="deflate", tiled=True, count=1, dtype="uint8")
with rasterio.open("data/chm/agg2_mosaic.tif") as s:
    for b, name, scale in ((1, "c2", 255 / 64), (2, "c5", 255 / 64), (3, "hm", 1.0)):
        src = s.read(b).astype(np.float32)
        dst = np.zeros((H, W), np.float32)
        reproject(src, dst, src_transform=s.transform, src_crs=s.crs, dst_transform=TR, dst_crs=CRS, resampling=Resampling.average)
        with rasterio.open(f"data/l10_{name}.tif", "w", **prof) as o:
            o.write(np.clip(dst * scale, 0, 255).astype(np.uint8), 1)
        print(name, "ok", flush=True)
with rasterio.open("data/s2ts/tree2026_prob.tif") as s:
    dst = np.zeros((H, W), np.uint8)
    reproject(s.read(1), dst, src_transform=s.transform, src_crs=s.crs, dst_transform=TR, dst_crs=CRS, resampling=Resampling.bilinear)
    with rasterio.open("data/l10_rf.tif", "w", **prof) as o: o.write(dst, 1)
print("rf ok")
