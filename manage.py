import os
import datetime as dt
from flask_script import Manager

from app import app, db, models
from app.models import GalleryImage, User, Role

manager = Manager(app)

@manager.command
def run_gallery_update():
	path = os.getcwd() + '/app/static/img/gallery/prod/'
	dbpath = '/prod/'
	files = os.listdir(path)
	f_count = 0
	for f in files:
		f_path = dbpath + f
		if not GalleryImage.query.filter_by(path=f_path).first():
			g = GalleryImage(path=f_path)
			db.session.add(g)
			f_count += 1
	print "%d Files Added" % (f_count)
	db.session.commit()

@manager.command
def test_command():
	print "Test Success"

@manager.command
def create_db():
	db.create_all()

@manager.command
def create_super():
	user = User.query.filter_by(email='super@gumleyvillagehall.org.uk').first()
	if user:
		db.session.delete(user)
		db.session.commit()
	user = User(
		email='super@gumleyvillagehall.org.uk',
		password='changeme',
		active=True,
		confirmed_at=dt.datetime.utcnow()
		)
	db.session.add(user)
	roles = ['admin','-events','-event-delete','-bookings','-database','-users']
	for role in roles:
		r = Role.query.filter_by(name=role).first()
		if not r:
			r = Role(name=role)
			db.session.add(r)
		user.roles.append(r)
	db.session.commit()
	print('Superuser created')

if __name__ == "__main__":
	manager.run()