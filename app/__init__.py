from flask import Flask
from flask_mail import Mail
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from app.config import Config
import logging
from googlemaps import Client

mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    app.logger.info("Starting Flask application")

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate("travel-guide-2bc2a-firebase-adminsdk-fbsvc-7e677ebf7d.json")
            firebase_admin.initialize_app(cred)
            app.logger.info("Firebase initialized successfully")
        except Exception as e:
            app.logger.error(f"Failed to initialize Firebase: {str(e)}")

    mail.init_app(app)

    with app.app_context():
        app.gmaps = Client(key=app.config.get('GOOGLE_MAPS_API_KEY'))

    from app.routes.main_routes import main_bp
    from app.routes.api_routes import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app