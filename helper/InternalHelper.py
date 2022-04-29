import configparser
from datetime import datetime, timedelta, date

from API.GoogleMapsAPI import GoogleMapsAPI
from helper.ExcelHelper import ExcelHelper
from helper.PriceCategories import PriceCategories


class InternalHelper:
    api_key = None
    googleMapsAPI = None

    def __init__(self):
        self.api_key = self.__get_google_api_key()
        self.googleMapsAPI = GoogleMapsAPI(self.api_key)

    def calculate_estimated_price_based_on_service(self, client_location, preferred_client_destination,
                                                   type_of_service, vehicle_type):
        call_out_price = ExcelHelper.retrieve_from_price_list_service_data(PriceCategories.CALL_OUT.name)[vehicle_type]
        service_price = ExcelHelper.retrieve_from_price_list_service_data(type_of_service)[vehicle_type]

        total_price = call_out_price + service_price

        if preferred_client_destination is not None:
            distance_driver_client = self.googleMapsAPI.calculate_live_distance(client_location,
                                                                                preferred_client_destination)
            if type_of_service == 'BREAKDOWN_RECOVERY_SERVICE':
                mile_price = ExcelHelper.retrieve_price_mile_by_vehicle_type(vehicle_type)
                total_price += ((distance_driver_client[0]['distance'] / 1600) * mile_price)

        total_price += self.__additional_prices_to_charge(vehicle_type)

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
            data['duration_in_traffic'] = str(timedelta(seconds=data['duration_in_traffic']))
            data['distance'] = str(int(data['distance']) // 1600) + ' miles'
        return driver_data

    @staticmethod
    def normalize_tel_values(drivers_response):
        for driver_data in drivers_response:
            if '/' in driver_data['Tel']:
                driver_data['Tel'] = driver_data['Tel'].split('/')
            else:
                driver_data['Tel'] = [driver_data['Tel']]
        return drivers_response

    @staticmethod
    def __additional_prices_to_charge(vehicle_type):
        additional_price = 0
        timestamp = datetime.now()
        if timestamp.hour > 18 or timestamp.hour < 6:
            additional_price += ExcelHelper.retrieve_from_price_list_service_data(PriceCategories.NIGHT_RATE.name)[vehicle_type]
        if date.today().weekday() > 4:
            additional_price += ExcelHelper.retrieve_from_price_list_service_data(PriceCategories.WEEKEND.name)[vehicle_type]
        return additional_price
