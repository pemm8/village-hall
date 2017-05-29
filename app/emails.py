from flask import render_template
from flask_mail import Message
from app import mail
from app import app
from config import SECURITY_EMAIL_SENDER, ADMINS

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    return True

def contact_email(name, email, phone, message):
	subject = "Gumley Village Hall: New Message Received"
	sender = SECURITY_EMAIL_SENDER
	recipients = ADMINS
	text_body = render_template("contact_email.txt",name=name, email=email, phone=phone, message=message)
	html_body = render_template("contact_email.html",name=name, email=email, phone=phone, message=message)
	send_email(subject,sender,recipients,text_body,html_body)