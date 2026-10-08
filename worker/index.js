/* La Nogalera · Worker de Cloudflare: sirve el sitio estático (public/) y expone tres rutas:
     POST /api/render-ia   renders fotorrealistas con el modelo de imágenes de OpenAI (secretos OPENAI_API_KEY y RENDER_CLAVE)
     POST /api/prospecto   guarda los datos que deja un cliente en /inicio/ (base de datos: Durable Object `Prospectos` con SQLite, sin nada que crear)
     GET  /api/prospectos  descarga los prospectos (?clave=ADMIN_CLAVE, &formato=csv): la clave es el secreto ADMIN_CLAVE (o RENDER_CLAVE si no hay; sin secretos, "123")
   Opcional: con los secretos RESEND_API_KEY y AVISO_CORREO, cada prospecto nuevo se avisa por correo (API de Resend). */
import { DurableObject } from "cloudflare:workers";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/api/render-ia") return renderIA(request, env);
    if (url.pathname === "/api/prospecto") return guardarProspecto(request, env, ctx);
    if (url.pathname === "/api/prospectos") return listarProspectos(request, env);
    return env.ASSETS.fetch(request);
  }
};

/* Clave provisional mientras no se ponen los secretos ADMIN_CLAVE y RENDER_CLAVE en Cloudflare: en cuanto existen, mandan ellos. */
const CLAVE_PROVISIONAL = "123";
const claveRender = env => env.RENDER_CLAVE || CLAVE_PROVISIONAL;
const claveAdmin = env => env.ADMIN_CLAVE || env.RENDER_CLAVE || CLAVE_PROVISIONAL;
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

/* ---------- prospectos: la base de datos ---------- */
export class Prospectos extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    ctx.blockConcurrencyWhile(async () => {
      ctx.storage.sql.exec(`CREATE TABLE IF NOT EXISTS prospectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, nombre TEXT NOT NULL, celular TEXT NOT NULL, correo TEXT NOT NULL,
        casa TEXT NOT NULL, credito TEXT NOT NULL, rapidez TEXT NOT NULL, mensaje TEXT, origen TEXT, pais TEXT, ciudad TEXT, agente TEXT)`);
    });
  }
  guardar(p) {
    this.ctx.storage.sql.exec("INSERT INTO prospectos (fecha, nombre, celular, correo, casa, credito, rapidez, mensaje, origen, pais, ciudad, agente) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
      p.fecha, p.nombre, p.celular, p.correo, p.casa, p.credito, p.rapidez, p.mensaje, p.origen, p.pais, p.ciudad, p.agente);
    const r = this.ctx.storage.sql.exec("SELECT COUNT(*) AS n FROM prospectos").one();
    return r.n;
  }
  listar() { return this.ctx.storage.sql.exec("SELECT * FROM prospectos ORDER BY id DESC").toArray(); }
  repetido(celular, correo) {
    const r = this.ctx.storage.sql.exec("SELECT COUNT(*) AS n FROM prospectos WHERE celular = ? OR correo = ?", celular, correo).one();
    return r.n > 0;
  }
}
const CASA = { primera: "Primera casa", segunda: "Segunda casa" };
const CREDITO = { si: "Sí, más de $4 millones", no: "No", nose: "No lo sé" };
const RAPIDEZ = { viendo: "Estoy viendo", ya: "Quiero comprar ya" };
const limpia = (s, n) => String(s || "").replace(/\s+/g, " ").trim().slice(0, n);

async function guardarProspecto(request, env, ctx) {
  if (request.method !== "POST") return json({ error: "Usa POST" }, 405);
  if (!env.PROSPECTOS) return json({ error: "Falta la base de datos (binding PROSPECTOS en wrangler.jsonc)." }, 503);
  let c; try { c = await request.json(); } catch (e) { return json({ error: "Cuerpo inválido" }, 400); }
  if (c.empresa) return json({ ok: true });                                   // campo trampa para robots: se contesta ok y no se guarda
  const nombre = limpia(c.nombre, 120), correo = limpia(c.correo, 160).toLowerCase(), mensaje = limpia(c.mensaje, 1000);
  const celular = limpia(c.celular, 30).replace(/[^\d+]/g, "");
  if (nombre.length < 2) return json({ error: "Falta el nombre" }, 400);
  if (celular.replace(/\D/g, "").length < 10) return json({ error: "El celular necesita 10 dígitos" }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(correo)) return json({ error: "El correo no parece correcto" }, 400);
  const brochure = c.tipo === "brochure";                                     // el formulario corto: solo nombre, celular y correo para recibir el brochure
  if (!brochure && (!CASA[c.casa] || !CREDITO[c.credito] || !RAPIDEZ[c.rapidez])) return json({ error: "Faltan respuestas" }, 400);
  const p = { fecha: new Date().toISOString(), nombre, celular, correo, casa: CASA[c.casa] || "—", credito: CREDITO[c.credito] || "—", rapidez: RAPIDEZ[c.rapidez] || (brochure ? "Pidió el brochure" : "—"), mensaje,
              origen: limpia(c.origen, 200), pais: request.cf?.country || "", ciudad: request.cf?.city || "", agente: limpia(request.headers.get("user-agent"), 200) };
  const stub = env.PROSPECTOS.get(env.PROSPECTOS.idFromName("todos"));
  const repetido = await stub.repetido(p.celular, p.correo);
  const n = await stub.guardar(p);
  if (env.RESEND_API_KEY && env.AVISO_CORREO) ctx.waitUntil(avisar(env, p, n, repetido));
  if (env.RESEND_API_KEY && brochure && !repetido) ctx.waitUntil(confirmarBrochure(env, p));
  return json({ ok: true, n, repetido, correo: !!env.RESEND_API_KEY });
}

async function avisar(env, p, n, repetido) {
  const filas = [["Nombre", p.nombre], ["Celular", p.celular], ["Correo", p.correo], ["Casa", p.casa], ["Crédito de más de $4 millones", p.credito], ["Rapidez", p.rapidez], ["Mensaje", p.mensaje || "—"], ["Desde", [p.ciudad, p.pais].filter(Boolean).join(", ") || "—"], ["Página", p.origen || "—"]];
  const texto = filas.map(([k, v]) => `${k}: ${v}`).join("\n");
  try {
    await fetch("https://api.resend.com/emails", { method: "POST", headers: { authorization: "Bearer " + env.RESEND_API_KEY, "content-type": "application/json" },
      body: JSON.stringify({ from: env.AVISO_DESDE || "La Nogalera <onboarding@resend.dev>", to: env.AVISO_CORREO.split(",").map(s => s.trim()),
        subject: `Prospecto ${n}: ${p.nombre} · ${p.rapidez}${repetido ? " (ya había escrito)" : ""}`, text: texto + "\n\nTodos: https://nogalera.capitaltorreon.com/api/prospectos?clave=…&formato=csv" }) });
  } catch (e) { /* el prospecto ya quedó guardado; el aviso es un extra */ }
}

/* al que pide el brochure se le contesta en el momento: el brochure se le manda en cuanto esté listo */
async function confirmarBrochure(env, p) {
  const nombre = p.nombre.split(" ")[0];
  const texto = `Hola, ${nombre}.\n\nGracias por tu interés en La Nogalera. Ya tenemos tus datos: en cuanto el brochure esté listo te lo mandamos a este correo, con la lista de precios de la etapa 1, el plano para elegir lote y la cita para recorrer la huerta.\n\nMientras, puedes ver la casa, la huerta y las noches en https://nogalera.capitaltorreon.com/inicio/\n\nSi prefieres que te llamemos, contesta este correo con la hora que te acomode.\n\nLa Nogalera · La Paz, Torreón`;
  const html = `<div style="font-family:Georgia,serif;max-width:36rem;margin:auto;color:#1a1d1a;line-height:1.5"><p style="font-size:0.75rem;letter-spacing:0.18em;text-transform:uppercase;color:#c9a65c">La Nogalera · Torreón</p>
<h1 style="font-weight:600;font-size:1.75rem;margin:0 0 1rem">Gracias, ${nombre}.</h1>
<p>Ya tenemos tus datos. <b>En cuanto el brochure esté listo te lo mandamos a este correo</b>, con la lista de precios de la etapa 1, el plano para elegir lote y la cita para recorrer la huerta.</p>
<p>Mientras, puedes ver la casa, la huerta y las noches en <a href="https://nogalera.capitaltorreon.com/inicio/" style="color:#2f5d3a">nogalera.capitaltorreon.com/inicio</a>.</p>
<p>Si prefieres que te llamemos, contesta este correo con la hora que te acomode.</p>
<p style="font-size:0.8125rem;color:#6b6f68;margin-top:2rem">La Nogalera · La Paz, Torreón, Coahuila. Vivir entre nogales de cuarenta años.</p></div>`;
  try {
    await fetch("https://api.resend.com/emails", { method: "POST", headers: { authorization: "Bearer " + env.RESEND_API_KEY, "content-type": "application/json" },
      body: JSON.stringify({ from: env.AVISO_DESDE || "La Nogalera <onboarding@resend.dev>", to: [p.correo], reply_to: env.AVISO_CORREO ? env.AVISO_CORREO.split(",")[0].trim() : undefined, subject: "La Nogalera: te mandamos el brochure en cuanto esté listo", text: texto, html }) });
  } catch (e) { /* el prospecto ya quedó guardado */ }
}

async function listarProspectos(request, env) {
  const url = new URL(request.url);
  if ((url.searchParams.get("clave") || request.headers.get("x-clave")) !== claveAdmin(env)) return json({ error: "Clave incorrecta" }, 401);
  if (!env.PROSPECTOS) return json({ error: "Falta la base de datos (binding PROSPECTOS)." }, 503);
  const stub = env.PROSPECTOS.get(env.PROSPECTOS.idFromName("todos"));
  const filas = await stub.listar();
  if (url.searchParams.get("formato") === "csv") {
    const cols = ["id", "fecha", "nombre", "celular", "correo", "casa", "credito", "rapidez", "mensaje", "origen", "pais", "ciudad", "agente"];
    const esc = v => '"' + String(v ?? "").replace(/"/g, '""') + '"';
    const csv = "﻿" + cols.join(",") + "\n" + filas.map(f => cols.map(k => esc(f[k])).join(",")).join("\n");
    return new Response(csv, { headers: { "content-type": "text/csv; charset=utf-8", "content-disposition": 'attachment; filename="prospectos-nogalera.csv"', "cache-control": "no-store" } });
  }
  return json({ total: filas.length, prospectos: filas });
}

/* ---------- renders con IA ---------- */
async function renderIA(request, env) {
  if (request.method === "GET") return json({ listo: !!env.OPENAI_API_KEY, clave: true, provisional: !env.RENDER_CLAVE });
  if (request.method !== "POST") return json({ error: "Usa POST" }, 405);
  if (!env.OPENAI_API_KEY) return json({ error: "Falta el secreto OPENAI_API_KEY en el Worker (Settings → Variables and Secrets, o npx wrangler secret put OPENAI_API_KEY)." }, 503);
  let cuerpo;
  try { cuerpo = await request.json(); } catch (e) { return json({ error: "Cuerpo inválido" }, 400); }
  const clave = request.headers.get("x-clave") || cuerpo.clave || "";
  if (clave !== claveRender(env)) return json({ error: "Clave incorrecta" }, 401);
  const prompt = String(cuerpo.prompt || "").slice(0, 6000);
  if (prompt.length < 20) return json({ error: "Falta el prompt" }, 400);
  const modelo = /^[a-z0-9.-]+$/i.test(cuerpo.modelo || "") ? cuerpo.modelo : "gpt-image-2";
  const calidad = ["low", "medium", "high", "auto"].includes(cuerpo.calidad) ? cuerpo.calidad : "high";
  const tamano = ["1024x1024", "1536x1024", "1024x1536", "auto"].includes(cuerpo.tamano) ? cuerpo.tamano : "1536x1024";
  const n = Math.max(1, Math.min(4, parseInt(cuerpo.variantes || 1, 10) || 1));
  const t0 = Date.now();
  let r;
  try {
    if (cuerpo.referencia && /^data:image\/(jpeg|png);base64,/.test(cuerpo.referencia)) {
      // con la maqueta como referencia: images/edits (multipart)
      const [cab, b64] = cuerpo.referencia.split(",");
      const tipo = cab.includes("png") ? "image/png" : "image/jpeg";
      const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
      const fd = new FormData();
      fd.append("model", modelo); fd.append("prompt", prompt); fd.append("n", String(n)); fd.append("size", tamano); fd.append("quality", calidad);
      fd.append("image[]", new Blob([bin], { type: tipo }), "maqueta." + (tipo === "image/png" ? "png" : "jpg"));
      r = await fetch("https://api.openai.com/v1/images/edits", { method: "POST", headers: { authorization: "Bearer " + env.OPENAI_API_KEY }, body: fd });
    } else {
      r = await fetch("https://api.openai.com/v1/images/generations", { method: "POST", headers: { authorization: "Bearer " + env.OPENAI_API_KEY, "content-type": "application/json" },
        body: JSON.stringify({ model: modelo, prompt, n, size: tamano, quality: calidad }) });
    }
  } catch (e) { return json({ error: "No se pudo llamar a OpenAI: " + String(e) }, 502); }
  const texto = await r.text();
  if (!r.ok) return json({ error: "OpenAI respondió " + r.status, detalle: texto.slice(0, 1500) }, 502);
  let datos; try { datos = JSON.parse(texto); } catch (e) { return json({ error: "Respuesta inválida de OpenAI" }, 502); }
  const imagenes = (datos.data || []).map(d => d.b64_json ? "data:image/png;base64," + d.b64_json : d.url).filter(Boolean);
  return json({ imagenes, modelo, calidad, tamano, ms: Date.now() - t0, uso: datos.usage || null });
}
