// =====================================================
// Shared Socket.IO client
// =====================================================
// Connects to the Flask-SocketIO server, applies live KPI
// metrics to any matching DOM elements on the page, and
// re-broadcasts "metrics" / "chart" payloads as DOM
// CustomEvents so page-specific scripts (charts.js) can
// react without each opening their own socket.
//
// Falls back silently if Socket.IO is unavailable — the
// per-page polling (dashboard.js / charts.js) keeps the UI
// alive in that case.
// =====================================================

(function () {

    // safe DOM setter (does not collide with dashboard.js setValue)
    function wsSet(id, value) {
        const el = document.getElementById(id);
        if (el && value !== undefined && value !== null) {
            el.innerText = value;
        }
    }

    function applyQueueBadge(id, status) {
        const el = document.getElementById(id);
        if (!el) return;
        el.innerText = status;
        if (el.classList.contains("badge")) {
            el.classList.remove("low", "medium", "high");
            el.classList.add((status || "low").toLowerCase());
        }
    }

    // Apply a full metrics payload to all known KPI elements
    window.applyRetailMetrics = function (data) {
        if (!data) return;

        wsSet("occupancy", data.occupancy);
        wsSet("entries", data.entries);
        wsSet("exits", data.exits);
        wsSet("active_customers", data.active_customers);
        wsSet("zone_occupancy", data.zone_occupancy);
        wsSet("total_tracks", data.total_tracks);
        wsSet("reid_identities", data.reid_identities);
        wsSet("male_count", data.male_count);
        wsSet("female_count", data.female_count);
        wsSet("journey_customers", data.journey_customers);
        wsSet("queue_length", data.queue_length);
        wsSet("average_wait", `${data.average_wait}s`);
        wsSet("cross_camera_customers", data.cross_camera_customers);
        wsSet("multi_camera_customers", data.multi_camera_customers);

        // queue status (plain + badge variants)
        applyQueueBadge("queue_status", data.queue_status);

        // dashboard duplicate display ids
        wsSet("queue_length_display", data.queue_length);
        wsSet("average_wait_display", `${data.average_wait}s`);
        wsSet("queue_status_display", data.queue_status);
    };

    if (typeof io === "undefined") {
        console.warn("[WS] Socket.IO not loaded — using polling fallback.");
        return;
    }

    const socket = io();
    window.retailSocket = socket;

    socket.on("connect", function () {
        console.log("[WS] connected:", socket.id);
        const ind = document.getElementById("live-indicator");
        if (ind) ind.style.opacity = "1";
    });

    socket.on("disconnect", function () {
        console.warn("[WS] disconnected");
        const ind = document.getElementById("live-indicator");
        if (ind) ind.style.opacity = "0.4";
    });

    socket.on("metrics", function (data) {
        window.applyRetailMetrics(data);
        document.dispatchEvent(
            new CustomEvent("retail-metrics", { detail: data })
        );
    });

    socket.on("chart", function (data) {
        document.dispatchEvent(
            new CustomEvent("retail-chart", { detail: data })
        );
    });

})();
