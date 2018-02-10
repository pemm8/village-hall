import re
import os
import functools
import datetime

import flask_admin
from flask import render_template, flash, redirect, session, url_for, request, g, Markup, abort
from flask_admin.contrib import sqla 
from flask_admin.contrib.sqla import filters, ModelView
from flask_admin.contrib.fileadmin import FileAdmin

from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user, utils, roles_required

from config import BOOKING_FORM_ENABLED
from app import app, db, admin
from models import User, Role, ContactMessage, Event, GalleryImage
from emails import *
from booking.models import RequestBooking, Client

app.jinja_env.globals.update(BOOKING_FORM_ENABLED=BOOKING_FORM_ENABLED)

def get_months(number):
    months = []
    now = datetime.datetime.utcnow()
    start = now.month
    for n in range(start, start + number):
        year = now.year
        if n > 12: 
            n -= 12
            year = year + 1
        months.append((datetime.date(year, n, 1).strftime('%b %Y'), datetime.date(year, n, 1).strftime('%m%y')))
    return months 

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
@app.route('/index')
def index():
	return render_template('home.html')

@app.route('/event_drafts')
@login_required
def event_drafts():
    events = Event.query.filter_by(published=False).order_by(Event.date).all()
    months = get_months(6)
    return render_template('events.html',events=events, months=months,title='Draft Events')

@app.route('/events')
def events():
    now = datetime.datetime.utcnow()
    events = Event.query.filter_by(published=True).filter(Event.date>now).order_by(Event.date).all()
    months = get_months(6)
    return render_template('events.html',events=events,months=months)

def create_or_edit_event(event, template):
    if request.method == 'POST':
        # Validated
        validated = True
        # Set Event Values
        event.title = request.form.get('title') or ''
        event.content = request.form.get('content') or ''
        event.excerpt = request.form.get('excerpt') or ''
        event.published = request.form.get('published') or False
        event.thumbnail = request.form.get('thumbnail') or ''
        datestr = request.form.get('event-date')
        if request.form.get('published'):
            event.published = True
        
        try:
            event.date = datetime.datetime.strptime(datestr,'%d/%m/%y %H:%M')
        except ValueError:
            flash('Event date is missing or format does not match requirement.', 'danger')
            validated = False

        if not (event.title and event.content):
            flash('Title and Content are required.', 'danger')
            validated = False

        if validated == True:
            event.slug = event.get_slug()
            db.session.add(event)
            db.session.commit()
            flash('Event saved successfully.', 'success')
            if event.published:
                return redirect(url_for('event_detail', slug=event.slug))
            else:
                return redirect(url_for('edit_event', slug=event.slug))

    return render_template(template, event=event)

@app.route('/<slug>/delete_event/')
@login_required
@roles_required('admin','-event-delete')
def delete_event(slug):
    e = Event.query.filter_by(slug=slug).first()
    if e is None:
        abort(404)
    e.deleted = True
    db.session.add(e)
    db.session.commit()
    flash('Event deleted successfully', 'success')
    return render_template('events.html')

@app.route('/create_event/', methods=['GET', 'POST'])
@login_required
@roles_required('admin','-events')
def create_event():
    event = Event()
    event.published = False
    return create_or_edit_event(event, 'create.html')

@app.route('/<slug>/edit_event/', methods=['GET', 'POST'])
@login_required
@roles_required('admin','-events')
def edit_event(slug):
    event = Event.query.filter_by(slug=slug).first()
    if event:
	    return create_or_edit_event(event, 'edit.html')

@app.route('/<slug>/')
def event_detail(slug):
    if g.user.is_authenticated and g.user.has_role('-events'):
        event = Event.query.filter_by(slug=slug).first()
    else:
        event = Event.query.filter_by(slug=slug,published=True).first()
    if event:
	    return render_template('detail.html', event=event)
    else:
        abort(404)

@app.route('/gallery')
def gallery():
    images = GalleryImage.query.filter_by(visible=True).all()
    return render_template('gallery.html',images=images)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name') or ''
        email = request.form.get('email') or ''
        phone = request.form.get('phone') or ''
        message = request.form.get('message') or ''
        contact_email(name, email, phone, message)
        contact_receipt_email(email)
        flash('Thank you, your message was sent', 'success')
    return render_template('contact_form.html')

# @app.route('/booking')
# def booking():
#     if BOOKING_FORM_ENABLED == True:
#         return redirect(url_for('booking_app.home'))
#     else:
#         return redirect(url_for('contact'))

@app.route('/gallery-admin')
def gallery_admin():
    pass

class AppAdmin(sqla.ModelView):
    def is_accessible(self):
        return current_user.has_role('-database')

class AppFileAdmin(FileAdmin):
    def is_accessible(self):
        return current_user.has_role('-database')

class UserAdmin(sqla.ModelView):
    column_exclude_list = ['password']
    def is_accessible(self):
        return current_user.has_role('-users')

class BookingAdmin(sqla.ModelView):
    def is_accessible(self):
        return current_user.has_role('-bookings')

admin.add_view(AppAdmin(Event, db.session))
admin.add_view(AppAdmin(GalleryImage, db.session))
admin.add_view(UserAdmin(User, db.session))
admin.add_view(UserAdmin(Role, db.session))
admin.add_view(AppAdmin(ContactMessage, db.session))
admin.add_view(BookingAdmin(RequestBooking, db.session))
admin.add_view(BookingAdmin(Client, db.session))

gallerypath = os.path.join(os.path.dirname(__file__), 'static/img/gallery')
admin.add_view(AppFileAdmin(gallerypath,'/static/img/gallery',name='Gallery Images'))
