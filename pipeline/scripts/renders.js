/* Genera los renders de /renders/ (public/renders/img/<id>.jpg) con el creador en Chromium.
   Uso: desde public/ corre `python3 -m http.server 8787` y luego `NODE_PATH=/opt/node-tools/node_modules node pipeline/scripts/renders.js [id…]`. */
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const RAIZ = path.resolve(__dirname, "..", ".."), IMG = path.join(RAIZ, "public", "renders", "img");
const W = 1920, H = 1080, SS = 2;
(async () => {
  fs.mkdirSync(IMG, { recursive: true });
  const indice = JSON.parse(fs.readFileSync(path.join(RAIZ, "public", "datos", "escenas", "index.json"), "utf8"));
  const pedidos = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: process.env.CHROME || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
  const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  p.on("pageerror", e => console.log("error:", String(e)));
  for (const e of indice) {
    if (pedidos.length && !pedidos.includes(e.id)) continue;
    const t0 = Date.now();
    await p.goto("http://localhost:8787/renders/?escena=" + e.id + "#crear", { waitUntil: "networkidle" });
    await p.evaluate(() => window.CREADOR.listo);
    const url = await p.evaluate(([w, h, ss]) => window.CREADOR.imagen(w, h, ss, "image/jpeg", 0.9), [W, H, SS]);
    fs.writeFileSync(path.join(IMG, e.id + ".jpg"), Buffer.from(url.split(",")[1], "base64"));
    console.log(e.id, Math.round((Date.now() - t0) / 100) / 10 + " s", Math.round(fs.statSync(path.join(IMG, e.id + ".jpg")).size / 1024) + " KB");
  }
  await b.close();
})();
