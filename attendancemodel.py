from google.appengine.ext import db

import datetime

class Meeting(db.Model):
	date = db.DateTimeProperty()
	description = db.TextProperty()
	tags = db.StringProperty()
	
	students = db.StringListProperty()
	data = db.ListProperty(bool)
	
class Assignment(db.Model):
	date = db.DateTimeProperty()
	description = db.TextProperty()
	tags = db.StringProperty()
	
	name = db.StringProperty()
	
	students = db.StringListProperty()
	maxscore = db.IntegerProperty()
	scores = db.ListProperty(int)