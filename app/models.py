import re

from app import db, app
from datetime import datetime
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from flask import Markup

oembed_providers = bootstrap_basic(OEmbedCache())

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

	def get_title(self):
		return re.sub('[^\w]+', '-', self.title.lower()).strip('-')

class GalleryImage(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	path = db.Column(db.String)
	caption = db.Column(db.String)

