// Frontend real: habla con el backend Python local (FastAPI) por HTTP y
// recibe el progreso de descarga por WebSocket.
const API = "http://127.0.0.1:8765";
const $ = (id) => document.getElementById(id);

// barra de título custom
$("tb-min").addEventListener("click", () => window.wctl.minimizar());
$("tb-close").addEventListener("click", () => window.wctl.cerrar());
$("tb-theme").addEventListener("click", () =>
  document.documentElement.classList.toggle("oscuro"));

let seleccion = null;      // {format_id, height, label} o {format_id:"mp3"}
let urlActual = "";
let descargando = false;

function estado(msg, tipo) {
  const e = $("estado");
  e.textContent = msg || "";
  e.className = "estado" + (tipo ? " " + tipo : "");
}

// ── WebSocket de progreso (reconecta solo) ──
function conectarWS() {
  const ws = new WebSocket(`ws://127.0.0.1:8765/ws`);
  ws.onmessage = (ev) => manejarProgreso(JSON.parse(ev.data));
  ws.onclose = () => setTimeout(conectarWS, 1500);
}
conectarWS();

function manejarProgreso(m) {
  const track = document.querySelector(".track");
  if (m.status === "downloading") {
    $("progreso").classList.remove("oculto");
    const ancho = track.clientWidth - 6;
    $("fill").style.width = (ancho * m.pct) / 100 + "px";
    $("knob").style.left = 3 + (ancho * m.pct) / 100 + "px";
    $("pct").textContent = m.pct.toFixed(0) + "%";
    let det = `${seleccion ? seleccion.label : ""} · ${m.speed} MB/s`;
    if (m.eta) det += ` · ETA ${m.eta}s`;
    $("detalle").textContent = det;
  } else if (m.status === "processing") {
    $("pct").textContent = "Processing…";
    $("detalle").textContent = "merging / converting with ffmpeg";
  } else if (m.status === "done") {
    descargando = false;
    $("dl").classList.remove("quieto");
    const ancho = track.clientWidth - 6;
    $("fill").style.width = ancho + "px";
    $("knob").style.left = 3 + ancho + "px";
    $("pct").textContent = "✓ Complete";
    $("pct").classList.add("fin");
    $("detalle").textContent = "saved to " + m.folder;
  } else if (m.status === "blocked" || m.status === "error") {
    descargando = false;
    $("dl").classList.remove("quieto");
    $("pct").textContent = "✗ Failed";
    $("detalle").textContent = "";
    estado(m.message, "error");
  }
}

// ── cargar vídeo (extracción real) ──
$("load").addEventListener("click", async () => {
  const url = $("url").value.trim();
  if (!url) { estado("Please enter a YouTube URL.", "error"); return; }

  const btn = $("load");
  btn.disabled = true;
  estado("");
  let segundos = 0;
  btn.textContent = "Loading…";
  const contador = setInterval(() => {
    segundos++;
    btn.textContent = `Loading… ${segundos}s`;
  }, 1000);

  try {
    const r = await fetch(API + "/api/load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const datos = await r.json();
    if (datos.error) { estado(datos.error, "error"); return; }

    urlActual = url;
    // tarjeta de vídeo
    $("thumb-img").src = datos.thumbnail;
    $("dur").textContent = datos.duration;
    $("titulo").textContent = datos.title;
    $("canal").textContent = datos.channel;
    $("video").classList.remove("oculto");
    requestAnimationFrame(() => $("video").classList.add("visible"));

    // chips: 2 mejores calidades reales + MP3
    const chips = $("chips");
    chips.innerHTML = "";
    const opciones = [
      ...datos.top.map((f) => ({ ...f, texto: f.height >= 2160 ? "4K" : f.height + "p" })),
      { format_id: "mp3", height: 0, label: "MP3", texto: "MP3" },
    ];
    opciones.forEach((op, i) => {
      const c = document.createElement("button");
      c.className = "chip";
      c.textContent = op.texto;
      c.title = op.label;
      c.addEventListener("click", () => {
        chips.querySelectorAll(".chip").forEach((x) => x.classList.remove("sel"));
        c.classList.add("sel");
        seleccion = op;
      });
      chips.appendChild(c);
      setTimeout(() => {
        c.classList.add("visible");
        if (i === 0) { c.classList.add("sel"); seleccion = op; }
      }, 120 * i + 150);
    });

    setTimeout(() => $("dl").classList.remove("oculto"), 120 * opciones.length + 300);
  } catch (e) {
    estado("Backend not reachable. Is the Python server running?", "error");
  } finally {
    clearInterval(contador);
    btn.disabled = false;
    btn.textContent = "Load Video";
  }
});

// ── descargar (real) ──
$("dl").addEventListener("click", async () => {
  if (descargando || !seleccion || !urlActual) return;
  descargando = true;
  $("dl").classList.add("quieto");
  $("progreso").classList.remove("oculto");
  $("pct").classList.remove("fin");
  $("pct").textContent = "0%";
  $("detalle").textContent = "starting…";
  estado("");

  try {
    const r = await fetch(API + "/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: urlActual,
        format_id: seleccion.format_id,
        height: seleccion.height || null,
        ratelimit: null,
      }),
    });
    const datos = await r.json();
    if (datos.error) {
      descargando = false;
      $("dl").classList.remove("quieto");
      estado(datos.error, "error");
    }
  } catch (e) {
    descargando = false;
    $("dl").classList.remove("quieto");
    estado("Backend not reachable.", "error");
  }
});

// ── banner de actualización interactivo ──
let updEstado = "idle"; // idle -> disponible -> descargando -> listo
function updRender(datos) {
  const caja = $("upd"), txt = $("upd-txt"), btn = $("upd-btn"),
        bar = $("upd-bar"), fill = $("upd-fill");
  if (datos.tipo === "disponible") {
    updEstado = "disponible";
    txt.textContent = `Version ${datos.version} available`;
    btn.textContent = "Install";
    btn.disabled = false;
    caja.classList.remove("oculto");
  } else if (datos.tipo === "progreso") {
    updEstado = "descargando";
    bar.classList.remove("oculto");
    fill.style.width = Math.round(datos.pct) + "%";
    txt.textContent = `Downloading update… ${Math.round(datos.pct)}%`;
    btn.textContent = "Install";
    btn.disabled = true;
  } else if (datos.tipo === "listo") {
    updEstado = "listo";
    bar.classList.add("oculto");
    txt.textContent = "Update ready ✓";
    btn.textContent = "Restart";
    btn.disabled = false;
  } else if (datos.tipo === "error") {
    updEstado = "idle";
    txt.textContent = "Update failed — will retry on next launch";
    btn.disabled = true;
    setTimeout(() => caja.classList.add("oculto"), 6000);
  }
}
if (window.updater) window.updater.onEvento(updRender);
$("upd-btn").addEventListener("click", () => {
  if (updEstado === "disponible") {
    window.SIM_UPD ? window.SIM_UPD() : window.updater.descargar();
  } else if (updEstado === "listo") {
    if (!window.SIM_UPD) window.updater.instalar();
  }
});

// ── modos demo (capturas automatizadas) ──
// demo=1: carga un vídeo real y cambia a oscuro (screenshots claro+oscuro)
// demo=2: flujo completo para el GIF — carga, selecciona y descarga de verdad
// simulación del banner de update para verificación visual en dev:
// npx electron . -- (con ?updtest=1) recorre disponible→descarga→listo sin red
if (new URLSearchParams(location.search).get("updtest") === "1") {
  window.SIM_UPD = () => {
    let p = 0;
    const t = setInterval(() => {
      p += 7;
      updRender({ tipo: "progreso", pct: Math.min(100, p) });
      if (p >= 100) { clearInterval(t); updRender({ tipo: "listo" }); }
    }, 180);
  };
  setTimeout(() => updRender({ tipo: "disponible", version: "9.9.9" }), 800);
  setTimeout(() => $("upd-btn").click(), 2200); // pulsa Install solo
}

const DEMO = new URLSearchParams(location.search).get("demo");
if (DEMO === "1" || DEMO === "2") {
  // demo 1 (screenshots): vídeo corto. demo 2 (GIF): vídeo grande para que
  // la barra de progreso se aprecie varios segundos con velocidad y ETA.
  $("url").value = DEMO === "1"
    ? "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    : "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
  setTimeout(() => $("load").click(), 1200);
  if (DEMO === "1") {
    setTimeout(() => $("tb-theme").click(), 10000);
  } else {
    // al aparecer el botón: elegir el 2º chip (1440p) y descargar
    const espera = setInterval(() => {
      if (!$("dl").classList.contains("oculto")) {
        clearInterval(espera);
        const chips = document.querySelectorAll(".chip");
        if (chips[1]) chips[1].click();
        setTimeout(() => $("dl").click(), 1200);
      }
    }, 200);
  }
}
