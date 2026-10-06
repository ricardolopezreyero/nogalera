"""CHM 1.19 m (Meta) -> bloques 8x8 (~8.6 m): b1 n(h>=2), b2 n(h>=5), b3 altura media (dm/10 -> m*4), b4 máx."""
import sys, numpy as np, rasterio
from rasterio.windows import Window
src, dst = sys.argv[1], sys.argv[2]
F = 8
with rasterio.open(src) as ds:
    W, H = ds.width, ds.height
    out = np.zeros((4, H // F, W // F), np.uint8)
    step = 1024
    for r0 in range(0, H, step):
        a = ds.read(1, window=Window(0, r0, W, step))
        b = a.reshape(step // F, F, W // F, F)
        sl = slice(r0 // F, (r0 + step) // F)
        out[0, sl] = (b >= 2).sum(axis=(1, 3))
        out[1, sl] = (b >= 5).sum(axis=(1, 3))
        out[2, sl] = np.clip(b.mean(axis=(1, 3)) * 4, 0, 255)   # altura media x4
        out[3, sl] = b.max(axis=(1, 3))
    prof = ds.profile; t = ds.transform
prof.update(width=W // F, height=H // F, count=4, transform=rasterio.Affine(t.a * F, 0, t.c, 0, t.e * F, t.f),
            tiled=True, blockxsize=512, blockysize=512, compress="deflate")
with rasterio.open(dst, "w", **prof) as o:
    o.write(out)
print(dst, "ok")
