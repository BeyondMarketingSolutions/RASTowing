import googlemaps
from datetime import datetime


class GoogleMapsAPI:
    'Common base class for all employees'
    gmaps = None

    def __init__(self, key):
        self.gmaps = googlemaps.Client(key=key)

    def retrieve_drivers_distance_data(self, drivers_locations, client_locations):
        response = self.gmaps.distance_matrix(origins=drivers_locations, destinations=client_locations,
                                              mode="driving", departure_time=datetime.now())['rows']
        return [dict((key, (data['elements'][0])[key]['value'])
                                for key in ['duration_in_traffic', 'distance']
                                if key in data['elements'][0])
                           for data in response]
