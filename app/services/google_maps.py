from googlemaps import Client
from datetime import datetime
from flask import current_app

class GoogleMapsService:
    def __init__(self):
        self.client = Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])

    def get_place_details(self, place_id):
        """Get detailed information about a specific place"""
        try:
            result = self.client.place(place_id, fields=[
                'name', 'rating', 'formatted_address', 'photo', 
                'opening_hours', 'price_level', 'review'
            ])
            return result.get('result')
        except Exception as e:
            print(f"Error getting place details: {e}")
            return None

    def get_route(self, origin, destination, waypoints=None, mode="walking"):
        """Get route between two points with optional waypoints"""
        try:
            route = self.client.directions(
                origin,
                destination,
                mode=mode,
                waypoints=waypoints,
                optimize_waypoints=True,
                departure_time=datetime.now()
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
            'polyline': route.get('overview_polyline', {}).get('points'),
            'bounds': route.get('bounds')
        }