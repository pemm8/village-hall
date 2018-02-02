import functools, os, re, string, random, datetime
from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, Markup, abort
from datetime import datetime
from flask_security import login_required, current_user, roles_required

from forms import BookingForm
from app import db
from models import Client, RequestBooking

booking_app = Blueprint('booking_app', __name__, template_folder='booking')

@booking_app.route('/')
@booking_app.route('/home')
def home():
	return render_template('booking/index.html')

@booking_app.route('/form', methods=['GET','POST'])
def form():
	form = BookingForm()
	if form.validate_on_submit():
		cl = Client.query.filter_by(email=form.email.data).first()
		if not cl:
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
		return redirect(url_for('booking_app.track', booking_ref=rq.receipt))
	return render_template('booking/form.html',form=form)

@booking_app.route('/track/<booking_ref>')
def track(booking_ref):
	b = RequestBooking.query.filter_by(receipt=booking_ref).first_or_404()
	if b:
		cl = b.requestor
		return render_template('booking/confirmation.html', booking=b, client=cl)
	else:
		return "<h1>That booking doesn't exist</h1>"

@booking_app.route('/admin/')
@login_required
@roles_required('admin','-bookings')
def admin():
	new_bookings = RequestBooking.query.filter_by(status='new').all()
	confirmed_bookings = RequestBooking.query.filter_by(status='confirmed').all()
	return render_template('booking/admin.html', new_bookings=new_bookings, confirmed_bookings=confirmed_bookings)

@booking_app.route('/approve/<booking_id>')
@login_required
@roles_required('admin','-bookings')
def approve(booking_id):
	booking = RequestBooking.query.get(booking_id)
	if booking:
		booking.status = "confirmed"
		db.session.commit()
		msg = 'Booking %s confirmed' % (booking.receipt)
		flash(msg, 'success')
		return redirect(url_for('booking_app.admin'))

@booking_app.route('/cancel/<booking_id>')
@login_required
@roles_required('admin','-bookings')
def cancel(booking_id):
	booking = RequestBooking.query.get(booking_id)
	if booking:
		booking.status = "cancelled"
		db.session.commit()
		msg = 'Booking %s cancelled' % (booking.receipt)
		flash(msg, 'danger')
		return redirect(url_for('booking_app.admin'))

@booking_app.route('/admin/client/<client_id>')
@login_required
@roles_required('admin','-bookings')
def admin_client(client_id):
	client = Client.query.get(client_id)
	if client:
		bookings = client.find_bookings()
		return render_template('booking/client.html', client=client, bookings=bookings)
	else:
		return redirect(url_for('admin'))

@booking_app.route('/admin/booking/<booking_id>')
@login_required
@roles_required('admin','-bookings')
def admin_booking(booking_id):
	booking = RequestBooking.query.get(booking_id)
	if booking:
		return render_template('booking/booking-detail.html', booking=booking)
	else:
		return redirect(url_for('admin'))





