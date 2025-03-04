from flask import Flask, render_template, request, jsonify
from googlemaps import Client
from google.cloud import translate_v2 as translate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='app/templates')

# Configure Google Maps API
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
gmaps = Client(key=GOOGLE_MAPS_API_KEY)

# Initialize Google Cloud Translation API
translate_client = translate.Client()

# Define the TravelGuide class
class TravelGuide:
    def __init__(self, gmaps_client):
        self.gmaps = gmaps_client
    
    def search_places(self, location, place_type, radius=5000):
        """Search for places near a location"""
        try:
            # First, geocode the location to get coordinates
            geocode_result = self.gmaps.geocode(location)
            if not geocode_result:
                return []
            
            location_coords = geocode_result[0]['geometry']['location']
            
            # Search for places
            places_result = self.gmaps.places_nearby(
                location=(location_coords['lat'], location_coords['lng']),
                radius=radius,
                type=place_type
            )
            
            return self._format_places(places_result.get('results', []))
        except Exception as e:
            print(f"Error searching places: {e}")
            return []
    
    def _format_places(self, places):
        """
        Format place results and fetch editorial summaries and photos from Place Details.
        """
        formatted_places = []
        for place in places:
            place_id = place.get('place_id')
            
            # Default description and photo
            description = "No description available."
            photo_url = None
            
            # Make a "place details" call to get editorial summary and photos
            if place_id:
                try:
                    details_result = self.gmaps.place(place_id=place_id)
                    details = details_result.get('result', {})
                    
                    # Get description
                    editorial_summary = details.get('editorial_summary', {})
                    description = editorial_summary.get('overview', "No description available.")
                    
                    # Get the first photo (if available)
                    photos = details.get('photos', [])
                    if photos:
                        photo_reference = photos[0].get('photo_reference')
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_MAPS_API_KEY}"
                except Exception as e:
                    print(f"Could not get details for place_id={place_id}: {e}")
            
            formatted_places.append({
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'location': place.get('geometry', {}).get('location'),
                'rating': place.get('rating'),
                'place_id': place_id,
                'types': place.get('types', []),
                'description': description,
                'photo': photo_url  # Add photo URL to the response
            })
        return formatted_places
    
    def get_route(self, origin, destination, waypoints=None):
        """Get route between points"""
        try:
            route = self.gmaps.directions(
                origin,
                destination,
                waypoints=waypoints,
                optimize_waypoints=True,
                mode="walking"
            )
            
            if route:
                return self._format_route(route[0])
            return None
        except Exception as e:
            print(f"Error getting route: {e}")
            return None
    
    def _format_route(self, route):
        """Format route information"""
        legs = route.get('legs', [])
        steps = []
        total_distance = 0
        total_duration = 0

        for leg in legs:
            total_distance += leg.get('distance', {}).get('value', 0)
            total_duration += leg.get('duration', {}).get('value', 0)
            steps.extend(leg.get('steps', []))

        return {
            'total_distance': f"{total_distance / 1000:.1f} km",
            'total_duration': f"{total_duration / 60:.0f} mins",
            'steps': steps,
            'polyline': route.get('overview_polyline', {}).get('points')
        }

# Initialize TravelGuide
travel_guide = TravelGuide(gmaps)

# HTML template for the main page
@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

@app.route('/search_places')
def search_places():
    """API endpoint to search for places"""
    location = request.args.get('location')
    place_type = request.args.get('type', 'tourist_attraction')
    
    if not location:
        return jsonify({'error': 'Location is required'}), 400
        
    places = travel_guide.search_places(location, place_type)
    return jsonify({'places': places})

@app.route('/get_route')
def get_route():
    """API endpoint to get a route"""
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    waypoints = request.args.getlist('waypoints')
    
    if not origin or not destination:
        return jsonify({'error': 'Origin and destination are required'}), 400
        
    route = travel_guide.get_route(origin, destination, waypoints)
    return jsonify(route)

@app.route('/translate')
def translate_text():
    """API endpoint to translate text"""
    text = request.args.get('text')
    target_lang = request.args.get('target_lang', 'en')  # Default to English
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    try:
        translated = translate_client.translate(text, target_language=target_lang)
        return jsonify({'translated_text': translated['translatedText']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)