"""Genera el render fotorrealista con gpt-image-2 a través del Worker del sitio (la llave de OpenAI vive en Cloudflare), usando como
referencia el render WebGL de public/renders/foto/img/. Sirve desde cualquier computadora con internet, sin llave local.
    python3 pipeline/scripts/renders_worker.py --clave 123 [--nombre fachada-horizonte] [--sitio https://nogalera.capitaltorreon.com] [--calidad high]"""
import argparse, base64, json, os, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
IMG = os.path.join(RAIZ, "public", "renders", "foto", "img"); OUT = os.path.join(RAIZ, "pipeline", "comfy", "salida"); os.makedirs(OUT, exist_ok=True)
LISTA = json.load(open(os.path.join(AQUI, "fotos_lista.json"))); PROMPTS = json.load(open(os.path.join(RAIZ, "public", "datos", "escenas", "prompts_ia.json")))
HORA = dict(dia="a media mañana", tarde="a media tarde, con sol cálido", atardecer="al atardecer", noche="de noche")
ap = argparse.ArgumentParser(); ap.add_argument("--clave", required=True); ap.add_argument("--nombre"); ap.add_argument("--sitio", default="https://nogalera.capitaltorreon.com"); ap.add_argument("--calidad", default="high"); ap.add_argument("--modelo", default="gpt-image-2")
a = ap.parse_args()
for nombre, escena, hora, vista, w, h in LISTA:
    if a.nombre and nombre != a.nombre: continue
    ruta = os.path.join(IMG, nombre + ".jpg")
    if not os.path.exists(ruta): print("falta", ruta); continue
    ref = "data:image/jpeg;base64," + base64.b64encode(open(ruta, "rb").read()).decode()
    prompt = PROMPTS.get(escena, "") + " Hora: " + HORA.get(hora, "") + ". Conserva exactamente la geometría, el encuadre y la posición de cada elemento de la imagen de referencia; sólo vuélvela una fotografía real de cámara réflex, lente 35 mm."
    datos = json.dumps(dict(prompt=prompt, modelo=a.modelo, calidad=a.calidad, tamano="1536x1024", variantes=1, referencia=ref)).encode()
    req = urllib.request.Request(a.sitio + "/api/render-ia", data=datos, headers={"content-type": "application/json", "x-clave": a.clave})
    print(nombre, "generando…", flush=True); r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    if r.get("error"): print("  error:", r["error"], r.get("detalle", "")); continue
    for i, src in enumerate(r["imagenes"]):
        salida = os.path.join(OUT, nombre + ("-ia" if i == 0 else f"-ia{i + 1}") + ".png")
        if src.startswith("data:"): open(salida, "wb").write(base64.b64decode(src.split(",")[1]))
        else: urllib.request.urlretrieve(src, salida)
        print("  →", salida, round(r["ms"] / 1000), "s")
