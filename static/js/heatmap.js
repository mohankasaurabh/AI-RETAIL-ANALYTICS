// =====================================================
// Heatmap Page Renderer
// =====================================================
// Renders movement-density heatmaps from /api/heatmap_data
// (MovementLog x/y points) onto canvases:
//   - live-heat : overlay sized to the live video frame
//   - hist-heat : standalone historical density map
// Plus a zone-concentration breakdown from /api/zone_ranking.
//
// Intensity is accumulated in "lighter" blend mode, then
// remapped through a blue→green→yellow→red ramp.
// =====================================================

// blue -> green -> yellow -> red ramp
function heatColor(t) {
    t = Math.max(0, Math.min(1, t));
    const stops = [
        [37, 99, 235],   // blue
        [34, 197, 94],   // green
        [234, 179, 8],   // yellow
        [239, 68, 68]    // red
    ];
    const seg = t * (stops.length - 1);
    const i = Math.floor(seg);
    const f = seg - i;
    const a = stops[i];
    const b = stops[Math.min(i + 1, stops.length - 1)];
    return [
        Math.round(a[0] + (b[0] - a[0]) * f),
        Math.round(a[1] + (b[1] - a[1]) * f),
        Math.round(a[2] + (b[2] - a[2]) * f)
    ];
}

function renderHeatmap(canvas, points) {
    if (!canvas) return;

    // size canvas to its rendered box
    const w = canvas.clientWidth || canvas.parentElement.clientWidth || 640;
    const h = canvas.clientHeight ||
              Math.round(w * 9 / 16) ||
              360;
    canvas.width = w;
    canvas.height = h;

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, w, h);

    if (!points || !points.length) return;

    // derive source bounds so points scale into the canvas
    let maxX = 0, maxY = 0;
    for (const p of points) {
        if (p.x > maxX) maxX = p.x;
        if (p.y > maxY) maxY = p.y;
    }
    maxX = maxX || w;
    maxY = maxY || h;

    // 1) accumulate intensity in grayscale
    ctx.globalCompositeOperation = "lighter";
    const radius = Math.max(14, w * 0.03);
    for (const p of points) {
        const x = (p.x / maxX) * w;
        const y = (p.y / maxY) * h;
        const grad = ctx.createRadialGradient(x, y, 0, x, y, radius);
        grad.addColorStop(0, "rgba(255,255,255,0.30)");
        grad.addColorStop(1, "rgba(255,255,255,0)");
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
    }
    ctx.globalCompositeOperation = "source-over";

    // 2) remap intensity -> heat color ramp
    const img = ctx.getImageData(0, 0, w, h);
    const data = img.data;
    for (let i = 0; i < data.length; i += 4) {
        const intensity = data[i]; // grayscale value 0..255
        if (intensity === 0) continue;
        const t = Math.min(1, intensity / 200);
        const [r, g, b] = heatColor(t);
        data[i] = r;
        data[i + 1] = g;
        data[i + 2] = b;
        data[i + 3] = Math.min(220, intensity + 40);
    }
    ctx.putImageData(img, 0, 0);
}

async function fetchPoints() {
    try {
        const d = await (await fetch("/api/heatmap_data")).json();
        return d.points || [];
    } catch (e) {
        console.error(e);
        return [];
    }
}

async function loadLiveHeatmap() {
    const canvas = document.getElementById("live-heat");
    const base = document.getElementById("live-base");
    if (canvas && base) {
        // match overlay to the displayed video size
        canvas.style.height = base.clientHeight + "px";
    }
    const points = await fetchPoints();
    renderHeatmap(canvas, points);
}

async function loadHistoricalHeatmap() {
    const points = await fetchPoints();
    renderHeatmap(document.getElementById("hist-heat"), points);
    const c = document.getElementById("hist-count");
    if (c) c.innerText = points.length + " points";
}

async function loadZoneConcentration() {
    const box = document.getElementById("zone-concentration");
    if (!box) return;
    try {
        const d = await (await fetch("/api/zone_ranking")).json();
        const zones = d.zones || [];
        if (!zones.length) {
            box.innerHTML = '<p class="muted">No zone data yet.</p>';
            return;
        }
        const max = Math.max(1, ...zones.map(z => z.count));
        box.innerHTML = zones.map(z => {
            const pct = (z.count / max) * 100;
            const [r, g, b] = heatColor(z.count / max);
            return `
                <div class="zone-bar">
                    <div class="label"><span>${z.zone}</span><span>${z.count}</span></div>
                    <div class="track"><div class="fill"
                        style="width:${pct}%;background:rgb(${r},${g},${b})"></div></div>
                </div>`;
        }).join("");
    } catch (e) { console.error(e); }
}

function refreshHeatmaps() {
    loadLiveHeatmap();
    loadHistoricalHeatmap();
    loadZoneConcentration();
}

window.loadHistoricalHeatmap = loadHistoricalHeatmap;

window.addEventListener("load", refreshHeatmaps);
setInterval(loadLiveHeatmap, 2000);
setInterval(loadZoneConcentration, 4000);
