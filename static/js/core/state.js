// =====================================================
// Global UI state (store + date range) and topbar wiring
// =====================================================
// Pages read RetailState.store / RetailState.range and listen
// for the "retail-state-change" event to refetch scoped data.

window.RetailState = {
    store: localStorage.getItem("retail-store") || "1",
    range: localStorage.getItem("retail-range") || "all",

    setStore(v) {
        this.store = v;
        localStorage.setItem("retail-store", v);
        this._emit();
    },
    setRange(v) {
        this.range = v;
        localStorage.setItem("retail-range", v);
        this._emit();
    },
    _emit() {
        document.dispatchEvent(new CustomEvent("retail-state-change", {
            detail: { store: this.store, range: this.range },
        }));
    },
};

document.addEventListener("DOMContentLoaded", () => {

    // ---- store selector ----
    const storeSel = document.getElementById("store-select");
    if (storeSel) {
        API.get("/api/stores").then(stores => {
            storeSel.innerHTML = stores
                .map(s => `<option value="${s.id}">${s.name}</option>`).join("");
            storeSel.value = RetailState.store;
        }).catch(() => {});
        storeSel.addEventListener("change", e => RetailState.setStore(e.target.value));
    }

    // ---- date range selector ----
    const rangeSel = document.getElementById("range-select");
    if (rangeSel) {
        rangeSel.value = RetailState.range;
        rangeSel.addEventListener("change", e => RetailState.setRange(e.target.value));
    }

    // ---- theme toggle ----
    const saved = localStorage.getItem("retail-theme") || "dark";
    if (saved === "light") document.body.classList.add("light");
    const themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
        themeBtn.textContent = saved === "light" ? "☀️" : "🌙";
        themeBtn.addEventListener("click", () => {
            document.body.classList.toggle("light");
            const light = document.body.classList.contains("light");
            localStorage.setItem("retail-theme", light ? "light" : "dark");
            themeBtn.textContent = light ? "☀️" : "🌙";
        });
    }

    // ---- notifications ----
    const notifBtn = document.getElementById("notif-btn");
    const dropdown = document.getElementById("notif-dropdown");
    if (notifBtn && dropdown) {
        notifBtn.addEventListener("click", () => {
            dropdown.classList.toggle("open");
        });
        document.addEventListener("click", (e) => {
            if (!document.getElementById("notif").contains(e.target)) {
                dropdown.classList.remove("open");
            }
        });
        loadAlerts();
        setInterval(loadAlerts, 8000);
    }

    function loadAlerts() {
        API.get("/api/alerts").then(alerts => {
            const badge = document.getElementById("notif-badge");
            const list = document.getElementById("notif-list");
            const unack = alerts.filter(a => !a.acknowledged);
            if (badge) {
                badge.style.display = unack.length ? "inline-block" : "none";
                badge.textContent = unack.length;
            }
            if (list) {
                list.innerHTML = alerts.length
                    ? alerts.slice(0, 10).map(a => `
                        <div class="notif-item sev-${a.severity}" style="${a.acknowledged ? 'opacity:.5' : ''}">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <b>${a.type}</b>
                                ${a.acknowledged ? '' : `<button class="btn-outline" style="padding:2px 8px;font-size:11px;" onclick="ackAlert(${a.id})">ack</button>`}
                            </div>
                            <span class="muted">${a.message}</span><br>
                            <small class="muted">${a.ts}</small>
                        </div>`).join("")
                    : '<p class="muted" style="padding:10px">No alerts</p>';
            }
        }).catch(() => {});
    }
    window.reloadAlerts = loadAlerts;

    window.ackAlert = function (id) {
        API.post(`/api/alerts/${id}/ack`).then(loadAlerts).catch(() => {});
    };
});
