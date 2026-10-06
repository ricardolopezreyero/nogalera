"""Puntaje de cuadrícula (huerta) por objeto: autocorrelación enmascarada del CHM de 1 m dentro del polígono.
score = ACF(pico en 6-16 px) - ACF(mitad del vector del pico). Cuadrícula de árboles -> alto (>0.2)."""
import numpy as np, rasterio, shapely
from rasterio.merge import merge
from rasterio import features
from shapely.ops import transform as stf
from pyproj import Transformer
u2m = Transformer.from_crs(32613, 3857, always_xy=True).transform
CHM = [rasterio.open(f"data/chm/{t}.tif") for t in ("023123120", "023123121", "023123102", "023123103")]
def chm_for(geom_utm, max_px=1400):
    gm = stf(u2m, geom_utm)
    b = gm.bounds
    srcs = [s for s in CHM if not (s.bounds.right < b[0] or s.bounds.left > b[2] or s.bounds.top < b[1] or s.bounds.bottom > b[3])]
    if not srcs: return None, None
    # recorta a una ventana central si es muy grande (para velocidad)
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    half = min(max(b[2] - b[0], b[3] - b[1]) / 2, max_px * 1.194 / 2)
    bb = (cx - half, cy - half, cx + half, cy + half)
    arr, tr = merge(srcs, bounds=bb)
    m = features.rasterize([(gm, 1)], out_shape=arr.shape[1:], transform=tr, dtype="uint8")
    return arr[0].astype(np.float32), m.astype(bool)
def score(geom_utm):
    f, m = chm_for(geom_utm)
    if f is None or m.sum() < 400: return np.nan, np.nan, np.nan
    f = np.minimum(f, 15.0)
    if (f[m] >= 2).mean() < 0.03: return 0.0, 0.0, 0.0
    mu = f[m].mean(); x = np.where(m, f - mu, 0.0)
    H, W = x.shape
    P = (2 * H, 2 * W)
    Fx = np.fft.rfft2(x, P); Fm = np.fft.rfft2(m.astype(np.float32), P)
    num = np.fft.irfft2(Fx * np.conj(Fx), P); den = np.fft.irfft2(Fm * np.conj(Fm), P)
    var = (x[m] ** 2).mean()
    acf = num / np.maximum(den, 1) / max(var, 1e-6)
    acf = np.fft.fftshift(acf)
    cy, cx = H, W
    r = 17
    sub = acf[cy - r:cy + r + 1, cx - r:cx + r + 1]
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    rr = np.hypot(yy, xx)
    ann = (rr >= 6) & (rr <= 16)
    rb = np.round(rr).astype(int)
    prof = np.bincount(rb.ravel(), weights=sub.ravel()) / np.maximum(np.bincount(rb.ravel()), 1)
    resid = sub - prof[rb]
    vals = np.where(ann, resid, -9)
    k = np.argmax(vals); py, px = np.unravel_index(k, vals.shape)
    dy, dx = py - r, px - r
    peak = resid[py, px]
    mid = sub[r + int(round(dy / 2)), r + int(round(dx / 2))]
    return float(peak), float(np.hypot(dy, dx) * 1.078), float(sub[py, px] - mid)   # residuo del pico, espaciamiento (m), pico-mitad

from scipy import ndimage as _ndi
def texture(geom_utm):
    """Contraste local de copas en el CHM de 1 m: copas individuales -> alto; manchas lisas -> bajo."""
    f, m = chm_for(geom_utm)
    if f is None or m.sum() < 400: return np.nan, np.nan, np.nan
    f = np.minimum(f, 20.0)
    blur = _ndi.gaussian_filter(f, 3)
    con = np.abs(f - blur)[m].mean()
    return float(con), float((f[m] >= 5).mean()), float(f[m].std())
