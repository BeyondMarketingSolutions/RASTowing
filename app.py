import pandas

from flask import Flask, render_template, request
from helper.InternalHelper import InternalHelper
from helper.ExcelHelper import ExcelHelper

app = Flask(__name__)


@app.route('/')
def towing_dashboard():
    return render_template('main.html')


@app.route('/', methods=['POST'])
def render_results():
    client_location, preferred_client_destination, service_filter, vehicle_type = InternalHelper.input_data_elaborate(
        request)
    drivers_basic_data = ExcelHelper.retrieve_drivers_data()
    drivers_basic_data = [driver_data for driver_data in drivers_basic_data if driver_data[service_filter] == 'Yes']
    if len(drivers_basic_data) == 0:
        return render_template('main.html', drivers=None, messages=['No driver provides the selected service!'])
    else:
        driversLocations = [data['Address'] for data in drivers_basic_data]
        driversResponse = InternalHelper.retrieve_nearest_drivers(driversLocations, client_location, drivers_basic_data)
        estimatedPriceResponse = \
            InternalHelper.calculate_estimated_price_based_on_service(client_location, preferred_client_destination,
                                                                      service_filter, vehicle_type)
        return render_template('main.html', drivers=driversResponse, estimatedPrice=estimatedPriceResponse,
                               messages=None)


if __name__ == '__main__':
    app.run('localhost', 3000, debug=True)
