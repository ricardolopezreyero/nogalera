"""N6 · escenas para el creador de renders (public/render/render3d.js): calles, casas con sus nueve fachadas, acceso, bulevar, parque,
pista, club, interiores y la vista aérea de todo el fraccionamiento. Escribe public/datos/escenas/<id>.json y el índice.
Prisma: [puntos (x, y), z, alto, color "#rrggbb[aa]", grupo, material]. Metros; z = 0 es el piso de las casas; el suelo está en -0.32."""
import os, sys, json, math, random
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import n6_casa3d as C3D, n6_casa_planta as CP
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..")); DAT = os.path.join(RAIZ, "public", "datos"); OUT = os.path.join(DAT, "escenas")
os.makedirs(OUT, exist_ok=True)

COL = dict(pasto="#86b35f", pasto2="#7aa855", asfalto="#5c5c5c", banqueta="#c6c2b9", guarnicion="#a9a59d", cochera="#d0cdc5", andador="#dad7d0", tierra="#c9b89a",
           grava="#b9b3a8", vidrio="#9ec6dd8c", vidrio_osc="#4e6f8ac0", ventana_noche="#ffd58e", madera="#8a5a2c", marco="#33363a", losa="#55534f", azotea="#c6c2ba", pretil="#d9d5cd",
           tronco="#6a4b2d", copa=["#4f8f3c", "#5a9a44", "#467f36", "#5f9e4b"], poste="#3a3a3a", luz="#fff1cc", acero="#b3bac1", piel="#d9b08c", ropa=["#3d5a80", "#9b2226", "#2a9d8f", "#e9c46a", "#f4f1de", "#6d597a"],
           auto=["#2b2b2b", "#d8d8d8", "#8c1c13", "#1f3a5f", "#b7b7b7", "#f2f2f2"], agua="#7fb6d6", arena="#e2d3b3", cancha="#b94a3c", cancha_l="#f1f1f1", bordo="#9a8c6c")
FACH = {  # cuerpo PB, cuerpo PA
    "Horizonte": ("#e4d9c6", "#e4d9c6"), "Ladrillo": ("#d8cfc2", "#b3563f"), "Duela": ("#ece6da", "#ece6da"), "Cantera": ("#d6c6a4", "#d6c6a4"), "Hacienda": ("#f5f1e8", "#f5f1e8"),
    "Marco": ("#d2d2cf", "#d2d2cf"), "Lamas": ("#e9e2d4", "#e9e2d4"), "Concreto": ("#a9a9a4", "#a9a9a4"), "Celosía": ("#e3d4c0", "#e3d4c0")}
SEQ = ["Cantera", "Ladrillo", "Lamas", "Marco", "Hacienda", "Concreto", "Celosía", "Duela", "Horizonte"]
W, PB_D, PA_D, FRENTE, LOTE_W, LOTE_D = 9.0, 12.0, 15.0, 5.5, 12.7, 25.8

class Escena:
    def __init__(self, nombre): self.P = []; self.luces = []; self.nombre = nombre; self.rnd = random.Random(hash(nombre) & 0xffff)
    def prisma(self, pts, z, h, color, grupo="", mat=""):
        if h <= 0: return
        self.P.append([[[round(x, 3), round(y, 3)] for x, y in pts], round(z, 3), round(h, 3), color, grupo, mat])
    def caja(self, x, y, z, w, d, h, color, grupo="", mat="", rot=0.0, px=None, py=None):
        pts = [(x, y), (x + w, y), (x + w, y + d), (x, y + d)]
        if rot: pts = girar(pts, rot, x if px is None else px, y if py is None else py)
        self.prisma(pts, z, h, color, grupo, mat)
    def cil(self, cx, cy, r, z, h, color, grupo="", mat="", n=10, fase=0.0):
        self.prisma([(cx + r * math.cos(2 * math.pi * k / n + fase), cy + r * math.sin(2 * math.pi * k / n + fase)) for k in range(n)], z, h, color, grupo, mat)
    def luz(self, x, y, z, r=2.0, color="#ffd9a0"): self.luces.append([round(x, 2), round(y, 2), round(z, 2), r, color])
    # ---- elementos ----
    def suelo(self, x0, y0, x1, y1, z, color, grupo="suelo"): self.caja(x0, y0, z - 0.04, x1 - x0, y1 - y0, 0.04, color, grupo, "suelo")
    def nogal(self, x, y, esc=1.0, iluminado=False, alza=0.0):
        """Nogal adulto: tronco de 0.6 m que se abre en 3 ramas a los 2.5 m y copa irregular de 7 lóbulos (10 a 12 m de alto)."""
        r = self.rnd; k = (r.random() * 0.25 + 0.88) * esc; fase = r.random() * 6.28
        self.cil(x, y, 0.32 * k, -0.36, 2.7 * k + alza, COL["tronco"], "arboles", n=8, fase=fase)
        self.cil(x, y, 0.42 * k, -0.36, 0.5, "#5a3f26", "arboles", n=8, fase=fase)
        ramas = []
        for j in range(3):
            a = fase + j * 2.1 + r.random() * 0.5; d = 0.45 * k
            bx, by = x + d * math.cos(a), y + d * math.sin(a); ramas.append((bx, by, a))
            self.cil(bx, by, 0.17 * k, 2.3 * k + alza, (2.0 + r.random() * 0.8) * k, "#6f5033", "arboles", n=6)
        cols = COL["copa"]
        for j in range(7):
            a = fase + j * 0.9 + r.random() * 0.6; d = (0.4 + r.random() * 2.2) * k
            rr = (2.0 + r.random() * 1.5) * k; z = (3.6 + r.random() * 3.6) * k + alza; h = (2.2 + r.random() * 1.4) * k
            self.cil(x + d * math.cos(a), y + d * math.sin(a), rr, z, h, cols[(j + int(fase * 3)) % len(cols)] + "fa", "arboles", n=9, fase=r.random())
        self.cil(x + r.uniform(-0.6, 0.6) * k, y + r.uniform(-0.6, 0.6) * k, 1.7 * k, 8.4 * k + alza, 2.0 * k, cols[int(fase * 5) % len(cols)] + "fa", "arboles", n=8, fase=r.random())
        if iluminado: self.luz(x, y, 1.2, 1.6 * esc, "#ffe9b0")
    def nogal_simple(self, x, y, h=10.0):
        k = max(0.5, min(1.2, h / 11)); r = self.rnd; col = r.choice(COL["copa"]); col2 = r.choice(COL["copa"]); a = r.random() * 6.28
        self.cil(x, y, 0.3, -0.36, 4.0 * k, COL["tronco"], "arboles", n=6)
        self.cil(x + 0.9 * k * math.cos(a), y + 0.9 * k * math.sin(a), 3.9 * k, 3.6 * k, 4.2 * k, col, "arboles", n=8, fase=a)
        self.cil(x - 0.8 * k * math.cos(a), y - 0.8 * k * math.sin(a), 3.0 * k, 6.2 * k, 3.4 * k, col2, "arboles", n=7, fase=a + 1)
    def arbotante(self, x, y, h=6.0, brazo=1.3, lado=1, doble=False, noche=False):
        self.cil(x, y, 0.08, -0.32, h, COL["poste"], "luz", n=6)
        for s in ((1, -1) if doble else (lado,)):
            self.caja(min(x, x + s * brazo), y - 0.05, h - 0.1, brazo, 0.1, 0.1, COL["poste"], "luz")
            self.caja(x + s * brazo - 0.3 if s > 0 else x - brazo - 0.0, y - 0.15, h - 0.25, 0.6, 0.3, 0.15, COL["luz"] if noche else "#e6e6e6", "luz", "luz" if noche else "")
            if noche: self.luz(x + s * brazo, y, h - 0.3, 2.6)
    def auto(self, x, y, rot=0.0, color=None):
        c = color or self.rnd.choice(COL["auto"])
        self.caja(x, y, -0.32 + 0.3, 4.5, 1.85, 0.65, c, "autos", rot=rot, px=x, py=y)
        self.caja(x + 1.2, y + 0.12, -0.32 + 0.95, 2.3, 1.6, 0.62, COL["vidrio_osc"], "autos", rot=rot, px=x, py=y)
        for dx in (0.75, 3.6):
            for dy in (0.0, 1.7): self.caja(x + dx - 0.33, y + dy - 0.08, -0.32, 0.66, 0.16, 0.6, "#222222", "autos", rot=rot, px=x, py=y)
    def auto_luces(self, x, y, rot=0.0):
        for dy in (0.3, 1.55):
            px, py = girar([(x + 4.5, y + dy)], rot, x, y)[0]; self.luz(px, py, 0.4, 1.2, "#fff4d6")
    def persona(self, x, y, h=1.7, color=None):
        c = color or self.rnd.choice(COL["ropa"])
        self.cil(x, y, 0.16, -0.32, 0.8 * h / 1.7, "#2f2f2f", "gente", n=6); self.cil(x, y, 0.2, -0.32 + 0.8 * h / 1.7, 0.65 * h / 1.7, c, "gente", n=6)
        self.cil(x, y, 0.11, -0.32 + 1.45 * h / 1.7, 0.25 * h / 1.7, COL["piel"], "gente", n=6)
    def arbusto(self, x, y, r=0.5, h=0.7, color=None):
        self.cil(x, y, r, -0.34, h, color or self.rnd.choice(["#6f9a4a", "#5f8c42", "#8aa85e", "#4f7d3a"]), "plantas", n=7, fase=self.rnd.random())
    def arbolito(self, x, y, h=3.2):
        c = self.rnd.choice(["#7fae5a", "#9bbf6a", "#6a9c4e"]); f = self.rnd.random()
        self.cil(x, y, 0.08, -0.34, h * 0.45, "#7a5a3a", "plantas", n=5); self.cil(x, y, h * 0.30, h * 0.4, h * 0.4, c, "plantas", n=10, fase=f); self.cil(x, y, h * 0.2, h * 0.75, h * 0.28, c, "plantas", n=10, fase=f)
    def farol(self, x, y, h=3.5, noche=False):
        self.cil(x, y, 0.05, -0.34, h, COL["poste"], "luz", n=5); self.caja(x - 0.14, y - 0.14, h - 0.05, 0.28, 0.28, 0.3, COL["luz"] if noche else "#eaeaea", "luz", "luz" if noche else "")
        if noche: self.luz(x, y, h + 0.1, 1.8)
    def pergola(self, x, y, w, d, h=2.8, rot=0.0):
        for dx, dy in ((0.1, 0.1), (w - 0.3, 0.1), (0.1, d - 0.3), (w - 0.3, d - 0.3)): self.caja(x + dx, y + dy, -0.34, 0.2, 0.2, h, "#5a4632", "mob", rot=rot, px=x, py=y)
        self.caja(x, y, h - 0.34, w, 0.2, 0.25, "#5a4632", "mob", rot=rot, px=x, py=y); self.caja(x, y + d - 0.2, h - 0.34, w, 0.2, 0.25, "#5a4632", "mob", rot=rot, px=x, py=y)
        k = 0.0
        while k < w: self.caja(x + k, y, h - 0.1, 0.12, d, 0.14, "#5a4632", "mob", rot=rot, px=x, py=y); k += 0.5
    def banca(self, x, y, rot=0.0):
        self.caja(x, y, -0.32 + 0.4, 1.8, 0.45, 0.05, COL["madera"], "mob", rot=rot, px=x, py=y); self.caja(x, y + 0.4, -0.32 + 0.45, 1.8, 0.05, 0.45, COL["madera"], "mob", rot=rot, px=x, py=y)
        for dx in (0.1, 1.6): self.caja(x + dx, y + 0.05, -0.32, 0.08, 0.35, 0.4, COL["poste"], "mob", rot=rot, px=x, py=y)
    # ---- la casa con su fachada (coordenadas locales: x 0..9 a lo ancho, y 0 al frente hacia atrás, z 0 piso) ----
    def casa(self, fachada, x0, y0, rot=0.0, noche=False, detalle=True):
        E = Escena("tmp"); E.rnd = self.rnd; pb, pa = FACH.get(fachada, FACH["Concreto"])
        vent = COL["ventana_noche"] if noche else COL["vidrio"]; mat_v = "luz" if noche else ""
        E.caja(0, 0, -0.3, W, PB_D, 3.6, pb, "casa"); E.caja(0, 0, 3.3, W, PA_D, 3.3, pa, "casa")
        E.caja(-0.1, -0.1, 6.6, W + 0.2, PA_D + 0.2, 0.3, COL["azotea"], "casa")
        for xx, yy, ww, dd in ((-0.1, -0.1, W + 0.2, 0.2), (-0.1, PA_D - 0.1, W + 0.2, 0.2), (-0.1, -0.1, 0.2, PA_D + 0.2), (W - 0.1, -0.1, 0.2, PA_D + 0.2)): E.caja(xx, yy, 6.9, ww, dd, 0.45, COL["pretil"], "casa")
        E.caja(0, PB_D, 2.95, W, PA_D - PB_D, 0.35, COL["losa"], "casa")                                    # losa sobre el portal
        for xx in (0.75, 8.25): E.caja(xx - 0.15, PA_D - 0.3, 0, 0.3, 0.3, 2.95, pb, "casa")                 # columnas del portal
        E.caja(0, PB_D, -0.3, W, PA_D - PB_D, 0.3, COL["andador"], "casa")                                      # piso del portal
        def ventana(a, b, z0, z1, y=-0.02, marco=COL["marco"]):
            E.caja(a, y, z0, b - a, 0.06, z1 - z0, vent, "casa", mat_v)
            if detalle:
                for xx in (a - 0.06, b): E.caja(xx, y - 0.03, z0 - 0.06, 0.06, 0.1, z1 - z0 + 0.12, marco, "casa")
                for zz in (z0 - 0.06, z1): E.caja(a - 0.06, y - 0.03, zz, b - a + 0.12, 0.1, 0.06, marco, "casa")
        def puerta(a=4.25, b=5.35, color=COL["madera"]):
            E.caja(a, -0.03, 0, b - a, 0.06, 2.2, color, "casa")
            if noche: E.luz(4.8, -0.6, 2.4, 1.4)
        if fachada == "Horizonte":
            E.caja(-0.6, -0.6, 3.2, W + 1.2, 0.6, 0.25, COL["losa"], "casa"); E.caja(-0.6, -0.6, 3.2, 0.6, PA_D + 0.6, 0.25, COL["losa"], "casa"); E.caja(W, -0.6, 3.2, 0.6, PA_D + 0.6, 0.25, COL["losa"], "casa")
            E.caja(-0.6, -0.6, 6.6, W + 1.2, 0.6, 0.35, COL["losa"], "casa"); E.caja(-0.6, -0.6, 6.6, 0.6, PA_D + 0.6, 0.35, COL["losa"], "casa"); E.caja(W, -0.6, 6.6, 0.6, PA_D + 0.6, 0.35, COL["losa"], "casa")
            E.caja(0.3, -0.04, 4.0, W - 0.6, 0.06, 2.25, COL["ventana_noche"] if noche else "#34506cb8", "casa", mat_v)
            ventana(0.6, 3.3, 0.9, 2.6); ventana(6.3, 8.4, 0.9, 2.6); puerta()
            E.caja(5.75, -0.6, -0.3, 3.6, 0.6, 0.9, "#b59a79", "casa")
        elif fachada == "Ladrillo":
            ventana(0.6, 3.3, 0.9, 2.6, marco="#f4f1ea"); ventana(6.3, 8.4, 0.9, 2.6, marco="#f4f1ea"); ventana(0.6, 3.3, 4.2, 5.9, marco="#f4f1ea"); ventana(6.1, 8.6, 4.2, 5.9, marco="#f4f1ea"); puerta(color="#2b2b2b")
            if detalle:
                for k in range(4): E.caja(3.6 + k * 0.7, -1.6, 2.5, 0.12, 1.7, 0.12, COL["madera"], "casa")
                E.caja(3.5, -1.6, 2.4, 0.12, 0.12, 0.1, COL["madera"], "casa"); E.caja(3.5, -1.6, 0, 0.12, 0.12, 2.5, COL["madera"], "casa"); E.caja(6.1, -1.6, 0, 0.12, 0.12, 2.5, COL["madera"], "casa")
        elif fachada == "Duela":
            if detalle:
                for k in range(16): E.caja(0, -0.08, 3.4 + k * 0.2, W, 0.06, 0.12, "#9a6a3a", "casa")
            ventana(0.6, 3.3, 0.9, 2.6); ventana(6.3, 8.4, 0.9, 2.6); ventana(0.6, 3.3, 4.2, 5.9); ventana(6.1, 8.6, 4.2, 5.9); puerta()
        elif fachada == "Cantera":
            ventana(0.6, 3.3, 0.9, 2.6, marco="#8b7b5e"); ventana(6.3, 8.4, 0.9, 2.6, marco="#8b7b5e"); ventana(0.6, 3.3, 4.2, 5.9, marco="#8b7b5e"); ventana(6.1, 8.6, 4.2, 5.9, marco="#8b7b5e"); puerta()
            if detalle:
                E.caja(3.9, -2.0, 0, 0.3, 0.3, 2.7, "#bda98a", "casa"); E.caja(5.6, -2.0, 0, 0.3, 0.3, 2.7, "#bda98a", "casa")
                for k in range(5): E.caja(3.7, -2.0 + k * 0.45, 2.7, 2.4, 0.12, 0.15, COL["madera"], "casa")
                E.caja(0.3, -0.6, -0.3, 3.0, 0.6, 0.7, "#bda98a", "casa")
        elif fachada == "Hacienda":
            E.caja(-0.2, -0.2, 6.3, W + 0.4, 0.3, 0.5, "#e8e1d3", "casa")
            ventana(0.6, 3.3, 0.9, 2.6, marco="#5a3e2b"); ventana(6.3, 8.4, 0.9, 2.6, marco="#5a3e2b"); ventana(0.6, 3.3, 4.2, 5.9, marco="#5a3e2b"); ventana(6.1, 8.6, 4.2, 5.9, marco="#5a3e2b"); puerta(4.1, 5.5)
            if detalle:
                for xx in (3.6, 5.9): E.caja(xx, -0.5, 0, 0.5, 0.5, 2.6, "#e8e1d3", "casa")
                E.caja(3.6, -0.5, 2.6, 2.8, 0.5, 0.4, "#e8e1d3", "casa")
        elif fachada == "Marco":
            E.caja(-0.6, -0.7, -0.3, 0.6, 0.7, 7.4, "#3b3b3b", "casa"); E.caja(W, -0.7, -0.3, 0.6, 0.7, 7.4, "#3b3b3b", "casa"); E.caja(-0.6, -0.7, 7.1, W + 1.2, 0.7, 0.5, "#3b3b3b", "casa")
            ventana(0.5, 3.4, 0.6, 2.8); ventana(6.0, 8.5, 0.6, 2.8); ventana(0.5, 8.5, 4.0, 6.1); puerta()
        elif fachada == "Lamas":
            if detalle:
                for k in range(28): E.caja(0.3 + k * 0.3, -0.38, 3.4, 0.08, 0.14, 3.0, COL["madera"], "casa")
            ventana(0.6, 3.3, 0.9, 2.6); ventana(6.3, 8.4, 0.9, 2.6); ventana(0.6, 3.3, 4.2, 5.9); ventana(6.1, 8.6, 4.2, 5.9); puerta()
        elif fachada == "Concreto":
            if detalle:
                for zz in (1.1, 2.2, 4.4, 5.5): E.caja(0, -0.015, zz, W, 0.03, 0.05, "#8c8c87", "casa")
            ventana(0.5, 3.6, 0.5, 2.9); ventana(6.0, 8.6, 0.5, 2.9); ventana(0.5, 3.6, 3.9, 6.2); ventana(6.0, 8.6, 3.9, 6.2); puerta(color="#1e1e1e")
        else:  # Celosía
            if detalle:
                for i in range(20):
                    for j in range(7): E.caja(0.15 + i * 0.45, -0.42, 3.5 + j * 0.45, 0.3, 0.12, 0.3, "#c4704f", "casa")
            ventana(0.6, 3.3, 0.9, 2.6); ventana(6.3, 8.4, 0.9, 2.6); ventana(0.6, 3.3, 4.2, 5.9); ventana(6.1, 8.6, 4.2, 5.9); puerta()
        if noche: E.luz(2.0, -0.4, 2.0, 1.1, "#ffe0a8"); E.luz(7.3, -0.4, 2.0, 1.1, "#ffe0a8")
        for p in E.P: self.P.append([girar(p[0], rot, 0, 0, x0, y0), p[1], p[2], p[3], p[4], p[5]])
        for l in E.luces: px, py = girar([(l[0], l[1])], rot, 0, 0, x0, y0)[0]; self.luces.append([px, py, l[2], l[3], l[4]])
    def lote(self, fachada, x0, y0, rot=0.0, noche=False, auto=None, detalle=True, bardas=True):
        """Lote de 12.7 × 25.8 con su casa, cochera, andador, jardín, bardas de colindancia y equipos; el frente en y0 (local), la calle hacia -y local."""
        E = Escena("tmp"); E.rnd = self.rnd; r = self.rnd
        E.suelo(0, 0, LOTE_W, LOTE_D, -0.32, r.choice([COL["pasto"], COL["pasto2"]]))
        E.suelo(LOTE_W - 0.3 - 5.85, 0, LOTE_W - 0.3, FRENTE, -0.3, COL["cochera"]); E.suelo(0.3, 0, 1.5, FRENTE, -0.3, COL["andador"])
        E.casa(fachada, (LOTE_W - W) / 2, FRENTE, 0, noche, detalle)
        if auto: E.auto(LOTE_W - 0.3 - 5.85 + 0.6, 0.6, math.pi / 2 + 0.0, auto if isinstance(auto, str) else None)
        if bardas:                                                     # bardas de colindancia de 2.4 m detrás del paramento, y la del fondo
            E.caja(0, FRENTE + 1.0, -0.32, 0.15, LOTE_D - FRENTE - 1.0, 2.4, "#d9d5cd", "casa"); E.caja(0, LOTE_D - 0.15, -0.32, LOTE_W, 0.15, 2.4, "#d9d5cd", "casa")
            E.caja(LOTE_W - 0.15, FRENTE + 1.0, -0.32, 0.15, LOTE_D - FRENTE - 1.0, 2.4, "#d9d5cd", "casa")
            E.caja(0.3, FRENTE + 0.2, -0.32, 1.2, 0.05, 1.6, "#3a3a3a", "casa")                            # reja del patio lateral
            E.caja(LOTE_W - 0.3 - 1.4, FRENTE - 0.05, -0.32, 1.4, 0.05, 1.8, "#3a3a3a", "casa")           # reja de servicio
        if detalle:
            for k in range(r.randint(2, 4)): E.arbusto(1.9 + r.random() * 2.2, 0.5 + r.random() * 2.6, 0.35 + r.random() * 0.3, 0.4 + r.random() * 0.5)
            if r.random() < 0.5: E.arbolito(2.0 + r.random() * 1.5, 1.2 + r.random() * 2.0, 2.6 + r.random() * 1.2)
            E.caja((LOTE_W - W) / 2 + 0.6, FRENTE + 1.0, 6.9, 0.9, 0.4, 0.55, "#d8d8d8", "casa"); E.caja((LOTE_W - W) / 2 + 1.7, FRENTE + 1.0, 6.9, 0.9, 0.4, 0.55, "#d8d8d8", "casa")   # equipos de aire
            E.caja((LOTE_W - W) / 2 + 5.2, FRENTE + 9.0, 6.9, 2.0, 1.0, 0.3, "#3a4d6a", "casa"); E.caja((LOTE_W - W) / 2 + 5.4, FRENTE + 10.1, 6.9, 1.6, 0.6, 0.6, "#c9c9c9", "casa")   # calentador solar
            E.caja(1.5, 0.3, -0.32, 0.12, 0.12, 1.1, "#3a3a3a", "casa"); E.caja(1.4, 0.2, 0.78, 0.32, 0.32, 0.22, "#2a2a2a", "casa")   # buzón y número
            for k in range(3): E.arbusto(LOTE_W - 2.5 + r.random() * 2.0, FRENTE + 16 + r.random() * 8, 0.5, 0.6)
            E.arbusto(1.0 + r.random() * 2, LOTE_D - 3 - r.random() * 4, 0.6, 0.8)
        for p in E.P: self.P.append([girar(p[0], rot, 0, 0, x0, y0), p[1], p[2], p[3], p[4], p[5]])
        for l in E.luces: px, py = girar([(l[0], l[1])], rot, 0, 0, x0, y0)[0]; self.luces.append([px, py, l[2], l[3], l[4]])
    def calle(self, x0, x1, y=0.0, noche=False, lotes=True, arbotantes=True, fachadas=SEQ, autos=0.4, gente=3, n_ini=0, arboles=True):
        """Calle tipo de 11 m con eje en y, lotes a los dos lados (frente en y ± 5.5), nogales cada 12.7 m en la orilla de la banqueta."""
        self.suelo(x0, y - 3.5, x1, y + 3.5, -0.47, COL["asfalto"]); self.caja(x0, y - 3.5, -0.47, x1 - x0, 7, 0.02, COL["asfalto"], "suelo", "suelo")
        for s in (-1, 1):
            self.suelo(x0, y + s * 3.5 if s > 0 else y - 5.5, x1, y + 5.5 if s > 0 else y - 3.5, -0.32, COL["banqueta"])
            self.caja(x0, y + s * 3.5 - (0.15 if s < 0 else 0), -0.47, x1 - x0, 0.15, 0.17, COL["guarnicion"], "suelo")
        n = int((x1 - x0) / LOTE_W); k = 0
        for i in range(n):
            xa = x0 + i * LOTE_W
            for s, rot, yy in ((1, 0.0, y + 5.5), (-1, math.pi, y - 5.5)):
                if lotes:
                    f = fachadas[(k + n_ini + (4 if s < 0 else 0)) % len(fachadas)]
                    self.lote(f, xa if s > 0 else xa + LOTE_W, yy, rot, noche, auto=self.rnd.random() < autos)
                if arboles: self.nogal(xa, yy + s * 0.9, 1.0, iluminado=noche and i % 2 == 0)
            k += 1
        if arboles: self.nogal(x0 + n * LOTE_W, y + 6.4); self.nogal(x0 + n * LOTE_W, y - 6.4)
        if arbotantes:
            for i, xx in enumerate(range(int(x0) + 12, int(x1) - 4, 25)):
                s = 1 if i % 2 == 0 else -1; self.arbotante(xx, y + s * 4.6, 6.0, 1.3, -s, noche=noche)
        for g in range(gente):
            self.persona(self.rnd.uniform(x0 + 5, x1 - 5), y + self.rnd.choice([-4.5, 4.5]) + self.rnd.uniform(-0.4, 0.4))

def girar(pts, rot, px, py, tx=0.0, ty=0.0):
    c, s = math.cos(rot), math.sin(rot)
    return [(round(px + (x - px) * c - (y - py) * s + tx, 3), round(py + (x - px) * s + (y - py) * c + ty, 3)) for x, y in pts]

def guardar(E, meta):
    d = dict(prismas=E.P, luces=E.luces, **meta)
    json.dump(d, open(os.path.join(OUT, E.nombre + ".json"), "w"), separators=(",", ":"), ensure_ascii=False)
    return dict(id=E.nombre, prismas=len(E.P), **{k: v for k, v in meta.items() if k != "vistas"}, vistas=meta.get("vistas", {}))

INDICE = []
def cam(az, el, zoom, dist, cx, cy, cz): return dict(az=az, el=el, zoom=zoom, dist=dist, cx=cx, cy=cy, cz=cz)
def ojo(o, m, fov=50.0):
    """Cámara desde el ojo `o` mirando al punto `m`, con campo horizontal `fov` grados (para 1920 × 1080)."""
    dx, dy, dz = m[0] - o[0], m[1] - o[1], m[2] - o[2]; d = math.sqrt(dx * dx + dy * dy + dz * dz)
    fx, fy, fz = dx / d, dy / d, dz / d
    az = math.atan2(fx, fy); el = math.asin(max(-1, min(1, -fz)))
    fw = 2 * d * math.tan(math.radians(fov / 2)); zoom = math.log((1920 / fw) / (1080 / 32)) / math.log(1.15)
    return dict(az=round(az, 4), el=round(el, 4), zoom=round(zoom, 2), dist=round(d, 2), cx=m[0], cy=m[1], cz=m[2])

# ---------- 1 · Calle entre nogales ----------
E = Escena("calle"); E.suelo(-120, -80, 120, 80, -0.5, COL["tierra"])
E.calle(-63.5, 63.5, 0.0, autos=0.45, gente=4)
E.auto(-20, -1.6, 0.0, "#d8d8d8"); E.auto(22, 1.0, math.pi, "#1f3a5f")
INDICE.append(guardar(E, dict(titulo="La calle bajo los nogales", porque="Es lo que nadie más puede ofrecer en Torreón: una calle de casas nuevas ya sombreada por nogales de 10 m. Vende el lugar antes que la casa.",
    hora="dia", centro=[0, 0, 2.0], dist=40, suelo_z=-0.32, contornos=0.6, bruma=[60, 180], cam=ojo((-34, 0.6, 1.7), (40, 0, 3.0), 58),
    vistas=dict(peaton=ojo((-34, 0.6, 1.7), (40, 0, 3.0), 58), banqueta=ojo((-30, 4.2, 1.7), (30, -2, 3.0), 60), alta=ojo((-50, -30, 22), (10, 2, 2), 55), frente=ojo((2, -14, 1.7), (-6, 16, 4), 60)))))

# ---------- 2 · La casa Modelo Nogal (fachada Horizonte), con vecinas ----------
E = Escena("casa"); E.suelo(-80, -60, 80, 80, -0.5, COL["tierra"])
E.calle(-38.1, 38.1, 0.0, lotes=False, gente=2, arboles=False)
for i in range(7):
    xa = -38.1 + i * LOTE_W
    E.nogal(xa, 6.4, 0.85 if i in (2, 3) else 1.0, alza=1.8 if i in (2, 3) else 0.0); E.nogal(xa, -6.4, 1.0)
for i, f in enumerate(["Ladrillo", "Lamas", None, "Duela", "Cantera", "Hacienda"]):
    xa = -38.1 + i * LOTE_W
    if f: E.lote(f, xa, 5.5, 0.0, auto=i in (0, 4))
for i, f in enumerate(["Marco", "Concreto", "Celosía", "Horizonte", "Ladrillo", "Lamas"]): E.lote(f, -38.1 + (i + 1) * LOTE_W, -5.5, math.pi, auto=i in (1, 4))
for p in C3D.MODELO["prismas"]:
    if p[4] in ("arboles",): continue
    E.P.append([[[x + (-38.1 + 2 * LOTE_W), y + 5.5] for x, y in p[0]], p[1], p[2], p[3], "casa", p[5]])
E.auto(-38.1 + 2 * LOTE_W + 6.9, 6.1, math.pi / 2, "#f2f2f2"); E.persona(-38.1 + 2 * LOTE_W + 1.0, 4.2); E.persona(-38.1 + 2 * LOTE_W + 1.6, 4.0, 1.2, "#e9c46a")
INDICE.append(guardar(E, dict(titulo="Modelo Nogal · fachada Horizonte", porque="La casa que se vende: 4 recámaras con baño, 243 m², y la fachada que la hace distinta de la de al lado. Con la vecina de ladrillo y la de duela se ve que no hay dos iguales.",
    hora="tarde", centro=[-6.35, 10, 3], dist=34, suelo_z=-0.32, contornos=0.55, bruma=[50, 160], cam=ojo((6.3, -11, 1.6), (-6.35, 11, 3.6), 50),
    vistas=dict(calle=ojo((6.3, -11, 1.6), (-6.35, 11, 3.6), 50), frente=ojo((-6.35, -12, 1.7), (-6.35, 12, 3.4), 50), esquina=ojo((14, -16, 9), (-6.35, 12, 3), 48), vecinas=ojo((20, -6, 1.7), (-10, 12, 3.4), 60)))))

# ---------- 3 · Vista aérea del fraccionamiento (geometría real) ----------
FC = json.load(open(f"{DAT}/confort.geojson")); SV = json.load(open(f"{DAT}/servicios.json")); ARB = json.load(open(f"{DAT}/arboles_confort.json"))
LIM = next(f for f in FC["features"] if f["properties"]["capa"] == "limite"); _cs = LIM["geometry"]["coordinates"][0]
_lon0 = sum(c[0] for c in _cs) / len(_cs); _lat0 = sum(c[1] for c in _cs) / len(_cs); _t = math.radians(SV["geo"]["th"])
def uv(lon, lat):
    x = (lon - _lon0) * math.cos(math.radians(_lat0)) * 111320.0; y = (lat - _lat0) * 110574.0
    return x * math.cos(_t) + y * math.sin(_t), -x * math.sin(_t) + y * math.cos(_t)
def poly(f): return [uv(*c) for c in f["geometry"]["coordinates"][0]]
rot = [f for f in FC["features"] if f["properties"]["capa"] == "rotulo"]
V_CALLE = {}
for f in rot:
    if f["properties"]["eje"] == "largo": V_CALLE.setdefault(f["properties"]["nombre"].replace("Bulevar ", ""), []).append(uv(*f["geometry"]["coordinates"])[1])
V_CALLE = {k: sorted(v)[len(v) // 2] for k, v in V_CALLE.items()}
E = Escena("aerea")
lim = poly(LIM); E.prisma(lim, -0.5, 0.1, COL["tierra"], "suelo", "suelo")
E.suelo(-900, -600, 900, 600, -0.6, "#d8cdb3")
capas_col = {"vial": (COL["asfalto"], -0.47, 0.05), "bulevar": (COL["banqueta"], -0.4, 0.05), "arroyo": (COL["asfalto"], -0.47, 0.06), "sendero": (COL["andador"], -0.34, 0.03), "pista": ("#e2ded4", -0.38, 0.05),
             "parque": (COL["pasto"], -0.36, 0.04), "comunal": (COL["pasto2"], -0.36, 0.04), "plaza_acceso": (COL["andador"], -0.36, 0.04), "ptar": ("#9a9a9a", -0.36, 0.04), "estacionamiento": (COL["cochera"], -0.36, 0.05),
             "salon": ("#e4d9c6", -0.3, 7.0), "tenis": (COL["cancha"], -0.3, 0.06), "padel": ("#2f7a5c", -0.3, 0.06), "caseta": ("#55534f", -0.3, 3.4), "comercio": ("#d6c6a4", -0.3, 4.5), "isla": (COL["pasto"], -0.3, 0.05)}
for f in FC["features"]:
    c = f["properties"]["capa"]
    if c in capas_col and f["geometry"]["type"] == "Polygon":
        col, z, h = capas_col[c]; E.prisma(poly(f), z, h, col, "suelo" if h < 0.1 else "edif", "suelo" if h < 0.1 else "")
for f in FC["features"]:
    p = f["properties"]
    if p["capa"] != "lote": continue
    pts = poly(f); us = [q[0] for q in pts]; vs = [q[1] for q in pts]; u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
    cu = (u0 + u1) / 2; vc = V_CALLE.get(p["dir"].rsplit(" ", 1)[0], v0 - 10); ancho = u1 - u0
    E.prisma(pts, -0.36, 0.04, COL["pasto"] if (p["n"] % 3) else COL["pasto2"], "suelo", "suelo")
    if (v0 + v1) / 2 > vc: y0, s = v0 + FRENTE, 1          # frente al sur del lote (la calle está abajo)
    else: y0, s = v1 - FRENTE, -1
    pb, pa = FACH[p["fachada"]]
    xa = cu - W / 2
    E.caja(xa, y0 if s > 0 else y0 - PB_D, -0.3, W, PB_D, 3.6, pb, "casa"); E.caja(xa, y0 if s > 0 else y0 - PA_D, 3.3, W, PA_D, 3.3, pa, "casa")
    E.caja(xa - 0.1, (y0 if s > 0 else y0 - PA_D) - 0.1, 6.6, W + 0.2, PA_D + 0.2, 0.35, COL["azotea"], "casa")
    E.suelo(cu + W / 2 - 5.85 + (0 if s > 0 else 0), y0 - FRENTE if s > 0 else y0, cu + W / 2 + 0.0, y0 if s > 0 else y0 + FRENTE, -0.3, COL["cochera"])
for a in ARB:
    if a[2]: continue
    u, v = uv(a[0], a[1]); E.nogal_simple(u, v, a[3])
# barda perimetral, acceso, calzada, autos y las huertas vecinas alrededor
for a, b in zip(lim[:-1], lim[1:]):
    L_ = math.dist(a, b)
    if L_ < 1: continue
    ang = math.atan2(b[1] - a[1], b[0] - a[0]); E.caja(a[0], a[1] - 0.1, -0.36, L_, 0.2, 3.0, "#e4d9c6", "edif", rot=ang, px=a[0], py=a[1])
def dentro(x, y, poly=lim):
    c = False; n = len(poly) - 1
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[i + 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
umin, umax = min(p[0] for p in lim), max(p[0] for p in lim); vmin, vmax = min(p[1] for p in lim), max(p[1] for p in lim)
E.suelo(umin - 200, vmin - 46, umax + 200, vmin - 18, -0.52, COL["asfalto"])                          # calzada
cu = SV["calles"]["u_acceso"]
E.caja(cu - 16, vmin + 7, -0.3, 32, 0.8, 6.4, "#55534f", "edif")                                        # pórtico
ii = 0
for gi in range(int((umin - 140) / 12.62), int((umax + 140) / 12.62)):
    for gj in range(int((vmin - 140) / 12.62), int((vmax + 140) / 12.62)):
        x, y = gi * 12.62 + 3.0, gj * 12.62 + 1.0; ii += 1
        if dentro(x, y) or min(math.dist((x, y), p) for p in lim[::1]) < 7 and dentro(x, y): continue
        if E.rnd.random() < 0.72 and not dentro(x, y): E.nogal_simple(x, y, 9.0 + E.rnd.random() * 2.5)
for f in FC["features"]:
    if f["properties"]["capa"] == "vial" and f["geometry"]["type"] == "Polygon":
        pts = poly(f); us = [q[0] for q in pts]; vs = [q[1] for q in pts]
        if max(us) - min(us) > 200:
            for k in range(int((max(us) - min(us)) / 45)):
                if E.rnd.random() < 0.6: E.auto(min(us) + 10 + k * 45 + E.rnd.random() * 20, (min(vs) + max(vs)) / 2 - 2.5 + E.rnd.choice([0, 3.4]), 0.0 if E.rnd.random() < 0.5 else math.pi)
INDICE.append(guardar(E, dict(titulo="La Nogalera desde el aire", porque="Las 1,105 casas entre 1,943 nogales, el bulevar, el club, los parques y la pista alrededor: el comprador entiende el tamaño y el orden del lugar en una sola imagen.",
    hora="tarde", centro=[-40, -20, 0], dist=1400, suelo_z=-0.32, contornos=0.3, bruma=[900, 2200], cam=cam(0.55, 0.62, -22, 1400, -40, -20, 0),
    vistas=dict(oriente=cam(0.55, 0.62, -22, 1400, -40, -20, 0), acceso=cam(0.05, 0.5, -20, 1200, -300, -150, 0), club=cam(0.9, 0.55, -17, 900, -250, -40, 0), cenital=cam(0.0, 1.5, -22, 1400, -40, -20, 0)))))

# ---------- 4 · El acceso al atardecer ----------
import n6_acceso_calc as ACC, n6_acceso as ACP
E = Escena("acceso"); A0, A1 = ACC.ANCHO; CV = ACC.CASETA_V
E.suelo(-200, -80, 200, 140, -0.62, COL["tierra"])
E.suelo(-200, -34, 200, -18, -0.5, COL["asfalto"]); E.suelo(-200, -18, 200, 0, -0.42, COL["banqueta"])          # calzada y franja
E.suelo(A0, -18, A1, CV + 30, -0.47, COL["asfalto"]); E.suelo(-200, 0, 200, 5, -0.4, "#e2ded4")                   # carriles y pista
E.suelo(-180, 5, A0 - 1, 100, -0.36, COL["pasto"]); E.suelo(A1 + 1, 5, 180, 100, -0.36, COL["pasto"]); E.suelo(-5.5, CV + 12, 5.5, 120, -0.47, COL["asfalto"])
for n, a, b, t in ACC.CARRILES:
    if t == "isla":
        for ya, yb in ((ACC.ISLA_V0, ACC.RETORNO[0]), (ACC.RETORNO[1], CV + 6)): E.caja(a, ya, -0.47, b - a, yb - ya, 0.32, COL["pasto"], "suelo", "suelo")
        if "visitas" in n: E.caja(a + 0.2, CV - 3, -0.15, b - a - 0.4, 6, 3.4, "#55534f", "edif"); E.caja(a + 0.35, CV - 2.6, 0.9, b - a - 0.7, 5.2, 1.6, COL["ventana_noche"], "edif", "luz")
        else: E.caja(a + 0.5, CV - 1.5, -0.15, b - a - 1.0, 3, 3.2, "#55534f", "edif"); E.caja(a + 0.65, CV - 1.2, 0.9, b - a - 1.3, 2.4, 1.5, COL["ventana_noche"], "edif", "luz")
    elif t == "peaton": E.caja(a, -18, -0.4, b - a, CV + 30, 0.08, COL["banqueta"], "suelo", "suelo"); E.caja(a + 0.5, CV - 0.6, -0.32, b - a - 1.0, 1.2, 1.1, COL["acero"], "edif")
    else:
        E.caja(a + 0.2, CV - 0.1, 0.6, 0.1, 0.1, 0.5, COL["poste"], "edif"); E.caja(a + 0.2, CV - 0.05, 0.95, b - a - 0.6, 0.08, 0.08, "#f0f0f0", "edif")
# muro de identidad, reja, nombre, pórtico, postes
E.caja(-180, -0.1, -0.32, 180 + A0 - 40, 0.2, 3.3, "#e4d9c6", "edif"); E.caja(A1 + 40, -0.1, -0.32, 140, 0.2, 3.3, "#e4d9c6", "edif")
for xx in list(range(-180, int(A0 - 40), 6)) + list(range(int(A1 + 40), 180, 6)): E.caja(xx, -0.2, -0.32, 0.4, 0.4, 3.5, "#d9d5cd", "edif")
E.caja(A0 - 54, -0.35, 1.1, 13, 0.1, 1.2, "#2a2a2a", "edif"); E.caja(A0 - 53.6, -0.3, 1.25, 12.2, 0.02, 0.9, COL["luz"], "edif", "luz"); E.luz(A0 - 47.5, -0.8, 1.8, 4.0, "#fff0cc")
for a, b in ((A0 - 40, A0), (A1, A1 + 40)):
    E.caja(a, -0.1, -0.32, b - a, 0.2, 0.9, "#e4d9c6", "edif"); E.caja(a, -0.05, 2.95, b - a, 0.1, 0.1, COL["poste"], "edif")
    x = a + 0.2
    while x < b: E.caja(x, -0.03, 0.58, 0.05, 0.06, 2.4, COL["poste"], "edif"); x += 0.36
for xx in (A0 - 1.0, A1 + 0.2): E.caja(xx, ACP.PORTICO_V - 0.4, -0.32, 0.8, 0.8, ACP.PORTICO_H + 1.2, "#55534f", "edif")
E.caja(A0 - 1.0, ACP.PORTICO_V - 0.4, ACP.PORTICO_H, A1 - A0 + 2.0, 0.8, 0.9, "#55534f", "edif"); E.caja(A0 + 6, ACP.PORTICO_V - 0.46, ACP.PORTICO_H + 0.2, A1 - A0 - 12, 0.04, 0.5, COL["luz"], "edif", "luz")
for xx in (A0 - 1.2, A1 - 1.5): E.arbotante(xx, 12, 9.0, 1.6, 1 if xx < 0 else -1, noche=True)
for xx in (A0 - 1.2, A1 - 1.5): E.arbotante(xx, 48, 9.0, 1.6, 1 if xx < 0 else -1, noche=True)
E.caja(A0 - 48, 8, -0.3, 44, 22, 5.0, "#d6c6a4", "edif"); E.caja(A0 - 46, 7.9, 0.3, 40, 0.08, 3.0, COL["ventana_noche"], "edif", "luz"); E.caja(A0 - 49, 7.0, 4.6, 46, 1.2, 0.5, COL["losa"], "edif")  # súper
E.suelo(A1 + 4, 8, A1 + 51, 28, -0.38, COL["cochera"])
for k in range(5): E.auto(A1 + 8 + k * 6, 10, math.pi / 2)
for xx, yy in ((A0 - 30, 40), (A0 - 14, 48), (A0 - 42, 54), (A1 + 20, 40), (A1 + 36, 48), (A1 + 10, 56), (A1 + 50, 56), (A0 - 20, 70), (A1 + 30, 72), (-60, -10), (60, -10), (-110, -9), (110, -9)): E.nogal(xx, yy, 1.0, iluminado=True)
E.auto(A0 + 4.2, 30, math.pi / 2, "#d8d8d8"); E.auto_luces(A0 + 4.2, 30, math.pi / 2); E.auto(A0 + 7.5, 20, math.pi / 2, "#1f3a5f"); E.auto(A0 + 17, 44, math.pi / 2, "#8c1c13")
E.auto(A0 + 1.2, 40, -math.pi / 2, "#f2f2f2"); E.auto_luces(A0 + 1.2, 40, -math.pi / 2)
E.persona(A1 + 1.6, 20); E.persona(A1 + 2.4, 34, 1.7, "#f4f1de")
INDICE.append(guardar(E, dict(titulo="El acceso al atardecer", porque="La primera impresión: el pórtico, el nombre iluminado, la reja con los nogales atrás y la caseta encendida. Dice «seguro» y «cuidado» sin decirlo.",
    hora="atardecer", centro=[0, 12, 3], dist=70, suelo_z=-0.32, contornos=0.45, bruma=[90, 240], cam=ojo((-14, -30, 2.4), (2, 30, 4.2), 62),
    vistas=dict(calzada=ojo((-14, -30, 2.4), (2, 30, 4.2), 62), frontal=ojo((0, -60, 2.0), (0, 30, 4), 50), alta=ojo((-40, -70, 26), (0, 30, 3), 55), adentro=ojo((0, 95, 2.0), (0, 20, 4), 60)))))

# ---------- 5 · Bulevar Nogal ----------
E = Escena("bulevar"); E.suelo(-120, -90, 120, 90, -0.5, COL["tierra"])
x0, x1 = -63.5, 63.5
E.suelo(x0, -15, x1, 15, -0.4, COL["banqueta"])
for ya, yb in ((-9.8, -2.8), (2.8, 9.8)): E.suelo(x0, ya, x1, yb, -0.47, COL["asfalto"])
E.suelo(x0, -2.8, x1, 2.8, -0.42, COL["grava"]); E.suelo(x0, -1.2, x1, 1.2, -0.34, COL["andador"])
for k in range(int((x1 - x0) / 2.2)):
    xx = x0 + 1.1 + k * 2.2
    for yy in (-2.0, 2.0): E.cil(xx + E.rnd.uniform(-0.3, 0.3), yy + E.rnd.uniform(-0.4, 0.4), E.rnd.uniform(0.2, 0.4), -0.42, E.rnd.uniform(0.2, 0.55), E.rnd.choice(["#6f9a4a", "#8aa85e", "#5f8c42"]), "plantas", n=6)
for i in range(10):
    xa = x0 + i * LOTE_W
    E.lote(SEQ[(i + 2) % 9], xa, 15, 0.0, auto=i % 3 == 0); E.lote(SEQ[(i + 6) % 9], xa + LOTE_W, -15, math.pi, auto=i % 3 == 1)
    E.nogal(xa, 15.9); E.nogal(xa, -15.9)
for xx in range(int(x0) + 3, int(x1) - 5, 28): E.arbotante(xx, -2.3, 8.0, 1.4, 1, doble=True)
E.auto(-30, -6.5, 0.0, "#f2f2f2"); E.auto(10, -7.5, 0.0, "#8c1c13"); E.auto(25, 6.5, math.pi, "#1f3a5f")
for k in range(5): E.persona(E.rnd.uniform(x0 + 8, x1 - 8), E.rnd.choice([-0.5, 0.5, 12.5, -12.5]))
E.cil(-12, 0.4, 0.3, -0.34, 0.5, "#3d5a80", "gente", n=6); E.cil(-12, 0.4, 0.18, 0.16, 0.9, "#f4f1de", "gente", n=6); E.cil(-11.3, 0.4, 0.35, -0.34, 0.7, "#222222", "gente", n=8); E.cil(-12.7, 0.4, 0.35, -0.34, 0.7, "#222222", "gente", n=8)
INDICE.append(guardar(E, dict(titulo="Bulevar Nogal", porque="La calle principal con camellón que es jardín de lluvia y sendero: el paseo del fraccionamiento, donde se camina, se corre y se saluda. Da la escala de un lugar con vida de barrio.",
    hora="dia", centro=[0, 0, 2], dist=48, suelo_z=-0.32, contornos=0.55, bruma=[70, 190], cam=ojo((-30, 0.8, 1.7), (40, 0.5, 3.0), 60),
    vistas=dict(sendero=ojo((-30, 0.8, 1.7), (40, 0.5, 3.0), 60), banqueta=ojo((-28, 13.5, 1.7), (30, 5, 3), 60), alta=ojo((-50, -40, 24), (10, 0, 2), 55)))))

# ---------- 6 · Parque Garza ----------
E = Escena("parque"); E.suelo(-120, -90, 120, 90, -0.5, COL["tierra"])
E.suelo(-45, -40, 45, 40, -0.36, COL["pasto"])
for k in range(-40, 40, 8): E.suelo(-45, k, 45, k + 4, -0.355, COL["pasto2"])                      # pasto con franjas de corte
for xx, yy, ww, dd in ((-45, -40, 90, 0.8), (-45, 39.2, 90, 0.8), (-45, -40, 0.8, 80), (44.2, -40, 0.8, 80)): E.caja(xx, yy, -0.36, ww, dd, 0.3, COL["bordo"], "suelo")
E.caja(-45, 40, -0.47, 90, 11, 0.02, COL["asfalto"], "suelo", "suelo"); E.suelo(-45, 51, 45, 53, -0.32, COL["banqueta"]); E.suelo(-45, -51, 45, -40, -0.47, COL["asfalto"]); E.suelo(-45, -53, 45, -51, -0.32, COL["banqueta"])
E.caja(-2.5, -53, -0.34, 5, 106, 0.03, "#e2ded4", "suelo", "suelo"); E.caja(-45, -2.5, -0.34, 90, 5, 0.03, "#e2ded4", "suelo", "suelo")  # pista cruza el parque
for a0, a1, cx_, cy_, rr in ((0, 180, 0, 0, 22), (180, 360, 0, 0, 22)):                              # sendero circular de 2 m
    for a in range(a0, a1, 6):
        t = math.radians(a); E.caja(cx_ + rr * math.cos(t) - 1.3, cy_ + rr * math.sin(t) - 1.0, -0.34, 2.6, 2.0, 0.02, COL["andador"], "suelo", "suelo", rot=t + math.pi / 2, px=cx_ + rr * math.cos(t), py=cy_ + rr * math.sin(t))
for i in range(-3, 4):
    for j in range(-3, 4):
        if (i, j) in ((0, 0), (1, 1), (-1, 1), (0, 1)): continue
        E.nogal(i * 12.6 + E.rnd.uniform(-0.5, 0.5), j * 12.6 + E.rnd.uniform(-0.5, 0.5), 1.05)
E.pergola(-8, 8, 10, 5, 2.9); E.suelo(-8.5, 7.5, 2.5, 13.5, -0.33, COL["andador"])
for xx in (-6.5, -2.5, 1.0): E.caja(xx, 9.5, -0.34, 1.8, 0.8, 0.75, COL["madera"], "mob"); E.caja(xx, 8.8, -0.34, 1.8, 0.4, 0.45, COL["madera"], "mob"); E.caja(xx, 10.5, -0.34, 1.8, 0.4, 0.45, COL["madera"], "mob")
for xx, yy, rot in ((8, 20, 0.0), (-20, 16, 1.2), (14, -16, 2.4), (-16, -8, 0.6), (22, 2, 1.57), (-24, -2, -1.57)): E.banca(xx, yy, rot)
for xx, yy in ((10, 22), (-18, 18), (16, -18), (-14, -10)): E.cil(xx, yy, 0.3, -0.34, 0.9, "#4a4a4a", "mob", n=6)
E.caja(14, 14, -0.36, 14, 10, 0.02, COL["arena"], "suelo", "suelo")                                   # juegos
for xx, yy in ((16, 16), (22, 16), (16, 21), (22, 21)): E.caja(xx, yy, -0.36, 0.12, 0.12, 2.4, COL["poste"], "mob")
E.caja(16, 16, 2.3, 6.1, 0.1, 0.1, COL["poste"], "mob"); E.caja(16, 21, 2.3, 6.1, 0.1, 0.1, COL["poste"], "mob")
for xx in (17.5, 19.0, 20.5): E.caja(xx, 16.4, 0.1, 0.5, 0.2, 0.05, "#e9c46a", "mob"); E.caja(xx + 0.02, 16.45, 0.15, 0.03, 0.03, 2.1, "#8a8a8a", "mob"); E.caja(xx + 0.45, 16.45, 0.15, 0.03, 0.03, 2.1, "#8a8a8a", "mob")
E.caja(24, 18, -0.36, 1.2, 1.2, 1.8, "#e76f51", "mob"); E.caja(25.2, 18.2, 0.9, 2.6, 0.8, 0.12, "#2a9d8f", "mob", rot=0.0); E.caja(27.6, 18.2, -0.36, 0.3, 0.8, 1.2, "#2a9d8f", "mob")   # resbaladilla
E.caja(15, 22.5, -0.36, 2.4, 0.3, 0.8, "#e9c46a", "mob"); E.caja(15.2, 22.3, 0.3, 2.0, 0.7, 0.1, "#f4a261", "mob")   # sube y baja
for xx, yy in ((-30, 30), (30, 30), (-30, -30), (30, -30), (0, 36), (0, -36), (36, 0), (-36, 0)): E.farol(xx, yy, 3.5)
for xx, yy in ((-33, 20), (33, -22), (-28, -26), (28, 26)): E.arbusto(xx, yy, 1.0, 0.9); E.arbusto(xx + 1.4, yy + 0.8, 0.7, 0.6)
for k in range(9): E.persona(E.rnd.uniform(-34, 34), E.rnd.uniform(-34, 34), E.rnd.choice([1.7, 1.7, 1.2, 1.0]))
E.persona(0.6, -20, 1.7, "#9b2226"); E.persona(0.9, -12, 1.7, "#2a9d8f"); E.persona(18.5, 17.5, 1.0, "#e9c46a"); E.persona(26, 19.5, 1.1, "#3d5a80")
for i in range(7): E.lote(SEQ[(i + 1) % 9], -44.5 + i * LOTE_W, 58.5, 0.0, auto=i % 2 == 0); E.nogal(-44.5 + i * LOTE_W, 57.8)
for i in range(7): E.lote(SEQ[(i + 5) % 9], -44.5 + (i + 1) * LOTE_W, -58.5, math.pi, auto=i % 2 == 1); E.nogal(-44.5 + i * LOTE_W, -57.8)
INDICE.append(guardar(E, dict(titulo="Parque Garza, bajo la huerta", porque="Un parque que ya tiene árboles grandes el día que se inaugura: pérgola, juegos, bancas, un sendero circular y la pista cruzándolo, con las casas enfrente. Vende familia: niños, sombra y seguridad a la vista.",
    hora="dia", centro=[0, 5, 2], dist=60, suelo_z=-0.32, contornos=0.5, bruma=[80, 220], cam=ojo((-6.3, -47, 1.8), (-4.0, 20, 3.6), 64),
    vistas=dict(entrada=ojo((-6.3, -47, 1.8), (-4.0, 20, 3.6), 64), pista=ojo((-1.0, -50, 1.7), (6, 24, 3.2), 62), juegos=ojo((4, 2, 1.7), (20, 18, 1.8), 60), pergola=ojo((12, -4, 1.6), (-3, 10, 2.0), 62), alta=ojo((-60, -70, 32), (0, 10, 2), 55)))))

# ---------- 7 · La pista al amanecer ----------
E = Escena("pista"); E.suelo(-150, -60, 150, 60, -0.5, COL["tierra"])
E.suelo(-150, -2.5, 150, 2.5, -0.34, "#e2ded4"); E.suelo(-150, 2.5, 150, 40, -0.36, COL["pasto"]); E.suelo(-150, -2.5, 150, -6, -0.36, COL["pasto2"])
E.caja(-150, -6.2, -0.32, 300, 0.2, 3.0, "#e4d9c6", "edif")
for xx in range(-150, 150, 3): E.caja(xx, -6.27, -0.32, 0.15, 0.3, 3.1, "#d9d5cd", "edif")
for k in range(6): E.caja(-150, -6.22, 3.1 + 0.1 * k, 300, 0.02, 0.02, "#555555", "edif")
for xx in range(-140, 150, 60): E.cil(xx, -5.0, 0.08, -0.32, 6.0, COL["poste"], "edif", n=6); E.caja(xx - 0.15, -5.15, 5.8, 0.3, 0.3, 0.25, "#333333", "edif")
for xx in range(-140, 150, 20): E.cil(xx, 3.0, 0.06, -0.32, 0.9, COL["poste"], "luz", n=6); E.caja(xx - 0.08, 2.92, 0.85, 0.16, 0.16, 0.1, COL["luz"], "luz", "luz")
for i, xx in enumerate(range(-140, 150, 13)): E.nogal(xx + E.rnd.uniform(-0.6, 0.6), 2.5 + 2.8 + E.rnd.uniform(-0.5, 0.5), 1.0)
for i in range(11): E.lote(SEQ[(i + 3) % 9], -70 + i * LOTE_W, 14 + 25.8, math.pi, auto=False, detalle=False)
for xx, c in ((-18, "#9b2226"), (-10, "#2a9d8f"), (12, "#f4f1de"), (40, "#3d5a80")): E.persona(xx, E.rnd.uniform(-1.5, 1.5), 1.7, c)
E.cil(28, 0.8, 0.3, -0.34, 0.5, "#e9c46a", "gente", n=6); E.cil(28, 0.8, 0.18, 0.16, 0.9, "#222222", "gente", n=6); E.cil(28.7, 0.8, 0.35, -0.34, 0.7, "#222222", "gente", n=8); E.cil(27.3, 0.8, 0.35, -0.34, 0.7, "#222222", "gente", n=8)
INDICE.append(guardar(E, dict(titulo="La pista, 3.3 km bajo los nogales", porque="Correr o caminar a la sombra, sin salir del fraccionamiento, con la barda y la ronda al lado. Vende el estilo de vida y la seguridad en una sola toma.",
    hora="tarde", centro=[0, 0, 1.8], dist=34, suelo_z=-0.32, contornos=0.55, bruma=[40, 160], cam=ojo((-36, 0.4, 1.7), (40, -0.5, 2.5), 58),
    vistas=dict(corredor=ojo((-36, 0.4, 1.7), (40, -0.5, 2.5), 58), alta=ojo((-40, -30, 20), (10, 4, 2), 55), barda=ojo((-20, 16, 1.7), (20, -4, 2.5), 60)))))

# ---------- 8 · El club ----------
E = Escena("club"); E.suelo(-120, -90, 120, 90, -0.5, COL["tierra"])
E.suelo(-70, -60, 70, 60, -0.36, COL["pasto"]); E.suelo(-70, -5.5, 70, 5.5, -0.47, COL["asfalto"]); E.suelo(-70, 5.5, 70, 7.5, -0.32, COL["banqueta"]); E.suelo(-70, -7.5, 70, -5.5, -0.32, COL["banqueta"])
E.suelo(-40, 8, 40, 20, -0.34, COL["andador"])
E.caja(-30, 20, -0.3, 36, 20, 4.2, "#e4d9c6", "edif"); E.caja(-30, 20, 3.9, 36, 20, 3.6, "#d9d5cd", "edif"); E.caja(-31, 19, 7.5, 38, 22, 0.4, COL["losa"], "edif")
E.caja(-29, 19.9, 0.2, 34, 0.08, 3.2, COL["vidrio"], "edif"); E.caja(-29, 19.9, 4.3, 34, 0.08, 2.6, COL["vidrio"], "edif")
for xx in range(-30, 7, 4): E.caja(xx - 0.2, 17.5, -0.3, 0.4, 0.4, 4.2, COL["losa"], "edif")
E.caja(-30, 17.3, 3.9, 36, 2.9, 0.3, COL["losa"], "edif")
E.caja(12, 20, -0.3, 32, 16, 3.8, "#d2d2cf", "edif"); E.caja(12, 20, 3.5, 32, 16, 3.5, "#d2d2cf", "edif"); E.caja(11, 19, 7.0, 34, 18, 0.4, COL["losa"], "edif")
E.caja(13, 19.9, 0.6, 30, 0.08, 2.2, COL["vidrio_osc"], "edif"); E.caja(13, 19.9, 4.0, 30, 0.08, 2.4, COL["vidrio_osc"], "edif")
for k in range(10): E.caja(12.5 + k * 3.2, -0.42 + 0.0 - 0.0, 3.6, 0.1, 16.5, 0.08, "#8a5a2c", "edif") if False else None
E.suelo(-12, 44, 12, 68, -0.3, COL["cancha"]); E.caja(-12, 44, -0.3, 24, 0.05, 0.05, COL["cancha_l"], "mob")
for xx, yy, ww, dd in ((-12, 44, 0.08, 24), (11.92, 44, 0.08, 24), (-12, 44, 24, 0.08), (-12, 67.92, 24, 0.08)): E.caja(xx, yy, -0.3, ww, dd, 4.0, "#3a3a3a90", "mob")
E.caja(-6, 55.95, -0.3, 12, 0.1, 0.9, "#2a2a2a", "mob")
for xx in (16, 40):
    E.suelo(xx, 44, xx + 20, 54, -0.3, "#2f7a5c")
    for a, b, ww, dd in ((xx, 44, 0.06, 10), (xx + 19.94, 44, 0.06, 10), (xx, 44, 20, 0.06), (xx, 53.94, 20, 0.06)): E.caja(a, b, -0.3, ww, dd, 3.0, "#bcd9e866", "mob")
for xx, yy in ((-20, 10), (0, 10), (20, 10), (-40, 30), (-45, 50), (50, 30), (55, 62), (-30, 70), (30, 72), (-55, 10), (60, 8)): E.nogal(xx, yy, 1.0)
for k in range(4): E.caja(-20 + k * 6, 10, 2.4, 3.2, 3.2, 0.08, "#f4f1de", "mob"); E.cil(-18.4 + k * 6, 11.6, 0.05, -0.34, 2.4, COL["poste"], "mob", n=6)
for k in range(6): E.persona(E.rnd.uniform(-35, 35), E.rnd.uniform(9, 19))
for k in range(5): E.auto(-60 + k * 7, -3.8, 0.0)
INDICE.append(guardar(E, dict(titulo="El club: salón, gimnasio y canchas", porque="Salón con oficinas arriba, gimnasio de dos niveles, tenis y pádel entre nogales. Vende lo que la cuota paga y lo que una casa sola no tiene.",
    hora="tarde", centro=[8, 25, 3], dist=80, suelo_z=-0.32, contornos=0.55, bruma=[90, 240], cam=ojo((-44, -24, 5), (8, 26, 4), 60),
    vistas=dict(plaza=ojo((-44, -24, 5), (8, 26, 4), 60), canchas=ojo((30, 80, 8), (4, 48, 2), 60), alta=ojo((-40, -60, 40), (8, 35, 3), 55)))))

# ---------- 9 · Interior: sala, comedor y cocina abiertos al portal ----------
E = Escena("interior"); HX, HY = C3D.HX, C3D.HY
for p in C3D.MODELO["prismas"]: E.P.append(p)
E.suelo(-60, -40, 80, 80, -0.5, COL["pasto"])
for xx, yy in ((HX - 4, HY + 30), (HX + 14, HY + 30), (HX + 5, HY + 36), (-4, 13.4), (16.7, 13.4)): E.nogal(xx, yy, 1.0)
E.persona(HX + 6.9, HY + 9.4, 1.7, "#3d5a80"); E.persona(HX + 1.8, HY + 9.0, 1.7, "#e9c46a")
INDICE.append(guardar(E, dict(titulo="Sala, comedor y cocina abiertos al portal", porque="Desde adentro se ve el portal y los nogales del fondo: es la foto que hace que el comprador se imagine viviendo ahí. Medidas reales, muebles reales.",
    hora="tarde", centro=[HX + 4.5, HY + 11.5, 1.5], dist=9, suelo_z=-0.32, contornos=0.45, bruma=[0, 0], cam=ojo((HX + 1.2, HY + 7.9, 1.6), (HX + 6.0, HY + 14.5, 1.5), 72),
    vistas=dict(portal=ojo((HX + 1.2, HY + 7.9, 1.6), (HX + 6.0, HY + 14.5, 1.5), 72), comedor=ojo((HX + 0.8, HY + 11.2, 1.6), (HX + 8.5, HY + 9.0, 1.3), 72), cocina=ojo((HX + 5.3, HY + 9.5, 1.6), (HX + 7.5, HY + 3.5, 1.3), 70), sala=ojo((HX + 4.8, HY + 7.8, 1.6), (HX + 0.5, HY + 10.5, 1.2), 72)))))

# ---------- 10 · El portal y el jardín al atardecer ----------
E = Escena("portal"); E.suelo(-60, -40, 80, 90, -0.5, COL["pasto2"])
for p in C3D.MODELO["prismas"]: E.P.append(p)
for xx, yy in ((-1.5, 25.8), (14.2, 25.8), (4, 36), (-4, 13.4), (16.7, 13.4), (14, 44)): E.nogal(xx, yy, 0.95, iluminado=True)
E.luz(HX + 1.8, HY + 13.8, 2.6, 1.6); E.luz(HX + 7.0, HY + 13.8, 2.6, 1.6)
for xx in (HX + 0.3, HX + 8.7): E.caja(xx - 0.05, HY + 12.3, 2.5, 0.1, 0.1, 0.1, COL["luz"], "luz", "luz")
E.persona(HX + 3.2, HY + 14.2, 1.7, "#f4f1de"); E.persona(HX + 6.6, HY + 13.3, 1.7, "#9b2226"); E.persona(HX + 4.5, HY + 17, 1.1, "#2a9d8f")
INDICE.append(guardar(E, dict(titulo="El portal y el jardín al atardecer", porque="La vida de atrás: el portal techado con el asador, el jardín y los nogales iluminados. Es la imagen de fin de semana que cierra la venta.",
    hora="atardecer", centro=[HX + 4.5, HY + 15, 2], dist=22, suelo_z=-0.32, contornos=0.45, bruma=[30, 140], cam=ojo((HX + 10.5, HY + 27, 1.7), (HX + 4.0, HY + 13.5, 2.6), 58),
    vistas=dict(jardin=ojo((HX + 10.5, HY + 27, 1.7), (HX + 4.0, HY + 13.5, 2.6), 58), fondo=ojo((HX + 4.5, HY + 32, 1.7), (HX + 4.5, HY + 13, 3.0), 50), portal=ojo((HX + 8.5, HY + 17.5, 1.6), (HX + 1.5, HY + 13.2, 1.5), 68), alta=ojo((HX + 20, HY + 30, 12), (HX + 4.5, HY + 13, 2), 55)))))

# ---------- 11 · La calle de noche, con los nogales iluminados ----------
E = Escena("noche"); E.suelo(-120, -80, 120, 80, -0.5, COL["tierra"])
E.calle(-63.5, 63.5, 0.0, noche=True, autos=0.4, gente=2, n_ini=3)
E.auto(-10, 1.0, math.pi, "#2b2b2b"); E.auto_luces(-10, 1.0, math.pi)
INDICE.append(guardar(E, dict(titulo="La calle de noche", porque="Los nogales iluminados desde abajo, los arbotantes y las ventanas encendidas: la seguridad y el cuidado se ven. Nadie en Torreón vende una calle así de noche.",
    hora="noche", centro=[0, 0, 2.0], dist=40, suelo_z=-0.32, contornos=0.35, bruma=[40, 160], cam=ojo((-34, 0.6, 1.7), (40, 0, 3.0), 58),
    vistas=dict(peaton=ojo((-34, 0.6, 1.7), (40, 0, 3.0), 58), banqueta=ojo((-30, 4.2, 1.7), (30, -2, 3.0), 60), alta=ojo((-50, -30, 22), (10, 2, 2), 55)))))

# ---------- 12 · Las nueve fachadas, una por lote, para los renders de concurso ----------
E = Escena("fachadas"); E.suelo(-120, -80, 120, 80, -0.5, COL["tierra"])
E.calle(-57.15, 57.15, 0.0, lotes=False, arbotantes=False, gente=0, arboles=False)
VF = {}
for i, f in enumerate(SEQ):
    xa = -57.15 + i * LOTE_W
    E.lote(f, xa, 5.5, 0.0, auto=False)
    E.nogal(xa, 6.4, 0.9 + 0.1 * (i % 2), alza=1.4)                    # el nogal en la esquina del lote, con la copa alzada para despejar la fachada
    cx = xa + LOTE_W / 2
    VF["f%d_%s" % (i + 1, f.lower().replace("í", "i"))] = ojo((cx + 13, -9.5, 1.6), (cx - 0.5, 5.5 + 5.0, 3.4), 40)
    VF["frente_%d" % (i + 1)] = ojo((cx, -16, 1.7), (cx, 5.5 + 6, 3.4), 36)
E.nogal(57.15, 6.4, 1.0, alza=1.4)
for i in range(9): E.lote(SEQ[(i + 4) % 9], -57.15 + (i + 1) * LOTE_W, -5.5, math.pi, auto=False); E.nogal(-57.15 + i * LOTE_W, -6.4, 1.0)
E.nogal(57.15, -6.4, 1.0)
for xx in (-45, -20, 5, 30, 55): E.arbotante(xx, -4.6, 6.0, 1.3, 1)
VF["lejos"] = ojo((-96, -4.2, 2.0), (20, 6.5, 3.6), 26)                # la cuadra de lejos, desde la banqueta de enfrente con lente larga
VF["cuadra"] = ojo((-51, -1.5, 7.5), (12, 9, 3.2), 42)                   # la cuadra en escorzo, desde la calle y un poco en alto
VF["alta"] = ojo((-60, -55, 38), (0, 10, 2.0), 40)
INDICE.append(guardar(E, dict(titulo="Las nueve fachadas", porque="Una cuadra con las nueve fachadas seguidas, de frente y en escorzo, de cerca y de lejos: la imagen de concurso de cada una.",
    hora="tarde", centro=[0, 8, 3], dist=40, suelo_z=-0.32, contornos=0.5, bruma=[60, 180], cam=VF["f9_horizonte"], vistas=VF)))

json.dump(INDICE, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=1)
if __name__ == "__main__":
    for e in INDICE: print(e["id"], e["prismas"], "prismas")
