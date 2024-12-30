from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialisering
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    # Registrer ruter
    from app.routes.auth import auth_bp
    from app.routes.rsvp import rsvp_bp
    from app.routes.gallery import gallery_bp
    from app.routes.info import info_bp
    from app.routes.faq import faq_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(rsvp_bp)
    app.register_blueprint(gallery_bp)
    app.register_blueprint(info_bp)
    app.register_blueprint(faq_bp)

    return app
