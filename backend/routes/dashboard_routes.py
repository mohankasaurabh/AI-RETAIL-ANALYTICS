from flask import Blueprint
from flask import render_template


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/")
def dashboard():

    return render_template(
        "dashboard.html"
    )