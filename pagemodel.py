from google.appengine.ext import db

class PageCode(db.Model):
	name = db.StringProperty()
	html = db.TextProperty()