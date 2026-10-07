"""N6 · iluminación de lo que mantiene el fraccionamiento (calles, bulevar, pista, parques, club y acceso) → public/n6/luces.json.
Luz cálida (2700–3000 K) y baja: arbotantes entre los nogales, focos de piso a los nogales de las áreas comunes,
balizas en la pista y el acceso más iluminado. Suma al costo del proyecto lo que no entra en «redes» (todo menos los arbotantes de calle)."""
import os, sys, math
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
ALTURA = {"calle": 6.0, "bulevar": 8.0, "acceso": 9.0, "peatonal": 3.5, "baliza": 0.9, "nogal": 0.0, "estac": 6.0, "cancha": 6.0, "caseta": 3.0, "letrero": 0.6}
PREFIJO = {"calle": "C", "bulevar": "B", "acceso": "A", "peatonal": "P", "baliza": "Z", "nogal": "N", "estac": "E", "cancha": "Q", "caseta": "K", "letrero": "L"}
KWH, MANT = 5.0, 0.04                         # $/kWh de alumbrado (CFE, aprox.) y mantenimiento anual sobre la inversión
P = []                                        # (u, v, tipo, zona)
def nombre_calle(c): return ("Bulevar " if nombre_v[round(c, 2)][1] == "bulevar" else "") + nombre_v[round(c, 2)][0]
def nombre_cruce(x): return CRUCES[min(range(len(cruces)), key=lambda i: abs(cruces[i] - x))]
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
            if inner_p.contains(Point(u, v)): P.append((u, v, "calle", f"{nombre_calle(c)} · cuadra {cuadra_de(u)} · acera {'norte' if v > c else 'sur'}"))
for c in cruces:
    ln = shapely.LineString([(c, v0 - 10), (c, v1 + 10)]).intersection(inner)
    for seg in getattr(ln, "geoms", [ln]):
        a, b = seg.bounds[1], seg.bounds[3]
        for k, v in enumerate(np.arange(a + 6, b - 3, PASO)):
            if bul[0] - 2 < v < bul[1] + 2: continue                  # el cruce con el bulevar ya lo alumbra el bulevar
            u = c + (4.6 if k % 2 == 0 else -4.6)
            u, v = libre_de_troncos(u, v, "v")
            if acc_p.contains(Point(u, v)): continue
            if inner_p.contains(Point(u, v)): P.append((u, v, "calle", f"{nombre_cruce(c)} · acera {'oriente' if u > c else 'poniente'}"))
# 1b) Esquinas: en cada cruce, un arbotante en dos esquinas opuestas (el peatón cruza con luz); se quitan los de calle que quedaban a menos de 12 m
esquinas = []
for c in calles_v:
    for x in cruces:
        for du, dv in ((-ROW_CALLE / 2 - 1.5, 4.6), (ROW_CALLE / 2 + 1.5, -4.6)):
            u, v = x + du, c + dv
            if not inner_p.contains(Point(u, v)) or acc_p.contains(Point(u, v)): continue
            u, v = libre_de_troncos(u, v, "u", 2.5)
            esquinas.append((u, v, "calle", f"{nombre_calle(c)} esquina {nombre_cruce(x)} · esquina {'noroeste' if dv > 0 else 'sureste'}"))
P = [p for p in P if p[2] != "calle" or all(math.hypot(p[0] - q[0], p[1] - q[1]) >= 12 for q in esquinas)] + esquinas
# 2) Bulevar: arbotante doble en el camellón cada 30 m; postes peatonales en el sendero, a la mitad entre arbotantes;
#    foco de piso a cada nogal de sus banquetas
ln = shapely.LineString([(u0 - 10, vb), (u1 + 10, vb)]).intersection(inner)
for seg in getattr(ln, "geoms", [ln]):
    a, b = seg.bounds[0], seg.bounds[2]
    for u in np.arange(a + 8, b - 4, 30.0):
        P.append((u, vb, "bulevar", f"Bulevar Nogal · camellón · cuadra {cuadra_de(u)}"))
        if u + 15 < b - 4: P.append((u + 15, vb + 1.6, "peatonal", f"Bulevar Nogal · sendero · cuadra {cuadra_de(u)}"))
m_bul = quedan & (np.abs(Q[:, 1] - vb) > 8) & (np.abs(Q[:, 1] - vb) < BUL + 2.5)
for i in np.where(m_bul)[0]:
    if inner_p.contains(Point(Q[i])): P.append((Q[i, 0], Q[i, 1], "nogal", f"Bulevar Nogal · banqueta {'norte' if Q[i, 1] > vb else 'sur'} · cuadra {cuadra_de(Q[i, 0])}"))
# 3) Pista para correr: balizas cada 20 m (fuera del cruce del acceso)
eje_pista = R.buffer(-TRAIL / 2, join_style=2).exterior
s0_pista = eje_pista.project(Point(c_pri, v_pri))                    # km 0 de la pista: frente al acceso
for d in np.arange(0, eje_pista.length, 20.0):
    pt = eje_pista.interpolate((s0_pista + d) % eje_pista.length)
    if not acceso_zona.buffer(4).contains(pt): P.append((pt.x, pt.y, "baliza", f"Pista · km {d / 1000:.2f}"))
# 4) Parques: foco de piso a cada nogal y postes peatonales en la orilla cada 30 m
for p in parques:
    gp = prepared.prep(p["g"].buffer(-0.5))
    for i in np.where(quedan)[0]:
        if gp.contains(Point(Q[i])): P.append((Q[i, 0], Q[i, 1], "nogal", f"Parque {nombre_cruce(p['g'].centroid.x)}"))
    orilla = p["g"].buffer(-1.5).exterior
    for d in np.arange(5, orilla.length, 30.0):
        pt = orilla.interpolate(d); P.append((pt.x, pt.y, "peatonal", f"Parque {nombre_cruce(p['g'].centroid.x)} · orilla"))
# 5) Club: nogales iluminados, canchas, estacionamientos y andadores
edif = unary_union(list(el.values())).buffer(1.5)
for cel in (cA, cB):
    gp = prepared.prep(cel["g"].buffer(-0.5).difference(edif))
    for i in np.where(quedan)[0]:
        if gp.contains(Point(Q[i])): P.append((Q[i, 0], Q[i, 1], "nogal", "Club social" if cel is cA else "Club deportivo"))
def proyectores(g, n_lado, nombre):
    a, b, c_, d = g.bounds
    for u in np.linspace(a + 1, c_ - 1, n_lado):
        P.append((u, b - 1.2, "cancha", f"Club deportivo · {nombre}")); P.append((u, d + 1.2, "cancha", f"Club deportivo · {nombre}"))
proyectores(el["tenis"], 3, "tenis")
proyectores(el["padel1"], 2, "pádel 1"); proyectores(el["padel2"], 2, "pádel 2")
for k, nm in (("estacionamiento", "Club social · estacionamiento"), ("estacionamiento2", "Club deportivo · estacionamiento")):
    a, b, c_, d = el[k].bounds
    for u in np.arange(a + 6, c_ - 2, 20.0): P.append((u, (b + d) / 2, "estac", nm))
for k, nm in (("salon", "Club social · entrada del salón"), ("gimnasio", "Club social · entrada del gimnasio")):
    a, b, c_, d = el[k].bounds
    P.append((a - 2, b + 3, "peatonal", nm)); P.append((c_ + 2, b + 3, "peatonal", nm))
# 6) Acceso: postes altos en las orillas y en las islas, casetas, letrero, nogales de la plaza y estacionamiento de visitas
for v in np.arange(v_pri + 4, v_gate + 22, 14.0):
    P.append((c_pri + ANCHO[0] - 1.2, v, "acceso", f"Acceso · orilla poniente · {v - v_pri:.0f} m de la calzada")); P.append((c_pri + ANCHO[1] - 1.5, v, "acceso", f"Acceso · orilla oriente · {v - v_pri:.0f} m de la calzada"))
for n_, a, b, t in CARRILES:
    if t == "isla":
        for v in (v_pri + ISLA_V0 + 2, (v_pri + ISLA_V0 + v_pri + RETORNO[0]) / 2, v_pri + RETORNO[1] + 2, v_gate - 8):
            P.append((c_pri + (a + b) / 2, v, "acceso", f"Acceso · {n_.lower()} · {v - v_pri:.0f} m de la calzada"))
        P.append((c_pri + (a + b) / 2, v_gate, "caseta", f"Acceso · {n_.lower()}"))
P.append((c_pri + ANCHO[0] - 3, v_pri + 3, "letrero", "Acceso · letrero poniente")); P.append((c_pri + ANCHO[1] + 1, v_pri + 3, "letrero", "Acceso · letrero oriente"))
plaza_libre = prepared.prep(plaza_acc.difference(unary_union([super_, estac_vis] + acc_calles).buffer(1.0)))
for i in np.where(quedan)[0]:
    if plaza_libre.contains(Point(Q[i])): P.append((Q[i, 0], Q[i, 1], "nogal", "Plaza de acceso"))
a, b, c_, d = estac_vis.bounds
for u in np.arange(a + 5, c_ - 2, 18.0): P.append((u, (b + d) / 2, "estac", "Acceso · estacionamiento de visitas"))
a, b, c_, d = super_.bounds
for v in (b + 4, (b + d) / 2, d - 4): P.append((c_ + 1.5, v, "peatonal", "Acceso · andador del súper"))
dentro_R = prepared.prep(R)
P = [p for p in P if dentro_R.contains(Point(p[0], p[1]))]
import math

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
pw = []; cont = {t: 0 for t in TIPOS}
import csv as _csv
with open(f"{OUT}/luminarias.csv", "w", newline="", encoding="utf-8-sig") as fh:
    wr = _csv.writer(fh); wr.writerow(["id", "tipo", "luminaria", "dónde", "longitud", "latitud", "u_m", "v_m", "altura_m", "watts", "horas_por_noche"])
    for u, v, t, zona in sorted(P, key=lambda p: (orden_t.index(p[2]), p[0], p[1])):
        cont[t] += 1; idn = f"{PREFIJO[t]}-{cont[t]:03d}"
        w = stf(to_w, geo(Point(u, v))); pw.append([round(w.x, 6), round(w.y, 6), orden_t.index(t), idn, zona])
        wr.writerow([idn, t, TIPOS[t][0], zona, round(w.x, 6), round(w.y, 6), round(u, 1), round(v, 1), ALTURA[t], TIPOS[t][2], TIPOS[t][3]])
luz["km0_pista"] = [round(x, 6) for x in (lambda w: (w.x, w.y))(stf(to_w, geo(eje_pista.interpolate(s0_pista))))]
luz["pista_m"] = round(float(eje_pista.length))
json.dump({"tipos": orden_t, "resumen": luz, "p": pw}, open(f"{OUT}/luces.json", "w"), separators=(",", ":"), ensure_ascii=False)
print("luces", len(pw), "costo nuevo", res["costo"], "margen", res["margen"], res["roi"])
