from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.utils.db import init_db, close_db

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Render sits behind a reverse proxy - trust its X-Forwarded-* headers
    # so request.host_url, url_for(_external=True), and client IPs
    # (used by rate limiting and access_logs) are correct.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Initialise server-side Redis sessions
    Session(app)

    # Initialise CSRF protection
    csrf.init_app(app)

    # Initialise rate limiter (uses Redis storage from config)
    limiter.init_app(app)

    # Initialise database (creates DB + tables if not present)
    with app.app_context():
        init_db()

    # Release DB connections at end of each request
    app.teardown_appcontext(close_db)

    # Register routes and blueprints
    from app.routes.patient   import patient_bp
    from app.routes.responder import responder_bp
    from app.routes.main      import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(responder_bp)

    # --- Custom error handlers ---
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        """Return a friendly page when rate-limited instead of raw 429."""
        return render_template("responder/scan.html", found=False), 429

    return app
