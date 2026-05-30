// =====================================================
// Executive Dashboard
// =====================================================
// KPI cards + realtime overview + system health + live
// camera snapshot grid. Reads /api/dashboard and /api/sources.

let ageChart;
let snapshotSig = "";   // signature of current camera grid (rebuild only on change)

function initAgeChart() {
    const el = document.getElementById("ageChart");
    if (!el) return;
    ageChart = new Chart(el, {
        type: "bar",
        data: {
            labels: ["0-17", "18-25", "26-35", "36-50", "51+"],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: ["#00ff99", "#38bdf8", "#f59e0b", "#ef4444", "#a78bfa"],
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#94a3b8" } },
                y: { ticks: { color: "#94a3b8" }, beginAtZero: true },
            },
        },
    });
}

function setText(id, v) {
    const el = document.getElementById(id);
    if (el) el.innerText = v;
}

async function loadDashboard() {
    try {
        const d = await API.get("/api/dashboard");

        // KPI cards
        setText("kpi-footfall", d.kpi.current_footfall);
        setText("kpi-today", d.kpi.today_visitors);
        setText("kpi-peak", d.kpi.peak_hour);
        setText("kpi-dwell", d.kpi.avg_dwell);
        setText("kpi-cameras", d.kpi.active_cameras);
        setText("kpi-zones", d.kpi.active_zones);

        // realtime
        setText("rt-live", d.realtime.live_count);
        const m = d.realtime.male, f = d.realtime.female;
        const total = Math.max(1, m + f);
        const mp = Math.round((m / total) * 100);
        const maleBar = document.getElementById("rt-male-bar");
        const femBar = document.getElementById("rt-female-bar");
        if (maleBar && femBar) {
            maleBar.style.width = mp + "%";
            femBar.style.width = (100 - mp) + "%";
            maleBar.textContent = "M " + m;
            femBar.textContent = "F " + f;
        }

        // age chart
        if (ageChart && d.realtime.age) {
            ageChart.data.datasets[0].data = Object.values(d.realtime.age);
            ageChart.update();
        }

        // system health
        const hw = document.getElementById("h-writer");
        if (hw) hw.className = d.system_health.db_writer ? "ok" : "bad";
        const hc = document.getElementById("h-cams");
        const online = d.system_health.cameras_online;
        const tot = d.system_health.cameras_total;
        if (hc) hc.className = online > 0 ? "ok" : "bad";
        setText("h-cams-count", `${online} / ${tot}`);
    } catch (e) {
        console.error("dashboard error", e);
    }
}

async function loadAlertsFeed() {
    try {
        const alerts = await API.get("/api/alerts");
        const box = document.getElementById("dash-alerts");
        if (!box) return;
        box.innerHTML = alerts.length
            ? alerts.slice(0, 6).map(a => `
                <div class="notif-item sev-${a.severity}">
                    <b>${a.type}</b> — <span class="muted">${a.message}</span><br>
                    <small class="muted">${a.ts}</small>
                </div>`).join("")
            : '<p class="muted">No alerts</p>';
    } catch (e) {}
}

async function refreshSnapshots() {
    try {
        const cams = await API.get("/api/sources");
        const grid = document.getElementById("snapshot-grid");
        if (!grid) return;

        const sig = cams.map(c => `${c.id}:${c.running}`).join("|");
        if (sig !== snapshotSig) {
            // rebuild grid structure
            snapshotSig = sig;
            grid.innerHTML = cams.map(c => `
                <div class="snapshot-card">
                    ${c.running
                        ? `<img id="snap-${c.id}" src="/api/sources/${c.id}/snapshot" alt="${c.name}">`
                        : `<div style="aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;background:#000;color:#666">stopped</div>`}
                    <div class="meta">
                        <span><span class="dot ${c.running ? 'online' : 'offline'}"></span>${c.name}</span>
                        <span class="muted" id="fps-${c.id}">${c.running ? c.fps + ' fps' : c.source_type}</span>
                    </div>
                </div>`).join("");
        }
        // refresh running snapshots (cache-bust) + fps label
        const t = Date.now();
        cams.filter(c => c.running).forEach(c => {
            const img = document.getElementById(`snap-${c.id}`);
            if (img) img.src = `/api/sources/${c.id}/snapshot?t=${t}`;
            const fps = document.getElementById(`fps-${c.id}`);
            if (fps) fps.textContent = c.fps + ' fps';
        });
    } catch (e) {}
}

// ---- boot ----
initAgeChart();
loadDashboard();
loadAlertsFeed();
refreshSnapshots();
setInterval(loadDashboard, 2000);
setInterval(loadAlertsFeed, 8000);
setInterval(refreshSnapshots, 1500);

// react to live socket metrics for snappier KPI updates
document.addEventListener("retail-metrics", loadDashboard);
