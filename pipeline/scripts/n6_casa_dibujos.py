"""N6 · Modelo Nogal: dibujos (emplazamiento con el sol, corte, azotea, fachada posterior, 9 fachadas y cuadra). Lo usa sitio.py."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
LOTE_W, LOTE_D = 12.7, 25.8          # lote muestra (cerca del promedio de los lotes)
CASA_W = 9.0                         # deja 1.85 m libres a cada lado (1.5 m en lotes de 12.0 m)
FRENTE = 5.5                         # cochera para 2 autos
RUMBO_FONDO = {"norte": 329.0, "sur": 149.0}   # hacia dónde mira el jardín según el lado de la calle
SOL = {"ver_med": 87.9, "inv_med": 41.0, "equ_med": 64.4, "ver_puesta": 296.2, "inv_puesta": 243.8, "ver_salida": 63.8, "inv_salida": 116.2}
import n6_casa_planta as CP
PB_D, PA_D = CP.PB_D, CP.PA_D        # planta baja cerrada y planta alta (vuela 3 m sobre el portal)
m2_pb, m2_pa = CASA_W * PB_D, CASA_W * PA_D
bx0, by0, bx1, by1 = CP.BODEGA_EXT
m2_bodega = (bx1 - bx0) * (by1 - by0)
jardin = LOTE_W * LOTE_D - CASA_W * PA_D - 5.85 * FRENTE - (bx1 - bx0) * 5.2   # sin casa, cochera, bodega ni patio de servicio (incluye portal y jardín frontal)
sala_m2 = sum((c["r"][2] - c["r"][0]) * (c["r"][3] - c["r"][1]) for c in CP.PB if c["n"] in ("Sala", "Comedor", "Cocina"))

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;")

# ---------- emplazamiento con sol ----------
def flecha(cx, cy, rumbo_rel, L, cls, texto):
    a = math.radians(rumbo_rel)
    x1, y1 = cx + math.sin(a) * L, cy - math.cos(a) * L
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{cx:.1f}" y2="{cy:.1f}" class="{cls}" marker-end="url(#pf)"/>'
            f'<text x="{x1 + math.sin(a)*12:.1f}" y="{y1 - math.cos(a)*12 + 4:.1f}" class="a" text-anchor="middle">{texto}</text>')

def emplazamiento(lado, S=13):
    B = RUMBO_FONDO[lado]                      # rumbo del jardín (pantalla: arriba)
    pad = 150; w, h = LOTE_W * S + 2 * pad, LOTE_D * S + 2 * pad
    X = lambda x: pad + x * S; Y = lambda y: pad + (LOTE_D - y) * S
    hx = (LOTE_W - CASA_W) / 2
    tit = "Lote del lado norte de la calle · jardín al NNO" if lado == "norte" else "Lote del lado sur de la calle · jardín al SSE"
    o = [f'<svg viewBox="0 0 {w:.0f} {h+20:.0f}" role="img" aria-label="{tit}">',
         '<defs><marker id="pf" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="currentColor"/></marker></defs>',
         f'<text x="10" y="18" class="t">{tit}</text>']
    o.append(f'<rect x="{X(0)}" y="{Y(LOTE_D)}" width="{LOTE_W*S}" height="{LOTE_D*S}" class="lote"/>')
    o.append(f'<rect x="{X(-3)}" y="{Y(0)}" width="{(LOTE_W+6)*S}" height="{0.9*S}" class="calle"/>')
    o.append(f'<text x="{X(LOTE_W/2)}" y="{Y(0)+0.9*S+13}" class="a" text-anchor="middle">calle</text>')
    xc = LOTE_W - 0.3 - 5.85
    o.append(f'<rect x="{X(xc)}" y="{Y(FRENTE)}" width="{5.85*S}" height="{(FRENTE-0.3)*S}" class="cochera"/>')
    o.append(f'<text x="{X(xc + 2.9)}" y="{Y(2.8)}" class="a" text-anchor="middle">cochera</text>')
    o.append(f'<rect x="{X(hx + CASA_W)}" y="{Y(FRENTE + 3.0)}" width="{(LOTE_W - hx - CASA_W)*S}" height="{3.0*S}" class="cochera"/>')
    o.append(f'<rect x="{X(hx + bx0)}" y="{Y(FRENTE + by1)}" width="{(bx1 - bx0)*S}" height="{(by1 - by0)*S}" class="casa"/>')
    o.append(f'<text x="{X(LOTE_W) + 6}" y="{Y(FRENTE + 1.5) + 4}" class="a">patio de servicio</text>')
    o.append(f'<text x="{X(LOTE_W) + 6}" y="{Y(FRENTE + 4.1) + 4}" class="a">bodega</text>')
    o.append(f'<text x="{X(hx / 2)}" y="{Y(2.8)}" class="a" text-anchor="middle">jardín</text>')
    o.append(f'<rect x="{X(hx)}" y="{Y(FRENTE+PA_D)}" width="{CASA_W*S}" height="{PA_D*S}" class="casa"/>')
    o.append(f'<rect x="{X(hx)}" y="{Y(FRENTE+PA_D)}" width="{CASA_W*S}" height="{3*S}" class="portal2"/>')
    o.append(f'<text x="{X(LOTE_W/2)}" y="{Y(FRENTE+5)}" class="r inv" text-anchor="middle">CASA</text>')
    o.append(f'<text x="{X(LOTE_W/2)}" y="{Y(FRENTE+PA_D-1.6)}" class="a" text-anchor="middle">portal</text>')
    o.append(f'<text x="{X(LOTE_W/2)}" y="{Y(FRENTE+PA_D+3.4)}" class="r" text-anchor="middle">JARDÍN</text>')
    for tx, ty in ((0, 0.8), (LOTE_W, 0.8), (0, 13.4), (LOTE_W, 13.4), (0, 25.8), (LOTE_W, 25.8)):
        o.append(f'<circle cx="{X(tx)}" cy="{Y(ty)}" r="{4.3*S}" class="copa"/><circle cx="{X(tx)}" cy="{Y(ty)}" r="4" class="tronco"/>')
    o.append(f'<text x="{X(LOTE_W)+6}" y="{Y(13.4)+4}" class="a">nogal</text>')
    # norte y sol (rumbo relativo a "arriba" = B)
    cx, cy = X(LOTE_W) + 62, Y(LOTE_D) - 45
    a = math.radians((0 - B) % 360)
    o.append(f'<circle cx="{cx}" cy="{cy}" r="22" class="rosa"/>'
             f'<line x1="{cx - math.sin(a)*18:.1f}" y1="{cy + math.cos(a)*18:.1f}" x2="{cx + math.sin(a)*18:.1f}" y2="{cy - math.cos(a)*18:.1f}" class="norte" marker-end="url(#pf)"/>'
             f'<text x="{cx + math.sin(a)*32:.1f}" y="{cy - math.cos(a)*32 + 4:.1f}" class="r" text-anchor="middle">N</text>')
    hc = (X(LOTE_W/2), Y(FRENTE + PA_D / 2))
    o.append(flecha(*hc, (180 - B) % 360, 205, "sol", "sol de invierno, mediodía"))
    o.append(flecha(*hc, (SOL["ver_puesta"] - B) % 360, 205, "sol2", "sol de verano, tarde"))
    o.append(f'<text x="10" y="{h+14}" class="a">Medidas en metros. Lote 12.7 × 25.8 m. Los nogales quedan en los linderos.</text>')
    o.append("</svg>")
    return "\n".join(o)

# ---------- corte ----------
def corte(S=22):
    pad = 30; w, h = (LOTE_D + 9) * S + 2 * pad, 16 * S
    gy = h - 40
    X = lambda y: pad + (y + 2) * S; Z = lambda z: gy - z * S
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Corte con el sol">', f'<text x="{pad}" y="18" class="t">Corte: el portal da sombra de marzo a octubre y deja entrar el sol de invierno</text>']
    o.append(f'<line x1="{X(-2)}" y1="{gy}" x2="{X(LOTE_D+2)}" y2="{gy}" class="suelo"/>')
    f0 = FRENTE
    o.append(f'<rect x="{X(f0)}" y="{Z(6.6)}" width="{PA_D*S}" height="{3.3*S}" class="corteM"/>')      # planta alta
    o.append(f'<rect x="{X(f0)}" y="{Z(3.3)}" width="{PB_D*S}" height="{3.3*S}" class="corteM"/>')      # planta baja
    o.append(f'<text x="{X(f0+PA_D/2)}" y="{Z(5)}" class="r" text-anchor="middle">Planta alta: 3 recámaras con baño</text>')
    o.append(f'<text x="{X(f0+PB_D/2)}" y="{Z(1.6)}" class="r" text-anchor="middle">Planta baja: recámara, cocina, sala-comedor</text>')
    gx = f0 + PB_D                                   # cristal hacia el portal
    o.append(f'<line x1="{X(gx)}" y1="{Z(0)}" x2="{X(gx)}" y2="{Z(2.7)}" class="vidrioC"/>')
    o.append(f'<text x="{X(f0+PB_D+1.5)}" y="{Z(1.3)}" class="a" text-anchor="middle">portal</text>')
    edge = (f0 + PA_D, 3.0)
    for alt, cls, t in ((SOL["inv_med"], "sol", f"invierno {SOL['inv_med']:.0f}°: entra"), (SOL["equ_med"], "sol2", f"marzo y sept. {SOL['equ_med']:.0f}°: sombra"), (SOL["ver_med"], "sol2", f"verano {SOL['ver_med']:.0f}°: sombra")):
        a = math.radians(alt)
        L = 6.0
        x1, z1 = edge[0] + L * math.cos(a), edge[1] + L * math.sin(a)
        zg = edge[1] - (edge[0] - gx) * math.tan(a)   # dónde pega en el cristal
        x2, z2 = (gx, max(zg, 0)) if zg > 0 else (edge[0] - edge[1] / math.tan(a), 0)
        o.append(f'<line x1="{X(x1)}" y1="{Z(z1)}" x2="{X(x2)}" y2="{Z(z2)}" class="{cls}" marker-end="url(#pf2)"/>')
        o.append(f'<text x="{X(x1)-4}" y="{Z(z1)-4}" class="a" text-anchor="end">{t}</text>')
    o.insert(1, '<defs><marker id="pf2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="currentColor"/></marker></defs>')
    # nogal al fondo
    tx = LOTE_D + 1.5
    o.append(f'<line x1="{X(tx)}" y1="{Z(0)}" x2="{X(tx)}" y2="{Z(4)}" class="tronco2"/><ellipse cx="{X(tx)}" cy="{Z(8)}" rx="{4.3*S}" ry="{4*S}" class="copaC"/>')
    o.append(f'<text x="{X(tx)}" y="{Z(8)}" class="a" text-anchor="middle">nogal</text><text x="{X(tx)}" y="{Z(8)+12}" class="a" text-anchor="middle">sombra en verano,</text><text x="{X(tx)}" y="{Z(8)+24}" class="a" text-anchor="middle">sin hojas en invierno</text>')
    o.append(f'<text x="{X(f0/2)}" y="{gy+16}" class="a" text-anchor="middle">calle · cochera</text><text x="{X(f0+PA_D+3.4)}" y="{gy+16}" class="a" text-anchor="middle">jardín</text>')
    o.append("</svg>")
    return "\n".join(o)

# ---------- fachadas ----------
from n6_fachadas import NOMBRES, SEQ, slug, fachada_de
S = 30                                     # unidades de dibujo por metro (las mismas en todas las fachadas y en la cuadra)
ESTUCO, BLANCO, NEGRO, VIDRIO, SOMBRA = "#f5f5f5", "#ffffff", "#161616", "#2c2c2c", "rgba(0,0,0,0.17)"
DEFS = f"""<svg width="0" height="0" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true"><defs>
<pattern id="p-cantera" width="36" height="27" patternUnits="userSpaceOnUse"><rect width="36" height="27" fill="#e2e2e2"/><path d="M0 13.5H36M0 27H36M0.35 0V13.5M18 13.5V27" stroke="#9a9a9a" stroke-width="0.7" fill="none"/></pattern>
<pattern id="p-ladrillo" width="21.6" height="7.2" patternUnits="userSpaceOnUse"><rect width="21.6" height="7.2" fill="#b3b3b3"/><path d="M0 3.6H21.6M0 7.2H21.6M0.3 0V3.6M10.8 0V3.6M5.4 3.6V7.2M16.2 3.6V7.2" stroke="#f2f2f2" stroke-width="0.7" fill="none"/></pattern>
<pattern id="p-soldado" width="3.6" height="8" patternUnits="userSpaceOnUse"><rect width="3.6" height="8" fill="#b0b0b0"/><path d="M0.3 0V8" stroke="#f2f2f2" stroke-width="0.6"/></pattern>
<pattern id="p-madera" width="3.6" height="10" patternUnits="userSpaceOnUse"><rect width="3.6" height="10" fill="#9b9b9b"/><path d="M0.4 0V10" stroke="#5c5c5c" stroke-width="0.9"/></pattern>
<pattern id="p-viga" width="20" height="3" patternUnits="userSpaceOnUse"><rect width="20" height="3" fill="#585858"/><path d="M0 1.5H12M6 0.4H20" stroke="#3a3a3a" stroke-width="0.5"/></pattern>
<pattern id="p-concreto" width="36" height="18" patternUnits="userSpaceOnUse"><rect width="36" height="18" fill="#d5d5d5"/><path d="M0 9H36M0 18H36" stroke="#bdbdbd" stroke-width="0.6"/><circle cx="9" cy="4.5" r="0.9" fill="#8a8a8a"/><circle cx="27" cy="4.5" r="0.9" fill="#8a8a8a"/></pattern>
<pattern id="p-celosia" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#eeeeee"/><circle cx="4.5" cy="4.5" r="3" fill="#3a3a3a"/></pattern>
<pattern id="p-petatillo" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#c4c4c4"/><rect x="2.2" y="2.2" width="4.6" height="4.6" fill="#333"/></pattern>
<pattern id="p-lamas" width="10" height="4.5" patternUnits="userSpaceOnUse"><rect width="10" height="2.8" fill="#dcdcdc"/><path d="M0 2.8H10" stroke="#6e6e6e" stroke-width="0.6"/></pattern>
</defs></svg>"""

class Dib:
    """Dibujo en metros: x a lo ancho de la fachada (0 = esquina izquierda de la casa), z hacia arriba (0 = piso)."""
    def __init__(self, ox, ztop): self.o, self.ox, self.zt = [], ox, ztop
    def X(self, x): return (x + self.ox) * S
    def Z(self, z): return (self.zt - z) * S
    def r(self, x0, x1, z0, z1, fill, stroke=None, sw=1.0):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.o.append(f'<rect x="{self.X(x0):.1f}" y="{self.Z(z1):.1f}" width="{(x1-x0)*S:.1f}" height="{(z1-z0)*S:.1f}" fill="{fill}"{st}/>')
    def ln(self, x0, z0, x1, z1, color="#000", sw=1.0):
        self.o.append(f'<line x1="{self.X(x0):.1f}" y1="{self.Z(z0):.1f}" x2="{self.X(x1):.1f}" y2="{self.Z(z1):.1f}" stroke="{color}" stroke-width="{sw}"/>')
    def c(self, x, z, rad, fill):
        self.o.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Z(z):.1f}" r="{rad*S:.1f}" fill="{fill}"/>')
    def vidrio(self, x0, x1, z0, z1, cols=1, rows=1, marco=NEGRO):
        self.r(x0, x1, z0, z1, VIDRIO, marco, 1.4)
        self.o.append(f'<polygon points="{self.X(x0):.1f},{self.Z(z1):.1f} {self.X(x0+(x1-x0)*0.45):.1f},{self.Z(z1):.1f} {self.X(x0):.1f},{self.Z(z1-(z1-z0)*0.55):.1f}" fill="rgba(255,255,255,0.09)"/>')
        for k in range(1, cols): self.ln(x0 + (x1 - x0) * k / cols, z0, x0 + (x1 - x0) * k / cols, z1, "#8c8c8c", 1.1)
        for k in range(1, rows): self.ln(x0, z0 + (z1 - z0) * k / rows, x1, z0 + (z1 - z0) * k / rows, "#8c8c8c", 1.1)
    def sombra(self, x0, x1, z0, z1): self.r(x0, x1, z0, z1, SOMBRA)
    def suelo(self, x0, x1): self.ln(x0, 0, x1, 0, "#000", 2.2)

# huecos (iguales en las 9): recámara 1, puerta, cocina; recámara 2, escalera, recámara 3
W1, PU, W2 = (0.6, 3.3), (4.25, 5.35), (6.3, 8.4)
W3, ES, W4 = (0.6, 3.3), (4.35, 5.25), (6.1, 8.6)

def puerta_madera(d, x0=PU[0], x1=PU[1], z1=2.6, marco=NEGRO):
    d.r(x0 - 0.1, x1 + 0.1, 0, z1 + 0.1, marco); d.r(x0, x1, 0, z1, "url(#p-madera)", "#000", 0.8); d.ln(x1 - 0.18, 0.9, x1 - 0.18, 1.5, "#fff", 2)

def f_cantera(d):
    d.r(0, 9, 0, 6.95, ESTUCO, "#000", 1.6)
    d.r(0, 9, 0, 3.3, "url(#p-cantera)", "#000", 1.2)
    d.r(-0.06, 9.06, 3.25, 3.47, "url(#p-cantera)", "#000", 0.8)                     # imposta de cantera
    d.sombra(0, 9, 6.55, 6.75); d.r(-0.15, 9.15, 6.75, 7.0, "url(#p-cantera)", "#000", 1)   # cornisa
    for (a, b), z0, z1, cols in ((W3, 4.2, 5.9, 2), (W4, 4.2, 5.9, 2)):
        d.r(a - 0.18, b + 0.18, z0 - 0.25, z1 + 0.18, "url(#p-cantera)", "#000", 1)
        d.vidrio(a, b, z0, z1, cols); d.sombra(a - 0.18, b + 0.18, z0 - 0.4, z0 - 0.25)
    d.r(ES[0] - 0.15, ES[1] + 0.15, 3.65, 6.3, "url(#p-cantera)", "#000", 1); d.vidrio(*ES, 3.8, 6.15, 1, 3)
    for (a, b), z0, z1 in ((W1, 0.9, 2.5), (W2, 1.1, 2.5)):
        d.vidrio(a, b, z0, z1, 2); d.sombra(a, b, z1 - 0.14, z1); d.r(a - 0.1, b + 0.1, z0 - 0.1, z0, "#d0d0d0", "#000", 0.6)
    d.r(4.05, 5.55, 0, 2.85, NEGRO); puerta_madera(d, z1=2.65, marco=NEGRO)

def f_celosia(d):
    d.r(0, 9, 0, 6.9, ESTUCO, "#000", 1.6); d.r(0, 9, 0, 0.35, "#cfcfcf", "#000", 0.8)
    d.vidrio(*W1, 0.9, 2.6, 2); d.vidrio(*W2, 1.1, 2.6); puerta_madera(d)
    d.sombra(0.4, 5.7, 3.38, 3.55)
    d.r(0.25, 5.55, 3.55, 6.45, "url(#p-celosia)", "#000", 1.4)                          # celosía de barro sobre recámara y escalera
    d.r(5.95, 8.75, 4.0, 6.1, BLANCO, "#000", 1.2); d.vidrio(*W4, 4.15, 5.95, 2)
    d.sombra(W4[0], W4[1], 5.78, 5.95); d.sombra(W4[0], W4[0] + 0.15, 4.15, 5.78)
    d.ln(0, 6.9, 9, 6.9, "#000", 2.5)

def f_marco(d):
    d.r(0, 9, 0, 3.3, "url(#p-madera)", "#000", 1.4)
    d.vidrio(*W1, 0.5, 2.7, 3); d.vidrio(*W2, 1.0, 2.7, 2)
    d.r(PU[0] - 0.05, PU[1] + 0.05, 0, 2.75, NEGRO); d.ln(PU[1] - 0.2, 0.8, PU[1] - 0.2, 1.9, "#bbb", 2)
    d.sombra(0, 9, 2.85, 3.3)
    d.r(-0.25, 9.25, 3.3, 7.05, NEGRO)                                                 # caja con marco negro
    d.r(0.15, 8.85, 3.65, 6.7, ESTUCO); d.sombra(0.15, 8.85, 6.42, 6.7); d.sombra(0.15, 0.38, 3.65, 6.42)
    d.vidrio(*W3, 4.1, 6.0, 2); d.vidrio(*ES, 3.85, 6.25); d.vidrio(*W4, 4.1, 6.0, 2)

def f_duela(d):
    d.r(0, 9, 0, 3.3, ESTUCO, "#000", 1.6)
    d.r(0, 9, 3.3, 6.85, "url(#p-madera)", "#000", 1.4); d.r(-0.05, 9.05, 6.85, 7.0, BLANCO, "#000", 1)
    d.r(0, 9, 3.22, 3.36, NEGRO)
    d.vidrio(*W3, 4.1, 6.0, 2); d.r(1.85, 3.6, 4.0, 6.1, "url(#p-madera)", "#000", 1.2); d.sombra(3.6, 3.72, 4.0, 6.1)   # postigo corrido
    d.vidrio(*W4, 4.1, 6.0, 2); d.r(5.9, 7.7, 4.0, 6.1, "url(#p-madera)", "#000", 1.2); d.sombra(7.7, 7.82, 4.0, 6.1)
    d.vidrio(*ES, 3.7, 6.3)
    for k in range(1, 6): d.ln(ES[0] + k * 0.15, 3.7, ES[0] + k * 0.15, 6.3, "#9b9b9b", 2.2)
    d.vidrio(*W1, 0.6, 2.7, 3); d.vidrio(*W2, 1.1, 2.7, 2); puerta_madera(d, z1=2.7)

def f_ladrillo(d):
    d.r(0, 9, 0, 6.95, "url(#p-ladrillo)", "#000", 1.6)
    d.r(0, 9, 3.3, 3.5, "#e0e0e0", "#000", 0.8); d.r(-0.05, 9.05, 6.8, 6.98, "#e0e0e0", "#000", 0.8)
    for (a, b), z0, z1, cols in ((W1, 0.9, 2.5, 2), (W2, 1.1, 2.5, 1), (W3, 4.1, 5.8, 2), (W4, 4.1, 5.8, 2)):
        d.vidrio(a, b, z0, z1, cols); d.r(a - 0.12, b + 0.12, z1, z1 + 0.27, "url(#p-soldado)", "#000", 0.6)
        d.r(a - 0.06, b + 0.06, z0 - 0.08, z0, "#e0e0e0", "#000", 0.5)
    d.r(ES[0] - 0.1, ES[1] + 0.1, 3.75, 6.55, "url(#p-petatillo)", "#000", 1)            # celosía de ladrillo (petatillo)
    d.r(PU[0], PU[1], 0, 2.6, NEGRO); d.r(PU[1] - 0.3, PU[1] - 0.15, 0.2, 2.4, "#6a6a6a")
    d.r(PU[0] - 0.12, PU[1] + 0.12, 2.6, 2.87, "url(#p-soldado)", "#000", 0.6)

def f_hacienda(d):
    d.r(0, 9, 0, 6.95, BLANCO, "#000", 1.8); d.r(0, 9, 0, 0.45, "#d6d6d6", "#000", 0.8)    # rodapié
    for (a, b), z0, z1, rej in ((W1, 0.9, 2.4, True), (W2, 1.1, 2.4, True), (W3, 4.1, 5.7, False), (W4, 4.1, 5.7, False)):
        d.vidrio(a, b, z0, z1, 2, 2); d.sombra(a, b, z1 - 0.2, z1); d.sombra(a, a + 0.2, z0, z1 - 0.2)    # muro grueso: hueco hondo
        d.r(a - 0.4, b + 0.4, z1, z1 + 0.22, "url(#p-viga)", "#000", 0.6)                 # cerramiento de madera
        d.r(a - 0.05, b + 0.05, z0 - 0.08, z0, "#d6d6d6", "#000", 0.5)
        if rej:
            for k in range(1, int((b - a) / 0.16)): d.ln(a + k * 0.16, z0, a + k * 0.16, z1, "#000", 1.3)
            d.ln(a, (z0 + z1) / 2, b, (z0 + z1) / 2, "#000", 1.3)
    d.vidrio(*ES, 3.9, 5.9, 1, 3); d.sombra(ES[0], ES[1], 5.7, 5.9); d.r(ES[0] - 0.3, ES[1] + 0.3, 5.9, 6.1, "url(#p-viga)", "#000", 0.6)
    d.r(PU[0] - 0.15, PU[1] + 0.15, 0, 2.75, "url(#p-madera)", "#000", 1); d.ln(4.8, 0, 4.8, 2.75, "#000", 1)
    for x in (4.45, 4.63, 4.97, 5.15):                                                  # clavos de la puerta
        for j in range(4): d.c(x, 0.5 + j * 0.6, 0.035, "#000")
    d.r(PU[0] - 0.5, PU[1] + 0.5, 2.75, 2.98, "url(#p-viga)", "#000", 0.6)
    for k in range(15): d.c(0.3 + k * 0.6, 6.5, 0.09, "#4a4a4a")                       # rollizos (puntas de las vigas)
    for g in (1.95, 7.35):                                                             # gárgolas
        d.r(g - 0.12, g + 0.12, 6.6, 6.78, "#3a3a3a"); d.ln(g, 6.6, g, 5.95, "#9a9a9a", 0.8)

def f_horizonte(d):
    d.r(0, 9, 0, 6.6, ESTUCO, "#000", 1.6)
    d.r(0.3, 8.7, 4.0, 6.25, "#8a8a8a", "#000", 1)                                     # franja corrida
    d.vidrio(*W3, 4.15, 6.1, 3); d.vidrio(*ES, 4.15, 6.1); d.vidrio(*W4, 4.15, 6.1, 3)
    d.sombra(0, 9, 2.95, 3.2); d.sombra(0, 9, 6.3, 6.6)
    d.r(-0.6, 9.6, 3.2, 3.45, NEGRO); d.r(-0.6, 9.6, 6.6, 6.95, NEGRO)                 # losas voladas 60 cm
    d.vidrio(*W1, 0.45, 2.85, 3); d.vidrio(*W2, 1.2, 2.85, 2); puerta_madera(d, z1=2.85)
    d.r(5.75, 9.35, 0, 0.6, "url(#p-concreto)", "#000", 1)                              # jardinera
    for k in range(7): d.c(6.0 + k * 0.5, 0.75, 0.17, "#7a7a7a")

def f_lamas(d):
    d.r(0, 9, 0, 6.9, ESTUCO, "#000", 1.6); d.r(0, 9, 0, 0.3, "#cfcfcf", "#000", 0.8)
    d.sombra(0.4, 8.95, 3.45, 3.65)
    d.r(0.25, 8.75, 3.65, 6.5, NEGRO); d.r(0.35, 8.65, 3.75, 6.4, VIDRIO)
    d.r(0.35, 8.65, 3.75, 6.4, "url(#p-lamas)")                                         # piel de lamas de aluminio
    for x in (3.0, 5.7): d.ln(x, 3.75, x, 6.4, NEGRO, 2)
    d.vidrio(*W1, 0.8, 2.6, 2); d.vidrio(*W2, 1.1, 2.6)
    d.r(PU[0] - 0.1, PU[1] + 0.1, 0, 3.0, NEGRO); d.r(PU[0], PU[1], 0, 2.9, "url(#p-madera)", "#000", 0.8); d.ln(PU[0] + 0.2, 0.7, PU[0] + 0.2, 2.2, "#fff", 2)

def f_concreto(d):
    d.r(0, 9, 0, 6.95, "url(#p-concreto)", "#000", 1.6)
    d.sombra(0.42, 3.72, 3.7, 3.9)
    d.r(0.3, 3.6, 3.9, 6.25, BLANCO, "#000", 1.4)                                       # cajón blanco
    d.vidrio(*W3, 4.2, 5.95); d.sombra(W3[0], W3[1], 5.8, 5.95); d.sombra(W3[0], W3[0] + 0.14, 4.2, 5.8)
    d.r(4.15, 5.45, 0, 6.5, NEGRO)                                                      # ranura de piso a techo
    d.r(PU[0], PU[1], 0, 2.6, "url(#p-madera)", "#000", 0.8); d.vidrio(*ES, 3.0, 6.35, 1, 1, "#555")
    d.vidrio(*W4, 4.2, 5.9, 1, 1, "#555"); d.vidrio(*W1, 1.0, 2.5, 1, 1, "#555"); d.vidrio(*W2, 1.1, 2.4, 1, 1, "#555")

DIBUJO = dict(zip(NOMBRES, [f_cantera, f_celosia, f_marco, f_duela, f_ladrillo, f_hacienda, f_horizonte, f_lamas, f_concreto]))
TEXTO = {
    "Cantera": "Planta baja de cantera, planta alta lisa y ventanas enmarcadas en cantera, con cornisa. Mexicana y sobria.",
    "Celosía": "Una celosía de barro tapa la recámara y la escalera: de día filtra el sol y de noche la casa brilla a través de ella.",
    "Marco": "La planta alta es una caja con marco negro que vuela sobre una planta baja forrada de madera.",
    "Duela": "Planta alta forrada de duela de madera, con postigos corredizos que se abren o se cierran según el sol. Planta baja blanca.",
    "Ladrillo": "Ladrillo aparente, cerramientos de ladrillo parado y una celosía de petatillo en la escalera.",
    "Hacienda": "Muros blancos gruesos, vigas de madera, herrería, rollizos y gárgolas. Lagunera de siempre.",
    "Horizonte": "Dos losas que vuelan 60 cm y una franja de ventanas corrida en la planta alta. Se ve larga y baja.",
    "Lamas": "Una piel de lamas de aluminio cubre toda la planta alta: da sombra y privacidad sin perder la vista.",
    "Concreto": "Concreto aparente con huella de cimbra, un cajón blanco en la ventana principal y una ranura de piso a techo en la entrada.",
}
SOMBRA_DE = {"Cantera": "ventanas remetidas en su marco", "Celosía": "la celosía", "Marco": "la caja, que vuela", "Duela": "los postigos",
             "Ladrillo": "el hueco hondo del ladrillo", "Hacienda": "el muro grueso y las vigas", "Horizonte": "las losas voladas",
             "Lamas": "las lamas", "Concreto": "el cajón y la ranura"}

def patio(d):
    """Costado derecho: bodega de servicio detrás de la reja de madera del patio de servicio."""
    d.r(9.0, 10.7, 0, 2.6, "#e4e4e4", "#000", 1.0)
    d.r(9.08, 10.62, 0, 2.15, "url(#p-madera)", "#000", 1.0)

def fachada(nombre):
    d = Dib(0.9, 7.5)
    patio(d); DIBUJO[nombre](d); d.suelo(-0.8, 11.2)
    w, h = (9 + 0.9 + 2.2) * S, 7.85 * S
    return f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Fachada {nombre}">' + "".join(d.o) + "</svg>"

def cuadra(n=6, calle_i=0, lado_norte=True, calle="Álamo"):
    """Elevación de una acera: n lotes seguidos, con los nogales en los linderos."""
    zt, mx = 11.8, 0.6
    tipos = [fachada_de(k, lado_norte, calle_i) for k in range(n)]
    o = []
    for k, t in enumerate(tipos):
        d = Dib(mx + k * LOTE_W + (LOTE_W - CASA_W) / 2, zt); patio(d); DIBUJO[t](d); o += d.o
        num = 2 * k + (1 if lado_norte else 2)
        o.append(f'<text x="{(mx + k * LOTE_W + LOTE_W / 2) * S:.0f}" y="{(zt + 0.75) * S:.0f}" font-size="26" font-weight="700" fill="#000" text-anchor="middle">{calle} {num} · {t}</text>')
    d = Dib(mx, zt)
    for k in range(n + 1):                                   # nogales en los linderos, delante de las casas
        x = k * LOTE_W
        d.ln(x, 0, x, 3.4, "#000", 4)
        d.o.append(f'<ellipse cx="{d.X(x):.1f}" cy="{d.Z(7.2):.1f}" rx="{4.4*S:.1f}" ry="{3.6*S:.1f}" fill="rgba(0,0,0,0.04)" stroke="#000" stroke-width="1" stroke-dasharray="5 4"/>')
    d.suelo(-mx, n * LOTE_W + mx)
    o += d.o
    w, h = (n * LOTE_W + 2 * mx) * S, (zt + 1.3) * S
    return f'<svg class="cuadra" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Una cuadra de {calle}">' + "".join(o) + "</svg>"

# ---------- planta de azotea ----------
def azotea(S=34):
    W, D = CASA_W, PA_D
    pad = 26; w, h = (W + 2.2) * S + 2 * pad, D * S + 2 * pad + 22
    X = lambda x: pad + x * S; Y = lambda y: pad + 22 + (D - y) * S
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Planta de azotea">', f'<text x="{pad}" y="16" class="t">Planta de azotea</text>']
    o.append(f'<rect x="{X(0)}" y="{Y(D)}" width="{W*S}" height="{D*S}" class="cuarto"/>')
    o.append(f'<rect x="{X(0.15)}" y="{Y(D-0.15)}" width="{(W-0.3)*S}" height="{(D-0.3)*S}" class="pretil"/>')
    bx0, by0, bx1, by1 = CP.BODEGA_EXT
    o.append(f'<rect x="{X(bx0)}" y="{Y(by1)}" width="{(bx1-bx0)*S}" height="{(by1-by0)*S}" class="cuarto"/><rect x="{X(bx0+0.12)}" y="{Y(by1-0.12)}" width="{(bx1-bx0-0.24)*S}" height="{(by1-by0-0.24)*S}" class="pretil"/>')
    o.append(f'<text x="{X((bx0+bx1)/2)}" y="{Y((by0+by1)/2)+3}" class="m" text-anchor="middle">bodega</text>')
    # pendientes: 2 % hacia las bajadas de las esquinas del frente y del fondo (al jardín, no a la calle)
    for (x, y, dx, dy) in ((1.0, 1.0, 1, 1), (8.0, 1.0, -1, 1), (1.0, D - 1.0, 1, -1), (8.0, D - 1.0, -1, -1)):
        o.append(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{0.12*S}" class="bajada"/>')
        o.append(f'<line x1="{X(x+dx*2.6)}" y1="{Y(y+dy*2.6)}" x2="{X(x+dx*0.4)}" y2="{Y(y+dy*0.4)}" class="pend" marker-end="url(#pf2)"/>')
    o.append(f'<text x="{X(4.5)}" y="{Y(2.4)}" class="a" text-anchor="middle">pendiente 2 % a 4 bajadas · descargan al jardín, no a la calle</text>')
    # paneles solares: 12 de 1.1 × 1.8 en 2 filas, en la mitad que da al sur (se decide por lote)
    for i in range(6):
        for j in range(2):
            o.append(f'<rect x="{X(1.2 + i * 1.15)}" y="{Y(10.6 - j * 2.0)}" width="{1.05*S}" height="{1.85*S}" class="panel"/>')
    o.append(f'<text x="{X(4.5)}" y="{Y(11.1)}" class="r" text-anchor="middle">12 paneles solares · 5.5 kW</text>')
    o.append(f'<text x="{X(4.5)}" y="{Y(11.1)+11}" class="a" text-anchor="middle">en la mitad que mira al sur, inclinados 20°</text>')
    # calentador solar, tinaco, condensadoras, escalera marina
    o.append(f'<rect x="{X(6.4)}" y="{Y(5.6)}" width="{2.0*S}" height="{1.2*S}" class="mueble"/><text x="{X(7.4)}" y="{Y(5.0)+3}" class="m" text-anchor="middle">calentador solar</text>')
    o.append(f'<circle cx="{X(7.6)}" cy="{Y(3.2)}" r="{0.55*S}" class="mueble"/><text x="{X(7.6)}" y="{Y(3.2)+3}" class="m" text-anchor="middle">tinaco</text>')
    for k, (x, y) in enumerate(((1.0, 6.6), (2.0, 6.6), (1.0, 13.3), (2.0, 13.3), (7.9, 13.3))):
        o.append(f'<rect x="{X(x)}" y="{Y(y)}" width="{0.8*S}" height="{0.35*S}" class="mueble"/>')
    o.append(f'<text x="{X(1.9)}" y="{Y(5.9)+3}" class="m" text-anchor="middle">condensadoras</text>')
    o.append(f'<rect x="{X(4.35)}" y="{Y(1.9)}" width="{0.9*S}" height="{0.6*S}" class="mueble"/><text x="{X(4.8)}" y="{Y(2.05)+3}" class="m" text-anchor="middle">tapa</text>')
    o.append(f'<text x="{X(4.8)}" y="{Y(0.6)+3}" class="a" text-anchor="middle">escalera marina desde el patio</text>')
    o.append(f'<line x1="{X(0)}" y1="{Y(3.0)}" x2="{X(W)}" y2="{Y(3.0)}" class="div"/><text x="{X(0.3)}" y="{Y(3.25)}" class="a">↑ frente · ↓ sobre el portal</text>')
    o.append(f'<text x="{X(4.5)}" y="{h-6}" class="a" text-anchor="middle">↓ calle · losa con aislante y acabado blanco reflejante</text>')
    o.append("</svg>")
    return "\n".join(o)

# ---------- fachada posterior (al jardín): igual en las 9 ----------
def fachada_posterior():
    d = Dib(0.9, 7.5)
    d.r(0, 9, 0, 3.0, "#f5f5f5", "#000", 1.2)                                           # portal: fondo (muro de la sala con cancel)
    d.vidrio(0.4, 8.6, 0.05, 2.7, 4)                                                       # cancel corredizo de 4 hojas
    d.r(0, 9, 3.0, 3.35, "#1a1a1a")                                                        # losa de la planta alta (vuela sobre el portal)
    d.r(0, 9, 3.35, 6.95, ESTUCO, "#000", 1.4)
    for x in (0.9, 8.1): d.r(x - 0.15, x + 0.15, 0, 3.0, "#444")                            # 2 columnas delgadas al borde del portal
    d.vidrio(0.6, 4.6, 4.0, 6.0, 2); d.sombra(0.6, 4.6, 5.8, 6.0); d.r(0.4, 4.8, 6.0, 6.2, NEGRO)   # recámara principal, con alero
    d.vidrio(6.0, 7.2, 5.2, 6.1); d.vidrio(7.6, 8.6, 5.2, 6.1)                              # baño principal: ventanas altas
    d.r(-0.3, 9.3, 6.95, 7.2, NEGRO)                                                       # pretil
    d.ln(-0.9, 0, 9.9, 0, "#000", 2.2)
    for x in (-0.6, 9.6):                                                                  # nogales de los linderos
        d.ln(x, 0, x, 3.2, "#000", 4); d.o.append(f'<ellipse cx="{d.X(x):.1f}" cy="{d.Z(6.0):.1f}" rx="{3.2*S:.1f}" ry="{2.9*S:.1f}" fill="rgba(0,0,0,0.04)" stroke="#000" stroke-width="1" stroke-dasharray="5 4"/>')
    d.o.append(f'<text x="{d.X(4.5):.1f}" y="{d.Z(1.4):.1f}" font-size="11" fill="#555" text-anchor="middle">portal · cancel de 8.2 m a la sala y el comedor</text>')
    w, h = (9 + 1.8) * S, 7.85 * S
    return f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Fachada posterior, al jardín">' + "".join(d.o) + "</svg>"
