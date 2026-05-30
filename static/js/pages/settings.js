// =====================================================
// Settings page
// =====================================================

async function loadSettings() {
    const s = await API.get("/api/settings");

    const models = s.default_models || {};
    document.querySelectorAll("#set-models input").forEach(i => {
        i.checked = !!models[i.dataset.model];
    });

    document.getElementById("set-reid-threshold").value = s.reid_threshold;
    document.getElementById("set-reid-timeout").value = s.reid_timeout;
    document.getElementById("set-db-backend").value = s.db_backend;
    document.getElementById("set-snapshot-freq").value = s.snapshot_frequency;
    document.getElementById("set-retention").value = s.retention_days;
    document.getElementById("set-alerts-enabled").checked = !!s.alerts_enabled;
    document.getElementById("set-alert-occupancy").value = s.alert_occupancy;
    document.getElementById("set-alert-queue").value = s.alert_queue_length;
}

async function saveSettings() {
    const models = {};
    document.querySelectorAll("#set-models input").forEach(i => {
        models[i.dataset.model] = i.checked;
    });

    const payload = {
        default_models: models,
        reid_threshold: parseFloat(document.getElementById("set-reid-threshold").value),
        reid_timeout: parseInt(document.getElementById("set-reid-timeout").value, 10),
        db_backend: document.getElementById("set-db-backend").value,
        snapshot_frequency: parseInt(document.getElementById("set-snapshot-freq").value, 10),
        retention_days: parseInt(document.getElementById("set-retention").value, 10),
        alerts_enabled: document.getElementById("set-alerts-enabled").checked,
        alert_occupancy: parseInt(document.getElementById("set-alert-occupancy").value, 10),
        alert_queue_length: parseInt(document.getElementById("set-alert-queue").value, 10),
    };

    const status = document.getElementById("set-status");
    try {
        await API.put("/api/settings", payload);
        status.textContent = "✓ Saved & applied";
        status.style.color = "var(--accent)";
    } catch (e) {
        status.textContent = "Save failed";
        status.style.color = "var(--danger)";
    }
    setTimeout(() => (status.textContent = ""), 3000);
}
window.saveSettings = saveSettings;

window.addEventListener("load", loadSettings);
