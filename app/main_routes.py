from flask import Blueprint, render_template
from app.config import Config

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Render the main page"""
    return render_template('index.html', api_key=Config.GOOGLE_MAPS_API_KEY)
    