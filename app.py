from flask import Flask

from backend.routes.dashboard_routes import (
    dashboard_bp
)

from backend.routes.stream_routes import (
    stream_bp
)

from backend.routes.analytics_routes import (
    analytics_bp
)

from backend.routes.api_routes import (
    api_bp
)
from backend.routes.report_routes import (
    report_bp
)

def create_app():

    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(dashboard_bp)

    app.register_blueprint(stream_bp)

    app.register_blueprint(analytics_bp)

    app.register_blueprint(api_bp)

    app.register_blueprint(report_bp)

    return app