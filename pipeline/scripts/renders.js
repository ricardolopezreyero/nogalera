/* Genera los renders de /renders/ (public/renders/img/<id>.jpg) con el creador en Chromium.
   Uso: desde public/ corre `python3 -m http.server 8787` y luego `NODE_PATH=/opt/node-tools/node_modules node pipeline/scripts/renders.js [id…]`. */
/* Con --lista <archivo.json> genera una lista de encuadres [[nombre, escena, hora, vista], …] en public/inicio/img/<nombre>.jpg (la página del cliente). */
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const RAIZ = path.resolve(__dirname, "..", ".."), IMG = path.join(RAIZ, "public", "renders", "img");
const W = 1920, H = 1080, SS = 2;
(async () => {
  fs.mkdirSync(IMG, { recursive: true });
  const indice = JSON.parse(fs.readFileSync(path.join(RAIZ, "public", "datos", "escenas", "index.json"), "utf8"));
  let pedidos = process.argv.slice(2), lista = null, salida = IMG;
  const iL = pedidos.indexOf("--lista");
  if (iL >= 0) { lista = JSON.parse(fs.readFileSync(path.resolve(pedidos[iL + 1]), "utf8")); salida = path.join(RAIZ, "public", "inicio", "img"); pedidos = pedidos.slice(iL + 2); fs.mkdirSync(salida, { recursive: true }); }
  const trabajos = lista ? lista.filter(t => !pedidos.length || pedidos.includes(t[0])).map(([nombre, id, hora, vista]) => ({ nombre, url: `/renders/?escena=${id}&hora=${hora}&vista=${vista}#crear` }))
                         : indice.filter(e => !pedidos.length || pedidos.includes(e.id)).map(e => ({ nombre: e.id, url: `/renders/?escena=${e.id}#crear` }));
  const b = await chromium.launch({ executablePath: process.env.CHROME || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
  const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  p.on("pageerror", e => console.log("error:", String(e)));
  for (const t of trabajos) {
    const t0 = Date.now();
    await p.goto("http://localhost:8787" + t.url, { waitUntil: "networkidle" });
    await p.evaluate(() => window.CREADOR.listo);
    const url = await p.evaluate(([w, h, ss]) => window.CREADOR.imagen(w, h, ss, "image/jpeg", 0.9), [W, H, SS]);
    const archivo = path.join(salida, t.nombre + ".jpg");
    fs.writeFileSync(archivo, Buffer.from(url.split(",")[1], "base64"));
    console.log(t.nombre, Math.round((Date.now() - t0) / 100) / 10 + " s", Math.round(fs.statSync(archivo).size / 1024) + " KB");
  }
  await b.close();
})();
