import os
import flask_admin as admin

from flask import Flask
from app.booking import booking
from flask_sqlalchemy import SQLAlchemy 
from flask_security import Security, SQLAlchemyUserDatastore, \
	UserMixin, RoleMixin, login_required, current_user, utils

# Create App
app = Flask(__name__)
app.config.from_object('config')
app.register_blueprint(booking, url_prefix='/booking')

# Setup Database
db = SQLAlchemy(app)

# Setup Flask-Admin
admin = admin.Admin(app, name='Admin', template_mode='bootstrap3')

from app import views, models
from models import User, Role

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)