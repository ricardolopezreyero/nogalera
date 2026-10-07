/* La Nogalera · motor de render. Sin librerías: rasterizador por software en un canvas (z-buffer, perspectiva, sol con sombra
   sobre el suelo, cristales y copas translúcidos, materiales que emiten luz con halo, bruma por distancia y contornos).
   Escena: { prismas: [[puntos xy, z, alto, color "#rrggbb[aa]", grupo, material], …], centro: [x,y,z], suelo_z, luces: [[x,y,z,radio,color]] }
   Materiales: "" normal · "suelo" recibe sombra · "luz" emite (no se sombrea, lleva halo). */
(function () {
  "use strict";
  var HORAS = {
    dia:       { sol: [-0.42, -0.5, 0.76], cielo: ["#cfe3f5", "#eef5fb", "#ffffff"], amb: 0.5, dif: 0.5, bruma: [0.0, 0.0], brumaCol: [225, 235, 245], luces: 0, sombra: 0.62 },
    tarde:     { sol: [-0.75, -0.3, 0.6], cielo: ["#bcd6ee", "#f1e9d6", "#fff4df"], amb: 0.5, dif: 0.55, bruma: [0.0, 0.0], brumaCol: [240, 230, 210], luces: 0, sombra: 0.58, tono: [1.04, 1.0, 0.92] },
    atardecer: { sol: [-0.92, -0.2, 0.33], cielo: ["#5b6f9c", "#e2a77a", "#f6cf9a"], amb: 0.42, dif: 0.5, bruma: [0.0, 0.0], brumaCol: [230, 180, 140], luces: 1, sombra: 0.55, tono: [1.06, 0.92, 0.8] },
    noche:     { sol: [-0.3, -0.4, 0.87], cielo: ["#0b1630", "#1a2b52", "#2e4572"], amb: 0.27, dif: 0.1, bruma: [0.0, 0.0], brumaCol: [20, 32, 60], luces: 1, sombra: 0.9, tono: [0.66, 0.72, 0.92] }
  };
  function norm(v) { var l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; }
  function color(s) {
    var r = parseInt(s.slice(1, 3), 16), g = parseInt(s.slice(3, 5), 16), b = parseInt(s.slice(5, 7), 16), a = s.length > 7 ? parseInt(s.slice(7, 9), 16) / 255 : 1;
    return [r, g, b, a];
  }
  function Render3D(cv, esc, opt) {
    var self = this; opt = opt || {};
    var ctx = cv.getContext("2d"), off = document.createElement("canvas"), octx = off.getContext("2d");
    this.cam = { az: 0.62, el: 0.52, zoom: 2, dist: esc.dist || 58, cx: esc.centro[0], cy: esc.centro[1], cz: esc.centro[2] };
    this.capas = {}; this.contornos = esc.contornos === undefined ? 1 : esc.contornos; this.hora = esc.hora || "dia";
    var ZG = esc.suelo_z === undefined ? -0.32 : esc.suelo_z, caras = [], sombras = [], luces = esc.luces || [];
    var Wr = 0, Hr = 0, img, cbuf, zbuf, nbuf, sbuf;
    function cara(v, n, col, g, mat, H) {
      var S = H.sol, lum;
      if (mat === "luz") lum = 1.15;
      else {
        lum = H.amb + H.dif * Math.max(0, n[0] * S[0] + n[1] * S[1] + n[2] * S[2]) + (n[2] > 0.5 ? 0.06 : 0);
        if (n[2] < -0.5) lum = H.amb * 0.85;
      }
      lum = Math.min(1.15, lum);
      var t = H.tono || [1, 1, 1];
      var rgb = [Math.min(255, col[0] * lum * t[0]), Math.min(255, col[1] * lum * t[1]), Math.min(255, col[2] * lum * t[2])];
      var code = (((n[0] * 31) | 0) + 32) << 12 | (((n[1] * 31) | 0) + 32) << 6 | (((n[2] * 31) | 0) + 32);
      return { v: v, n: n, rgb: rgb, a: col[3], g: g, suelo: mat === "suelo", luz: mat === "luz", code: code | 0x40000 };
    }
    this.construir = function () {
      var H = HORAS[self.hora]; H.sol = norm(H.sol); caras = [];
      esc.prismas.forEach(function (p) {
        if (self.capas[p[4]] === false) return;
        var pts = p[0].slice(), z0 = p[1], h = p[2], col = color(p[3]), g = p[4], mat = p[5] || "", n = pts.length, area = 0, i;
        for (i = 0; i < n; i++) { var a = pts[i], b = pts[(i + 1) % n]; area += a[0] * b[1] - b[0] * a[1]; }
        if (area < 0) pts.reverse();
        var top = [], bot = [];
        for (i = 0; i < n; i++) { top.push([pts[i][0], pts[i][1], z0 + h]); bot.push([pts[n - 1 - i][0], pts[n - 1 - i][1], z0]); }
        caras.push(cara(top, [0, 0, 1], col, g, mat, H)); if (!(mat === "suelo")) caras.push(cara(bot, [0, 0, -1], col, g, mat, H));
        for (i = 0; i < n; i++) {
          var a2 = pts[i], b2 = pts[(i + 1) % n], dx = b2[0] - a2[0], dy = b2[1] - a2[1], l = Math.hypot(dx, dy) || 1;
          caras.push(cara([[a2[0], a2[1], z0], [b2[0], b2[1], z0], [b2[0], b2[1], z0 + h], [a2[0], a2[1], z0 + h]], [dy / l, -dx / l, 0], col, g, mat, H));
        }
      });
      sombras = caras.filter(function (f) { return !f.suelo && !f.luz && f.g !== "muebles"; });
    };
    function buffers(w, h) {
      if (w === Wr && h === Hr) return;
      Wr = w; Hr = h; off.width = w; off.height = h;
      img = octx.createImageData(w, h); cbuf = img.data; zbuf = new Float32Array(w * h); nbuf = new Int32Array(w * h); sbuf = new Uint8Array(w * h);
    }
    function tri(x0, y0, w0, x1, y1, w1, x2, y2, w2, f, modo, som) {
      var minx = Math.max(0, Math.floor(Math.min(x0, x1, x2))), maxx = Math.min(Wr - 1, Math.ceil(Math.max(x0, x1, x2)));
      var miny = Math.max(0, Math.floor(Math.min(y0, y1, y2))), maxy = Math.min(Hr - 1, Math.ceil(Math.max(y0, y1, y2)));
      if (minx > maxx || miny > maxy) return;
      var det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0);
      if (Math.abs(det) < 1e-9) return;
      var inv = 1 / det, a0 = (y1 - y2) * inv, b0 = (x2 - x1) * inv, a1 = (y2 - y0) * inv, b1 = (x0 - x2) * inv;
      var r = f && f.rgb, R = 0, G = 0, B = 0, Rs = 0, Gs = 0, Bs = 0, al = f ? f.a : 1, code = f ? f.code : 0, suelo = f && f.suelo;
      if (r) { R = r[0]; G = r[1]; B = r[2]; Rs = R * som; Gs = G * som; Bs = B * (som + 0.04); }
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
    this.rasterizar = function (w, h) {
      buffers(w, h); zbuf.fill(0); nbuf.fill(0); sbuf.fill(0); cbuf.fill(0);
      var H = HORAS[self.hora], SOL = H.sol, c = self.cam;
      var ca = Math.cos(c.az), sa = Math.sin(c.az), ce = Math.cos(c.el), se = Math.sin(c.el);
      var r_ = [ca, -sa, 0], u_ = [sa * se, ca * se, ce], f_ = [sa * ce, ca * ce, -se];
      var eye = [c.cx - f_[0] * c.dist, c.cy - f_[1] * c.dist, c.cz - f_[2] * c.dist];
      var F = Math.min(w, h) / 32 * Math.pow(1.15, c.zoom) * c.dist, hw = w / 2, hh = h / 2, NEAR = 0.4;
      function vista(p) {
        var x = p[0] - eye[0], y = p[1] - eye[1], z = p[2] - eye[2];
        return [x * r_[0] + y * r_[1] + z * r_[2], x * u_[0] + y * u_[1] + z * u_[2], x * f_[0] + y * f_[1] + z * f_[2]];
      }
      function proy(p) { var v = vista(p); if (v[2] < NEAR) return null; return [hw + F * v[0] / v[2], hh - F * v[1] / v[2], 1 / v[2]]; }
      function poligono(f, pts, modo) {
        // a coordenadas de cámara, recorte contra el plano cercano (Sutherland-Hodgman) y proyección
        var vs = [], i, n = pts.length; for (i = 0; i < n; i++) vs.push(vista(pts[i]));
        var out = [], todo = true;
        for (i = 0; i < n; i++) if (vs[i][2] < NEAR) { todo = false; break; }
        if (todo) out = vs;
        else {
          for (i = 0; i < n; i++) {
            var a = vs[i], b = vs[(i + 1) % n], ina = a[2] >= NEAR, inb = b[2] >= NEAR;
            if (ina) out.push(a);
            if (ina !== inb) { var t = (NEAR - a[2]) / (b[2] - a[2]); out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, NEAR]); }
          }
          if (out.length < 3) return;
        }
        var q = []; for (i = 0; i < out.length; i++) q.push([hw + F * out[i][0] / out[i][2], hh - F * out[i][1] / out[i][2], 1 / out[i][2]]);
        for (i = 1; i < q.length - 1; i++) tri(q[0][0], q[0][1], q[0][2], q[i][0], q[i][1], q[i][2], q[i + 1][0], q[i + 1][1], q[i + 1][2], f, modo, H.sombra);
      }
      var i, f, k;
      if (H.sombra < 0.99) for (i = 0; i < sombras.length; i++) {
        f = sombras[i]; var sp = [];
        for (k = 0; k < f.v.length; k++) { var p = f.v[k], t = (p[2] - ZG) / SOL[2]; sp.push([p[0] - SOL[0] * t, p[1] - SOL[1] * t, ZG]); }
        poligono(null, sp, 2);
      }
      var trans = [];
      for (i = 0; i < caras.length; i++) {
        f = caras[i]; var v0 = f.v[0];
        if (f.n[0] * (v0[0] - eye[0]) + f.n[1] * (v0[1] - eye[1]) + f.n[2] * (v0[2] - eye[2]) > 0) continue;
        if (f.a < 1) { var cc = f.v[1]; f.d = (cc[0] - eye[0]) * f_[0] + (cc[1] - eye[1]) * f_[1] + (cc[2] - eye[2]) * f_[2]; trans.push(f); continue; }
        poligono(f, f.v, 0);
      }
      trans.sort(function (a, b) { return b.d - a.d; });
      for (i = 0; i < trans.length; i++) poligono(trans[i], trans[i].v, 1);
      // contornos
      if (self.contornos > 0) {
        var mS = 1 - 0.7 * self.contornos, mA = 1 - 0.38 * self.contornos;
        for (var y = 0; y < h - 1; y++) for (var x = 0; x < w - 1; x++) {
          i = y * w + x; var n0 = nbuf[i]; if (!n0 && !nbuf[i + 1] && !nbuf[i + w]) continue;
          var z0 = zbuf[i] ? 1 / zbuf[i] : 1e9, z1 = zbuf[i + 1] ? 1 / zbuf[i + 1] : 1e9, z2 = zbuf[i + w] ? 1 / zbuf[i + w] : 1e9;
          var umbral = 0.12 + 0.006 * Math.min(z0, z1, z2), fuerte = Math.abs(z0 - z1) > umbral || Math.abs(z0 - z2) > umbral;
          var arista = !fuerte && n0 && ((nbuf[i + 1] && nbuf[i + 1] !== n0) || (nbuf[i + w] && nbuf[i + w] !== n0));
          if (!fuerte && !arista) continue;
          var m = fuerte ? mS : mA; k = i * 4; cbuf[k] *= m; cbuf[k + 1] *= m; cbuf[k + 2] *= m; cbuf[k + 3] = 255;
        }
      }
      // bruma por distancia
      var bz0 = (esc.bruma && esc.bruma[0]) || H.bruma[0], bz1 = (esc.bruma && esc.bruma[1]) || H.bruma[1];
      if (bz1 > 0) {
        var bc = H.brumaCol;
        for (i = 0; i < w * h; i++) {
          if (!zbuf[i]) continue; var zv = 1 / zbuf[i]; if (zv <= bz0) continue;
          var t2 = Math.min(0.85, (zv - bz0) / bz1); k = i * 4;
          cbuf[k] += (bc[0] - cbuf[k]) * t2; cbuf[k + 1] += (bc[1] - cbuf[k + 1]) * t2; cbuf[k + 2] += (bc[2] - cbuf[k + 2]) * t2;
        }
      }
      // halos de las luces
      if (H.luces) for (i = 0; i < luces.length; i++) {
        var L = luces[i], q = proy([L[0], L[1], L[2]]); if (!q) continue;
        var px = Math.round(q[0]), py = Math.round(q[1]); if (px < 0 || py < 0 || px >= w || py >= h) continue;
        var zl = 1 / q[2], zb = zbuf[py * w + px]; if (zb && 1 / zb < zl - 0.6) continue;
        var rad = Math.max(3, Math.round(F * L[3] / zl)), lc = color(L[4] || "#ffd9a0"), I = 0.9;
        var x0 = Math.max(0, px - rad), x1 = Math.min(w - 1, px + rad), y0 = Math.max(0, py - rad), y1 = Math.min(h - 1, py + rad);
        for (var yy = y0; yy <= y1; yy++) {
          var sk = cieloRGB(yy / h);
          for (var xx = x0; xx <= x1; xx++) {
            var dd = Math.hypot(xx - px, yy - py) / rad; if (dd > 1) continue;
            var a = I * (1 - dd) * (1 - dd); k = (yy * w + xx) * 4;
            if (!cbuf[k + 3]) { cbuf[k] = sk[0]; cbuf[k + 1] = sk[1]; cbuf[k + 2] = sk[2]; }
            cbuf[k] = Math.min(255, cbuf[k] + lc[0] * a); cbuf[k + 1] = Math.min(255, cbuf[k + 1] + lc[1] * a); cbuf[k + 2] = Math.min(255, cbuf[k + 2] + lc[2] * a); cbuf[k + 3] = 255;
          }
        }
      }
      octx.putImageData(img, 0, 0);
      return off;
    };
    function cieloRGB(t) {
      var H = HORAS[self.hora], a = color(H.cielo[0]), b = color(H.cielo[1]), c = color(H.cielo[2]), u;
      if (t < 0.55) { u = t / 0.55; return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u]; }
      u = (t - 0.55) / 0.45; return [b[0] + (c[0] - b[0]) * u, b[1] + (c[1] - b[1]) * u, b[2] + (c[2] - b[2]) * u];
    }
    this.cielo = function (c2, W, Hh) {
      var H = HORAS[self.hora], g = c2.createLinearGradient(0, 0, 0, Hh);
      g.addColorStop(0, H.cielo[0]); g.addColorStop(0.55, H.cielo[1]); g.addColorStop(1, H.cielo[2]); c2.fillStyle = g; c2.fillRect(0, 0, W, Hh);
    };
    this.dibujar = function (escala) {
      var Wc = cv.clientWidth, Hc = cv.clientHeight; if (!Wc || !Hc) return;
      var o = self.rasterizar(Math.round(Wc * escala), Math.round(Hc * escala));
      var dpr = window.devicePixelRatio || 1;
      if (cv.width !== Math.round(Wc * dpr) || cv.height !== Math.round(Hc * dpr)) { cv.width = Math.round(Wc * dpr); cv.height = Math.round(Hc * dpr); }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); self.cielo(ctx, Wc, Hc);
      ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = "high"; ctx.drawImage(o, 0, 0, Wc, Hc);
    };
    this.imagen = function (W, Hh, ss, tipo, calidad) {
      // imagen final de W × H píxeles, rasterizada a ss× y reducida (antialias)
      var o = self.rasterizar(W * ss, Hh * ss), c3 = document.createElement("canvas"); c3.width = W; c3.height = Hh;
      var g3 = c3.getContext("2d"); self.cielo(g3, W, Hh); g3.imageSmoothingEnabled = true; g3.imageSmoothingQuality = "high"; g3.drawImage(o, 0, 0, W, Hh);
      return c3.toDataURL(tipo || "image/jpeg", calidad || 0.9);
    };
    var pendiente = false, fino = null;
    this.arrastrando = false;
    this.pedir = function () {
      if (!pendiente) { pendiente = true; requestAnimationFrame(function () { pendiente = false; self.dibujar(self.arrastrando ? (opt.escalaRapida || 1) : Math.min(2, window.devicePixelRatio || 1)); }); }
      clearTimeout(fino); fino = setTimeout(function () { if (!self.arrastrando) self.dibujar(Math.min(2, window.devicePixelRatio || 1)); }, 180);
    };
    this.orbita = function () {
      var arr = null, c = self.cam;
      cv.addEventListener("pointerdown", function (e) { arr = [e.clientX, e.clientY, c.az, c.el]; self.arrastrando = true; cv.setPointerCapture(e.pointerId); });
      cv.addEventListener("pointermove", function (e) { if (!arr) return; c.az = arr[2] + (e.clientX - arr[0]) * 0.01; c.el = Math.min(1.5, Math.max(0.0, arr[3] + (e.clientY - arr[1]) * 0.006)); self.pedir(); if (self.onCam) self.onCam(); });
      function soltar() { arr = null; self.arrastrando = false; self.pedir(); }
      cv.addEventListener("pointerup", soltar); cv.addEventListener("pointercancel", soltar);
      cv.addEventListener("wheel", function (e) { e.preventDefault(); c.zoom += e.deltaY < 0 ? 1 : -1; c.zoom = Math.max(-10, Math.min(16, c.zoom)); self.pedir(); if (self.onCam) self.onCam(); }, { passive: false });
    };
    this.HORAS = HORAS;
    this.construir();
  }
  window.Render3D = Render3D;
})();
