import functools, os, re, string, random, datetime

from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, Markup, abort
from datetime import datetime
from forms import BookingForm
from app import db
from models import Client, RequestBooking

booking = Blueprint('booking', __name__, template_folder='booking')

@booking.route('/')
@booking.route('/home')
def home():
	return render_template('booking/index.html')

@booking.route('/form', methods=['GET','POST'])
def form():
	form = BookingForm()
	if form.validate_on_submit():
		cl = Client(
			first_name = form.first_name.data,
			last_name = form.last_name.data,
			email = form.email.data,
			phone = form.phone.data)
		db.session.add(cl)
		rq = RequestBooking(
			dtStart = form.dateStart.data,
			dtEnd = form.dateEnd.data,
			status = 'new',
			dtStatus = datetime.utcnow(),
			requestor = cl)
		rq.allocate_receipt()
		db.session.add(rq)
		db.session.commit()
		# flash('Thank you, your booking request has been sent', 'success')
		return redirect(url_for('booking.track', booking_ref=rq.receipt))
	return render_template('booking/form.html',form=form)

@booking.route('/track/<booking_ref>')
def track(booking_ref):
	b = RequestBooking.query.filter_by(receipt=booking_ref).first_or_404()
	cl = b.requestor
	if b:
		return render_template('booking/confirmation.html', booking=b, client=cl)
	else:
		return "<h1>That booking doesn't exist</h1>"
