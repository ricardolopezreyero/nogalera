"""Objetos v2: activas 2026 (T26) y perdidas (T19 alto >=5 m sin verde 2026), con filtros de terreno y atributos."""
import numpy as np, rasterio, pyarrow.parquet as pq, shapely, json, time
from rasterio import features
from scipy import ndimage as ndi
from shapely.ops import transform as stf
from shapely.geometry import shape, mapping
from pyproj import Transformer
from collections import defaultdict
T0 = time.time()
def log(*a): print(f"[{time.time()-T0:5.0f}s]", *a, flush=True)
to_utm = Transformer.from_crs(4326, 32613, always_xy=True).transform
R = lambda p: rasterio.open(p).read(1)
ref = rasterio.open("data/l10_c2.tif"); TR, H, W = ref.transform, ref.height, ref.width
c2, c5, hm, rf = R("data/l10_c2.tif"), R("data/l10_c5.tif"), R("data/l10_hm.tif"), R("data/l10_rf.tif")
nd = R("data/s2ts/ndvi10_2026-08.tif"); slope = R("data/l10_slope.tif"); wc = R("data/l10_wc.tif"); dem = R("data/l10_dem.tif")
log("capas")
relief = ndi.maximum_filter(dem, 31) - ndi.minimum_filter(dem, 31)       # relieve en 300 m
FLAT = (ndi.uniform_filter(slope.astype(np.float32), 5) <= 50) & (relief <= 60)   # pendiente media <= 5°, relieve <= 60 m
log("terreno: plano", FLAT.mean().round(3))
c5s = ndi.uniform_filter(c5.astype(np.float32), 5)
T19 = (c5s >= 51) & (ndi.maximum_filter(c5, 3) >= 64)                   # >=20 % del vecindario con árboles >=5 m
T26 = ((rf >= 128) & (nd >= 3500)) | (T19 & (rf >= 77) & (nd >= 4500))
log("T19 ha", T19.sum() / 100, "T26 ha", T26.sum() / 100)
seg = pq.read_table("data/ov_segments.parquet", columns=["geometry", "class"]).to_pylist()
CUT = {"motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "living_street", "standard_gauge"}
cut_geoms = [stf(to_utm, shapely.from_wkb(r["geometry"])) for r in seg if r["class"] in CUT]
RES = [stf(to_utm, shapely.from_wkb(r["geometry"])) for r in seg if r["class"] in ("residential", "living_street", "service")]
wat = pq.read_table("data/ov_water.parquet", columns=["geometry", "class"]).to_pylist()
for r in wat:
    if r["class"] in ("canal", "river"):
        g = stf(to_utm, shapely.from_wkb(r["geometry"]))
        cut_geoms.append(g.boundary if g.geom_type in ("Polygon", "MultiPolygon") else g)
CUTM = features.rasterize(((g, 1) for g in cut_geoms), out_shape=(H, W), transform=TR, all_touched=True, dtype="uint8").astype(bool)
MAJOR = {"motorway", "trunk", "primary", "secondary", "tertiary", "standard_gauge"}
cut_major = [stf(to_utm, shapely.from_wkb(r["geometry"])) for r in seg if r["class"] in MAJOR]
for r in wat:
    if r["class"] in ("canal", "river"):
        g = stf(to_utm, shapely.from_wkb(r["geometry"]))
        cut_major.append(g.boundary if g.geom_type in ("Polygon", "MultiPolygon") else g)
CUTMAJ = features.rasterize(((g, 1) for g in cut_major), out_shape=(H, W), transform=TR, all_touched=True, dtype="uint8").astype(bool)
RESM = features.rasterize(((g, 1) for g in RES), out_shape=(H, W), transform=TR, all_touched=True, dtype="uint8")
RIVER = [stf(to_utm, shapely.from_wkb(r["geometry"])) for r in wat if r["class"] in ("river", "stream")]
RIVM = features.rasterize(((g.buffer(100), 1) for g in RIVER), out_shape=(H, W), transform=TR, dtype="uint8").astype(bool)
LAKES = [stf(to_utm, shapely.from_wkb(r["geometry"])) for r in wat if r["class"] in ("reservoir", "lake", "basin", "water", "river")]
LAKES = [g for g in LAKES if g.geom_type in ("Polygon", "MultiPolygon")]
LAKM = features.rasterize(((g.buffer(200), 1) for g in LAKES if g.area > 5e4), out_shape=(H, W), transform=TR, dtype="uint8").astype(bool)
lu = pq.read_table("data/ov_land_use.parquet").to_pylist()
NOT_ORCH = {"park", "golf_course", "green", "bunker", "cemetery", "grave_yard", "pitch", "playground", "school", "university",
            "college", "kindergarten", "hospital", "stadium", "recreation_ground", "track", "plant_nursery", "garden", "theme_park",
            "water_park", "nature_reserve", "zoo", "clinic", "religious", "military", "grass"}
URB = {"residential", "commercial", "retail", "industrial", "brownfield", "construction", "greenfield"}
NOLU = features.rasterize(((stf(to_utm, shapely.from_wkb(r["geometry"])), 1) for r in lu if r["class"] in NOT_ORCH), out_shape=(H, W), transform=TR, dtype="uint8").astype(bool)
URLU = features.rasterize(((stf(to_utm, shapely.from_wkb(r["geometry"])), 1) for r in lu if r["class"] in URB), out_shape=(H, W), transform=TR, dtype="uint8").astype(bool)
BLD = np.load("data/l10_bld.npy")
log("vectores rasterizados")
S4 = ndi.generate_binary_structure(2, 1)
def make_objects(mask, min_cells=50, cut=None):
    m = ndi.binary_closing(mask, structure=np.ones((3, 3)))
    m &= ~(CUTM if cut is None else cut)
    m = ndi.binary_opening(m, structure=np.ones((3, 3)))
    lab, n = ndi.label(m, structure=S4)
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    keep = sizes >= min_cells; keep[0] = False
    m = keep[lab]
    # rellenar huecos de hasta 0.3 ha
    holes = ndi.binary_fill_holes(m) & ~m
    hl, hn = ndi.label(holes)
    hs = np.bincount(hl.ravel(), minlength=hn + 1); small = hs <= 30; small[0] = False
    m |= small[hl]
    return ndi.label(m, structure=S4)
ACT_lab, nA = make_objects(T26 & FLAT); log("activas", nA)
LOSTm = T19 & FLAT & ~ndi.binary_dilation(T26, iterations=2) & ((nd < 3000) | (rf < 77))
LOST_lab, nL = make_objects(LOSTm, cut=CUTMAJ); log("perdidas", nL)
np.save("data/obj2_act.npy", ACT_lab.astype(np.int32)); np.save("data/obj2_lost.npy", LOST_lab.astype(np.int32))
CROPCTX = ndi.uniform_filter((wc == 40).astype(np.float32), 61)       # fracción de cultivo en 600 m
BUILTCTX = ndi.uniform_filter((wc == 50).astype(np.float32), 61)
log("contexto")
def attrs(lab, n):
    idx = np.arange(1, n + 1)
    cells = np.bincount(lab.ravel(), minlength=n + 1)[1:].astype(np.float64)
    S = lambda arr: np.bincount(lab.ravel(), weights=arr.ravel().astype(np.float64), minlength=n + 1)[1:]
    return {
        "cells": cells, "t19": S(T19) / cells, "t26": S(T26) / cells, "nolu": S(NOLU) / cells, "urlu": S(URLU) / cells,
        "bld": S(BLD), "resroad": S(RESM), "ndvi": S(nd) / cells / 10000, "rf": S(rf) / cells / 255, "c2": S(c2) / cells / 255,
        "c5": S(c5) / cells / 255, "hm": S(hm) / cells / 4, "slope": S(slope) / cells / 10, "relief": S(relief) / cells,
        "crop": S(CROPCTX) / cells, "built": S(BUILTCTX) / cells, "wc_tree": S(wc == 10) / cells, "wc_built": S(wc == 50) / cells,
        "river": S(RIVM) / cells, "lake": S(LAKM) / cells,
    }
A = attrs(ACT_lab, nA); L = attrs(LOST_lab, nL); log("atributos")
def vectorize(lab, a, kind):
    parts = defaultdict(list)
    for geom, val in features.shapes(lab.astype(np.int32), mask=lab > 0, transform=TR, connectivity=4):
        parts[int(val) - 1].append(shape(geom))
    feats = []
    for i, gs in parts.items():
        g = shapely.union_all(gs) if len(gs) > 1 else gs[0]
        mrr = g.minimum_rotated_rectangle
        ext = list(mrr.exterior.coords)
        e1 = shapely.LineString(ext[0:2]).length; e2 = shapely.LineString(ext[1:3]).length
        props = {k: float(v[i]) for k, v in a.items()}
        props.update(kind=kind, rect=g.area / max(mrr.area, 1), convex=g.area / max(g.convex_hull.area, 1),
                     elong=max(e1, e2) / max(min(e1, e2), 1), width=min(e1, e2), length=max(e1, e2))
        feats.append({"type": "Feature", "geometry": mapping(g), "properties": props})
    return feats
feats = vectorize(ACT_lab, A, "activa") + vectorize(LOST_lab, L, "perdida")
json.dump({"type": "FeatureCollection", "crs": "EPSG:32613", "features": feats}, open("data/objects2_utm.geojson", "w"))
log("listo", len(feats))
