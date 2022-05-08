import flask
from flask import Flask, render_template, request, session, flash
from helper.InternalHelper import InternalHelper
from helper.ExcelHelper import ExcelHelper
from static.Services import Services
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

helper = InternalHelper()


@app.route('/')
def towing_dashboard():
    return render_template('main.html')


@app.route('/service/payment', methods=['POST'])
def render_results():
    session.pop('_flashes', None)
    client_location, preferred_client_destination, service_filter, vehicle_type = InternalHelper.input_data_elaborate(
        request)
    drivers_basic_data = ExcelHelper.retrieve_drivers_data()
    service_value = Services[service_filter].value
    drivers_basic_data = [driver_data for driver_data in drivers_basic_data if driver_data[service_value] == 'Yes']
    if len(drivers_basic_data) == 0:
        return render_template('main.html', drivers=None)
    else:
        driversLocations = [data['Address'] for data in drivers_basic_data]
        driversResponse = helper.retrieve_nearest_drivers(driversLocations, client_location, drivers_basic_data)
        estimatedPriceResponse, price_per_mile, advanced_payment = helper.calculate_estimated_price_based_on_service(
            client_location,
            preferred_client_destination,
            service_filter, vehicle_type)
        session['drivers'] = helper.normalize_tel_values(driversResponse)
        session['advanced_payment_price'] = advanced_payment
        session['type_of_service'] = service_value
        return render_template('main.html', estimatedPrice=estimatedPriceResponse, price_per_mile=price_per_mile,
                               advanced_payment_price=advanced_payment)


@app.route('/book/drivers', methods=['POST'])
def send_customer_invoice():
    if 'Cancel' in request.form:
        return render_template('main.html', drivers=None)
    customer = InternalHelper.customer_input_data_elaborate(request)
    payment_link = helper.send_customer_invoice(session['advanced_payment_price'], customer, session['type_of_service'])
    flash(payment_link, "info")
    return render_template('main.html', drivers=flask.session['drivers'])


if __name__ == '__main__':
    app.run('localhost', 3000, debug=True)
