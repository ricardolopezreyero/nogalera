/* Genera los renders fotorrealistas (WebGL, public/render/foto3d.js) y sus mapas de control para ControlNet.
   Uso: desde public/ corre `python3 -m http.server 8787` y luego
        NODE_PATH=/opt/node-tools/node_modules node pipeline/scripts/fotos.js [--lista pipeline/scripts/fotos_lista.json] [--control] [nombre…]
   Salida: public/renders/foto/img/<nombre>.jpg (el render) y, con --control, public/renders/foto/control/<nombre>-{depth,normal,lineart}.png
   La lista: [[nombre, escena, hora, vista, ancho, alto], …]. Cada render tarda de 20 s a 3 min en CPU (SwiftShader); con GPU, segundos. */
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const RAIZ = path.resolve(__dirname, "..", ".."), IMG = path.join(RAIZ, "public", "renders", "foto", "img"), CTL = path.join(RAIZ, "public", "renders", "foto", "control");
(async () => {
  let args = process.argv.slice(2), lista = path.join(__dirname, "fotos_lista.json"), control = false;
  const iL = args.indexOf("--lista"); if (iL >= 0) { lista = path.resolve(args[iL + 1]); args.splice(iL, 2); }
  const iC = args.indexOf("--control"); if (iC >= 0) { control = true; args.splice(iC, 1); }
  const trabajos = JSON.parse(fs.readFileSync(lista, "utf8")).filter(t => !args.length || args.includes(t[0]));
  fs.mkdirSync(IMG, { recursive: true }); if (control) fs.mkdirSync(CTL, { recursive: true });
  const b = await chromium.launch({ executablePath: process.env.CHROME || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  p.on("pageerror", e => console.log("error:", String(e)));
  await p.goto("http://localhost:8787/renders/foto/", { waitUntil: "networkidle" }); await p.evaluate(() => window.FOTO.listo);
  const guarda = (archivo, url) => fs.writeFileSync(archivo, Buffer.from(url.split(",")[1], "base64"));
  for (const [nombre, escena, hora, vista, w, h] of trabajos) {
    const t0 = Date.now();
    const url = await p.evaluate(o => window.FOTO.render(o).catch(e => "ERR " + e.stack), { escena, hora, vista: vista || "", w: w || 1920, h: h || 1080, calidad: 0.93 });
    if (url.startsWith("ERR")) { console.log(nombre, url); continue; }
    guarda(path.join(IMG, nombre + ".jpg"), url);
    if (control) for (const tipo of ["depth", "normal", "lineart"]) {
      const u = await p.evaluate(o => window.FOTO.control(o), { escena, vista: vista || "", w: w || 1920, h: h || 1080, tipo }); guarda(path.join(CTL, nombre + "-" + tipo + ".png"), u);
    }
    console.log(nombre, escena, hora, vista || "(principal)", (w || 1920) + "x" + (h || 1080), Math.round((Date.now() - t0) / 1000) + " s", Math.round(fs.statSync(path.join(IMG, nombre + ".jpg")).size / 1024) + " KB");
  }
  await b.close();
})();
