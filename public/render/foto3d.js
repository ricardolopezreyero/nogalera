/* La Nogalera · motor de render fotorrealista (WebGL con three.js). Lee las mismas escenas que render3d.js
   (prismas [puntos xy, z, alto, color, grupo, material] y luces) y las convierte en materiales físicos con texturas
   procedurales, follaje de hojas reales para los nogales, cielo físico con sol, sombras suaves, oclusión ambiental,
   bloom y mapeo tonal de cámara. Uso: const F = new Foto3D(canvas); await F.cargar(escena); F.render({cam, hora, w, h}) → dataURL. */
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { GTAOPass } from "three/addons/postprocessing/GTAOPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { SMAAPass } from "three/addons/postprocessing/SMAAPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { Sky } from "three/addons/objects/Sky.js";
import * as BGU from "three/addons/utils/BufferGeometryUtils.js";

/* ---------- horas: sol, cielo, exposición ---------- */
const HORAS = {
  dia:       { sol: [-0.3, -0.62, 0.72], int: 4.0, colSol: 0xfff4e6, hemi: [0xbfd8f2, 0x8a7a5a, 0.6], turb: 2.5, ray: 1.1, mie: 0.003, mieG: 0.8, expo: 0.8, env: 0.06, bloom: [0.05, 0.4, 1.0], bruma: 0.0012, noche: false, pl: 0, emis: 0 },
  tarde:     { sol: [-0.6, -0.58, 0.48], int: 3.6, colSol: 0xffe2b8, hemi: [0xb9d0ec, 0x8a7a5a, 0.55], turb: 4, ray: 1.6, mie: 0.005, mieG: 0.82, expo: 0.85, env: 0.07, bloom: [0.07, 0.4, 1.0], bruma: 0.0015, noche: false, pl: 0, emis: 0 },
  atardecer: { sol: [-0.9, -0.32, 0.2], int: 2.8, colSol: 0xffb978, hemi: [0x7f93b8, 0x6e5a44, 0.45], turb: 9, ray: 3.0, mie: 0.02, mieG: 0.9, expo: 0.85, env: 0.07, bloom: [0.15, 0.5, 0.9], bruma: 0.002, noche: false, pl: 1.5, emis: 1.2 },
  noche:     { sol: [-0.3, -0.4, 0.87], int: 0.6, colSol: 0x8aa0ff, hemi: [0x1c2a4a, 0x0c0f16, 0.5], turb: 2, ray: 0.5, mie: 0.001, mieG: 0.7, expo: 1.3, env: 0.15, bloom: [0.3, 0.6, 0.75], bruma: 0.0025, noche: true, pl: 8.0, emis: 1.4 }
};
const COPAS = new Set(["#4f8f3c", "#5a9a44", "#467f36", "#5f9e4b", "#7fae5a", "#9bbf6a", "#6a9c4e"]);
const ARBUSTOS = new Set(["#6f9a4a", "#5f8c42", "#8aa85e", "#4f7d3a"]);

/* ---------- texturas procedurales ---------- */
function lienzo(n) { const c = document.createElement("canvas"); c.width = c.height = n; return [c, c.getContext("2d", { willReadFrequently: true })]; }
let semilla = 7;
function rnd() { semilla = (semilla * 1103515245 + 12345) & 0x7fffffff; return semilla / 0x7fffffff; }
function ruido(ctx, n, fuerza, escala, base) {
  // ruido de valor en varias octavas sobre la imagen (modula luminancia)
  const img = ctx.getImageData(0, 0, n, n), d = img.data;
  const oct = [];
  for (let o = 0; o < 4; o++) { const s = Math.max(2, Math.round(escala / Math.pow(2, o))), g = new Float32Array(s * s); for (let i = 0; i < s * s; i++) g[i] = rnd(); oct.push([s, g]); }
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    let v = 0, amp = 1, tot = 0;
    for (const [s, g] of oct) {
      const fx = x / n * s, fy = y / n * s, x0 = Math.floor(fx) % s, y0 = Math.floor(fy) % s, x1 = (x0 + 1) % s, y1 = (y0 + 1) % s, tx = fx - Math.floor(fx), ty = fy - Math.floor(fy);
      const sx = tx * tx * (3 - 2 * tx), sy = ty * ty * (3 - 2 * ty);
      const a = g[y0 * s + x0] * (1 - sx) + g[y0 * s + x1] * sx, b = g[y1 * s + x0] * (1 - sx) + g[y1 * s + x1] * sx;
      v += (a * (1 - sy) + b * sy) * amp; tot += amp; amp *= 0.5;
    }
    v = v / tot - 0.5; const i = (y * n + x) * 4, k = 1 + v * fuerza * 2 + (base || 0);
    d[i] = Math.max(0, Math.min(255, d[i] * k)); d[i + 1] = Math.max(0, Math.min(255, d[i + 1] * k)); d[i + 2] = Math.max(0, Math.min(255, d[i + 2] * k));
  }
  ctx.putImageData(img, 0, 0);
}
function normalDe(c, n, fuerza) {
  // mapa de normales a partir de la luminancia (Sobel)
  const ctx = c.getContext("2d"), src = ctx.getImageData(0, 0, n, n).data, [c2, x2] = lienzo(n), out = x2.createImageData(n, n), d = out.data;
  const L = (x, y) => { x = (x + n) % n; y = (y + n) % n; const i = (y * n + x) * 4; return (src[i] * 0.3 + src[i + 1] * 0.59 + src[i + 2] * 0.11) / 255; };
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const dx = (L(x + 1, y) - L(x - 1, y)) * fuerza, dy = (L(x, y + 1) - L(x, y - 1)) * fuerza, l = Math.hypot(dx, dy, 1), i = (y * n + x) * 4;
    d[i] = (-dx / l * 0.5 + 0.5) * 255; d[i + 1] = (-dy / l * 0.5 + 0.5) * 255; d[i + 2] = (1 / l * 0.5 + 0.5) * 255; d[i + 3] = 255;
  }
  x2.putImageData(out, 0, 0); return c2;
}
function tex(c, metros, srgb) {
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1 / metros, 1 / metros); t.anisotropy = 8;
  if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.needsUpdate = true; return t;
}
const TEX = {};
function texturas() {
  let c, x, n;
  // pasto: base verde con ruido fino y manchas
  n = 1024; [c, x] = lienzo(n); x.fillStyle = "#6f9a48"; x.fillRect(0, 0, n, n); ruido(x, n, 0.35, 160); ruido(x, n, 0.18, 12);
  for (let i = 0; i < 14000; i++) { x.fillStyle = `rgba(${40 + rnd() * 60 | 0},${90 + rnd() * 70 | 0},${30 + rnd() * 40 | 0},0.55)`; const px = rnd() * n, py = rnd() * n; x.fillRect(px, py, 1 + rnd() * 2, 3 + rnd() * 7); }
  TEX.pasto = [tex(c, 3, true), tex(normalDe(c, n, 1.2), 3)];
  // asfalto: gris oscuro granulado
  n = 1024; [c, x] = lienzo(n); x.fillStyle = "#4e4e4c"; x.fillRect(0, 0, n, n); ruido(x, n, 0.22, 200); ruido(x, n, 0.12, 24);
  for (let i = 0; i < 30000; i++) { x.fillStyle = `rgba(${150 + rnd() * 80 | 0},${150 + rnd() * 80 | 0},${150 + rnd() * 70 | 0},${0.08 + rnd() * 0.14})`; x.fillRect(rnd() * n, rnd() * n, 1, 1); }
  TEX.asfalto = [tex(c, 4, true), tex(normalDe(c, n, 0.6), 4)];
  // concreto / banqueta: claro, con juntas cada 1.5 m
  n = 1024; [c, x] = lienzo(n); x.fillStyle = "#c9c5bc"; x.fillRect(0, 0, n, n); ruido(x, n, 0.14, 120); ruido(x, n, 0.07, 18);
  x.strokeStyle = "rgba(60,58,54,0.55)"; x.lineWidth = 3; for (let k = 0; k <= 4; k++) { x.beginPath(); x.moveTo(k * n / 4, 0); x.lineTo(k * n / 4, n); x.moveTo(0, k * n / 4); x.lineTo(n, k * n / 4); x.stroke(); }
  TEX.concreto = [tex(c, 6, true), tex(normalDe(c, n, 0.8), 6)];
  // adoquín / andador: piezas 30 × 15
  n = 1024; [c, x] = lienzo(n); x.fillStyle = "#cfcac1"; x.fillRect(0, 0, n, n);
  const pw = n / 8, ph = n / 16;
  for (let j = 0; j < 16; j++) for (let i = -1; i < 9; i++) { const ox = (j % 2) * pw / 2; x.fillStyle = `hsl(${35 + rnd() * 10},${8 + rnd() * 8}%,${72 + rnd() * 10}%)`; x.fillRect(i * pw + ox + 2, j * ph + 2, pw - 4, ph - 4); }
  ruido(x, n, 0.1, 60); TEX.adoquin = [tex(c, 2.4, true), tex(normalDe(c, n, 1.0), 2.4)];
  // tierra / huerta
  n = 1024; [c, x] = lienzo(n); x.fillStyle = "#b9a883"; x.fillRect(0, 0, n, n); ruido(x, n, 0.3, 90); ruido(x, n, 0.15, 10);
  TEX.tierra = [tex(c, 8, true), tex(normalDe(c, n, 0.7), 8)];
  // aplanado de muro: ruido muy fino
  n = 512; [c, x] = lienzo(n); x.fillStyle = "#ffffff"; x.fillRect(0, 0, n, n); ruido(x, n, 0.08, 64); ruido(x, n, 0.05, 8);
  TEX.aplanado = [tex(c, 2.5, true), tex(normalDe(c, n, 0.35), 2.5)];
  // ladrillo: 24 × 6 cm con junta clara
  n = 1024; [c, x] = lienzo(n); x.fillStyle = "#d9d2c6"; x.fillRect(0, 0, n, n);
  const bw = n / 5, bh = n / 20;
  for (let j = 0; j < 20; j++) for (let i = -1; i < 6; i++) { const ox = (j % 2) * bw / 2; x.fillStyle = `hsl(${12 + rnd() * 10},${48 + rnd() * 14}%,${38 + rnd() * 12}%)`; x.fillRect(i * bw + ox + 3, j * bh + 3, bw - 6, bh - 6); }
  ruido(x, n, 0.12, 100); TEX.ladrillo = [tex(c, 1.2, true), tex(normalDe(c, n, 1.4), 1.2)];
  // madera: veta
  n = 512; [c, x] = lienzo(n); x.fillStyle = "#9a6a3a"; x.fillRect(0, 0, n, n);
  for (let k = 0; k < 140; k++) { x.strokeStyle = `rgba(${40 + rnd() * 50 | 0},${20 + rnd() * 30 | 0},${5 + rnd() * 15 | 0},${0.12 + rnd() * 0.25})`; x.lineWidth = 1 + rnd() * 3; x.beginPath(); const y0 = rnd() * n; x.moveTo(0, y0); x.bezierCurveTo(n * 0.3, y0 + (rnd() - 0.5) * 30, n * 0.7, y0 + (rnd() - 0.5) * 30, n, y0 + (rnd() - 0.5) * 10); x.stroke(); }
  ruido(x, n, 0.1, 30); TEX.madera = [tex(c, 1.5, true), tex(normalDe(c, n, 0.5), 1.5)];
  // corteza
  n = 512; [c, x] = lienzo(n); x.fillStyle = "#8a7560"; x.fillRect(0, 0, n, n);
  for (let k = 0; k < 400; k++) { x.strokeStyle = `rgba(${20 + rnd() * 40 | 0},${12 + rnd() * 25 | 0},${5 + rnd() * 10 | 0},${0.2 + rnd() * 0.5})`; x.lineWidth = 1 + rnd() * 4; x.beginPath(); const x0 = rnd() * n; x.moveTo(x0, 0); x.lineTo(x0 + (rnd() - 0.5) * 40, n); x.stroke(); }
  ruido(x, n, 0.25, 40); TEX.corteza = [tex(c, 1.2, true), tex(normalDe(c, n, 2.0), 1.2)];
  // cantera: sillares
  n = 1024; [c, x] = lienzo(n); x.fillStyle = "#bfae8c"; x.fillRect(0, 0, n, n);
  for (let j = 0; j < 8; j++) for (let i = -1; i < 5; i++) { const ox = (j % 2) * n / 8; x.fillStyle = `hsl(${38 + rnd() * 8},${22 + rnd() * 10}%,${62 + rnd() * 10}%)`; x.fillRect(i * n / 4 + ox + 3, j * n / 8 + 3, n / 4 - 6, n / 8 - 6); }
  ruido(x, n, 0.14, 80); TEX.cantera = [tex(c, 2.0, true), tex(normalDe(c, n, 1.0), 2.0)];
  // hoja: ramillete de hojas compuestas de nogal pecanero (alfa)
  n = 512; [c, x] = lienzo(n); x.clearRect(0, 0, n, n);
  for (let r = 0; r < 7; r++) {
    const ang = -Math.PI / 2 + (r - 3) * 0.5 + (rnd() - 0.5) * 0.3, L = n * (0.4 + rnd() * 0.1), cx = n / 2 + (rnd() - 0.5) * 60, cy = n * 0.6 + (rnd() - 0.5) * 60;
    x.save(); x.translate(cx, cy); x.rotate(ang);
    x.strokeStyle = "rgba(70,60,30,0.9)"; x.lineWidth = 3; x.beginPath(); x.moveTo(0, 0); x.lineTo(L, 0); x.stroke();
    const nf = 9 + Math.floor(rnd() * 4);
    for (let k = 0; k < nf; k++) {
      const t = (k + 1) / (nf + 1), px = t * L, lado = k % 2 ? 1 : -1, lh = n * (0.075 + rnd() * 0.03) * (1 - 0.3 * t), lw = lh * 0.3;
      const g = `hsl(${95 + rnd() * 25},${36 + rnd() * 20}%,${24 + rnd() * 14}%)`;
      x.save(); x.translate(px, 0); x.rotate(lado * (0.9 + rnd() * 0.4)); x.fillStyle = g; x.beginPath(); x.ellipse(lh * 0.55, 0, lh * 0.55, lw, 0, 0, Math.PI * 2); x.fill();
      x.strokeStyle = "rgba(255,255,255,0.18)"; x.lineWidth = 1; x.beginPath(); x.moveTo(0, 0); x.lineTo(lh, 0); x.stroke(); x.restore();
    }
    x.save(); x.translate(L, 0); x.rotate(0); x.fillStyle = `hsl(${100 + rnd() * 20},${45}%,${32}%)`; x.beginPath(); x.ellipse(n * 0.03, 0, n * 0.035, n * 0.015, 0, 0, Math.PI * 2); x.fill(); x.restore();
    x.restore();
  }
  TEX.hoja = new THREE.CanvasTexture(c); TEX.hoja.colorSpace = THREE.SRGBColorSpace; TEX.hoja.anisotropy = 8;
  // brizna: un manojo de hojas de pasto (alfa)
  n = 256; [c, x] = lienzo(n); x.clearRect(0, 0, n, n);
  for (let k = 0; k < 26; k++) {
    const x0 = n * (0.3 + rnd() * 0.4), h = n * (0.45 + rnd() * 0.5), dx = (rnd() - 0.5) * n * 0.5, wdt = 2 + rnd() * 3;
    x.strokeStyle = `hsl(${85 + rnd() * 30},${40 + rnd() * 25}%,${22 + rnd() * 22}%)`; x.lineWidth = wdt; x.lineCap = "round";
    x.beginPath(); x.moveTo(x0, n); x.quadraticCurveTo(x0 + dx * 0.3, n - h * 0.6, x0 + dx, n - h); x.stroke();
  }
  TEX.brizna = new THREE.CanvasTexture(c); TEX.brizna.colorSpace = THREE.SRGBColorSpace;
}

/* ---------- geometría: prismas → caras con UV planar ---------- */
function col(s) { return [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16), s.length > 7 ? parseInt(s.slice(7, 9), 16) / 255 : 1]; }
function prismaGeo(pts, z0, h, uvEsc) {
  const n = pts.length, pos = [], nor = [], uv = [], idx = [];
  let area = 0; for (let i = 0; i < n; i++) { const a = pts[i], b = pts[(i + 1) % n]; area += a[0] * b[1] - b[0] * a[1]; }
  if (area < 0) pts = pts.slice().reverse();
  const tri = THREE.ShapeUtils.triangulateShape(pts.map(p => new THREE.Vector2(p[0], p[1])), []);
  // tapa
  let base = 0;
  for (const p of pts) { pos.push(p[0], p[1], z0 + h); nor.push(0, 0, 1); uv.push(p[0] * uvEsc, p[1] * uvEsc); }
  for (const t of tri) idx.push(base + t[0], base + t[1], base + t[2]);
  base = pos.length / 3;
  for (const p of pts) { pos.push(p[0], p[1], z0); nor.push(0, 0, -1); uv.push(p[0] * uvEsc, p[1] * uvEsc); }
  for (const t of tri) idx.push(base + t[2], base + t[1], base + t[0]);
  // lados
  let s = 0;
  for (let i = 0; i < n; i++) {
    const a = pts[i], b = pts[(i + 1) % n], dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1, nx = dy / l, ny = -dx / l;
    base = pos.length / 3;
    pos.push(a[0], a[1], z0, b[0], b[1], z0, b[0], b[1], z0 + h, a[0], a[1], z0 + h);
    for (let k = 0; k < 4; k++) nor.push(nx, ny, 0);
    uv.push(s * uvEsc, z0 * uvEsc, (s + l) * uvEsc, z0 * uvEsc, (s + l) * uvEsc, (z0 + h) * uvEsc, s * uvEsc, (z0 + h) * uvEsc);
    idx.push(base, base + 1, base + 2, base, base + 2, base + 3); s += l;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3)); g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx);
  return g;
}
function centroRadio(pts) {
  let cx = 0, cy = 0; for (const p of pts) { cx += p[0]; cy += p[1]; } cx /= pts.length; cy /= pts.length;
  let r = 0; for (const p of pts) r += Math.hypot(p[0] - cx, p[1] - cy); return [cx, cy, r / pts.length];
}

/* ---------- clasificación de materiales ---------- */
function clase(p) {
  const [pts, z, h, c, g, mat] = p, [r, gg, b, a] = col(c), hex = c.slice(0, 7), [, , rad] = centroRadio(pts);
  if (mat === "luz") return "luz";
  if (g === "arboles") return rad > 0.9 ? "copa" : "corteza";
  if (g === "plantas") return rad > 0.22 ? (rad > 0.9 ? "copa" : "arbusto") : "corteza";
  if (a < 1) return "vidrio";
  if (g === "suelo" || mat === "suelo") {
    if (hex === "#86b35f" || hex === "#7aa855") return "pasto";
    if (hex === "#5c5c5c" || hex === "#5a5a5a") return "asfalto";
    if (hex === "#c9b89a" || hex === "#d8cdb3") return "tierra";
    if (hex === "#dad7d0" || hex === "#d0cdc5" || hex === "#e2ded4") return "adoquin";
    if (hex === "#c6c2b9" || hex === "#c3bfb6" || hex === "#a9a59d" || hex === "#a8a49c") return "concreto";
    if (hex === "#b9b3a8") return "grava";
    return "mate";
  }
  if (hex === "#b3563f") return "ladrillo";
  if (hex === "#d6c6a4" || hex === "#bda98a") return "cantera";
  if (hex === "#8a5a2c" || hex === "#9a6a3a" || hex === "#5a4632" || hex === "#a97a4e" || hex === "#7a5a3a") return "madera";
  if (hex === "#33363a" || hex === "#3a3a3a" || hex === "#2a2a2a" || hex === "#3b3b3b" || hex === "#222222" || hex === "#1e1e1e" || hex === "#2b2b2b") return "metal";
  if (hex === "#b3bac1" || hex === "#c9c9c9" || hex === "#d8d8d8" || hex === "#8a8a8a") return "acero";
  if (g === "autos") return "auto";
  if (g === "casa" || g === "edif") return (hex === "#55534f" || hex === "#9a9a9a") ? "concreto_liso" : "aplanado";
  return "mate";
}

export class Foto3D {
  constructor(canvas) {
    this.cv = canvas;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, powerPreference: "high-performance" });
    this.renderer.shadowMap.enabled = true; this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping; this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    if (!Object.keys(TEX).length) texturas();
    this.pmrem = new THREE.PMREMGenerator(this.renderer);
    this.opciones = { gente: true, autos: true, ao: true, sombras: 4096, nueces: true, pasto: true };
  }
  /* materiales */
  material(k, hex, a) {
    const key = k + hex + a; if (this._mats && this._mats[key]) return this._mats[key];
    this._mats = this._mats || {};
    const c = new THREE.Color(hex); let m;
    const std = (o) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.9, metalness: 0 }, o));
    const t = (k2) => ({ map: TEX[k2][0], normalMap: TEX[k2][1] });
    switch (k) {
      case "pasto": m = std(Object.assign(t("pasto"), { color: c.clone().multiplyScalar(1.15), roughness: 1 })); break;
      case "asfalto": m = std(Object.assign(t("asfalto"), { color: new THREE.Color(0x8c8c8a), roughness: 0.95 })); break;
      case "tierra": m = std(Object.assign(t("tierra"), { color: c.clone().multiplyScalar(1.05), roughness: 1 })); break;
      case "adoquin": m = std(Object.assign(t("adoquin"), { color: c.clone().multiplyScalar(1.05), roughness: 0.85 })); break;
      case "concreto": m = std(Object.assign(t("concreto"), { color: c.clone().multiplyScalar(1.05), roughness: 0.9 })); break;
      case "grava": m = std(Object.assign(t("tierra"), { color: c, roughness: 1 })); break;
      case "ladrillo": m = std(Object.assign(t("ladrillo"), { color: new THREE.Color(0xffffff), roughness: 0.95 })); break;
      case "cantera": m = std(Object.assign(t("cantera"), { color: c.clone().multiplyScalar(1.1), roughness: 0.9 })); break;
      case "madera": m = std(Object.assign(t("madera"), { color: c.clone().multiplyScalar(1.15), roughness: 0.6 })); break;
      case "corteza": m = std(Object.assign(t("corteza"), { color: c.clone().multiplyScalar(1.7), roughness: 1 })); break;
      case "aplanado": m = std(Object.assign(t("aplanado"), { color: c, roughness: 0.85 })); break;
      case "concreto_liso": m = std(Object.assign(t("aplanado"), { color: c, roughness: 0.7 })); break;
      case "metal": m = std({ roughness: 0.45, metalness: 0.6 }); break;
      case "acero": m = std({ roughness: 0.35, metalness: 0.8 }); break;
      case "auto": m = new THREE.MeshPhysicalMaterial({ color: c, roughness: 0.25, metalness: 0.5, clearcoat: 1, clearcoatRoughness: 0.08 }); break;
      case "vidrio": m = new THREE.MeshPhysicalMaterial({ color: c.clone().multiplyScalar(0.75), roughness: 0.03, metalness: 0.35, transparent: true, opacity: Math.min(0.9, 0.45 + a * 0.35), envMapIntensity: 2.4, side: THREE.DoubleSide, depthWrite: false, clearcoat: 1, clearcoatRoughness: 0.02 }); break;
      case "luz": m = new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: 1.4, roughness: 0.6 }); m.userData.luz = true; break;
      case "arbusto": m = std({ color: c, roughness: 1 }); break;
      default: m = std({});
    }
    this._mats[key] = m; return m;
  }
  /* carga la escena: geometría por material, follaje instanciado, luces */
  async cargar(esc) {
    this.esc = esc; this.luces = esc.luces || []; this.lamparas = []; this.pastos = [];
    const scene = this.scene = new THREE.Scene();
    const grupos = {}; const copas = []; const arbustos = []; const hayCopas = (esc.copas || []).length > 0;
    for (const p of esc.prismas) {
      if (p[4] === "gente" && !this.opciones.gente) continue;
      if (p[4] === "autos" && !this.opciones.autos) continue;
      if (p[4] === "arboles_lod") { if (hayCopas) continue; else p[4] = "arboles"; }
      const k = clase(p);
      if (k === "pasto") this.pastos.push([p[0], p[1] + p[2]]);
      if (k === "copa" || k === "arbusto") { copas.push(p); continue; }
      if (p[4] === "luz" && (p[3] === "#e6e6e6" || p[3] === "#eaeaea") && p[0].length === 4) { const [cx, cy] = centroRadio(p[0]); this.lamparas.push([cx, cy, p[1] - 0.15]); }
      const uvEsc = 1; const g = prismaGeo(p[0], p[1], p[2], uvEsc);
      const key = k + "|" + p[3].slice(0, 7) + "|" + (p[4] === "muebles" ? "m" : "");
      (grupos[key] = grupos[key] || { k, hex: p[3].slice(0, 7), a: col(p[3])[3], geos: [] }).geos.push(g);
    }
    for (const key in grupos) {
      const G = grupos[key], geo = BGU.mergeGeometries(G.geos, false); G.geos.forEach(g => g.dispose());
      const mesh = new THREE.Mesh(geo, this.material(G.k, G.hex, G.a));
      mesh.castShadow = G.k !== "vidrio" && G.k !== "pasto" && G.k !== "asfalto" && G.k !== "tierra" && G.k !== "adoquin" && G.k !== "concreto" && G.k !== "grava";
      mesh.receiveShadow = true; if (G.k === "vidrio") mesh.renderOrder = 10;
      scene.add(mesh);
    }
    // clusters de follaje: elipsoides [cx, cy, cz, rx, ry, rz, color, nogal]; de las copas del generador y de los prismas de copa (arbustos, nogales simples)
    this.clusters = (esc.copas || []).map(c => [c[0], c[1], c[2], c[3], c[4], c[5], c[6].slice(0, 7), true]);
    for (const p of copas) { const [cx, cy, r] = centroRadio(p[0]); this.clusters.push([cx, cy, p[1] + p[2] / 2, r, r, p[2] / 2, p[3].slice(0, 7), r >= 0.9]); }
    this.ramas(esc.ramas || []); this.suelo(); return this;
  }
  ramas(lista) {
    // ramas inclinadas del generador de nogales: cilindros orientados, agrupados por color (corteza / encalado)
    if (!lista.length) return;
    const por = {}; const up = new THREE.Vector3(0, 1, 0), dir = new THREE.Vector3(), q = new THREE.Quaternion(), mid = new THREE.Vector3();
    for (const [x0, y0, z0, x1, y1, z1, r0, r1, col] of lista) {
      dir.set(x1 - x0, y1 - y0, z1 - z0); const L = dir.length(); if (L < 0.01) continue; dir.divideScalar(L);
      const seg = r0 > 0.12 ? 8 : (r0 > 0.06 ? 6 : 4);
      const g = new THREE.CylinderGeometry(r1, r0, L, seg, 1, true); q.setFromUnitVectors(up, dir); g.applyQuaternion(q); mid.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); g.translate(mid.x, mid.y, mid.z);
      const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * Math.max(0.3, r0 * 6), uv.getY(i) * L);
      (por[col] = por[col] || []).push(g);
    }
    for (const col in por) {
      const geo = BGU.mergeGeometries(por[col], false); por[col].forEach(g => g.dispose());
      const esCal = col === "#e9e7e0"; const m = esCal ? new THREE.MeshStandardMaterial({ color: 0xf2f0ea, roughness: 0.95, map: TEX.aplanado[0] }) : this.material("corteza", col, 1);
      const mesh = new THREE.Mesh(geo, m); mesh.castShadow = true; mesh.receiveShadow = true; this.scene.add(mesh);
    }
    this.nRamas = lista.length;
  }
  follaje(cam) {
    // tarjetas de hojas instanciadas dentro de cada cluster; la densidad depende de la distancia al ojo (se rehace en cada render)
    if (this.hojasMesh) { this.scene.remove(this.hojasMesh); this.hojasMesh.geometry.dispose(); this.hojasMesh = null; }
    if (this.nuecesMesh) { this.scene.remove(this.nuecesMesh); this.nuecesMesh.geometry.dispose(); this.nuecesMesh = null; }
    const cl = this.clusters || []; if (!cl.length) return;
    const sa = Math.sin(cam.az), ca = Math.cos(cam.az), ce = Math.cos(cam.el), se = Math.sin(cam.el);
    const ex = cam.cx - sa * ce * cam.dist, ey = cam.cy - ca * ce * cam.dist, ez = cam.cz + se * cam.dist;
    const dens = d => d < 50 ? 1 : d < 120 ? 0.6 : d < 300 ? 0.3 : d < 800 ? 0.12 : 0.05;
    const plano = new THREE.PlaneGeometry(1, 1), p2 = plano.clone().rotateY(Math.PI / 2), geo = BGU.mergeGeometries([plano, p2], false);
    const info = []; let total = 0;
    for (const c of cl) {
      const d = Math.hypot(c[0] - ex, c[1] - ey, c[2] - ez); const vol = 4.19 * c[3] * c[4] * c[5];
      const n = Math.max(3, Math.round(vol * (c[7] ? 30 : 60) * dens(d))); info.push([c, n, d]); total += n;
    }
    const tope = 1100000, f = total > tope ? tope / total : 1;
    const cuenta = info.reduce((s_, i) => s_ + Math.max(3, Math.round(i[1] * f)), 0);
    const mat = new THREE.MeshStandardMaterial({ map: TEX.hoja, alphaTest: 0.5, side: THREE.DoubleSide, roughness: 0.8, metalness: 0, color: 0xffffff, emissive: 0x2a4a14, emissiveIntensity: 0.18 });
    const im = new THREE.InstancedMesh(geo, mat, cuenta); im.castShadow = true; im.receiveShadow = true;
    im.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: TEX.hoja, alphaTest: 0.5, side: THREE.DoubleSide });
    const M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), sv = new THREE.Vector3(), pos = new THREE.Vector3(), col = new THREE.Color();
    let i = 0; const nuez = [];
    for (const [c, n0, d] of info) {
      const n = Math.max(3, Math.round(n0 * f)), base = new THREE.Color(c[6]); const rm = (c[3] + c[4] + c[5]) / 3;
      const tam = (c[7] ? Math.min(1.0, Math.max(0.45, rm * 0.55)) : Math.max(0.3, rm * 0.8)) * Math.min(2.5, 1 / Math.sqrt(Math.max(0.05, f * dens(d))));
      for (let k = 0; k < n; k++) {
        const u = rnd(), v = rnd(), w = Math.cbrt(rnd()) * 0.92 + 0.08, th = u * Math.PI * 2, ph = Math.acos(2 * v - 1);
        pos.set(c[0] + c[3] * w * Math.sin(ph) * Math.cos(th), c[1] + c[4] * w * Math.sin(ph) * Math.sin(th), c[2] + c[5] * w * Math.cos(ph));
        e.set(rnd() * 0.8 - 0.4 + (rnd() < 0.5 ? 0 : Math.PI / 2), rnd() * 0.6 - 0.3, rnd() * Math.PI * 2); q.setFromEuler(e);
        const t = tam * (0.75 + rnd() * 0.5); sv.set(t, t, t); M.compose(pos, q, sv); im.setMatrixAt(i, M);
        col.copy(base).multiplyScalar(1.2).offsetHSL((rnd() - 0.5) * 0.03, (rnd() - 0.5) * 0.1, (rnd() - 0.5) * 0.14); im.setColorAt(i, col); i++;
        if (c[7] && this.opciones.nueces && d < 90 && k % 4 === 0 && w > 0.75) nuez.push(pos.x, pos.y, pos.z);
      }
    }
    im.count = i; im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true; this.scene.add(im); this.hojasMesh = im; this.nHojas = i;
    // copas lejanas (más de 250 m): además de las pocas tarjetas, un volumen opaco de copa para que desde el aire se lea la masa verde
    if (this.lejosMesh) { this.scene.remove(this.lejosMesh); this.lejosMesh = null; }
    const lejos = info.filter(k => k[2] > 250 && k[0][7]);
    if (lejos.length) {
      const gL = new THREE.IcosahedronGeometry(1, 1), mL = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1, flatShading: true });
      const lm = new THREE.InstancedMesh(gL, mL, lejos.length); lm.castShadow = true; lm.receiveShadow = true;
      lejos.forEach(([c], idx) => { pos.set(c[0], c[1], c[2]); e.set(rnd() * 3, rnd() * 3, rnd() * 3); q.setFromEuler(e); sv.set(c[3] * 0.9, c[4] * 0.9, c[5] * 0.9); M.compose(pos, q, sv); lm.setMatrixAt(idx, M); col.set(c[6]).multiplyScalar(0.85).offsetHSL((rnd() - 0.5) * 0.03, 0, (rnd() - 0.5) * 0.1); lm.setColorAt(idx, col); });
      lm.instanceMatrix.needsUpdate = true; if (lm.instanceColor) lm.instanceColor.needsUpdate = true; this.scene.add(lm); this.lejosMesh = lm;
    }
    if (nuez.length) {
      // nueces: racimos de 2 o 3 frutos (3.5 cm, cáscara verde) cerca de la cámara
      const geoN = new THREE.SphereGeometry(0.018, 6, 5); geoN.scale(1, 1, 1.5); const matN = new THREE.MeshStandardMaterial({ color: 0x7a8a3a, roughness: 0.8 });
      const cnt = Math.min(260000, nuez.length), nz = new THREE.InstancedMesh(geoN, matN, cnt); let j = 0;
      for (let k = 0; k < cnt / 3 && j < cnt; k++) {
        const nr = 2 + (rnd() < 0.5 ? 1 : 0);
        for (let qn = 0; qn < nr && j < cnt; qn++) { pos.set(nuez[k * 3] + (rnd() - 0.5) * 0.06, nuez[k * 3 + 1] + (rnd() - 0.5) * 0.06, nuez[k * 3 + 2] - qn * 0.03); e.set(rnd() * 0.5, rnd() * 0.5, rnd() * 6.28); q.setFromEuler(e); const t = 0.9 + rnd() * 0.4; sv.set(t, t, t); M.compose(pos, q, sv); nz.setMatrixAt(j, M); col.setHSL(0.2 + rnd() * 0.05, 0.35 + rnd() * 0.2, 0.3 + rnd() * 0.15); nz.setColorAt(j, col); j++; }
      }
      nz.count = j; nz.instanceMatrix.needsUpdate = true; if (nz.instanceColor) nz.instanceColor.needsUpdate = true; this.scene.add(nz); this.nuecesMesh = nz; this.nNueces = j;
    }
  }
  suelo() {
    // el terreno hasta el horizonte, por debajo del suelo de la escena
    const z = (this.esc.suelo_z === undefined ? -0.32 : this.esc.suelo_z) - 0.75;
    const g = new THREE.PlaneGeometry(12000, 12000, 1, 1); g.translate(0, 0, z);
    const uv = g.attributes.uv; for (let i = 0; i < uv.count; i++) uv.setXY(i, uv.getX(i) * 12000, uv.getY(i) * 12000);
    const m = new THREE.Mesh(g, this.material("tierra", "#c4b48f", 1)); m.receiveShadow = true; this.scene.add(m);
  }
  /* cielo, sol y luces según la hora */
  iluminar(hora, cam) {
    const H = HORAS[hora] || HORAS.dia, scene = this.scene;
    if (this.luzGrupo) scene.remove(this.luzGrupo);
    const L = this.luzGrupo = new THREE.Group(); scene.add(L);
    const S = new THREE.Vector3(...H.sol).normalize();
    // cielo físico
    const sky = new Sky(); sky.scale.setScalar(50000); const u = sky.material.uniforms;
    u.turbidity.value = H.turb; u.rayleigh.value = H.ray; u.mieCoefficient.value = H.mie; u.mieDirectionalG.value = H.mieG;
    const Sl = H.noche ? new THREE.Vector3(0.3, 0.4, -0.3) : S;
    u.sunPosition.value.set(Sl.x, Sl.z, -Sl.y); sky.rotation.x = Math.PI / 2;          // el cielo trabaja con +Y arriba; nuestro mundo es +Z arriba
    u.cloudCoverage.value = H.noche ? 0.1 : (hora === "atardecer" ? 0.45 : 0.3); u.cloudDensity.value = 0.35; u.cloudScale.value = 0.00025; u.showSunDisc.value = 1;
    L.add(sky);
    const skyScene = new THREE.Scene(); skyScene.add(sky.clone()); skyScene.children[0].material = sky.material;
    const env = this.pmrem.fromScene(skyScene, 0, 1, 100000); scene.environment = env.texture; scene.environmentIntensity = H.env;
    if (H.noche) { scene.background = new THREE.Color(0x0a1226); } else scene.background = null;
    // sol
    const sol = new THREE.DirectionalLight(H.colSol, H.int); const foco = new THREE.Vector3(cam.cx, cam.cy, cam.cz);
    sol.position.copy(foco).addScaledVector(S, 800); sol.target.position.copy(foco); L.add(sol); L.add(sol.target);
    sol.castShadow = true; const ext = Math.min(700, Math.max(30, cam.dist * 1.6));
    sol.shadow.mapSize.set(this.opciones.sombras, this.opciones.sombras); sol.shadow.camera.left = -ext; sol.shadow.camera.right = ext; sol.shadow.camera.top = ext; sol.shadow.camera.bottom = -ext;
    sol.shadow.camera.near = 1; sol.shadow.camera.far = 2000; sol.shadow.bias = -0.0004; sol.shadow.normalBias = 0.02 + ext / 4000; sol.shadow.radius = 2;
    const hemi = new THREE.HemisphereLight(H.hemi[0], H.hemi[1], H.hemi[2]); hemi.position.set(0, 0, 1); L.add(hemi);
    // luces de la escena (noche y atardecer): las más cercanas a la cámara
    const luces = this.luces.length ? this.luces : this.lamparas.map(l => [l[0], l[1], l[2], 2.6, "#ffd9a0"]);
    for (const m of scene.children) if (m.isMesh && m.material.transparent && m.material.isMeshPhysicalMaterial) { m.material.emissive = new THREE.Color(0xffd9a0); m.material.emissiveIntensity = H.noche && !this.luces.length ? 0.9 : 0; }
    if (H.noche || hora === "atardecer") {
      const cerca = luces.map(l => [Math.hypot(l[0] - cam.cx, l[1] - cam.cy), l]).sort((a, b) => a[0] - b[0]).slice(0, 48);
      for (const [, l] of cerca) { const pl = new THREE.PointLight(l[4] || 0xffd9a0, H.pl * l[3], l[3] * 12, 2); pl.position.set(l[0], l[1], l[2]); L.add(pl); }
    }
    for (const m of scene.children) if (m.isMesh && m.material.emissive && m.material.emissiveIntensity !== undefined && m.material.userData.luz) m.material.emissiveIntensity = H.emis;
    scene.fog = new THREE.FogExp2(H.noche ? 0x0a1226 : (hora === "atardecer" ? 0xe8c9a8 : 0xdbe6f0), H.bruma * Math.min(1, 60 / Math.max(1, cam.dist)) * (this.esc.bruma && this.esc.bruma[1] ? 1 : 0.6));
    this.renderer.toneMappingExposure = H.expo; this.H = H;
  }
  /* cámara con los mismos parámetros que render3d.js (az, el, zoom, dist, cx, cy, cz) */
  camara(c, w, h) {
    const sa = Math.sin(c.az), ca = Math.cos(c.az), se = Math.sin(c.el), ce = Math.cos(c.el), f = new THREE.Vector3(sa * ce, ca * ce, -se);
    const centro = new THREE.Vector3(c.cx, c.cy, c.cz), ojo = centro.clone().addScaledVector(f, -c.dist);
    const F = Math.min(w, h) / 32 * Math.pow(1.15, c.zoom) * c.dist, fov = 2 * Math.atan(h / (2 * F)) * 180 / Math.PI;
    const cam = new THREE.PerspectiveCamera(fov, w / h, Math.max(0.2, c.dist / 400), 30000); cam.up.set(0, 0, 1); cam.position.copy(ojo); cam.lookAt(centro); cam.updateMatrixWorld(); return cam;
  }
  briznas(cam) {
    // manojos de pasto instanciados en un radio alrededor del ojo, sólo sobre superficies de pasto (más densos cerca)
    if (this.pastoMesh) { this.scene.remove(this.pastoMesh); this.pastoMesh.geometry.dispose(); this.pastoMesh = null; }
    if (!this.opciones.pasto || !this.pastos.length) return;
    const sa = Math.sin(cam.az), ca = Math.cos(cam.az), ce = Math.cos(cam.el), se = Math.sin(cam.el);
    const ex = cam.cx - sa * ce * cam.dist, ey = cam.cy - ca * ce * cam.dist, ez = cam.cz + se * cam.dist;
    const R = Math.min(90, Math.max(25, cam.dist * 1.2)); if (ez > 60) return;
    const plano = new THREE.PlaneGeometry(1, 1), p2 = plano.clone().rotateY(Math.PI / 2), p3 = plano.clone().rotateY(-Math.PI / 4), geo = BGU.mergeGeometries([plano, p2, p3], false); geo.translate(0, 0, 0.5);
    const mat = new THREE.MeshStandardMaterial({ map: TEX.brizna, alphaTest: 0.45, side: THREE.DoubleSide, roughness: 0.9, color: 0xffffff });
    const tope = 320000, pts = [];
    for (const [poly, z] of this.pastos) {
      let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; for (const q of poly) { x0 = Math.min(x0, q[0]); x1 = Math.max(x1, q[0]); y0 = Math.min(y0, q[1]); y1 = Math.max(y1, q[1]); }
      if (x1 < ex - R || x0 > ex + R || y1 < ey - R || y0 > ey + R) continue;
      const area = (x1 - x0) * (y1 - y0); const n = Math.min(60000, Math.round(area * 1.6));
      const tri = THREE.ShapeUtils.triangulateShape(poly.map(q => new THREE.Vector2(q[0], q[1])), []);
      const areas = tri.map(t => { const a = poly[t[0]], b = poly[t[1]], c = poly[t[2]]; return Math.abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2; }); const tot = areas.reduce((a, b) => a + b, 0) || 1;
      for (let k = 0; k < n; k++) {
        let u = rnd() * tot, ti = 0; while (ti < areas.length - 1 && u > areas[ti]) { u -= areas[ti]; ti++; }
        const a = poly[tri[ti][0]], b = poly[tri[ti][1]], c = poly[tri[ti][2]]; let r1 = rnd(), r2 = rnd(); if (r1 + r2 > 1) { r1 = 1 - r1; r2 = 1 - r2; }
        const px = a[0] + (b[0] - a[0]) * r1 + (c[0] - a[0]) * r2, py = a[1] + (b[1] - a[1]) * r1 + (c[1] - a[1]) * r2, d = Math.hypot(px - ex, py - ey);
        if (d > R || rnd() > Math.max(0.15, 1 - d / R)) continue;
        pts.push(px, py, z);
      }
      if (pts.length / 3 > tope) break;
    }
    const cnt = Math.min(tope, pts.length / 3); if (!cnt) return;
    const im = new THREE.InstancedMesh(geo, mat, cnt); im.castShadow = false; im.receiveShadow = true;
    const M = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), sc = new THREE.Vector3(), pos = new THREE.Vector3(), col = new THREE.Color();
    for (let i = 0; i < cnt; i++) {
      pos.set(pts[i * 3], pts[i * 3 + 1], pts[i * 3 + 2] - 0.02); e.set(Math.PI / 2 + (rnd() - 0.5) * 0.3, 0, rnd() * 6.28); q.setFromEuler(e);
      const t = 0.22 + rnd() * 0.18; sc.set(t * 1.3, t, t * 1.3); M.compose(pos, q, sc); im.setMatrixAt(i, M); col.setHSL(0.24 + rnd() * 0.04, 0.45 + rnd() * 0.2, 0.3 + rnd() * 0.15); im.setColorAt(i, col);
    }
    im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true; this.scene.add(im); this.pastoMesh = im; this.nBriznas = cnt;
  }
  /* render a un tamaño dado; devuelve el canvas listo */
  render(o) {
    const w = o.w || 1920, h = o.h || 1080, cam = Object.assign({}, this.esc.cam, o.cam || {}), hora = o.hora || this.esc.hora || "dia";
    this.briznas(cam); this.follaje(cam);
    this.iluminar(hora, cam); const camera = this.camara(cam, w, h);
    this.renderer.setPixelRatio(1); this.renderer.setSize(w, h, false);
    const comp = new EffectComposer(this.renderer); comp.setSize(w, h);
    comp.addPass(new RenderPass(this.scene, camera));
    if (this.opciones.ao) {
      const ao = new GTAOPass(this.scene, camera, w, h); ao.output = GTAOPass.OUTPUT.Default; ao.blendIntensity = 0.9;
      ao.updateGtaoMaterial({ radius: Math.min(3, Math.max(0.4, cam.dist / 30)), distanceExponent: 1, thickness: 1, scale: 1, samples: 16, distanceFallOff: 1, screenSpaceRadius: false });
      ao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 4, rings: 2, samples: 8 }); comp.addPass(ao);
    }
    const H = this.H, bloom = new UnrealBloomPass(new THREE.Vector2(w, h), H.bloom[0], H.bloom[1], H.bloom[2]); comp.addPass(bloom);
    comp.addPass(new OutputPass());
    const vin = new ShaderPass({ uniforms: { tDiffuse: { value: null }, f: { value: 0.28 } }, vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
      fragmentShader: "uniform sampler2D tDiffuse; uniform float f; varying vec2 vUv; void main(){ vec4 c = texture2D(tDiffuse, vUv); float d = distance(vUv, vec2(0.5)); c.rgb *= 1.0 - f * smoothstep(0.35, 0.95, d); gl_FragColor = c; }" }); comp.addPass(vin);
    comp.addPass(new SMAAPass(w, h));
    comp.render(); comp.dispose();
    return this.cv;
  }
  imagen(o) { this.render(o); return this.cv.toDataURL(o.tipo || "image/jpeg", o.calidad || 0.92); }
  /* mapas de control para ControlNet: "depth" (cerca = blanco), "normal" (espacio de cámara) y "lineart" (bordes por profundidad y normales, negro sobre blanco) */
  pase(o, tipo) {
    const w = o.w || 1920, h = o.h || 1080, cam = Object.assign({}, this.esc.cam, o.cam || {}), camera = this.camara(cam, w, h), scene = this.scene;
    if (!this.hojasMesh) this.follaje(cam);
    const r = this.renderer; r.setPixelRatio(1); r.setSize(w, h, false);
    const guardar = []; scene.traverse(m => { if (m.isMesh) guardar.push([m, m.material, m.visible]); });
    const fondo = scene.background, niebla = scene.fog, env = scene.environment; scene.fog = null; scene.environment = null;
    if (this.luzGrupo) this.luzGrupo.visible = false;
    const near = camera.near, far = Math.max(40, cam.dist * 2.5);
    const vtx = `varying float vz; varying vec3 vn; varying vec2 vUv;
void main() {
  vUv = uv;
#ifdef USE_INSTANCING
  mat4 mvm = modelViewMatrix * instanceMatrix;
#else
  mat4 mvm = modelViewMatrix;
#endif
  vec4 mv = mvm * vec4(position, 1.0);
  vn = normalize(mat3(mvm) * normal);
  vz = -mv.z;
  gl_Position = projectionMatrix * mv;
}`;
    const matDepth = (map) => new THREE.ShaderMaterial({ uniforms: { near: { value: near }, far: { value: far }, map: { value: map || null }, usaMapa: { value: map ? 1 : 0 } }, side: THREE.DoubleSide, vertexShader: vtx,
      fragmentShader: `uniform float near; uniform float far; uniform sampler2D map; uniform int usaMapa; varying float vz; varying vec3 vn; varying vec2 vUv;
void main() {
  if (usaMapa == 1 && texture2D(map, vUv).a < 0.5) discard;
  float d = clamp((vz - near) / (far - near), 0.0, 1.0);
  float v = 1.0 - pow(d, 0.6);
  gl_FragColor = vec4(v, v, v, 1.0);
}` });
    const matNormal = (map) => new THREE.ShaderMaterial({ uniforms: { map: { value: map || null }, usaMapa: { value: map ? 1 : 0 } }, side: THREE.DoubleSide, vertexShader: vtx,
      fragmentShader: `uniform sampler2D map; uniform int usaMapa; varying float vz; varying vec3 vn; varying vec2 vUv;
void main() {
  if (usaMapa == 1 && texture2D(map, vUv).a < 0.5) discard;
  vec3 n = normalize(vn);
  if (!gl_FrontFacing) n = -n;
  gl_FragColor = vec4(n * 0.5 + 0.5, 1.0);
}` });
    const mk = tipo === "normal" ? matNormal : matDepth;
    for (const [m, mat] of guardar) m.material = mk(m.isInstancedMesh ? TEX.hoja : null);
    scene.background = new THREE.Color(tipo === "normal" ? 0x8080ff : 0x000000);
    r.toneMapping = THREE.NoToneMapping; r.render(scene, camera); r.toneMapping = THREE.ACESFilmicToneMapping;
    for (const [m, mat, vis] of guardar) { m.material = mat; m.visible = vis; }
    scene.background = fondo; scene.fog = niebla; scene.environment = env; if (this.luzGrupo) this.luzGrupo.visible = true;
    return this.cv;
  }
  lineart(o) {
    // bordes: discontinuidades de profundidad + de normales, con Sobel sobre los dos pases; negro sobre blanco
    const w = o.w || 1920, h = o.h || 1080, leer = () => { const c = document.createElement("canvas"); c.width = w; c.height = h; const x = c.getContext("2d", { willReadFrequently: true }); x.drawImage(this.cv, 0, 0); return x.getImageData(0, 0, w, h).data; };
    this.pase(o, "depth"); const D = leer(); this.pase(o, "normal"); const N = leer();
    const out = document.createElement("canvas"); out.width = w; out.height = h; const x = out.getContext("2d"); const img = x.createImageData(w, h), d = img.data;
    const at = (A, px, py, k) => A[((Math.max(0, Math.min(h - 1, py)) * w) + Math.max(0, Math.min(w - 1, px))) * 4 + k];
    for (let y = 0; y < h; y++) for (let xx = 0; xx < w; xx++) {
      let e = 0;
      const gd = Math.abs(at(D, xx + 1, y, 0) - at(D, xx - 1, y, 0)) + Math.abs(at(D, xx, y + 1, 0) - at(D, xx, y - 1, 0));
      let gn = 0; for (let k = 0; k < 3; k++) gn += Math.abs(at(N, xx + 1, y, k) - at(N, xx - 1, y, k)) + Math.abs(at(N, xx, y + 1, k) - at(N, xx, y - 1, k));
      e = Math.min(1, gd / 14 + gn / 90); const v = 255 - Math.round(255 * Math.pow(e, 0.8)); const i = (y * w + xx) * 4; d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255;
    }
    x.putImageData(img, 0, 0); return out;
  }
  control(o, tipo) { if (tipo === "lineart") return this.lineart(o).toDataURL("image/png"); this.pase(o, tipo); return this.cv.toDataURL("image/png"); }
}
export default Foto3D;
