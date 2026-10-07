"""Cálculo de la entrada de N6 en hora pico (modelo de colas M/M/1 por carril, conservador)."""
import math, json, sys, os
try:                                # casas del diseño vigente (las escribe n6_servicios.py en confort.geojson)
    CASAS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../public/datos/confort.geojson")))["resumen"]["lotes"]
except Exception:
    CASAS = 1105
PHF = 0.85                          # factor de hora pico: los 15 minutos más cargados
HORAS = {"mañana (7 a 8)": dict(tasa=0.85, entra=0.25), "tarde (6 a 7 pm)": dict(tasa=1.00, entra=0.63)}
VISITAS = {"entra": 0.15, "sale": 0.08}          # parte de los viajes que son visitas, servicios y apps
CAP = {"res_entra": 600, "vis_entra_registro": 90, "vis_entra_qr": 240, "res_sale_pluma": 900, "res_sale_libre": 1400, "vis_sale": 360}   # autos por hora por carril
AUTO_M = 6.5                         # largo que ocupa cada auto en la fila
def mm1(lam, mu):
    rho = lam / mu
    if rho >= 1: return dict(rho=round(rho, 2), espera_s=None, fila95=None)
    wq = rho / (mu - lam) * 3600
    n95 = max(0, math.ceil(math.log(0.05) / math.log(rho) - 1)) if rho > 0 else 0
    return dict(rho=round(rho, 2), espera_s=round(wq), fila95=n95, fila95_m=round(n95 * AUTO_M))
res = {}
for hora, h in HORAS.items():
    viajes = CASAS * h["tasa"] / PHF
    entra, sale = viajes * h["entra"], viajes * (1 - h["entra"])
    r = dict(viajes_h=round(viajes), entran_h=round(entra), salen_h=round(sale))
    ve, vs = entra * VISITAS["entra"], sale * VISITAS["sale"]
    re_, rs = entra - ve, sale - vs
    r["entrada_residentes_1_carril"] = mm1(re_, CAP["res_entra"])
    r["entrada_residentes_2_carriles"] = mm1(re_ / 2, CAP["res_entra"])
    r["entrada_visitas_1_carril"] = mm1(ve, CAP["vis_entra_registro"])
    r["entrada_visitas_2_carriles"] = mm1(ve / 2, CAP["vis_entra_registro"])
    r["salida_residentes_pluma"] = mm1(rs, CAP["res_sale_pluma"])
    r["salida_residentes_libre"] = mm1(rs, CAP["res_sale_libre"])
    r["salida_visitas_1_carril"] = mm1(vs, CAP["vis_sale"])
    r.update(res_entran=round(re_), vis_entran=round(ve), res_salen=round(rs), vis_salen=round(vs))
    res[hora] = r
if __name__ == "__main__":
    print(json.dumps(res, ensure_ascii=False, indent=1))

# ---------- trazo de la entrada (metros; u = a lo ancho, 0 = eje de la calle de acceso; v = desde el límite del terreno hacia adentro)
# Se maneja por la derecha: los que entran van por el lado +u.
CASETA_V = 60                       # plumas y casetas a 60 m del límite: caben las filas de la hora pico sin salir a la calle
ISLA_V0 = 12                        # donde empiezan las islas
RETORNO = (34, 42)                  # hueco en las islas para que el visitante que no pasa se regrese
CARRILES = [  # (nombre, u0, u1, sentido)
    ("Salida visitas", -14.0, -10.5, "sale"),
    ("Salida residentes", -10.5, -7.0, "sale"),
    ("Isla y caseta de salida", -7.0, -4.0, "isla"),
    ("Entrada residentes 1", -4.0, -0.7, "entra"),
    ("Entrada residentes 2", -0.7, 2.6, "entra"),
    ("Isla y caseta de visitas", 2.6, 4.6, "isla"),
    ("Entrada visitas 1", 4.6, 7.9, "entra"),
    ("Entrada visitas 2", 7.9, 11.2, "entra"),
    ("Banqueta y puerta peatonal", 11.2, 15.0, "peaton"),
]
ANCHO = (CARRILES[0][1], CARRILES[-1][2])
