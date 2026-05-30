// =====================================================
// Camera & Media Sources page
// =====================================================

let currentFilter = "all";
let sourcesCache = [];

// ---------- filters ----------
document.querySelectorAll("#filter-tabs .chip").forEach(chip => {
    chip.addEventListener("click", () => {
        document.querySelectorAll("#filter-tabs .chip").forEach(c => c.classList.remove("active"));
        chip.classList.add("active");
        currentFilter = chip.dataset.filter;
        render();
    });
});

function statusOf(c) {
    if (c.running) return c.runtime_status === "offline" ? "offline" : "processing";
    return c.runtime_status === "offline" ? "offline" : "stopped";
}

// ---------- load + render ----------
async function loadSources() {
    try {
        sourcesCache = await API.get("/api/sources");
        // summary
        document.getElementById("s-total").innerText = sourcesCache.length;
        document.getElementById("s-active").innerText =
            sourcesCache.filter(c => c.running && c.runtime_status !== "offline").length;
        document.getElementById("s-processing").innerText =
            sourcesCache.filter(c => statusOf(c) === "processing").length;
        document.getElementById("s-offline").innerText =
            sourcesCache.filter(c => statusOf(c) === "offline").length;
        render();
    } catch (e) { console.error(e); }
}

function render() {
    const grid = document.getElementById("sources-grid");
    let cams = sourcesCache;
    if (currentFilter !== "all") {
        cams = cams.filter(c => {
            if (currentFilter === "active") return c.running && statusOf(c) === "processing";
            return statusOf(c) === currentFilter;
        });
    }
    if (!cams.length) {
        grid.innerHTML = '<p class="muted">No sources in this view.</p>';
        return;
    }
    grid.innerHTML = cams.map(c => {
        const st = statusOf(c);
        const models = Object.entries(c.models_enabled || {})
            .filter(([, v]) => v).map(([k]) => k).join(", ") || "none";
        return `
        <div class="panel" style="margin:0;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <h3 style="margin:0;font-size:16px;">${c.name}</h3>
                <span class="badge ${st === 'processing' ? 'low' : st === 'offline' ? 'high' : 'medium'}">${st.toUpperCase()}</span>
            </div>
            ${c.running
                ? `<img src="/api/sources/${c.id}/snapshot?t=${Date.now()}" class="video-frame" style="margin:10px 0;aspect-ratio:16/9;object-fit:cover;">`
                : `<div class="video-frame" style="margin:10px 0;aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;color:#666;">stopped</div>`}
            <table class="data-table" style="font-size:12px;">
                <tr><td>Type</td><td>${c.source_type}</td></tr>
                <tr><td>Location</td><td>${c.location || '—'}</td></tr>
                <tr><td>Resolution</td><td>${c.resolution}</td></tr>
                <tr><td>FPS</td><td>${c.running ? c.fps : c.fps_target}</td></tr>
                <tr><td>Models</td><td>${models}</td></tr>
            </table>
            <div class="controls-row" style="margin-top:12px;">
                ${c.running
                    ? `<button class="btn-outline" onclick="stopSource(${c.id})">Stop</button>`
                    : `<button class="btn" onclick="startSource(${c.id})">Start</button>`}
                <button class="btn-outline" onclick="editSource(${c.id})">Edit</button>
                <button class="btn-outline" onclick="deleteSource(${c.id})">Delete</button>
            </div>
        </div>`;
    }).join("");
}

// ---------- runtime control ----------
async function startSource(id) { await API.post(`/api/sources/${id}/start`); setTimeout(loadSources, 800); }
async function stopSource(id) { await API.post(`/api/sources/${id}/stop`); setTimeout(loadSources, 500); }
async function deleteSource(id) {
    if (!confirm("Delete this source?")) return;
    await API.del(`/api/sources/${id}`);
    loadSources();
}

// ---------- modal ----------
function openSourceModal() {
    document.getElementById("modal-title").innerText = "Add Source";
    document.getElementById("f-id").value = "";
    document.getElementById("f-name").value = "";
    document.getElementById("f-type").value = "video";
    document.getElementById("f-uri").value = "";
    document.getElementById("f-location").value = "";
    document.getElementById("f-resolution").value = "1280x720";
    document.getElementById("f-fps").value = 10;
    document.querySelectorAll("#f-models input").forEach(i => i.checked = true);
    const file = document.getElementById("f-file"); if (file) file.value = "";
    onTypeChange();
    document.getElementById("source-modal").classList.add("open");
}
function closeSourceModal() {
    document.getElementById("source-modal").classList.remove("open");
}
function onTypeChange() {
    const type = document.getElementById("f-type").value;
    const isVideo = type === "video";
    document.getElementById("upload-row").style.display = isVideo ? "block" : "none";
    const label = document.getElementById("uri-label");
    if (type === "webcam") label.innerText = "Device Index (e.g. 0)";
    else if (isVideo) label.innerText = "Path (or upload below)";
    else label.innerText = "Stream URL";
}

function editSource(id) {
    const c = sourcesCache.find(x => x.id === id);
    if (!c) return;
    document.getElementById("modal-title").innerText = "Edit Source";
    document.getElementById("f-id").value = c.id;
    document.getElementById("f-name").value = c.name;
    document.getElementById("f-type").value = c.source_type;
    document.getElementById("f-uri").value = c.uri;
    document.getElementById("f-location").value = c.location || "";
    document.getElementById("f-resolution").value = c.resolution;
    document.getElementById("f-fps").value = c.fps_target;
    document.querySelectorAll("#f-models input").forEach(i => {
        i.checked = !!(c.models_enabled || {})[i.dataset.model];
    });
    onTypeChange();
    document.getElementById("source-modal").classList.add("open");
}

async function saveSource() {
    const id = document.getElementById("f-id").value;
    const type = document.getElementById("f-type").value;
    let uri = document.getElementById("f-uri").value.trim();

    // handle upload for video type
    const fileInput = document.getElementById("f-file");
    if (type === "video" && fileInput && fileInput.files.length) {
        const fd = new FormData();
        fd.append("file", fileInput.files[0]);
        const r = await fetch("/api/sources/upload", { method: "POST", body: fd });
        const res = await r.json();
        if (res.success) uri = res.path;
        else { alert("Upload failed: " + res.message); return; }
    }

    const models = {};
    document.querySelectorAll("#f-models input").forEach(i => {
        models[i.dataset.model] = i.checked;
    });

    const payload = {
        name: document.getElementById("f-name").value.trim(),
        source_type: type,
        uri: uri,
        location: document.getElementById("f-location").value.trim(),
        resolution: document.getElementById("f-resolution").value.trim(),
        fps_target: parseInt(document.getElementById("f-fps").value, 10),
        models_enabled: models,
    };
    if (!payload.name) { alert("Name is required"); return; }

    try {
        if (id) await API.put(`/api/sources/${id}`, payload);
        else await API.post("/api/sources", payload);
        closeSourceModal();
        loadSources();
    } catch (e) { alert("Save failed: " + e.message); }
}

// ---------- boot ----------
loadSources();
setInterval(loadSources, 4000);
