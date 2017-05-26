class Booking(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	datetime_start = db.Column(db.Datetime)
	datetime_end = db.Column(db.Datetime)
	datetime_request = db.Column(db.Datetime)
	status = db.Column(db.String)
	datetime_status = db.Column(db.Datetime)
	requestor_id = db.Column(db.Integer, db.ForeignKey('client.id'))
	note = db.Column(db.Text)

class Client(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.String)
	phone = db.Column(db.String)
	email = db.Column(db.String)

	def __str__(self):
		return self.email

class Availability(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.Date)
	timeblock = db.Column(db.Datetime)
	status = db.Column(db.String)
	booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))

def check_available(timeblock_start,timeblock_end):



