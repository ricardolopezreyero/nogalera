"""N6 · precio del terreno y aportación en fideicomiso → public/n6/terreno.html
El dueño aporta el terreno a un fideicomiso y cobra un porcentaje de cada venta, conforme se cobra.
Porcentaje justo: el que deja al dueño y al proyecto con la MISMA ganancia, en pesos de hoy, frente a una venta de contado.
  dueño:    X·VP(ventas, r_dueño) − P      (lo que gana contra vender hoy a P)
  proyecto: P − X·VP(ventas, r_proyecto)    (lo que ahorra contra comprar hoy a P)
  iguales → X = 2P / (VP_dueño + VP_proyecto)
El proyecto descuenta más alto que el dueño (su dinero cuesta más), por eso los dos ganan con el fideicomiso."""
import json, os, sys
D = sys.argv[1] if len(sys.argv) > 1 else "../public/n6"
fc = json.load(open(f"{D}/confort.geojson")); r = fc["resumen"]
A, PM2 = fc["bruto_m2"], r["terreno_m2_precio"]
P, S, C, LOTES = PM2 * A, r["venta"], r["costo"], r["lotes"]
R_DUENO, R_PROY = 0.10, 0.18          # tasas anuales: dueño (inversión segura y algo más), proyecto (crédito puente y capital)
INICIO, RITMO = 9, 25                 # mes en que empiezan las ventas (licencia) y lotes por mes

def vp(tasa, ritmo=RITMO, inicio=INICIO, monto=S):
    """Valor de hoy de las ventas, repartidas parejo a `ritmo` lotes por mes desde `inicio`."""
    n = LOTES / ritmo; m = monto / n; i = (1 + tasa) ** (1 / 12) - 1; t, total = 0, 0.0
    while t < n:
        f = min(1, n - t); total += m * f / (1 + i) ** (inicio + t + f / 2); t += 1
    return total
VPd, VPp = vp(R_DUENO), vp(R_PROY)
X_piso, X_techo = P / VPd, P / VPp
X = 2 * P / (VPd + VPp)
gana = X * VPd - P
cobra = X * S
meses = LOTES / RITMO
margen_fid = S * (1 - X) - (C - P)
costo_fid = C - P
print(f"P={P:,.0f} VPd={VPd:,.0f} VPp={VPp:,.0f} piso={X_piso:.4f} eq={X:.4f} techo={X_techo:.4f} cobra={cobra:,.0f} ({cobra/A:,.0f}/m²) gana={gana:,.0f} margen={margen_fid:,.0f}")

fmt = lambda x: f"{x:,.0f}"
mill = lambda x: f"${x/1e6:,.1f} millones"
pct = lambda x, d=1: f"{100*x:.{d}f} %"
filas_precio = "".join(
    f"<tr{' class=\"eq\"' if p == PM2 else ''}><td>${fmt(p)}/m²</td><td>{mill(p*A)}</td><td>{pct(2*p*A/(VPd+VPp), 2)}</td><td>{mill(2*p*A/(VPd+VPp)*S)}</td></tr>"
    for p in (450, 550, PM2, 750, 850))
def fila_ritmo(rt):
    v = vp(R_DUENO, rt); hoy = X * v
    return f"<tr{' class=\"eq\"' if rt == RITMO else ''}><td>{rt} lotes al mes ({LOTES/rt/12:.1f} años)</td><td>{mill(X*S)}</td><td>{mill(hoy)}</td><td>${fmt(hoy/A)}/m²</td></tr>"
filas_ritmo = "".join(fila_ritmo(rt) for rt in (15, 20, 25, 35))

HTML = f"""<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>N6 · Terreno</title>
<meta name="description" content="N6: precio del terreno y porcentaje justo si el dueño lo aporta en fideicomiso.">
<link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../style.css">
<style>
  html, body {{ height: auto; }} body {{ background: var(--papel); }}
  .doc {{ max-width: 52rem; margin: 0 auto; padding: 1rem 1rem 3rem; }}
  .nav {{ display: flex; flex-wrap: wrap; border: 1px solid var(--linea); margin-bottom: 1rem; max-width: 48rem; }}
  .nav a {{ flex: 1 0 auto; text-align: center; padding: 0.35rem 0.5rem; text-decoration: none; font-size: 0.8125rem; border-right: 1px solid var(--linea); }}
  .nav a:last-child {{ border-right: 0; }} .nav a[aria-current="page"] {{ background: var(--tinta); color: var(--papel); }}
  h1 {{ font-size: 1.75rem; margin: 0 0 0.25rem; }} h1 span {{ display: block; font-size: 0.9375rem; font-weight: 400; color: var(--gris); }}
  h2 {{ font-size: 1.0625rem; margin: 2rem 0 0.5rem; border-top: 1px solid var(--linea); padding-top: 0.75rem; }}
  p, ul {{ max-width: 46rem; }} li {{ margin: 0.3rem 0; }}
  .datos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: 0.75rem 1rem; margin: 1rem 0; }}
  .datos div {{ border-top: 2px solid var(--tinta); padding-top: 0.3rem; }} .datos dt {{ font-size: 0.75rem; color: var(--gris); }}
  .datos dd {{ margin: 0; font-weight: 700; font-size: 1.375rem; line-height: 1.2; }} .datos dd small {{ display: block; font-size: 0.8125rem; font-weight: 400; color: var(--gris); }}
  .frase {{ border: 2px solid var(--tinta); padding: 0.75rem 1rem; font-size: 1.0625rem; max-width: 46rem; }}
  .scroll {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; font-size: 0.875rem; font-variant-numeric: tabular-nums; width: 100%; max-width: 46rem; margin: 0.5rem 0 1rem; }}
  th, td {{ border-bottom: 1px solid var(--suave); padding: 0.3rem 0.4rem; text-align: right; }} th:first-child, td:first-child {{ text-align: left; }}
  th {{ font-size: 0.75rem; color: var(--gris); font-weight: 400; }} tr.eq td {{ font-weight: 700; border-bottom: 2px solid var(--tinta); }}
  .nota {{ color: var(--gris); font-size: 0.8125rem; }}
  code {{ font-size: 0.875rem; }}
</style></head>
<body><main class="doc">
  <nav class="nav" aria-label="Pestañas del proyecto">
    <a href="../">Nogaleras</a><a href="./">N6 · diseño</a><a href="acceso.html">Acceso</a><a href="casa.html">Casa muestra</a><a href="terreno.html" aria-current="page">Terreno</a><a href="base.html">N6 · base</a><a href="tamanos.html">N6 · tamaños</a>
  </nav>
  <h1>Terreno <span>Cuánto vale y cuánto le toca al dueño si lo aporta en fideicomiso</span></h1>
  <dl class="datos">
    <div><dt>Precio al que lo tomamos</dt><dd>${fmt(PM2)}/m²<small>{fmt(A)} m² · {mill(P)} de contado</small></dd></div>
    <div><dt>En fideicomiso, el dueño recibe</dt><dd>{pct(X, 2)} de cada venta<small>≈ {mill(cobra)} en {meses/12:.1f} años · ${fmt(cobra/A)}/m²</small></dd></div>
    <div><dt>Lo que gana cada parte contra el contado</dt><dd>{mill(gana)}<small>el dueño y el proyecto, lo mismo, en pesos de hoy</small></dd></div>
  </dl>
  <p class="frase">«Tu terreno vale {mill(P).replace(' millones', ' millones de pesos')} de contado (${fmt(PM2)} por m²). Si lo aportas al fideicomiso, te damos el <b>{pct(X, 2)} de cada venta</b>. Es el punto exacto en el que tú y el proyecto ganan lo mismo contra una venta de contado: {mill(gana)} cada uno, en pesos de hoy.»</p>

  <h2>De dónde sale</h2>
  <ul>
    <li><b>Precio del metro: ${fmt(PM2)}/m².</b> Es el estimado del mapa de nogaleras para N6: nogalera pegada a la mancha urbana de Torreón, en un rango de $440 a $1,010/m². Se aplica a todo el terreno ({fmt(A)} m², {A/1e4:,.1f} ha), no solo a lo vendible. No es un avalúo.</li>
    <li><b>Ventas del proyecto: {mill(S)}</b> ({fmt(LOTES)} lotes y el comercio). Empiezan en el mes {INICIO}, con la licencia, a {RITMO} lotes por mes: se venden en {meses/12:.1f} años.</li>
    <li><b>El dinero no vale lo mismo para los dos.</b> Al dueño, esperar un año por su dinero le cuesta {pct(R_DUENO, 0)} (lo que ganaría invirtiéndolo seguro, y un poco más). Al proyecto, tener el dinero un año le cuesta {pct(R_PROY, 0)}, porque tendría que pedir prestado o poner capital para pagar el terreno de contado.</li>
    <li><b>Lo mínimo que le conviene al dueño: {pct(X_piso, 2)}.</b> Con eso, las ventas que le tocan valen hoy exactamente {mill(P)}.</li>
    <li><b>Lo máximo que le conviene al proyecto: {pct(X_techo, 2)}.</b> Arriba de eso, le saldría mejor comprar de contado.</li>
    <li><b>El justo: {pct(X, 2)}.</b> Es el que reparte a partes iguales lo que se gana con el fideicomiso. Fórmula: <code>X = 2 × valor del terreno ÷ (valor de hoy de las ventas para el dueño + para el proyecto)</code>.</li>
  </ul>
  <div class="scroll"><table>
    <tr><th></th><th>Porcentaje de las ventas</th><th>Cobra en total</th><th>Vale hoy para el dueño</th><th>Vale hoy para el proyecto</th></tr>
    <tr><td>Piso (dueño)</td><td>{pct(X_piso, 2)}</td><td>{mill(X_piso*S)}</td><td>{mill(X_piso*VPd)}</td><td>{mill(X_piso*VPp)}</td></tr>
    <tr class="eq"><td>Equilibrio</td><td>{pct(X, 2)}</td><td>{mill(X*S)}</td><td>{mill(X*VPd)}</td><td>{mill(X*VPp)}</td></tr>
    <tr><td>Techo (proyecto)</td><td>{pct(X_techo, 2)}</td><td>{mill(X_techo*S)}</td><td>{mill(X_techo*VPd)}</td><td>{mill(X_techo*VPp)}</td></tr>
  </table></div>
  <p>Ojo: el porcentaje sale alto porque, de contado, el terreno ya es {pct(P/S)} de las ventas; en fraccionamientos lo común es que ande entre 15 y 25 %. Si se baja el precio del metro, baja en proporción (tabla de abajo).</p>
  <p>Con el {pct(X, 2)}, al proyecto le quedan {mill(S*(1-X))} de las ventas para pagar {mill(costo_fid)} de urbanización, amenidades, iluminación, permisos y ventas: margen de {mill(margen_fid)} ({pct(margen_fid/costo_fid)} sobre lo que pone), sin tener que pagar el terreno por adelantado.</p>

  <h2>Si se negocia otro precio por metro</h2>
  <p>El porcentaje justo sube parejo con el precio: cada $100/m² son {pct(2*100*A/(VPd+VPp), 2)} de las ventas.</p>
  <div class="scroll"><table>
    <tr><th>Precio del metro</th><th>Valor de contado</th><th>Porcentaje justo</th><th>Cobra en total</th></tr>
    {filas_precio}
  </table></div>

  <h2>Si las ventas van más lentas o más rápidas</h2>
  <p>En el fideicomiso el dueño cobra cuando se vende. Si el proyecto vende más despacio, cobra lo mismo pero más tarde, y eso vale menos hoy. Con el {pct(X, 2)}:</p>
  <div class="scroll"><table>
    <tr><th>Ritmo de ventas</th><th>Cobra en total</th><th>Vale hoy (al {pct(R_DUENO, 0)})</th><th>Equivale a</th></tr>
    {filas_ritmo}
  </table></div>
  <p>Si prefiere cobrar en lotes, el {pct(X, 2)} equivale a unos {X*LOTES:,.0f} lotes; como los recibe al final y los vende él, conviene ajustarlo.</p>
  <p class="nota">Cuentas antes de impuestos y con precios de venta fijos (si los lotes suben de precio, el dueño gana en proporción). El fideicomiso de desarrollo lo administra un banco: el dueño aporta el terreno libre de gravámenes, el proyecto pone todo lo demás y el banco le paga al dueño su porcentaje de cada cobro. Todo se calcula con <code>pipeline/scripts/n6_terreno.py</code>.</p>
</main></body></html>
"""
open(f"{D}/terreno.html", "w").write(HTML)
print("ok terreno.html")
