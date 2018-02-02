from flask_wtf import Form
from wtforms import validators, StringField, DateTimeField
from wtforms.widgets import TextArea
from wtforms.fields.html5 import EmailField
from wtforms.validators import ValidationError
import re

# from user.models import User
    
class BookingForm(Form):
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    email = EmailField('Email Address', [
        validators.DataRequired(), 
        validators.Email()
        ]    
    )
    phone = StringField('Telephone Number', [validators.DataRequired()])
    dateStart = DateTimeField('Request Hall From', format='%d/%m/%Y %I:%M %p')
    dateEnd = DateTimeField('Request Hall Until', format='%d/%m/%Y %I:%M %p')