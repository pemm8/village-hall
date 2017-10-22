import datetime as dt
import random, string

from app import db

class Client(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String)
	last_name = db.Column(db.String)
	phone = db.Column(db.String)
	email = db.Column(db.String)
	created = db.Column(db.DateTime, default=dt.datetime.utcnow())

	def __str__(self):
		return self.email

	def find_bookings(self):
		return RequestBooking.query.filter_by(requestor=self).all()

class RequestBooking(db.Model):
	__tablename__ = 'request'
	id = db.Column(db.Integer, primary_key=True)
	dtStart = db.Column(db.DateTime)
	dtEnd = db.Column(db.DateTime)
	dtRequest = db.Column(db.DateTime, default=dt.datetime.utcnow())
	status = db.Column(db.String)
	dtStatus = db.Column(db.DateTime)
	requestor_id = db.Column(db.Integer, db.ForeignKey('client.id'))
	requestor = db.relationship('Client',backref=db.backref('requests', lazy='dynamic'))
	note = db.Column(db.Text)
	receipt = db.Column(db.String(8))

	def allocate_receipt(self):
		s=string.lowercase+string.digits
		uid=''.join(random.sample(s,8))
		if RequestBooking.query.filter_by(receipt=uid).first() is None:
			self.receipt = uid
			return True
			
