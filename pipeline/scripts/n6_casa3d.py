"""N6 · Modelo Nogal en 3D: convierte las plantas (n6_casa_planta) en prismas para el visor (public/casa/modelo3d.js).
Coordenadas en metros: x a lo ancho del lote (0 = lindero izquierdo visto desde la calle), y hacia el fondo (0 = banqueta), z hacia arriba (0 = piso de la casa).
Fachada: Horizonte (dos losas que vuelan 60 cm y una franja corrida de ventanas en la planta alta).
Cada pieza es un prisma: [puntos (x, y) en planta, z, alto, color, grupo, material]. El visor lo rasteriza con z-buffer, sombra y contornos."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n6_casa_planta as CP

W, PB_D, PA_D = CP.W, CP.PB_D, CP.PA_D
LOTE_W, LOTE_D, FRENTE = 12.7, 25.8, 5.5
HX, HY = (LOTE_W - 9.0) / 2, FRENTE                 # dónde queda la casa dentro del lote
NIVEL = 3.3                                           # piso a piso
G = 0.05                                              # rejilla para sacar los muros (5 cm)
C = dict(muro_ext="#e4d9c6", muro="#f6f3ed", losa="#55534f", banda="#34506cb8", marco="#33363a", vidrio="#9ec6dd8c", vidrio_claro="#bcd9e866",
         piso="#d4bd95", piso_h="#d2dadf", slab="#e4e2dd", azotea="#c6c2ba", madera="#8a5a2c", mueble="#ede5d7", tela="#6e8398", sanit="#ffffff", acero="#b3bac1",
         cubierta="#e6e6e4", closet="#a97a4e", tv="#1e1e1e", suelo="#86b35f", calle="#5a5a5a", banqueta="#c3bfb6", guarnicion="#a8a49c", cochera="#d0cdc5", patio="#dad7d0",
         tronco="#6a4b2d", copa="#5a9a4699", agua="#a9d9e9", jardinera="#b59a79", planta="#5c9a44", pretil="#d9d5cd", cojin="#f3ede2", pantalla="#2a3f55")
P = []                                                # prismas
def prisma(pts, z, h, color, grupo, mat=""):
    if h <= 0: return
    P.append([[[round(x, 3), round(y, 3)] for x, y in pts], round(z, 3), round(h, 3), color, grupo, mat])
def caja(x, y, z, w, d, h, color, grupo, mat=""):
    if w <= 0 or d <= 0 or h <= 0: return
    prisma([(x, y), (x + w, y), (x + w, y + d), (x, y + d)], z, h, color, grupo, mat)
def casa(x, y, z, w, d, h, color, grupo, mat=""): caja(HX + x, HY + y, z, w, d, h, color, grupo, mat)
def cilindro(cx, cy, r, z, h, color, grupo, n=10, mat=""):
    prisma([(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)], z, h, color, grupo, mat)

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
    def exterior(x0, y0, x1, y1): return x0 < 0.01 or y0 < 0.01 or x1 > W - 0.01 or y1 > D - 0.01
    for x0, y0, x1, y1 in rectangulos(1):
        casa(x0, y0, z0, x1 - x0, y1 - y0, 3.0, C["muro_ext"] if exterior(x0, y0, x1, y1) else C["muro"], grupo)
    for x0, y0, x1, y1 in rectangulos(2):                # ventana: antepecho, cristal con marco, cerramiento
        alta = (x1 - x0) < 1.0 and nivel == "PA" and 4.3 <= x0 <= 4.4   # ventana de la escalera, de piso a techo casi
        cancel = nivel == "PB" and y0 > PB_D - 0.3                      # cancel al portal
        ant, cab = (0.4, 2.9) if alta else (0.05, 2.7) if cancel else (0.9, 2.6)
        col = C["muro_ext"]
        casa(x0, y0, z0, x1 - x0, y1 - y0, ant, col, grupo)
        casa(x0, y0, z0 + cab, x1 - x0, y1 - y0, 3.0 - cab, col, grupo)
        en_x = (x1 - x0) > (y1 - y0)                                    # el muro corre en x (ventana vista desde el frente o el fondo)
        if en_x:
            ym = (y0 + y1) / 2
            casa(x0 + 0.05, ym - 0.01, z0 + ant + 0.05, x1 - x0 - 0.1, 0.02, cab - ant - 0.1, C["vidrio"], grupo)
            for xx in (x0, x1 - 0.05): casa(xx, y0 - 0.02, z0 + ant, 0.05, y1 - y0 + 0.04, cab - ant, C["marco"], grupo)
            for zz in (z0 + ant, z0 + cab - 0.05): casa(x0, y0 - 0.02, zz, x1 - x0, y1 - y0 + 0.04, 0.05, C["marco"], grupo)
        else:
            xm = (x0 + x1) / 2
            casa(xm - 0.01, y0 + 0.05, z0 + ant + 0.05, 0.02, y1 - y0 - 0.1, cab - ant - 0.1, C["vidrio"], grupo)
            for yy in (y0, y1 - 0.05): casa(x0 - 0.02, yy, z0 + ant, x1 - x0 + 0.04, 0.05, cab - ant, C["marco"], grupo)
            for zz in (z0 + ant, z0 + cab - 0.05): casa(x0 - 0.02, y0, zz, x1 - x0 + 0.04, y1 - y0, 0.05, C["marco"], grupo)
    for x, y, a, muro, bis, sent in CP.PUERTAS[nivel]:    # hojas y marcos de las puertas
        if muro == "x":
            casa(x, y - 0.02, z0, a, 0.04, 2.15, C["madera"], grupo)
            for xx in (x - 0.05, x + a): casa(xx, y - 0.12, z0, 0.05, 0.24, 2.2, C["marco"], grupo)
            casa(x - 0.05, y - 0.12, z0 + 2.15, a + 0.1, 0.24, 0.05, C["marco"], grupo)
        else:
            casa(x - 0.02, y, z0, 0.04, a, 2.15, C["madera"], grupo)
            for yy in (y - 0.05, y + a): casa(x - 0.12, yy, z0, 0.24, 0.05, 2.2, C["marco"], grupo)
            casa(x - 0.12, y - 0.05, z0 + 2.15, 0.24, a + 0.1, 0.05, C["marco"], grupo)
    # pisos por cuarto: losa clara con acabado encima (madera en cuartos, loseta en baños, cocina y lavandería)
    for c in rooms + [dict(r=r, tipo="circ") for r in CP.ABIERTO[nivel]]:
        x0, y0, x1, y1 = c["r"]
        if nivel == "PA" and (x0, y0, x1, y1) == (3.86, 1.34, 4.78, 4.80): continue      # hueco de la escalera
        humedo = c.get("tipo") in ("bano", "serv") or "Lavander" in c.get("n", "")
        casa(x0, y0, z0 - 0.3, x1 - x0, y1 - y0, 0.28, C["slab"], grupo)
        casa(x0, y0, z0 - 0.02, x1 - x0, y1 - y0, 0.02, C["piso_h"] if humedo else C["piso"], grupo)
    if techo_grupo == "techo":                            # azotea: losa, impermeabilizante y pretil
        casa(0, 0, z0 + 3.0, W, D, 0.3, C["azotea"], "techo")
        for x0, y0, w_, d_ in ((0, 0, W, 0.2), (0, D - 0.2, W, 0.2), (0, 0, 0.2, D), (W - 0.2, 0, 0.2, D)): casa(x0, y0, z0 + 3.3, w_, d_, 0.5, C["pretil"], "techo")

muros("PB", PB_D, 0.0, "pb", "pa")                     # el piso de la planta alta es el techo de la baja
muros("PA", PA_D, NIVEL, "pa", "techo")
casa(0, PB_D, NIVEL - 0.3, W, PA_D - PB_D, 0.3, C["slab"], "pa")   # losa de la planta alta sobre el portal

# ---------- escalera ----------
for k in range(17):
    y1 = CP.ESC_PIE - k * CP.HUELLA; z = (k + 1) * CP.PERALTE
    casa(3.86, y1 - CP.HUELLA, z - 0.18, 0.92, CP.HUELLA, 0.18, C["madera"] if k % 2 == 0 else "#95642f", "pb")
casa(4.78, 1.34, NIVEL, 0.02, 3.46, 1.0, C["vidrio_claro"], "pa")        # barandal de cristal del vacío
casa(4.76, 1.34, NIVEL + 0.98, 0.06, 3.46, 0.04, C["madera"], "pa")
casa(3.86, 4.80, NIVEL, 0.92, 0.02, 1.0, C["vidrio_claro"], "pa"); casa(3.86, 4.78, NIVEL + 0.98, 0.92, 0.06, 0.04, C["madera"], "pa")

# ---------- muebles ----------
ALTO = dict(closet=2.4, entrepanos=2.4, alacena=2.3, wc=0.42, lavabo=0.85, tarja=0.9, estufa=0.9, refri=1.8, lavadora=0.85, cubierta=0.9, tv=0.5, mesa=0.75)
ALTO_R = dict(buró=0.55, escritorio=0.75, centro=0.4, credenza=0.8, horno=2.1, lv=0.85, banca=0.45, tapa=0.1)
for nivel, z0 in (("PB", 0.0), ("PA", NIVEL)):
    for t, x0, y0, x1, y1, e in CP.MUEBLES[nivel]:
        g = "muebles"; w, d = x1 - x0, y1 - y0
        if t == "escalera": continue
        if t == "R":
            if e in ("buró", "credenza", "escritorio"):
                casa(x0, y0, z0, w, d, ALTO_R[e], C["madera"], g)
            elif e == "centro":
                casa(x0, y0, z0 + 0.36, w, d, 0.04, C["madera"], g)
                for xx, yy in ((x0 + 0.03, y0 + 0.03), (x1 - 0.07, y0 + 0.03), (x0 + 0.03, y1 - 0.07), (x1 - 0.07, y1 - 0.07)): casa(xx, yy, z0, 0.04, 0.04, 0.36, C["madera"], g)
            elif e == "banca": casa(x0, y0, z0, w, d, 0.45, C["tela"], g)
            elif e == "horno": casa(x0, y0, z0, w, d, 2.1, C["acero"], g)
            elif e == "lv": casa(x0, y0, z0, w, d, 0.85, C["acero"], g)
            else: casa(x0, y0, z0, w, d, ALTO_R.get(e, 0.5), C["mueble"], g)
        elif t == "cama":
            casa(x0, y0, z0, w, d, 0.25, C["madera"], g); casa(x0 + 0.03, y0 + 0.03, z0 + 0.25, w - 0.06, d - 0.06, 0.3, C["cojin"], g)
            lado = {"s": (x0, y1 - 0.08, w, 0.08), "n": (x0, y0, w, 0.08), "e": (x1 - 0.08, y0, 0.08, d), "w": (x0, y0, 0.08, d)}[e]
            casa(lado[0], lado[1], z0, lado[2], lado[3], 1.1, C["madera"], g)
            if e in ("s", "n"):
                yy = y1 - 0.08 - 0.45 if e == "s" else y0 + 0.08
                for xx in (x0 + 0.08, (x0 + x1) / 2 + 0.03): casa(xx, yy, z0 + 0.55, w / 2 - 0.11, 0.45, 0.12, C["sanit"], g)
            else:
                xx = x1 - 0.08 - 0.45 if e == "e" else x0 + 0.08
                for yy in (y0 + 0.08, (y0 + y1) / 2 + 0.03): casa(xx, yy, z0 + 0.55, 0.45, d / 2 - 0.11, 0.12, C["sanit"], g)
        elif t in ("closet", "entrepanos", "alacena"):
            casa(x0, y0, z0, w, d, ALTO[t], C["closet"], g)
        elif t == "regadera":
            casa(x0, y0, z0, w, d, 0.04, C["agua"], g)
            if w > d: casa(x0, y0 if y0 > 5.5 else y1 - 0.02, z0, w, 0.02, 2.0, C["vidrio_claro"], g)
            else: casa(x1 - 0.02 if x0 < 4 else x0, y0, z0, 0.02, d, 2.0, C["vidrio_claro"], g)
        elif t == "wc":
            casa(x0 + 0.05, y0, z0, w - 0.1, d, 0.42, C["sanit"], g)
            if e == "s": casa(x0, y1 - 0.18, z0, w, 0.18, 0.8, C["sanit"], g)
            else: casa(x0, y0, z0, w, 0.18, 0.8, C["sanit"], g)
        elif t == "lavabo":
            casa(x0, y0, z0, w, d, 0.82, C["madera"], g); casa(x0, y0, z0 + 0.82, w, d, 0.04, C["sanit"], g)
        elif t == "tv":
            casa(x0, y0, z0, w, d, 0.5, C["madera"], g)
            if w < d: casa(x0 + 0.02, y0 + 0.2, z0 + 0.65, 0.04, d - 0.4, 0.8, C["pantalla"], g)
            else: casa(x0 + 0.2, y0 + 0.02, z0 + 0.65, w - 0.4, 0.04, 0.8, C["pantalla"], g)
        elif t in ("sofa", "sillon"):
            casa(x0, y0, z0, w, d, 0.42, C["tela"], g)
            resp = {"e": (x1 - 0.2, y0, 0.2, d), "w": (x0, y0, 0.2, d), "n": (x0, y1 - 0.2, w, 0.2), "s": (x0, y0, w, 0.2)}[e]
            casa(resp[0], resp[1], z0, resp[2], resp[3], 0.85, C["tela"], g)
            if e in ("e", "w"):
                for yy in (y0, y1 - 0.2): casa(x0, yy, z0, w, 0.2, 0.6, C["tela"], g)
                casa(x0 + (0.0 if e == "e" else 0.2), y0 + 0.2, z0 + 0.42, w - 0.2, d - 0.4, 0.1, C["cojin"], g)
            else:
                for xx in (x0, x1 - 0.2): casa(xx, y0, z0, 0.2, d, 0.6, C["tela"], g)
                casa(x0 + 0.2, y0 + (0.0 if e == "n" else 0.2), z0 + 0.42, w - 0.4, d - 0.2, 0.1, C["cojin"], g)
        elif t == "mesa":
            casa(x0, y0, z0 + 0.72, w, d, 0.04, C["madera"], g)
            for xx, yy in ((x0 + 0.05, y0 + 0.05), (x1 - 0.1, y0 + 0.05), (x0 + 0.05, y1 - 0.1), (x1 - 0.1, y1 - 0.1)): casa(xx, yy, z0, 0.05, 0.05, 0.72, C["madera"], g)
            n = int(e) // 2 - 1
            def silla(sx, sy, lado):
                casa(sx, sy, z0 + 0.42, 0.44, 0.44, 0.04, C["madera"], g)
                for dx, dy in ((0.02, 0.02), (0.38, 0.02), (0.02, 0.38), (0.38, 0.38)): casa(sx + dx, sy + dy, z0, 0.04, 0.04, 0.42, C["madera"], g)
                if lado == "w": casa(sx, sy, z0 + 0.46, 0.04, 0.44, 0.44, C["madera"], g)
                elif lado == "e": casa(sx + 0.4, sy, z0 + 0.46, 0.04, 0.44, 0.44, C["madera"], g)
                elif lado == "s": casa(sx, sy, z0 + 0.46, 0.44, 0.04, 0.44, C["madera"], g)
                else: casa(sx, sy + 0.4, z0 + 0.46, 0.44, 0.04, 0.44, C["madera"], g)
            for k in range(n):
                yy = y0 + 0.25 + (d - 0.5) * (k + 0.5) / n
                silla(x0 - 0.5, yy - 0.22, "w"); silla(x1 + 0.06, yy - 0.22, "e")
            cx = (x0 + x1) / 2
            silla(cx - 0.22, y1 + 0.06, "n"); silla(cx - 0.22, y0 - 0.5, "s")
        elif t == "cubierta":
            casa(x0, y0, z0, w, d, 0.86, C["closet"], g); casa(x0 - 0.02, y0 - 0.02, z0 + 0.86, w + 0.04, d + 0.04, 0.04, C["cubierta"], g)
        elif t in ("tarja", "estufa"):
            casa(x0, y0, z0 + 0.9, w, d, 0.02, C["acero"], g)
        elif t == "refri": casa(x0, y0, z0, w, d, 1.8, C["acero"], g)
        elif t == "lavadora": casa(x0, y0, z0, w, d, 0.85, C["acero"], g)
        else:
            casa(x0, y0, z0, w, d, ALTO.get(t, 0.8), C["mueble"], g)

# ---------- fachada Horizonte ----------
casa(-0.6, -0.6, NIVEL - 0.1, W + 1.2, 0.6, 0.25, C["losa"], "fach")              # losa que vuela al frente, a media altura
casa(-0.6, -0.6, NIVEL - 0.1, 0.6, PA_D + 0.6, 0.25, C["losa"], "fach"); casa(W, -0.6, NIVEL - 0.1, 0.6, PA_D + 0.6, 0.25, C["losa"], "fach")
casa(-0.6, -0.6, 2 * NIVEL, W + 1.2, 0.6, 0.35, C["losa"], "techo")                # losa de remate
casa(-0.6, -0.6, 2 * NIVEL, 0.6, PA_D + 0.6, 0.35, C["losa"], "techo"); casa(W, -0.6, 2 * NIVEL, 0.6, PA_D + 0.6, 0.35, C["losa"], "techo")
casa(0.3, -0.04, NIVEL + 0.7, W - 0.6, 0.04, 2.25, C["banda"], "pa")              # franja corrida de la planta alta
casa(5.75, -0.6, -0.3, 3.6, 0.6, 0.9, C["jardinera"], "ext")                        # jardinera
for k in range(6): cilindro(HX + 6.2 + k * 0.55, HY - 0.3, 0.16, 0.6, 0.45, C["planta"], "ext", 6)
for x in (0.9, 8.1): casa(x - 0.15, PA_D - 0.3, 0, 0.3, 0.3, NIVEL - 0.3, C["muro_ext"], "pb")   # columnas del portal
casa(0, PB_D, -0.3, W, PA_D - PB_D, 0.3, C["patio"], "pb")                          # piso del portal
casa(1.0, PB_D + 0.6, 0, 1.6, 0.8, 0.75, C["madera"], "muebles")                    # mesa del portal
for xx, yy in ((0.6, PB_D + 0.75), (2.7, PB_D + 0.75), (1.1, PB_D + 1.5), (2.0, PB_D + 1.5)): casa(xx, yy, 0, 0.44, 0.44, 0.45, C["tela"], "muebles")
casa(6.5, PB_D + 0.4, 0, 1.5, 0.6, 0.9, C["acero"], "muebles")                      # asador

# ---------- el lote: pasto, banqueta, calle, cochera, patio y bodega ----------
caja(0, 0, -0.36, LOTE_W, LOTE_D, 0.04, C["suelo"], "ext", "suelo")                 # pasto
caja(-0.3, -2.2, -0.38, LOTE_W + 0.6, 2.2, 0.06, C["banqueta"], "ext", "suelo")     # banqueta
caja(-0.3, -2.35, -0.47, LOTE_W + 0.6, 0.15, 0.17, C["guarnicion"], "ext", "suelo") # guarnición
caja(-0.3, -5.5, -0.47, LOTE_W + 0.6, 3.15, 0.02, C["calle"], "ext", "suelo")       # calle
caja(LOTE_W - 0.3 - 5.85, -2.2, -0.34, 5.85, FRENTE + 1.9, 0.03, C["cochera"], "ext", "suelo")   # cochera (con la rampa de la banqueta)
caja(HX + W, HY, -0.34, LOTE_W - HX - W, 3.0, 0.03, C["patio"], "ext", "suelo")      # patio de servicio
caja(0.3, -2.2, -0.34, 1.2, FRENTE - 0.3 + 2.2, 0.03, C["patio"], "ext", "suelo")   # andador a la puerta
bx0, by0, bx1, by1 = CP.BODEGA_EXT
casa(bx0, by0, -0.3, bx1 - bx0, by1 - by0, 2.6, C["muro_ext"], "ext")
casa(bx0 - 0.05, by0 - 0.05, 2.3, bx1 - bx0 + 0.1, by1 - by0 + 0.1, 0.12, C["losa"], "ext")
for tx, ty in ((0, 0.8), (LOTE_W, 0.8), (0, 13.4), (LOTE_W, 13.4), (0, 25.8), (LOTE_W, 25.8)):           # nogales de los linderos
    cilindro(tx, ty, 0.22, -0.36, 4.3, C["tronco"], "arboles", 8)
    for r, z, h in ((2.7, 4.3, 1.9), (2.2, 6.2, 1.5), (1.3, 7.7, 1.1)): cilindro(tx, ty, r, z, h, C["copa"], "arboles", 10)

MODELO = dict(prismas=P, centro=[HX + W / 2, HY + PA_D / 2, 2.2], lote=[LOTE_W, LOTE_D], nombre="Modelo Nogal · fachada Horizonte")
if __name__ == "__main__":
    import json; print(len(P), "prismas"); json.dump(MODELO, open(sys.argv[1], "w"), separators=(",", ":"))
