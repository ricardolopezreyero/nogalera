"""N6 · el modelo completo del fraccionamiento con la geometría real: cada lote con su casa y su fachada, los 1,943 nogales en su sitio,
las 1,013 luminarias reales, calles con banquetas y guarniciones, bulevar, cruces elevados, parques detallados, club (salón con oficinas,
gimnasio, canchas, estacionamientos), acceso completo, barda con pilastras y cámaras, planta de tratamiento, pozos, cisterna, transformadores,
hidrantes, comercio y las huertas vecinas. Escribe public/datos/escenas/completo.json y lo agrega al índice.
Se corre después de n6_escenas (lo importa): python3 scripts/n6_completo.py"""
import os, sys, json, math
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import n6_escenas as ES
from n6_escenas import Escena, COL, FACH, SEQ, W, PB_D, PA_D, FRENTE, LOTE_W, LOTE_D, girar, guardar, ojo, cam, uv, poly, FC, SV, ARB, LIM, lim, V_CALLE, dentro, umin, umax, vmin, vmax
import n6_acceso_calc as ACC, n6_acceso as ACP
DAT = ES.DAT
LZ = json.load(open(f"{DAT}/luces.json")); SG = json.load(open(f"{DAT}/servicios.geojson"))
E = Escena("completo"); r = E.rnd
feats = FC["features"]
def capa(c): return [f for f in feats if f["properties"]["capa"] == c]
def caja_de(pts): us = [q[0] for q in pts]; vs = [q[1] for q in pts]; return min(us), max(us), min(vs), max(vs)
rot = capa("rotulo")
U_CRUCE = {}
for f in rot:
    if f["properties"]["eje"] != "largo": U_CRUCE.setdefault(f["properties"]["nombre"], []).append(uv(*f["geometry"]["coordinates"])[0])
U_CRUCE = {k: sorted(v)[len(v) // 2] for k, v in U_CRUCE.items()}
U_ACC, V_LIM = -351.0, -263.0                      # eje del acceso y límite sur del terreno (de las casetas e islas del plano)
FRENTE_SEG = max(zip(lim[:-1], lim[1:]), key=lambda ab: (ab[1][0] - ab[0][0]) ** 2 if ab[0][1] < V_LIM + 40 and ab[1][1] < V_LIM + 40 else -1)   # el tramo más largo del límite por el sur
(_fa, _fb) = FRENTE_SEG
if _fa[0] > _fb[0]: _fa, _fb = _fb, _fa
ANG_FRENTE = math.atan2(_fb[1] - _fa[1], _fb[0] - _fa[0])
def v_frente(u): return _fa[1] + (_fb[1] - _fa[1]) * (u - _fa[0]) / (_fb[0] - _fa[0])

# ---------- 1 · el terreno, las calles y el bulevar ----------
E.suelo(-1500, -1000, 1500, 1000, -0.62, "#d8cdb3")                                   # el valle
E.prisma(lim, -0.5, 0.12, COL["tierra"], "suelo", "suelo")                            # la huerta (suelo de los lotes y las áreas comunes)
for f in capa("vial"): E.prisma(poly(f), -0.4, 0.06, COL["banqueta"], "suelo", "suelo")          # derecho de vía completo: banqueta
# arroyos de 7 m sobre los ejes de cada calle larga y de cada cruce, con guarnición
u_lim0, u_lim1 = -715, 650
for nombre, vc in V_CALLE.items():
    if nombre == "Nogal": continue
    us = [q[0] for f in capa("lote") if f["properties"]["dir"].rsplit(" ", 1)[0] == nombre for q in poly(f)]
    if not us: continue
    a, b = min(us) - 6, max(us) + 6
    E.suelo(a, vc - 3.5, b, vc + 3.5, -0.47, COL["asfalto"])
    for s_ in (-1, 1): E.caja(a, vc + s_ * 3.5 - (0.15 if s_ < 0 else 0), -0.47, b - a, 0.15, 0.16, COL["guarnicion"], "suelo")
for nombre, uc in U_CRUCE.items():
    vs = [q[1] for f in capa("lote") if f["properties"]["dir"].rsplit(" ", 1)[0] == nombre for q in poly(f)]
    a, b = (min(vs) - 6, max(vs) + 6) if vs else (vmin + 8, vmax - 8)
    E.suelo(uc - 3.5, a, uc + 3.5, b, -0.47, COL["asfalto"])
    for s_ in (-1, 1): E.caja(uc + s_ * 3.5 - (0.15 if s_ < 0 else 0), a, -0.47, 0.15, b - a, 0.16, COL["guarnicion"], "suelo")
for f in capa("bulevar"): E.prisma(poly(f), -0.4, 0.05, COL["banqueta"], "suelo", "suelo")
for f in capa("arroyo"): E.prisma(poly(f), -0.47, 0.07, COL["asfalto"], "suelo", "suelo")
for f in capa("sendero"): E.prisma(poly(f), -0.42, 0.04, COL["grava"], "suelo", "suelo")
for f in capa("sendero"):
    u0, u1, v0, v1 = caja_de(poly(f)); vc = (v0 + v1) / 2
    E.suelo(u0, vc - 1.2, u1, vc + 1.2, -0.34, COL["andador"])
    for k in range(int((u1 - u0) / 2.4)):
        xx = u0 + 1.2 + k * 2.4
        for yy in (vc - 2.6, vc + 2.6): E.cil(xx + r.uniform(-0.3, 0.3), yy + r.uniform(-0.5, 0.5), r.uniform(0.25, 0.45), -0.42, r.uniform(0.25, 0.6), r.choice(["#6f9a4a", "#8aa85e", "#5f8c42"]), "plantas", n=6)
for f in [f for f in SG["features"] if f["properties"].get("capa") == "mesa"]: E.prisma(poly(f), -0.4, 0.09, COL["adoquin"] if "adoquin" in COL else COL["andador"], "suelo", "suelo")   # cruces elevados
for f in capa("pista"): E.prisma(poly(f), -0.36, 0.03, "#e2ded4", "suelo", "suelo")
for f in capa("isla"): E.prisma(poly(f), -0.47, 0.3, COL["pasto"], "suelo", "suelo")
for f in capa("plaza_acceso"): E.prisma(poly(f), -0.36, 0.05, COL["andador"], "suelo", "suelo")
for f in capa("estacionamiento"):
    pts = poly(f); E.prisma(pts, -0.38, 0.03, COL["cochera"], "suelo", "suelo"); u0, u1, v0, v1 = caja_de(pts)
    for k in range(int((u1 - u0) / 2.6)): E.caja(u0 + 0.5 + k * 2.6, v0 + 0.5, -0.35, 0.1, 5.0, 0.005, "#f0f0f0", "suelo", "suelo")
    for k in range(int((u1 - u0) / 2.6)):
        if r.random() < 0.35: E.auto(u0 + 0.9 + k * 2.6, v0 + 0.8, math.pi / 2)
ca, cb = _fa[0] - 400, _fb[0] + 400                                                        # la calzada José Vasconcelos, paralela al frente
E.caja(ca, v_frente(ca) - 44, -0.52, cb - ca, 28, 0.02, COL["asfalto"], "suelo", "suelo", rot=ANG_FRENTE, px=ca, py=v_frente(ca))
for k in range(int((cb - ca) / 4)): E.caja(ca + k * 4, v_frente(ca) - 30.1, -0.52, 2.0, 0.15, 0.005, "#f0f0f0", "suelo", "suelo", rot=ANG_FRENTE, px=ca, py=v_frente(ca))
E.caja(ca, v_frente(ca) - 16, -0.42, cb - ca, 13, 0.02, COL["banqueta"], "suelo", "suelo", rot=ANG_FRENTE, px=ca, py=v_frente(ca))
for xx in range(int(ca), int(cb), 30): E.arbusto(xx, v_frente(xx) - 9 + r.uniform(-1, 1), 0.7, 0.8)

# ---------- 2 · los lotes: cada uno con su casa, su fachada, cochera, jardín y bardas ----------
BUL_V = (V_CALLE.get("Nogal", 17.0))
n_lotes = 0
for f in capa("lote"):
    p = f["properties"]; pts = poly(f); u0, u1, v0, v1 = caja_de(pts); w, d = u1 - u0, v1 - v0
    calle = p["dir"].rsplit(" ", 1)[0]; cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
    fach = p["fachada"]; auto = r.random() < 0.35; noche = False
    if calle in U_CRUCE:                                                  # frente a un cruce: la calle está al este o al oeste
        if U_CRUCE[calle] > cu: E.lote(fach, u1, v0, math.pi / 2, noche, auto, w=d, d=w)
        else: E.lote(fach, u0, v1, -math.pi / 2, noche, auto, w=d, d=w)
    else:
        vc = BUL_V if p["frente"] == "bulevar" else V_CALLE.get(calle, v0 - 10)
        if vc > cv: E.lote(fach, u1, v1, math.pi, noche, auto, w=w, d=d)
        else: E.lote(fach, u0, v0, 0.0, noche, auto, w=w, d=d)
    n_lotes += 1

# ---------- 3 · los nogales reales (los que se quedan) y las huertas vecinas ----------
for a in ARB:
    if a[2]: continue
    u, v = uv(a[0], a[1]); E.nogal(u, v, max(0.75, min(1.2, a[3] / 10.0)))
for gi in range(int((umin - 260) / 12.62), int((umax + 260) / 12.62)):
    for gj in range(int((vmin - 200) / 12.62), int((vmax + 200) / 12.62)):
        x, y = gi * 12.62 + 3.0, gj * 12.62 + 1.0
        if dentro(x, y) or (v_frente(x) - 55 < y < v_frente(x) + 3) or (abs(x - U_ACC) < 70 and y < v_frente(x) + 3): continue
        if r.random() < 0.74: E.nogal_simple(x, y, 9.0 + r.random() * 2.5)

# ---------- 4 · luminarias reales ----------
TIPOS = LZ["tipos"]
def hacia_calle(u, v):
    """Vector unitario hacia el eje de calle más cercano (para que el brazo del arbotante apunte al arroyo)."""
    mejor = (1e9, (0, 1))
    for vc in V_CALLE.values(): mejor = min(mejor, (abs(vc - v), (0, 1 if vc > v else -1)))
    for uc in U_CRUCE.values(): mejor = min(mejor, (abs(uc - u), (1 if uc > u else -1, 0)))
    return mejor[1]
def arbot(u, v, h, brazo, dir_, poste=True):
    """Arbotante: poste y brazo hacia dir_ (dx, dy), con la luminaria en la punta."""
    dx, dy = dir_; ang = math.atan2(dy, dx)
    if poste: E.cil(u, v, 0.08, -0.32, h, COL["poste"], "luz", n=6)
    E.caja(u, v - 0.05, h - 0.1, brazo, 0.1, 0.1, COL["poste"], "luz", rot=ang, px=u, py=v)
    E.caja(u + brazo - 0.3, v - 0.15, h - 0.25, 0.6, 0.3, 0.15, "#e6e6e6", "luz", rot=ang, px=u, py=v)
for lon, lat, ti, clave, desc in LZ["p"]:
    u, v = uv(lon, lat); t = TIPOS[ti]
    if t == "calle": arbot(u, v, 6.0, 1.3, hacia_calle(u, v))
    elif t == "bulevar": arbot(u, v, 8.0, 1.4, (0, 1)); arbot(u, v, 8.0, 1.4, (0, -1), poste=False)
    elif t == "acceso": arbot(u, v, 9.0, 1.6, (1, 0) if u < U_ACC else (-1, 0))
    elif t == "peatonal": E.farol(u, v, 3.5)
    elif t == "baliza": E.cil(u, v, 0.06, -0.32, 0.9, COL["poste"], "luz", n=6); E.caja(u - 0.08, v - 0.08, 0.55, 0.16, 0.16, 0.1, "#eaeaea", "luz")
    elif t == "nogal": E.caja(u - 0.1, v - 0.1, -0.32, 0.2, 0.2, 0.18, "#333333", "luz")
    elif t == "estac": E.arbotante(u, v, 6.0, 1.0, 1)
    elif t == "cancha": E.cil(u, v, 0.1, -0.32, 6.0, COL["poste"], "luz", n=6); E.caja(u - 0.3, v - 0.2, 5.6, 0.6, 0.4, 0.3, "#333333", "luz")
    elif t == "letrero": pass

# ---------- 5 · parques: bordo, senderos, pérgola, bancas, juegos, botes ----------
for f in capa("parque"):
    pts = poly(f); u0, u1, v0, v1 = caja_de(pts); cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
    E.prisma(pts, -0.36, 0.05, COL["pasto"], "suelo", "suelo")
    for k in range(int(v0), int(v1), 8): E.suelo(u0 + 0.8, k, u1 - 0.8, min(k + 4, v1 - 0.8), -0.355, COL["pasto2"])
    for xx, yy, ww, dd in ((u0, v0, u1 - u0, 0.6), (u0, v1 - 0.6, u1 - u0, 0.6), (u0, v0, 0.6, v1 - v0), (u1 - 0.6, v0, 0.6, v1 - v0)): E.caja(xx, yy, -0.36, ww, dd, 0.3, COL["bordo"], "suelo")
    E.suelo(cu - 1.2, v0, cu + 1.2, v1, -0.34, COL["andador"]); E.suelo(u0, cv - 1.2, u1, cv + 1.2, -0.34, COL["andador"])       # cruz de andadores
    rr = min(u1 - u0, v1 - v0) / 2 - 4
    for a in range(0, 360, 5):
        t = math.radians(a); E.caja(cu + rr * math.cos(t) - 1.3, cv + rr * math.sin(t) - 1.0, -0.34, 2.6, 2.0, 0.02, COL["andador"], "suelo", "suelo", rot=t + math.pi / 2, px=cu + rr * math.cos(t), py=cv + rr * math.sin(t))
    E.pergola(cu - 5, cv + 6, 10, 5, 2.9); E.suelo(cu - 5.5, cv + 5.5, cu + 5.5, cv + 11.5, -0.33, COL["andador"])
    for xx in (cu - 3.5, cu + 0.5): E.caja(xx, cv + 7.5, -0.34, 1.8, 0.8, 0.75, COL["madera"], "mob"); E.caja(xx, cv + 6.8, -0.34, 1.8, 0.4, 0.45, COL["madera"], "mob")
    for k in range(8):
        t = math.radians(k * 45 + 20); E.banca(cu + (rr + 1.6) * math.cos(t), cv + (rr + 1.6) * math.sin(t), t + math.pi / 2)
    for k in range(4):
        t = math.radians(k * 90 + 65); E.cil(cu + (rr + 2.2) * math.cos(t), cv + (rr + 2.2) * math.sin(t), 0.3, -0.34, 0.9, "#4a4a4a", "mob", n=6)
    E.juegos(u1 - 24, v0 + 6)                                                             # juegos de colores
    E.flores(cu - 6, cv + 12, 12, 1.2, 14); E.flores(cu - 6, cv + 4.2, 12, 1.0, 12)      # jardineras de flores junto a la pérgola
    for k in range(10): E.persona(u0 + 3 + r.random() * (u1 - u0 - 6), v0 + 3 + r.random() * (v1 - v0 - 6), r.choice([1.7, 1.75, 1.65, 1.2, 1.0]))
    for k in range(3): E.perro(u0 + 5 + r.random() * (u1 - u0 - 10), v0 + 5 + r.random() * (v1 - v0 - 10))
    E.persona(u1 - 20, v0 + 4, 1.0, "#ffd166"); E.persona(u1 - 12, v0 + 9, 1.1, "#118ab2"); E.persona(u1 - 16, v0 + 12.5, 1.7, "#9b2226")   # niños en los juegos y una mamá
    for k in range(6): E.arbusto(u0 + 2 + r.random() * (u1 - u0 - 4), v0 + 2 + r.random() * 3, 0.6, 0.6); E.arbusto(u0 + 2 + r.random() * (u1 - u0 - 4), v1 - 5 + r.random() * 3, 0.6, 0.6)

# ---------- 6 · el club: salón con oficinas, gimnasio, canchas, plaza ----------
for f in capa("comunal"): E.prisma(poly(f), -0.36, 0.04, COL["pasto2"], "suelo", "suelo")
def edificio(u0, u1, v0, v1, niveles, color, vidrio_frente=True, frente="sur"):
    h = 3.6 * niveles
    E.caja(u0, v0, -0.3, u1 - u0, v1 - v0, h, color, "edif")
    E.caja(u0 - 0.8, v0 - 0.8, h - 0.1, u1 - u0 + 1.6, v1 - v0 + 1.6, 0.4, COL["losa"], "edif")           # losa que vuela
    for k in range(niveles):                                                                               # ventanal corrido en cada nivel, frente y fondo
        z = -0.3 + k * 3.6 + 0.8
        E.caja(u0 + 0.6, v0 - 0.08, z, u1 - u0 - 1.2, 0.1, 2.3, COL["vidrio"], "edif"); E.caja(u0 + 0.6, v1 - 0.02, z, u1 - u0 - 1.2, 0.1, 2.3, COL["vidrio"], "edif")
        for xx in range(int(u0 + 0.6), int(u1 - 0.6), 3): E.caja(xx, v0 - 0.1, z, 0.08, 0.14, 2.3, COL["marco"], "edif"); E.caja(xx, v1 - 0.04, z, 0.08, 0.14, 2.3, COL["marco"], "edif")
        E.caja(u0 + 0.6, v0 - 0.12, z + 2.3, u1 - u0 - 1.2, 0.2, 0.3, COL["losa"], "edif")                 # dintel / cortasol
    for xx in range(int(u0) + 2, int(u1) - 1, 6): E.caja(xx, v0 - 3.2, -0.3, 0.4, 0.4, h - 0.2, COL["losa"], "edif")   # columnas del pórtico del frente
    E.caja(u0, v0 - 3.4, h - 0.5, u1 - u0, 3.4, 0.3, COL["losa"], "edif")                                   # techo del pórtico
    E.suelo(u0 - 1, v0 - 4, u1 + 1, v0, -0.33, COL["andador"])
    E.caja(u0 + 2, v0 + 2, h - 0.1, 2.2, 1.0, 0.7, "#d8d8d8", "edif"); E.caja(u0 + 5, v0 + 2, h - 0.1, 2.2, 1.0, 0.7, "#d8d8d8", "edif")   # equipos en azotea
for f in capa("salon"):
    u0, u1, v0, v1 = caja_de(poly(f)); edificio(u0, u1, v0, v1, 2, "#e4d9c6")
    if "Gimnasio" in f["properties"]["nombre"]:
        for k in range(10): E.caja(u0 + 2 + k * 3, v1 + 0.05, 0.4, 1.0, 0.12, 6.4, COL["madera"], "edif")   # lamas de madera en el fondo del gimnasio
for f in capa("tenis"):
    pts = poly(f); u0, u1, v0, v1 = caja_de(pts); E.prisma(pts, -0.3, 0.05, COL["cancha"], "suelo", "suelo")
    for xx, yy, ww, dd in ((u0, v0, 0.06, v1 - v0), (u1 - 0.06, v0, 0.06, v1 - v0), (u0, v0, u1 - u0, 0.06), (u0, v1 - 0.06, u1 - u0, 0.06)): E.caja(xx, yy, -0.3, ww, dd, 4.0, "#3a3a3a90", "mob")
    E.caja(u0 + 1, (v0 + v1) / 2 - 0.05, -0.3, u1 - u0 - 2, 0.1, 0.9, "#2a2a2a", "mob")
    for yy in (v0 + 1.5, v1 - 1.5, (v0 + v1) / 2): E.caja(u0 + 1, yy, -0.25, u1 - u0 - 2, 0.05, 0.005, COL["cancha_l"], "suelo", "suelo")
for f in capa("padel"):
    pts = poly(f); u0, u1, v0, v1 = caja_de(pts); E.prisma(pts, -0.3, 0.05, "#2f7a5c", "suelo", "suelo")
    for xx, yy, ww, dd in ((u0, v0, 0.06, v1 - v0), (u1 - 0.06, v0, 0.06, v1 - v0), (u0, v0, u1 - u0, 0.06), (u0, v1 - 0.06, u1 - u0, 0.06)): E.caja(xx, yy, -0.3, ww, dd, 3.0, "#bcd9e866", "mob")
    E.caja(u0 + 0.5, (v0 + v1) / 2 - 0.04, -0.3, u1 - u0 - 1, 0.08, 0.9, "#2a2a2a", "mob")
for f in capa("comunal"):                                                                 # plaza del club: pérgolas, bancas, macetones
    u0, u1, v0, v1 = caja_de(poly(f)); cu = (u0 + u1) / 2
    E.suelo(u0 + 4, v1 - 30, u1 - 4, v1 - 22, -0.33, COL["andador"])
    for k in range(4): E.pergola(u0 + 8 + k * (u1 - u0 - 16) / 3, v1 - 29, 6, 4, 2.9)
    for k in range(6): E.banca(u0 + 6 + k * (u1 - u0 - 12) / 5, v1 - 23.5, 0.0); E.cil(u0 + 7 + k * (u1 - u0 - 12) / 5, v1 - 21.5, 0.5, -0.34, 0.6, "#b59a79", "mob", n=8); E.arbusto(u0 + 7 + k * (u1 - u0 - 12) / 5, v1 - 21.5, 0.4, 0.7)
    for k in range(5): E.arbolito(u0 + 10 + k * (u1 - u0 - 20) / 4, v1 - 16, 3.2)

# ---------- 7 · el acceso (pórtico, casetas, reja, muro de identidad, letrero, súper) ----------
A = Escena("acc"); A.rnd = r; A0, A1 = ACC.ANCHO; CV = ACC.CASETA_V
for n, a, b, t in ACC.CARRILES:
    if t == "isla":
        if "visitas" in n: A.caja(a + 0.2, CV - 3, -0.15, b - a - 0.4, 6, 3.4, "#55534f", "edif"); A.caja(a + 0.35, CV - 2.6, 0.9, b - a - 0.7, 5.2, 1.6, COL["vidrio"], "edif"); A.caja(a, CV - 3.4, 3.2, b - a, 6.8, 0.25, COL["losa"], "edif")
        else: A.caja(a + 0.5, CV - 1.5, -0.15, b - a - 1.0, 3, 3.2, "#55534f", "edif"); A.caja(a + 0.65, CV - 1.2, 0.9, b - a - 1.3, 2.4, 1.5, COL["vidrio"], "edif"); A.caja(a + 0.3, CV - 1.8, 3.0, b - a - 0.6, 3.6, 0.25, COL["losa"], "edif")
    elif t == "peaton": A.caja(a, 0, -0.4, b - a, CV + 30, 0.08, COL["banqueta"], "suelo", "suelo"); A.caja(a + 0.5, CV - 0.6, -0.32, b - a - 1.0, 1.2, 1.1, COL["acero"], "edif"); A.caja(a + 1.0, CV - 0.1, -0.32, 0.1, 0.1, 2.3, COL["poste"], "edif"); A.caja(a + 1.0, CV - 0.1, 2.2, b - a - 2.0, 0.1, 0.1, COL["poste"], "edif")
    else:
        A.caja(a + 0.2, CV - 0.1, 0.6, 0.1, 0.1, 0.5, COL["poste"], "edif"); A.caja(a + 0.2, CV - 0.05, 0.95, b - a - 0.6, 0.08, 0.08, "#f0f0f0", "edif"); A.caja(a + 0.25, CV - 0.08, 0.9, 0.3, 0.14, 0.2, "#c8102e", "edif")
        A.caja(a, 0, -0.47, b - a, CV + 40, 0.01, COL["asfalto"], "suelo", "suelo")
        for k in range(int((CV + 40) / 6)): A.caja(b - 0.08, k * 6, -0.46, 0.06, 3, 0.005, "#f0f0f0", "suelo", "suelo")
A.caja(A0 - 54, -0.35, 1.1, 13, 0.1, 1.2, "#2a2a2a", "edif"); A.caja(A0 - 53.6, -0.3, 1.25, 12.2, 0.02, 0.9, COL["luz"], "edif", "luz")     # letrero
for a, b in ((A0 - 40, A0), (A1, A1 + 40)):
    A.caja(a, -0.1, -0.32, b - a, 0.2, 0.9, "#e4d9c6", "edif"); A.caja(a, -0.05, 2.95, b - a, 0.1, 0.1, COL["poste"], "edif")
    x = a + 0.2
    while x < b: A.caja(x, -0.03, 0.58, 0.05, 0.06, 2.4, COL["poste"], "edif"); x += 0.36
    for xx in range(int(a), int(b), 8): A.caja(xx - 0.2, -0.2, -0.32, 0.4, 0.4, 3.1, "#55534f", "edif")
for xx in (A0 - 1.0, A1 + 0.2): A.caja(xx, ACP.PORTICO_V - 0.4, -0.32, 0.8, 0.8, ACP.PORTICO_H + 1.2, "#55534f", "edif")
A.caja(A0 - 1.0, ACP.PORTICO_V - 0.4, ACP.PORTICO_H, A1 - A0 + 2.0, 0.8, 0.9, "#55534f", "edif"); A.caja(A0 + 6, ACP.PORTICO_V - 0.46, ACP.PORTICO_H + 0.2, A1 - A0 - 12, 0.04, 0.5, COL["luz"], "edif", "luz")
A.caja(A0 + 8, ACP.PORTICO_V - 0.42, ACP.PORTICO_H + 0.25, 7.5, 0.02, 0.4, "#2a2a2a", "edif")                   # nombre sobre el pórtico
for xx in (A0 - 2.4, A1 + 1.6): A.caja(xx - 0.5, ACP.PORTICO_V - 0.9, -0.32, 1.0, 1.0, 0.6, "#b59a79", "edif"); A.arbusto(xx, ACP.PORTICO_V - 0.4, 0.45, 0.8)
VL = v_frente(U_ACC)
for p in A.P: E.P.append([[[x + U_ACC, y + VL] for x, y in p[0]], p[1], p[2], p[3], p[4], p[5]])
for f in capa("comercio"):
    pts = poly(f); u0, u1, v0, v1 = caja_de(pts); h = 5.0 if "súper" in f["properties"].get("nombre", "") else 4.5
    E.prisma(pts, -0.3, h, "#d6c6a4", "edif"); E.caja(u0 - 1, v0 - 1, h - 0.4, u1 - u0 + 2, v1 - v0 + 2, 0.5, COL["losa"], "edif")
    lado = v0 if v0 > V_LIM + 30 else v1
    E.caja(u0 + 0.8, (v0 - 0.08) if lado == v0 else (v1 - 0.02), 0.3, u1 - u0 - 1.6, 0.1, 3.0, COL["vidrio"], "edif")
    for xx in range(int(u0 + 0.8), int(u1 - 0.8), 3): E.caja(xx, (v0 - 0.1) if lado == v0 else v1 - 0.04, 0.3, 0.08, 0.14, 3.0, COL["marco"], "edif")
    E.caja(u0 + 1, (v0 - 0.2) if lado == v0 else v1 + 0.05, 3.5, u1 - u0 - 2, 0.15, 0.8, "#2a2a2a", "edif")      # rótulo
for f in capa("caseta"):
    pts = poly(f); u0, u1, v0, v1 = caja_de(pts)
    if v1 < V_LIM + 70: continue                                                      # las del acceso ya están en el bloque anterior
    E.prisma(pts, -0.3, 3.4, "#55534f", "edif"); E.caja(u0 + 0.2, v0 - 0.05, 0.9, u1 - u0 - 0.4, 0.08, 1.5, COL["vidrio"], "edif")

# ---------- 8 · barda perimetral con pilastras y cámaras; salida de emergencia ----------
for a, b in zip(lim[:-1], lim[1:]):
    L_ = math.dist(a, b)
    if L_ < 1: continue
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    en_frente = (a, b) == FRENTE_SEG or (b, a) == FRENTE_SEG          # el frente sur lleva muro de identidad; el resto, muro ciego
    if en_frente:
        for x0_, x1_ in ((_fa[0], U_ACC - 40), (U_ACC + 40, _fb[0])):
            if x1_ - x0_ < 2: continue
            L2 = (x1_ - x0_) / math.cos(ANG_FRENTE); y_ = v_frente(x0_)
            E.caja(x0_, y_ - 0.1, -0.32, L2, 0.2, 3.3, "#e4d9c6", "edif", rot=ANG_FRENTE, px=x0_, py=y_)
            for k in range(int(L2 / 6)): E.caja(x0_ + k * 6, y_ - 0.2, -0.32, 0.4, 0.4, 3.5, "#d9d5cd", "edif", rot=ANG_FRENTE, px=x0_, py=y_)
            E.caja(x0_, y_ - 0.15, 3.2, L2, 0.3, 0.12, "#55534f", "edif", rot=ANG_FRENTE, px=x0_, py=y_)
    else:
        E.caja(a[0], a[1] - 0.1, -0.36, L_, 0.2, 3.0, "#e4d9c6", "edif", rot=ang, px=a[0], py=a[1])
        for k in range(int(L_ / 6)): E.caja(a[0] + k * 6, a[1] - 0.18, -0.36, 0.36, 0.36, 3.15, "#d9d5cd", "edif", rot=ang, px=a[0], py=a[1])
        for k in range(6): E.caja(a[0], a[1] - 0.12, 3.05 + 0.1 * k, L_, 0.02, 0.02, "#555555", "edif", rot=ang, px=a[0], py=a[1])
for f in [f for f in SG["features"] if f["properties"].get("capa") == "camara_perim"]:
    u, v = uv(*f["geometry"]["coordinates"]); E.cil(u, v, 0.06, -0.32, 4.2, COL["poste"], "edif", n=6); E.caja(u - 0.12, v - 0.12, 3.9, 0.24, 0.24, 0.2, "#f0f0f0", "edif")

# ---------- 9 · servicios: planta de tratamiento, vaso, pozos, cisterna, acopio, transformadores, hidrantes ----------
for f in capa("ptar"): E.prisma(poly(f), -0.36, 0.05, "#9a9a9a", "suelo", "suelo")
for f in [f for f in SG["features"] if f["properties"].get("capa") == "ptar_planta"]:
    u0, u1, v0, v1 = caja_de(poly(f)); cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
    E.cil(cu - 9, cv, 5.0, -0.3, 3.2, "#8a8f94", "edif", n=24); E.cil(cu + 1, cv, 5.0, -0.3, 3.2, "#8a8f94", "edif", n=24); E.cil(cu + 10, cv, 3.0, -0.3, 2.6, "#7f8a91", "edif", n=20)
    E.caja(u0 + 1, v0 + 1, -0.3, 8, 5, 3.2, "#d2d2cf", "edif"); E.caja(u0 + 1, v0 + 1, 2.8, 8, 5, 0.3, COL["losa"], "edif")
    for xx in range(int(u0), int(u1), 3): E.caja(xx, v0 - 0.05, -0.32, 0.05, 0.05, 2.2, COL["poste"], "edif")
    E.caja(u0, v0 - 0.02, 1.9, u1 - u0, 0.02, 0.02, COL["poste"], "edif")
for f in [f for f in SG["features"] if f["properties"].get("capa") == "vaso"]: E.prisma(poly(f), -0.6, 0.1, "#9fb77a", "suelo", "suelo")
for f in [f for f in SG["features"] if f["properties"].get("capa") in ("agua_pozo", "agua_tanque", "acopio")]:
    pts = poly(f); u0, u1, v0, v1 = caja_de(pts); c = f["properties"]["capa"]
    E.prisma(pts, -0.34, 0.04, COL["cochera"], "suelo", "suelo")
    if c == "agua_pozo": E.caja(u0 + 2, v0 + 2, -0.3, 4, 4, 3.0, "#d2d2cf", "edif"); E.cil((u0 + u1) / 2 + 2, (v0 + v1) / 2, 0.4, -0.3, 1.2, "#8a8f94", "edif", n=10); E.caja(u0 + 2, v0 + 2, 2.7, 4, 4, 0.3, COL["losa"], "edif")
    elif c == "agua_tanque": E.caja(u0 + 1, v0 + 1, -0.3, u1 - u0 - 2, v1 - v0 - 2, 1.2, "#c9c5bc", "edif"); E.caja(u0 + 2, v0 + 2, 0.9, 6, 4, 3.0, "#d2d2cf", "edif"); E.caja(u0 + 2, v0 + 2, 3.7, 6, 4, 0.3, COL["losa"], "edif")
    else: E.caja(u0 + 0.5, v0 + 0.5, -0.3, u1 - u0 - 1, v1 - v0 - 1, 2.6, "#d9d5cd", "edif"); E.caja(u0 + 0.5, v0 + 0.5, 2.3, u1 - u0 - 1, v1 - v0 - 1, 0.3, COL["losa"], "edif")
    for xx in range(int(u0), int(u1), 3): E.caja(xx, v0 - 0.05, -0.32, 0.05, 0.05, 2.0, COL["poste"], "edif")
for f in [f for f in SG["features"] if f["properties"].get("capa") in ("trafo", "trafo_esp")]:
    u, v = uv(*f["geometry"]["coordinates"]); E.caja(u - 0.8, v - 0.6, -0.32, 1.6, 1.2, 1.2, "#5f7d5a", "edif"); E.caja(u - 0.9, v - 0.7, 0.85, 1.8, 1.4, 0.06, "#4e6a4a", "edif")
for f in [f for f in SG["features"] if f["properties"].get("capa") == "hidrante"]:
    u, v = uv(*f["geometry"]["coordinates"]); E.cil(u, v, 0.12, -0.32, 0.8, "#c8102e", "edif", n=8); E.cil(u, v, 0.17, 0.3, 0.12, "#c8102e", "edif", n=8)

# ---------- 10 · autos en las calles y gente en los parques ----------
for nombre, vc in V_CALLE.items():
    if nombre == "Nogal": continue
    us = [q[0] for f in capa("lote") if f["properties"]["dir"].rsplit(" ", 1)[0] == nombre for q in poly(f)]
    if not us: continue
    for k in range(int((max(us) - min(us)) / 60)):
        if r.random() < 0.5: E.auto(min(us) + 10 + k * 60 + r.random() * 30, vc - 2.6 + r.choice([0, 3.4]), 0.0 if r.random() < 0.5 else math.pi)
for f in capa("arroyo"):
    u0, u1, v0, v1 = caja_de(poly(f))
    for k in range(int((u1 - u0) / 50)):
        if r.random() < 0.6: E.auto(u0 + 10 + k * 50 + r.random() * 20, (v0 + v1) / 2 - 0.9, 0.0 if v0 < BUL_V else math.pi)

for nombre, vc in V_CALLE.items():
    if nombre == "Nogal": continue
    us = [q[0] for f in capa("lote") if f["properties"]["dir"].rsplit(" ", 1)[0] == nombre for q in poly(f)]
    if not us: continue
    for k in range(int((max(us) - min(us)) / 45)):
        px = min(us) + 8 + k * 45 + r.random() * 25; py = vc + r.choice([-4.6, 4.6]) + r.uniform(-0.3, 0.3)
        E.persona(px, py, r.choice([1.7, 1.75, 1.65]), rot=r.choice([0.0, math.pi]))
        if r.random() < 0.25: E.perro(px + 0.9, py + 0.3, rot=r.choice([0.0, math.pi]))
for f in capa("sendero"):
    u0, u1, v0, v1 = caja_de(poly(f)); vc = (v0 + v1) / 2
    for k in range(int((u1 - u0) / 30)):
        px = u0 + 5 + k * 30 + r.random() * 15; E.persona(px, vc + r.uniform(-0.6, 0.6), 1.7, rot=r.choice([0.0, math.pi]))
        if r.random() < 0.3: E.persona(px + 0.8, vc + 0.5, 1.1)
        if r.random() < 0.2: E.perro(px - 1.0, vc - 0.5, rot=0.0)
PI = next(iter(capa("pista")), None)
if PI:
    pp = poly(PI)
    for a, b in zip(pp[:-1], pp[1:]):
        L_ = math.dist(a, b)
        for k in range(int(L_ / 70)):
            t = (k + 0.5) * 70 / L_; E.persona(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 1.72, r.choice(["#e63946", "#f4f1de", "#2a9d8f", "#3d5a80"]), rot=math.atan2(b[1] - a[1], b[0] - a[0]))
for f in capa("comunal"):
    u0, u1, v0, v1 = caja_de(poly(f))
    for k in range(8): E.persona(u0 + 6 + r.random() * (u1 - u0 - 12), v1 - 29 + r.random() * 8, r.choice([1.7, 1.65, 1.75]))
    E.perro(u0 + 20, v1 - 25)

# ---------- cámaras y guardado ----------
PG = next(f for f in capa("parque") if "Garza" in f["properties"]["nombre"]); pu0, pu1, pv0, pv1 = caja_de(poly(PG)); pcu, pcv = (pu0 + pu1) / 2, (pv0 + pv1) / 2
pv_calle = max([vc for vc in V_CALLE.values() if vc < pv0] or [pv0 - 6])
casa_h = next(f for f in capa("lote") if f["properties"]["fachada"] == "Horizonte" and f["properties"]["frente"] == "calle" and abs(caja_de(poly(f))[2] - V_CALLE.get(f["properties"]["dir"].rsplit(" ", 1)[0], -999) - 6) < 2 and f["properties"]["ancho"] < 14)
hu0, hu1, hv0, hv1 = caja_de(poly(casa_h)); hvc = V_CALLE[casa_h["properties"]["dir"].rsplit(" ", 1)[0]]; hcu = (hu0 + hu1) / 2
VC = dict(
    entrada=ojo((U_ACC - 16, v_frente(U_ACC) - 34, 2.0), (U_ACC + 1, v_frente(U_ACC) + 30, 4.2), 56),
    entrada_frontal=ojo((U_ACC, v_frente(U_ACC) - 60, 2.0), (U_ACC, v_frente(U_ACC) + 30, 4), 44),
    entrada_alta=ojo((U_ACC - 60, v_frente(U_ACC) - 90, 30), (U_ACC, v_frente(U_ACC) + 40, 3), 55),
    casa=ojo((hcu + 13, hvc - 2.5, 1.6), (hcu - 0.5, hv0 + 4.5, 3.4), 40),
    casa_frente=ojo((hcu, hvc - 4.5, 1.7), (hcu, hv0 + 6, 3.4), 38),
    completo=cam(0.6, 0.58, -21, 1500, -40, -20, 0),
    completo_sur=ojo((U_ACC + 200, V_LIM - 700, 260), (0, 0, 0), 60),
    completo_bajo=ojo((umax + 500, vmin - 450, 120), (-100, 0, 0), 50),
    parque=ojo((pcu - 7, pv_calle - 2.0, 1.7), (pcu + 3, pcv + 12, 3.0), 60),
    parque_pergola=ojo((pcu + 16, pcv - 6, 1.6), (pcu - 2, pcv + 8, 2.2), 60),
    parque_alto=ojo((pcu - 70, pv0 - 60, 36), (pcu, pcv, 2), 55),
    club=ojo((-384, -205, 2.0), (-400, -160, 4), 60),
    bulevar=ojo((-500, 17, 1.7), (-380, 17, 3), 56),
)
ES.INDICE.append(guardar(E, dict(titulo="El fraccionamiento completo", porque="Todo el modelo con la geometría real: cada casa con su fachada, los nogales en su sitio, luminarias, parques, club, acceso y barda. Escena pesada: para el render fotorrealista.",
    hora="tarde", centro=[-40, -20, 0], dist=1500, suelo_z=-0.32, contornos=0.3, bruma=[900, 2400], cam=VC["completo"], vistas=VC)))
json.dump(ES.INDICE, open(os.path.join(ES.OUT, "index.json"), "w"), ensure_ascii=False, indent=1)
if __name__ == "__main__":
    print("completo:", len(E.P), "prismas,", n_lotes, "lotes,", round(os.path.getsize(os.path.join(ES.OUT, "completo.json")) / 1e6, 1), "MB")
