"""N6: busca el tamaño de lote (280–330 m²) y fondo que dan más m² vendibles, con amenidades:
circuito vehicular perimetral, pista para correr, bulevar central, 2 parques y área comunal
(pádel ×2, tenis, salón con oficinas arriba, estacionamiento)."""
import json, math, os, sys, shapely
from shapely.geometry import shape, mapping, box
from shapely import affinity, prepared
from shapely.ops import transform as stf, unary_union
from pyproj import Transformer, Geod
G = Geod(ellps="WGS84")
to_u = Transformer.from_crs(4326, 32613, always_xy=True).transform
to_w = Transformer.from_crs(32613, 4326, always_xy=True).transform
SRC = sys.argv[1] if len(sys.argv) > 1 else "etiquetas/n6_limite.geojson"
OUT = sys.argv[2] if len(sys.argv) > 2 else "../public/n6"
lim = stf(to_u, shape(json.load(open(SRC))))
mrr = list(lim.minimum_rotated_rectangle.exterior.coords)
e = max(((mrr[i], mrr[i + 1]) for i in range(4)), key=lambda s: math.dist(*s))
ang = math.degrees(math.atan2(e[1][1] - e[0][1], e[1][0] - e[0][0]))
C = lim.centroid
R = affinity.rotate(lim, -ang, origin=C)
x0, y0, x1, y1 = R.bounds
CALLE, PERIM, PISTA, CORR = 12.0, 12.0, 5.0, 36.0
ycor = (y0 + y1) / 2
inner = R.buffer(-PERIM, join_style=2)
dev = R.buffer(-(PERIM + PISTA), join_style=2)
anillo_calle = R.difference(inner)
pista = inner.difference(dev)
corr = box(x0 - 50, ycor - CORR / 2, x1 + 50, ycor + CORR / 2).intersection(R)
cx = (x0 + x1) / 2
# área comunal 100 × 80 m al norte del bulevar, a la mitad
bx, by = cx - 50, ycor + CORR / 2
comunal = box(bx, by, bx + 100, by + 80)
salon = box(bx, by, bx + 40, by + 25)                 # planta baja salón, planta alta oficinas
estac = box(bx, by + 25, bx + 40, by + 60)
tenis = box(bx + 48, by + 3, bx + 88, by + 23)         # 36.6 × 18.3 m con orillas
padel = [box(bx + 48, by + 30, bx + 59, by + 52), box(bx + 61, by + 30, bx + 72, by + 52)]   # 10 × 20 m cada una
# dos parques de ~1 ha a un cuarto y tres cuartos del bulevar, uno de cada lado
Lx = x1 - x0
parque1 = box(x0 + 0.27 * Lx - 50, ycor - CORR / 2 - 90, x0 + 0.27 * Lx + 50, ycor - CORR / 2).intersection(dev)
parque2 = box(x0 + 0.73 * Lx - 50, ycor + CORR / 2, x0 + 0.73 * Lx + 50, ycor + CORR / 2 + 90).intersection(dev)
amen = unary_union([corr, comunal, parque1, parque2])
libre = dev.difference(amen)
libre_p = prepared.prep(libre.buffer(0.01))
gross = abs(G.geometry_area_perimeter(stf(to_w, lim))[0])
TERRENO, URB_CALLE, URB_BASE, BLANDOS, AMENIDADES = 670.0, 1400.0, 250.0, 0.12, 32e6

def precio(A):                       # $/m² de lote: 3,400 a 300 m², baja $2 por cada m² más de lote
    return 3400 - 2 * (A - 300)

def trazar(F, D):
    nb = max(1, round(170 / F)); LB = nb * F          # cuadra = número exacto de frentes
    xs = []; x = x0 + PERIM + PISTA
    while x < x1:
        xs.append(x); x += LB + CALLE
    lotes, calles = [], []
    for side in (1, -1):
        y = ycor + side * CORR / 2
        filas = [(y, y + side * D)]; y += side * D
        while abs(y - ycor) < (y1 - y0):
            filas.append((y, y + side * D)); y += side * D
            calles.append((y, y + side * CALLE)); y += side * CALLE
            filas.append((y, y + side * D)); y += side * D
        for a, b in filas:
            ya, yb = min(a, b), max(a, b)
            for xa in xs:
                for k in range(nb):
                    L = box(xa + k * F, ya, xa + (k + 1) * F, yb)
                    if libre_p.contains(L):
                        lotes.append(L)
    franjas = [box(x0 - 50, min(a, b), x1 + 50, max(a, b)) for a, b in calles] + [box(xa + LB, y0 - 50, xa + LB + CALLE, y1 + 50) for xa in xs]
    vial = unary_union(franjas).intersection(libre)
    return lotes, vial

def evaluar(A, F, D, lotes, vial):
    vend = len(lotes) * A
    vial_m2 = anillo_calle.area + vial.area + corr.area * 18 / CORR
    venta = vend * precio(A)
    costo = TERRENO * gross + URB_CALLE * vial_m2 + URB_BASE * gross + BLANDOS * venta + AMENIDADES
    return dict(m2=A, frente=round(F, 2), fondo=D, lotes=len(lotes), vendible_m2=round(vend), pct_vendible=round(100 * vend / R.area, 1),
                vial_pct=round(100 * vial_m2 / R.area, 1), verde_pct=round(100 * (R.area - vend - vial_m2) / R.area, 1),
                precio_lote_m2=precio(A), precio_lote=round(A * precio(A)), venta=round(venta), costo=round(costo),
                margen=round(venta - costo), margen_m2_bruto=round((venta - costo) / gross), roi=round(100 * (venta - costo) / costo, 1),
                nogales_por_lote=round(A / 144, 1))

def geo(g):
    return stf(to_w, affinity.rotate(g, ang, origin=C))

FONDOS = tuple(range(20, 31))   # fondo de 20 a 30 m
barrido, mejores = [], {}
for A in range(280, 331, 5):
    best = None
    for D in FONDOS:
        F = A / D
        if F < 10 or not (1.4 <= D / F <= 3.0):   # frente mínimo de 10 m
            continue
        lotes, vial = trazar(F, D)
        r = evaluar(A, F, D, lotes, vial)
        barrido.append(r)
        if best is None or r["vendible_m2"] > best[0]["vendible_m2"]:
            best = (r, lotes)
    mejores[A] = best
    print(A, best[0]["frente"], "×", best[0]["fondo"], "lotes", best[0]["lotes"], "vendible", best[0]["vendible_m2"], best[0]["pct_vendible"], "% margen", round(best[0]["margen"] / 1e6), "M roi", best[0]["roi"])

os.makedirs(OUT, exist_ok=True)
def poly(g):
    return {"type": "Polygon", "coordinates": [[[round(a, 6), round(b, 6)] for a, b in g.exterior.coords]]}
def feat(capa, g, **kw):
    g = geo(g)
    gs = g.geoms if g.geom_type == "MultiPolygon" else [g]
    return [{"type": "Feature", "properties": dict(capa=capa, **kw), "geometry": poly(x)} for x in gs if not x.is_empty]
base = []
base += feat("limite", R); base += feat("calle_perimetral", anillo_calle); base += feat("pista", pista)
base += feat("corredor", corr); base += feat("comunal", comunal)
base += feat("salon", salon, nombre="Salón (PB) y oficinas (PA)"); base += feat("estacionamiento", estac, nombre="Estacionamiento")
base += feat("tenis", tenis, nombre="Tenis")
for p in padel: base += feat("padel", p, nombre="Pádel")
base += feat("parque", parque1, nombre="Parque 1"); base += feat("parque", parque2, nombre="Parque 2")
escen = [mejores[A][0] for A in sorted(mejores)]
fc = {"type": "FeatureCollection", "bruto_m2": round(gross), "escenarios": escen, "barrido": barrido,
      "amenidades": {"pista_m": round(pista.area / PISTA), "parque_m2": round(parque1.area + parque2.area), "comunal_m2": round(comunal.area),
                     "bulevar_m2": round(corr.area)}, "features": base}
json.dump(fc, open(f"{OUT}/n6.geojson", "w"), separators=(",", ":"), ensure_ascii=False)
for A, (r, lotes) in mejores.items():
    json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": poly(geo(l))} for l in lotes]},
              open(f"{OUT}/lotes-{A}.geojson", "w"), separators=(",", ":"))
print("pista m", round(pista.area / PISTA), "parques", round(parque1.area), round(parque2.area), "comunal", round(comunal.area))
