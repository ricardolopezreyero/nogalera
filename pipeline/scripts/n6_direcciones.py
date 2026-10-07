"""N6 · nombres de calles y direcciones sobre el diseño (n6_confort.py)."""
import sys, json
args = sys.argv[1:]
exec(open(__file__.replace("n6_direcciones.py", "n6_confort.py")).read())

from n6_fachadas import fachada_de
FRACC = "La Nogalera"                       # nombre del fraccionamiento (provisional)
# Calles: las que corren a lo largo (paralelas al bulevar) son árboles; las que cruzan, aves. Las dos en orden alfabético:
# de sur a norte y de poniente a oriente. Si sabes una letra, sabes dónde está la calle.
# Nombres cortos, sin acentos y fáciles de decir y de escribir.
LARGAS = ["Cedro", "Encino", "Fresno", "Laurel", "Nogal", "Olmo", "Pino", "Roble"]
CRUCES = ["Alondra", "Canario", "Garza", "Grulla", "Mirlo", "Paloma", "Perico", "Tordo", "Zorzal"]
ejes = sorted([(c, "calle") for c in calles_v] + [(vb, "bulevar")])
assert len(ejes) == len(LARGAS) and len(cruces) == len(CRUCES), (len(ejes), len(cruces))
nombre_v = {round(c, 2): (LARGAS[i], t) for i, (c, t) in enumerate(ejes)}
centros = [c for c, _ in ejes]

# Dirección de cada lote: calle a la que da su frente; impares del lado norte, pares del lado sur, crecen de poniente a oriente
por_calle = {}
for L in lotes:
    a, lo_, b, hi_ = L["g"].bounds
    borde = lo_ if L["lado"] == "abajo" else hi_
    c = min(centros, key=lambda x: abs(abs(borde - x) - (BUL if abs(x - vb) < 1 else ROW_CALLE / 2)))
    lado_n = L["lado"] == "abajo"            # el lote queda al norte de su calle
    por_calle.setdefault((round(c, 2), lado_n), []).append(L)
# Numeración por cuadra: la centena es cuántas transversales quedan al poniente del lote (Encino 305 = pasando la 3.ª transversal),
# y dentro de la cuadra el número va por posición (cada 12.7 m), así que las casas de enfrente tienen números seguidos.
PASO_NUM = 12.7
def cuadra_de(u): return sum(1 for x in cruces if x < u)
def inicio_cuadra(q): return cruces[q - 1] + ROW_CALLE / 2 if q > 0 else u0
for (c, lado_n), Ls in por_calle.items():
    Ls.sort(key=lambda L: L["g"].centroid.x)
    previo = -1
    for k, L in enumerate(Ls):
        L["calle"] = nombre_v[c][0]
        q = cuadra_de(L["g"].centroid.x); pos = int((L["g"].bounds[0] - inicio_cuadra(q)) / PASO_NUM + 0.5)
        num = 100 * q + 2 * pos + (1 if lado_n else 2)
        if num <= previo: num = previo + 2                       # dos lotes angostos en la misma posición: el segundo toma el siguiente número
        L["num"] = num; previo = num
        L["fachada"] = fachada_de(k, lado_n, LARGAS.index(L["calle"]))
dirs = [f'{L["calle"]} {L["num"]}' for L in lotes]
assert len(set(dirs)) == len(dirs), "direcciones repetidas"
max_num = max(L["num"] for L in lotes)

# Parques y plazas toman el nombre de su calle de cruce más cercana
def ave_cercana(g): return CRUCES[min(range(len(cruces)), key=lambda i: abs(cruces[i] - g.centroid.x))]

print(f"direcciones: {len(dirs)}; número más alto {max_num}")

# ===== Salida: enriquece confort.geojson =====
it = iter([f for f in feats if f["properties"]["capa"] == "lote"])
for L in lotes:
    f = next(it); f["properties"].update(dir=f'{L["calle"]} {L["num"]}', fachada=L["fachada"])
for f in feats:
    p = f["properties"]
# nombres de parques y plazas por su calle de cruce
FLORES = ["Azahar", "Bugambilia", "Dalia", "Gardenia", "Jazmín", "Lavanda", "Magnolia", "Nardo", "Violeta", "Orquídea"]   # plazas: flores, en orden alfabético de poniente a oriente
pp = sorted([f for f in feats if f["properties"]["capa"] in ("parque", "plaza")], key=lambda f: shape(f["geometry"]).centroid.x)
for f in pp:
    gu = affinity.rotate(affinity.translate(stf(to_u, shape(f["geometry"])), -cx, -cy), -th, origin=(0, 0))
    ave = ave_cercana(gu)
    p = f["properties"]
    if p["capa"] == "parque":
        p["nombre"] = f"Parque {ave}"
    else:
        p["nombre"] = f"Plaza {FLORES.pop(0)}"
# ejes de calle con nombre (para rotular)
for (c, t), nm in zip(ejes, LARGAS):
    ln = shapely.LineString([(u0 - 20, c), (u1 + 20, c)]).intersection(inner)
    for seg in getattr(ln, "geoms", [ln]):
        pts_ = [seg.interpolate(f, normalized=True) for f in (0.2, 0.5, 0.8)]
        for pt in pts_:
            pw = stf(to_w, geo(pt)); feats.append({"type": "Feature", "properties": {"capa": "rotulo", "nombre": ("Bulevar " if t == "bulevar" else "") + nm, "eje": "largo"}, "geometry": {"type": "Point", "coordinates": [round(pw.x, 6), round(pw.y, 6)]}})
for c, nm in zip(cruces, CRUCES):
    ln = shapely.LineString([(c, v0 - 20), (c, v1 + 20)]).intersection(inner)
    for seg in getattr(ln, "geoms", [ln]):
        for f_ in (0.15, 0.85):
            pw = stf(to_w, geo(seg.interpolate(f_, normalized=True)))
            feats.append({"type": "Feature", "properties": {"capa": "rotulo", "nombre": nm, "eje": "cruce"}, "geometry": {"type": "Point", "coordinates": [round(pw.x, 6), round(pw.y, 6)]}})
res.update(fraccionamiento=FRACC, calles_largas=LARGAS, calles_cruce=CRUCES, num_max=max_num)
json.dump({"type": "FeatureCollection", "bruto_m2": round(gross), "resumen": res, "features": feats}, open(f"{OUT}/confort.geojson", "w"), separators=(",", ":"), ensure_ascii=False)
print("listo")
