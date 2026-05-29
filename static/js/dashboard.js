// =====================================
// DASHBOARD DATA REFRESH
// =====================================

async function loadAnalytics() {

    try {

        const response = await fetch(
            "/analytics"
        )

        const data = await response.json()

        // ==========================
        // KPI CARDS
        // ==========================

        setValue(
            "occupancy",
            data.occupancy
        )

        setValue(
            "entries",
            data.entries
        )

        setValue(
            "exits",
            data.exits
        )

        setValue(
            "active_customers",
            data.active_customers
        )

        setValue(
            "zone_occupancy",
            data.zone_occupancy
        )

        setValue(
            "total_tracks",
            data.total_tracks
        )

        setValue(
            "reid_identities",
            data.reid_identities
        )

        setValue(
            "male_count",
            data.male_count
        )

        setValue(
            "female_count",
            data.female_count
        )

        setValue(
            "journey_customers",
            data.journey_customers
        )

        setValue(
            "queue_length",
            data.queue_length
        )

        setValue(
            "average_wait",
            `${data.average_wait}s`
        )

        setValue(
            "queue_status",
            data.queue_status
        )

        // ==========================
        // QUEUE PANEL
        // ==========================

        setValue(
            "queue_length_display",
            data.queue_length
        )

        setValue(
            "average_wait_display",
            `${data.average_wait}s`
        )

        setValue(
            "queue_status_display",
            data.queue_status
        )

        // ==========================
        // ZONE PANEL
        // ==========================

        updateZonePanel(
            data.zone_data || {}
        )

    }
    catch (error) {

        console.error(
            "Analytics error:",
            error
        )
    }
}


// =====================================
// SAFE DOM UPDATE
// =====================================

function setValue(
    id,
    value
) {

    const element =
        document.getElementById(id)

    if (element) {

        element.innerText = value
    }
}


// =====================================
// ZONE PANEL
// =====================================

function updateZonePanel(
    zoneData
) {

    const container =
        document.getElementById(
            "zone-container"
        )

    if (!container) return

    let html = ""

    for (
        const zone in zoneData
    ) {

        html += `
            <div class="analytics-item">
                ${zone} :
                ${zoneData[zone]}
            </div>
        `
    }

    if (
        html.trim() === ""
    ) {

        html =
            "No Zone Data Available"
    }

    container.innerHTML = html
}


// =====================================
// CAMERA SWITCH
// =====================================

async function changeCamera() {

    const camera =

        document.getElementById(
            "camera-select"
        ).value

    try {

        await fetch(

            `/switch_camera?camera=${camera}`
        )

        console.log(
            "Camera switched:",
            camera
        )

    }
    catch (error) {

        console.error(error)
    }
}


// =====================================
// RTSP CONNECT
// =====================================

async function connectRTSP() {

    const rtspUrl =

        document.getElementById(
            "rtsp_url"
        ).value

    if (!rtspUrl) {

        alert(
            "Please enter RTSP URL"
        )

        return
    }

    try {

        const response = await fetch(

            "/connect_rtsp",

            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    rtsp_url:
                        rtspUrl
                })
            }
        )

        const result =
            await response.json()

        console.log(result)

        alert(
            "RTSP Connected"
        )

    }
    catch (error) {

        console.error(error)

        alert(
            "RTSP Connection Failed"
        )
    }
}


// =====================================
// PAUSE STREAM
// =====================================

async function pauseStream() {

    try {

        await fetch(
            "/pause_stream"
        )

    }
    catch (error) {

        console.error(error)
    }
}


// =====================================
// PLAY STREAM
// =====================================

async function playStream() {

    try {

        await fetch(
            "/play_stream"
        )

    }
    catch (error) {

        console.error(error)
    }
}


// =====================================
// RESTART STREAM
// =====================================

async function restartStream() {

    try {

        await fetch(
            "/restart_stream"
        )

        const img =

            document.getElementById(
                "video-stream"
            )

        if (img) {

            img.src =
                "/video_feed?t=" +
                new Date().getTime()
        }

    }
    catch (error) {

        console.error(error)
    }
}


// =====================================
// LIVE ANALYTICS CHART
// =====================================

const occupancyChartCtx =

    document.getElementById(
        "occupancyChart"
    )

let occupancyChart = null

if (occupancyChartCtx) {

    occupancyChart =
        new Chart(

            occupancyChartCtx,

            {

                type: "line",

                data: {

                    labels: [],

                    datasets: [

                        {

                            label:
                                "Occupancy",

                            data: [],

                            borderWidth: 2
                        }
                    ]
                },

                options: {

                    responsive: true
                }
            }
        )
}


// =====================================
// HISTORICAL CHART
// =====================================

const historicalChartCtx =

    document.getElementById(
        "historicalChart"
    )

let historicalChart = null

if (historicalChartCtx) {

    historicalChart =
        new Chart(

            historicalChartCtx,

            {

                type: "line",

                data: {

                    labels: [],

                    datasets: [

                        {

                            label:
                                "Historical Occupancy",

                            data: [],

                            borderWidth: 2
                        }
                    ]
                },

                options: {

                    responsive: true
                }
            }
        )
}


// =====================================
// LOAD CHART DATA
// =====================================

async function loadChartData() {

    try {

        const response = await fetch(
            "/chart_data"
        )

        const data =
            await response.json()

        if (
            occupancyChart
        ) {

            occupancyChart.data.labels =
                data.timestamps

            occupancyChart.data.datasets[0].data =
                data.occupancy

            occupancyChart.update()
        }

        if (
            historicalChart
        ) {

            historicalChart.data.labels =
                data.timestamps

            historicalChart.data.datasets[0].data =
                data.occupancy

            historicalChart.update()
        }

    }
    catch (error) {

        console.error(
            "Chart error:",
            error
        )
    }
}


// =====================================
// AUTO REFRESH
// =====================================

loadAnalytics()

loadChartData()

setInterval(
    loadAnalytics,
    2000
)

setInterval(
    loadChartData,
    5000
)


setValue(
    "cross_camera_customers",
    data.cross_camera_customers
)

setValue(
    "multi_camera_customers",
    data.multi_camera_customers
)