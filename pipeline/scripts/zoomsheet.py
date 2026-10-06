"""Hoja de acercamientos CHM 1 m (centro del objeto, ventana de hasta 700 m) para revisar etiquetas."""
import sys, json, numpy as np, rasterio
from rasterio.merge import merge
from shapely.geometry import shape, box
from shapely.ops import transform as stf
from pyproj import Transformer
from PIL import Image, ImageDraw, ImageFont
u2m = Transformer.from_crs(32613, 3857, always_xy=True).transform
F = json.load(open("data/objects2_utm.geojson"))["features"]
CHM = [rasterio.open(f"data/chm/{t}.tif") for t in ("023123120", "023123121", "023123102", "023123103")]
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
ids = [int(x) for x in sys.argv[2].split(",")]
S, cols = int(sys.argv[3]) if len(sys.argv) > 3 else 420, int(sys.argv[4]) if len(sys.argv) > 4 else 3
rows = (len(ids) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (S + 8), rows * (S + 24)), (255, 255, 255))
for k, i in enumerate(ids):
    g = shape(F[i]["geometry"])
    c = g.representative_point()
    h = min(max(g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1]) / 2 * 1.1, 350)
    bb = box(c.x - h, c.y - h, c.x + h, c.y + h)
    mb = stf(u2m, bb).bounds
    srcs = [s for s in CHM if not (s.bounds.right < mb[0] or s.bounds.left > mb[2] or s.bounds.top < mb[1] or s.bounds.bottom > mb[3])]
    if not srcs:
        continue
    arr, _ = merge(srcs, bounds=mb)
    im = Image.fromarray((255 - np.clip(arr[0].astype(np.float32) * 12, 0, 255)).astype(np.uint8)).convert("RGB").resize((S, S), Image.BILINEAR)
    d = ImageDraw.Draw(im)
    B = bb.bounds
    for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
        pts = [((x - B[0]) / (B[2] - B[0]) * S, (B[3] - y) / (B[3] - B[1]) * S) for x, y in poly.exterior.coords]
        d.line(pts, fill=(255, 0, 0), width=1)
    x, y = (k % cols) * (S + 8), (k // cols) * (S + 24)
    sheet.paste(im, (x, y + 22))
    ImageDraw.Draw(sheet).text((x + 2, y + 2), f"#{i} {F[i]['properties']['cells']/100:.1f} ha  ventana {2*h:.0f} m", fill=(0, 0, 0), font=FONT)
sheet.save(sys.argv[1]); print("ok", sys.argv[1])
