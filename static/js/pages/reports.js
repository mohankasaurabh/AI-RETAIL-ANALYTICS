// =====================================================
// Reports & Insights page
// =====================================================

let reportType = "daily";
let footfallChart, genderChart;

document.querySelectorAll("#report-tabs .chip").forEach(chip => {
    chip.addEventListener("click", () => {
        document.querySelectorAll("#report-tabs .chip").forEach(c => c.classList.remove("active"));
        chip.classList.add("active");
        reportType = chip.dataset.type;
        loadSummary();
    });
});

function exportReport(fmt) {
    window.location.href = `/api/reports/${reportType}?fmt=${fmt}`;
}
window.exportReport = exportReport;

function initCharts() {
    footfallChart = new Chart(document.getElementById("reportFootfall"), {
        type: "line",
        data: { labels: [], datasets: [{ data: [], borderColor: "#38bdf8", backgroundColor: "rgba(56,189,248,.15)", fill: true, tension: 0.3 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
            scales: { x: { ticks: { color: "#94a3b8", maxTicksLimit: 8 } }, y: { ticks: { color: "#94a3b8" }, beginAtZero: true } } },
    });
    genderChart = new Chart(document.getElementById("reportGender"), {
        type: "doughnut",
        data: { labels: ["Male", "Female"], datasets: [{ data: [0, 0], backgroundColor: ["#38bdf8", "#f472b6"] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#cbd5e1" } } } },
    });
}

async function loadSummary() {
    const d = await API.get(`/api/reports/summary?type=${reportType}`);
    const s = d.summary;
    document.getElementById("r-entries").innerText = s.total_entries;
    document.getElementById("r-peak").innerText = s.peak_occupancy;
    document.getElementById("r-unique").innerText = s.unique_customers;
    document.getElementById("r-returning").innerText = s.returning_customers;
    document.getElementById("report-window").innerText = `Since ${s.window_start} UTC`;

    footfallChart.data.labels = d.footfall.map(f => f.ts.slice(11, 16));
    footfallChart.data.datasets[0].data = d.footfall.map(f => f.occupancy);
    footfallChart.update();

    genderChart.data.datasets[0].data = [d.demographics.male, d.demographics.female];
    genderChart.update();

    const body = document.getElementById("report-zones");
    body.innerHTML = d.zones.length ? d.zones.map(z => `
        <tr><td>${z.name}</td><td>${z.camera || '—'}</td><td>${z.total_visits}</td>
        <td>${z.unique_visitors}</td><td>${z.avg_dwell}</td><td>${z.revisits}</td></tr>`).join("")
        : '<tr><td colspan="6" class="muted">No zone visits in this window.</td></tr>';
}

window.addEventListener("load", () => {
    initCharts();
    loadSummary();
});
