"""Une las 4 teselas agregadas del CHM (agg2_*.tif) y las lleva a la malla UTM de 20 m de la serie Sentinel-2.
Salidas: data/chm/agg2_mosaic.tif (Web Mercator, ~9.5 m) y data/chm/chm20.tif
(b1 fracción >=2 m, b2 fracción >=5 m, b3 altura media en m, b4 altura máxima)."""
import numpy as np, rasterio
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling

TILES = ("023123120", "023123121", "023123102", "023123103")
srcs = [rasterio.open(f"data/chm/agg2_{t}.tif") for t in TILES]
arr, tr = merge(srcs)
prof = srcs[0].profile
prof.update(width=arr.shape[2], height=arr.shape[1], transform=tr)
with rasterio.open("data/chm/agg2_mosaic.tif", "w", **prof) as o:
    o.write(arr)

with rasterio.open("data/s2ts/ndvi_2026-08.tif") as ref:
    dst_tr, W, H, crs = ref.transform, ref.width, ref.height, ref.crs
out = np.zeros((4, H, W), np.float32)
for i in range(4):
    reproject(arr[i].astype(np.float32), out[i], src_transform=tr, src_crs=prof["crs"], dst_transform=dst_tr, dst_crs=crs,
              resampling=Resampling.average if i < 3 else Resampling.max, src_nodata=None)
out[0] /= 64; out[1] /= 64; out[2] /= 4
with rasterio.open("data/chm/chm20.tif", "w", driver="GTiff", width=W, height=H, count=4, dtype="float32",
                   crs=crs, transform=dst_tr, compress="deflate", tiled=True) as o:
    o.write(out)
print("chm20 ok", out.shape)
