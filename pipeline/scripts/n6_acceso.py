"""N6 · plano a escala del acceso (el cálculo de hora pico vive en n6_acceso_calc.py). Lo usa sitio.py."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from n6_acceso_calc import res, CARRILES, CASETA_V, ISLA_V0, RETORNO, ANCHO, CAP, CASAS, AUTO_M
man, tar = res["mañana (7 a 8)"], res["tarde (6 a 7 pm)"]

def plano(S=9):
    u0, u1 = ANCHO[0] - 52, ANCHO[1] + 55          # súper a la izquierda, estacionamiento de visitas a la derecha
    v0, v1 = -32, CASETA_V + 32
    pad = 20
    w, h = (u1 - u0) * S + 2 * pad, (v1 - v0) * S + 2 * pad
    X = lambda u: pad + (u - u0) * S; Y = lambda v: pad + (v1 - v) * S
    R = lambda a, b, c, d, cls, extra="": f'<rect x="{X(a):.1f}" y="{Y(d):.1f}" width="{(b-a)*S:.1f}" height="{(d-c)*S:.1f}" class="{cls}" {extra}/>'
    T = lambda u, v, t, cls="a", anc="middle", rot=None: (f'<text x="{X(u):.1f}" y="{Y(v):.1f}" class="{cls}" text-anchor="{anc}"' + (f' transform="rotate({rot} {X(u):.1f} {Y(v):.1f})"' if rot else "") + f'>{t}</text>')
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Plano de la entrada">',
         '<defs><marker id="fl" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0L10,5L0,10z" fill="#000"/></marker></defs>']
    o.append(R(u0, u1, v0, -18, "calzada")); o.append(T((u0 + u1) / 2, -26, "CALZADA JOSÉ VASCONCELOS (derecho de vía por confirmar)", "r"))
    o.append(R(u0, u1, -18, 0, "franja")); o.append(T(u0 + 2, -9, "franja entre la calzada y el terreno", "a", "start"))
    o.append(R(u0, u1, 0, 5, "pista")); o.append(T(u0 + 2, 1.5, "pista para correr", "a", "start"))
    o.append(R(ANCHO[0] - 48, ANCHO[0] - 4, 8, 30, "super")); o.append(T(ANCHO[0] - 26, 20, "MINI SÚPER", "r inv"))
    o.append(T(ANCHO[0] - 26, 15.5, "abre a la calle", "a inv"))
    o.append(R(ANCHO[1] + 4, ANCHO[1] + 51, 8, 28, "estac")); o.append(T(ANCHO[1] + 27.5, 19, "estacionamiento", "a")); o.append(T(ANCHO[1] + 27.5, 15.5, "visitas y súper", "a"))
    # carriles
    o.append(R(ANCHO[0], ANCHO[1], -18, CASETA_V + 25, "asfalto"))
    for n, a, b, t in CARRILES:
        cx = (a + b) / 2
        if t == "isla":
            o.append(R(a, b, ISLA_V0, RETORNO[0], "isla")); o.append(R(a, b, RETORNO[1], CASETA_V + 6, "isla"))
            o.append(R(a + 0.3, b - 0.3, CASETA_V - 2.5, CASETA_V + 2.5, "caseta"))
        elif t == "peaton":
            o.append(R(a, b, -18, CASETA_V + 25, "banq")); o.append(T(cx, CASETA_V - 18, "puerta peatonal", "a", rot=-90))
        else:
            o.append(f'<line x1="{X(a+0.2):.1f}" y1="{Y(CASETA_V):.1f}" x2="{X(b-0.4):.1f}" y2="{Y(CASETA_V):.1f}" class="pluma"/>')
            y1, y2 = (8, 20) if t == "entra" else (20, 8)
            o.append(f'<line x1="{X(cx):.1f}" y1="{Y(y1):.1f}" x2="{X(cx):.1f}" y2="{Y(y2):.1f}" class="fl" marker-end="url(#fl)"/>')
            o.append(T(cx + 0.55, CASETA_V - 24, n.replace("Entrada residentes", "residentes").replace("Entrada visitas", "visitas").replace("Salida ", "sale "), "c", rot=-90))
    for (n1, a1, b1, t1), (n2, a2, b2, t2) in zip(CARRILES[:-1], CARRILES[1:]):
        if t1 == t2 and t1 in ("entra", "sale"):
            o.append(f'<line x1="{X(b1):.1f}" y1="{Y(-16):.1f}" x2="{X(b1):.1f}" y2="{Y(CASETA_V+10):.1f}" class="divc"/>')
    # filas en hora pico (95 %) frente a las plumas
    for n, a, b, t in CARRILES:
        if n.startswith("Entrada residentes"): L = tar["entrada_residentes_2_carriles"]["fila95_m"]
        elif n.startswith("Entrada visitas"): L = tar["entrada_visitas_2_carriles"]["fila95_m"]
        else: continue
        o.append(R(a + 0.6, b - 0.6, CASETA_V - L, CASETA_V - 0.5, "fila"))
    o.append(f'<path d="M{X(9):.1f},{Y(RETORNO[0]+2):.1f} C{X(9):.1f},{Y(RETORNO[1]+4):.1f} {X(-12):.1f},{Y(RETORNO[1]+4):.1f} {X(-12):.1f},{Y(RETORNO[0]):.1f}" class="ret" marker-end="url(#fl)"/>')
    o.append(T(-1.5, RETORNO[1] + 7.5, "retorno", "a"))
    o.append(T(ANCHO[1] + 3, CASETA_V + 1, f"plumas y casetas a {CASETA_V} m", "a", "start"))
    o.append(T(ANCHO[1] + 3, CASETA_V - 30, "en gris: fila de la", "a", "start")); o.append(T(ANCHO[1] + 3, CASETA_V - 32.2, "hora pico (95 %)", "a", "start"))
    o.append(T(ANCHO[1] + 3, CASETA_V + 16, "↑ al fraccionamiento:", "a", "start")); o.append(T(ANCHO[1] + 3, CASETA_V + 13.8, "calle de 2 carriles", "a", "start"))
    o.append(f'<line x1="{X(ANCHO[0]-1.5):.1f}" y1="{Y(0):.1f}" x2="{X(ANCHO[0]-1.5):.1f}" y2="{Y(CASETA_V):.1f}" class="cota"/>')
    o.append(T(ANCHO[0] - 2.4, CASETA_V - 12, f"{CASETA_V} m", "a", rot=-90))
    o.append(f'<line x1="{X(ANCHO[0]):.1f}" y1="{Y(CASETA_V+20):.1f}" x2="{X(ANCHO[1]):.1f}" y2="{Y(CASETA_V+20):.1f}" class="cota"/>')
    o.append(T((ANCHO[0] + ANCHO[1]) / 2, CASETA_V + 21.5, f"{ANCHO[1]-ANCHO[0]:.0f} m", "a"))
    o.append("</svg>")
    return "\n".join(o)

def fila(t, d):
    if d.get("espera_s") is None: return f"<tr><td>{t}</td><td>{d['rho']*100:.0f} %</td><td colspan=2><b>se satura</b>: la fila no deja de crecer</td></tr>"
    return f"<tr><td>{t}</td><td>{d['rho']*100:.0f} %</td><td>{d['espera_s']} s</td><td>{d['fila95']} autos · {d['fila95_m']} m</td></tr>"
