import configparser
import datetime

from API.GoogleMapsAPI import GoogleMapsAPI
from helper.ExcelHelper import ExcelHelper


class InternalHelper:

    api_key = None
    googleMapsAPI = None

    def __init__(self):
        self.api_key = self.__get_google_api_key()
        self.googleMapsAPI = GoogleMapsAPI(self.api_key)

    @staticmethod
    def calculate_estimated_price_based_on_service(client_location, preferred_client_destination,
                                                                      type_of_service, vehicle_type):
        price_list_data = ExcelHelper.retrieve_price_list_data()
        if price_list_data is not None and price_list_data[type_of_service] is not None:
            return price_list_data[type_of_service][vehicle_type]
        else:
            return 0

    def retrieve_nearest_drivers(self, drivers_locations, client_location, drivers_basic_data):
        drivers_final_data = drivers_basic_data
        drivers_distance_data = self.googleMapsAPI.retrieve_drivers_distance_data(drivers_locations, client_location)
        [drivers_final_data[index].update(additional_data) for index, additional_data in
         enumerate(drivers_distance_data)]
        drivers_final_data = self.__normalize_values(drivers_final_data)
        drivers_final_data.sort(key=lambda d: d['duration_in_traffic'])
        return drivers_final_data

    @staticmethod
    def input_data_elaborate(request):
        preferred_client_destination = None

        client_location = request.form['originInput']
        service_filter = request.form['filterByService']
        vehicle_type = request.form['filterByVehicleType']
        if request.form['destinationInput']:
            preferred_client_destination = request.form['destinationInput']

        return client_location, preferred_client_destination, service_filter, vehicle_type

    @staticmethod
    def __get_google_api_key():
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['googleAPI']['key']

    @staticmethod
    def __normalize_values(driver_data):
        for data in driver_data:
            data['duration_in_traffic'] = str(datetime.timedelta(seconds=data['duration_in_traffic']))
            data['distance'] = str(int(data['distance']) // 1000) + ' km'
        return driver_data
