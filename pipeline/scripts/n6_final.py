"""N6 · diseño final alineado a la cuadrícula de nogales.
- Calles longitudinales sobre las líneas libres entre hileras (cada 5 hileras): los troncos quedan fuera del arroyo.
- Linderos laterales de lote sobre las columnas de árboles (desfase local por manzana): la casa va entre árboles.
- Bulevar central sobre la hilera faltante (calle interna existente); área comunal en la otra hilera faltante.
- Parques en las manzanas con los nogales más grandes; pista para correr perimetral.
Cuenta los árboles que hay que reubicar (troncos dentro de arroyos, casas, edificios y canchas)."""
import json, math, os, sys, numpy as np, shapely
from shapely.geometry import shape, mapping, box, Point
from shapely import affinity, prepared
from shapely.ops import transform as stf, unary_union
from pyproj import Transformer, Geod
G = Geod(ellps="WGS84")
D = sys.argv[1] if len(sys.argv) > 1 else "data"
OUT = sys.argv[2] if len(sys.argv) > 2 else "../public/n6"
to_u = Transformer.from_crs(4326, 32613, always_xy=True).transform
to_w = Transformer.from_crs(32613, 4326, always_xy=True).transform
A = np.load(f"{D}/n6_arboles.npy"); P, H = A[:, :2], A[:, 2]
th, _, _, _, _, cx, cy = np.load(f"{D}/n6_grid.npy")
t = np.radians(th); Rm = np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])
Q = (P - [cx, cy]) @ Rm.T                                   # (u, v): u a lo largo de las hileras
lim = stf(to_u, shape(json.load(open(sys.argv[3] if len(sys.argv) > 3 else "etiquetas/n6_limite.geojson"))))
R = affinity.rotate(affinity.translate(lim, -cx, -cy), -th, origin=(0, 0))
u0, v0, u1, v1 = R.bounds
gross = abs(G.geometry_area_perimeter(stf(to_w, lim))[0])

def fit(x, lo, hi, step=0.02):
    best = (0, 0, 0)
    for s in np.arange(lo, hi, step):
        z = np.exp(2j * np.pi * x / s); r = abs(z.mean())
        if r > best[0]: best = (r, s, (np.angle(z.mean()) / (2 * np.pi) * s) % s)
    return best
_, SV, PV = fit(Q[:, 1], 12.0, 13.4)
row = lambda k: PV + SV * k
gap = lambda k: row(k) + SV / 2
kk = np.round((Q[:, 1] - PV) / SV).astype(int)
ks, cnt = np.unique(kk, return_counts=True)
cnt_k = dict(zip(ks.tolist(), cnt.tolist()))
internas = range(int(ks.min()) + 3, int(ks.max()) - 2)          # sin las hileras de orilla
faltan = [k for k in internas if cnt_k.get(k, 0) < 0.35 * np.median(cnt)]
kc = min(faltan, key=lambda k: abs(row(k)))                  # hilera faltante más central: bulevar
ka = [k for k in faltan if k != kc and abs(k - kc) > 6]      # otra hilera faltante: área comunal
print(f"hileras cada {SV:.2f} m; faltan {faltan}; bulevar en {kc}, comunal en {ka}")

ROW_CALLE, TRAIL, BUL = 11.0, 5.0, 15.0                     # derecho de vía de calle, pista, medio bulevar
vb = row(kc)
bul = (vb - BUL, vb + BUL)
# calles longitudinales: cada 5 hileras a partir de la manzana del bulevar
calles_v = []
k = kc + 5
while gap(k) < v1 - 20: calles_v.append(gap(k)); k += 5
k = kc - 6
while gap(k) > v0 + 20: calles_v.append(gap(k)); k -= 5
calles_v.sort()
# ajuste fino: cada calle (y el bulevar) se mueve hasta ±2 m para que el arroyo quede entre hileras
dentro_v = lambda c: (Q[:, 0] > u0) & (Q[:, 0] < u1)
def mejor_offset(fn):
    offs = np.arange(-2.0, 2.01, 0.25)
    return min(offs, key=lambda o: (fn(o), abs(o)))
calles_v = [c + mejor_offset(lambda o, c=c: int(np.sum(np.abs(Q[:, 1] - (c + o)) < 4.0))) for c in calles_v]
ob = mejor_offset(lambda o: int(np.sum((np.abs(Q[:, 1] - (vb + o)) > 2.3) & (np.abs(Q[:, 1] - (vb + o)) < 10.3))))
vb += ob; bul = (vb - BUL, vb + BUL)
print("ajuste del bulevar", ob, "m")
# franjas de lote (profundidad de un lote) con su calle de frente
bandas = sorted([(vb - BUL, vb + BUL, "bulevar")] + [(c - ROW_CALLE / 2, c + ROW_CALLE / 2, "calle") for c in calles_v])
franjas = []
lims = [(v0 - 1, v0 - 1, "borde")] + bandas + [(v1 + 1, v1 + 1, "borde")]
for (a0, a1, ta), (b0, b1, tb) in zip(lims[:-1], lims[1:]):
    lo, hi = a1, b0
    if hi - lo <= 1: continue
    if ta != "borde" and tb != "borde":
        mid = (lo + hi) / 2
        franjas += [(lo, mid, "abajo"), (mid, hi, "arriba")]          # dos lotes espalda con espalda
    elif ta == "borde":
        franjas.append((max(lo, hi - 30), hi, "arriba"))
    else:
        franjas.append((lo, min(hi, lo + 30), "abajo"))
inner = R.buffer(-TRAIL, join_style=2)
pista = R.difference(inner)

# calles transversales: posiciones con menos troncos, separadas 150–190 m
uu = np.arange(math.floor(u0), math.ceil(u1), 1.0)
dentro = np.array([R.intersects(box(x - 5.5, v0, x + 5.5, v1)) for x in uu])
conf = np.array([np.sum(np.abs(Q[:, 0] - x) < 4.0) for x in uu]).astype(float)   # troncos en el arroyo
conf[~dentro] = 1e6
n = len(uu); best = np.full(n, np.inf); prev = np.full(n, -1)
for i in range(n):
    if not (u0 + 40 <= uu[i] <= u0 + 110): continue
    best[i] = conf[i]
for i in range(n):
    if not np.isfinite(best[i]): continue
    for j in range(i + 150, min(n, i + 191)):
        c = best[i] + conf[j]
        if c < best[j]: best[j], prev[j] = c, i
fin = [i for i in range(n) if u1 - 110 <= uu[i] <= u1 - 40 and np.isfinite(best[i])]
i = min(fin, key=lambda i: best[i]); cruces = []
while i >= 0: cruces.append(uu[i]); i = prev[i]
cruces = sorted(cruces)
print("calles transversales en u =", [round(c) for c in cruces], "troncos en ellas:", int(sum(conf[np.searchsorted(uu, c)] for c in cruces)))

# geometría de vialidad
vial = [box(u0 - 5, a, u1 + 5, b) for a, b, tp in bandas if tp == "calle"]
vial += [box(c - ROW_CALLE / 2, v0 - 5, c + ROW_CALLE / 2, v1 + 5) for c in cruces]
vial = unary_union(vial).intersection(inner)
pav = [box(u0 - 5, c - 3.5, u1 + 5, c + 3.5) for c in calles_v] + [box(c - 3.5, v0 - 5, c + 3.5, v1 + 5) for c in cruces]
pavimento = unary_union(pav).intersection(inner)
bulevar = box(u0 - 5, bul[0], u1 + 5, bul[1]).intersection(inner)
arroyos_bul = unary_union([box(u0 - 5, vb - 9.8, u1 + 5, vb - 2.8), box(u0 - 5, vb + 2.8, u1 + 5, vb + 9.8)]).intersection(inner)
sendero_bul = box(u0 - 5, vb - 2.8, u1 + 5, vb + 2.8).intersection(inner)
segs = [u0 - 5] + [x for c in cruces for x in (c - ROW_CALLE / 2, c + ROW_CALLE / 2)] + [u1 + 5]
segs = list(zip(segs[0::2], segs[1::2]))                     # tramos entre transversales

# manzanas (para parques y comunal): tramo × bloque entre calles
bloques = []
for (a0, a1, _), (b0, b1, _) in zip(bandas[:-1], bandas[1:]):
    bloques.append((a1, b0))
celdas = []
for bi, (lo, hi) in enumerate(bloques):
    for si, (sa, sb) in enumerate(segs):
        g = box(sa, lo, sb, hi).intersection(inner)
        if g.area < 3000: continue
        m = (Q[:, 0] > sa) & (Q[:, 0] < sb) & (Q[:, 1] > lo) & (Q[:, 1] < hi)
        celdas.append(dict(bi=bi, si=si, g=g, lo=lo, hi=hi, sa=sa, sb=sb, valor=float(np.sum(H[m] ** 2)), arboles=int(m.sum()), hmed=float(np.median(H[m])) if m.any() else 0))
# área comunal: manzana que contiene la hilera faltante del sur, en el tramo más cercano al acceso (extremo SO = u menor)
va = row(ka[0]) if ka else None
cand = [c for c in celdas if va is not None and c["lo"] < va < c["hi"]]
com = min(cand, key=lambda c: c["sa"]) if cand else None
if com and com["g"].area < 6000:
    com = sorted(cand, key=lambda c: c["sa"])[1]
# parques: las 2 manzanas de más valor (árboles grandes), una a cada lado del bulevar, separadas >= 300 m
pool = [c for c in celdas if c is not com and 7000 <= c["g"].area <= 11000]
lado = lambda c: (c["lo"] + c["hi"]) / 2 > vb
p1 = max([c for c in pool if lado(c)], key=lambda c: c["valor"])
p2 = max([c for c in pool if not lado(c) and abs((c["sa"] + c["sb"]) / 2 - (p1["sa"] + p1["sb"]) / 2) >= 300], key=lambda c: c["valor"])
parques = [p1, p2]
print("comunal", round(com["g"].area), "m²; parques", [(round(p["g"].area), p["arboles"], round(p["hmed"], 1)) for p in parques])

# elementos del área comunal dentro de la hilera vacía (sin árboles)
ua = com["sa"] + 8
lane = (va - SV + 1.5, va + SV - 1.5)                        # entre troncos de las hileras vecinas
lw = lane[1] - lane[0]
# en la hilera vacía: salón, tenis y 2 de pádel en línea; estacionamiento arbolado entre las dos hileras siguientes
mid = lambda w: (lane[0] + (lw - w) / 2, lane[0] + (lw + w) / 2)
com_el = {"salon": box(ua, lane[0], ua + 40, lane[0] + min(18, lw))}
x = ua + 44
com_el["tenis"] = box(x, mid(18.3)[0], x + 36.6, mid(18.3)[1]); x += 40.6
com_el["padel1"] = box(x, mid(10)[0], x + 20, mid(10)[1]); x += 22
com_el["padel2"] = box(x, mid(10)[0], x + 20, mid(10)[1])
gc = va + 1.5 * SV if abs(va + 1.5 * SV - (com["lo"] + com["hi"]) / 2) < abs(va - 1.5 * SV - (com["lo"] + com["hi"]) / 2) else va - 1.5 * SV
com_el["estacionamiento"] = box(ua, gc - 5, ua + 60, gc + 5)
com_el = {k: v for k, v in com_el.items() if v is not None}

amen = unary_union([com["g"]] + [p["g"] for p in parques])
libre = inner.difference(vial).difference(bulevar).difference(amen)
libre_p = prepared.prep(libre.buffer(0.05))

# lotes: linderos laterales sobre columnas de árboles (desfase y separación locales por celda)
lotes = []
for lo, hi, lado_f in franjas:
    for sa, sb in segs:
        cell = box(sa, lo, sb, hi)
        if not libre.intersects(cell): continue
        m = (Q[:, 0] > sa) & (Q[:, 0] < sb) & (Q[:, 1] > lo - 7) & (Q[:, 1] < hi + 7)
        if m.sum() >= 8:
            r, s, ph = fit(Q[m, 0], 11.8, 13.6)
            if r < 0.45: s, ph = 12.7, (Q[m, 0].mean()) % 12.7
        else:
            s, ph = 12.7, 0.0
        j0 = math.floor((sa - ph) / s) - 1
        bordes = [ph + j * s for j in range(j0, j0 + int((sb - sa) / s) + 4)]
        bordes = [b for b in bordes if sa < b < sb]
        if not bordes: continue
        # remates: < 8 m se suman al lote vecino (lotes de esquina más anchos)
        cortes = [sa] + bordes + [sb]
        if cortes[1] - cortes[0] < 8: cortes.pop(1)
        if cortes[-1] - cortes[-2] < 8: cortes.pop(-2)
        for a, b in zip(cortes[:-1], cortes[1:]):
            L = box(a, lo, b, hi)
            if libre_p.contains(L):
                lotes.append(dict(g=L, frente="bulevar" if (lo == bul[1] or hi == bul[0]) else "calle", ancho=b - a, fondo=hi - lo, lado=lado_f))
            else:
                Li = L.intersection(libre)
                if Li.geom_type == "Polygon" and Li.area >= 0.8 * 300 and Li.area / L.area > 0.6 and (b - a) >= 8:
                    lotes.append(dict(g=Li, frente="calle", ancho=b - a, fondo=hi - lo, lado=lado_f, irregular=True))

# reubicación de árboles
pts = [Point(q) for q in Q]
def troncos_en(g, margen=0.0):
    gp = prepared.prep(g.buffer(margen)) if margen else prepared.prep(g)
    return [i for i, p in enumerate(pts) if gp.contains(p)]
casas = []
for L in lotes:
    a, lo_, b, hi_ = L["g"].bounds
    if L["lado"] == "abajo":   # frente hacia v menor? la calle de frente está en el extremo exterior de la franja
        pass
    casas.append(box(a + 1.5, lo_ + 3, b - 1.5, hi_ - 3).intersection(L["g"]))
r_casas = set(i for c in casas for i in troncos_en(c))
r_calles = set(troncos_en(unary_union([pavimento, arroyos_bul]), 0.5))
r_com = set(i for g in com_el.values() for i in troncos_en(g, 1.0))
reubicar = r_casas | r_calles | r_com
print(f"árboles {len(Q)}; a reubicar: casas {len(r_casas)}, calles {len(r_calles)}, comunal {len(r_com)}, total {len(reubicar)} ({100*len(reubicar)/len(Q):.1f} %)")

# números
areas = np.array([L["g"].area for L in lotes])
def precio(a): return 3400 - 2 * (a - 300)
venta = float(sum(a * precio(a) for a in areas))
vial_m2 = vial.area + arroyos_bul.area
TERRENO, URB_CALLE, URB_BASE, BLANDOS, AMENIDADES, REUBICA = 670.0, 1400.0, 250.0, 0.12, 32e6, 12000.0
costo = TERRENO * gross + URB_CALLE * vial_m2 + URB_BASE * gross + BLANDOS * venta + AMENIDADES + REUBICA * len(reubicar)
res = dict(lotes=len(lotes), vendible_m2=round(areas.sum()), pct_vendible=round(100 * areas.sum() / R.area, 1),
           lote_mediana=round(float(np.median(areas))), lote_min=round(float(areas.min())), lote_max=round(float(areas.max())),
           lotes_bulevar=sum(1 for L in lotes if L["frente"] == "bulevar"), frente_mediano=round(float(np.median([L["ancho"] for L in lotes])), 1),
           vial_pct=round(100 * vial_m2 / R.area, 1), verde_pct=round(100 * (R.area - areas.sum() - vial_m2) / R.area, 1),
           arboles=len(Q), reubicar=len(reubicar), reubicar_casas=len(r_casas), reubicar_calles=len(r_calles), reubicar_comunal=len(r_com),
           arboles_en_lotes=len(set(i for L in lotes for i in troncos_en(L["g"].buffer(0.6)))), arboles_parques=sum(p["arboles"] for p in parques),
           venta=round(venta), costo=round(costo), margen=round(venta - costo), roi=round(100 * (venta - costo) / costo, 1),
           pista_km=round(inner.length / 1000, 1), sendero_bulevar_km=round((sendero_bul.bounds[2] - sendero_bul.bounds[0]) / 1000, 1), parque_m2=round(sum(p["g"].area for p in parques)), comunal_m2=round(com["g"].area))
print(json.dumps(res, ensure_ascii=False))

# acceso: punto medio del borde más al sur (y mínima en norte arriba), unido a la calle más cercana
geo = lambda g: affinity.translate(affinity.rotate(g, th, origin=(0, 0)), cx, cy)
Rg = geo(R); ring = list(Rg.exterior.coords)
segm = min(zip(ring[:-1], ring[1:]), key=lambda s: (s[0][1] + s[1][1]) / 2)
acc_pt = Point((segm[0][0] + segm[1][0]) / 2, (segm[0][1] + segm[1][1]) / 2)
acc_uv = affinity.rotate(affinity.translate(acc_pt, -cx, -cy), -th, origin=(0, 0))
destino = unary_union([vial, bulevar])
from shapely.ops import nearest_points
p_dest = nearest_points(acc_uv, destino)[1]
acceso = shapely.LineString([acc_uv, p_dest]).buffer(5.5, cap_style=2)
caseta = acc_uv.buffer(6, cap_style=3)

os.makedirs(OUT, exist_ok=True)
def poly(g):
    gs = g.geoms if g.geom_type in ("MultiPolygon", "GeometryCollection") else [g]
    out = []
    for x in gs:
        if x.geom_type != "Polygon" or x.is_empty: continue
        out.append({"type": "Polygon", "coordinates": [[[round(a, 6), round(b, 6)] for a, b in stf(to_w, geo(x)).exterior.coords]]})
    return out
feats = []
def add(capa, g, **kw):
    for pg in poly(g): feats.append({"type": "Feature", "properties": dict(capa=capa, **kw), "geometry": pg})
add("limite", R); add("pista", pista); add("vial", vial.union(acceso)); add("bulevar", bulevar)
add("arroyo", arroyos_bul); add("sendero", sendero_bul)
add("comunal", com["g"], nombre="Área comunal")
nombres = {"salon": "Salón (PB) · oficinas (PA)", "estacionamiento": "Estacionamiento", "tenis": "Tenis", "padel1": "Pádel", "padel2": "Pádel"}
for k, g in com_el.items(): add(k.rstrip("12"), g, nombre=nombres[k])
for i, p in enumerate(parques, 1): add("parque", p["g"], nombre=f"Parque {i}", arboles=p["arboles"])
add("caseta", caseta, nombre="Acceso y caseta")
for i, L in enumerate(lotes, 1):
    add("lote", L["g"], n=i, m2=round(L["g"].area), frente=L["frente"], ancho=round(L["ancho"], 1), fondo=round(L["fondo"], 1),
        arboles=len(troncos_en(L["g"].buffer(0.6))))
arb = []
for i, q in enumerate(Q):
    p = Point(q); pw = stf(to_w, geo(p))
    arb.append([round(pw.x, 6), round(pw.y, 6), 1 if i in reubicar else 0, round(float(H[i]), 1)])
json.dump({"type": "FeatureCollection", "bruto_m2": round(gross), "resumen": res, "features": feats}, open(f"{OUT}/final.geojson", "w"), separators=(",", ":"), ensure_ascii=False)
json.dump(arb, open(f"{OUT}/arboles.json", "w"), separators=(",", ":"))
print("listo", len(feats), "elementos")
