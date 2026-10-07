"""N6 · servicios: calles, drenaje pluvial, drenaje sanitario, tratamiento, agua potable, red morada, electricidad y telecomunicaciones.
Trazo sobre el diseño (n6_luz → n6_direcciones → n6_confort), cálculo con la pendiente del terreno (Copernicus DEM, plano ajustado),
presupuesto por partida (sustituye los supuestos globales de calles y redes) y cuota de mantenimiento.
Salidas: public/n6/servicios.geojson (capas del mapa), servicios.html (hoja de especificaciones), especificaciones.csv; actualiza confort.geojson."""
import os, sys, csv, math, io
_aqui = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
__file__ = os.path.join(_aqui, "n6_luz.py")
exec(open(__file__).read())
import rasterio
from rasterio.mask import mask as rmask
from shapely.geometry import LineString

N = len(lotes)
# ======================= terreno =======================
with rasterio.open(f"{D}/l10_dem.tif") as src:
    a_, tr_ = rmask(src, [lim.buffer(150)], crop=True, nodata=np.nan)
zz = a_[0]; yy_, xx_ = np.mgrid[0:zz.shape[0], 0:zz.shape[1]]
Xd = tr_.c + (xx_ + 0.5) * tr_.a; Yd = tr_.f + (yy_ + 0.5) * tr_.e; mk = ~np.isnan(zz)
(gx, gy, Z0), *_ = np.linalg.lstsq(np.c_[Xd[mk] - cx, Yd[mk] - cy, np.ones(mk.sum())], zz[mk], rcond=None)
_t = math.radians(th)
GU, GV = gx * math.cos(_t) + gy * math.sin(_t), -gx * math.sin(_t) + gy * math.cos(_t)
zf = lambda u, v: Z0 + GU * u + GV * v
cotas = [zf(*q) for q in R.exterior.coords]
TERR = dict(z_media=round(float(Z0), 1), pend_km=round(math.hypot(gx, gy) * 1000, 2), rumbo=round(math.degrees(math.atan2(-gx, -gy)) % 360),
            desnivel=round(max(cotas) - min(cotas), 2))
print("terreno", TERR)

calle_c = {LARGAS[i]: c for i, (c, _) in enumerate(ejes)}
U_TOR = cruces[-1]
sin_ptar = inner.difference(ptar)
def tramo(c):
    ln = LineString([(u0 - 20, c), (u1 + 20, c)]).intersection(sin_ptar)
    g = max(getattr(ln, "geoms", [ln]), key=lambda g: g.length)
    return g.bounds[0], g.bounds[2]
def tramo_v(c):
    ln = LineString([(c, v0 - 20), (c, v1 + 20)]).intersection(sin_ptar)
    g = max(getattr(ln, "geoms", [ln]), key=lambda g: g.length)
    return g.bounds[1], g.bounds[3]
eje_pista = R.buffer(-TRAIL / 2, join_style=2).exterior
def en_pista(u, v):
    p = eje_pista.interpolate(eje_pista.project(Point(u, v))); return (p.x, p.y)
L_largo = sum(tramo(c)[1] - tramo(c)[0] for c in calles_v)
L_cruce = sum(tramo_v(c)[1] - tramo_v(c)[0] for c in cruces)
L_bul = tramo(vb)[1] - tramo(vb)[0]
SF = []                                                         # capas de servicios: (capa, geometría uv, props)
def F(capa, g, **kw): SF.append((capa, g, kw))

# ======================= población y caudales =======================
HAB, DOT, APORTA = 4.0, 250.0, 0.80                             # habitantes por casa, l/hab/día (clima cálido seco), aportación al drenaje
EXTRA = 1.06                                                    # club, súper, comercio y áreas comunes (+6 %)
POB = N * HAB
Qmed = POB * DOT * EXTRA / 86400; Qmd = 1.4 * Qmed; Qmh = 1.55 * Qmd
vol_anual = Qmed * 86400 * 365 / 1000
Qs_med = APORTA * Qmed
harmon = lambda p: min(3.8, 1 + 14 / (4 + math.sqrt(p / 1000)))
Qs_max = Qs_med * harmon(POB); Qs_ext = 1.5 * Qs_max
print(f"población {POB:.0f}; agua Qmed {Qmed:.1f} Qmd {Qmd:.1f} Qmh {Qmh:.1f} l/s; drenaje Qmed {Qs_med:.1f} Qmax {Qs_max:.1f} Qext {Qs_ext:.1f}")

# ======================= drenaje sanitario (gravedad, todo al oriente) =======================
N_MAN = 0.009                                                   # PVC / PEAD
def q_lleno(d, s): A = math.pi * d * d / 4; return A / N_MAN * (d / 4) ** (2 / 3) * s ** 0.5 * 1000   # l/s
DIAM = [0.20, 0.25, 0.30, 0.38, 0.45]
S_AT, S_COL, H0 = 0.0025, 0.0020, 1.30                          # pendiente mínima de atarjea y colector; profundidad de arranque (plantilla)
q_lote = lambda n: APORTA * n * HAB * DOT / 86400 * harmon(max(n * HAB, 1000)) * 1.5
ramas = []                                                      # (nombre, [(u,v)...] en sentido del flujo, lotes)
def lotes_de(c, lado=None, ua=-1e9, ub=1e9):
    nm = [k for k, v in calle_c.items() if abs(v - c) < 1][0]
    return [L for L in lotes if L["calle"] == nm and ua <= L["g"].centroid.x <= ub and (lado is None or L["lado"] == lado)]
salidas = {}                                                    # punto de llegada → nombre de la rama
for c in calles_v:
    ua, ub = tramo(c); nm = [k for k, v in calle_c.items() if abs(v - c) < 1][0]
    if c > vb and ub < U_TOR - 20:                              # calle norte que termina antes: baja por la transversal a la calle de abajo
        cu = max(x for x in cruces if x < ub); abajo = max(x for x in calles_v if x < c)
        ramas.append((f"{nm} (poniente)", [(ua, c), (cu, c)], lotes_de(c, ub=cu)))
        if ub - cu > 8: ramas.append((f"{nm} (oriente)", [(ub, c), (cu, c)], lotes_de(c, ua=cu)))
        ramas.append((f"Enlace {CRUCES[cruces.index(cu)]}", [(cu, c), (cu, abajo)], []))
    elif ub >= U_TOR - 20:
        ramas.append((nm, [(ua, c), (U_TOR, c)], lotes_de(c, ub=U_TOR)))
        if ub - U_TOR > 8: ramas.append((f"{nm} (punta)", [(ub, c), (U_TOR, c)], lotes_de(c, ua=U_TOR)))
    else:
        ramas.append((nm, [(ua, c), (ub, c)], lotes_de(c)))
ua, ub = tramo(vb); ub = min(ub, U_TOR)
ramas.append(("Bulevar Nogal (sur)", [(ua, vb - 6.3), (ub, vb - 6.3)], lotes_de(vb, "arriba")))
ramas.append(("Bulevar Nogal (norte)", [(ua, vb + 6.3), (ub, vb + 6.3)], lotes_de(vb, "abajo")))
# colector oriente: bajo la pista por el borde SE, luego por la transversal Tórtola hasta la planta
v_in = c_ptar + ROW_CALLE / 2 + 14
sur = sorted([r for r in ramas if r[1][-1][1] < vb - 1 and not r[0].startswith("Enlace")], key=lambda r: r[1][-1][1])
nodos_col = []
for r in sur:
    e = r[1][-1]; p = en_pista(*e); nodos_col.append((p, [r]))
nodos_col.append(((U_TOR, vb - 6.3), [r for r in ramas if r[0] == "Bulevar Nogal (sur)"]))
nodos_col.append(((U_TOR, vb + 6.3), [r for r in ramas if r[0] == "Bulevar Nogal (norte)"]))
for c in sorted(x for x in calles_v if vb < x < c_ptar + 1):
    nodos_col.append(((U_TOR, c), [r for r in ramas if abs(r[1][-1][1] - c) < 1 and abs(r[1][-1][0] - U_TOR) < 1]))
nodos_col.append(((U_TOR, v_in), []))
# rama norte (calle de la planta y las de más arriba) bajando por Tórtola a la planta
norte = [r for r in ramas if r[1][-1][1] > c_ptar + 1 or (abs(r[1][-1][1] - c_ptar) < 1 and abs(r[1][-1][0] - U_TOR) < 1)]
# cálculo de plantillas
def plantilla(rama, inv0=None):
    pts = rama[1]; L = sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))
    zi = zf(*pts[0]) - H0 if inv0 is None else inv0
    return zi, zi - S_AT * L, L
inv_fin = {}
detalle_ramas = []
def recibe(r):                                                   # enlaces que caen a media rama (calle de abajo)
    if r[0].startswith("Enlace"): return []
    a, b = r[1][0], r[1][-1]
    return [x for x in ramas if x[0].startswith("Enlace") and abs(x[1][-1][1] - a[1]) < 1 and min(a[0], b[0]) <= x[1][-1][0] <= max(a[0], b[0])]
def calc(r, entradas=()):
    pts = r[1]; L = sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))
    zi = zf(*pts[0]) - H0; zo = zi - S_AT * L
    for s_, iv in entradas: zo = min(zo, iv - 0.03 - S_AT * (L - s_))
    inv_fin[r[0]] = zo
    n = len(r[2]) + sum(lotes_aguas_arriba(e) for e in recibe(r))
    q = q_lote(max(n, 1)); d = next(x for x in DIAM if q <= 0.8 * q_lleno(x, S_AT))
    detalle_ramas.append(dict(nombre=r[0], largo=round(L), lotes=len(r[2]), q=round(q, 1), diam=d, prof_ini=round(zf(*pts[0]) - zi, 2), prof_fin=round(zf(*pts[-1]) - zo, 2)))
def lotes_aguas_arriba(r):
    n = len(r[2])
    if r[0].startswith("Enlace"):
        cu, ctop = r[1][0]; n += sum(len(x[2]) for x in ramas if x[1][-1] == (cu, ctop) and not x[0].startswith("Enlace"))
    return n
receptoras = [r for r in ramas if recibe(r)]
for r in ramas:
    if not r[0].startswith("Enlace") and r not in receptoras: calc(r)
for r in ramas:
    if not r[0].startswith("Enlace"): continue
    cu, ctop = r[1][0]; arriba = [x for x in ramas if x[1][-1] == (cu, ctop) and not x[0].startswith("Enlace")]
    zi = min(inv_fin[x[0]] for x in arriba) - 0.03; L = math.dist(*r[1]); inv_fin[r[0]] = zi - S_AT * L
    detalle_ramas.append(dict(nombre=r[0], largo=round(L), lotes=0, q=round(q_lote(lotes_aguas_arriba(r)), 1), diam=0.20,
                              prof_ini=round(zf(cu, ctop) - zi, 2), prof_fin=round(zf(*r[1][-1]) - inv_fin[r[0]], 2)))
for r in receptoras:
    calc(r, [(abs(e[1][-1][0] - r[1][0][0]), inv_fin[e[0]]) for e in recibe(r)])
col = []; inv = None; n_acum = 0; prev = None; perfil = []; dist_acum = 0.0
for (p, llegan) in nodos_col:
    llegan2 = list(llegan)
    if prev is not None:
        d_ = math.dist(prev, p); dist_acum += d_; inv = inv - S_COL * d_
    for r in llegan2:
        cand = inv_fin[r[0]] - 0.03 - (S_AT * math.dist(r[1][-1], p))
        inv = cand if inv is None else min(inv, cand)
        n_acum += len(r[2]) + sum(lotes_aguas_arriba(e) for e in recibe(r))
    col.append(dict(p=p, inv=inv, n=n_acum, prof=zf(*p) - inv)); perfil.append((dist_acum, zf(*p), inv)); prev = p
n_total = col[-1]["n"]
q_col = q_lote(N); d_col = next(x for x in DIAM if q_col <= 0.8 * q_lleno(x, S_COL))
prof_max_at = max(r["prof_fin"] for r in detalle_ramas)
prof_llegada = col[-1]["prof"]
print(f"colector: {len(col)} nodos, Ø{d_col*100:.0f} cm, Q {q_col:.1f} l/s, profundidad a la llegada {prof_llegada:.2f} m; atarjea más honda {prof_max_at:.2f} m")
for r in ramas: F("san_atarjea" if not r[0].startswith("Enlace") else "san_atarjea", LineString(r[1]), nombre=r[0], d=20)
F("san_colector", LineString([c_["p"] for c_ in col]), nombre="Colector oriente", d=round(d_col * 100))
for c in sorted(x for x in calles_v if x > c_ptar + 1):
    F("san_colector", LineString([(U_TOR, c), (U_TOR, v_in)]), nombre="Colector Tórtola norte", d=round(d_col * 100))
# pozos de visita: en cada cruce, cada cambio de dirección y a no más de 100 m
pozos = []
for r in ramas:
    for a, b in zip(r[1][:-1], r[1][1:]):
        L = math.dist(a, b); k = max(1, math.ceil(L / 100))
        for i in range(k + 1): pozos.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    for c in cruces:
        a, b = r[1][0], r[1][-1]
        if abs(a[1] - b[1]) < 1 and min(a[0], b[0]) < c < max(a[0], b[0]): pozos.append((c, a[1]))
for c_ in col: pozos.append(c_["p"])
pz = []
for p in pozos:
    if all(math.dist(p, q) > 15 for q in pz): pz.append(p)
pozos = pz
for p in pozos: F("san_pozo", Point(p))
F("san_llegada", Point(U_TOR + 8, v_in), nombre="Pozo de llegada y cárcamo de la planta")

# ======================= planta de tratamiento y vaso =======================
pa_ = ptar.bounds
corte_v = pa_[1] + 0.45 * (pa_[3] - pa_[1])
planta = ptar.intersection(box(pa_[0], pa_[1], pa_[2], corte_v))
vaso = ptar.intersection(box(pa_[0], corte_v + 4, pa_[2], pa_[3])).buffer(-3, join_style=2)
F("ptar_planta", planta, nombre="Planta de tratamiento")
F("vaso", vaso, nombre="Vaso de tormentas")
Q_PTAR = math.ceil(Qs_med * 1.15)                              # capacidad de proyecto
trat_dia = Qs_med * 86400 / 1000 * 0.95
trat_anual = trat_dia * 365
# riego de nogales: evapotranspiración de una huerta de nogal en La Laguna ≈ 1.3 m al año; en ciudad se riega al 60 %
n_nogales = int(quedan.sum()); ET_NOGAL, FRAC_RIEGO, M2_ARBOL = 1.30, 0.60, SV * 12.7
riego_nogal = n_nogales * M2_ARBOL * ET_NOGAL * FRAC_RIEGO
pasto = sum(p["g"].area for p in parques) * 0.25 + bulevar.area * 0.1
riego_otros = pasto * 1.1
riego_total = riego_nogal + riego_otros
print(f"tratada {trat_anual:,.0f} m³/año; riego nogales {riego_nogal:,.0f} + otros {riego_otros:,.0f} = {riego_total:,.0f} m³/año")

# ======================= drenaje pluvial (cero descarga a la calle de afuera) =======================
P10, P50, I10 = 50.0, 70.0, 100.0                               # mm en 1 h (Tr 10 y 50 años) e intensidad de 15 min, Tr 10 (por confirmar con isoyetas)
A_lotes = float(sum(L["g"].area for L in lotes)) + com_m2 + predio_super
techo, cochera_m2 = 9.0 * 14.0, 5.85 * 5.5                    # azotea de la casa (planta alta) y cochera
C_lote = (techo * 0.95 + cochera_m2 * 0.90 + (330 - techo - cochera_m2) * 0.20) / 330
A_calle = float(vial.area + arroyos_bul.area + sum(g.area for g in acc_calles))
A_verde = float(R.area - A_lotes - A_calle - planta.area - vaso.area)
esc = lambda P: dict(lotes=A_lotes * C_lote * P / 1000, calles=A_calle * 0.90 * P / 1000, verde=A_verde * 0.15 * P / 1000)
E10, E50 = esc(P10), esc(P50)
ret_lotes = N * (330 - techo - cochera_m2) * 0.10 * 0.9           # jardín 10 cm abajo de la banqueta
jardin_lluvia = sendero_bul.intersection(R).area * (3.2 / 5.6)  # dos franjas de 1.6 m en el camellón
V_jl = jardin_lluvia * 0.40
V_par = sum(p["g"].area for p in parques) * 0.30                 # bordo de 30 cm: se encharcan como se regaba la huerta
V_zanja = eje_pista.length * 0.8 * 1.0 * 0.35
V_vaso = vaso.area * 1.5
estacs = [el["estacionamiento"], el["estacionamiento2"], estac_vis]
A_cajas = sum(g.area for g in estacs)
V_cajas = A_cajas * 0.9 * 0.95                                  # cajas de infiltración de 90 cm bajo el pavimento
# bocas de tormenta y pozos de absorción en los puntos bajos (cruces de cada calle con las transversales)
bocas = []
for c in calles_v:
    ua, ub = tramo(c)
    for x in cruces:
        if ua + 8 < x < ub - 8: bocas += [(x - ROW_CALLE / 2 - 1.5, c - 3.2), (x - ROW_CALLE / 2 - 1.5, c + 3.2)]
for x in cruces:
    if tramo(vb)[0] < x < tramo(vb)[1]: bocas += [(x - ROW_CALLE / 2 - 1.5, vb - 9.6), (x - ROW_CALLE / 2 - 1.5, vb + 9.6)]
V_pozos = len(bocas) / 2 * (math.pi * 0.6 ** 2 * 10 * 0.35 + 2 * math.pi * 0.6 * 10 * 1e-5 * 3600)
almacen = dict(jardines_lluvia=V_jl, parques=V_par, zanja_pista=V_zanja, pozos=V_pozos, cajas=V_cajas, vaso=V_vaso)
print("pluvial", {k: round(v) for k, v in E10.items()}, "ret lotes", round(ret_lotes), {k: round(v) for k, v in almacen.items()})
for p in bocas[0::2]: F("plu_pozo", Point(p))
for p in bocas[1::2]: F("plu_pozo", Point(p))
F("plu_jardin", sendero_bul.intersection(R), nombre="Jardín de lluvia del camellón")
for p in parques: F("plu_parque", p["g"], nombre="Parque con bordo de 30 cm")
F("plu_zanja", eje_pista, nombre="Zanja de infiltración bajo la pista")
for g in estacs: F("plu_cajas", g, nombre="Cajas de infiltración bajo el estacionamiento")
def flecha(a, b, capa, cada=55):
    L = math.dist(a, b)
    if L < 6: return
    F(capa, LineString([a, b]))
    ux_, uy_ = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    for s in np.arange(min(cada / 2, L * 0.6), L, cada):
        px, py = a[0] + ux_ * s, a[1] + uy_ * s
        F(capa + "_punta", LineString([(px - 4 * ux_ - 2.5 * uy_, py - 4 * uy_ + 2.5 * ux_), (px, py), (px - 4 * ux_ + 2.5 * uy_, py - 4 * uy_ - 2.5 * ux_)]))
for c in calles_v:                                               # calles: parteaguas a media cuadra, bajan a los cruces
    ua, ub = tramo(c); xs = [ua] + [x for x in cruces if ua < x < ub] + [ub]
    for a, b in zip(xs[:-1], xs[1:]):
        m = (a + b) / 2
        flecha((m, c), (a + 6, c), "plu_flujo"); flecha((m, c), (b - 6, c), "plu_flujo")
for x in cruces:                                                 # transversales: bajan al bulevar
    va_, vz_ = tramo_v(x)
    if va_ < bul[0]: flecha((x, va_ + 3), (x, bul[0] - 1), "plu_flujo", 70)
    if vz_ > bul[1]: flecha((x, vz_ - 3), (x, bul[1] + 1), "plu_flujo", 70)
ua, ub = tramo(vb)
for dv in (-6.3, 6.3): flecha((ua + 5, vb + dv), (ub - 2, vb + dv), "plu_flujo", 90)
flecha((U_TOR, vb + 10), (U_TOR, corte_v + 6), "plu_flujo", 40)

# ======================= agua potable =======================
def mejor_sitio(zona, w, h, cerca, paso=2.0):
    """Rectángulo w × h dentro de la zona que tapa menos nogales (y, empate, el más cercano a `cerca`)."""
    zp = prepared.prep(zona); mejor = None; b_ = zona.bounds
    for x in np.arange(b_[0], b_[2] - w, paso):
        for y in np.arange(b_[1], b_[3] - h, paso):
            g = box(x, y, x + w, y + h)
            if not zp.contains(g): continue
            n = int(np.sum(quedan & (Q[:, 0] > x - 2) & (Q[:, 0] < x + w + 2) & (Q[:, 1] > y - 2) & (Q[:, 1] < y + h + 2)))
            k = (n, g.centroid.distance(cerca))
            if mejor is None or k < mejor[0]: mejor = (k, g)
    return mejor[1], mejor[0][0]
ocupado = unary_union([super_, estac_vis] + acc_calles).buffer(3)
lado_oeste = plaza_acc.difference(ocupado).intersection(box(u0 - 10, v0 - 10, c_pri + ANCHO[0], v1))
lado_este = plaza_acc.difference(ocupado).intersection(box(c_pri + ANCHO[1], v0 - 10, u1 + 10, v1))
tanque, arb_tanque = mejor_sitio(lado_oeste, 24, 20, Point(c_pri - 40, v_pri + 40))
acopio, arb_acopio = mejor_sitio(lado_este, 12, 16, Point(c_pri + 70, v_pri + 18))
CISTERNA = math.ceil(Qmd * 11 * 3.6 / 50) * 50 + 0                # regulación de 11 h del gasto máximo diario
print("cisterna", CISTERNA, "m³; nogales tapados: tanque", arb_tanque, "acopio", arb_acopio)
F("agua_tanque", tanque, nombre=f"Cisterna {CISTERNA} m³ y bombeo")
F("acopio", acopio, nombre="Acopio de basura y reciclaje")
tc = tanque.centroid
lineas_agua = []
def LA(pts, d, nombre): lineas_agua.append((pts, d, nombre)); F("agua_linea", LineString(pts), d=d, nombre=nombre)
LA([(tc.x, tc.y), (c_pri - 8, tc.y), (c_pri - 8, bul[0] + 2)], 200, "Alimentación 8\"")
for dv in (-11.5, 11.5): LA([(tramo(vb)[0], vb + dv), (tramo(vb)[1], vb + dv)], 200, "Bulevar 8\"")
for x in cruces:
    a_, b_ = tramo_v(x); LA([(x + 4.5, a_), (x + 4.5, b_)], 150, "Transversal 6\"")
for c in calles_v:
    a_, b_ = tramo(c); LA([(a_, c + 4.5), (b_, c + 4.5)], 100, "Calle 4\"")
L_agua = {d: sum(LineString(p).length for p, dd, _ in lineas_agua if dd == d) for d in (200, 150, 100)}
hidrantes = []
for j, c in enumerate(calles_v + [vb]):
    for i, x in enumerate(cruces):
        a_, b_ = tramo(c)
        if a_ < x < b_ and (i + j) % 2 == 0: hidrantes.append((x + ROW_CALLE / 2 + 1, c + (4.5 if c != vb else 11.5)))
for p in hidrantes: F("hidrante", Point(p))
valvulas = sum(1 for c in calles_v + [vb] for x in cruces if tramo(c)[0] < x < tramo(c)[1])
# red morada: de la planta, por el camellón y las transversales; goteo a cada nogal desde la banqueta
morada = []
def LM(pts, d, nombre): morada.append((pts, d)); F("morada", LineString(pts), d=d, nombre=nombre)
LM([(U_TOR + 8, corte_v - 4), (U_TOR - 2, corte_v - 4), (U_TOR - 2, vb), (tramo(vb)[0], vb)], 100, "Principal 4\" (camellón)")
for x in cruces:
    a_, b_ = tramo_v(x); LM([(x - 4.5, a_), (x - 4.5, b_)], 75, "Transversal 3\"")
L_morada = {d: sum(LineString(p).length for p, dd in morada if dd == d) for d in (100, 75)}
L_goteo = 2 * L_largo
TANQUE_TRAT = math.ceil(trat_dia / 50) * 50

# ======================= electricidad y telecom =======================
DEM_CASA = 4.0                                                  # kVA diversificados por casa (minisplits en verano)
trafos = []
def poner_trafos(Ls, v_ban):
    if not Ls: return
    xs = sorted(L["g"].centroid.x for L in Ls); k = max(1, math.ceil(len(Ls) / 16))
    for i in range(k):
        x = xs[min(len(xs) - 1, int((i + 0.5) / k * len(xs)))]; trafos.append((x, v_ban(i)))
for c in calles_v:
    poner_trafos(lotes_de(c), lambda i, c=c: c + (4.9 if i % 2 == 0 else -4.9))
poner_trafos(lotes_de(vb, "arriba"), lambda i: vb - 13.5)
poner_trafos(lotes_de(vb, "abajo"), lambda i: vb + 13.5)
especiales = [(cA["g"].centroid.x, cA["g"].centroid.y, "Club social · 150 kVA trifásico"), (cB["g"].centroid.x, cB["g"].centroid.y, "Club deportivo · 112.5 kVA trifásico"),
              (super_.centroid.x + 25, super_.centroid.y, "Acceso, súper y comercio · 150 kVA trifásico"), (planta.centroid.x, planta.centroid.y, "Planta y bombeo · 150 kVA trifásico")]
for p in trafos: F("trafo", Point(p))
for x, y, n in especiales: F("trafo_esp", Point(x, y), nombre=n)
kva = N * DEM_CASA + 150 + 112.5 + 150 + 150 + sum(TIPOS[k][2] * luz["cuenta"][k] for k in TIPOS) / 1000 / 0.9
print("transformadores", len(trafos), "+", len(especiales), "demanda", round(kva), "kVA")
# calles: cruces elevados, nomenclatura, salida de emergencia
mesas = []
for x in cruces:
    if tramo(vb)[0] < x < tramo(vb)[1]:
        for a_, b_ in ((vb - 9.8, vb - 2.8), (vb + 2.8, vb + 9.8)): mesas.append(box(x - ROW_CALLE / 2 - 4, a_, x - ROW_CALLE / 2 - 0.5, b_))
va_c = row(ka[0]) if ka else vb
mesas.append(box(c_pri - 3.5, va_c - 1.75, c_pri + 3.5, va_c + 1.75))     # entre el club social y el deportivo
for g in mesas: F("mesa", g, nombre="Cruce elevado")
cruces_n = sum(1 for c in calles_v + [vb] for x in cruces if tramo(c)[0] < x < tramo(c)[1])
x_em = cruces[min(range(len(cruces)), key=lambda i: abs(cruces[i] - (u0 + u1) / 2))]
v_em = tramo_v(x_em)[1]
F("emergencia", LineString([(x_em, v_em - 2), (x_em, v_em + TRAIL + 6)]), nombre=f"Salida de emergencia (calle {CRUCES[cruces.index(x_em)]})")
F("emergencia_p", Point(x_em, v_em + TRAIL / 2), nombre=f"Salida de emergencia · {CRUCES[cruces.index(x_em)]}")
barda = R.exterior.length - (ANCHO[1] - ANCHO[0])

# ======================= cantidades =======================
A_pav = float(pavimento.area); A_pav_bul = float(arroyos_bul.area + sum(g.area for g in acc_calles))
A_banq = float(vial.area - pavimento.area) + float(bulevar.area - arroyos_bul.area - sendero_bul.area)
L_guarn = float(pavimento.boundary.length + arroyos_bul.boundary.length)
L_atarjea = sum(r["largo"] for r in detalle_ramas)
L_colector = float(sum(math.dist(a["p"], b["p"]) for a, b in zip(col[:-1], col[1:])) + sum(abs(v_in - c) for c in calles_v if c > c_ptar + 1))
L_calles_tot = L_largo + L_cruce + L_bul
# ======================= presupuesto por partida (MXN 2026 sin IVA) =======================
P_ = []
def partida(serv, elem, espec, cant, unidad, pu): P_.append(dict(servicio=serv, elemento=elem, especificacion=espec, cantidad=round(cant, 1), unidad=unidad, pu=pu, importe=round(cant * pu)))
partida("Terracerías", "Despalme, nivelación y rasantes", "Despalme 20 cm, cortes y rellenos compactados al 95 % Proctor para dar 0.3 % mínimo a las calles", gross, "m²", 55)
partida("Calles", "Pavimento de calles", "Concreto hidráulico MR 42 kg/cm², 15 cm, losas de 3.5 × 3.5 m con juntas aserradas y selladas; base hidráulica 20 cm y subbase 20 cm al 95 %", A_pav, "m²", 1250)
partida("Calles", "Pavimento de bulevar y acceso", "Concreto hidráulico MR 45 kg/cm², 18 cm, con pasajuntas; base 20 cm y subbase 25 cm", A_pav_bul, "m²", 1420)
partida("Calles", "Guarniciones", "Concreto f'c 200 kg/cm², sección 15 × 20 × 40 cm; rebajadas en cocheras y esquinas (rampas)", L_guarn, "m", 480)
partida("Calles", "Banquetas", "Concreto f'c 150 kg/cm², 10 cm, escobillado, con malla 6-6/10-10; pendiente 2 % hacia la calle", A_banq, "m²", 520)
partida("Calles", "Cruces elevados", "Mesa de concreto de 3.5 m, rampas 1:10, pintura blanca; en el bulevar y frente al club", len(mesas), "pza", 95000)
partida("Calles", "Señalamiento y nomenclatura", "Placa de calle en cada esquina (nombre y números), alto, 30 km/h, pintura de pasos peatonales", cruces_n, "cruce", 18000)
partida("Drenaje pluvial", "Bocas de tormenta", "Rejilla de piso de fierro fundido 90 × 60 cm, en los puntos bajos junto a la guarnición", len(bocas), "pza", 28000)
partida("Drenaje pluvial", "Pozos de absorción", "Ø 1.2 m, 10 m de profundidad, ademe de tabique junteado a hueso, grava de 1–2\" y filtro de arena; uno por cada 2 bocas", len(bocas) / 2, "pza", 65000)
partida("Drenaje pluvial", "Jardines de lluvia del camellón", "2 franjas de 1.6 m, 40 cm abajo del sendero: grava, suelo filtrante y plantas del desierto; cortes en guarnición cada 10 m", jardin_lluvia, "m²", 750)
partida("Drenaje pluvial", "Bordos de los parques", "Bordo de tierra compactada de 30 cm con vertedor de piedra hacia la calle", sum(p["g"].length for p in parques), "m", 900)
partida("Drenaje pluvial", "Zanja de infiltración de la pista", "Zanja de 0.8 × 1.0 m con grava y geotextil, bajo la pista", eje_pista.length, "m", 650)
partida("Drenaje pluvial", "Cajas de infiltración", "Módulos plásticos de 90 cm bajo los 3 estacionamientos, con geotextil y registro de limpieza", A_cajas, "m²", 2600)
partida("Drenaje pluvial", "Vaso de tormentas", "Vaso de 1.5 m con taludes 3:1, fondo de grava; rebosa a la calle norte solo en tormentas de más de 50 años", V_vaso, "m³", 380)
partida("Drenaje sanitario", "Atarjeas", "PVC sanitario serie 20 (NMX-E-215) Ø 20 cm, pendiente 2.5 al millar, cama de arena 10 cm y relleno compactado", L_atarjea, "m", 2400)
partida("Drenaje sanitario", "Colector", f"PVC/PEAD Ø {d_col*100:.0f} cm, pendiente 2 al millar, bajo la pista y la calle Tórtola", L_colector, "m", 4800)
partida("Drenaje sanitario", "Pozos de visita", "Concreto prefabricado Ø 1.2 m con brocal y tapa de fierro fundido; en cada cruce y a no más de 100 m", len(pozos), "pza", 32000)
partida("Drenaje sanitario", "Descargas domiciliarias", "PVC Ø 15 cm al 1 %, con registro de 40 × 60 cm dentro del lote", N + 20, "pza", 7800)
partida("Tratamiento", "Planta de tratamiento", f"Lodos activados (SBR) de {Q_PTAR} l/s, compacta y cerrada, con desinfección UV; cumple NOM-003-SEMARNAT para riego", Q_PTAR, "l/s", 2_100_000)
partida("Tratamiento", "Tanque de agua tratada", "Concreto, enterrado, con bombeo a presión constante para la red morada", TANQUE_TRAT, "m³", 5200)
partida("Tratamiento", "Red morada principal", "PEAD morado Ø 4\" por el camellón", L_morada[100], "m", 650)
partida("Tratamiento", "Red morada transversal", "PEAD morado Ø 3\" por las transversales", L_morada[75], "m", 480)
partida("Tratamiento", "Goteo a los nogales", "PEAD morado Ø 2\" en las dos banquetas con 2 goteros autocompensados de 8 l/h por nogal y válvulas por sector", L_goteo, "m", 260)
partida("Agua potable", "Pozo y derechos", "Rehabilitación del pozo de la huerta, equipo sumergible, macromedidor y cambio de uso de los derechos (agrícola a público urbano) ante Conagua", 1, "lote", 6_000_000)
partida("Agua potable", "Cisterna y bombeo", f"Cisterna de concreto {CISTERNA} m³ y equipo de presión constante (3 + 1 bombas con variador), cloración", 1, "lote", CISTERNA * 9500 + 3_200_000)
partida("Agua potable", "Línea de 8\"", "PEAD RD 17 / PVC hidráulico C-10 Ø 200 mm", L_agua[200], "m", 1700)
partida("Agua potable", "Línea de 6\"", "PVC hidráulico C-10 Ø 150 mm", L_agua[150], "m", 1250)
partida("Agua potable", "Línea de 4\"", "PVC hidráulico C-10 Ø 100 mm, bajo la banqueta norte de cada calle", L_agua[100], "m", 900)
partida("Agua potable", "Cajas de válvulas", "Válvulas de seccionamiento en cada cruce: se puede cortar una cuadra sin dejar sin agua al resto", valvulas, "pza", 35000)
partida("Agua potable", "Hidrantes", "Hidrante de columna 6\" con 2 salidas de 2.5\" y una de 4.5\", a tresbolillo en los cruces (ninguna casa a más de 150 m)", len(hidrantes), "pza", 48000)
partida("Agua potable", "Tomas domiciliarias", "PEAD Ø 1/2\" con abrazadera, llave de banqueta y medidor en nicho", N + 20, "pza", 6800)
partida("Electricidad", "Red subterránea por lote", "Media tensión 13.2 kV en anillo, transformadores pedestal monofásicos de 75 kVA (uno cada ≈ 16 casas), baja tensión 240/120 V, ductos y registros, según norma CFE de distribución subterránea", N, "lote", 46000)
partida("Electricidad", "Transformadores trifásicos", "Pedestal trifásico para club, acceso y súper, y planta con bombeo", len(especiales), "pza", 420000)
partida("Electricidad", "Aportación y obras de conexión CFE", "Por confirmar con la factibilidad de CFE", 1, "lote", 6_000_000)
partida("Alumbrado", "Arbotantes de calle", "Ya contados en la capa de iluminación (los de paisaje y acceso se suman aparte)", luz["cuenta"]["calle"], "pza", TIPOS["calle"][1])
partida("Telecomunicaciones", "Ductería", "3 ductos PAD Ø 2\" (2 para operadores y 1 de reserva) bajo la banqueta norte, registro cada 50 m; red abierta a cualquier operador de fibra", L_calles_tot, "m", 210)
partida("Barda y accesos", "Barda perimetral", "Block de concreto 15 cm, 2.8 m de alto, castillos cada 3 m, aplanado y pintura; cimentación corrida", barda, "m", 4800)
partida("Barda y accesos", "Salida de emergencia", "Portón de 6 m con cerradura de bomberos, a la calle del norte", 1, "pza", 180000)
partida("Barda y accesos", "Acopio de basura y reciclaje", "Cuarto ventilado con 6 contenedores y lavado, junto a la salida y antes de las plumas: el camión no entra", 1, "pza", 650000)
sub = sum(x["importe"] for x in P_)
partida("Indirectos", "Proyecto ejecutivo y estudios", "Topografía, mecánica de suelos, prueba de infiltración, proyecto ejecutivo de todas las redes y trámites", 1, "global", round(sub * 0.025))
partida("Indirectos", "Supervisión y laboratorio", "Control de calidad de concretos, compactaciones y pruebas de hermeticidad y presión", 1, "global", round(sub * 0.02))
partida("Indirectos", "Imprevistos", "5 % sobre la obra", 1, "global", round(sub * 0.05))
URB = sum(x["importe"] for x in P_)
antes = URB_CALLE * vial_m2 + URB_BASE * gross
print(f"urbanización por partida ${URB/1e6:,.1f} M (antes ${antes/1e6:,.1f} M)")

# ======================= cuota de mantenimiento =======================
energia_ptar = trat_dia * 0.7 * 30 * 3.2                       # 0.7 kWh/m³ a $3.2/kWh (tarifa de bombeo de aguas residuales)
CUOTA = [("Seguridad 24 h", "2 guardias por turno en la caseta, 1 rondín y monitoreo de cámaras", 9 * 17000 + 15000),
         ("Jardinería y riego", "6 jardineros, insumos y mantenimiento del goteo de los nogales", 6 * 12500 + 25000),
         ("Planta de tratamiento", "Operador, energía, químicos y retiro de lodos", 16000 + energia_ptar + 12000),
         ("Iluminación", "Energía y mantenimiento de la capa de iluminación", (luz["energia_anual"] + luz["mantenimiento_anual"]) / 12),
         ("Club y áreas comunes", "Limpieza, gimnasio, canchas y alberca de riego", 45000),
         ("Bombeo de agua potable", "Si el fraccionamiento opera el pozo (si lo opera SIMAS, se paga en el recibo)", 0),
         ("Administración", "Administrador, contador, seguros y app de visitas", 50000)]
sub_c = sum(x[2] for x in CUOTA)
CUOTA.append(("Fondo de reserva", "10 % para pavimentos, bombas y renovaciones", sub_c * 0.10))
cuota_total = sum(x[2] for x in CUOTA); cuota_casa = cuota_total / N
print(f"cuota {cuota_total:,.0f} al mes; {cuota_casa:,.0f} por casa")

# ======================= actualizar el resumen del proyecto =======================
res["costo"] = round(res["costo"] - antes + URB); res["margen"] = round(res["venta"] - res["costo"]); res["roi"] = round(100 * res["margen"] / res["costo"], 1)
res["urbanizacion"] = round(URB); res["urbanizacion_m2"] = round(URB / gross); res["cuota_casa_mes"] = round(cuota_casa)
res["servicios"] = dict(poblacion=round(POB), agua_lps=round(Qmd, 1), drenaje_lps=round(Qs_med, 1), ptar_lps=Q_PTAR, trafos=len(trafos), hidrantes=len(hidrantes), pozos_visita=len(pozos))
json.dump({"type": "FeatureCollection", "bruto_m2": round(gross), "resumen": res, "features": feats}, open(f"{OUT}/confort.geojson", "w"), separators=(",", ":"), ensure_ascii=False)

# ======================= salidas =======================
def wgs(g):
    return stf(to_w, geo(g))
def coords(g):
    if g.geom_type == "Point": return [round(g.x, 6), round(g.y, 6)]
    if g.geom_type == "LineString": return [[round(x, 6), round(y, 6)] for x, y in g.coords]
    if g.geom_type == "Polygon": return [[[round(x, 6), round(y, 6)] for x, y in g.exterior.coords]]
sf = []
for capa, g, kw in SF:
    for x in (g.geoms if hasattr(g, "geoms") else [g]):
        if x.is_empty: continue
        if x.geom_type == "LinearRing": x = LineString(x.coords)
        w = wgs(x); sf.append({"type": "Feature", "properties": dict(capa=capa, **{k: (v if not isinstance(v, (np.floating, np.integer)) else float(v)) for k, v in kw.items()}), "geometry": {"type": w.geom_type, "coordinates": coords(w)}})
json.dump({"type": "FeatureCollection", "features": sf}, open(f"{OUT}/servicios.geojson", "w"), separators=(",", ":"), ensure_ascii=False)
with open(f"{OUT}/especificaciones.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh); w.writerow(["Servicio", "Elemento", "Especificación", "Cantidad", "Unidad", "Precio unitario (MXN)", "Importe (MXN)"])
    for x in P_: w.writerow([x["servicio"], x["elemento"], x["especificacion"], x["cantidad"], x["unidad"], x["pu"], x["importe"]])
print("servicios", len(sf), "elementos")
SALIDA = dict(TERR=TERR, POB=POB, Qmed=Qmed, Qmd=Qmd, Qmh=Qmh, Qs_med=Qs_med, Qs_max=Qs_max, Qs_ext=Qs_ext, vol_anual=vol_anual)
exec(open(os.path.join(_aqui, "n6_servicios_html.py")).read())
