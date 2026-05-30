// =====================================================
// Live Monitoring — per-camera multi-feed grid
// =====================================================
// Each running camera streams its own annotated MJPEG via
// /video_feed/<id> (Phase 2 concurrent workers). Per-camera
// live metrics are polled from /api/sources/<id>/metrics.

let liveSig = "";

async function loadGrid() {
    let cams;
    try {
        cams = await API.get("/api/sources");
    } catch (e) { return; }

    const grid = document.getElementById("live-grid");
    const sig = cams.map(c => `${c.id}:${c.running}`).join("|");

    if (sig !== liveSig) {
        liveSig = sig;
        grid.innerHTML = cams.map(c => `
            <div class="snapshot-card">
                ${c.running
                    ? `<img src="/video_feed/${c.id}" alt="${c.name}">`
                    : `<div style="aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;background:#000;color:#666;">
                           <button class="btn" onclick="startCam(${c.id})">▶ Start ${c.name}</button>
                       </div>`}
                <div class="meta">
                    <span><span class="dot ${c.running ? 'online' : 'offline'}"></span>${c.name}
                        <span class="muted" style="font-size:11px;">(${c.source_type})</span></span>
                    ${c.running ? `<button class="btn-outline" style="padding:3px 10px;font-size:12px;" onclick="stopCam(${c.id})">Stop</button>` : ''}
                </div>
                <div class="meta" id="livemeta-${c.id}" style="border-top:1px solid var(--border);">
                    <span class="muted">${c.running ? 'loading metrics…' : 'stopped'}</span>
                </div>
            </div>`).join("");
    }

    // refresh per-camera metrics for running cameras
    cams.filter(c => c.running).forEach(async c => {
        try {
            const m = await API.get(`/api/sources/${c.id}/metrics`);
            const el = document.getElementById(`livemeta-${c.id}`);
            if (el) {
                el.innerHTML =
                    `<span>👥 ${m.occupancy} · 🚪 ${m.entries} · 🔁 ${m.reid_identities}</span>` +
                    `<span class="muted">M ${m.male_count} / F ${m.female_count} · Q ${m.queue_length}</span>`;
            }
        } catch (e) {}
    });
}

async function startCam(id) { await API.post(`/api/sources/${id}/start`); liveSig = ""; setTimeout(loadGrid, 800); }
async function stopCam(id) { await API.post(`/api/sources/${id}/stop`); liveSig = ""; setTimeout(loadGrid, 400); }
async function startAll() {
    const cams = await API.get("/api/sources");
    for (const c of cams.filter(c => !c.running && c.source_type !== "rtsp" && c.source_type !== "ip" && c.source_type !== "nvr")) {
        await API.post(`/api/sources/${c.id}/start`);
    }
    liveSig = "";
    setTimeout(loadGrid, 1000);
}
window.startCam = startCam;
window.stopCam = stopCam;
window.startAll = startAll;

window.addEventListener("load", () => {
    loadGrid();
    setInterval(loadGrid, 3000);
});
