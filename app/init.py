from flask import Flask
from config import Config
from app.utils.db import init_db, close_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialise database (creates DB + tables if not present)
    with app.app_context():
        init_db()

    # Release DB connections at end of each request
    app.teardown_appcontext(close_db)

    # Register blueprints
    from app.routes.patient import patient_bp
    from app.routes.responder import responder_bp
    app.register_blueprint(patient_bp)
    app.register_blueprint(responder_bp)

    return app