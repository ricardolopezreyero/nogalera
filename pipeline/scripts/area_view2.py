"""Vista de área: TCI 2026, CHM y máscara T26; contornos: verde=seleccionada, rojo=objeto descartado, azul=perdida."""
import sys, json, numpy as np, rasterio, shapely
from rasterio.merge import merge
from rasterio.windows import from_bounds
from shapely.geometry import shape, box
from shapely.ops import transform as stf
from pyproj import Transformer
from PIL import Image, ImageDraw
lat, lon, half, out = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
t = Transformer.from_crs(4326, 32613, always_xy=True).transform
u2m = Transformer.from_crs(32613, 3857, always_xy=True).transform
x, y = t(lon, lat); B = (x - half, y - half, x + half, y + half)
S = 700
TCI = rasterio.open("data/s2ts/tci10_2026-08.tif")
a = TCI.read(window=from_bounds(*B, TCI.transform), boundless=True, fill_value=0).astype(np.float32)
a = np.clip((a - a.min()) / max(np.percentile(a, 99) - a.min(), 1) * 255, 0, 255).astype(np.uint8)
im = Image.fromarray(np.moveaxis(a, 0, -1)).resize((S, S), Image.BILINEAR)
CHM = [rasterio.open(f"data/chm/{t_}.tif") for t_ in ("023123120", "023123121", "023123102", "023123103")]
mb = stf(u2m, box(*B)).bounds
srcs = [s for s in CHM if not (s.bounds.right < mb[0] or s.bounds.left > mb[2] or s.bounds.top < mb[1] or s.bounds.bottom > mb[3])]
arr, _ = merge(srcs, bounds=mb, res=(mb[2] - mb[0]) / 1400)
ch = Image.fromarray((255 - np.clip(arr[0].astype(np.float32) * 14, 0, 255)).astype(np.uint8)).convert("RGB").resize((S, S), Image.BILINEAR)
rf = rasterio.open("data/l10_rf.tif"); nd = rasterio.open("data/s2ts/ndvi10_2026-08.tif")
w = from_bounds(*B, rf.transform)
r = rf.read(1, window=w, boundless=True); n = nd.read(1, window=w, boundless=True)
viz = np.stack([np.clip(r, 0, 255), np.clip((n.astype(np.float32) / 10000) * 255, 0, 255).astype(np.uint8), np.zeros_like(r)], -1).astype(np.uint8)
t26 = Image.fromarray(viz).resize((S, S), Image.NEAREST)
obj = json.load(open("data/objects2_utm.geojson"))["features"]
fin = json.load(open("data/nogaleras_full.geojson"))["features"]
src_sel = {f["properties"]["_src"] for f in fin}
for img in (im, ch, t26):
    dr = ImageDraw.Draw(img)
    for i, f in enumerate(obj):
        g = shape(f["geometry"])
        if not g.intersects(box(*B)): continue
        col = (0, 200, 0) if i in src_sel else ((0, 120, 255) if f["properties"]["kind"] == "perdida" else (255, 0, 0))
        for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
            pts = [((px - B[0]) / (2 * half) * S, (B[3] - py) / (2 * half) * S) for px, py in poly.exterior.coords]
            dr.line(pts, fill=col, width=2)
        c = g.representative_point()
        dr.text(((c.x - B[0]) / (2 * half) * S, (B[3] - c.y) / (2 * half) * S), str(i), fill=(0, 0, 0))
sheet = Image.new("RGB", (3 * S + 20, S), (255, 255, 255))
sheet.paste(im, (0, 0)); sheet.paste(ch, (S + 10, 0)); sheet.paste(t26, (2 * S + 20, 0)); sheet.save(out)
print(out)
