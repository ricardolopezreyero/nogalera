"""Generador de renders fotorrealistas con el modelo de imágenes de OpenAI, a partir de los renders de maqueta del sitio.
Cada escena de /renders/ (public/renders/img/<id>.jpg) se manda como imagen de referencia junto con un prompt muy detallado:
el modelo respeta el encuadre, la geometría y la luz de la maqueta y los vuelve una fotografía. Salida: public/renders/ia/<id>.jpg
y public/renders/ia/index.json (prompts, modelo, fecha). Los prompts viven en PROMPTS, abajo, para afinarlos sin tocar el código.

Uso:  OPENAI_API_KEY=…  python3 pipeline/scripts/renders_ia.py [id …] [--modelo gpt-image-2] [--calidad high] [--tamano 1536x1024] [--variantes 1]
      python3 pipeline/scripts/renders_ia.py --prompts        (solo imprime los prompts, sin llamar a la API)
La llave se lee de OPENAI_API_KEY (variable de entorno); nunca se escribe en el repositorio."""
import os, sys, json, base64, time, argparse, urllib.request, urllib.error, io
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
IMG = os.path.join(RAIZ, "public", "renders", "img"); OUT = os.path.join(RAIZ, "public", "renders", "ia")

ESTILO = ("Fotografía arquitectónica fotorrealista, cámara full frame, lente 24 mm, luz natural real, sombras suaves, colores fieles, sin texto, sin marcas de agua, "
          "sin logotipos, sin personas con rostros reconocibles. Lugar: fraccionamiento residencial nuevo dentro de una huerta de nogales pecaneros adultos "
          "(troncos gruesos de corteza gris, copas amplias de hojas pinnadas verde oscuro, 10 a 12 metros de alto, plantados en cuadrícula cada 12.6 m) en el oriente de "
          "Torreón, Coahuila, México: cielo del desierto, aire seco y limpio, pasto verde regado, calles de concreto hidráulico gris claro con guarniciones. "
          "Respeta exactamente el encuadre, la posición de los edificios, los árboles, las calles y la luz de la imagen de referencia; conviértela en una fotografía real "
          "con materiales verdaderos: aplanado color arena, cristal con reflejos, concreto aparente, madera, ladrillo, acero negro.")
CASA = ("Las casas son de dos niveles, 9 m de ancho, azotea plana con pretil, ventanas con marco negro delgado, puerta de madera, cochera abierta al frente, "
        "y cada fachada es distinta: aplanado arena con losas voladas y una franja corrida de cristal (Horizonte), ladrillo rojo con marcos blancos, duela de madera "
        "horizontal, cantera beige con pérgola, blanca estilo hacienda con cornisa, marco de concreto oscuro, lamas verticales de madera, concreto aparente con "
        "ranuras, celosía de barro terracota.")
PROMPTS = {
    "calle": ESTILO + " Vista a nivel de peatón, a media mañana, por el eje de una calle residencial de 11 m: arroyo de 7 m de concreto, banquetas de 2 m con pasto, "
             "un nogal grande en cada lindero formando un túnel de sombra sobre la calle, arbotantes negros de 6 m. " + CASA + " Un auto blanco estacionado en una cochera, "
             "una persona caminando por la banqueta, luz moteada por las hojas sobre el pavimento.",
    "casa": ESTILO + " Vista de tres cuartos desde la banqueta de enfrente, en la tarde, de una casa de dos niveles fachada Horizonte: aplanado color arena, dos losas de "
            "concreto oscuro que vuelan 60 cm al frente, franja corrida de cristal oscuro en la planta alta, ventanas grandes con marco negro en la planta baja, "
            "puerta de madera, jardinera con plantas del desierto, cochera con un auto blanco, jardín con pasto y arbustos, un nogal grande en cada lado del lote. "
            "A los lados, vecinas con fachada de lamas de madera y de ladrillo rojo. Dos personas platicando en la banqueta.",
    "aerea": ESTILO + " Vista aérea oblicua desde dron, a 250 m de altura, en la tarde, de un fraccionamiento completo de 60 hectáreas dentro de una huerta de nogales: "
             "1,105 casas de dos niveles con azoteas planas color arena y algunas de ladrillo, calles paralelas de concreto, un bulevar central con camellón verde, "
             "dos parques arbolados, un club con salón, gimnasio, cancha de tenis y dos de pádel, una pista perimetral junto a la barda, un acceso con pórtico, "
             "y alrededor, más huertas de nogales y la calzada; al fondo el horizonte del desierto de Coahuila. Cuadrícula perfecta de árboles entre las casas.",
    "acceso": ESTILO + " Vista desde la calzada, al atardecer con el cielo naranja y azul, del acceso principal: un pórtico de concreto oscuro de 29 m con el nombre "
              "LA NOGALERA en letras de acero retroiluminadas, muro de identidad de 3 m color arena con pilastras, reja de acero negro con barrotes verticales a los lados "
              "a través de la que se ven nogales grandes, carriles de entrada y salida con islas ajardinadas, caseta de control con cristal iluminado al fondo, plumas, "
              "postes de 9 m encendidos, un mini súper a la izquierda, autos entrando con faros encendidos. Ambiente cálido y seguro.",
    "bulevar": ESTILO + " Vista a nivel de peatón, a media mañana, por el sendero central de un bulevar de 30 m: dos arroyos de concreto, camellón de 5.6 m con un sendero "
               "de concreto en medio y jardines de lluvia con grava y plantas del desierto (agaves, lavanda, salvia) a los lados, postes dobles de 8 m, nogales grandes "
               "en ambas banquetas, casas de dos niveles de fachadas distintas, un ciclista y personas caminando, autos circulando.",
    "parque": ESTILO + " Vista a nivel de peatón, al mediodía, dentro de un parque de barrio bajo nogales adultos plantados en cuadrícula: pasto recién cortado con "
              "franjas, pista de concreto que lo cruza, sendero circular, pérgola de madera con mesas, área de juegos con columpios y resbaladilla sobre arena, bancas "
              "de madera y acero, farolas de 3.5 m, familias con niños, y al fondo las casas de dos niveles del frente del parque.",
    "pista": ESTILO + " Vista a nivel de corredor, temprano en la mañana con luz dorada baja, por una pista de concreto de 5 m que corre bajo una hilera de nogales grandes; "
             "a la derecha, la barda perimetral de block aplanado de 3 m con cerca electrificada arriba y postes de cámaras de 6 m; a la izquierda, pasto y las bardas "
             "traseras y azoteas de las casas; balizas de luz bajas a lo largo de la pista; tres corredores y una ciclista; sombras largas.",
    "interior": ESTILO + " Fotografía de interior, a media tarde, de una sala-comedor-cocina abierta de una casa nueva: piso de madera clara, muros blancos, plafón "
                "de concreto pintado, sofá azul grisáceo de tres plazas, mesa de centro de madera, mesa de comedor para ocho con sillas de madera, cocina con barra, "
                "y al fondo una cancelería de cristal de piso a techo abierta a un portal techado con columnas y un jardín con nogales grandes. Luz natural entrando "
                "por el cristal, vista desde la sala hacia el portal.",
    "portal": ESTILO + " Vista desde el jardín trasero, al atardecer con cielo naranja, de un portal techado de una casa de dos niveles: losa de concreto sobre dos "
              "columnas, piso de concreto pulido, mesa de madera con sillas, asador de acero inoxidable, cancel de cristal que deja ver la sala iluminada por dentro, "
              "lámparas cálidas encendidas en el portal, pasto, y nogales grandes iluminados desde abajo con luz cálida. Tres personas conversando. Ambiente de fin de semana.",
    "noche": ESTILO + " Vista a nivel de peatón, de noche, por el eje de una calle residencial bajo nogales: arbotantes negros de 6 m con luz cálida LED, nogales "
             "iluminados desde el piso con proyectores cálidos que resaltan los troncos y las copas, ventanas de las casas encendidas, un auto con faros encendidos, "
             "cielo azul oscuro con estrellas, pavimento con reflejos suaves. " + CASA + " Sensación de calle segura y cuidada.",
    "club": ESTILO + " Vista de tres cuartos, en la tarde, del club de un fraccionamiento: salón social de dos niveles con cristal y pérgola de acceso, gimnasio de dos "
            "niveles con fachada de lamas de madera, cancha de tenis con malla y dos canchas de pádel con cristales, plaza con sombrillas, nogales grandes alrededor, "
            "personas y autos estacionados en la calle.",
}

def llamar(ruta, datos=None, archivos=None, llave=None, intentos=3):
    url = "https://api.openai.com/v1/" + ruta
    for k in range(intentos):
        try:
            if archivos:
                limite = "----nogalera" + str(int(time.time()))
                cuerpo = io.BytesIO()
                for nombre, valor in datos.items():
                    cuerpo.write(f"--{limite}\r\nContent-Disposition: form-data; name=\"{nombre}\"\r\n\r\n{valor}\r\n".encode())
                for nombre, (fn, contenido, tipo) in archivos:
                    cuerpo.write(f"--{limite}\r\nContent-Disposition: form-data; name=\"{nombre}\"; filename=\"{fn}\"\r\nContent-Type: {tipo}\r\n\r\n".encode()); cuerpo.write(contenido); cuerpo.write(b"\r\n")
                cuerpo.write(f"--{limite}--\r\n".encode())
                req = urllib.request.Request(url, data=cuerpo.getvalue(), headers={"Authorization": f"Bearer {llave}", "Content-Type": f"multipart/form-data; boundary={limite}"})
            else:
                req = urllib.request.Request(url, data=json.dumps(datos).encode(), headers={"Authorization": f"Bearer {llave}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            texto = e.read().decode(errors="replace")
            if e.code in (429, 500, 502, 503) and k < intentos - 1: time.sleep(8 * (k + 1)); continue
            raise SystemExit(f"OpenAI respondió {e.code}: {texto[:600]}")

def generar(ids, modelo, calidad, tamano, variantes, llave, sin_referencia=False):
    os.makedirs(OUT, exist_ok=True)
    indice = json.load(open(os.path.join(OUT, "index.json"))) if os.path.exists(os.path.join(OUT, "index.json")) else {}
    for id_ in ids:
        prompt = PROMPTS[id_]; ref = os.path.join(IMG, id_ + ".jpg"); t0 = time.time()
        print(f"{id_}: generando con {modelo} ({calidad}, {tamano})…", flush=True)
        if sin_referencia or not os.path.exists(ref):
            res = llamar("images/generations", dict(model=modelo, prompt=prompt, n=variantes, size=tamano, quality=calidad), llave=llave)
        else:
            res = llamar("images/edits", {"model": modelo, "prompt": prompt, "n": str(variantes), "size": tamano, "quality": calidad},
                         [("image[]", (id_ + ".jpg", open(ref, "rb").read(), "image/jpeg"))], llave=llave)
        for i, d in enumerate(res["data"]):
            if "b64_json" in d: datos = base64.b64decode(d["b64_json"])
            else: datos = urllib.request.urlopen(d["url"], timeout=120).read()
            fn = f"{id_}{'' if i == 0 else '-' + str(i + 1)}.png"; open(os.path.join(OUT, fn), "wb").write(datos)
            print(f"  → {fn} ({len(datos)//1024} KB, {time.time() - t0:.0f} s)")
        indice[id_] = dict(modelo=modelo, calidad=calidad, tamano=tamano, prompt=prompt, fecha=time.strftime("%Y-%m-%d %H:%M"), archivo=f"{id_}.png")
        json.dump(indice, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("ids", nargs="*"); ap.add_argument("--modelo", default="gpt-image-2"); ap.add_argument("--calidad", default="high")
    ap.add_argument("--tamano", default="1536x1024"); ap.add_argument("--variantes", type=int, default=1); ap.add_argument("--prompts", action="store_true"); ap.add_argument("--sin-referencia", action="store_true")
    a = ap.parse_args(); ids = a.ids or ["calle", "casa", "aerea", "acceso", "bulevar", "parque", "pista", "interior", "portal", "noche"]
    if a.prompts:
        for k in ids: print(f"\n## {k}\n{PROMPTS[k]}")
        sys.exit(0)
    llave = os.environ.get("OPENAI_API_KEY")
    if not llave: raise SystemExit("Falta OPENAI_API_KEY en el entorno (no la pongas en el código ni en el repositorio).")
    generar(ids, a.modelo, a.calidad, a.tamano, a.variantes, llave, a.sin_referencia)
