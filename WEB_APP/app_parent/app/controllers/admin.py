from flask import Blueprint, flash, redirect, url_for
from flask import request, render_template
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import TextAreaField
from wtforms.widgets import TextArea
from app.models.page import Page
from app import db
from bs4 import BeautifulSoup   
import sys
import zlib
import re
import bcrypt
import json
import base64
import cryptography.fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import session, redirect
#gets login_required wrapper from ./login
from app.controllers.login import login_required
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
from app.services.json_tools import encrypt_json, decrypt_json
from app.controllers.get_pages import result as pages_list
with open("symmetric_key.key", "rb") as key_file:
    symmetric_key = key_file.read()
def remove_jinja_templates(html_content):
    # This regex will match content within { } brackets, accounting for nested brackets as well.
    pattern = r'\{[^{}]*\}'
    while re.search(pattern, html_content):
        html_content = re.sub(pattern, '', html_content)
    return html_content

###FUNCTION TO GET VALUE OF AN OBJECT by matching the value of another key in the object. 
###Returns the content value of object in the list, with a matchig "name" value. made by chatgpt.

def get_content_by_name(object_list, search_name):
    
    # Iterate over each object in the list
    for obj in object_list:
        # Check if the object has the 'link' attribute and if it matches the search_name
        if 'link' in obj and obj['link'] == search_name:
            # If the object has the 'content' attribute, return its value
            if 'content' in obj:
                _content=obj['content']
                try:
                    try:
                        decoded_bytes = base64.b64decode(obj['content'])
                        decoded_content = zlib.decompress(decoded_bytes)

                        html_content = (remove_jinja_templates((decoded_content.decode('utf-8'))))
                        soup = BeautifulSoup(html_content, "html.parser")
                        decoded_content = soup.get_text()
                        
                    except Exception as e:
                        print(f"Base64 data: {obj['content']}")
                        print(f"Decoded content: {decoded_content}")
                        raise e
                    
                    
                    return html_content
                except Exception as e:
                    return "Error decoding base64 content: {}".format(str(e))
            # If the object does not have the 'content' attribute, return an error message
            else:
                return "Error: Object with name '{}' does not have a 'content' attribute.".format(search_name)
    
    # If no object with the given 'name' attribute is found, return an error message
    return "Error: No object with name '{}' found.".format(search_name)



admin_custom_blueprint = Blueprint('admin_custom', __name__, template_folder='templates/admin')
@admin_custom_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Decrypt the existing user data
        encrypted_data = open("app/data/encrypted_users.json", "rb").read()
        decrypted_data = decrypt_json(encrypted_data, symmetric_key)

        # Initialize user_found as False
        user_found = False

        # Loop through the list of user dictionaries
        for user in decrypted_data:
            if user['email'] == email:
                stored_password_hash = user['password']
                if isinstance(stored_password_hash, str):
                    stored_password_hash = stored_password_hash.encode('utf-8')  # Encode to bytes
                user_found = True
                break
        if user_found:
            print(f"Stored password hash for debugging: {stored_password_hash}",file=sys.stdout)

            if isinstance(stored_password_hash, str):
                stored_password_hash = stored_password_hash.encode('utf-8')

            
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
                    session['public_key'] = user['public_key']
                    session['logged_in'] = True
                    session['email'] = email
                    session['admin_authorized']=True
                    return redirect(url_for("admin_custom.dashboard"))
                else:
                    return "Wrong password", 401
            except Exception as e:
                return f"An error occurred during password check: {e}", 500
    else:
        return render_template('admin/login.html')
class PageModelView(ModelView):
    column_exclude_list = ['content']
    column_list = ('title', 'slug')
    form_columns = ('title', 'slug', 'content')
    form_widget_args = {
        'content': {
            'widget': TextArea()
        }
    }

@admin_custom_blueprint.route('/access', methods=['GET', 'POST'])
def admin_access():
    if request.method == 'POST':
        secret_phrase = request.form.get('secret_phrase')
        if secret_phrase == "!Gratitude98":
            session['admin_authorized'] = True
            return redirect(url_for('admin_custom.login'))
    return render_template('admin/admin_access.html')


###
#THIS route creates a user with a public-private key pair. A little
#overkill but wanted to get some practice on making 
#something for email and password that can stand up against
#phone and OTP security, cryptography-wise
###
@admin_custom_blueprint.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if session['admin_authorized']==False:
        return redirect(url_for('admin_custom.admin_access'))
    else:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()

            pem_priv = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            pem_pub = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Prepare user data
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_data = {
                'email': email,
                'password': hashed_password.decode('utf-8'),  # Decode to utf-8 string
                'private_key': pem_priv.decode('utf-8'),
                'public_key': pem_pub.decode('utf-8')
            }
            print(user_data['password'],file=sys.stdout)

            encrypted_data = open("app/data/encrypted_users.json", "rb").read()
            users = decrypt_json(encrypted_data, symmetric_key)
            if users is None:  #allows empty user file to be loaded without throwing NoneType Error
                users = [] 
            
            users.append(user_data)
            encrypted_data = encrypt_json(users, symmetric_key)
            
            with open("app/data/encrypted_users.json", "wb") as f:
                f.write(encrypted_data)

            return "User created successfully"

        return render_template('admin/admin_signup.html')

###
#DASHBOARD PAGES
###
page_names=[]
print('PAGES \n #############################################',file=sys.stdout)
print(pages_list("page.html"),file=sys.stdout)
i=0

@login_required
@admin_custom_blueprint.route('/dashboard', methods=['GET'])
def dashboard():
    if 'admin_authorized' not in session:
        return redirect(url_for('admin_custom.admin_access'))
    else:
        # Assuming you have a way to fetch the pages
        pages = pages_list("page.html")

        # Fetch the public_key from session
        public_key = None
        if 'public_key' in session:
            public_key = session['public_key']
        
        return render_template('admin/dashboard.html', pages=pages_list("page.html"), public_key=session["public_key"])


@login_required
@admin_custom_blueprint.route('/new_page', methods=['GET'])
def new_page():
    if 'admin_authorized' not in session:
        return redirect(url_for('admin_custom.admin_access'))
    # Load the menu.json file
    with open("app/controllers/menu.json", 'r') as f:
        menu_data = json.load(f)
        
    # Extract the parent menu names
    parent_menus = [item['name'] for item in menu_data]
    
    return render_template('admin/new_page.html', parent_menus=parent_menus)
 
@login_required
@admin_custom_blueprint.route('/edit-page', methods=['GET', 'POST'])
def edit_page():
    link = request.args.get('link')

    if 'public_key' in session:
        public_key = session['public_key']
    else:
        request.args.get('public_key')
    
    if request.method == 'POST':
        name = request.form.get("name")
        new_link = request.form.get("link")
        content = request.form.get("content")
        category = request.form.get("category")
        
        # Function to update JSON
        def update_json(link, new_link, name, category):
            with open("app/controllers/menu.json", 'r') as f:
                data = json.load(f)
                
            for menu_item in data:
                if menu_item['link'] == link:
                    menu_item['name'] = name
                    menu_item['link'] = new_link
                    menu_item['category'] = category
                
            with open("app/controllers/menu.json", 'w') as f:
                json.dump(data, f, indent=4)
        
        update_json(link, new_link, name, category)

        return redirect(url_for('admin_custom.dashboard'))

    return render_template('admin/edit.html', article_content=(get_content_by_name(pages_list('page.html'), link)), link=link, public_key=public_key)
    
@login_required
@admin_custom_blueprint.route('/webmaster-add-page', methods=['POST'])
def webmaster_add_page():
    import os

    current_directory = os.getcwd()
    print("Current Working Directory:", current_directory,file=sys.stdout)
    title = request.form.get("title")
    slug = request.form.get("slug")
    content = request.form.get("content")

    template_content = '''
    {{% extends "page.html" %}}
    {{% block pagecontent %}}
    
    <div>{}</div>
    {{% endblock %}}
    '''.format(content)
    
    with open("./app/templates/" + slug + ".html", "w") as f:
        f.write(template_content)

    return redirect(url_for('main.page', slug=slug))

@login_required
@admin_custom_blueprint.route('/delete-page', methods=['POST'])
def delete_page():
    if 'public_key' in session:
        public_key = session['public_key']
        link_to_delete = request.form.get('link')

        # Delete the template file
        try:
            os.remove(f"./app/templates/{link_to_delete}.html")
        except FileNotFoundError:
            # Handle error if the file doesn't exist
            pass

        # Update menu.json
        with open("app/controllers/menu.json", 'r') as f:
            data = json.load(f)

        data = [item for item in data if item['link'] != link_to_delete]
        
        with open("app/controllers/menu.json", 'w') as f:
            json.dump(data, f, indent=4)

        return redirect(url_for('admin_custom.dashboard'))
    else:
        # Handle unauthorized access
        return redirect(url_for('main.home')) 