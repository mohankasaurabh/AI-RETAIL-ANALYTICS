"""
=====================================================
Page Routes (server-rendered HTML)
=====================================================

Serves every page in the 8-module SaaS shell. JSON/data
endpoints live in analytics_routes / api_routes / source_routes;
page paths here are chosen to avoid colliding with those.

page_title / page_subtitle are passed from here so the shared
topbar (included by base.html before the child content block
renders) shows the correct heading.

Modules not yet rebuilt on base.html render a styled placeholder
(replaced in their respective phases).
"""

from flask import Blueprint, render_template


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    return render_template(
        "dashboard.html", active_page="dashboard",
        page_title="Executive Dashboard",
        page_subtitle="Real-Time AI Retail Analytics",
    )


@dashboard_bp.route("/sources")
def sources():
    return render_template(
        "sources.html", active_page="sources",
        page_title="Camera & Media Sources",
        page_subtitle="Manage CCTV / RTSP / IP / webcam / video sources",
    )


@dashboard_bp.route("/live")
def live_stream():
    return render_template(
        "live_stream.html", active_page="live",
        page_title="Live Monitoring",
        page_subtitle="Per-camera live AI pipeline",
    )


@dashboard_bp.route("/zones")
def zones():
    return render_template(
        "zones.html", active_page="zones",
        page_title="Zone Analytics",
        page_subtitle="Draw zones · dwell · journeys",
    )


@dashboard_bp.route("/heatmaps")
def heatmaps():
    return render_template(
        "heatmaps.html", active_page="heatmaps",
        page_title="Heatmap Analytics",
        page_subtitle="Live & historical movement density",
    )


@dashboard_bp.route("/customers")
def customers():
    return render_template(
        "customers.html", active_page="customers",
        page_title="Customer Analytics",
        page_subtitle="Demographics · journeys · returning visitors",
    )


@dashboard_bp.route("/reports")
def reports():
    return render_template(
        "reports.html", active_page="reports",
        page_title="Reports & Insights",
        page_subtitle="Daily / weekly / monthly exports",
    )


@dashboard_bp.route("/settings")
def settings():
    return render_template(
        "settings.html", active_page="settings",
        page_title="Settings",
        page_subtitle="AI engine · database · cameras · alerts",
    )


# =====================================
# LEGACY (kept for back-compat)
# =====================================

@dashboard_bp.route("/insights")
def insights():
    return render_template("analytics.html", active_page="customers")


@dashboard_bp.route("/welcome")
def welcome():
    return render_template("index.html", active_page="welcome")
