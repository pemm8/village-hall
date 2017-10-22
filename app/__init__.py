import os
import flask_admin as admin 
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy 
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user, utils, roles_required
from flask_mail import Mail

# Create App
app = Flask(__name__)
app.config.from_object('config')

# Setup Database
db = SQLAlchemy(app)

# Register Blueprints
from app.booking import booking

app.register_blueprint(booking, url_prefix='/booking')


# Setup Flask-Mail
mail = Mail(app)

# Setup Flask-Admin
admin = admin.Admin(app, name='Admin', template_mode='bootstrap3')

from app import views, models
from models import User, Role

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)