from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
import os
from sqlalchemy import MetaData
app = Flask(__name__)
metadata = MetaData(schema="public")

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://centurysecurity:Century!@localhost/century_security'

db = SQLAlchemy(app)

####LOGGING###################################
import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('flask.log', maxBytes=10000, backupCount=3)
formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
#################################

admin = Admin(app, template_mode='bootstrap3')
login = LoginManager(app)
jwt = JWTManager(app)
login.login_view = 'main.login'  

from .models.page import Page
from .models.user import User, Visitor

with app.app_context():
    db.create_all()

from .controllers.main import main as main_blueprint
from .controllers.admin import admin_custom_blueprint as admin_blueprint

app.register_blueprint(main_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(401)
def unauthorized_error(e):
    return redirect(url_for('main.login'))