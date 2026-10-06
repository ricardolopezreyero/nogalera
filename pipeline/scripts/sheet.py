"""Hojas de revisión: por objeto, CHM 1 m (2018-20) y color verdadero Sentinel-2 (2026) con el contorno."""
import json, sys, numpy as np, rasterio, shapely
from rasterio.merge import merge
from rasterio.windows import from_bounds
from shapely.geometry import shape
from shapely.ops import transform as stf
from pyproj import Transformer
from PIL import Image, ImageDraw, ImageFont
u2m = Transformer.from_crs(32613, 3857, always_xy=True).transform
CHM = [rasterio.open(f"data/chm/{t}.tif") for t in ("023123120", "023123121", "023123102", "023123103")]
TCI = rasterio.open("data/s2ts/tci10_2026-08.tif")
TS = 220
try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
except Exception:
    FONT = ImageFont.load_default()
def square(b, pad=0.25, minsize=300):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = max(x1 - x0, y1 - y0, minsize) * (1 + 2 * pad) / 2
    return cx - s, cy - s, cx + s, cy + s
def draw_outline(img, geom, bounds, color):
    x0, y0, x1, y1 = bounds
    sx, sy = img.size[0] / (x1 - x0), img.size[1] / (y1 - y0)
    d = ImageDraw.Draw(img)
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            pts = [((x - x0) * sx, (y1 - y) * sy) for x, y in ring.coords]
            d.line(pts, fill=color, width=2)
def chm_img(bu):
    mb = stf(u2m, shapely.box(*bu)).bounds
    srcs = [s for s in CHM if not (s.bounds.right < mb[0] or s.bounds.left > mb[2] or s.bounds.top < mb[1] or s.bounds.bottom > mb[3])]
    if not srcs: return Image.new("RGB", (TS, TS), (200, 200, 200))
    arr, _ = merge(srcs, bounds=mb)
    a = arr[0].astype(np.float32)
    im = Image.fromarray((255 - np.clip(a * 14, 0, 255)).astype(np.uint8)).convert("RGB").resize((TS, TS), Image.BILINEAR)
    return im
def tci_img(bu):
    w = from_bounds(*bu, TCI.transform)
    a = TCI.read(window=w, boundless=True, fill_value=0)
    a = np.clip(a.astype(np.float32) * 1.6, 0, 255).astype(np.uint8)
    return Image.fromarray(np.moveaxis(a, 0, -1)).resize((TS, TS), Image.BILINEAR)
def render(items, out, cols=4):
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (2 * TS + 12), rows * (TS + 22)), (255, 255, 255))
    for k, (label, geom) in enumerate(items):
        bu = square(geom.bounds)
        a, b = chm_img(bu), tci_img(bu)
        draw_outline(a, geom, bu, (255, 0, 0)); draw_outline(b, geom, bu, (255, 255, 0))
        x, y = (k % cols) * (2 * TS + 12), (k // cols) * (TS + 22)
        sheet.paste(a, (x, y + 20)); sheet.paste(b, (x + TS + 2, y + 20))
        ImageDraw.Draw(sheet).text((x + 2, y + 2), label, fill=(0, 0, 0), font=FONT)
    sheet.save(out)
if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    ids = [int(x) for x in sys.argv[3].split(",")]
    feats = d["features"]
    items = []
    for i in ids:
        p = feats[i]["properties"]
        items.append((f"#{i} {p['kind'][:3]} {p['cells']/100:.1f}ha c2={p['c2']:.2f} rf={p['rf']:.2f} b={p['bld']/max(p['cells']/100,0.01):.0f} r={p['resroad']*10/max(p['cells']/100,0.01):.0f}", shape(feats[i]["geometry"])))
    render(items, sys.argv[2])
    print("ok", sys.argv[2])
