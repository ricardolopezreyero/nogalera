"""Corre el flujo nogalera_flux_controlnet.json en un ComfyUI (máquina con GPU) para cada render de fotos_lista.json.
    python3 pipeline/comfy/correr.py --comfy http://localhost:8188 [--nombre fachada-horizonte] [--pasos 28] [--ancho 2048 --alto 1152]
Sube los mapas de control, rellena el prompt, espera el resultado y lo guarda en pipeline/comfy/salida/<nombre>.png."""
import argparse, json, os, sys, time, urllib.request, uuid
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
CTL = os.path.join(RAIZ, "public", "renders", "foto", "control"); OUT = os.path.join(AQUI, "salida"); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(RAIZ, "pipeline", "scripts"))
LISTA = json.load(open(os.path.join(RAIZ, "pipeline", "scripts", "fotos_lista.json")))
PROMPTS = json.load(open(os.path.join(RAIZ, "public", "datos", "escenas", "prompts_ia.json")))
HORA = dict(dia="a media mañana, luz clara", tarde="a media tarde, sol cálido y sombras largas", atardecer="al atardecer, hora dorada", noche="de noche, con los nogales iluminados desde abajo y las ventanas encendidas")
FACHADA = dict(cantera="fachada de cantera beige con cornisa y ventanas enmarcadas", ladrillo="planta alta de ladrillo rojo aparente sobre planta baja blanca, pérgola de madera", lamas="celosía de lamas verticales de madera en la planta alta",
               marco="un gran marco de concreto negro que envuelve la fachada", hacienda="muros blancos, pretil con moldura y portón enmarcado", concreto="concreto aparente con líneas de cimbra", celosia="celosía de barro rojo en la planta alta",
               duela="planta alta forrada de duela de madera", horizonte="dos losas que vuelan y una franja corrida de ventanas en la planta alta")
def api(comfy, ruta, datos=None, binario=None, ctype="application/json"):
    req = urllib.request.Request(comfy + ruta, data=binario if binario is not None else (json.dumps(datos).encode() if datos else None), headers={"content-type": ctype} if (datos or binario) else {})
    return urllib.request.urlopen(req).read()
def subir(comfy, archivo):
    lim = "----nogalera" + uuid.uuid4().hex; nombre = os.path.basename(archivo)
    cuerpo = (f"--{lim}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{nombre}\"\r\nContent-Type: image/png\r\n\r\n").encode() + open(archivo, "rb").read() + f"\r\n--{lim}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{lim}--\r\n".encode()
    return json.loads(api(comfy, "/upload/image", binario=cuerpo, ctype=f"multipart/form-data; boundary={lim}"))["name"]
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--comfy", default="http://localhost:8188"); ap.add_argument("--nombre"); ap.add_argument("--pasos", type=int, default=28); ap.add_argument("--ancho", type=int, default=2048); ap.add_argument("--alto", type=int, default=1152)
    a = ap.parse_args(); flujo = json.load(open(os.path.join(AQUI, "nogalera_flux_controlnet.json")))
    for nombre, escena, hora, vista, w, h in LISTA:
        if a.nombre and nombre != a.nombre: continue
        d, l = os.path.join(CTL, f"{nombre}-depth.png"), os.path.join(CTL, f"{nombre}-lineart.png")
        if not (os.path.exists(d) and os.path.exists(l)): print("faltan mapas de", nombre, "(corre fotos.js --control)"); continue
        fach = next((k for k in FACHADA if k in (vista or "")), None)
        prompt = PROMPTS.get(escena, "") + " " + HORA.get(hora, "") + (". La casa del centro: " + FACHADA[fach] + "." if fach else "") + " Fotografía arquitectónica real, lente 35 mm, nitidez de cámara réflex, materiales reales, nogales pecaneros adultos."
        f = json.loads(json.dumps(flujo)); f["5"]["inputs"]["text"] = prompt; f["8"]["inputs"]["image"] = subir(a.comfy, d); f["9"]["inputs"]["image"] = subir(a.comfy, l)
        f["15"]["inputs"].update(width=a.ancho, height=a.alto); f["16"]["inputs"]["steps"] = a.pasos; f["21"]["inputs"]["filename_prefix"] = "nogalera/" + nombre
        pid = json.loads(api(a.comfy, "/prompt", {"prompt": f, "client_id": "nogalera"}))["prompt_id"]; print(nombre, "en cola", pid, flush=True)
        while True:
            time.sleep(5); h_ = json.loads(api(a.comfy, "/history/" + pid))
            if pid in h_:
                for nodo in h_[pid]["outputs"].values():
                    for im in nodo.get("images", []):
                        datos = api(a.comfy, f"/view?filename={im['filename']}&subfolder={im.get('subfolder', '')}&type={im['type']}"); open(os.path.join(OUT, nombre + ".png"), "wb").write(datos); print("  →", os.path.join(OUT, nombre + ".png"))
                break
if __name__ == "__main__": main()
