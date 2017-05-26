import functools, os, re, string, random

from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, Markup, abort
from datetime import datetime

booking = Blueprint('booking', __name__, template_folder='booking')

@booking.route('/')
@booking.route('/intro')
def show_intro():
	return render_template('booking/intro.html')

@booking.route('/booking_calendar')
def show_calendar():
	return render_template('booking/calendar.html')