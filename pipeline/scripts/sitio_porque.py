# ======================= POR QUÉ $522 POR M² (se ejecuta dentro de sitio.py) =======================
# Argumentación completa del precio del terreno. Usa los globales de sitio.py: GROSS, R, N, X_DUENO, PRECIO_FID, DUENO_TOTAL, MOD, FID, OBRA_TOTAL, SV, FI, TE, N6…

# ---- referencias de mercado (anuncios públicos, octubre de 2026; cifras redondeadas) ----
MERCADO_HUERTAS = [("Huerta de nogal, 50 ha, con derechos de agua, bodega y riego, cerca de Torreón", 46e6, 500000),
                   ("Huerta de 50 ha con 1,100 nogales y pozo concesionado, Matamoros", 34.5e6, 500000)]
MERCADO_LOTES = [("Los Viñedos / Las Viñas (oriente de Torreón), lotes de 286 a 380 m²", 5900), ("Hacienda del Rosario (La Paz), lotes de 500 m²", 5400),
                 ("Residencial Senderos, lotes chicos", 4200)]
NUEZ_T_HA, NUEZ_PRECIO_T = 1.5, 76000.0           # t/ha en riego en La Laguna (INIFAP) y precio estimado de la cosecha 2025 (Milenio / Sader)
RANGO_HUERTA = (min(p / a for _, p, a in MERCADO_HUERTAS), max(p / a for _, p, a in MERCADO_HUERTAS))
PRECIO_LOTE_MODELO = VENTA_LOTES / R["vendible_m2"]      # $/m² de lote que supone el modelo (≈ 3,344)

def _modelo_x(x):
    return FI.modelo(R["venta"], N, x, SV["URB"], dict(social=AM_SOCIAL, deportivo=AM_DEP), PAISAJE, REUBICA, SV["cuota_casa"])

def _vp_dueno(tasa):
    i = (1 + tasa) ** (1 / 12) - 1
    return sum(f["dueno"] / (1 + i) ** f["mes"] for f in MOD["flujo"])

def barras_precio_svg(filas):
    """Barras horizontales de $/m² para el dueño según la vía. filas: (etiqueta, valor, nota, negra)."""
    W, alto, top = 1000, 48, 10; H = top + alto * len(filas) + 30
    mx = max(v for _, v, _, _ in filas); x0, x1 = 400, W - 110; k = (x1 - x0) / mx
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Lo que recibe el dueño por metro cuadrado según la vía" class="esquema">']
    for i, (et, v, nota, negra) in enumerate(filas):
        y = top + i * alto
        o.append(f'<text x="{x0 - 12}" y="{y + 20}" text-anchor="end" font-size="13" font-weight="700">{e(et)}</text>')
        o.append(f'<text x="{x0 - 12}" y="{y + 36}" text-anchor="end" font-size="11" fill="#555">{e(nota)}</text>')
        o.append(f'<rect x="{x0}" y="{y + 9}" width="{max(2, v * k)}" height="{alto - 20}" fill="{"#111" if negra else "#fff"}" stroke="#000" stroke-width="1.4"/>')
        o.append(f'<text x="{x0 + v * k + 8}" y="{y + 28}" font-size="14" font-weight="700">${f0(v)}/m²</text>')
    o.append(f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{H - 28}" stroke="#000" stroke-width="1"/>')
    o.append(f'<text x="{(x0 + W)/2}" y="{H - 8}" text-anchor="middle" font-size="11.5" fill="#333">Pesos por m² de huerta ({f0(GROSS)} m²). Barras blancas: otras vías; negras: el fideicomiso que proponemos.</text></svg>')
    return "\n".join(o)

def cascada_svg(partes):
    """De cada $100 de venta, a dónde va cada peso. partes: (etiqueta, fracción, negra). Las rebanadas angostas llevan su etiqueta abajo, alternando renglón."""
    W, H = 1000, 190; x = 20; y = 30; h = 56; k = (W - 40) / 1.0; abajo = 0
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="A dónde va cada peso de la venta" class="esquema">']
    for et, fr, negra in partes:
        w = fr * k
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{"#111" if negra else "#fff"}" stroke="#000" stroke-width="1.4"/>')
        if w > 150:
            o.append(f'<text x="{x + w/2}" y="{y + 24}" text-anchor="middle" font-size="15" font-weight="700" fill="{"#fff" if negra else "#000"}">{pct(fr, 1)}</text>')
            o.append(f'<text x="{x + w/2}" y="{y + 42}" text-anchor="middle" font-size="11" fill="{"#ddd" if negra else "#333"}">{e(et)}</text>')
        else:
            yy = y + h + 18 + 34 * (abajo % 2); abajo += 1
            o.append(f'<text x="{x + w/2}" y="{y + 34}" text-anchor="middle" font-size="13" font-weight="700">{pct(fr, 1)}</text>')
            o.append(f'<line x1="{x + w/2}" y1="{y + h}" x2="{x + w/2}" y2="{yy - 12}" stroke="#000" stroke-width="0.8"/>')
            o.append(f'<text x="{min(x + w/2, W - 60)}" y="{yy}" text-anchor="middle" font-size="11" fill="#333">{e(et)}</text>')
        x += w
    o.append(f'<text x="20" y="18" font-size="12" fill="#333">De cada $100 que paga un comprador por su lote:</text></svg>')
    return "\n".join(o)

def porque():
    S = R["venta"]; A = GROSS
    p_contado = FID["p_contado"]; contado_total = p_contado * A
    huerta_lo, huerta_hi = RANGO_HUERTA
    nuez_bruto = A / 1e4 * NUEZ_T_HA * NUEZ_PRECIO_T
    # calendario del dueño
    fl = MOD["flujo"]; anos = []; acum = 0.0
    for a in range(0, 5):
        y = sum(f["dueno"] for f in fl if a * 12 <= f["mes"] < (a + 1) * 12); acum += y
        anos.append((f"Año {a + 1}", mill(y, 1), mill(acum, 1), pct(acum / DUENO_TOTAL, 0)))
    hitos = {}; acum = 0.0
    for f in fl:
        acum += f["dueno"]
        for q in (0.25, 0.5, 0.75, 1.0):
            if q not in hitos and acum >= q * DUENO_TOTAL - 1: hitos[q] = f["mes"]
    # sensibilidad al porcentaje
    sens = []
    for x in (0.30, 0.32, X_DUENO, 0.36, 0.38, 0.40, 0.45):
        m = _modelo_x(x); costo_fid = FID["costo_fid"]; margen = (S * (1 - x) - costo_fid) / costo_fid
        peq = x * (FID["VPd"] + FID["VPp"]) / (2 * A)
        rec = f"mes {m['m_recupera']}" if m["m_recupera"] else "no recupera"
        es = abs(x - X_DUENO) < 1e-6
        fila = (f"<b>{pct(x)}</b>" if es else pct(x), f"${f0(peq)}", mill(x * S), mill(m["desarrollador"]) if m["desarrollador"] > 1e6 else "—", pct(margen, 0), rec,
                "<b>la propuesta</b>" if es else ("sobra margen: el dueño cobra de menos" if x < X_DUENO else ("el inversionista no recupera en 10 años: no hay obra" if rec == "no recupera" else "margen bajo el mínimo: el inversionista no entra")))
        sens.append(fila)
    # precio de los lotes: el porcentaje protege al dueño
    escen = []
    for p in (3000, PRECIO_LOTE_MODELO, 4000, 5000, 5900):
        s_l = p * R["vendible_m2"] + VENTA_COM; d = X_DUENO * s_l
        escen.append((f"${f0(p)}/m²" + (" <b>(el modelo)</b>" if abs(p - PRECIO_LOTE_MODELO) < 1 else ""), mill(s_l), mill(d), f"<b>${f0(d / A)}</b>"))
    # esperar
    espera = []
    for anios in (3, 5, 8, 10):
        vp = 1010 / (1.10 ** anios); espera.append((f"{anios} años", "$1,010/m²", f"${f0(vp)}/m²", mill(vp * A), mill(nuez_bruto * anios / 2)))
    vp10 = _vp_dueno(0.10); vp15 = _vp_dueno(0.15)
    barras = barras_precio_svg([("Vender la huerta como huerta", (huerta_lo + huerta_hi) / 2, f"nogaleras anunciadas en la región: ${f0(huerta_lo)} a ${f0(huerta_hi)}/m²", False),
                                ("Terreno rústico en Torreón", 420, "anuncios de parcelas de 6,000 a 9,000 m² sin urbanizar", False),
                                ("Venta de contado a un desarrollador", p_contado, "lo máximo que paga quien compra hoy con 20 % de margen", False),
                                ("Esperar 5 años y vender a $1,010/m²", 1010 / 1.10 ** 5, "en pesos de hoy, al 10 % anual; si ese comprador llega", False),
                                (f"Fideicomiso: {pct(X_DUENO)} de cada venta", DUENO_TOTAL / A, f"{mill(DUENO_TOTAL)} en {MOD['fin_ventas']/12:.1f} años, con lotes a ${f0(PRECIO_LOTE_MODELO)}/m²", True),
                                ("Fideicomiso con lotes a $5,000/m²", X_DUENO * (5000 * R["vendible_m2"] + VENTA_COM) / A, "el porcentaje es del dueño: la subida también", True)])
    cascada = cascada_svg([("al dueño del terreno", X_DUENO, True), ("ventas, comisiones y escrituras", FI.COMISION, False), ("proyecto y permisos", FI.PROYECTO, False),
                           ("la obra: calles, redes, club, parques y luz", OBRA_TOTAL / S, False), ("rendimiento del inversionista", MOD["rend"] / S, False), ("nosotros, en lotes", MOD["desarrollador"] / S, False)])
    cuerpo = f"""
<p class="frase" style="font-size:1.25rem"><b>${f0(PRECIO_FID)} por m² en fideicomiso: te damos el {pct(X_DUENO)} de cada venta.</b></p>
{kpis([("Lo que cobra el dueño", mill(DUENO_TOTAL), f"${f0(DUENO_TOTAL/A)} por m² · en {MOD['fin_ventas']/12:.1f} años"), ("La mitad ya cobrada", f"mes {hitos[0.5]}", f"el 25 % en el mes {hitos[0.25]}, el 75 % en el mes {hitos[0.75]}"),
       ("De contado, lo máximo", f"${f0(p_contado)}/m²", f"{mill(contado_total)} · {pct(DUENO_TOTAL/contado_total - 1, 0)} menos que el fideicomiso"), ("Como huerta", f"${f0(huerta_lo)}–{f0(huerta_hi)}/m²", f"{mill(huerta_lo*A)} a {mill(huerta_hi*A)} por todo"),
       ("Lo que cuesta la obra", f"${f0(OBRA_TOTAL/A)}/m²", f"{mill(OBRA_TOTAL)}: más que el terreno mismo"), ("Lotes en el modelo", f"${f0(PRECIO_LOTE_MODELO)}/m²", "el oriente de Torreón hoy vende a $4,200–5,900")])}
<p>El precio del terreno no es una opinión ni un punto de partida para regatear. Sale de una cuenta que cualquiera puede repetir: <b>lo que pagan los compradores por los lotes, menos lo que cuesta convertir la huerta en lotes, menos el margen mínimo sin el cual nadie pone el dinero de la obra</b>. Lo que queda es el terreno. Esa cuenta da {pct(X_DUENO)} de cada venta, que son {mill(DUENO_TOTAL)} en {MOD['fin_ventas']/12:.1f} años (${f0(DUENO_TOTAL/A)}/m²) y equivalen a ${f0(PRECIO_FID)}/m² pagados hoy. Abajo están las siete razones, con números, de por qué ese es el precio correcto y no otro.</p>

<h2 id="vias">Lo que recibe el dueño por cada vía</h2>
<figure><div class="scroll sec"><div class="dibujo">{barras}</div></div><figcaption><b>El fideicomiso es la vía que más paga, y la única que paga en años y no en «algún día».</b> Las referencias de mercado son anuncios públicos de octubre de 2026 en los portales inmobiliarios; están redondeadas.</figcaption></figure>

<h2 id="peso">1 · De dónde sale cada peso</h2>
<figure><div class="scroll sec"><div class="dibujo">{cascada}</div></div><figcaption><b>La obra cuesta más que el terreno.</b> Convertir la huerta en {f0(N)} lotes con calles, drenajes, agua, luz, club y parques cuesta {mill(OBRA_TOTAL)}: ${f0(OBRA_TOTAL/A)} por cada m² de huerta, contra los ${f0(DUENO_TOTAL/A)} que cobra el dueño. El terreno se lleva la rebanada más grande después de la obra, {X_DUENO/(MOD['desarrollador']/S):.0f} veces lo que nos llevamos nosotros.</figcaption></figure>
<p>Es el <b>método residual</b>, el mismo que usa cualquier valuador para un terreno que se va a urbanizar: valor del terreno = venta de los lotes − costo de urbanizar − costos de venta − margen del que arriesga. Con los números de este proyecto ({mill(S)} de venta, {mill(OBRA_TOTAL)} de obra, {pct(FI.COMISION + FI.PROYECTO, 0)} de blandos, 20 % de margen mínimo) el residual es {pct(FID['X_viable'], 2)} de las ventas. Redondeado a favor del proyecto, {pct(X_DUENO)}.</p>

<h2 id="mas">2 · Pedir más no es negociar: es que no haya proyecto</h2>
{tabla(sens, ["Para el dueño", "Equivale hoy a", "Cobra en total", "Nosotros (lotes)", "Margen del proyecto", "El inversionista recupera", "Qué pasa"], "renglon")}
<p>El inversionista pone hasta {mill(MOD['capital_pico'])} al mismo tiempo y exige {TASA_INV_TXT} sobre lo que tiene puesto; nadie pone ese dinero en una huerta de La Paz con menos de 20 % de margen en el proyecto. Con {pct(X_DUENO)} el margen es exactamente ese 20 % y el inversionista recupera en el mes {MOD['m_recupera']}. Con 36 % el margen baja a 17 % y nosotros cobramos la mitad. <b>A partir de 38 % el inversionista no recupera su dinero en diez años</b>: no hay quien financie la obra y el terreno sigue siendo huerta. Cada $100/m² más de precio son {pct(2*100*A/(FID['VPd']+FID['VPp']), 2)} más de las ventas, y salen de la única parte que puede ceder, que es la nuestra: por eso {pct(X_DUENO)} es el máximo y no el inicio de una negociación.</p>

<h2 id="contado">3 · Cobra más que vendiendo de contado</h2>
<p>Con la misma cuenta, lo máximo que un desarrollador puede pagar hoy, de contado, por toda la huerta es <b>${f0(p_contado)}/m²: {mill(contado_total)}</b>. El fideicomiso paga {mill(DUENO_TOTAL)}: <b>{mill(DUENO_TOTAL - contado_total)} más</b> ({pct(DUENO_TOTAL/contado_total - 1, 0)}). ¿Por qué puede pagar más? Porque el proyecto no tiene que pedir prestados {mill(contado_total)} antes de vender el primer lote: el dueño financia el terreno con el terreno mismo, y esa diferencia (${f0(DUENO_TOTAL/A - p_contado)}/m²) se la queda él.</p>
<p>Y ese comprador de contado a ${f0(p_contado)}/m² no existe en la práctica: tendría que poner {mill(contado_total)} de su bolsa, más {mill(OBRA_TOTAL)} de obra, antes de cobrar un peso. Las ofertas reales de contado por una nogalera son de huerta: en la región se anuncian hoy huertas de nogal con derechos de agua a ${f0(huerta_lo)} y ${f0(huerta_hi)} por m² ({mill(MERCADO_HUERTAS[1][1])} y {mill(MERCADO_HUERTAS[0][1])} por 50 ha), y parcelas rústicas en Torreón a $420/m². El fideicomiso paga <b>{DUENO_TOTAL/A/huerta_hi:.0f} a {DUENO_TOTAL/A/huerta_lo:.0f} veces el precio de huerta</b>.</p>

<h2 id="cuando">4 · Cuánto y cuándo: años, no décadas</h2>
{tabla(anos, ["", "Cobra en el año", "Acumulado", "Del total"], "compacta")}
<p>Las ventas arrancan en el mes 9, con la licencia. El dueño tiene <b>la cuarta parte en el mes {hitos[0.25]}, la mitad en el mes {hitos[0.5]}, tres cuartas partes en el mes {hitos[0.75]} y todo en el mes {hitos[1.0]}</b>: {MOD['fin_ventas']/12:.1f} años. Es dinero con fecha, de un proyecto con plano, presupuesto y comprador conocido, no una plusvalía que llegará «cuando crezca la ciudad». Y el dueño cobra <b>primero</b>: su {pct(X_DUENO)} sale de cada venta antes que la obra, antes que el inversionista y antes que nosotros.</p>

<h2 id="porcentaje">5 · Es un porcentaje, no un precio: la subida es del dueño</h2>
{tabla(escen, ["Si los lotes se venden a", "Venta total", "Cobra el dueño", "Por m² de huerta"], "compacta")}
<p>El modelo vende los lotes a ${f0(PRECIO_LOTE_MODELO)}/m² (un lote de {R['lote_mediana']} m² en {mill(PRECIO_LOTE_MODELO * R['lote_mediana'], 2)}). Hoy el oriente de Torreón vende lotes urbanizados a <b>$5,400 a $5,900/m²</b> en Los Viñedos y Hacienda del Rosario, y el precio medio de la ciudad subió 15.5 % entre febrero de 2025 y agosto de 2026. Si La Nogalera vende a esos precios, el dueño cobra ${f0(X_DUENO * (5000 * R['vendible_m2'] + VENTA_COM) / A)} a ${f0(X_DUENO * (5900 * R['vendible_m2'] + VENTA_COM) / A)} por m². <b>Los ${f0(PRECIO_FID)} son el piso con el precio más conservador; todo lo que el mercado dé de más, el {pct(X_DUENO)} se lo lleva el dueño</b>. Un precio fijo de contado, por alto que fuera, le quitaría esa subida.</p>

<h2 id="esperar">6 · Lo que cuesta esperar</h2>
{tabla(espera, ["Si vende dentro de", "A", "Vale hoy (10 % anual)", "Por toda la huerta", "Nuez cosechada mientras tanto (bruto)"], "compacta")}
<p>El tope del rango de precio de la huerta, $1,010/m², existe solo cuando alguien la urbaniza; mientras no llegue ese alguien, el terreno produce nuez. A {NUEZ_T_HA} t/ha y ${f0(NUEZ_PRECIO_T)} la tonelada (cosecha 2025), las {ha(A)} dan unos <b>{mill(nuez_bruto, 1)} brutos al año</b>, antes de agua, poda, cosecha y mano de obra, y la cosecha 2025 en La Laguna se desplomó por el calor y la falta de agua. El fideicomiso paga en promedio {mill(DUENO_TOTAL / (MOD['fin_ventas']/12))} al año durante {MOD['fin_ventas']/12:.1f} años: <b>{DUENO_TOTAL / (MOD['fin_ventas']/12) / nuez_bruto:.0f} veces la cosecha bruta</b>. Esperar cinco años a un comprador a $1,010 vale hoy ${f0(1010/1.1**5)}/m², menos que el fideicomiso, y nadie garantiza que ese comprador llegue en cinco años, ni en diez.</p>

<h2 id="riesgo">7 · Quién corre el riesgo</h2>
<ul>
<li><b>El dueño no pone un peso</b> y es el primero en cobrar de cada venta. El terreno queda en el fideicomiso a su favor hasta que cada lote se escritura: si la obra no arranca en el plazo pactado, el terreno regresa, intacto y con sus nogales.</li>
<li><b>El inversionista arriesga {mill(MOD['capital_pico'])}</b> y cobra después del dueño, con un rendimiento fijo.</li>
<li><b>Nosotros cobramos al final y en lotes</b> ({MOD['lotes_desarrollador']:.0f} lotes, {mill(MOD['desarrollador'])}), solo si el proyecto cumple. Si el precio del terreno sube, lo que desaparece es nuestra paga; por eso podemos decir con exactitud dónde está el límite.</li>
<li><b>El banco fiduciario</b> cobra y reparte según el contrato: el dueño no depende de la palabra de nadie.</li>
</ul>
<p>En las aportaciones de tierra para fraccionamientos en México el terreno suele pesar entre 15 y 25 % de la venta. Aquí pesa {pct(X_DUENO)} porque la obra es solo urbanización (no hay edificios), porque los nogales ya están y porque el dueño financia el terreno con el terreno. Es una participación alta, y es la máxima que el proyecto aguanta.</p>

<h2 id="frase">En una frase, y qué pedirle a cualquier otra oferta</h2>
<p class="frase">Te damos el {pct(X_DUENO)} de cada venta: {mill(DUENO_TOTAL)} en {MOD['fin_ventas']/12:.1f} años, {pct(DUENO_TOTAL/contado_total - 1, 0)} más que la mejor venta de contado posible, {DUENO_TOTAL/A/huerta_hi:.0f} veces el precio de huerta, sin poner un peso, cobrando primero, y con la subida del mercado a tu favor. Un peso más y la obra se queda sin quien la pague.</p>
<p>Si alguien ofrece más por m², hay que pedirle el mismo cuadro: a cuánto vende el lote, cuánto cuesta su obra, quién pone los {mill(MOD['capital_pico'])} y en qué mes paga. Un precio sin ese cuadro es una promesa, no una oferta. Este cuadro está completo en <a href="/numeros/">Números y fideicomiso</a> y se recalcula con cualquier dato que cambie.</p>
<p class="nota">Referencias de mercado: anuncios de nogaleras y terrenos en portales inmobiliarios (Inmuebles24, Trovit, Propiedades.com, Icasas) consultados en octubre de 2026; rendimiento del nogal en riego en La Laguna según INIFAP; precio de la nuez 2025 según Sader. Pesos de 2026, antes de impuestos; el valor presente usa 10 % anual para el dueño y 18 % para el proyecto, como en <code>n6_terreno.py</code>.</p>
"""
    pagina("porque", "Por qué $522 por m²", "12 · Por qué $522 por m²", f"Siete razones, con números, de por qué {pct(X_DUENO)} de cada venta es el precio correcto del terreno: es el máximo que el proyecto aguanta y, aun así, más de lo que el dueño obtendría por cualquier otra vía.", cuerpo,
           [("vias", "Lo que recibe por cada vía"), ("peso", "1 · De dónde sale cada peso"), ("mas", "2 · Pedir más"), ("contado", "3 · Más que de contado"), ("cuando", "4 · Cuánto y cuándo"), ("porcentaje", "5 · Es un porcentaje"), ("esperar", "6 · Lo que cuesta esperar"), ("riesgo", "7 · Quién corre el riesgo"), ("frase", "En una frase")],
           descripcion=f"Por qué ${f0(PRECIO_FID)}/m² en fideicomiso ({pct(X_DUENO)} de cada venta) es el precio correcto del terreno de La Nogalera.")
