from flask import Blueprint, render_template, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', 
                         api_key=current_app.config['GOOGLE_MAPS_API_KEY'])

@main_bp.route('/planner')
def planner():
    """Render the trip planner page"""
    return render_template('planner.html',
                         api_key=current_app.config['GOOGLE_MAPS_API_KEY'])