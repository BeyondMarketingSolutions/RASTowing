import configparser
import math
from datetime import datetime, timedelta, date


from API.GoogleMapsAPI import GoogleMapsAPI
from helper.ExcelHelper import ExcelHelper
from helper.PaymentHelper import PaymentHelper
from static.Customer import Customer
from static.PriceCategories import PriceCategories
from static.JobData import JobData
from static.Services import Services


class InternalHelper:
    api_key = None
    googleMapsAPI = None
    paymentHelper = None

    def __init__(self):
        self.api_key = self.__get_google_api_key()
        self.googleMapsAPI = GoogleMapsAPI(self.api_key)
        self.paymentHelper = PaymentHelper(InternalHelper.__get_stripe_api_key())

    def calculate_estimated_price_based_on_service(self, job_data):
        call_out_price = ExcelHelper.retrieve_from_price_list_service_data(PriceCategories.CALL_OUT.value)[
            job_data.weight]
        service_price = ExcelHelper.retrieve_from_price_list_service_data(job_data.service)[job_data.weight]
        if job_data.weight is not None \
                and job_data.destination is None \
                and job_data.service in [Services.BREAKDOWN_RECOVERY_SERVICE.value, Services.TOTAL_LIFT_RECOVERY.value]:
            job_data.price_per_mile = ExcelHelper.retrieve_price_mile_by_vehicle_type(job_data.weight)

        total_price = call_out_price + service_price

        if job_data.destination is not None:
            distance_driver_client = self.googleMapsAPI.calculate_live_distance(job_data.origin, job_data.destination)
            job_data.mileage = str(math.ceil(distance_driver_client[0]['distance'] / 1600))
            if job_data.service in [Services.BREAKDOWN_RECOVERY_SERVICE.value, Services.TOTAL_LIFT_RECOVERY.value]:
                mile_price = ExcelHelper.retrieve_price_mile_by_vehicle_type(job_data.weight)
                total_price += ((distance_driver_client[0]['distance'] / 1600) * mile_price)

        total_price += (self.__additional_prices_to_charge(job_data.weight))
        job_data.total_price = math.ceil(total_price)
        job_data.advanced_payment = math.ceil(total_price * 0.3)
        job_data.driver_price = job_data.total_price - job_data.advanced_payment


    def retrieve_nearest_drivers(self, drivers_locations, client_location, drivers_basic_data):
        drivers_final_data = drivers_basic_data
        drivers_distance_data = []
        for paginatedLocations in [drivers_locations[i:i + 25] for i in range(0, len(drivers_locations), 25)]:
            drivers_distance_data.extend(self.googleMapsAPI.calculate_live_distance(paginatedLocations, client_location))
        [drivers_final_data[index].update(additional_data) for index, additional_data in
         enumerate(drivers_distance_data)]
        drivers_final_data = self.__normalize_values(drivers_final_data)
        drivers_final_data.sort(key=lambda d: d['duration_in_traffic'])
        self.normalize_tel_values(drivers_final_data)
        return drivers_final_data

    def send_customer_invoice(self, price, customer, type_of_service):
        return self.paymentHelper.generate_invoice_link(price, customer, type_of_service)

    @staticmethod
    def job_data_elaborate(request):
        preferred_client_destination = None
        origin = request.form['originInput']
        service = Services[request.form['filterByService']].value
        weight = request.form['filterByVehicleType']
        description = request.form['descriptionInput']
        if request.form['destinationInput']:
            preferred_client_destination = request.form['destinationInput']

        job_data = JobData(origin, preferred_client_destination, service, weight, description)
        return job_data

    @staticmethod
    def retrieve_customer_questions(service):
        if service is None:
            service = "Breakdown Recovery"
        with open(f'./static/questions/{service}.txt', 'r', encoding='utf-8') as file_read:
            return [str(data) for data in file_read.readlines()]

    @staticmethod
    def customer_input_data_elaborate(request):
        customer_name = request.form['nameInput']
        customer_email = request.form['emailInput']
        customer_phone = request.form['phoneInput']
        customer = Customer(customer_name, customer_email, customer_phone)
        return customer

    @staticmethod
    def __get_google_api_key():
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['googleAPI']['key']

    @staticmethod
    def __get_stripe_api_key():
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['stripeAPI']['key']

    @staticmethod
    def __normalize_values(driver_data):
        indexes_to_remove = []
        for index, data in enumerate(driver_data):
            if 'duration_in_traffic' and 'distance' in data:
                data['duration_in_traffic'] = str(timedelta(seconds=data['duration_in_traffic']))
                data['distance'] = str(int(data['distance']) // 1600) + ' miles'
            else:
                indexes_to_remove.append(index)
        for index in indexes_to_remove:
            del driver_data[index]
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
    def store_job_data_to_session(drivers_response):
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
            additional_price += ExcelHelper.retrieve_from_price_list_service_data(PriceCategories.NIGHT_RATE.value)[
                vehicle_type]
        if date.today().weekday() > 4:
            additional_price += ExcelHelper.retrieve_from_price_list_service_data(PriceCategories.WEEKEND.value)[
                vehicle_type]
        return additional_price
