"""Cuenta edificios de Overture (centro de su recuadro) por celda de la malla UTM de 10 m -> data/l10_bld.npy."""
import numpy as np, rasterio, pyarrow.parquet as pq
from pyproj import Transformer

ref = rasterio.open("data/l10_c2.tif")
TR, H, W = ref.transform, ref.height, ref.width
bb = pq.read_table("data/ov_buildings.parquet", columns=["bbox"]).column("bbox").to_pylist()
bx = np.array([(b["xmin"] + b["xmax"]) / 2 for b in bb])
by = np.array([(b["ymin"] + b["ymax"]) / 2 for b in bb])
ux, uy = Transformer.from_crs(4326, 32613, always_xy=True).transform(bx, by)
col = ((np.asarray(ux) - TR.c) / 10).astype(int)
row = ((TR.f - np.asarray(uy)) / 10).astype(int)
ok = (col >= 0) & (col < W) & (row >= 0) & (row < H)
BLD = np.zeros((H, W), np.uint16)
np.add.at(BLD, (row[ok], col[ok]), 1)
np.save("data/l10_bld.npy", BLD)
print("edificios", int(ok.sum()))
