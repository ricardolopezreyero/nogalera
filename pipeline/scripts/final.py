"""Ensambla el GeoJSON final de nogaleras: selección, geometría limpia, medidas, ubicación y estimación de precio."""
import json, math, numpy as np, rasterio, pyarrow.parquet as pq, shapely
from rasterio import features
from shapely.geometry import shape, mapping, Point
from shapely.ops import transform as stf
from shapely.strtree import STRtree
from pyproj import Transformer, Geod
G = Geod(ellps="WGS84")
to_wgs = Transformer.from_crs(32613, 4326, always_xy=True).transform
to_utm = Transformer.from_crs(4326, 32613, always_xy=True).transform
d = json.load(open("data/objects2_utm.geojson")); F = d["features"]
lab = dict(l.split() for l in open("etiquetas/labels.txt") if l.strip())
labL = dict(l.split() for l in open("etiquetas/labels_lost2.txt") if l.strip())
ref = rasterio.open("data/l10_c2.tif"); TR, H, W = ref.transform, ref.height, ref.width
dmetro = rasterio.open("data/l10_dmetro.tif").read(1); dtown = rasterio.open("data/l10_dtown.tif").read(1)
urban = rasterio.open("data/l10_urban.tif").read(1)
HOME = (25.60174, -103.39234)   # Real del Nogalar (centroide OSM)
# --- divisiones: municipios y localidades
da = pq.read_table("data/ov_division_area.parquet").to_pylist()
muni = [(r["names"]["primary"], shapely.from_wkb(r["geometry"])) for r in da if r["subtype"] == "county"]
dv = pq.read_table("data/ov_division.parquet").to_pylist()
locs = [(r["names"]["primary"], shapely.from_wkb(r["geometry"]), r["population"] or 0) for r in dv if r["subtype"] in ("locality",)]
loc_tree = STRtree([g for _, g, _ in locs])
def municipio(pt):
    for n, g in muni:
        if g.contains(pt): return n
    return None
def cerca_de(pt):
    i = loc_tree.nearest(pt)
    n, g, pop = locs[i]
    dist = G.inv(pt.x, pt.y, g.x, g.y)[2]
    return n, dist
# --- selección
sel = []
for i, f in enumerate(F):
    p = f["properties"]
    if p["kind"] == "activa":
        l = lab.get(str(i))
        if l == "N": continue
        if l in ("O", "M") or p["p_orch"] >= 0.5:
            conf = "alta" if (l == "O" or p["p_orch"] >= 0.75) else "media"
            sel.append((i, "activa", conf, l == "M"))
    else:
        if labL.get(str(i)) == "L":
            sel.append((i, "perdida", "alta", False))
# bloques vecinos (<= 20 m) de una huerta confirmada, con probabilidad >= 0.35: también son huerta
_geoms = [shape(f["geometry"]) for f in F]
_tree = STRtree(_geoms)
_sel_ids = {i for i, *_ in sel}
_strong = {i for i, k, c, m in sel if k == "activa" and c == "alta"}
for i, f in enumerate(F):
    p = f["properties"]
    if i in _sel_ids or p["kind"] != "activa" or lab.get(str(i)) == "N" or p.get("p_orch", 0) < 0.35:
        continue
    g = _geoms[i]
    if any(j in _strong and g.distance(_geoms[j]) <= 20 for j in _tree.query(g.buffer(20))):
        sel.append((i, "activa", "media", False)); _sel_ids.add(i)
print("seleccionadas", len(sel))
PRICE_EDGE = {"Torreón": 800, "Gómez Palacio": 600, "Lerdo": 600}
P_AG, P_AG_BARE, P_TOWN = 90.0, 55.0, 300.0
def precio_m2(dm, dt, mun, ha, bare):
    base = P_AG_BARE if bare else P_AG
    pe = PRICE_EDGE.get(mun, 600)
    pm = base + (pe - base) * math.exp(-dm / 2500.0)
    pt = base + (P_TOWN - base) * math.exp(-dt / 1500.0)
    p = max(pm, pt) * min(max((ha / 10.0) ** -0.12, 0.75), 1.3)
    return p
def r2(x):  # redondeo a 2 cifras significativas
    if x <= 0: return 0
    k = 10 ** (int(math.floor(math.log10(x))) - 1)
    return int(round(x / k) * k)
def r_m2(x):
    return int(round(x / 5.0) * 5) if x < 200 else int(round(x / 10.0) * 10)
out = []
for i, kind, conf, mixed in sel:
    f = F[i]; p = f["properties"]
    g = shape(f["geometry"])
    g = g.buffer(5, join_style=1).buffer(-5, join_style=1).simplify(4, preserve_topology=True)
    if g.geom_type == "MultiPolygon":
        g = max(g.geoms, key=lambda x: x.area) if len(g.geoms) > 0 else g
    g = shapely.Polygon(g.exterior, [r for r in g.interiors if shapely.Polygon(r).area > 2500])
    if not g.is_valid: g = shapely.make_valid(g)
    gw = stf(to_wgs, g)
    area = abs(G.geometry_area_perimeter(gw)[0]); per = abs(G.geometry_area_perimeter(gw)[1])
    if area < 4000: continue
    mrr = g.minimum_rotated_rectangle; ext = list(mrr.exterior.coords)
    e1 = math.dist(ext[0], ext[1]); e2 = math.dist(ext[1], ext[2])
    rp = gw.representative_point()
    # muestreo de rásters en la ventana del polígono
    win = rasterio.windows.from_bounds(*g.bounds, TR).round_offsets().round_lengths()
    r0, c0 = int(win.row_off), int(win.col_off); hh, ww = max(int(win.height), 1), max(int(win.width), 1)
    wtr = rasterio.windows.transform(win, TR)
    mm = features.rasterize([(g, 1)], out_shape=(hh, ww), transform=wtr, dtype="uint8").astype(bool)
    if mm.sum() == 0: mm[hh // 2, ww // 2] = True
    sub = lambda a: a[r0:r0 + hh, c0:c0 + ww][mm]
    dm = float(sub(dmetro).min()); dt = float(sub(dtown).min()); urb_frac = float((sub(urban) > 0).mean())
    mun = municipio(rp) or ""
    loc, ldist = cerca_de(rp)
    ha = area / 1e4
    dist_casa = G.inv(HOME[1], HOME[0], rp.x, rp.y)[2] / 1000
    estado = kind
    if kind == "perdida":
        bld_ha = p["bld"] / max(p["cells"] / 100, 0.01); road_ha = p["resroad"] / max(p["cells"] / 100, 0.01)
        estado = "urbanizada" if (bld_ha >= 2 or road_ha >= 3 or p["urlu"] >= 0.3 or urb_frac >= 0.3) else "desmontada"
    rec = dict(estado=estado, confianza=conf, mixta=mixed, area_m2=int(round(area)), perimetro_m=int(round(per)),
               largo_m=int(round(max(e1, e2))), ancho_m=int(round(min(e1, e2))), lat=round(rp.y, 6), lon=round(rp.x, 6),
               municipio=mun, cerca_de=loc, cerca_de_km=round(ldist / 1000, 1), dist_ref_km=round(dist_casa, 1),
               d_ciudad_km=round(dm / 1000, 1), d_pueblo_km=round(dt / 1000, 1), en_mancha_urbana=round(urb_frac, 2),
               altura_m=round(p["hm"], 1) if p.get("hm") else None, p_modelo=round(p.get("p_orch", 0), 2), _src=i)
    if estado != "urbanizada":
        pm2 = precio_m2(dm, dt, mun, ha, bare=(estado == "desmontada"))
        rec.update(precio_m2=r_m2(pm2), precio_m2_min=r_m2(pm2 * 0.65), precio_m2_max=r_m2(pm2 * 1.5),
                   valor=r2(pm2 * area), valor_min=r2(pm2 * 0.65 * area), valor_max=r2(pm2 * 1.5 * area))
    out.append((rec, gw))
# orden por distancia al punto de referencia y numeración
out.sort(key=lambda x: x[1].representative_point().distance(Point(HOME[1], HOME[0])))
feats = []
for n, (rec, gw) in enumerate(out, 1):
    rec = {"id": n, **rec}
    geom = mapping(gw)
    def rnd(c):
        return [[round(x, 5), round(y, 5)] for x, y in c]
    geom = {"type": "Polygon", "coordinates": [rnd(r) for r in geom["coordinates"]]}
    feats.append({"type": "Feature", "properties": rec, "geometry": geom})
json.dump({"type": "FeatureCollection", "features": feats}, open("data/nogaleras_full.geojson", "w"), ensure_ascii=False)
from collections import Counter
c = Counter(f["properties"]["estado"] for f in feats)
ha = Counter(); val = Counter()
for f in feats:
    ha[f["properties"]["estado"]] += f["properties"]["area_m2"] / 1e4; val[f["properties"]["estado"]] += f["properties"].get("valor", 0)
print({k: (c[k], round(ha[k]), f"${val[k]/1e9:.2f} mil M") for k in c})
mc = Counter(f["properties"]["municipio"] for f in feats if f["properties"]["estado"] == "activa")
print("por municipio:", mc.most_common())
print("más cercanas:", [(f["properties"]["id"], f["properties"]["dist_ref_km"], round(f["properties"]["area_m2"]/1e4, 1), f["properties"]["estado"], f["properties"].get("precio_m2")) for f in feats[:8]])
