from flask import render_template
from flask_mail import Message
from app import app, mail, db
from models import ContactMessage
from config import SECURITY_EMAIL_SENDER, ADMINS
import datetime as dt

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    return True

	# name = db.Column(db.String)
	# phone = db.Column(db.String)
	# email = db.Column(db.String)
	# body = db.Column(db.Text)
	# status = db.Column(db.String(10))
	# created = db.Column(db.DateTime)
	# updated = db.Column(db.DateTime)
	# receipt = db.Column(db.String(8))

def save_contact(name,email,phone,message):
	msgdb = ContactMessage()
	msgdb.body = message
	msgdb.name = name
	msgdb.phone = phone
	msgdb.email = email
	msgdb.status = 'msg_sent'
	msgdb.created = dt.datetime.utcnow()
	msgdb.receipt = msgdb.allocate_receipt()
	db.session.add(msgdb)
	if db.session.commit():
		return True

def contact_email(name, email, phone, message):
	subject = "Gumley Village Hall: New Message Received"
	sender = SECURITY_EMAIL_SENDER
	recipients = ADMINS
	save_contact(name,email,phone,message)
	text_body = render_template("contact_email.txt",name=name, email=email, phone=phone, message=message)
	html_body = render_template("contact_email.html",name=name, email=email, phone=phone, message=message)
	send_email(subject,sender,recipients,text_body,html_body)

def contact_receipt_email(email):
	subject = "Gumley Village Hall: Thank you for your message"
	sender = SECURITY_EMAIL_SENDER
	recipients = []
	recipients.append(email)
	text_body = ''
	text_body = render_template("contact_receipt_email.txt")
	html_body = render_template("contact_receipt_email.html")
	send_email(subject,sender,recipients,text_body,html_body)