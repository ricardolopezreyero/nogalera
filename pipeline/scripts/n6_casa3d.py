"""N6 · Modelo Nogal en 3D: convierte las plantas (n6_casa_planta) en cajas para el visor (public/casa/modelo3d.js).
Coordenadas en metros: x a lo ancho del lote (0 = lindero izquierdo visto desde la calle), y hacia el fondo (0 = banqueta), z hacia arriba (0 = piso de la casa).
Fachada: Horizonte (dos losas que vuelan 60 cm y una franja corrida de ventanas en la planta alta)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n6_casa_planta as CP

W, PB_D, PA_D = CP.W, CP.PB_D, CP.PA_D
LOTE_W, LOTE_D, FRENTE = 12.7, 25.8, 5.5
HX, HY = (LOTE_W - 9.0) / 2, FRENTE                 # dónde queda la casa dentro del lote
NIVEL = 3.3                                           # piso a piso
G = 0.05                                              # rejilla para sacar los muros (5 cm)
C = dict(muro="#fafafa", piso="#efefef", techo="#e2e2e2", vidrio="#3a3a3a", madera="#9a9a9a", mueble="#e6e6e6", closet="#cfcfcf", losa="#2a2a2a",
         suelo="#ededed", calle="#cfcfcf", cochera="#e0e0e0", verde="#d9d9d9", tronco="#444444", copa="rgba(200,200,200,0.28)", banda="#2b2b2b", agua="#bdbdbd")
B = []                                                # cajas: [x, y, z, w, d, h, color, grupo]
SIN_BORDE = {"piso", "techo", "suelo", "calle", "cochera", "copa"}
def caja(x, y, z, w, d, h, color, grupo, borde=None):
    if w <= 0 or d <= 0 or h <= 0: return
    sb = 1 if (borde is False or (borde is None and color in (C[k] for k in SIN_BORDE))) else 0
    B.append([round(x, 3), round(y, 3), round(z, 3), round(w, 3), round(d, 3), round(h, 3), color, grupo, sb])
def casa(x, y, z, w, d, h, color, grupo): caja(HX + x, HY + y, z, w, d, h, color, grupo)

# ---------- muros por rejilla ----------
def muros(nivel, D, z0, grupo, techo_grupo):
    rooms = CP.PB if nivel == "PB" else CP.PA
    nx, ny = round(W / G), round(D / G)
    cel = [[1] * ny for _ in range(nx)]                 # 1 = muro, 0 = espacio, 2 = ventana
    def marca(x0, y0, x1, y1, val=0):
        for i in range(max(0, round(x0 / G)), min(nx, round(x1 / G))):
            for j in range(max(0, round(y0 / G)), min(ny, round(y1 / G))): cel[i][j] = val
    for c in rooms: marca(*c["r"])
    for r in CP.ABIERTO[nivel] + CP.APERTURAS[nivel]: marca(*r)
    for x, y, a, muro, bis, sent in CP.PUERTAS[nivel]:
        if muro == "x": marca(x, y - 0.11, x + a, y + 0.11)
        else: marca(x - 0.11, y, x + 0.11, y + a)
    for a, b, muro, pos in CP.VENTANAS[nivel]:
        if muro == "x": marca(a, (pos - 0.2 if pos > 0 else 0), b, (pos if pos > 0 else 0.2), 2)
        else: marca((pos - 0.2 if pos > 0 else 0), a, (pos if pos > 0 else 0.2), b, 2)
    def rectangulos(val):
        visto = [[False] * ny for _ in range(nx)]; out = []
        for i in range(nx):
            for j in range(ny):
                if cel[i][j] != val or visto[i][j]: continue
                i2 = i
                while i2 + 1 < nx and cel[i2 + 1][j] == val and not visto[i2 + 1][j]: i2 += 1
                j2 = j
                while j2 + 1 < ny and all(cel[k][j2 + 1] == val and not visto[k][j2 + 1] for k in range(i, i2 + 1)): j2 += 1
                for k in range(i, i2 + 1):
                    for l in range(j, j2 + 1): visto[k][l] = True
                out.append((i * G, j * G, (i2 + 1) * G, (j2 + 1) * G))
        return out
    for x0, y0, x1, y1 in rectangulos(1):
        casa(x0, y0, z0, x1 - x0, y1 - y0, 3.0, C["muro"], grupo)
    for x0, y0, x1, y1 in rectangulos(2):                # ventana: antepecho, cristal y cerramiento
        alta = (x1 - x0) < 1.0 and nivel == "PA" and 4.3 <= x0 <= 4.4   # ventana de la escalera, de piso a techo casi
        cancel = nivel == "PB" and y0 > PB_D - 0.3                      # cancel al portal
        ant, cab = (0.4, 2.9) if alta else (0.05, 2.7) if cancel else (0.9, 2.6)
        casa(x0, y0, z0, x1 - x0, y1 - y0, ant, C["muro"], grupo)
        casa(x0, y0, z0 + ant, x1 - x0, y1 - y0, cab - ant, C["vidrio"], grupo)
        casa(x0, y0, z0 + cab, x1 - x0, y1 - y0, 3.0 - cab, C["muro"], grupo)
    for x, y, a, muro, bis, sent in CP.PUERTAS[nivel]:    # hojas de las puertas
        if muro == "x": casa(x, y - 0.025, z0, a, 0.05, 2.2, C["madera"], grupo)
        else: casa(x - 0.025, y, z0, 0.05, a, 2.2, C["madera"], grupo)
    # pisos y techos por cuarto (piezas chicas para que el dibujo las ordene bien)
    for c in rooms + [dict(r=r) for r in CP.ABIERTO[nivel]]:
        x0, y0, x1, y1 = c["r"]
        if nivel == "PA" and (x0, y0, x1, y1) == (3.86, 1.34, 4.78, 4.80): continue      # hueco de la escalera
        casa(x0, y0, z0 - 0.3, x1 - x0, y1 - y0, 0.3, C["piso"], grupo)
        casa(x0, y0, z0 + 3.0, x1 - x0, y1 - y0, 0.3, C["techo"], techo_grupo)

muros("PB", PB_D, 0.0, "pb", "pa")                     # el techo de la planta baja es el piso de la alta
muros("PA", PA_D, NIVEL, "pa", "techo")
casa(0, PB_D, NIVEL - 0.3, W, PA_D - PB_D, 0.3, C["techo"], "pa")   # losa de la planta alta sobre el portal

# ---------- escalera ----------
for k in range(17):
    y1 = CP.ESC_PIE - k * CP.HUELLA; z = (k + 1) * CP.PERALTE
    casa(3.86, y1 - CP.HUELLA, z - 0.16, 0.92, CP.HUELLA, 0.16, C["mueble"], "pb")
casa(4.78, 1.34, NIVEL, 0.04, 3.46, 1.0, C["madera"], "pa")        # barandal del vacío
casa(3.86, 4.80, NIVEL, 0.92, 0.04, 1.0, C["madera"], "pa")

# ---------- muebles ----------
ALTO = dict(cama=0.55, closet=2.4, entrepanos=2.4, alacena=2.3, regadera=0.06, wc=0.42, lavabo=0.85, tarja=0.9, estufa=0.9, refri=1.8, lavadora=0.85, cubierta=0.9, tv=0.5, sofa=0.45, sillon=0.45, mesa=0.75)
ALTO_R = dict(buró=0.55, escritorio=0.75, centro=0.4, credenza=0.8, horno=2.1, lv=0.85, banca=0.45, tapa=0.1)
for nivel, z0 in (("PB", 0.0), ("PA", NIVEL)):
    for t, x0, y0, x1, y1, e in CP.MUEBLES[nivel]:
        g = "muebles"; w, d = x1 - x0, y1 - y0
        if t == "escalera": continue
        if t == "R":
            casa(x0, y0, z0, w, d, ALTO_R.get(e, 0.5), C["mueble"], g)
        elif t == "cama":
            casa(x0, y0, z0, w, d, 0.55, C["mueble"], g)
            if e == "s": casa(x0, y1 - 0.08, z0, w, 0.08, 1.1, C["madera"], g)
            elif e == "n": casa(x0, y0, z0, w, 0.08, 1.1, C["madera"], g)
            elif e == "e": casa(x1 - 0.08, y0, z0, 0.08, d, 1.1, C["madera"], g)
            else: casa(x0, y0, z0, 0.08, d, 1.1, C["madera"], g)
        elif t in ("closet", "entrepanos", "alacena"):
            casa(x0, y0, z0, w, d, ALTO[t], C["closet"], g)
        elif t == "regadera":
            casa(x0, y0, z0, w, d, 0.06, C["agua"], g)
            if w > d: casa(x0, y0 if y0 > 5.5 else y1 - 0.02, z0, w, 0.02, 2.0, C["vidrio"], g)
            else: casa(x1 - 0.02 if x0 < 4 else x0, y0, z0, 0.02, d, 2.0, C["vidrio"], g)
        elif t == "wc":
            casa(x0, y0, z0, w, d, 0.42, C["mueble"], g)
            if e == "s": casa(x0, y1 - 0.18, z0, w, 0.18, 0.8, C["mueble"], g)
            else: casa(x0, y0, z0, w, 0.18, 0.8, C["mueble"], g)
        elif t == "tv":
            casa(x0, y0, z0, w, d, 0.5, C["mueble"], g); casa(x0 + 0.02, y0 + 0.2, z0 + 0.6, 0.04, d - 0.4, 0.85, C["vidrio"], g)
        elif t in ("sofa", "sillon"):
            casa(x0, y0, z0, w, d, 0.45, C["mueble"], g)
            if e == "e": casa(x1 - 0.2, y0, z0, 0.2, d, 0.85, C["mueble"], g)
            elif e == "w": casa(x0, y0, z0, 0.2, d, 0.85, C["mueble"], g)
            elif e == "n": casa(x0, y1 - 0.2, z0, w, 0.2, 0.85, C["mueble"], g)
            else: casa(x0, y0, z0, w, 0.2, 0.85, C["mueble"], g)
        elif t == "mesa":
            casa(x0, y0, z0 + 0.72, w, d, 0.04, C["madera"], g)
            for xx, yy in ((x0 + 0.05, y0 + 0.05), (x1 - 0.1, y0 + 0.05), (x0 + 0.05, y1 - 0.1), (x1 - 0.1, y1 - 0.1)): casa(xx, yy, z0, 0.05, 0.05, 0.72, C["madera"], g)
            n = int(e) // 2 - 1
            for k in range(n):
                yy = y0 + 0.25 + (d - 0.5) * (k + 0.5) / n
                for sx in (x0 - 0.5, x1 + 0.06):
                    casa(sx, yy - 0.22, z0, 0.44, 0.44, 0.45, C["mueble"], g); casa(sx if sx < x0 else sx + 0.4, yy - 0.22, z0, 0.04, 0.44, 0.9, C["madera"], g)
            cx = (x0 + x1) / 2
            for sy in (y1 + 0.06, y0 - 0.5):
                casa(cx - 0.22, sy, z0, 0.44, 0.44, 0.45, C["mueble"], g); casa(cx - 0.22, sy + 0.4 if sy > y1 else sy, z0, 0.44, 0.04, 0.9, C["madera"], g)
        else:
            casa(x0, y0, z0, w, d, ALTO.get(t, 0.8), C["mueble"] if t not in ("tarja", "cubierta", "estufa") else C["closet"], g)

# ---------- fachada Horizonte ----------
casa(-0.6, -0.6, NIVEL - 0.1, W + 1.2, 0.6, 0.25, C["losa"], "fach")              # losa que vuela al frente, a media altura
casa(-0.6, -0.6, NIVEL - 0.1, 0.6, PA_D + 0.6, 0.25, C["losa"], "fach"); casa(W, -0.6, NIVEL - 0.1, 0.6, PA_D + 0.6, 0.25, C["losa"], "fach")
casa(-0.6, -0.6, 2 * NIVEL, W + 1.2, 0.6, 0.35, C["losa"], "techo")                # losa de remate
casa(-0.6, -0.6, 2 * NIVEL, 0.6, PA_D + 0.6, 0.35, C["losa"], "techo"); casa(W, -0.6, 2 * NIVEL, 0.6, PA_D + 0.6, 0.35, C["losa"], "techo")
casa(0.3, -0.04, NIVEL + 0.7, W - 0.6, 0.04, 2.25, C["banda"], "pa")              # franja corrida de la planta alta
casa(5.75, -0.6, -0.3, 3.6, 0.6, 0.9, C["closet"], "ext")                           # jardinera
for k in range(6): casa(6.0 + k * 0.55, -0.45, 0.6, 0.3, 0.3, 0.5, C["verde"], "ext")
for x in (0.9, 8.1): casa(x - 0.15, PA_D - 0.3, 0, 0.3, 0.3, NIVEL - 0.3, C["muro"], "pb")   # columnas del portal
casa(0, PB_D, -0.3, W, PA_D - PB_D, 0.3, C["piso"], "pb")                           # piso del portal

# ---------- el lote ----------
for i in range(9):
    for j in range(18):
        caja(i * LOTE_W / 9, j * LOTE_D / 18, -0.35, LOTE_W / 9, LOTE_D / 18, 0.05, C["suelo"], "ext")
for i in range(9): caja(i * LOTE_W / 9, -3.0, -0.35, LOTE_W / 9, 3.0, 0.05, C["calle"], "ext")
caja(LOTE_W - 0.3 - 5.85, 0.3, -0.31, 5.85, FRENTE - 0.3, 0.03, C["cochera"], "ext")
caja(HX + W, HY, -0.31, LOTE_W - HX - W, 3.0, 0.03, C["cochera"], "ext")              # patio de servicio
bx0, by0, bx1, by1 = CP.BODEGA_EXT
casa(bx0, by0, -0.3, bx1 - bx0, by1 - by0, 2.6, C["muro"], "ext")
for tx, ty in ((0, 0.8), (LOTE_W, 0.8), (0, 13.4), (LOTE_W, 13.4), (0, 25.8), (LOTE_W, 25.8)):           # nogales de los linderos
    caja(tx - 0.2, ty - 0.2, -0.3, 0.4, 0.4, 4.0, C["tronco"], "arboles")
    caja(tx - 3.0, ty - 3.0, 3.7, 6.0, 6.0, 3.6, C["copa"], "arboles")

def partir(b, maxl=2.0):
    """Parte las cajas largas en piezas de ≤ 2 m para que el orden de dibujo salga bien."""
    x, y, z, w, d, h, c, g, sb = b
    if g == "arboles": yield b; return
    nx = max(1, int(w / maxl + 0.999)); nyy = max(1, int(d / maxl + 0.999))
    for i in range(nx):
        for j in range(nyy):
            yield [round(x + w * i / nx, 3), round(y + d * j / nyy, 3), z, round(w / nx, 3), round(d / nyy, 3), h, c, g, sb]
CAJAS = [p for b in B for p in partir(b)]
MODELO = dict(cajas=CAJAS, centro=[HX + W / 2, HY + PA_D / 2, 2.5], lote=[LOTE_W, LOTE_D], nombre="Modelo Nogal · fachada Horizonte")
if __name__ == "__main__":
    import json; print(len(B), "cajas,", len(CAJAS), "piezas"); json.dump(MODELO, open(sys.argv[1], "w"), separators=(",", ":"))
