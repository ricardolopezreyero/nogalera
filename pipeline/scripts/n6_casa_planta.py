"""N6 · Modelo Nogal: plantas amuebladas con medidas libres (a paño interior de muro).
Coordenadas en metros: x a lo ancho (0 = costado izquierdo visto desde la calle), y hacia el fondo (0 = fachada).
Muros exteriores de 20 cm (dentro de los 9.0 m), interiores de 12 cm; bajo la escalera, tablaroca de 7 cm.
Columnas: A (0–3.8) recámaras con su clóset de paso y su baño; B (3.8–5.8) vestíbulo, escalera y pasillo; C (5.8–9.0)."""
W = 9.0
PB_D, PA_D = 12.0, 15.0                 # planta baja cerrada; la alta vuela 3 m sobre el portal
EXT, HALF = 0.20, 0.06
XA, XB = 3.8, 5.8
Y_REC, Y_PASO, Y_FIN = 3.7, 5.3, 7.2    # recámara | clóset de paso | baño (A y C, se repite en las dos plantas: tubería en línea)
HUELLA, PERALTE, ESC_ANCHO = 0.28, 0.1833, 0.92
ESC_TOP, ESC_PIE = 1.40, 1.40 + 17 * HUELLA      # sube hacia la fachada: arranca junto a la sala y llega al frente
BODEGA_EXT = (9.0, 3.0, 10.7, 5.2)     # bodega de servicio en el costado (fuera de los 9 m), detrás del patio de servicio

def esc(t): return str(t).replace("&", "&amp;").replace("<", "&lt;")

# ---------------- cuartos ----------------
# cada cuarto: nombre, rectángulo libre (x0, y0, x1, y1), tipo, texto de lo que cabe
def R(n, x0, y0, x1, y1, tipo, cabe="", lbl=None):
    return dict(n=n, r=(x0, y0, x1, y1), tipo=tipo, cabe=cabe, lbl=lbl)

PB = [
    R("Recámara 1", 0.20, 0.20, 3.74, 3.64, "hab", "Cama queen 1.60 × 2.00 con cabecera al muro del clóset, 2 burós de 45 cm, escritorio de 1.20 bajo la ventana. Al pie de la cama quedan 1.44 m libres.", (1.95, 1.0)),
    R("Clóset de paso 1", 0.20, 3.76, 3.74, 5.24, "guardar", "Clóset de 2.55 m × 60 cm (doble barra, cajonera y maletero) y pasillo de 88 cm que lleva al baño.", (1.5, 4.25)),
    R("Baño 1", 0.20, 5.36, 3.74, 7.14, "bano", "Regadera de 1.20 × 1.78 con cancel, WC, lavabo de 1.00 con mueble; ventana alta al costado.", (2.3, 5.95)),
    R("Vestíbulo", 3.86, 0.20, 5.74, 1.34, "circ", "Entrada de 1.10 m.", (4.8, 0.85)),
    R("Medio baño", 3.86, 1.46, 4.78, 2.96, "bano", "WC y lavabo de 45 cm, bajo la parte alta de la escalera (2.0 a 2.8 m libres).", (4.32, 1.98)),
    R("Bodega", 3.86, 3.08, 4.78, 5.20, "guardar", "Bajo la escalera: aspiradora, escalera de mano, maletas, adornos de temporada.", (4.32, 4.1)),
    R("Pasillo", 4.85, 1.34, 5.74, 7.20, "circ", "88 cm de la puerta a la sala.", None),
    R("Lavandería y blancos", 5.86, 0.20, 8.80, 2.84, "guardar", "Lavadora y secadora de 70 cm, tarja y mesa de doblar de 1.70 bajo la ventana, y una pared de entrepaños de 2.0 m × 45 cm de piso a techo para los blancos. Puerta de servicio al patio lateral.", (7.2, 1.9)),
    R("Cocina", 5.86, 2.96, 8.80, 8.00, "serv", "Cocina en paralelo: 5.0 m de cubierta y columnas de cada lado con pasillo de 1.70. Refrigerador de 90 cm, alacena de piso a techo de 1.20, horno en torre, parrilla de 90, tarja doble y lavavajillas. La barra remata hacia la sala.", (7.33, 5.4)),
    R("Sala", 0.20, 7.26, 5.00, 11.80, "estar", "Sofá de 3 plazas de 2.30, 2 sillones, mesa de centro y mueble de TV de 1.80 en el muro ciego (2.45 m de la pantalla al sofá).", (3.6, 11.3)),
    R("Comedor", 5.00, 8.00, 8.80, 11.80, "estar", "Mesa para 8 de 2.20 × 1.00 con 90 cm alrededor; credenza de 1.60.", (6.9, 11.45)),
]
PA = [
    R("Recámara 2", 0.20, 0.20, 3.74, 3.64, "hab", "Igual que la recámara 1: cama queen, 2 burós y escritorio bajo la ventana.", (1.95, 1.0)),
    R("Clóset de paso 2", 0.20, 3.76, 3.74, 5.24, "guardar", "Clóset de 2.55 m × 60 cm.", (1.5, 4.25)),
    R("Baño 2", 0.20, 5.36, 3.74, 7.14, "bano", "Regadera de 1.20, WC y lavabo de 1.00.", (2.3, 5.95)),
    R("Recámara 3", 5.86, 0.20, 8.80, 3.64, "hab", "Cama queen con cabecera al muro del costado, 2 burós; 89 cm al pie de la cama.", (7.3, 3.2)),
    R("Clóset de paso 3", 5.86, 3.76, 8.80, 5.24, "guardar", "Clóset en L de 2.8 m × 60 cm.", (7.0, 4.25)),
    R("Baño 3", 5.86, 5.36, 8.80, 7.14, "bano", "Regadera de 1.10, WC y lavabo de 80 cm.", (6.9, 5.95)),
    R("Llegada", 3.86, 0.20, 5.74, 1.34, "circ", "Descanso de la escalera junto a la ventana alta.", (4.8, 0.75)),
    R("Pasillo", 4.78, 1.34, 5.74, 7.20, "circ", "96 cm, con barandal al vacío de la escalera.", None),
    R("Clóset de blancos y limpieza", 3.86, 4.86, 4.78, 7.14, "guardar", "Puertas plegadizas al pasillo: 2.28 m de entrepaños de 92 cm de fondo (toallas, sábanas, aspiradora).", (4.32, 6.0)),
    R("Estancia", 0.20, 7.26, 3.74, 9.74, "estar", "Sofá de 2.00, mueble de TV o escritorio para trabajar en casa.", (1.9, 9.35)),
    R("Recibidor", 3.86, 7.26, 5.74, 9.74, "circ", "", None),
    R("Cuarto de blancos y bodega", 5.86, 7.26, 8.80, 9.74, "guardar", "Entrepaños en U de 45 cm: 6.9 m lineales de piso a techo. Blancos, maletas, ropa de temporada, cajas.", (7.33, 8.5)),
    R("Recámara principal", 0.20, 9.86, 5.14, 14.80, "hab", "Cama king 2.00 × 2.00 con cabecera al muro interior, 2 burós de 50 cm, banca al pie y sillón de lectura junto a la ventana. Al pie de la cama quedan 2.8 m.", (2.3, 13.0)),
    R("Vestidor", 5.26, 9.86, 8.80, 12.34, "guardar", "Vestidor de entrar: 6.2 m lineales de colgado y cajones de 60 cm en dos lados, pasillo de 1.28 m.", (7.0, 11.1)),
    R("Baño principal", 5.26, 12.46, 8.80, 14.80, "bano", "Doble lavabo de 1.60, regadera de 1.50 × 1.20 sin escalón, WC en nicho; ventana alta al jardín.", (7.0, 13.25)),
]
# superficies que se pintan de blanco para unir espacios abiertos (sin muro)
ABIERTO = {
    "PB": [(3.86, ESC_PIE, 5.74, 7.30), (3.86, 5.27, 4.78, ESC_PIE), (4.90, 7.20, 5.10, 11.80), (5.00, 7.20, 5.92, 8.10), (5.00, 7.90, 8.80, 8.10), (3.70, 7.20, 5.00, 7.30)],
    "PA": [(3.86, 1.34, 4.78, 4.80), (3.70, 7.26, 5.74, 9.74), (4.78, 7.10, 5.74, 7.30)],
}

# ---------------- muebles ----------------
# (tipo, x0, y0, x1, y1, extra)
M_REC_A = [("cama", 0.65, 1.64, 2.25, 3.64, "s"), ("R", 0.20, 3.19, 0.65, 3.64, "buró"), ("R", 2.25, 3.19, 2.70, 3.64, "buró"), ("R", 0.30, 0.20, 1.50, 0.70, "escritorio")]
M_PASO_A = [("closet", 0.20, 4.64, 2.75, 5.24, "")]
M_BANO_A = [("regadera", 0.20, 5.36, 1.40, 7.14, ""), ("wc", 1.65, 6.44, 2.15, 7.14, "s"), ("lavabo", 2.55, 6.62, 3.55, 7.14, "1")]
MUEBLES = {
    "PB": M_REC_A + M_PASO_A + M_BANO_A + [
        ("lavabo", 3.86, 1.46, 4.31, 1.86, "1"), ("wc", 4.07, 2.36, 4.57, 2.96, "s"),
        ("entrepanos", 3.86, 3.08, 4.78, 3.50, ""),
        ("lavadora", 8.10, 0.20, 8.80, 0.90, ""), ("lavadora", 8.10, 0.92, 8.80, 1.62, ""),
        ("tarja", 6.30, 0.20, 8.00, 0.80, ""), ("entrepanos", 5.86, 0.90, 6.31, 2.84, ""),
        ("refri", 8.05, 3.00, 8.80, 3.90, ""), ("alacena", 8.18, 3.80, 8.80, 5.00, ""), ("R", 8.18, 5.00, 8.80, 5.60, "horno"),
        ("cubierta", 8.18, 5.60, 8.80, 7.95, ""), ("estufa", 8.18, 6.10, 8.80, 7.00, ""),
        ("cubierta", 5.86, 3.20, 6.48, 7.95, ""), ("tarja", 5.86, 5.40, 6.48, 6.30, ""), ("R", 5.86, 6.30, 6.48, 6.90, "lv"),
        ("tv", 0.20, 8.60, 0.65, 10.40, ""), ("sofa", 3.10, 8.35, 4.05, 10.65, "e"), ("R", 1.60, 9.20, 2.20, 9.80, "centro"),
        ("sillon", 1.45, 7.55, 2.30, 8.40, "n"), ("sillon", 1.45, 10.60, 2.30, 11.45, "s"),
        ("mesa", 6.40, 8.80, 7.40, 11.00, "8"), ("R", 8.35, 9.10, 8.80, 10.70, "credenza"),
        ("escalera", 3.86, 5.20, 4.78, ESC_PIE, "pb"),
    ],
    "PA": M_REC_A + M_PASO_A + M_BANO_A + [
        ("cama", 6.80, 1.00, 8.80, 2.60, "e"), ("R", 8.35, 0.55, 8.80, 1.00, "buró"), ("R", 8.35, 2.60, 8.80, 3.05, "buró"),
        ("closet", 6.85, 4.64, 8.80, 5.24, ""), ("closet", 8.20, 3.76, 8.80, 4.64, ""),
        ("lavabo", 5.95, 6.64, 6.75, 7.14, "1"), ("wc", 6.95, 6.44, 7.45, 7.14, "s"), ("regadera", 7.70, 5.36, 8.80, 7.14, ""),
        ("escalera", 3.86, ESC_TOP, 4.78, 4.80, "pa"),
        ("entrepanos", 3.86, 4.86, 4.78, 7.14, ""),
        ("tv", 0.20, 7.70, 0.60, 9.30, ""), ("sofa", 2.70, 7.50, 3.60, 9.50, "e"),
        ("entrepanos", 8.35, 7.26, 8.80, 9.74, ""), ("entrepanos", 5.86, 9.29, 8.35, 9.74, ""), ("entrepanos", 6.40, 7.26, 8.35, 7.71, ""),
        ("cama", 1.30, 9.86, 3.30, 11.91, "n"), ("R", 0.80, 9.86, 1.30, 10.31, "buró"), ("R", 3.30, 9.86, 3.80, 10.31, "buró"),
        ("R", 1.60, 12.05, 3.00, 12.50, "banca"), ("sillon", 0.35, 13.70, 1.25, 14.60, "s"),
        ("closet", 5.26, 9.86, 8.80, 10.46, ""), ("closet", 5.26, 11.74, 7.90, 12.34, ""),
        ("lavabo", 5.26, 12.70, 5.81, 14.30, "2v"), ("regadera", 7.30, 13.60, 8.80, 14.80, ""), ("wc", 6.25, 14.10, 6.75, 14.80, "s"),
        ("R", 5.95, 13.90, 6.05, 14.80, ""),
    ],
}
# puertas: (x, y, ancho, muro 'x' (corre en x) o 'y', bisagra 0/1, abre hacia +1/-1)
PUERTAS = {
    "PB": [(4.25, 0.1, 1.10, "x", 0, 1), (3.8, 0.35, 0.85, "y", 1, -1), (2.85, Y_REC, 0.80, "x", 1, 1), (2.85, Y_PASO, 0.80, "x", 1, 1),
           (4.815, 1.60, 0.70, "y", 0, 1), (4.815, 3.30, 0.60, "y", 0, 1), (6.60, 2.90, 0.80, "x", 0, -1), (8.9, 1.85, 0.90, "y", 1, -1)],
    "PA": [(3.8, 0.35, 0.85, "y", 1, -1), (2.85, Y_REC, 0.80, "x", 1, 1), (2.85, Y_PASO, 0.80, "x", 1, 1),
           (5.8, 2.60, 0.80, "y", 0, 1), (5.95, Y_REC, 0.80, "x", 0, 1), (5.95, Y_PASO, 0.80, "x", 0, 1),
           (5.8, 8.00, 0.80, "y", 0, 1), (4.00, 9.8, 0.90, "x", 0, 1), (5.2, 10.70, 0.80, "y", 0, 1), (8.00, 12.4, 0.80, "x", 1, 1)],
}
VENTANAS = {
    "PB": [(0.6, 3.3, "x", 0.0), (6.3, 8.4, "x", 0.0), (0.4, 8.6, "x", PB_D), (5.7, 6.8, "y", 0.0), (6.3, 7.8, "y", W)],
    "PA": [(0.6, 3.3, "x", 0.0), (4.35, 5.25, "x", 0.0), (6.1, 8.6, "x", 0.0), (0.6, 4.6, "x", PA_D), (6.0, 7.2, "x", PA_D),
           (5.7, 6.8, "y", 0.0), (5.7, 6.8, "y", W), (7.6, 9.4, "y", 0.0)],
}
APERTURAS = {"PB": [], "PA": []}     # huecos sin puerta

def ml_closet(nivel):
    return sum(max(x1 - x0, y1 - y0) for t, x0, y0, x1, y1, e in MUEBLES[nivel] if t == "closet")

# ---------------- dibujo ----------------
def planta(nivel, titulo, S=42):
    D = PB_D if nivel == "PB" else PA_D
    pad = 22; top = 30
    w, h = (W + 1.9) * S + 2 * pad, PA_D * S + top + pad + 18
    X = lambda x: pad + x * S
    Y = lambda y: top + (PA_D - y) * S                 # fachada abajo, jardín arriba
    rect = lambda x0, y0, x1, y1, cls, extra="": f'<rect x="{X(x0):.1f}" y="{Y(y1):.1f}" width="{(x1-x0)*S:.1f}" height="{(y1-y0)*S:.1f}" class="{cls}" {extra}/>'
    ln = lambda x0, y0, x1, y1, cls: f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}" class="{cls}"/>'
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{esc(titulo)}">', f'<text x="{pad}" y="18" class="t">{esc(titulo)}</text>']
    if nivel == "PB":
        o.append(rect(0, PB_D, W, PA_D, "portal"))
        o.append(f'<text x="{X(4.5):.1f}" y="{Y(13.6):.1f}" class="r" text-anchor="middle">Portal techado · 9.0 × 3.0 m</text>')
        o.append(f'<text x="{X(4.5):.1f}" y="{Y(13.6)+12:.1f}" class="a" text-anchor="middle">comedor de exterior para 6 y asador</text>')
        bx0, by0, bx1, by1 = BODEGA_EXT
        o.append(rect(bx0, by0, bx1, by1, "muroE"))
        o.append(rect(bx0 + 0.1, by0 + 0.1, bx1 - 0.15, by1 - 0.1, "cuarto guardar"))
        o.append(f'<text x="{X((bx0+bx1)/2):.1f}" y="{Y((by0+by1)/2):.1f}" class="a" text-anchor="middle" transform="rotate(-90 {X((bx0+bx1)/2):.1f} {Y((by0+by1)/2):.1f})">bodega 1.45 × 2.0</text>')
        o.append(f'<text x="{X(9.85):.1f}" y="{Y(1.5):.1f}" class="a" text-anchor="middle" transform="rotate(-90 {X(9.85):.1f} {Y(1.5):.1f})">patio de servicio</text>')
    o.append(rect(0, 0, W, D, "muroE"))
    for c in (PB if nivel == "PB" else PA):
        x0, y0, x1, y1 = c["r"]
        o.append(rect(x0, y0, x1, y1, "cuarto " + c["tipo"]))
    for x0, y0, x1, y1 in ABIERTO[nivel] + APERTURAS[nivel]:
        o.append(rect(x0, y0, x1, y1, "cuarto"))
    # muebles
    for t, x0, y0, x1, y1, e in MUEBLES[nivel]:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if t == "R":
            o.append(rect(x0, y0, x1, y1, "mueble"))
            if e and (x1 - x0) * S > 22 and (y1 - y0) * S > 9: o.append(f'<text x="{X(cx):.1f}" y="{Y(cy)+3:.1f}" class="m" text-anchor="middle">{esc(e)}</text>')
        elif t == "cama":
            o.append(rect(x0, y0, x1, y1, "mueble"))
            if e in ("s", "n"):
                yh = y1 if e == "s" else y0; d_ = -1 if e == "s" else 1
                for xa, xb in ((x0 + 0.1, cx - 0.05), (cx + 0.05, x1 - 0.1)): o.append(rect(xa, min(yh + d_ * 0.1, yh + d_ * 0.45), xb, max(yh + d_ * 0.1, yh + d_ * 0.45), "almohada"))
                o.append(ln(x0, yh + d_ * 0.75, x1, yh + d_ * 0.75, "fino"))
            else:
                xh = x1 if e == "e" else x0; d_ = -1 if e == "e" else 1
                for ya, yb in ((y0 + 0.1, cy - 0.05), (cy + 0.05, y1 - 0.1)): o.append(rect(min(xh + d_ * 0.1, xh + d_ * 0.45), ya, max(xh + d_ * 0.1, xh + d_ * 0.45), yb, "almohada"))
                o.append(ln(xh + d_ * 0.75, y0, xh + d_ * 0.75, y1, "fino"))
        elif t == "closet":
            o.append(rect(x0, y0, x1, y1, "closet"))
            if x1 - x0 > y1 - y0: o.append(ln(x0 + 0.05, cy, x1 - 0.05, cy, "barra"))
            else: o.append(ln(cx, y0 + 0.05, cx, y1 - 0.05, "barra"))
        elif t in ("entrepanos", "alacena"):
            o.append(rect(x0, y0, x1, y1, "closet"))
            n = max(2, int(max(x1 - x0, y1 - y0) / 0.25))
            for k in range(1, n):
                if x1 - x0 > y1 - y0: xx = x0 + (x1 - x0) * k / n; o.append(ln(xx, y0, xx, y1, "fino"))
                else: yy = y0 + (y1 - y0) * k / n; o.append(ln(x0, yy, x1, yy, "fino"))
        elif t == "regadera":
            o.append(rect(x0, y0, x1, y1, "regadera"))
            o.append(ln(x0, y0, x1, y1, "fino")); o.append(ln(x0, y1, x1, y0, "fino"))
            o.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="2.5" class="mueble"/>')
        elif t == "wc":
            vert = e in ("s", "n")
            if vert:
                yt = y1 if e == "s" else y0; d_ = -1 if e == "s" else 1
                o.append(rect(x0, min(yt, yt + d_ * 0.2), x1, max(yt, yt + d_ * 0.2), "mueble"))
                o.append(f'<ellipse cx="{X(cx):.1f}" cy="{Y(yt + d_ * 0.42):.1f}" rx="{0.19*S:.1f}" ry="{0.24*S:.1f}" class="mueble"/>')
        elif t == "lavabo":
            o.append(rect(x0, y0, x1, y1, "mueble"))
            n = 2 if e.startswith("2") else 1
            for k in range(n):
                if e.endswith("v"): o.append(f'<ellipse cx="{X(cx):.1f}" cy="{Y(y0 + (y1 - y0) * (k + 0.5) / n):.1f}" rx="{0.17*S:.1f}" ry="{0.22*S:.1f}" class="fino2"/>')
                else: o.append(f'<ellipse cx="{X(x0 + (x1 - x0) * (k + 0.5) / n):.1f}" cy="{Y(cy):.1f}" rx="{min(0.22, (x1-x0)/2.6)*S:.1f}" ry="{0.15*S:.1f}" class="fino2"/>')
        elif t == "tarja":
            o.append(rect(x0, y0, x1, y1, "mueble"))
            o.append(rect(x0 + 0.08, y0 + 0.08, x1 - 0.08, y1 - 0.08, "fino2"))
        elif t == "estufa":
            o.append(rect(x0, y0, x1, y1, "mueble"))
            for dx in (0.3, 0.7):
                for dy in (0.25, 0.65):
                    o.append(f'<circle cx="{X(x0 + (x1 - x0) * dx):.1f}" cy="{Y(y0 + (y1 - y0) * dy):.1f}" r="{0.1*S:.1f}" class="fino2"/>')
        elif t == "refri":
            o.append(rect(x0, y0, x1, y1, "mueble")); o.append(f'<text x="{X(cx):.1f}" y="{Y(cy)+3:.1f}" class="m" text-anchor="middle">refri</text>')
        elif t == "lavadora":
            o.append(rect(x0, y0, x1, y1, "mueble")); o.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="{0.24*S:.1f}" class="fino2"/>')
        elif t == "cubierta":
            o.append(rect(x0, y0, x1, y1, "cubierta"))
        elif t == "tv":
            o.append(rect(x0, y0, x1, y1, "mueble")); o.append(rect(x0, y0 + 0.1, x0 + 0.08, y1 - 0.1, "negro"))
        elif t in ("sofa", "sillon"):
            o.append(rect(x0, y0, x1, y1, "mueble"))
            if e == "e": o.append(rect(x1 - 0.2, y0, x1, y1, "respaldo"))
            elif e == "w": o.append(rect(x0, y0, x0 + 0.2, y1, "respaldo"))
            elif e == "n": o.append(rect(x0, y1 - 0.2, x1, y1, "respaldo"))
            else: o.append(rect(x0, y0, x1, y0 + 0.2, "respaldo"))
        elif t == "mesa":
            n = int(e) // 2 - 1
            for k in range(n):
                yy = y0 + 0.25 + (y1 - y0 - 0.5) * (k + 0.5) / n
                o.append(rect(x0 - 0.5, yy - 0.22, x0 - 0.06, yy + 0.22, "silla")); o.append(rect(x1 + 0.06, yy - 0.22, x1 + 0.5, yy + 0.22, "silla"))
            o.append(rect(cx - 0.22, y1 + 0.06, cx + 0.22, y1 + 0.5, "silla")); o.append(rect(cx - 0.22, y0 - 0.5, cx + 0.22, y0 - 0.06, "silla"))
            o.append(rect(x0, y0, x1, y1, "mueble"))
        elif t == "escalera":
            n = round((y1 - y0) / HUELLA)
            for k in range(n + 1):
                yy = y1 - k * HUELLA
                if yy >= y0 - 0.01: o.append(ln(x0, yy, x1, yy, "esc"))
            if e == "pb":
                o.append(ln(x0, y0 + 0.3, x1, y0 + 0.05, "corte"))
                o.append(f'<text x="{X(cx):.1f}" y="{Y(y1 - 0.15)+3:.1f}" class="m" text-anchor="middle">sube</text>')
            else:
                o.append(ln(x1 + 0.03, y0, x1 + 0.03, y1 + 0.06, "barandal"))
                o.append(f'<text x="{X(cx):.1f}" y="{Y(y0 + 0.3)+3:.1f}" class="m" text-anchor="middle">baja</text>')
    # puertas
    for x, y, a, muro, bis, sent in PUERTAS[nivel]:
        if muro == "x":
            o.append(rect(x, y - 0.11, x + a, y + 0.11, "hueco"))
            hx = x + a * bis; fx = x + a * (1 - bis)
            o.append(ln(hx, y, hx, y + sent * a, "hoja"))
            sweep = 1 if (bis == 0) == (sent == 1) else 0
            o.append(f'<path d="M{X(fx):.1f},{Y(y):.1f} A{a*S:.1f},{a*S:.1f} 0 0 {sweep} {X(hx):.1f},{Y(y + sent * a):.1f}" class="arco"/>')
        else:
            o.append(rect(x - 0.11, y, x + 0.11, y + a, "hueco"))
            hy = y + a * bis; fy = y + a * (1 - bis)
            o.append(ln(x, hy, x + sent * a, hy, "hoja"))
            sweep = 0 if (bis == 0) == (sent == 1) else 1
            o.append(f'<path d="M{X(x):.1f},{Y(fy):.1f} A{a*S:.1f},{a*S:.1f} 0 0 {sweep} {X(x + sent * a):.1f},{Y(hy):.1f}" class="arco"/>')
    for a, b, muro, pos in VENTANAS[nivel]:
        if muro == "x":
            yy = pos - EXT / 2 if pos > 0 else EXT / 2
            o.append(rect(a, yy - EXT / 2, b, yy + EXT / 2, "ventana")); o.append(ln(a, yy, b, yy, "fino"))
        else:
            xx = pos - EXT / 2 if pos > 0 else EXT / 2
            o.append(rect(xx - EXT / 2, a, xx + EXT / 2, b, "ventana")); o.append(ln(xx, a, xx, b, "fino"))
    # rótulos
    for c in (PB if nivel == "PB" else PA):
        if not c["lbl"]: continue
        x0, y0, x1, y1 = c["r"]; lx, ly = c["lbl"]
        nombre = c["n"].replace("Clóset de paso", "Clóset").replace("Cuarto de blancos y bodega", "Blancos y bodega").replace("Clóset de blancos y limpieza", "Blancos")
        if (x1 - x0) < 1.2:
            o.append(f'<text x="{X(lx):.1f}" y="{Y(ly):.1f}" class="r" text-anchor="middle" transform="rotate(-90 {X(lx):.1f} {Y(ly):.1f})">{esc(nombre)}</text>')
            continue
        o.append(f'<text x="{X(lx):.1f}" y="{Y(ly):.1f}" class="r" text-anchor="middle">{esc(nombre)}</text>')
        o.append(f'<text x="{X(lx):.1f}" y="{Y(ly)+11:.1f}" class="a" text-anchor="middle">{x1-x0:.2f} × {y1-y0:.2f}</text>')
    o.append(f'<text x="{X(4.5):.1f}" y="{h-6:.1f}" class="a" text-anchor="middle">↓ calle · medidas libres en metros, a paño interior de muro</text>')
    o.append("</svg>")
    return "\n".join(o)

def tabla(nivel):
    filas = []
    for c in (PB if nivel == "PB" else PA):
        if not c["cabe"]: continue
        x0, y0, x1, y1 = c["r"]
        filas.append(f'<tr><td><b>{esc(c["n"])}</b></td><td>{x1-x0:.2f} × {y1-y0:.2f}</td><td>{(x1-x0)*(y1-y0):.1f}</td><td class="izq">{esc(c["cabe"])}</td></tr>')
    return '<div class="scroll"><table class="cuartos"><tr><th>Espacio</th><th>Medida libre (m)</th><th>m²</th><th class="izq">Qué cabe</th></tr>' + "".join(filas) + "</table></div>"

GUARDADO = [
    ("Clósets de paso de las recámaras 1, 2 y 3", "2.55 + 2.55 + 2.80 m de clóset de 60 cm, entre la recámara y el baño: la ropa no queda a la vista de la cama."),
    ("Vestidor de la principal", "6.2 m lineales en dos lados, de entrar."),
    ("Lavandería y blancos (planta baja)", "Se lava, se dobla y se guarda en el mismo cuarto: 2.0 m de entrepaños de piso a techo."),
    ("Cuarto de blancos y bodega (planta alta)", "7.3 m², entrepaños en U de 6.9 m lineales: sábanas, maletas, ropa de temporada."),
    ("Clóset de blancos y limpieza (planta alta)", "Junto a las recámaras: toallas a la mano y la aspiradora arriba."),
    ("Bodega bajo la escalera", "2.1 m de fondo, con puerta al pasillo."),
    ("Alacena de piso a techo", "1.20 m en la cocina, más 10 m de gabinetes."),
    ("Bodega de servicio", "1.45 × 2.0 m en el patio lateral: herramienta, bicicletas, hielera, adornos de Navidad. No ensucia la casa."),
]
