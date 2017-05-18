import re, string, random

from app import db, app
from datetime import datetime
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from flask import Markup
from flask_security import Security, SQLAlchemyUserDatastore, \
	UserMixin, RoleMixin, login_required, current_user, utils

oembed_providers = bootstrap_basic(OEmbedCache())

def gen_slug(title):
	s=string.lowercase+string.digits
	uid = ''.join(random.sample(s,5))
	slug = re.sub('[^\w]+', '-', title.lower()).strip('-')
	return slug + '-' + uid

class Event(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	slug = db.Column(db.String, unique=True)
	content = db.Column(db.Text)
	published = db.Column(db.Boolean, index=True, default=False)
	date = db.Column(db.DateTime)
	created = db.Column(db.DateTime, default=datetime.utcnow)
	excerpt = db.Column(db.Text)
	thumbnail = db.Column(db.String)

	@property
	def html_content(self):
		"""
		Generate HTML representation of the markdown-formatted blog entry,
		and also convert any media URLs into rich media objects such as video
		players or images.
		"""
		hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
		extras = ExtraExtension()
		markdown_content = markdown(self.content, extensions=[hilite, extras])
		oembed_content = parse_html(
			markdown_content,
			oembed_providers,
			urlize_all=True,
			maxwidth=app.config['SITE_WIDTH'])
		return Markup(oembed_content)

	def get_slug(self):
		slug = gen_slug(self.title)			
		if Event.query.filter_by(slug=slug).first() is None:
			return slug
		else:
			condition = False
			while condition == False:
				slug = gen_slug(self.title)
				condition = Event.query.filter_by(slug=slug).first()
				if condition: 
					return slug

class GalleryImage(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.String)
	caption = db.Column(db.String)

# Flask-Security Models

roles_users = db.Table('roles_users',
		db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
		db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(80), unique=True)
	description = db.Column(db.String(255))

	def __str__(self):
		return self.name

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True)
	password = db.Column(db.String(255))
	active = db.Column(db.Boolean())
	confirmed_at = db.Column(db.DateTime())
	roles = db.relationship('Role', secondary=roles_users,
							backref=db.backref('users', lazy='dynamic'))
	# User Tracking
	last_login_at = db.Column(db.DateTime())
	current_login_at = db.Column(db.DateTime())
	last_login_ip = db.Column(db.String(30))
	current_login_ip = db.Column(db.String(30))
	login_count = db.Column(db.Integer)

	def __str__(self):
		return self.email

