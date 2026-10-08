"""La Nogalera · el fideicomiso: quién aporta qué, flujo de efectivo mes a mes y lo que recibe cada parte. Lo usa sitio.py.
La propuesta al dueño es fija: $522/m² en fideicomiso = 34.3 % de cada venta (ver n6_terreno.py: es el porcentaje en el que el
dueño y el proyecto ganan lo mismo frente a una venta de contado, y el máximo que deja 20 % de margen con la urbanización completa)."""
import math

TASA_INV = 0.15                  # rendimiento preferente del inversionista, anual simple sobre el capital que tiene puesto
COMISION = 0.08                  # ventas, comisiones, escrituración y publicidad: 8 % de cada venta (el otro 4 % de blandos es proyecto y permisos, al inicio)
PROYECTO = 0.04
OCUPA = 12                       # meses entre la venta del lote y la casa habitada
ETAPAS_OBRA = [(8, 15, 0.32), (14, 21, 0.24), (20, 27, 0.22), (26, 33, 0.22)]      # (mes inicio, mes fin, parte de la urbanización)
HORIZONTE = 120                  # meses que se muestran del flujo (10 años)
ESCALON_ETAPA = 0.05             # la lista de precios sube 5 % en cada etapa de ventas (cada cuarta parte de los lotes): quien compra primero, compra más barato
ETAPAS_VENTA = 4
INCORPORACION = 0.0              # cuota única de incorporación por lote al escriturar (reglamento, app, tarjetas, alta en la operadora); 0 = no se cobra en el caso base
# ---- la operadora: mantenimiento + seguridad y agua como negocio (pesos de 2026) ----
CUOTA_CASA, CUOTA_LOTE = 1500.0, 1000.0  # cuota meta por casa habitada y por lote baldío (desde que se escritura)
RAMPA = (9, 36)                          # la cuota arranca al 70 % en el mes 9 (menos servicios al principio) y llega al 100 % en el mes 36
COSTO_FIJO_OPER = 320_000.0              # por mes desde el mes 12, no depende de cuántas casas hay: seguridad 24 h (2 por turno + rondín), monitoreo, administración, contador, seguros, app
COSTO_VAR_CASA = 520.0                   # por casa habitada al mes: jardinería y podas, pintura y reparaciones, barrido, planta, iluminación, club, tecnología
COSTO_VAR_LOTE = 120.0                   # por lote baldío al mes: limpieza y riego de sus nogales
FONDO_RESERVA = 0.10                     # de la cuota: es de los vecinos (pavimentos, bombas, renovaciones), no de la operadora
AGUA_FIJA, AGUA_M3, CONSUMO_M3 = 250.0, 11.0, 30.0   # tarifa: cargo fijo por la red y el bombeo + $11 por m³; una casa de 4 usa 30 m³ al mes (1,000 l/día)
COSTO_AGUA_CASA = 300.0                  # por casa al mes: energía de bombeo, cloración, operador, y depreciación de pozos, cisterna y red a 25 años
NUEZ_KG_ARBOL, PRECIO_NUEZ, COSTO_NUEZ, N_NOGALES, MES_NUEZ, ANIO_NUEZ = 8.0, 76.0, 0.40, 1943, 10, 3   # cosecha de los nogales comunes: 8 kg por árbol, $76/kg, 40 % de costo, cada octubre desde el año 3
def rampa(m):
    a, b = RAMPA
    return 0.0 if m < a else 0.7 + 0.3 * min(1.0, (m - a) / (b - a))
def lista(precio_base):
    """Precio de lista por m² (lote típico de 300 m²) en cada etapa de ventas."""
    return [precio_base * (1 + ESCALON_ETAPA) ** k for k in range(ETAPAS_VENTA)]
def anual(flujo, campo, anios=10):
    """Suma de un campo del flujo por año (lista de `anios` valores)."""
    return [sum(f[campo] for f in flujo if a * 12 <= f["mes"] < (a + 1) * 12) for a in range(anios)]
def tir_mensual(flujos):
    """TIR de una serie mensual, anualizada (bisección)."""
    def vpn(r): return sum(f / (1 + r) ** i for i, f in enumerate(flujos))
    lo, hi = -0.05, 0.5
    if vpn(lo) * vpn(hi) > 0: return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if vpn(lo) * vpn(mid) <= 0: hi = mid
        else: lo = mid
    return (1 + (lo + hi) / 2) ** 12 - 1
# ---- construcción de las casas por nosotros (Modelo Nogal, molde y compras repetidas) ----
M2_CASA = 243.0
PRECIO_M2_MERCADO = 17000.0      # lo que cobra un constructor de Torreón por una casa así, llave en mano, con acabados medios-altos (2026)
COSTO_M2_TIPICO = 14500.0        # lo que le cuesta a ese constructor (margen típico ≈ 15 %)
COSTO_M2_NOSOTROS = 12550.0      # lo que nos cuesta con un solo modelo: moldes de aluminio, compras por volumen y cuadrillas en serie (≈ 13 % menos)
ADOPCION = 0.70                  # parte de los compradores que construyen con nosotros (el paquete lote + casa)
DURACION_CASA = 8                # meses de obra por casa (con molde: 6 a 8)
ARRANQUE_CASA = 2                # meses entre la compra del lote y el arranque de la casa
PAGO_CASA = (0.30, 0.60, 0.10)   # anticipo, estimaciones durante la obra, entrega
PRECIO_CASA = M2_CASA * PRECIO_M2_MERCADO; COSTO_CASA = M2_CASA * COSTO_M2_NOSOTROS; MARGEN_CASA = PRECIO_CASA - COSTO_CASA
# ---- las partes del negocio: quién gana qué (ver sitio.py → «Las reglas del juego») ----
COMISION_VENDEDOR = 0.05         # de la COMISION (8 % de cada venta), lo que gana el comercializador; el otro 3 % es escrituración y publicidad
MARGEN_URB = 0.10                # margen del constructor desarrollador (el que ejecuta la urbanización, el club y los parques) dentro del presupuesto de obra
REPARTO_CASAS = {"constructor": 0.35, "idea": 0.20, "desarrollador": 0.15, "comercializador": 0.10, "inversionista": 0.10, "terreno": 0.10}   # cómo se reparte la utilidad de cada casa: todos ganan de las casas
OPERADORA_DE = {"idea": 1.0}     # a quién le queda el margen de la operación (agua, mantenimiento y nuez)
assert abs(sum(REPARTO_CASAS.values()) - 1) < 1e-9 and abs(sum(OPERADORA_DE.values()) - 1) < 1e-9

def curva_ventas(n, inicio=9, estira=1.0):
    """Lotes vendidos por mes: arranque lento, pico, valle y cierre. Suma n. `estira` > 1 alarga la venta (escenario lento)."""
    forma = [8, 12, 16, 20, 24, 28] + [36] * 10 + [18] * 8 + [26] * 12 + [22] * 8
    if estira != 1.0: forma = [forma[min(len(forma) - 1, int(i / estira))] for i in range(int(len(forma) * estira))]
    k = n / sum(forma); v = [round(x * k) for x in forma]
    v[-1] += n - sum(v)
    return {inicio + i: x for i, x in enumerate(v)}

def modelo(S, N, X, URB, amen, paisaje, reubica, cuota_mant, estira=1.0):
    """Flujo de efectivo del fideicomiso y de la operación. Todo en pesos nominales de 2026."""
    ventas = curva_ventas(N, estira=estira); fin = max(ventas)
    precio = S / N
    meses = range(0, HORIZONTE)
    flujo = []
    acum_v = 0
    for m in meses:
        v = ventas.get(m, 0); etapa = min(ETAPAS_VENTA - 1, int(acum_v * ETAPAS_VENTA / N)); acum_v += v
        ingreso = v * precio * (1 + ESCALON_ETAPA) ** etapa
        duen = X * ingreso; comis = COMISION * ingreso
        obra = sum(URB * parte / (b - a) for a, b, parte in ETAPAS_OBRA if a <= m < b)
        obra += (paisaje + reubica) * (1 / 25 if 8 <= m < 33 else 0)
        am = amen["social"] / 7 if 9 <= m < 16 else 0
        am += amen["deportivo"] / 6 if 15 <= m < 21 else 0
        proy = PROYECTO * S / 9 if m < 9 else 0
        flujo.append(dict(mes=m, lotes=v, ingreso=ingreso, dueno=duen, comision=comis, obra=obra, amen=am, proyecto=proy,
                          neto=ingreso - duen - comis - obra - am - proy))
    # el inversionista cubre el déficit mes a mes y se le paga en cuanto hay excedente, con su rendimiento
    capital, interes, pico, acum = 0.0, 0.0, 0.0, 0.0
    aportado = 0.0; devuelto = 0.0; rend_pagado = 0.0; inv_flujo = []
    for f in flujo:
        interes += capital * TASA_INV / 12
        caja = f["neto"]; mov = 0.0; pago_int = 0.0
        if caja < 0:
            capital += -caja; aportado += -caja; mov = caja
        else:
            pago_int = min(caja, interes); interes -= pago_int; rend_pagado += pago_int; caja -= pago_int
            pago_cap = min(caja, capital); capital -= pago_cap; devuelto += pago_cap; caja -= pago_cap
            acum += caja; mov = pago_int + pago_cap   # excedente libre: es la paga del desarrollador
        pico = max(pico, capital); inv_flujo.append(mov)
        f.update(capital=capital, excedente=acum, inv=mov, rend=pago_int)
    tir_inv = tir_mensual(inv_flujo); moic = (devuelto + rend_pagado) / aportado if aportado else 0
    m_recupera = next((f["mes"] for f in flujo if f["mes"] > 12 and f["capital"] == 0), None)   # None: no recupera en el horizonte
    # la operadora: cuota de mantenimiento y seguridad (casa habitada y lote baldío), agua por tarifa y la nuez de los nogales comunes
    casas = 0; vendidos = 0
    for f in flujo:
        m = f["mes"]; vendidos += ventas.get(m, 0); casas += ventas.get(m - OCUPA, 0); baldios = vendidos - casas
        k = rampa(m)
        cuota_ing = (casas * CUOTA_CASA + baldios * CUOTA_LOTE) * k
        agua_ing = casas * (AGUA_FIJA + AGUA_M3 * CONSUMO_M3)
        nuez = N_NOGALES * NUEZ_KG_ARBOL * PRECIO_NUEZ * (1 - COSTO_NUEZ) if (m % 12 == MES_NUEZ and m >= ANIO_NUEZ * 12) else 0.0
        costo = (COSTO_FIJO_OPER if m >= 12 else 0.0) + casas * COSTO_VAR_CASA + baldios * COSTO_VAR_LOTE + casas * COSTO_AGUA_CASA
        reserva = FONDO_RESERVA * cuota_ing
        f.update(casas=casas, baldios=baldios, cuota_ing=cuota_ing, agua_ing=agua_ing, nuez=nuez, cuotas=cuota_ing + agua_ing, oper_costo=costo, reserva=reserva,
                 oper_margen=cuota_ing + agua_ing + nuez - costo - reserva)
    # nosotros, mes a mes: los lotes que nos tocan (se liquidan cuando el inversionista ya recuperó) y el margen de la operación
    for f in flujo:
        f["pago_idea"] = acum if f["mes"] == m_recupera else 0.0          # los lotes de la idea se liquidan cuando el inversionista ya recuperó
        f["nosotros"] = f["oper_margen"] + f["pago_idea"]
    return dict(flujo=flujo, ventas=ventas, fin_ventas=fin, precio=precio, capital_pico=pico, aportado=aportado, rend=rend_pagado,
                m_recupera=m_recupera, desarrollador=acum, lotes_desarrollador=acum / precio, dueno_total=sum(f["dueno"] for f in flujo), comis_total=sum(f["comision"] for f in flujo),
                venta_total=sum(f["ingreso"] for f in flujo), escalacion=sum(f["ingreso"] for f in flujo) / S - 1,
                tir_inv=tir_inv, moic=moic, devuelto=devuelto, inv_flujo=inv_flujo)


def construccion(ventas, N):
    """Las casas que construimos nosotros: ingresos, costos y utilidad por mes, con el calendario de cada casa."""
    casas = {m: v * ADOPCION for m, v in ventas.items()}
    ing = [0.0] * HORIZONTE; cos = [0.0] * HORIZONTE; obra = [0.0] * HORIZONTE; ent = [0.0] * HORIZONTE
    for m, n in casas.items():
        a = m + ARRANQUE_CASA
        if a < HORIZONTE: ing[a] += n * PRECIO_CASA * PAGO_CASA[0]
        for k in range(DURACION_CASA):
            t = a + k
            if t < HORIZONTE: ing[t] += n * PRECIO_CASA * PAGO_CASA[1] / DURACION_CASA; cos[t] += n * COSTO_CASA / DURACION_CASA; obra[t] += n
        t = a + DURACION_CASA
        if t < HORIZONTE: ing[t] += n * PRECIO_CASA * PAGO_CASA[2]; ent[t] += n
    util = [i - c for i, c in zip(ing, cos)]
    caja, minimo, acum = 0.0, 0.0, []
    for u in util: caja += u; minimo = min(minimo, caja); acum.append(caja)
    total = sum(casas.values())
    return dict(casas=total, ingresos=sum(ing), costos=sum(cos), utilidad=sum(util), ing=ing, cos=cos, util=util, obra=obra, entregas=ent, acum=acum, capital=-minimo,
                pico_obra=max(obra), fin=max(i for i, x in enumerate(ent) if x > 0), margen_tipico=(PRECIO_M2_MERCADO - COSTO_M2_TIPICO) / PRECIO_M2_MERCADO, margen=MARGEN_CASA / PRECIO_CASA)


ESCENARIOS = [("Base", 1.0, 1.0), ("Ventas 30 % más lentas", 1.3, 1.0), ("Precio 10 % menor", 1.0, 0.9), ("Lento y 10 % más barato", 1.3, 0.9), ("Precio 5 % mayor", 1.0, 1.05)]
def escenarios(S, N, X, URB, amen, paisaje, reubica, cuota_mant):
    """El modelo bajo varios escenarios de venta: lo que ve el inversionista antes de entrar."""
    out = []
    for nombre, estira, pr in ESCENARIOS:
        m = modelo(S * pr, N, X, URB, amen, paisaje, reubica, cuota_mant, estira=estira)
        out.append(dict(nombre=nombre, estira=estira, precio=pr, venta=m["venta_total"], dueno=m["dueno_total"], pico=m["capital_pico"], recupera=m["m_recupera"], tir=m["tir_inv"], moic=m["moic"],
                        rend=m["rend"], desarrollador=m["desarrollador"], lotes=m["lotes_desarrollador"], fin=m["fin_ventas"], oper=sum(f["oper_margen"] for f in m["flujo"])))
    return out
