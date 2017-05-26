import flask_admin
import functools
import os
import re

from flask import render_template, flash, redirect, session, url_for, request, g, Markup, abort
from app import app, db, admin
from models import *
from flask_admin.contrib import sqla 
from flask_admin.contrib.sqla import filters, ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from datetime import datetime
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache

# def login_required(fn):
#     @functools.wraps(fn)
#     def inner(*args, **kwargs):
#         if session.get('logged_in'):
#             return fn(*args, **kwargs)
#         return redirect(url_for('login', next=request.path))
#     return inner

# @app.route('/login/', methods=['GET', 'POST'])
# def login():
#     next_url = request.args.get('next') or request.form.get('next')
#     if request.method == 'POST' and request.form.get('password'):
#         password = request.form.get('password')
#         # TODO: If using a one-way hash, you would also hash the user-submitted
#         # password and do the comparison on the hashed versions.
#         if password == app.config['ADMIN_PASSWORD']:
#             session['logged_in'] = True
#             session.permanent = True  # Use cookie to store session.
#             flash('You are now logged in.', 'success')
#             return redirect(next_url or url_for('index'))
#         else:
#             flash('Incorrect password.', 'danger')
#     return render_template('login.html', next_url=next_url)

# @app.route('/logout/', methods=['GET', 'POST'])
# def logout():
#     if request.method == 'POST':
#         session.clear()
#         return redirect(url_for('login'))
#     return render_template('logout.html')

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
    months = [('May 2017','0517'),
                ('Jun 2017','0617'),
                ('Jul 2017','0717'),
                ('Aug 2017','0817'),
                ('Sep 2017','0917'),
                ('Oct 2017','1017'),
                ('Nov 2017','1117'),
                ('Dec 2017','1217')]
    return render_template('events.html',events=events, months=months,title='Draft Events')

@app.route('/events')
def events():
    events = Event.query.filter_by(published=True).order_by(Event.date).all()
    months = [('May 2017','0517'),
                ('Jun 2017','0617'),
                ('Jul 2017','0717'),
                ('Aug 2017','0817'),
                ('Sep 2017','0917'),
                ('Oct 2017','1017'),
                ('Nov 2017','1117'),
                ('Dec 2017','1217')]
    return render_template('events.html',events=events,months=months)

def create_or_edit_event(event, template):
    if request.method == 'POST':
        event.title = request.form.get('title') or ''
        event.content = request.form.get('content') or ''
        event.excerpt = request.form.get('excerpt') or ''
        event.published = request.form.get('published') or False
        event.thumbnail = request.form.get('thumbnail') or ''
        datestr = request.form.get('event-date')
        try:
            event.date = datetime.strptime(datestr,'%d/%m/%y %H:%M')
        except ValueError:
            flash('Event date format does not match requirement.', 'danger')
        if request.form.get('published'):
            event.published = True
        if not (event.title and event.content):
            flash('Title and Content are required.', 'danger')
        else:
            event.slug = event.get_slug()
            db.session.add(event)
            db.session.commit()
            flash('Event saved successfully.', 'success')
            if event.published:
                return redirect(url_for('event_detail', slug=event.slug))
            else:
                return redirect(url_for('edit_event', slug=event.slug))

    return render_template(template, event=event)

@app.route('/create_event/', methods=['GET', 'POST'])
@login_required
def create_event():
    event = Event()
    event.title = 'Event title here...'
    event.content = 'Event information here...'
    event.excerpt = 'Optional: short description for events page'
    event.published = False
    return create_or_edit_event(event, 'create.html')

@app.route('/<slug>/edit_event/', methods=['GET', 'POST'])
@login_required
def edit_event(slug):
    event = Event.query.filter_by(slug=slug).first()
    if event:
	    return create_or_edit_event(event, 'edit.html')

@app.route('/<slug>/')
def event_detail(slug):
    if g.user.is_authenticated:
        event = Event.query.filter_by(slug=slug).first()
    else:
        event = Event.query.filter_by(slug=slug,published=True).first()
    if event:
	    return render_template('detail.html', event=event)
    else:
        abort(404)

@app.route('/gallery')
def gallery():
    images = GalleryImage.query.all()
    return render_template('gallery.html',images=images)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you, your message was sent', 'success')
        render_template('contact_form.html')
    return render_template('contact_form.html')

@app.route('/booking')
def booking():
    return render_template('contact_form.html')

def send_mail(recipient, message):
    return requests.post(
        "https://api.mailgun.net/v/sandboxf4964574be95424090ad8595a65f344.mailgun.org/messages",
        auth=("api", "key-f8ea884ca732d71f34b2cb001ef0463"),
        data={"from":"", "to": recipient}
        )

admin.add_view(ModelView(Event, db.session))
admin.add_view(ModelView(GalleryImage, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))
gallerypath = os.path.join(os.path.dirname(__file__), 'static/img/gallery')
admin.add_view(FileAdmin(gallerypath,'/static/img/gallery',name='Gallery Images'))
