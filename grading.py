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





def AuthenticateAdmin(handle):
	session = get_current_session()
	
	if session.get('admin') == True:
		return True
	else:
		handle.redirect('password')
		return False


class AddStudent2(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		key = self.request.get('key')
		a = Assignment.get(Key(key))
		
		name = self.request.get('student')
		
		query = User.gql("WHERE name = :1",name)
		results = query.fetch(limit=1)
		
		if len(results) > 0:
			user = results[0]
			a.students.append(str(user.key()))
			a.scores.append(0)
			a.put()
		
		self.redirect('/admin/editassignment?key=' + key)
		
class DeleteStudent2(webapp.RequestHandler):
	def get(self):
		AuthenticateAdmin(self)
		key = self.request.get('key')
		a = Assignment.get(Key(key))
		
		num = int(self.request.get('num'))
		
		a.students.pop(num)
		a.scores.pop(num)
		
		a.put()
		
		self.redirect('/admin/editassignment?key=' + key)
		
		
studenthtml = '''
<tr>
	<td><h3>{{name}}</h3></td>
	<td><h3><input type="text" name="score{{num}}" value="{{score}}"></input> / {{maxscore}}</h3></td>
	<td><a href="deletestudent2?key={{key}}&num={{num}}" class="ico del">Delete</a></td>
</tr>
'''

		
class EditAssignment(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		key = self.request.get('key')
		desc = self.request.get('desc')
		name = self.request.get('aname')
		maxscore = self.request.get('maxscore')
		

		
		
		a = Assignment.get(Key(key))
		a.description = desc
		a.name = name
		a.maxscore = int(maxscore)
		
		
		for x in range(len(a.students)):
			score = int(self.request.get('score' + str(x)))
			a.scores[x] = score
				
		
		
		a.put()
		
		self.redirect('/admin/grading')
	def get(self):
		AuthenticateAdmin(self)
		values = {}
		
		key = self.request.get('key')
		assignment = Assignment.get(Key(key))
		
		students = ""
		
		num = 0
		
		for skey in assignment.students:
			user = User.get(Key(skey))
			html = studenthtml.replace("{{name}}", user.name)
			html = html.replace("{{num}}", str(num))
			html = html.replace("{{key}}", str(assignment.key()))
			
			html = html.replace("{{score}}", str(assignment.scores[num]))
			html = html.replace("{{maxscore}}", str(assignment.maxscore))
			
			students += html
			
			num += 1
		
		values['students'] = students
		values['desc'] = assignment.description
		values['key'] = key
		
		values['name'] = assignment.name
		values['maxscore'] = assignment.maxscore
		
		values['date'] = assignment.date.date()
		values['type'] = assignment.tags
		values['numstudents'] = len(assignment.students)
		
		query = User.all()
		results = query.fetch(limit=1000)
		
		names=[]
		for user in results:
			names.append(user.name)
		
		values['names']=str(names).replace("u'","'")
		
		content = template.render(os.path.join(os.path.dirname(__file__), 'admin/assignment.html'),values)
		template_values = {
		'content' : content,
		'grading' : 'class="active"'
		}
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))
		

class NewAssignment(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		
		type = self.request.get('type')
		
		new = Assignment()
		new.date = datetime.datetime.now()
		new.name = "New Assignment"
		new.tags = type
		
		new.maxscore = 0
		
		new.description = ""
		
		query = User.all()
		results = query.fetch(limit=1000)
		
		tags = []
		for tag in type.split():
			tags.append(tag.lower())
			
		students = []
		scores = []
		
		for user in results:
			if 'general' in tags:
				students.append(str(user.key()))
				scores.append(0)
			else:
				usertags = user.tags.split()
				for usertag in usertags:
					if usertag.lower() in tags:
						students.append(str(user.key()))
						scores.append(0)
						break
		
		new.students = students
		new.scores = scores
		
		new.put()
		
		self.redirect("/admin/grading")
		


meetinghtml = '''
<tr class="odd">
	<td><a href="editassignment?key={{key}}">{{name}}</a></td>
	<td>{{type}}</td>
	<td>{{avg}}</td>
	<td>{{max}}</td>
	<td><a href="#" class="ico del">Delete</a></td>
</tr>
'''

class GradingPage(webapp.RequestHandler):
	def get(self):
		AuthenticateAdmin(self)
		
		values = {}
		
		query = Assignment.all()
		results = query.fetch(limit=1000)
		
		results.reverse()
		
		assignemnts = ""
		
		for a in results:
			html = meetinghtml.replace("{{name}}",str(a.name))
			html = html.replace("{{type}}", a.tags)
			
			total = 0
			
			for s in a.scores:
				total = total + s
				
			html = html.replace("{{avg}}", str(total/len(a.scores)))
			
			html = html.replace("{{max}}", str(a.maxscore))
			
			html = html.replace("{{key}}", str(a.key()))
			assignemnts += html
		
		values['assignemnts'] = assignemnts
		values['totalassignemnts'] = len(results)
		
		content = template.render(os.path.join(os.path.dirname(__file__), 'admin/grading.html'),values)
		template_values = {
		'content' : content,
		'grading' : 'class="active"'
		}
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))