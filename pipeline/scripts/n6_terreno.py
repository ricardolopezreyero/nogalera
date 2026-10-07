"""N6 · precio del terreno y aportación en fideicomiso (lo usa sitio.py).
El dueño aporta el terreno a un fideicomiso y cobra un porcentaje de cada venta, conforme se cobra.
Porcentaje justo: el que deja al dueño y al proyecto con la MISMA ganancia, en pesos de hoy, frente a una venta de contado.
  dueño:    X·VP(ventas, r_dueño) − P      (lo que gana contra vender hoy a P)
  proyecto: P − X·VP(ventas, r_proyecto)    (lo que ahorra contra comprar hoy a P)
  iguales → X = 2P / (VP_dueño + VP_proyecto)
El proyecto descuenta más alto que el dueño (su dinero cuesta más), por eso los dos ganan con el fideicomiso."""
R_DUENO, R_PROY = 0.10, 0.18          # tasas anuales: dueño (inversión segura y algo más), proyecto (crédito puente y capital)
INICIO, RITMO = 9, 25                 # mes en que empiezan las ventas (licencia) y lotes por mes
MARGEN_OBJ = 0.20                     # margen mínimo sano para el proyecto, sobre lo que pone

def fideicomiso(fc):
  r = fc["resumen"]
  A, PM2 = fc["bruto_m2"], r["terreno_m2_precio"]
  P, S, C, LOTES = PM2 * A, r["venta"], r["costo"], r["lotes"]

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
  p_contado = (S / (1 + MARGEN_OBJ) - costo_fid) / A               # precio de contado que deja ese margen
  X_viable = 1 - (1 + MARGEN_OBJ) * costo_fid / S                  # porcentaje de las ventas que deja ese margen
  p_fid = X_viable * (VPd + VPp) / (2 * A)                          # precio cuyo porcentaje justo es X_viable
  m_fid = lambda p: (S * (1 - 2 * p * A / (VPd + VPp)) - costo_fid) / costo_fid
  # print(f"contado máx {p_contado:,.0f}/m²; fideicomiso viable {X_viable:.4f} ↔ {p_fid:,.0f}/m²")
  # print(f"P={P:,.0f} VPd={VPd:,.0f} VPp={VPp:,.0f} piso={X_piso:.4f} eq={X:.4f} techo={X_techo:.4f} cobra={cobra:,.0f} ({cobra/A:,.0f}/m²) gana={gana:,.0f} margen={margen_fid:,.0f}")

  return dict(A=A, PM2=PM2, P=P, S=S, C=C, LOTES=LOTES, VPd=VPd, VPp=VPp, X_piso=X_piso, X_techo=X_techo, X=X, gana=gana, cobra=cobra, meses=meses, margen_fid=margen_fid, costo_fid=costo_fid,
              p_contado=p_contado, X_viable=X_viable, p_fid=p_fid, m_fid=m_fid, vp=vp, R_DUENO=R_DUENO, R_PROY=R_PROY, INICIO=INICIO, RITMO=RITMO, MARGEN_OBJ=MARGEN_OBJ)
