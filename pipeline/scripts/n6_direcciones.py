"""N6 · nombres de calles, direcciones y capa rentable, sobre el diseño con confort (n6_confort.py)."""
import sys, json
args = sys.argv[1:]
exec(open(__file__.replace("n6_direcciones.py", "n6_confort.py")).read())

FRACC = "La Nogalera"                       # nombre del fraccionamiento (provisional)
# Calles: las que corren a lo largo (paralelas al bulevar) son árboles; las que cruzan, aves. Las dos en orden alfabético:
# de sur a norte y de poniente a oriente. Si sabes una letra, sabes dónde está la calle.
LARGAS = ["Álamo", "Cedro", "Ébano", "Encino", "Nogal", "Olmo", "Roble", "Sabino"]
CRUCES = ["Alondra", "Calandria", "Cenzontle", "Colibrí", "Garza", "Gorrión", "Jilguero", "Paloma", "Tórtola"]
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
for (c, lado_n), Ls in por_calle.items():
    Ls.sort(key=lambda L: L["g"].centroid.x)
    for k, L in enumerate(Ls):
        L["calle"] = nombre_v[c][0]; L["num"] = 2 * k + (1 if lado_n else 2)
dirs = [f'{L["calle"]} {L["num"]}' for L in lotes]
assert len(set(dirs)) == len(dirs), "direcciones repetidas"
max_num = max(L["num"] for L in lotes)

# Parques y plazas toman el nombre de su calle de cruce más cercana
def ave_cercana(g): return CRUCES[min(range(len(cruces)), key=lambda i: abs(cruces[i] - g.centroid.x))]

# ===== Capa rentable (se queda en manos del desarrollador y genera renta mensual) =====
x_esp = [L["g"] for L in comercial]
rent = []
def r(nombre, g, m2_rentable, renta_m2, inv_m2, nota, unidades=None):
    rent.append(dict(nombre=nombre, g=g, m2=round(m2_rentable), renta=round(m2_rentable * renta_m2), inversion=round(m2_rentable * inv_m2), nota=nota, unidades=unidades))
r("Locales sobre Espinoza", unary_union(x_esp), 0.65 * sum(g.area for g in x_esp), 180, 14000,
  "Consultorios, restaurantes, panadería, veterinaria y lavandería con frente a la avenida y estacionamiento al frente", unidades=round(0.65 * sum(g.area for g in x_esp) / 120))
r("Súper, café y farmacia", super_, super_.area, 200, 14000, "Ancla del día a día; abre a la calle y los vecinos entran caminando")
guard = box(c_pri - 58, v_pri + 34, c_pri - 9, v_pri + 52).intersection(plaza_acc)
r("Guardería y estancia", guard, guard.area, 150, 15000, "Junto a la caseta: dejas a los niños de camino al trabajo sin dar vueltas")
bodegas = box(servicio.bounds[0] + 4, servicio.bounds[1] + 4, servicio.bounds[0] + 44, servicio.bounds[1] + 28).intersection(servicio)
r("Mini bodegas", bodegas, bodegas.area * 0.75, 260, 8000, "Unas 80 bodegas de 3 a 9 m²: las casas de 328 m² se quedan sin espacio para guardar", unidades=80)
r("Coworking", el["salon"], 30 * 6, 420, 9000, "Planta alta del salón: 30 lugares y 2 salas de juntas, junto a las oficinas de la administración", unidades=30)
r("Lockers de paquetería y carga de autos eléctricos", estac_vis, 0, 0, 0, "En el estacionamiento de visitas")
rent[-1].update(renta=35000, inversion=1500000)
total_renta = sum(x["renta"] for x in rent); total_inv = sum(x["inversion"] for x in rent)
valor = total_renta * 12 / 0.09
print(f"rentable: ${total_renta/1e3:.0f} mil/mes, inversión ${total_inv/1e6:.0f} M, valor a 9 % ${valor/1e6:.0f} M, regreso {total_inv/(total_renta*12):.1f} años")
print(f"direcciones: {len(dirs)}; número más alto {max_num}")

# ===== Salida: enriquece confort.geojson =====
it = iter([f for f in feats if f["properties"]["capa"] == "lote"])
for L in lotes:
    f = next(it); f["properties"].update(dir=f'{L["calle"]} {L["num"]}')
for f in feats:
    p = f["properties"]
    if p["capa"] == "salon" and p.get("nombre", "").startswith("Salón"): p["nombre"] = "Salón (PB) · oficinas y coworking (PA)"
# nombres de parques y plazas por su calle de cruce
FLORES = ["Azahar", "Bugambilia", "Dalia", "Gardenia", "Jazmín", "Lavanda", "Magnolia", "Nardo", "Violeta", "Orquídea"]   # plazas: flores, en orden alfabético de poniente a oriente
pp = sorted([f for f in feats if f["properties"]["capa"] in ("parque", "plaza")], key=lambda f: shape(f["geometry"]).centroid.x)
for f in pp:
    gu = affinity.rotate(affinity.translate(stf(to_u, shape(f["geometry"])), -cx, -cy), -th, origin=(0, 0))
    ave = ave_cercana(gu)
    p = f["properties"]
    if p["capa"] == "parque":
        p["nombre"] = f"Parque {ave} · " + p["nombre"].split(" · ", 1)[1]
    else:
        p["nombre"] = f"Plaza {FLORES.pop(0)}"
for x in rent:
    if x["g"].is_empty: continue
    add("rentable", x["g"], nombre=x["nombre"], renta=x["renta"], inversion=x["inversion"], m2=x["m2"], nota=x["nota"])
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
res.update(fraccionamiento=FRACC, calles_largas=LARGAS, calles_cruce=CRUCES, num_max=max_num,
           rentable=[{k: v for k, v in x.items() if k != "g"} for x in rent], renta_mensual=total_renta, inversion_rentable=total_inv, valor_rentable=round(valor))
json.dump({"type": "FeatureCollection", "bruto_m2": round(gross), "resumen": res, "features": feats}, open(f"{OUT}/confort.geojson", "w"), separators=(",", ":"), ensure_ascii=False)
print("listo")
