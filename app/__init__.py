import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy 
import flask_admin as admin 

# Create App
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
admin = admin.Admin(app, name='Admin', template_mode='bootstrap3')

from app import views, models