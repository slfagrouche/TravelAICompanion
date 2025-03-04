from flask import current_app
from googlemaps import Client

class PlacesService:
    def __init__(self):
        self.client = Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])

    def search_places(self, location, place_type='tourist_attraction', radius=5000):
        """Search for places near a location"""
        try:
            # First, geocode the location to get coordinates
            geocode_result = self.client.geocode(location)
            if not geocode_result:
                return []

            location_coords = geocode_result[0]['geometry']['location']
            
            # Search for places
            places_result = self.client.places_nearby(
                location=(location_coords['lat'], location_coords['lng']),
                radius=radius,
                type=place_type
            )

            return self._format_places(places_result.get('results', []))
        except Exception as e:
            print(f"Error searching places: {e}")
            return []

    def _format_places(self, places):
        """Format place results"""
        formatted_places = []
        for place in places:
            photos = place.get('photos', [])
            photo_reference = photos[0].get('photo_reference') if photos else None
            
            formatted_places.append({
                'id': place.get('place_id'),
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'location': place.get('geometry', {}).get('location'),
                'rating': place.get('rating'),
                'user_ratings_total': place.get('user_ratings_total'),
                'photo_reference': photo_reference,
                'types': place.get('types', []),
                'open_now': place.get('opening_hours', {}).get('open_now')
            })
        return formatted_places

    def get_place_photos(self, photo_reference, max_width=400):
        """Get photo URL for a place"""
        if not photo_reference:
            return None
        
        try:
            photo = self.client.places_photo(
                photo_reference,
                max_width=max_width
            )
            return photo
        except Exception as e:
            print(f"Error getting place photo: {e}")
            return None