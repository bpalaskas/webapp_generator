from flask import render_template,redirect,url_for, request, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, create_access_token, create_refresh_token,  set_access_cookies
import traceback
from app.services.jwt_tools import generate_token
from app.models.user import User
from functools import wraps
import sys
import os
import json
from app import app, db
from app.models.page import Page
import app.services.sms_tools as sms_tools
from app.services.db_tools import create_user, update_user, delete_user, get_user_by_phone
create_twilio_client=sms_tools.create_twilio_client
get_credentials_from_env=sms_tools.get_credentials_from_env
check_sms_verification=sms_tools.check_sms_verification
get_credentials_from_env=sms_tools.get_credentials_from_env
send_sms_verification=sms_tools.send_sms_verification

from flask import Blueprint, render_template

main = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # your existing logic here
        return f(*args, **kwargs)
    return decorated_function




@main.route('/signup', methods=['GET', 'POST'])
def signup():
    # If it's a GET request, render the signup form
    if request.method == 'GET':
        return render_template('signup.html')

    # If it's a POST request (form submission), start the verification process
    if request.method == 'POST':
        phone_number = str('+1'+request.form.get('phone_number'))
        print(phone_number, file=sys.stdout)

        account_sid, auth_token, service_sid = get_credentials_from_env()

        client = create_twilio_client(account_sid, auth_token)

        send_sms_verification(client, service_sid, phone_number)

        long_term_token = generate_token()
        resp = make_response(redirect(url_for('verify',phone_number=phone_number)))
        resp.set_cookie('lt_token', long_term_token, httponly=True, samesite='Strict')

        # Redirect the user to the OTP verification page with the response that contains the long term token
        return resp
    


@main.route('/page/<slug>')
def page(slug):
    # Use relative path for Flask
    template_path = os.path.join("app/templates", "{}.html".format(slug))
    current_directory = os.getcwd()

    try:
        if os.path.exists(os.path.join(current_directory, template_path)):
            with open("app/controllers/menu.json") as menu_file:
                menu_items = json.load(menu_file)
            return render_template(("{}.html".format(slug)),menu_data=menu_items)
        else:
            page = Page.query.filter_by(slug=slug).first_or_404()
            with open("app/controllers/menu.json") as menu_file:
                menu_items = json.load(menu_file)
            return render_template('page.html', page=page, menu_data=menu_items)
    except Exception as e:
        traceback_str = traceback.format_exc()
        return(f'''COULD NOT RETURN PAGE from {template_path} 
                \n WORKING DIRECTORY: {current_directory} 
                \n TEMPLATE REQUESTED: {template_path}, template: {(slug + ".html")}
                \n EXCEPTION: {str(e)}
                \n TRACEBACK: {traceback_str}''')
@main.route('/')
def index():
    with open("app/controllers/menu.json") as menu_file:
        menu_items = json.load(menu_file)
    return render_template('index.html', menu_data=menu_items)
@app.route('/index')
def index():
    with open("app/controllers/menu.json") as menu_file:
        menu_items = json.load(menu_file)
    return render_template('index.html', menu_data=menu_items)
