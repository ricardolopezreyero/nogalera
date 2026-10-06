"""Relieve y uso de suelo a la malla UTM de 10 m:
- data/l10_dem.tif y data/l10_slope.tif (pendiente en décimas de grado) desde Copernicus DEM 30 m.
- data/l10_wc.tif: ESA WorldCover 2021 (10 m), leído en línea desde S3."""
import os, numpy as np, rasterio
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling
from rasterio.windows import from_bounds

os.environ.update(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif")
ref = rasterio.open("data/l10_c2.tif")
H, W, TR, CRS = ref.height, ref.width, ref.transform, ref.crs
prof = dict(driver="GTiff", width=W, height=H, crs=CRS, transform=TR, compress="deflate", tiled=True, count=1)

DEM = ("N25_00_W104_00", "N25_00_W103_00", "N26_00_W104_00", "N26_00_W103_00")
srcs = [rasterio.open(f"data/dem/{t}.tif") for t in DEM]
arr, tr = merge(srcs)
dem = np.zeros((H, W), np.float32)
reproject(arr[0], dem, src_transform=tr, src_crs=srcs[0].crs, dst_transform=TR, dst_crs=CRS, resampling=Resampling.bilinear)
gy, gx = np.gradient(dem, 10.0)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))
with rasterio.open("data/l10_dem.tif", "w", dtype="float32", **prof) as o:
    o.write(dem, 1)
with rasterio.open("data/l10_slope.tif", "w", dtype="uint8", **prof) as o:
    o.write(np.clip(slope * 10, 0, 255).astype(np.uint8), 1)

u = "/vsicurl/https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N24W105_Map.tif"
with rasterio.open(u) as wc:
    w = from_bounds(-104.06, 25.08, -102.54, 26.35, wc.transform).round_offsets().round_lengths()
    a = wc.read(1, window=w)
    out = np.zeros((H, W), np.uint8)
    reproject(a, out, src_transform=wc.window_transform(w), src_crs=wc.crs, dst_transform=TR, dst_crs=CRS, resampling=Resampling.nearest)
with rasterio.open("data/l10_wc.tif", "w", dtype="uint8", **prof) as o:
    o.write(out, 1)
print("terreno ok")
