"""La Nogalera · el fideicomiso: quién aporta qué, flujo de efectivo mes a mes y lo que recibe cada parte. Lo usa sitio.py.
La propuesta al dueño es fija: $522/m² en fideicomiso = 34.3 % de cada venta (ver n6_terreno.py: es el porcentaje en el que el
dueño y el proyecto ganan lo mismo frente a una venta de contado, y el máximo que deja 20 % de margen con la urbanización completa)."""
import math

TASA_INV = 0.15                  # rendimiento preferente del inversionista, anual simple sobre el capital que tiene puesto
COMISION = 0.08                  # ventas, comisiones, escrituración y publicidad: 8 % de cada venta (el otro 4 % de blandos es proyecto y permisos, al inicio)
PROYECTO = 0.04
CUOTA_AGUA = 450.0               # $/casa/mes por el agua (tarifa comparable a SIMAS para una casa de 4); la cuota de mantenimiento viene de servicios.json
OCUPA = 12                       # meses entre la venta del lote y la casa habitada
ETAPAS_OBRA = [(8, 15, 0.32), (14, 21, 0.24), (20, 27, 0.22), (26, 33, 0.22)]      # (mes inicio, mes fin, parte de la urbanización)

def curva_ventas(n, inicio=9):
    """Lotes vendidos por mes: arranque lento, pico, valle y cierre. Suma n."""
    forma = [8, 12, 16, 20, 24, 28] + [36] * 10 + [18] * 8 + [26] * 12 + [22] * 8
    k = n / sum(forma); v = [round(x * k) for x in forma]
    v[-1] += n - sum(v)
    return {inicio + i: x for i, x in enumerate(v)}

def modelo(S, N, X, URB, amen, paisaje, reubica, cuota_mant):
    """Flujo de efectivo del fideicomiso y de la operación. Todo en pesos nominales de 2026."""
    ventas = curva_ventas(N); fin = max(ventas)
    precio = S / N
    meses = range(0, fin + 36)
    flujo = []
    for m in meses:
        v = ventas.get(m, 0); ingreso = v * precio
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
    aportado = 0.0; devuelto = 0.0; rend_pagado = 0.0
    for f in flujo:
        interes += capital * TASA_INV / 12
        caja = f["neto"]
        if caja < 0:
            capital += -caja; aportado += -caja
        else:
            pago_int = min(caja, interes); interes -= pago_int; rend_pagado += pago_int; caja -= pago_int
            pago_cap = min(caja, capital); capital -= pago_cap; devuelto += pago_cap; caja -= pago_cap
            acum += caja                      # excedente libre: es la paga del desarrollador
        pico = max(pico, capital)
        f.update(capital=capital, excedente=acum)
    m_recupera = next(f["mes"] for f in flujo if f["mes"] > 12 and f["capital"] == 0)
    # operación: cuotas de mantenimiento y agua conforme se habitan las casas
    casas = 0; oper = []
    for f in flujo:
        casas += ventas.get(f["mes"] - OCUPA, 0)
        f["casas"] = casas; f["cuotas"] = casas * (cuota_mant + CUOTA_AGUA)
    return dict(flujo=flujo, ventas=ventas, fin_ventas=fin, precio=precio, capital_pico=pico, aportado=aportado, rend=rend_pagado,
                m_recupera=m_recupera, desarrollador=acum, lotes_desarrollador=acum / precio, dueno_total=X * S, comis_total=COMISION * S)
