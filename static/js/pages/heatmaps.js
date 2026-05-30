// =====================================================
// Heatmap Analytics — live + historical density
// =====================================================

const FW = 1280, FH = 720;
let hmCamera = null;
let hmMode = "live";
let zoneDensityChart, hmHourlyChart;

const hmCanvas = document.getElementById("hm-canvas");
const hmBg = document.getElementById("hm-bg");
const hmCtx = hmCanvas.getContext("2d");

// ---- heat colour ramp (blue→green→yellow→red) ----
function heatColor(t) {
    t = Math.max(0, Math.min(1, t));
    const stops = [[37, 99, 235], [34, 197, 94], [234, 179, 8], [239, 68, 68]];
    const seg = t * (stops.length - 1), i = Math.floor(seg), f = seg - i;
    const a = stops[i], b = stops[Math.min(i + 1, stops.length - 1)];
    return [Math.round(a[0] + (b[0] - a[0]) * f),
            Math.round(a[1] + (b[1] - a[1]) * f),
            Math.round(a[2] + (b[2] - a[2]) * f)];
}

function renderHeatmap(points) {
    const w = hmCanvas.clientWidth || 640;
    const h = Math.round(w * FH / FW);
    hmCanvas.width = w; hmCanvas.height = h; hmCanvas.style.height = h + "px";
    hmCtx.clearRect(0, 0, w, h);
    if (!points.length) return;

    hmCtx.globalCompositeOperation = "lighter";
    const radius = Math.max(12, w * 0.028);
    points.forEach(p => {
        const x = p.x * w / FW, y = p.y * h / FH;
        const g = hmCtx.createRadialGradient(x, y, 0, x, y, radius);
        g.addColorStop(0, "rgba(255,255,255,0.28)");
        g.addColorStop(1, "rgba(255,255,255,0)");
        hmCtx.fillStyle = g;
        hmCtx.beginPath(); hmCtx.arc(x, y, radius, 0, Math.PI * 2); hmCtx.fill();
    });
    hmCtx.globalCompositeOperation = "source-over";

    const img = hmCtx.getImageData(0, 0, w, h);
    const d = img.data;
    for (let i = 0; i < d.length; i += 4) {
        const v = d[i];
        if (!v) continue;
        const [r, g, b] = heatColor(Math.min(1, v / 200));
        d[i] = r; d[i + 1] = g; d[i + 2] = b; d[i + 3] = Math.min(220, v + 40);
    }
    hmCtx.putImageData(img, 0, 0);
}

// ---- charts ----
function initHmCharts() {
    const opts = {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { color: "#94a3b8" } }, y: { ticks: { color: "#94a3b8" }, beginAtZero: true } },
    };
    zoneDensityChart = new Chart(document.getElementById("zoneDensityChart"),
        { type: "bar", data: { labels: [], datasets: [{ data: [], backgroundColor: "#ef4444", borderRadius: 4 }] }, options: opts });
    hmHourlyChart = new Chart(document.getElementById("hmHourlyChart"),
        { type: "line", data: { labels: [], datasets: [{ data: [], borderColor: "#38bdf8", backgroundColor: "rgba(56,189,248,.15)", fill: true, tension: 0.3 }] }, options: opts });
}

// ---- data ----
async function loadCameras() {
    const cams = await API.get("/api/sources");
    const sel = document.getElementById("hm-camera");
    sel.innerHTML = cams.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    sel.addEventListener("change", () => selectCamera(parseInt(sel.value, 10)));
    if (cams.length) selectCamera(cams[0].id);
}

function selectCamera(id) {
    hmCamera = id;
    API.post(`/api/sources/${id}/start`).catch(() => {});
    refreshBg();
    loadHeatmap();
}
function refreshBg() {
    if (hmCamera) hmBg.src = `/api/sources/${hmCamera}/snapshot?t=${Date.now()}`;
}

async function loadHeatmap() {
    if (!hmCamera) return;
    const range = document.getElementById("hm-range").value;
    const d = await API.get(`/api/cameras/${hmCamera}/heatmap?mode=${hmMode}&range=${range}`);

    renderHeatmap(d.points);

    document.getElementById("m-total").innerText = d.metrics.total_points;
    document.getElementById("m-peak").innerText = d.metrics.peak_density;
    document.getElementById("m-avg").innerText = d.metrics.avg_density;
    document.getElementById("m-hot").innerText =
        d.metrics.hot_zones[0] ? `${d.metrics.hot_zones[0].zone}` : "—";
    document.getElementById("m-cold").innerText =
        d.metrics.cold_zones[0] ? `${d.metrics.cold_zones[0].zone}` : "—";

    zoneDensityChart.data.labels = d.zone_density.map(z => z.zone);
    zoneDensityChart.data.datasets[0].data = d.zone_density.map(z => z.count);
    zoneDensityChart.update();

    hmHourlyChart.data.labels = d.hourly.labels;
    hmHourlyChart.data.datasets[0].data = d.hourly.counts;
    hmHourlyChart.update();
}

// ---- mode tabs ----
document.getElementById("mode-live").addEventListener("click", () => setMode("live"));
document.getElementById("mode-historical").addEventListener("click", () => setMode("historical"));
function setMode(m) {
    hmMode = m;
    document.getElementById("mode-live").classList.toggle("active", m === "live");
    document.getElementById("mode-historical").classList.toggle("active", m === "historical");
    document.getElementById("hm-range").style.display = m === "historical" ? "inline-block" : "none";
    loadHeatmap();
}
document.getElementById("hm-range").addEventListener("change", loadHeatmap);

// ---- boot ----
window.addEventListener("load", () => {
    initHmCharts();
    loadCameras();
    setInterval(() => { refreshBg(); if (hmMode === "live") loadHeatmap(); }, 2500);
});
