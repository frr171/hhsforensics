from google.appengine.ext import db

import datetime

class User(db.Model):
	name = db.StringProperty()
	username = db.StringProperty()
	email = db.StringProperty()
	password = db.StringProperty()
	registerdate = db.DateProperty()
	permissions = db.StringProperty()
	tags = db.StringProperty()
	facebookid = db.StringProperty()