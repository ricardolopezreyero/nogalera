"""Agrupa bloques contiguos (<= 20 m), limpia propiedades y exporta GeoJSON compacto + CSV para el sitio."""
import json, csv, math, os, sys
import shapely
from shapely.geometry import shape
from shapely.ops import transform as stf
from shapely.strtree import STRtree
from pyproj import Transformer
OUT = sys.argv[1] if len(sys.argv) > 1 else "../public"
to_utm = Transformer.from_crs(4326, 32613, always_xy=True).transform
d = json.load(open("data/nogaleras_full.geojson")); F = d["features"]
act = [f for f in F if f["properties"]["estado"] == "activa"]
G = [stf(to_utm, shape(f["geometry"])) for f in act]
tree = STRtree(G)
parent = list(range(len(G)))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
for i, g in enumerate(G):
    for j in tree.query(g.buffer(20)):
        if j != i and g.distance(G[j]) <= 20:
            parent[find(i)] = find(j)
groups = {}
for i in range(len(G)): groups.setdefault(find(i), []).append(i)
gid = {}
for k, (root, members) in enumerate(sorted(groups.items(), key=lambda kv: min(act[m]["properties"]["id"] for m in kv[1])), 1):
    tot = sum(act[m]["properties"]["area_m2"] for m in members)
    for m in members:
        gid[m] = (k, len(members), tot)
for i, f in enumerate(act):
    k, n, tot = gid[i]
    if n > 1:
        f["properties"].update(grupo=k, grupo_bloques=n, grupo_m2=int(tot))
KEEP = ["id", "estado", "confianza", "mixta", "area_m2", "perimetro_m", "largo_m", "ancho_m", "lat", "lon", "municipio", "cerca_de",
        "dist_ref_km", "d_ciudad_km", "altura_m", "precio_m2", "precio_m2_min", "precio_m2_max", "valor", "valor_min", "valor_max",
        "grupo", "grupo_bloques", "grupo_m2"]
out = []
for f in F:
    p = f["properties"]
    q = {k: p[k] for k in KEEP if k in p and p[k] is not None and p[k] is not False}
    out.append({"type": "Feature", "properties": q, "geometry": f["geometry"]})
fc = {"type": "FeatureCollection", "generado": "2026-10-06", "referencia": {"nombre": "Real del Nogalar", "lat": 25.60174, "lon": -103.39234}, "features": out}
s = json.dumps(fc, ensure_ascii=False, separators=(",", ":"))
open(os.path.join(OUT, "nogaleras.geojson"), "w").write(s)
print("geojson KB", len(s.encode()) // 1024, "features", len(out), "grupos multi-bloque", sum(1 for g in groups.values() if len(g) > 1))
cols = ["id", "estado", "area_m2", "largo_m", "ancho_m", "municipio", "cerca_de", "lat", "lon", "precio_m2_min", "precio_m2", "precio_m2_max", "valor_min", "valor", "valor_max", "dist_ref_km", "confianza", "grupo", "grupo_m2"]
with open(os.path.join(OUT, "nogaleras.csv"), "w", newline="", encoding="utf-8-sig") as fh:  # BOM: Excel abre bien los acentos
    w = csv.writer(fh); w.writerow(cols)
    for f in out:
        p = f["properties"]; w.writerow([p.get(c, "") for c in cols])
print("csv ok")
