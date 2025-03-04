from flask import Blueprint, jsonify, request, current_app
from flask_mail import Message
import logging
from datetime import datetime
import openai
from typing import Dict, Optional
from firebase_admin import firestore
import markdown  # For converting markdown to HTML
from dotenv import load_dotenv
import os

load_dotenv()

api_bp = Blueprint('api', __name__)

# DeepSeek API configuration
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

class GoogleMapsService:
    def get_place_details(self, place_id):
        try:
            details = current_app.gmaps.place(place_id=place_id)
            return details.get('result', {})
        except Exception as e:
            current_app.logger.error(f"Error fetching place details: {e}")
            return {}

    def get_route(self, origin, destination, waypoints=None, mode='walking'):
        try:
            route = current_app.gmaps.directions(
                origin,
                destination,
                waypoints=waypoints,
                optimize_waypoints=True,
                mode=mode
            )
            if route:
                return {
                    'total_distance': route[0]['legs'][0]['distance']['text'],
                    'total_duration': route[0]['legs'][0]['duration']['text'],
                    'steps': route[0]['legs'][0]['steps'],
                    'polyline': route[0]['overview_polyline']['points']
                }
            return {}
        except Exception as e:
            current_app.logger.error(f"Error getting route: {e}")
            return {}

class PlacesService:
    def search_places(self, location, place_type, radius=5000):
        try:
            geocode_result = current_app.gmaps.geocode(location)
            if not geocode_result:
                return []
            coords = geocode_result[0]['geometry']['location']
            places_result = current_app.gmaps.places_nearby(
                location=(coords['lat'], coords['lng']),
                radius=radius,
                type=place_type
            )
            places = places_result.get('results', [])
            enhanced_places = []
            for place in places:
                # Fetch additional details for descriptions and photos
                details = current_app.maps_service.get_place_details(place.get('place_id'))
                photo_url = None
                if details.get('photos'):
                    photo_ref = details['photos'][0]['photo_reference']
                    photo_url = (
                        f"https://maps.googleapis.com/maps/api/place/photo"
                        f"?maxwidth=400&photoreference={photo_ref}&key={current_app.config['GOOGLE_MAPS_API_KEY']}"
                    )
                description = details.get('editorial_summary', {}).get('overview', 'No description available.')
                enhanced_places.append({
                    'name': place.get('name'),
                    'address': place.get('vicinity'),
                    'location': place.get('geometry', {}).get('location'),
                    'rating': place.get('rating'),
                    'place_id': place.get('place_id'),
                    'types': place.get('types', []),
                    'photo': photo_url,
                    'description': description
                })
            return enhanced_places
        except Exception as e:
            current_app.logger.error(f"Error searching places: {e}")
            return []
        

def generate_travel_guide(
    destination: str = "Your Destination",
    start_date: str = "Not specified",
    end_date: str = "Not specified",
    travelers: int = 1,
    budget: str = "Moderate",
    interests: str = "General sightseeing",
    email: Optional[str] = None,
    special_requests: str = "None"
) -> Dict[str, any]:
    try:
        if not destination or not travelers or not budget:
            return {
                "success": False,
                "message": "Missing required fields: destination, travelers, or budget.",
                "data": {}
            }

        number_of_days = "Not specified"
        if start_date != "Not specified" and end_date != "Not specified":
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                if end > start:
                    number_of_days = (end - start).days + 1
                else:
                    raise ValueError("End date must be after start date")
            except ValueError as e:
                number_of_days = f"Invalid date range: {str(e)}"

        prompt = (
            f"Hi! I’m excited to help you plan your {number_of_days}-day trip to {destination} "
            f"for {travelers} travelers, from {start_date} to {end_date}. You’re working with a {budget} budget "
            f"and enjoy {interests}. You also mentioned {special_requests if special_requests != 'None' else 'wanting a great experience'}.\n\n"
            f"Create a detailed day-by-day itinerary with exact places to visit, where to eat, and fun activities. "
            f"Add practical advice—how to get around, costs to expect, and things to watch out for (like safety, scams, or weather). "
            f"Make it thorough for an email, covering everything needed for an amazing trip. "
            f"If anything’s missing, add awesome suggestions matching the interests!"
        )

        try:
            client = openai.OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
            current_app.logger.info(f"Attempting DeepSeek API call with prompt: {prompt[:100]}...")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                stream=False
            )
            itinerary = response.choices[0].message.content
            current_app.logger.info("DeepSeek API call succeeded")
        except Exception as api_error:
            current_app.logger.error(f"DeepSeek API error: {str(api_error)}")
            itinerary = (
                f"Here's a generic itinerary for your trip to {destination}:\n\n"
                f"For {number_of_days} days, we recommend exploring local landmarks, "
                f"enjoying regional cuisine, and relaxing at popular spots."
            )

        travel_guide_data = {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "number_of_days": number_of_days,
            "travelers": travelers,
            "budget": budget,
            "interests": interests,
            "special_requests": special_requests,
            "itinerary": itinerary,  # Raw markdown from DeepSeek
            "email": email,
            "generated_at": datetime.now().isoformat()
        }

        if email:
            try:
                db = firestore.client()
                db.collection('travel_guides').add({
                    **travel_guide_data,
                    "user_id": "anonymous",
                    "generated_at": firestore.SERVER_TIMESTAMP
                })
                current_app.logger.info(f"Travel guide logged to Firestore for {email}")
            except Exception as e:
                current_app.logger.error(f"Firestore error: {str(e)}")

        return {
            "success": True,
            "message": "Travel guide generated successfully!",
            "data": travel_guide_data
        }

    except Exception as e:
        current_app.logger.error(f"Error generating travel guide: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Failed to generate travel guide: {str(e)}",
            "data": {}
        }

@api_bp.before_request
def initialize_services():
    if not hasattr(current_app, 'maps_service'):
        current_app.maps_service = GoogleMapsService()
    if not hasattr(current_app, 'places_service'):
        current_app.places_service = PlacesService()

@api_bp.route('/search_places')
def search_places():
    location = request.args.get('location')
    place_type = request.args.get('type', 'tourist_attraction')
    radius = request.args.get('radius', 5000, type=int)

    if not location:
        return jsonify({'error': 'Location is required'}), 400

    places = current_app.places_service.search_places(
        location=location,
        place_type=place_type,
        radius=radius
    )
    
    current_app.logger.info(f"Found {len(places)} places for location: {location}")
    return jsonify({
        'places': places,
        'count': len(places)
    })

@api_bp.route('/place/<place_id>')
def get_place_details(place_id):
    details = current_app.maps_service.get_place_details(place_id)
    if not details:
        current_app.logger.warning(f"Place not found: {place_id}")
        return jsonify({'error': 'Place not found'}), 404
    return jsonify(details)

@api_bp.route('/generate-travel-guide', methods=['POST'])
def create_travel_guide():
    try:
        data = request.get_json()
        current_app.logger.info(f'Received travel guide request: {data}')

        guide = generate_travel_guide(
            destination=data.get('destination', 'Your Destination'),
            start_date=data.get('start_date', 'Not specified'),
            end_date=data.get('end_date', 'Not specified'),
            travelers=int(data.get('travelers', 1)),
            budget=data.get('budget', 'Moderate'),
            interests=data.get('interests', 'General sightseeing'),
            email=data.get('email'),
            special_requests=data.get('special_requests', 'None')
        )
        
        if guide['success']:
            current_app.logger.info(f'Travel guide generated successfully for {data["destination"]}')
            msg = Message(
                subject=f"Your Travel Itinerary for {guide['data']['destination']}",
                sender=("Travel Guide", current_app.config['MAIL_DEFAULT_SENDER']),
                recipients=[guide['data']['email']]
            )
            # Convert markdown itinerary to HTML
            itinerary_html = markdown.markdown(guide['data']['itinerary'])
            # Define HTML email body with CSS styling
            msg.html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    h1 {{ color: #2c3e50; font-size: 24px; }}
                    h2 {{ color: #2980b9; font-size: 20px; }}
                    h3 {{ color: #3498db; font-size: 18px; }}
                    strong {{ font-weight: bold; }}
                    em {{ font-style: italic; }}
                    ul {{ margin-left: 20px; }}
                    .section {{ margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <h1>Hello!</h1>
                <p>Here's your personalized travel guide for {guide['data']['destination']}!</p>

                <div class="section">
                    <h2>Trip Details</h2>
                    <ul>
                        <li><strong>Destination:</strong> {guide['data']['destination']}</li>
                        <li><strong>Dates:</strong> {guide['data']['start_date']} to {guide['data']['end_date']}</li>
                        <li><strong>Duration:</strong> {guide['data']['number_of_days']} days</li>
                        <li><strong>Travelers:</strong> {guide['data']['travelers']}</li>
                        <li><strong>Budget:</strong> {guide['data']['budget']}</li>
                        <li><strong>Interests:</strong> {guide['data']['interests']}</li>
                        <li><strong>Special Requests:</strong> {guide['data']['special_requests']}</li>
                    </ul>
                </div>

                <div class="section">
                    <h2>Your Itinerary</h2>
                    {itinerary_html}
                </div>

                <p>Have a great trip!</p>
                <p><strong>Best regards,</strong><br>Your Travel Guide Team</p>
            </body>
            </html>
            """
            current_app.logger.debug(f'Sending HTML email to {guide["data"]["email"]}')
            current_app.extensions['mail'].send(msg)
            current_app.logger.info(f'Email sent successfully to {guide["data"]["email"]}')
            return jsonify(guide), 200
        else:
            current_app.logger.warning(f'Travel guide generation failed: {guide}')
            return jsonify(guide), 400
            
    except Exception as e:
        current_app.logger.error(f"Error in create_travel_guide: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error generating travel guide: {str(e)}',
            'data': {}
        }), 500

@api_bp.route('/route')
def get_route():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    waypoints = request.args.getlist('waypoints')
    mode = request.args.get('mode', 'walking')

    if not origin or not destination:
        return jsonify({'error': 'Origin and destination are required'}), 400

    route = current_app.maps_service.get_route(
        origin=origin,
        destination=destination,
        waypoints=waypoints,
        mode=mode
    )

    if not route:
        current_app.logger.warning(f"Could not find route from {origin} to {destination}")
        return jsonify({'error': 'Could not find route'}), 404

    return jsonify(route)