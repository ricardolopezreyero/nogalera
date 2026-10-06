"""Borradores de lotificación para N6: corredor central, casa club, calles y lotes de 300 a 500 m²."""
import json, math, shapely
from shapely.geometry import shape, mapping, box, LineString
from shapely import affinity
from shapely.ops import transform as stf, unary_union
from pyproj import Transformer, Geod
G = Geod(ellps="WGS84")
to_u = Transformer.from_crs(4326, 32613, always_xy=True).transform
to_w = Transformer.from_crs(32613, 4326, always_xy=True).transform
lim = stf(to_u, shape(json.load(open("etiquetas/n6_limite.geojson"))))
# eje largo: lado largo del rectángulo mínimo
mrr = list(lim.minimum_rotated_rectangle.exterior.coords)
e = max(((mrr[i], mrr[i + 1]) for i in range(4)), key=lambda s: math.dist(*s))
ang = math.degrees(math.atan2(e[1][1] - e[0][1], e[1][0] - e[0][0]))
C = lim.centroid
R = affinity.rotate(lim, -ang, origin=C)            # eje largo horizontal
x0, y0, x1, y1 = R.bounds
CALLE, PERIM, CORR = 12.0, 12.0, 36.0              # anchos (m): calle local, circuito perimetral, bulevar central
ycor = (y0 + y1) / 2                                # el corredor sigue la calle interna existente, al centro
dev = R.buffer(-PERIM, join_style=2)
corr = box(x0 - 50, ycor - CORR / 2, x1 + 50, ycor + CORR / 2).intersection(R)
cx = (x0 + x1) / 2
club = box(cx - 50, ycor + CORR / 2, cx + 50, ycor + CORR / 2 + 75).intersection(dev)   # 100 × 75 m junto al bulevar
CRUCE = 170.0                                       # calle transversal cada ~170 m
ESC = {300: (12.0, 25.0, 3400), 350: (14.0, 25.0, 3300), 400: (16.0, 25.0, 3200), 450: (15.0, 30.0, 3100), 500: (50 / 3, 30.0, 3000)}
TERRENO, URB_CALLE, URB_BASE, BLANDOS = 670.0, 1400.0, 250.0, 0.12
gross = abs(G.geometry_area_perimeter(stf(to_w, lim))[0])
def lotes(F, D):
    libre = dev.difference(corr).difference(club)
    out, calles = [], []
    xs = []
    x = x0 + PERIM
    while x < x1:
        xs.append(x); x += CRUCE + CALLE
    for side in (1, -1):
        # filas desde el corredor hacia fuera: [frente al corredor] D, D, calle, D, D, calle...
        y = ycor + side * CORR / 2
        filas = []
        filas.append((y, y + side * D)); y += side * D
        while abs(y - ycor) < (y1 - y0):
            filas.append((y, y + side * D)); y += side * D
            calles.append((y, y + side * CALLE)); y += side * CALLE
            filas.append((y, y + side * D)); y += side * D
        for (a, b) in filas:
            ya, yb = min(a, b), max(a, b)
            for xa in xs:
                xb = min(xa + CRUCE, x1)
                n = int((xb - xa) // F)
                for k in range(n):
                    L = box(xa + k * F, ya, xa + (k + 1) * F, yb)
                    if L.difference(libre).area <= 0.02 * L.area:
                        out.append(L)
    franjas = [box(x0 - 50, min(a, b), x1 + 50, max(a, b)) for a, b in calles]
    franjas += [box(xa + CRUCE, y0 - 50, xa + CRUCE + CALLE, y1 + 50) for xa in xs]
    vial = unary_union(franjas).intersection(dev.difference(corr).difference(club))
    return out, vial
def geo(g):
    return stf(to_w, affinity.rotate(g, ang, origin=C))
feats = [{"type": "Feature", "properties": {"capa": "limite"}, "geometry": mapping(geo(R))},
         {"type": "Feature", "properties": {"capa": "corredor"}, "geometry": mapping(geo(corr))},
         {"type": "Feature", "properties": {"capa": "club"}, "geometry": mapping(geo(club))}]
res = []
for m2, (F, D, precio) in ESC.items():
    L, vial = lotes(F, D)
    area_l = sum(l.area for l in L)
    vial_m2 = (R.area - dev.area) + vial.area + corr.area * 18 / CORR      # circuito + calles + carriles del bulevar
    verde = R.area - area_l - vial_m2                                       # parque del bulevar, casa club y remates
    venta = area_l * precio
    costo = TERRENO * gross + URB_CALLE * vial_m2 + URB_BASE * gross + BLANDOS * venta
    margen = venta - costo
    r = dict(m2=m2, frente=round(F, 1), fondo=D, lotes=len(L), vendible_m2=round(area_l), pct_vendible=round(100 * area_l / R.area, 1),
             verde_pct=round(100 * verde / R.area, 1), vial_pct=round(100 * vial_m2 / R.area, 1), precio_lote_m2=precio, venta=round(venta), costo=round(costo), margen=round(margen),
             margen_m2_bruto=round(margen / gross), roi=round(100 * margen / costo, 1), nogales_por_lote=round(m2 / 144, 1),
             precio_lote=round(m2 * precio))
    res.append(r); print(r)
    for l in L:
        g = geo(l)
        feats.append({"type": "Feature", "properties": {"capa": "lote", "esc": m2},
                      "geometry": {"type": "Polygon", "coordinates": [[[round(a, 6), round(b, 6)] for a, b in g.exterior.coords]]}})
fc = {"type": "FeatureCollection", "bruto_m2": round(gross), "angulo": round(ang, 1), "escenarios": res, "features": feats}
json.dump(fc, open("../public/n6/n6.geojson", "w"), separators=(",", ":"), ensure_ascii=False)
print("bruto ha", round(gross / 1e4, 1), "club m2", round(club.area), "corredor m2", round(corr.area))
