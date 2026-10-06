"""Mancha urbana y distancias (malla UTM 10 m).
Construido = WorldCover 2021 clase 50, o celdas con >= 25 % de edificios de Overture en 90 m.
Se quitan líneas finas (carreteras), se unen manzanas y se rellenan huecos de hasta 30 ha.
La metrópoli es la mancha más grande (Torreón–Gómez–Lerdo); pueblos, las de 100 ha o más.
Salidas: data/l10_dmetro.tif y data/l10_dtown.tif (metros), data/l10_urban.tif (2 metrópoli, 1 pueblo)."""
import numpy as np, rasterio
from scipy import ndimage as ndi

wc = rasterio.open("data/l10_wc.tif")
built = wc.read(1) == 50
bld = np.load("data/l10_bld.npy")
dens = ndi.uniform_filter((bld > 0).astype(np.float32), 9)
urb = built | (dens >= 0.25)
urb = ndi.binary_opening(urb, structure=np.ones((5, 5)))
urb = ndi.binary_closing(urb, structure=np.ones((3, 3)), iterations=4)
holes = ndi.binary_fill_holes(urb) & ~urb
hl, _ = ndi.label(holes)
hs = np.bincount(hl.ravel()); small = hs <= 3000; small[0] = False
urb |= small[hl]
lab, n = ndi.label(urb)
sizes = np.bincount(lab.ravel()); sizes[0] = 0
metro_id = int(np.argmax(sizes))
town_ids = np.nonzero((sizes >= 10000) & (np.arange(len(sizes)) != metro_id))[0]
metro = lab == metro_id
town = np.isin(lab, town_ids)
print("metrópoli ha", sizes[metro_id] / 100, "| pueblos", len(town_ids))
prof = dict(driver="GTiff", width=wc.width, height=wc.height, crs=wc.crs, transform=wc.transform, compress="deflate", tiled=True, count=1, dtype="float32")
for name, m in (("dmetro", metro), ("dtown", town)):
    d = ndi.distance_transform_edt(~m) * 10.0
    with rasterio.open(f"data/l10_{name}.tif", "w", **prof) as o:
        o.write(d.astype(np.float32), 1)
prof.update(dtype="uint8")
with rasterio.open("data/l10_urban.tif", "w", **prof) as o:
    o.write((metro * 2 + town).astype(np.uint8), 1)
print("urbano ok")
