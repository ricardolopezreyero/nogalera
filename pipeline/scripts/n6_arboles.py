"""N6: detecta cada nogal en el CHM de 1 m (máximos locales >= 2 m) y ajusta la cuadrícula de plantación.
Salidas: data/n6_arboles.npy (x, y UTM 13N, altura) y data/n6_grid.npy (ángulo, s_u, fase_u, s_v, fase_v, cx, cy)."""
import json, numpy as np, rasterio
from rasterio.merge import merge
from rasterio import features
from scipy import ndimage as ndi
from shapely.geometry import shape
from shapely.ops import transform as stf
from pyproj import Transformer
gm = stf(Transformer.from_crs(4326, 3857, always_xy=True).transform, shape(json.load(open("etiquetas/n6_limite.geojson"))))
CHM = [rasterio.open(f"data/chm/{t}.tif") for t in ("023123120", "023123121", "023123102", "023123103")]
b = gm.buffer(40).bounds
srcs = [s for s in CHM if not (s.bounds.right < b[0] or s.bounds.left > b[2] or s.bounds.top < b[1] or s.bounds.bottom > b[3])]
arr, tr = merge(srcs, bounds=b)
h = ndi.gaussian_filter(arr[0].astype(np.float32), 1.5)
pk = (h == ndi.maximum_filter(h, size=7)) & (h >= 2.0)
pk &= features.rasterize([(gm.buffer(10), 1)], out_shape=h.shape, transform=tr).astype(bool)
r, c = np.nonzero(pk)
xs, ys = tr * (c + 0.5, r + 0.5)
ux, uy = Transformer.from_crs(3857, 32613, always_xy=True).transform(np.array(xs), np.array(ys))
P = np.c_[ux, uy]
np.save("data/n6_arboles.npy", np.c_[P, h[r, c]])
c0 = P.mean(0)
def fit(x, lo=9, hi=16):
    best = (0, 0, 0)
    for s in np.arange(lo, hi, 0.05):
        z = np.exp(2j * np.pi * x / s); rr = abs(z.mean())
        if rr > best[0]: best = (rr, s, (np.angle(z.mean()) / (2 * np.pi) * s) % s)
    return best
best = None
for th in np.arange(27, 32.01, 0.1):
    t = np.radians(th); Q = (P - c0) @ np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]]).T
    fu, fv = fit(Q[:, 0]), fit(Q[:, 1])
    if best is None or fu[0] * fv[0] > best[0]: best = (fu[0] * fv[0], th, fu, fv)
_, th, fu, fv = best
np.save("data/n6_grid.npy", np.array([th, fu[1], fu[2], fv[1], fv[2], c0[0], c0[1]]))
print(f"{len(P)} nogales; ángulo {th:.1f}°, separación {fu[1]:.2f} × {fv[1]:.2f} m")
