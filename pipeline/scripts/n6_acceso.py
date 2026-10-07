"""N6 · plano a escala del acceso y alzado desde la calzada (el cálculo de hora pico vive en n6_acceso_calc.py). Lo usa sitio.py."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from n6_acceso_calc import res, CARRILES, CASETA_V, ISLA_V0, RETORNO, ANCHO, CAP, CASAS, AUTO_M
man, tar = res["mañana (7 a 8)"], res["tarde (6 a 7 pm)"]
PORTICO_V, PORTICO_H = 8, 5.5           # el pórtico cruza los carriles a 8 m del límite, con 5.5 m libres
MESA_V = CASETA_V + 16                  # mesa reductora después de las plumas
REJA = 40                               # metros de reja a cada lado del acceso
DESACEL, BAHIA, ACEL = 60, 40, 40       # carriles en la calzada
ZONAS = [("0", "Calzada", "carril de desaceleración de 60 m por la derecha, bahía de vuelta izquierda de 40 m, carril de aceleración de 40 m a la salida; semáforo o glorieta por pedir al municipio"),
         ("1", "Umbral (0 a 12 m)", "muro de identidad con el nombre en letras de acero, 40 m de reja a cada lado para ver los nogales, pórtico de 5.5 m libres sobre los carriles, poste de 9 m en cada orilla"),
         ("2", "Plaza (0 a 60 m, fuera de las plumas)", "mini súper que abre a la calle, estacionamiento de visitas y clientes, lockers de paquetería, acopio de basura, puerta peatonal con torniquete, nogales de la huerta"),
         ("3", "Carriles y filas (12 a 60 m)", "2 carriles de residentes con tag, 2 de visitas (uno de ellos para proveedores y mudanzas), 2 de salida; islas con jardín del desierto; retorno a los 34 m para el que no pasa"),
         ("4", "Control (60 m)", "caseta principal de 3 × 6 m entre residentes y visitas, caseta de salida de 2 × 3 m, 6 plumas rápidas, lectores RFID a 10 m, cámara de placas en cada carril, interfón y QR, bolardos"),
         ("5", "Adentro (60 a 85 m)", "mesa reductora a 30 km/h, la calle vuelve a 2 carriles y entra al bulevar; planta de emergencia y cuarto de tableros detrás de la caseta")]

def plano(S=9):
    u0, u1 = ANCHO[0] - 62, ANCHO[1] + 66          # súper a la izquierda, estacionamiento de visitas a la derecha
    v0, v1 = -34, CASETA_V + 32
    pad = 20
    w, h = (u1 - u0) * S + 2 * pad, (v1 - v0) * S + 2 * pad
    X = lambda u: pad + (u - u0) * S; Y = lambda v: pad + (v1 - v) * S
    R = lambda a, b, c, d, cls, extra="": f'<rect x="{X(a):.1f}" y="{Y(d):.1f}" width="{(b-a)*S:.1f}" height="{(d-c)*S:.1f}" class="{cls}" {extra}/>'
    T = lambda u, v, t, cls="a", anc="middle", rot=None: (f'<text x="{X(u):.1f}" y="{Y(v):.1f}" class="{cls}" text-anchor="{anc}"' + (f' transform="rotate({rot} {X(u):.1f} {Y(v):.1f})"' if rot else "") + f'>{t}</text>')
    LN = lambda a, b, c, d, cls, extra="": f'<line x1="{X(a):.1f}" y1="{Y(b):.1f}" x2="{X(c):.1f}" y2="{Y(d):.1f}" class="{cls}" {extra}/>'
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Plano de la entrada">',
         '<defs><marker id="fl" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0L10,5L0,10z" fill="#000"/></marker>'
         '<pattern id="mesa" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,6 L6,0" stroke="#000" stroke-width="1"/></pattern></defs>']
    # calzada con sus carriles
    o.append(R(u0, u1, v0, -18, "calzada")); o.append(T((u0 + u1) / 2, -32, "CALZADA JOSÉ VASCONCELOS (derecho de vía por confirmar)", "r"))
    o.append(R(ANCHO[1], ANCHO[1] + DESACEL, -22, -18, "carrilc")); o.append(T(ANCHO[1] + DESACEL / 2, -20.6, f"carril de desaceleración · {DESACEL} m", "c"))
    o.append(R(ANCHO[0] - BAHIA, ANCHO[0] + 4, -26, -22, "carrilc")); o.append(T(ANCHO[0] - BAHIA / 2 + 2, -24.6, f"bahía de vuelta izquierda · {BAHIA} m", "c"))
    o.append(R(ANCHO[0] - ACEL, ANCHO[0], -22, -18, "carrilc")); o.append(T(ANCHO[0] - ACEL / 2, -20.6, f"aceleración · {ACEL} m", "c"))
    o.append(LN(ANCHO[1] + DESACEL + 2, -20, ANCHO[1] + 8, -20, "fl", 'marker-end="url(#fl)"')); o.append(LN(ANCHO[0] - 2, -20, ANCHO[0] - ACEL + 4, -20, "fl", 'marker-end="url(#fl)"'))
    o.append(T(u0 + 2, -28.5, "← a Torreón", "a", "start")); o.append(T(u1 - 2, -28.5, "al oriente →", "a", "end"))
    o.append(R(u0, u1, -18, 0, "franja")); o.append(T(u0 + 2, -9, "franja entre la calzada y el terreno: banqueta y nogales", "a", "start"))
    # barda, reja y nombre
    o.append(T(ANCHO[0] - REJA / 2, 2.2, f"reja {REJA} m", "c")); o.append(T(ANCHO[1] + REJA / 2, 2.2, f"reja {REJA} m", "c")); o.append(T(u0 + 2, 2.2, "muro de identidad 3.0 m", "c", "start")); o.append(T(u1 - 2, 2.2, "muro de identidad 3.0 m", "c", "end"))
    o.append(R(u0, u1, 0, 5, "pista")); o.append(T(u0 + 2, 1.5, "pista para correr", "a", "start"))
    o.append(LN(u0, 0.5, ANCHO[0] - REJA, 0.5, "barda")); o.append(LN(ANCHO[0] - REJA, 0.5, ANCHO[0], 0.5, "reja")); o.append(LN(ANCHO[1], 0.5, ANCHO[1] + REJA, 0.5, "reja")); o.append(LN(ANCHO[1] + REJA, 0.5, u1, 0.5, "barda"))
    o.append(R(ANCHO[0] - REJA - 15, ANCHO[0] - REJA - 1, -0.6, 0.5, "nombre")); o.append(T(ANCHO[0] - REJA - 8, -3.4, "LA NOGALERA (letras de acero)", "c"))
    o.append(R(ANCHO[0] - 48, ANCHO[0] - 4, 8, 30, "super")); o.append(T(ANCHO[0] - 26, 20, "MINI SÚPER", "r inv")); o.append(T(ANCHO[0] - 26, 15.5, "abre a la calle", "a inv"))
    o.append(R(ANCHO[1] + 4, ANCHO[1] + 51, 8, 28, "estac")); o.append(T(ANCHO[1] + 27.5, 19, "estacionamiento", "a")); o.append(T(ANCHO[1] + 27.5, 15.5, "visitas y súper · 40 cajones", "a"))
    o.append(R(ANCHO[1] + 53, ANCHO[1] + 63, 8, 16, "acopio")); o.append(T(ANCHO[1] + 58, 11.3, "acopio", "c"))
    o.append(R(ANCHO[1] + 4, ANCHO[1] + 10, 37, 40, "lockers")); o.append(T(ANCHO[1] + 12, 38, "lockers de paquetería", "c", "start"))
    for cu, cv in ((ANCHO[0] - 30, 40), (ANCHO[0] - 14, 48), (ANCHO[0] - 42, 54), (ANCHO[1] + 20, 40), (ANCHO[1] + 36, 48), (ANCHO[1] + 10, 56), (ANCHO[1] + 50, 56)):
        o.append(f'<circle cx="{X(cu):.1f}" cy="{Y(cv):.1f}" r="{3.2*S:.1f}" class="nogalp"/>')
    o.append(T(ANCHO[0] - 26, 72, "nogales de la huerta, jardín del desierto", "c"))
    # carriles
    o.append(R(ANCHO[0], ANCHO[1], -18, CASETA_V + 25, "asfalto"))
    for n, a, b, t in CARRILES:
        cx = (a + b) / 2
        if t == "isla":
            o.append(R(a, b, ISLA_V0, RETORNO[0], "isla")); o.append(R(a, b, RETORNO[1], CASETA_V + 6, "isla"))
            if "visitas" in n: o.append(R(a + 0.2, b - 0.2, CASETA_V - 3, CASETA_V + 3, "caseta")); o.append(T(cx, CASETA_V + 7.5, "caseta 3 × 6", "c"))
            else: o.append(R(a + 0.5, b - 0.5, CASETA_V - 1.5, CASETA_V + 1.5, "caseta")); o.append(T(cx, CASETA_V + 7.5, "caseta 2 × 3", "c"))
            for bv in (CASETA_V - 5, CASETA_V + 5): o.append(f'<circle cx="{X(a + 0.4):.1f}" cy="{Y(bv):.1f}" r="2" class="bolardo"/><circle cx="{X(b - 0.4):.1f}" cy="{Y(bv):.1f}" r="2" class="bolardo"/>')
        elif t == "peaton":
            o.append(R(a, b, -18, CASETA_V + 25, "banq")); o.append(T(cx, CASETA_V - 20, "puerta peatonal y bicis", "a", rot=-90))
            o.append(R(a + 0.6, b - 0.6, CASETA_V - 1, CASETA_V + 1, "torn")); o.append(T(cx + 0.2, CASETA_V + 4, "torniquete", "c", rot=-90))
        else:
            o.append(LN(a + 0.2, CASETA_V, b - 0.4, CASETA_V, "pluma"))
            y1, y2 = (8, 20) if t == "entra" else (20, 8)
            o.append(LN(cx, y1, cx, y2, "fl", 'marker-end="url(#fl)"'))
            lab = n.replace("Entrada residentes", "residentes").replace("Entrada visitas 2", "proveedores").replace("Entrada visitas", "visitas").replace("Salida ", "sale ")
            o.append(T(cx + 0.55, CASETA_V - 24, lab, "c", rot=-90))
            o.append(f'<circle cx="{X(cx):.1f}" cy="{Y(CASETA_V - 2):.1f}" r="2.4" class="cam"/>')
            if t == "entra": o.append(LN(a + 0.6, CASETA_V - 10, b - 0.6, CASETA_V - 10, "rfid"))
    o.append(T(ANCHO[1] + 3, CASETA_V - 10.5, "← lector RFID a 10 m", "c", "start")); o.append(T(ANCHO[1] + 3, CASETA_V - 3.5, "← cámara de placas en cada carril", "c", "start"))
    for (n1, a1, b1, t1), (n2, a2, b2, t2) in zip(CARRILES[:-1], CARRILES[1:]):
        if t1 == t2 and t1 in ("entra", "sale"): o.append(LN(b1, -16, b1, CASETA_V + 10, "divc"))
    for n, a, b, t in CARRILES:
        if n.startswith("Entrada residentes"): L = tar["entrada_residentes_2_carriles"]["fila95_m"]
        elif n.startswith("Entrada visitas"): L = tar["entrada_visitas_2_carriles"]["fila95_m"]
        else: continue
        o.append(R(a + 0.6, b - 0.6, CASETA_V - L, CASETA_V - 0.5, "fila"))
    o.append(f'<path d="M{X(9):.1f},{Y(RETORNO[0]+2):.1f} C{X(9):.1f},{Y(RETORNO[1]+4):.1f} {X(-12):.1f},{Y(RETORNO[1]+4):.1f} {X(-12):.1f},{Y(RETORNO[0]):.1f}" class="ret" marker-end="url(#fl)"/>')
    o.append(T(-1.5, RETORNO[1] + 7.5, "retorno", "a"))
    # pórtico y mesa
    o.append(LN(ANCHO[0] - 1, PORTICO_V, ANCHO[1] + 1, PORTICO_V, "portico")); o.append(T(ANCHO[1] + 3, PORTICO_V - 2.2, f"pórtico · {PORTICO_H} m libres", "a", "start"))
    o.append(R(-5.5, 5.5, MESA_V, MESA_V + 3.5, "mesar")); o.append(T(7, MESA_V + 1, "mesa reductora · 30 km/h", "a", "start"))
    o.append(T(ANCHO[1] + 3, CASETA_V + 1, f"plumas y casetas a {CASETA_V} m", "a", "start"))
    o.append(T(ANCHO[1] + 3, CASETA_V - 30, "en gris: fila de la", "a", "start")); o.append(T(ANCHO[1] + 3, CASETA_V - 32.2, "hora pico (95 %)", "a", "start"))
    o.append(T(ANCHO[1] + 3, CASETA_V + 26, "↑ al bulevar: calle de 2 carriles", "a", "start"))
    o.append(R(ANCHO[0] - 10, ANCHO[0] - 2, CASETA_V + 5, CASETA_V + 9, "lockers")); o.append(T(ANCHO[0] - 6, CASETA_V + 13.4, "planta de emergencia", "c")); o.append(T(ANCHO[0] - 6, CASETA_V + 11, "y tableros", "c"))
    o.append(LN(ANCHO[0] - 1.5, 0, ANCHO[0] - 1.5, CASETA_V, "cota")); o.append(T(ANCHO[0] - 2.4, CASETA_V - 12, f"{CASETA_V} m", "a", rot=-90))
    o.append(LN(ANCHO[0], CASETA_V + 20, ANCHO[1], CASETA_V + 20, "cota")); o.append(T((ANCHO[0] + ANCHO[1]) / 2, CASETA_V + 21.5, f"{ANCHO[1]-ANCHO[0]:.0f} m", "a"))
    o.append("</svg>")
    return "\n".join(o)

def alzado(S=18):
    """Vista desde la calzada: muro de identidad, reja, pórtico, casetas al fondo y nogales."""
    u0, u1 = ANCHO[0] - 58, ANCHO[1] + 58; z0, z1 = -1.2, 12.5; pad = 18
    w, h = (u1 - u0) * S + 2 * pad, (z1 - z0) * S + 2 * pad + 40
    X = lambda u: pad + (u - u0) * S; Z = lambda z: pad + 20 + (z1 - z) * S
    R = lambda a, b, c, d, cls, extra="": f'<rect x="{X(a):.1f}" y="{Z(d):.1f}" width="{(b-a)*S:.1f}" height="{(d-c)*S:.1f}" class="{cls}" {extra}/>'
    T = lambda u, z, t, cls="a", anc="middle": f'<text x="{X(u):.1f}" y="{Z(z):.1f}" class="{cls}" text-anchor="{anc}">{t}</text>'
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Alzado del acceso desde la calzada">']
    o.append(T((u0 + u1) / 2, z1 + 0.6, "Alzado desde la calzada", "r"))
    # nogales al fondo
    for cu in range(int(u0) + 6, int(u1), 13):
        o.append(f'<line x1="{X(cu):.1f}" y1="{Z(0):.1f}" x2="{X(cu):.1f}" y2="{Z(4.2):.1f}" class="tronco"/><ellipse cx="{X(cu):.1f}" cy="{Z(7.2):.1f}" rx="{5.5*S:.1f}" ry="{3.4*S:.1f}" class="copa"/>')
    # casetas al fondo (a 60 m: más chicas por la distancia, se dibujan a escala sin reducir)
    for a, b, hh in ((-7.0, -4.0, 3.2), (2.6, 4.6, 3.4)):
        o.append(R(a + 0.3, b - 0.3, 0, hh, "casetaA")); o.append(R(a + 0.6, b - 0.6, 1.0, hh - 0.5, "vidrioA"))
    o.append(T(3.6, 3.9, "casetas (a 60 m)", "c"))
    # muro de identidad y reja
    o.append(R(u0, ANCHO[0] - REJA, 0, 3.0, "muroA")); o.append(R(ANCHO[1] + REJA, u1, 0, 3.0, "muroA"))
    for cu in list(range(int(u0), int(ANCHO[0] - REJA), 6)) + list(range(int(ANCHO[1] + REJA), int(u1), 6)):
        o.append(R(cu, cu + 0.4, 0, 3.2, "pilastra"))
    o.append(R(u0, ANCHO[0] - REJA, 3.0, 3.15, "remate")); o.append(R(ANCHO[1] + REJA, u1, 3.0, 3.15, "remate"))
    for a, b in ((ANCHO[0] - REJA, ANCHO[0]), (ANCHO[1], ANCHO[1] + REJA)):
        o.append(R(a, b, 0, 0.6, "muroA"))
        for cu in range(int(a * 10), int(b * 10), 4): o.append(f'<line x1="{X(cu/10):.1f}" y1="{Z(0.6):.1f}" x2="{X(cu/10):.1f}" y2="{Z(3.0):.1f}" class="barrote"/>')
        o.append(R(a, b, 2.95, 3.05, "remate"))
    for a, b in ((u0, ANCHO[0] - REJA), (ANCHO[1] + REJA, u1)):
        for k in range(6): o.append(f'<line x1="{X(a):.1f}" y1="{Z(3.15 + 0.1 * (k + 1)):.1f}" x2="{X(b):.1f}" y2="{Z(3.15 + 0.1 * (k + 1)):.1f}" class="cerca"/>')
    o.append(T(u0 + 2, 4.3, "cerca electrificada · 6 hilos", "c", "start"))
    # nombre
    o.append(T(ANCHO[0] - REJA - 9, 1.75, "LA NOGALERA", "nombreA"))
    # pórtico: dos pilares y trabe
    for cu in (ANCHO[0] - 1.0, ANCHO[1] + 0.2): o.append(R(cu, cu + 0.8, 0, PORTICO_H + 0.9, "pilar"))
    o.append(R(ANCHO[0] - 1.0, ANCHO[1] + 1.0, PORTICO_H, PORTICO_H + 0.9, "trabe"))
    o.append(T((ANCHO[0] + ANCHO[1]) / 2, PORTICO_H + 0.6, "LA NOGALERA", "trabeT"))
    # plumas (a 60 m) y postes de 9 m
    for n, a, b, t in CARRILES:
        if t in ("entra", "sale"): o.append(f'<line x1="{X(a + 0.3):.1f}" y1="{Z(1.0):.1f}" x2="{X(b - 0.3):.1f}" y2="{Z(1.0):.1f}" class="plumaA"/>')
    for cu in (ANCHO[0] - 1.2, ANCHO[1] - 1.5):
        o.append(f'<line x1="{X(cu):.1f}" y1="{Z(0):.1f}" x2="{X(cu):.1f}" y2="{Z(9):.1f}" class="poste"/><rect x="{X(cu) - 4:.1f}" y="{Z(9) - 3:.1f}" width="8" height="3" class="lum"/>')
    o.append(T(ANCHO[1] - 1.5, 9.8, "poste 9 m", "c"))
    # cotas
    o.append(f'<line x1="{X(ANCHO[0]):.1f}" y1="{Z(PORTICO_H + 2.2):.1f}" x2="{X(ANCHO[1]):.1f}" y2="{Z(PORTICO_H + 2.2):.1f}" class="cota"/>'); o.append(T((ANCHO[0] + ANCHO[1]) / 2, PORTICO_H + 2.6, f"{ANCHO[1] - ANCHO[0]:.0f} m", "a"))
    o.append(f'<line x1="{X(ANCHO[1] - 2):.1f}" y1="{Z(0):.1f}" x2="{X(ANCHO[1] - 2):.1f}" y2="{Z(PORTICO_H):.1f}" class="cota"/>'); o.append(T(ANCHO[1] - 3, 1.7, f"{PORTICO_H} m libres", "a", "end"))
    o.append(f'<line x1="{X(u1 - 3):.1f}" y1="{Z(0):.1f}" x2="{X(u1 - 3):.1f}" y2="{Z(3.0):.1f}" class="cota"/>'); o.append(T(u1 - 4, 1.5, "3.0 m", "a", "end"))
    o.append(R(u0, u1, z0, 0, "tierra")); o.append(T(u0 + 2, -0.7, "calzada · banqueta · nogales de la franja", "a", "start"))
    o.append("</svg>")
    return "\n".join(o)

def fila(t, d):
    if d.get("espera_s") is None: return f"<tr><td>{t}</td><td>{d['rho']*100:.0f} %</td><td colspan=2><b>se satura</b>: la fila no deja de crecer</td></tr>"
    return f"<tr><td>{t}</td><td>{d['rho']*100:.0f} %</td><td>{d['espera_s']} s</td><td>{d['fila95']} autos · {d['fila95_m']} m</td></tr>"
