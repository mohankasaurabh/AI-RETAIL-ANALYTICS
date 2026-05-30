// =====================================================
// Customer Analytics page
// =====================================================

let genderChart, ageChart;

function currentRange() {
    return (window.RetailState && RetailState.range) || "all";
}

function initCharts() {
    genderChart = new Chart(document.getElementById("genderChart"), {
        type: "doughnut",
        data: { labels: ["Male", "Female"], datasets: [{ data: [0, 0], backgroundColor: ["#38bdf8", "#f472b6"] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#cbd5e1" } } } },
    });
    ageChart = new Chart(document.getElementById("ageChart"), {
        type: "bar",
        data: { labels: [], datasets: [{ data: [], backgroundColor: ["#00ff99", "#38bdf8", "#f59e0b", "#ef4444", "#a78bfa"], borderRadius: 4 }] },
        options: {
            responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
            scales: { x: { ticks: { color: "#94a3b8" } }, y: { ticks: { color: "#94a3b8" }, beginAtZero: true } },
        },
    });
}

async function loadDemographics() {
    const d = await API.get(`/api/customers/demographics?range=${currentRange()}`);
    document.getElementById("c-total").innerText = d.total;
    document.getElementById("c-male").innerText = d.male;
    document.getElementById("c-female").innerText = d.female;
    genderChart.data.datasets[0].data = [d.male, d.female];
    genderChart.update();
    ageChart.data.labels = d.age_labels;
    ageChart.data.datasets[0].data = d.age_values;
    ageChart.update();
}

async function loadCustomers() {
    const rows = await API.get(`/api/customers?range=${currentRange()}`);
    const body = document.getElementById("cust-body");
    body.innerHTML = rows.length ? rows.map(c => `
        <tr style="cursor:pointer" onclick="showDetail(${c.id})">
            <td>#${c.id}</td><td>${c.entry}</td><td>${c.exit}</td>
            <td>${c.dwell}</td><td>${c.zones.join(", ") || "—"}</td>
            <td>${c.gender}</td><td>${c.age}</td><td>${c.visit_count}</td>
        </tr>`).join("")
        : '<tr><td colspan="8" class="muted">No customers yet — run a camera.</td></tr>';
}

async function loadReturning() {
    const d = await API.get(`/api/customers/returning?range=${currentRange()}`);
    document.getElementById("c-returning").innerText = d.count;
    const body = document.getElementById("returning-body");
    body.innerHTML = d.customers.length ? d.customers.map(c => `
        <tr><td>#${c.id}</td><td>${c.visits}</td><td>${c.avg_stay}</td><td>${c.last_seen}</td></tr>`).join("")
        : '<tr><td colspan="4" class="muted">No returning visitors yet.</td></tr>';
}

async function showDetail(id) {
    const d = await API.get(`/api/customers/${id}`);
    const journey = d.journey.length
        ? d.journey.map((z, i) => `${i ? '<span class="journey-arrow">→</span>' : ''}<span class="journey-node">${z}</span>`).join(" ")
        : '<span class="muted">No zone journey recorded.</span>';
    document.getElementById("cust-detail").innerHTML = `
        <div style="margin-bottom:10px;">
            <b>Customer #${d.id}</b> · ${d.gender}, ${d.age} ·
            <span class="muted">${d.visit_count} visit(s)</span>
        </div>
        <div class="muted">First seen ${d.first_seen} · Last seen ${d.last_seen}</div>
        <h3 style="margin:14px 0 8px;font-size:14px;">Journey</h3>
        <div class="journey-timeline">${journey}</div>
        <h3 style="margin:14px 0 8px;font-size:14px;">Zone Dwell</h3>
        ${d.zone_visits.length ? `<table class="data-table"><thead><tr><th>Zone</th><th>Dwell (s)</th><th>Revisit</th></tr></thead>
            <tbody>${d.zone_visits.map(z => `<tr><td>${z.zone}</td><td>${z.dwell}</td><td>${z.revisit}</td></tr>`).join("")}</tbody></table>`
            : '<p class="muted">No zone visits.</p>'}`;
}
window.showDetail = showDetail;

function refresh() {
    loadDemographics();
    loadCustomers();
    loadReturning();
}

window.addEventListener("load", () => {
    initCharts();
    refresh();
    setInterval(refresh, 5000);
    document.addEventListener("retail-state-change", refresh);
});
