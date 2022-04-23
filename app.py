import datetime
import pandas
import configparser

from API.GoogleMapsAPI import GoogleMapsAPI
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def towing_dashboard():
    return render_template('main.html')


@app.route('/', methods=['POST'])
def render_results():
    api_key = get_api_key()
    clientLocation, serviceFilter, search_by_coordinates = input_data_elaborate()
    if clientLocation is None:
        return render_template('main.html', drivers=None, messages=['No input provided for client location!'])
    drivers_basic_data = read_excel_and_build_drivers_data()
    if serviceFilter is not None:
        drivers_basic_data = [driver_data for driver_data in drivers_basic_data if driver_data[serviceFilter] == 'Yes']
        if len(drivers_basic_data) == 0:
            return render_template('main.html', drivers=None, messages=['No driver provides the selected service!'])
    driversLocations = [data['Coordinates'] if search_by_coordinates else data['Address'] for data in
                        drivers_basic_data]
    googleMapsAPI = GoogleMapsAPI(api_key)
    driversDistanceResponse = googleMapsAPI.retrieve_drivers_distance_data(driversLocations, clientLocation)
    return render_template('main.html', drivers=retrieve_nearest_drivers(driversDistanceResponse, drivers_basic_data)
                           , messages=None)


def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['distancematrix']['api']


def input_data_elaborate():
    client_location = None
    service_filter = None
    search_by_coordinates = False

    if request.form['fullAddressInput']:
        client_location = request.form['fullAddressInput']
    elif request.form['zipCodeInput']:
        client_location = request.form['zipCodeInput']
    elif request.form['coordinatesInput']:
        search_by_coordinates = True
        client_location = request.form['coordinatesInput']

    if ':' not in request.form['filterByService']:
        service_filter = request.form['filterByService']

    return client_location, service_filter, search_by_coordinates


def read_excel_and_build_drivers_data():
    towingDrivers_df = pandas.read_excel('./static/DriversDB.xlsx')
    return towingDrivers_df.to_dict('records')


def normalize_values(driver_data):
    for data in driver_data:
        data['duration_in_traffic'] = str(datetime.timedelta(seconds=data['duration_in_traffic']))
        data['distance'] = str(int(data['distance']) // 1000) + ' km'
    return driver_data


def retrieve_nearest_drivers(drivers_distance_data, drivers_basic_data):
    drivers_final_data = drivers_basic_data
    [drivers_final_data[index].update(additional_data) for index, additional_data in enumerate(drivers_distance_data)]
    drivers_final_data = normalize_values(drivers_final_data)
    drivers_final_data.sort(key=lambda d: d['duration_in_traffic'])
    return drivers_final_data


if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)
