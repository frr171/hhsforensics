from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import os
from google.appengine.ext.webapp import template

from google.appengine.ext.db import Key

from usermodel import *
import re
import string
import datetime

from gaesessions import *

from attendancemodel import *

meetinghtml = '''
<tr class="odd">
	<td><a href="editmeeting?key={{key}}">{{date}}</a></td>
	<td>{{type}}</td>
	<td><a href="#" class="ico del">Delete</a></td>
</tr>
'''

studenthtml = '''
<tr>
	<td><input name="cb{{num}}" {{checked}} type="checkbox" class="checkbox" /></td>
	<td><h3>{{name}}</h3></td>
	<td><a href="deletestudent?key={{key}}&num={{num}}" class="ico del">Delete</a></td>
</tr>
'''

def AuthenticateAdmin(handle):
	session = get_current_session()
	
	if session.get('admin') == True:
		return True
	else:
		handle.redirect('password')
		return False

class AddStudent(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		key = self.request.get('key')
		meeting = Meeting.get(Key(key))
		
		name = self.request.get('student')
		
		query = User.gql("WHERE name = :1",name)
		results = query.fetch(limit=1)
		
		if len(results) > 0:
			user = results[0]
			meeting.students.append(str(user.key()))
			meeting.data.append(False)
			meeting.put()
		
		self.redirect('/admin/editmeeting?key=' + key)
		
class DeleteStudent(webapp.RequestHandler):
	def get(self):
		AuthenticateAdmin(self)
		key = self.request.get('key')
		meeting = Meeting.get(Key(key))
		
		num = int(self.request.get('num'))
		
		meeting.students.pop(num)
		meeting.data.pop(num)
		
		meeting.put()
		
		self.redirect('/admin/editmeeting?key=' + key)
		
class EditMeeting(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		key = self.request.get('key')
		desc = self.request.get('desc')
		

		
		
		meeting = Meeting.get(Key(key))
		meeting.description = desc
		
		for x in range(len(meeting.students)):
			cb = self.request.get('cb' + str(x))
			if cb == 'on':
				meeting.data[x] = True
			else:
				meeting.data[x] = False
		
		meeting.put()
		
		self.redirect('/admin/attend')
	def get(self):
		AuthenticateAdmin(self)
		values = {}
		
		key = self.request.get('key')
		meeting = Meeting.get(Key(key))
		
		students = ""
		
		num = 0
		
		for skey in meeting.students:
			user = User.get(Key(skey))
			html = studenthtml.replace("{{name}}", user.name)
			html = html.replace("{{num}}", str(num))
			html = html.replace("{{key}}", str(meeting.key()))
			
			if meeting.data[num] == True:
				html = html.replace("{{checked}}", 'checked="checked"')
			else:
				html = html.replace("{{checked}}", '')
				
			students += html
			
			num += 1
		
		values['students'] = students
		values['desc'] = meeting.description
		values['key'] = key
		
		values['date'] = meeting.date.date()
		values['type'] = meeting.tags
		values['numstudents'] = len(meeting.students)
		
		query = User.all()
		results = query.fetch(limit=1000)
		
		names=[]
		for user in results:
			names.append(user.name)
		
		values['names']=str(names).replace("u'","'")
		
		content = template.render(os.path.join(os.path.dirname(__file__), 'admin/meeting.html'),values)
		template_values = {
		'content' : content,
		'attend' : 'class="active"'
		}
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))
		

class NewMeeting(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		
		type = self.request.get('type')
		
		newmeeting = Meeting()
		newmeeting.date = datetime.datetime.now()
		newmeeting.tags = type
		newmeeting.description = ""
		
		query = User.all()
		results = query.fetch(limit=1000)
		
		tags = []
		for tag in type.split():
			tags.append(tag.lower())
			
		students = []
		data = []
		
		for user in results:
			if 'general' in tags:
				students.append(str(user.key()))
				data.append(False)
			else:
				usertags = user.tags.split()
				for usertag in usertags:
					if usertag.lower() in tags:
						students.append(str(user.key()))
						data.append(False)
						break
		
		newmeeting.students = students
		newmeeting.data = data
		
		newmeeting.put()
		
		self.redirect("/admin/attend")

class AttendPage(webapp.RequestHandler):
	def get(self):
		AuthenticateAdmin(self)
		
		values = {}
		
		query = Meeting.all()
		results = query.fetch(limit=1000)
		
		results.reverse()
		
		meetings = ""
		
		for meeting in results:
			html = meetinghtml.replace("{{date}}",str(meeting.date.date()))
			html = html.replace("{{type}}", meeting.tags)
			html = html.replace("{{key}}", str(meeting.key()))
			meetings += html
		
		values['meetings'] = meetings
		values['totalmeetings'] = len(results)
		
		content = template.render(os.path.join(os.path.dirname(__file__), 'admin/meetings.html'),values)
		template_values = {
		'content' : content,
		'attend' : 'class="active"'
		}
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))