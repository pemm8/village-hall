#!env/bin/python
from config import SQLALCHEMY_DATABASE_URI
from app import db
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache

db.create_all()