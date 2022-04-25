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

    def calculate_estimated_price_based_on_service(self, client_location, preferred_client_destination,
                                                   type_of_service, vehicle_type):
        price_service_list_data = ExcelHelper.retrieve_service_list_data()
        price_mile_data = ExcelHelper.retrieve_price_mile_list_data()
        call_out_price = [data for data in price_service_list_data if data['Categories'] == 'Call out'][0][vehicle_type]
        service_price = [data for data in price_service_list_data if data['Categories'] == type_of_service][0][
            vehicle_type]

        total_price = call_out_price + service_price

        if preferred_client_destination is not None:
            distance_driver_client = self.googleMapsAPI.calculate_live_distance(client_location,
                                                                                preferred_client_destination)
            if type_of_service == 'Breakdown Recovery':
                mile_price = [data for data in price_mile_data if data['CategoryType'] == vehicle_type][0]['Price']
                total_price += ((distance_driver_client[0]['distance'] / 1600) * mile_price)

        return round(total_price)

    def retrieve_nearest_drivers(self, drivers_locations, client_location, drivers_basic_data):
        drivers_final_data = drivers_basic_data
        drivers_distance_data = self.googleMapsAPI.calculate_live_distance(drivers_locations, client_location)
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
            data['distance'] = str(int(data['distance']) // 1600) + ' miles'
        return driver_data
