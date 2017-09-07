import datetime

class Client(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.String)
	phone = db.Column(db.String)
	email = db.Column(db.String)

	def __str__(self):
		return self.email

class Booking(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	datetime_start = db.Column(db.Datetime)
	datetime_end = db.Column(db.Datetime)
	datetime_request = db.Column(db.Datetime)
	status = db.Column(db.String)
	datetime_status = db.Column(db.Datetime)
	requestor_id = db.Column(db.Integer, db.ForeignKey('client.id'))
	note = db.Column(db.Text)

class Timeblock(db.Model):
	id = db.Column(db.Double, primary_key=True)
	status = db.Column(db.Integer)
	booking_id = db.Colmun(db.Integer, db.ForeignKey('booking.id'))

	def __str__(self):
		return self.id
	
def check_available(timeblock_start,timeblock_end):
	# TODO

def calculate_timeblock(date):
	return datetime.strftime('%Y%m%d%H%M',date)



