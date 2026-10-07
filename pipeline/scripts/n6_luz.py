"""N6 · iluminación de lo que mantiene el fraccionamiento (calles, bulevar, pista, parques, club y acceso) → public/n6/luces.json.
Luz cálida (2700–3000 K) y baja: arbotantes entre los nogales, focos de piso a los nogales de las áreas comunes,
balizas en la pista y el acceso más iluminado. Suma al costo del proyecto lo que no entra en «redes» (todo menos los arbotantes de calle)."""
import os, sys
_aqui = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
__file__ = os.path.join(_aqui, "n6_direcciones.py")
exec(open(__file__).read())

# tipo: (nombre, costo instalado MXN con su parte de cable y ducto, watts, horas encendida por noche)
TIPOS = {
    "calle":    ("Arbotante de calle · 6 m, LED 40 W", 26000, 40, 11.5),
    "bulevar":  ("Arbotante doble del bulevar · 8 m, 2 × 50 W", 52000, 100, 11.5),
    "acceso":   ("Poste del acceso · 9 m, LED 80 W", 45000, 80, 11.5),
    "peatonal": ("Poste peatonal · 3.5 m, LED 20 W", 16000, 20, 11.5),
    "baliza":   ("Baliza de la pista · 90 cm, LED 8 W", 6500, 8, 11.5),
    "nogal":    ("Foco de piso a un nogal · LED 12 W, 2700 K", 5500, 12, 5.0),
    "estac":    ("Poste de estacionamiento · 6 m, LED 40 W", 24000, 40, 11.5),
    "cancha":   ("Proyector de cancha · 6 m, LED 200 W", 38000, 200, 3.0),
    "caseta":   ("Luz de caseta y plumas · 6 × 15 W", 30000, 90, 11.5),
    "letrero":  ("Letrero de acceso iluminado · 2 × 30 W", 18000, 60, 11.5),
}
KWH, MANT = 5.0, 0.04                         # $/kWh de alumbrado (CFE, aprox.) y mantenimiento anual sobre la inversión
P = []                                        # (u, v, tipo)
quedan = np.array([i not in reubicar for i in range(len(Q))])
Qk = Q[quedan]
def libre_de_troncos(u, v, eje, rango=4.0):
    """Mueve el punto a lo largo de su calle (±rango) para alejarlo lo más posible de los troncos."""
    mejor = None
    for d in np.arange(-rango, rango + 0.01, 0.5):
        uu_, vv_ = (u + d, v) if eje == "u" else (u, v + d)
        dist = np.min(np.hypot(Qk[:, 0] - uu_, Qk[:, 1] - vv_)) if len(Qk) else 99
        if mejor is None or dist > mejor[0] + 0.25 or (abs(dist - mejor[0]) <= 0.25 and abs(d) < abs(mejor[1])): mejor = (dist, d, uu_, vv_)
    return mejor[2], mejor[3]
inner_p = prepared.prep(inner.buffer(-0.5))
amen_p = prepared.prep(unary_union([cA["g"], cB["g"]] + [p["g"] for p in parques]))
acceso_zona = box(c_pri + ANCHO[0] - 3, v0 - 10, c_pri + ANCHO[1] + 3, v_gate + 25)
acc_p = prepared.prep(acceso_zona)

# 1) Calles: arbotantes en la banqueta, a tresbolillo cada ≈ 25 m (dos lotes), corridos para no quedar junto a un tronco
PASO = 25.4
for c in calles_v:
    ln = shapely.LineString([(u0 - 10, c), (u1 + 10, c)]).intersection(inner)
    for seg in getattr(ln, "geoms", [ln]):
        a, b = seg.bounds[0], seg.bounds[2]
        for k, u in enumerate(np.arange(a + 6, b - 3, PASO)):
            v = c + (4.6 if k % 2 == 0 else -4.6)
            u, v = libre_de_troncos(u, v, "u")
            if inner_p.contains(Point(u, v)): P.append((u, v, "calle"))
for c in cruces:
    ln = shapely.LineString([(c, v0 - 10), (c, v1 + 10)]).intersection(inner)
    for seg in getattr(ln, "geoms", [ln]):
        a, b = seg.bounds[1], seg.bounds[3]
        for k, v in enumerate(np.arange(a + 6, b - 3, PASO)):
            if bul[0] - 2 < v < bul[1] + 2: continue                  # el cruce con el bulevar ya lo alumbra el bulevar
            u = c + (4.6 if k % 2 == 0 else -4.6)
            u, v = libre_de_troncos(u, v, "v")
            if acc_p.contains(Point(u, v)): continue
            if inner_p.contains(Point(u, v)): P.append((u, v, "calle"))
# 2) Bulevar: arbotante doble en el camellón cada 30 m; postes peatonales en el sendero, a la mitad entre arbotantes;
#    foco de piso a cada nogal de sus banquetas
ln = shapely.LineString([(u0 - 10, vb), (u1 + 10, vb)]).intersection(inner)
for seg in getattr(ln, "geoms", [ln]):
    a, b = seg.bounds[0], seg.bounds[2]
    for u in np.arange(a + 8, b - 4, 30.0):
        P.append((u, vb, "bulevar"))
        if u + 15 < b - 4: P.append((u + 15, vb + 1.6, "peatonal"))
m_bul = quedan & (np.abs(Q[:, 1] - vb) > 8) & (np.abs(Q[:, 1] - vb) < BUL + 2.5)
for i in np.where(m_bul)[0]:
    if inner_p.contains(Point(Q[i])): P.append((Q[i, 0], Q[i, 1], "nogal"))
# 3) Pista para correr: balizas cada 20 m (fuera del cruce del acceso)
eje_pista = R.buffer(-TRAIL / 2, join_style=2).exterior
for d in np.arange(0, eje_pista.length, 20.0):
    pt = eje_pista.interpolate(d)
    if not acceso_zona.buffer(4).contains(pt): P.append((pt.x, pt.y, "baliza"))
# 4) Parques: foco de piso a cada nogal y postes peatonales en la orilla cada 30 m
for p in parques:
    gp = prepared.prep(p["g"].buffer(-0.5))
    for i in np.where(quedan)[0]:
        if gp.contains(Point(Q[i])): P.append((Q[i, 0], Q[i, 1], "nogal"))
    orilla = p["g"].buffer(-1.5).exterior
    for d in np.arange(5, orilla.length, 30.0):
        pt = orilla.interpolate(d); P.append((pt.x, pt.y, "peatonal"))
# 5) Club: nogales iluminados, canchas, estacionamientos y andadores
edif = unary_union(list(el.values())).buffer(1.5)
for cel in (cA, cB):
    gp = prepared.prep(cel["g"].buffer(-0.5).difference(edif))
    for i in np.where(quedan)[0]:
        if gp.contains(Point(Q[i])): P.append((Q[i, 0], Q[i, 1], "nogal"))
def proyectores(g, n_lado):
    a, b, c_, d = g.bounds
    for u in np.linspace(a + 1, c_ - 1, n_lado):
        P.append((u, b - 1.2, "cancha")); P.append((u, d + 1.2, "cancha"))
proyectores(el["tenis"], 3)
proyectores(el["padel1"], 2); proyectores(el["padel2"], 2)
for k in ("estacionamiento", "estacionamiento2"):
    a, b, c_, d = el[k].bounds
    for u in np.arange(a + 6, c_ - 2, 20.0): P.append((u, (b + d) / 2, "estac"))
for k in ("salon", "gimnasio"):                                     # entrada de cada edificio
    a, b, c_, d = el[k].bounds
    P.append((a - 2, b + 3, "peatonal")); P.append((c_ + 2, b + 3, "peatonal"))
# 6) Acceso: postes altos en las orillas y en las islas, casetas, letrero, nogales de la plaza y estacionamiento de visitas
for v in np.arange(v_pri + 4, v_gate + 22, 14.0):
    P.append((c_pri + ANCHO[0] - 1.2, v, "acceso")); P.append((c_pri + ANCHO[1] - 1.5, v, "acceso"))
for n_, a, b, t in CARRILES:
    if t == "isla":
        for v in (v_pri + ISLA_V0 + 2, (v_pri + ISLA_V0 + v_pri + RETORNO[0]) / 2, v_pri + RETORNO[1] + 2, v_gate - 8):
            P.append((c_pri + (a + b) / 2, v, "acceso"))
        P.append((c_pri + (a + b) / 2, v_gate, "caseta"))
P.append((c_pri + ANCHO[0] - 3, v_pri + 3, "letrero")); P.append((c_pri + ANCHO[1] + 1, v_pri + 3, "letrero"))
plaza_libre = prepared.prep(plaza_acc.difference(unary_union([super_, estac_vis] + acc_calles).buffer(1.0)))
for i in np.where(quedan)[0]:
    if plaza_libre.contains(Point(Q[i])): P.append((Q[i, 0], Q[i, 1], "nogal"))
a, b, c_, d = estac_vis.bounds
for u in np.arange(a + 5, c_ - 2, 18.0): P.append((u, (b + d) / 2, "estac"))
a, b, c_, d = super_.bounds
for v in (b + 4, (b + d) / 2, d - 4): P.append((c_ + 1.5, v, "peatonal"))   # andador del súper hacia el estacionamiento
dentro_R = prepared.prep(R)
P = [p for p in P if dentro_R.contains(Point(p[0], p[1]))]

# ===== números =====
cuenta = {k: sum(1 for p in P if p[2] == k) for k in TIPOS}
inv = {k: cuenta[k] * TIPOS[k][1] for k in TIPOS}
kwh = {k: cuenta[k] * TIPOS[k][2] * TIPOS[k][3] * 365 / 1000 for k in TIPOS}
inv_total = sum(inv.values()); inv_paisaje = inv_total - inv["calle"]
energia = sum(kwh.values()) * KWH
anual = energia + MANT * inv_total
luz = dict(puntos=len(P), cuenta=cuenta, inversion=round(inv_total), inversion_paisaje=round(inv_paisaje), inversion_calles=round(inv["calle"]),
           kwh_anual=round(sum(kwh.values())), energia_anual=round(energia), mantenimiento_anual=round(MANT * inv_total),
           cuota_casa_mes=round(anual / 12 / (len(lotes)), 0), nogales_iluminados=cuenta["nogal"],
           tipos={k: dict(nombre=TIPOS[k][0], n=cuenta[k], costo=TIPOS[k][1], watts=TIPOS[k][2], horas=TIPOS[k][3]) for k in TIPOS})
print(json.dumps({k: v for k, v in luz.items() if k != "tipos"}, ensure_ascii=False))
# el costo de paisaje y acceso se suma al proyecto (los arbotantes de calle ya están en «redes»)
res["costo"] = round(res["costo"] + inv_paisaje); res["margen"] = round(res["venta"] - res["costo"])
res["roi"] = round(100 * res["margen"] / res["costo"], 1); res["iluminacion"] = luz
res["terreno_m2_precio"] = TERRENO; res["terreno_valor"] = round(TERRENO * gross)
json.dump({"type": "FeatureCollection", "bruto_m2": round(gross), "resumen": res, "features": feats}, open(f"{OUT}/confort.geojson", "w"), separators=(",", ":"), ensure_ascii=False)
orden_t = list(TIPOS)
pw = []
for u, v, t in P:
    w = stf(to_w, geo(Point(u, v))); pw.append([round(w.x, 6), round(w.y, 6), orden_t.index(t)])
json.dump({"tipos": orden_t, "resumen": luz, "p": pw}, open(f"{OUT}/luces.json", "w"), separators=(",", ":"), ensure_ascii=False)
print("luces", len(pw), "costo nuevo", res["costo"], "margen", res["margen"], res["roi"])
