/* La Nogalera · visor 3D del Modelo Nogal. Sin librerías: rasterizador propio en un canvas (z-buffer por pixel, perspectiva,
   luz de sol con sombra sobre el terreno, cristales translúcidos y contornos sacados de la geometría, no de las piezas).
   window.CASA3D = { prismas: [[puntos xy, z, alto, color, grupo, material], …], centro: [x, y, z] } */
(function () {
  "use strict";
  var M = window.CASA3D, cv = document.getElementById("c3d"), ctx = cv.getContext("2d");
  var az = 0.62, el = 0.52, zoom = 2, cx = M.centro[0], cy = M.centro[1], cz = M.centro[2];
  var ver = { techo: true, pa: true, muebles: true, arboles: true, fach: true, ext: true, pb: true };
  var DIST = 58, ZG = -0.32;
  var SOL = norm([-0.42, -0.5, 0.76]);                     // hacia el sol: entra por el frente-izquierda, alto
  var off = document.createElement("canvas"), octx = off.getContext("2d");
  var caras = [], opacas = [], translucidas = [], sombras = [];

  function norm(v) { var l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; }
  function color(s) {
    var r = parseInt(s.slice(1, 3), 16), g = parseInt(s.slice(3, 5), 16), b = parseInt(s.slice(5, 7), 16), a = s.length > 7 ? parseInt(s.slice(7, 9), 16) / 255 : 1;
    return [r, g, b, a];
  }
  function cara(v, n, col, g, suelo) {
    var lum = 0.5 + 0.5 * Math.max(0, n[0] * SOL[0] + n[1] * SOL[1] + n[2] * SOL[2]) + (n[2] > 0.5 ? 0.06 : 0);
    if (n[2] < -0.5) lum = 0.42;                           // caras que miran al piso
    lum = Math.min(1.04, lum);
    var rgb = [Math.min(255, col[0] * lum), Math.min(255, col[1] * lum), Math.min(255, col[2] * lum)];
    var code = (((n[0] * 31) | 0) + 32) << 12 | (((n[1] * 31) | 0) + 32) << 6 | (((n[2] * 31) | 0) + 32);
    return { v: v, n: n, rgb: rgb, a: col[3], g: g, suelo: suelo, code: code | 0x40000 };
  }
  function construir() {
    caras = [];
    M.prismas.forEach(function (p) {
      if (ver[p[4]] === false) return;
      var pts = p[0].slice(), z0 = p[1], h = p[2], col = color(p[3]), g = p[4], suelo = p[5] === "suelo", n = pts.length, area = 0, i;
      for (i = 0; i < n; i++) { var a = pts[i], b = pts[(i + 1) % n]; area += a[0] * b[1] - b[0] * a[1]; }
      if (area < 0) pts.reverse();
      var top = [], bot = [];
      for (i = 0; i < n; i++) { top.push([pts[i][0], pts[i][1], z0 + h]); bot.push([pts[n - 1 - i][0], pts[n - 1 - i][1], z0]); }
      caras.push(cara(top, [0, 0, 1], col, g, suelo)); caras.push(cara(bot, [0, 0, -1], col, g, false));
      for (i = 0; i < n; i++) {
        var a2 = pts[i], b2 = pts[(i + 1) % n], dx = b2[0] - a2[0], dy = b2[1] - a2[1], l = Math.hypot(dx, dy) || 1;
        caras.push(cara([[a2[0], a2[1], z0], [b2[0], b2[1], z0], [b2[0], b2[1], z0 + h], [a2[0], a2[1], z0 + h]], [dy / l, -dx / l, 0], col, g, false));
      }
    });
    sombras = caras.filter(function (f) { return f.g !== "muebles" && !f.suelo && f.g !== "ext" || (f.g === "ext" && !f.suelo); });
  }

  /* ---------- rasterizador ---------- */
  var Wr = 0, Hr = 0, img, cbuf, zbuf, nbuf, sbuf;
  function buffers(w, h) {
    if (w === Wr && h === Hr) return;
    Wr = w; Hr = h; off.width = w; off.height = h;
    img = octx.createImageData(w, h); cbuf = img.data; zbuf = new Float32Array(w * h); nbuf = new Int32Array(w * h); sbuf = new Uint8Array(w * h);
  }
  function tri(x0, y0, w0, x1, y1, w1, x2, y2, w2, f, modo) {
    // modo 0: opaco (z-buffer + color + normal) · 1: translúcido (prueba de z, mezcla) · 2: máscara de sombra
    var minx = Math.max(0, Math.floor(Math.min(x0, x1, x2))), maxx = Math.min(Wr - 1, Math.ceil(Math.max(x0, x1, x2)));
    var miny = Math.max(0, Math.floor(Math.min(y0, y1, y2))), maxy = Math.min(Hr - 1, Math.ceil(Math.max(y0, y1, y2)));
    if (minx > maxx || miny > maxy) return;
    var det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0);
    if (Math.abs(det) < 1e-9) return;
    var inv = 1 / det;
    var a0 = (y1 - y2) * inv, b0 = (x2 - x1) * inv, a1 = (y2 - y0) * inv, b1 = (x0 - x2) * inv;
    var r = f && f.rgb, R = 0, G = 0, B = 0, Rs = 0, Gs = 0, Bs = 0, al = f ? f.a : 1, code = f ? f.code : 0, suelo = f && f.suelo;
    if (r) { R = r[0]; G = r[1]; B = r[2]; Rs = R * 0.62; Gs = G * 0.62; Bs = B * 0.66; }
    for (var y = miny; y <= maxy; y++) {
      var py = y + 0.5, row = y * Wr;
      for (var x = minx; x <= maxx; x++) {
        var px = x + 0.5, l0 = a0 * (px - x2) + b0 * (py - y2), l1 = a1 * (px - x2) + b1 * (py - y2);
        if (l0 < -1e-6 || l1 < -1e-6) continue;
        var l2 = 1 - l0 - l1; if (l2 < -1e-6) continue;
        var i = row + x;
        if (modo === 2) { sbuf[i] = 1; continue; }
        var w = l0 * w0 + l1 * w1 + l2 * w2;
        if (w <= zbuf[i]) continue;
        var k = i * 4;
        if (modo === 0) {
          zbuf[i] = w; nbuf[i] = code;
          if (suelo && sbuf[i]) { cbuf[k] = Rs; cbuf[k + 1] = Gs; cbuf[k + 2] = Bs; } else { cbuf[k] = R; cbuf[k + 1] = G; cbuf[k + 2] = B; }
          cbuf[k + 3] = 255;
        } else {
          var q = 1 - al;
          cbuf[k] = cbuf[k] * q + R * al; cbuf[k + 1] = cbuf[k + 1] * q + G * al; cbuf[k + 2] = cbuf[k + 2] * q + B * al; cbuf[k + 3] = 255;
        }
      }
    }
  }
  function dibujar(escala) {
    var Wc = cv.clientWidth, Hc = cv.clientHeight; if (!Wc || !Hc) return;
    var w = Math.round(Wc * escala), h = Math.round(Hc * escala); buffers(w, h);
    zbuf.fill(0); nbuf.fill(0); sbuf.fill(0); cbuf.fill(0);
    var ca = Math.cos(az), sa = Math.sin(az), ce = Math.cos(el), se = Math.sin(el);
    var r_ = [ca, -sa, 0], u_ = [sa * se, ca * se, ce], f_ = [sa * ce, ca * ce, -se];
    var eye = [cx - f_[0] * DIST, cy - f_[1] * DIST, cz - f_[2] * DIST];
    var F = Math.min(w, h) / 32 * Math.pow(1.15, zoom) * DIST, hw = w / 2, hh = h / 2;
    function proy(p) {
      var x = p[0] - eye[0], y = p[1] - eye[1], z = p[2] - eye[2];
      var zv = x * f_[0] + y * f_[1] + z * f_[2]; if (zv < 1) zv = 1;
      return [hw + F * (x * r_[0] + y * r_[1] + z * r_[2]) / zv, hh - F * (x * u_[0] + y * u_[1] + z * u_[2]) / zv, 1 / zv];
    }
    function poligono(f, pts, modo) {
      var q = [], i; for (i = 0; i < pts.length; i++) q.push(proy(pts[i]));
      for (i = 1; i < q.length - 1; i++) tri(q[0][0], q[0][1], q[0][2], q[i][0], q[i][1], q[i][2], q[i + 1][0], q[i + 1][1], q[i + 1][2], f, modo);
    }
    // 1) máscara de sombra: cada cara proyectada por el sol sobre el plano del terreno
    var i, f, k;
    for (i = 0; i < sombras.length; i++) {
      f = sombras[i]; var sp = [];
      for (k = 0; k < f.v.length; k++) { var p = f.v[k], t = (p[2] - ZG) / SOL[2]; sp.push([p[0] - SOL[0] * t, p[1] - SOL[1] * t, ZG]); }
      poligono(null, sp, 2);
    }
    // 2) caras opacas (las que miran a la cámara) y 3) translúcidas de atrás hacia adelante
    translucidas = [];
    for (i = 0; i < caras.length; i++) {
      f = caras[i]; var v0 = f.v[0];
      if (f.n[0] * (v0[0] - eye[0]) + f.n[1] * (v0[1] - eye[1]) + f.n[2] * (v0[2] - eye[2]) > 0) continue;
      if (f.a < 1) { var c = f.v[1]; f.d = (c[0] - eye[0]) * f_[0] + (c[1] - eye[1]) * f_[1] + (c[2] - eye[2]) * f_[2]; translucidas.push(f); continue; }
      poligono(f, f.v, 0);
    }
    translucidas.sort(function (a, b) { return b.d - a.d; });
    for (i = 0; i < translucidas.length; i++) poligono(translucidas[i], translucidas[i].v, 1);
    // 4) contornos: salto de profundidad (silueta) o cambio de normal (arista)
    for (var y = 0; y < h - 1; y++) {
      for (var x = 0; x < w - 1; x++) {
        i = y * w + x; var n0 = nbuf[i]; if (!n0 && !nbuf[i + 1] && !nbuf[i + w]) continue;
        var z0 = zbuf[i] ? 1 / zbuf[i] : 1e9, z1 = zbuf[i + 1] ? 1 / zbuf[i + 1] : 1e9, z2 = zbuf[i + w] ? 1 / zbuf[i + w] : 1e9;
        var umbral = 0.12 + 0.004 * Math.min(z0, z1, z2), fuerte = Math.abs(z0 - z1) > umbral || Math.abs(z0 - z2) > umbral;
        var arista = !fuerte && n0 && ((nbuf[i + 1] && nbuf[i + 1] !== n0) || (nbuf[i + w] && nbuf[i + w] !== n0));
        if (!fuerte && !arista) continue;
        var m = fuerte ? 0.3 : 0.62; k = i * 4;
        cbuf[k] *= m; cbuf[k + 1] *= m; cbuf[k + 2] *= m; cbuf[k + 3] = 255;
      }
    }
    octx.putImageData(img, 0, 0);
    var dpr = window.devicePixelRatio || 1;
    if (cv.width !== Math.round(Wc * dpr) || cv.height !== Math.round(Hc * dpr)) { cv.width = Math.round(Wc * dpr); cv.height = Math.round(Hc * dpr); }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var g = ctx.createLinearGradient(0, 0, 0, Hc); g.addColorStop(0, "#dbeaf7"); g.addColorStop(0.55, "#f3f8fc"); g.addColorStop(1, "#ffffff");
    ctx.fillStyle = g; ctx.fillRect(0, 0, Wc, Hc);
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = "high";
    ctx.drawImage(off, 0, 0, Wc, Hc);
  }

  /* ---------- interacción ---------- */
  var pendiente = false, fino = null, arrastrando = false;
  function pedir() {
    if (!pendiente) { pendiente = true; requestAnimationFrame(function () { pendiente = false; dibujar(arrastrando ? 1 : Math.min(2, window.devicePixelRatio || 1)); }); }
    clearTimeout(fino); fino = setTimeout(function () { if (!arrastrando) dibujar(Math.min(2, window.devicePixelRatio || 1)); }, 160);
  }
  var arr = null;
  cv.addEventListener("pointerdown", function (e) { arr = [e.clientX, e.clientY, az, el]; arrastrando = true; cv.setPointerCapture(e.pointerId); });
  cv.addEventListener("pointermove", function (e) { if (!arr) return; az = arr[2] + (e.clientX - arr[0]) * 0.01; el = Math.min(1.5, Math.max(0.08, arr[3] + (e.clientY - arr[1]) * 0.006)); pedir(); });
  function soltar() { arr = null; arrastrando = false; pedir(); }
  cv.addEventListener("pointerup", soltar); cv.addEventListener("pointercancel", soltar);
  cv.addEventListener("wheel", function (e) { e.preventDefault(); zoom += e.deltaY < 0 ? 1 : -1; zoom = Math.max(-8, Math.min(14, zoom)); pedir(); }, { passive: false });
  document.querySelectorAll("[data-capa]").forEach(function (b) {
    b.addEventListener("click", function () {
      var k = b.getAttribute("data-capa"); ver[k] = !ver[k]; b.setAttribute("aria-pressed", ver[k]);
      if (k === "pa" && !ver.pa) { ver.techo = false; var t = document.querySelector('[data-capa="techo"]'); if (t) t.setAttribute("aria-pressed", "false"); }
      construir(); pedir();
    });
  });
  var VISTAS = { frente: [0.0, 0.35], esquina: [0.62, 0.52], jardin: [Math.PI + 0.5, 0.5], planta: [0.0, 1.5], lado: [Math.PI / 2, 0.3] };
  document.querySelectorAll("[data-vista]").forEach(function (b) {
    b.addEventListener("click", function () { var v = VISTAS[b.getAttribute("data-vista")]; az = v[0]; el = v[1]; pedir(); });
  });
  document.querySelectorAll("[data-zoom]").forEach(function (b) { b.addEventListener("click", function () { zoom += +b.getAttribute("data-zoom"); pedir(); }); });
  window.addEventListener("resize", pedir);
  construir(); pedir();
})();
