import flask
from flask import Flask, render_template, request, session, flash
from helper.InternalHelper import InternalHelper
from helper.ExcelHelper import ExcelHelper
from flask_session import Session
from static.SessionDataEnum import SessionDataEnum
from collections import namedtuple

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
    job_data = InternalHelper.job_data_elaborate(request)
    drivers_basic_data = ExcelHelper.retrieve_drivers_data()
    drivers_basic_data = [driver_data for driver_data in drivers_basic_data if driver_data[job_data.service] == 'Yes']
    if len(drivers_basic_data) == 0:
        return render_template('main.html', drivers=None)
    else:
        driversLocations = [data['Address'] for data in drivers_basic_data]
        drivers = helper.retrieve_nearest_drivers(driversLocations, job_data.origin, drivers_basic_data)
        helper.calculate_estimated_price_based_on_service(job_data)
        session[SessionDataEnum.DRIVERS] = drivers
        session[SessionDataEnum.JOB_DATA] = job_data.__dict__
        return render_template('ChargeCustomer.html', job_data=job_data, drivers=drivers)


@app.route('/', methods=['POST'])
def send_customer_invoice():
    if 'Cancel' in request.form:
        return return_search_page()
    customer = InternalHelper.customer_input_data_elaborate(request)
    payment_link = helper.send_customer_invoice(session[SessionDataEnum.JOB_DATA]['advanced_payment'], customer,
                                                session[SessionDataEnum.JOB_DATA]['service'])
    session[SessionDataEnum.JOB_DATA]['total_price'] = None
    job_data = namedtuple("JobData", session[SessionDataEnum.JOB_DATA].keys())(*session[SessionDataEnum.JOB_DATA].values())
    flash(payment_link, "info")
    return render_template('ChargeCustomer.html', drivers=session[SessionDataEnum.DRIVERS], job_data=job_data,
                           payment_link=payment_link)


@app.route('/', methods=['POST'])
def return_search_page():
    session.clear()
    return render_template('main.html', drivers=None)


if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)
