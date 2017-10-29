import os
from flask_script import Manager

from app import app, db, models
from app.models import GalleryImage

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

if __name__ == "__main__":
	manager.run()