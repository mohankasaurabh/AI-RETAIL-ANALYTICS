// =====================================================
// Analytics Page Charts
// =====================================================
// Footfall (hourly), demographics (gender pie + age bar),
// zone ranking, and customer-journey list. Uses Chart.js
// and the /api/* endpoints. Polls on an interval and also
// refreshes immediately on the "retail-metrics" socket
// event re-broadcast by websocket.js.
// =====================================================

const ACCENT = "#00ff99";
const ACCENT2 = "#38bdf8";
const PALETTE = ["#00ff99", "#38bdf8", "#f59e0b", "#ef4444", "#a78bfa", "#f472b6"];

let footfallChart, genderChart, ageChart;

// ---------- chart builders ----------

function initCharts() {

    const ff = document.getElementById("footfallChart");
    if (ff) {
        footfallChart = new Chart(ff, {
            type: "bar",
            data: {
                labels: [],
                datasets: [{
                    label: "Entries / hour",
                    data: [],
                    backgroundColor: ACCENT2,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: "#cbd5e1" } } },
                scales: {
                    x: { ticks: { color: "#94a3b8" } },
                    y: { ticks: { color: "#94a3b8" }, beginAtZero: true }
                }
            }
        });
    }

    const g = document.getElementById("genderChart");
    if (g) {
        genderChart = new Chart(g, {
            type: "doughnut",
            data: {
                labels: ["Male", "Female"],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: [ACCENT2, "#f472b6"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: "#cbd5e1" } } }
            }
        });
    }

    const a = document.getElementById("ageChart");
    if (a) {
        ageChart = new Chart(a, {
            type: "bar",
            data: {
                labels: [],
                datasets: [{
                    label: "Customers",
                    data: [],
                    backgroundColor: PALETTE,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: "#94a3b8" } },
                    y: { ticks: { color: "#94a3b8" }, beginAtZero: true }
                }
            }
        });
    }
}

// ---------- data loaders ----------

async function loadFootfall() {
    if (!footfallChart) return;
    try {
        const d = await (await fetch("/api/footfall")).json();
        footfallChart.data.labels = d.labels || [];
        footfallChart.data.datasets[0].data = d.entries || [];
        footfallChart.update();
    } catch (e) { console.error(e); }
}

async function loadDemographics() {
    try {
        const d = await (await fetch("/api/demographics")).json();
        if (genderChart) {
            genderChart.data.datasets[0].data = [d.male || 0, d.female || 0];
            genderChart.update();
        }
        if (ageChart) {
            ageChart.data.labels = d.age_labels || [];
            ageChart.data.datasets[0].data = d.age_values || [];
            ageChart.update();
        }
    } catch (e) { console.error(e); }
}

async function loadZoneRanking() {
    const box = document.getElementById("zone-ranking");
    if (!box) return;
    try {
        const d = await (await fetch("/api/zone_ranking")).json();
        const zones = d.zones || [];
        if (!zones.length) {
            box.innerHTML = '<p class="muted">No zone data yet.</p>';
        } else {
            const max = Math.max(1, ...zones.map(z => z.count));
            box.innerHTML = zones.map(z => `
                <div class="zone-bar">
                    <div class="label"><span>${z.zone}</span><span>${z.count}</span></div>
                    <div class="track"><div class="fill"
                        style="width:${(z.count / max) * 100}%"></div></div>
                </div>`).join("");
        }
        const top = (d.top || []).map(z => z.zone).join(", ") || "—";
        const dead = (d.dead || []).map(z => z.zone).join(", ") || "none";
        document.getElementById("top-zones").innerText = top;
        document.getElementById("dead-zones").innerText = dead;
    } catch (e) { console.error(e); }
}

async function loadJourneys() {
    const body = document.getElementById("journey-body");
    if (!body) return;
    try {
        const d = await (await fetch("/api/journey_list")).json();
        document.getElementById("journey-total").innerText = d.total || 0;
        const rows = d.customers || [];
        if (!rows.length) {
            body.innerHTML =
                '<tr><td colspan="3" class="muted">Waiting for customers…</td></tr>';
            return;
        }
        body.innerHTML = rows.slice(0, 25).map(c => `
            <tr>
                <td>Customer #${c.customer_id}</td>
                <td>${c.age}</td>
                <td>${c.gender}</td>
            </tr>`).join("");
    } catch (e) { console.error(e); }
}

function refreshAll() {
    loadFootfall();
    loadDemographics();
    loadZoneRanking();
    loadJourneys();
}

// ---------- boot ----------

initCharts();
refreshAll();
setInterval(refreshAll, 4000);

// react instantly to live socket pushes
document.addEventListener("retail-metrics", function () {
    loadDemographics();
    loadZoneRanking();
    loadJourneys();
});
