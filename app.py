import flask
from flask import Flask, render_template, request, session, flash, Response
import json
import math
from helper.InternalHelper import InternalHelper
from helper.ExcelHelper import ExcelHelper
from helper.FileHelper import FileHelper
from flask_session import Session
from static.SessionDataEnum import SessionDataEnum
from static.Services import Services
from collections import namedtuple

app = Flask(__name__)
app.config.update(
    SESSION_PERMANENT=True,
    SESSION_TYPE="filesystem",
    TEMPLATES_AUTO_RELOAD=True
)
Session(app)

helper = InternalHelper()


@app.route('/')
def towing_dashboard():
    service = request.args.get('service')
    if service is not None:
        service_selected = Services[service].value
    else:
        service_selected = Services.BREAKDOWN_RECOVERY_SERVICE.value
    questions = InternalHelper.retrieve_customer_questions(service_selected)
    return render_template('main.html', service=service_selected, questions=questions)


@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    post_codes = FileHelper.retrieve_postcodes_data()
    return Response(json.dumps(post_codes), mimetype='application/json')


@app.route('/service/payment', methods=['POST'])
def render_results():
    session.pop('_flashes', None)
    job_data = InternalHelper.job_data_elaborate(request)
    drivers_basic_data = ExcelHelper.retrieve_drivers_data(job_data.origin)
    drivers_basic_data = [driver_data for driver_data in drivers_basic_data if driver_data[job_data.service] == 'Yes']
    if len(drivers_basic_data) == 0:
        return render_template('main.html', drivers=None)
    else:
        driversLocations = [data['Post Code'] for data in drivers_basic_data]
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

@app.route('/edit', methods=['POST'])
def edit_price_manually():
    total_price = float(request.form['total_price'])
    session[SessionDataEnum.JOB_DATA]['total_price'] = math.ceil(total_price)
    session[SessionDataEnum.JOB_DATA]['advanced_payment'] = math.ceil(math.ceil(total_price) * 0.35)
    session[SessionDataEnum.JOB_DATA]['driver_price'] = \
        session[SessionDataEnum.JOB_DATA]['total_price'] - session[SessionDataEnum.JOB_DATA]['advanced_payment']
    job_data = namedtuple("JobData", session[SessionDataEnum.JOB_DATA].keys())(*session[SessionDataEnum.JOB_DATA].values())
    return render_template('ChargeCustomer.html', drivers=session[SessionDataEnum.DRIVERS], job_data=job_data)


@app.route('/', methods=['POST'])
def return_search_page():
    session.clear()
    service_selected = Services.BREAKDOWN_RECOVERY_SERVICE.value
    questions = InternalHelper.retrieve_customer_questions(service_selected)
    return render_template('main.html', drivers=None, service=service_selected, questions=questions)


if __name__ == '__main__':
    app.run('localhost', 8888, debug=True)
