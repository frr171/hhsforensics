#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import random

import os
from google.appengine.ext.webapp import template

from google.appengine.ext.db import Key

from usermodel import *
import re
import string
import datetime

from attendancemodel import *

from attendance import *
from grading import *

from password import *

from gaesessions import *

def validateEmail(email):
	if re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", email):
		return True
	return False
	
def validateUsername(name):
	allowed = string.letters + string.digits + '_'

	return all(c in allowed for c in name)

success='''
		<!-- Message OK -->		
		<div class="msg msg-ok">
			<p><strong>Your file was uploaded succesifully!</strong></p>
			<a href="#" class="close">close</a>
		</div>
		<!-- End Message OK -->	
'''



userlist='''
<tr class="odd">
	<td><h3><a href="viewuser?key={{KEY}}">NAME</a></h3></td>
	<td>USERN</td>
	<td>EMAIL</td>
	<td>DATE</td>
	<td><a href="#" class="ico del">Delete</a></td>
</tr>
'''


pageslist = '''
<tr>
	<td><h3>{{name}}</h3></td>
	<td><a href="#" class="ico del">Delete</a><a href="editpage?key={{key}}" class="ico edit">Edit</a></td>
</tr>
'''

from pagemodel import *

class EditPage(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		
		key = self.request.get('key')
		html = self.request.get('html')
		
		page = PageCode.get(Key(key))
		
		page.html = html
		
		page.put()
		
		self.redirect("pages")
	def get(self):
		AuthenticateAdmin(self)
		
		key = self.request.get('key')
		page = PageCode.get(Key(key))
	
		values = {}
		
		values['name'] = page.name
		values['html'] = page.html
		
		template_values = {
		'content' : template.render(os.path.join(os.path.dirname(__file__), 'admin/editpage.html'),values),
		'pages' : 'class="active"'
		}
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))

class NewPage(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		
		page = PageCode()
		page.name = self.request.get('name')
		page.html = ""
		page.put()
		
		self.redirect('pages')
	
class PagesPage(webapp.RequestHandler):
	def get(self):
		AuthenticateAdmin(self)
	
		values = {}
		
		pages = ""
		
		query = PageCode.all()
		results = query.fetch(limit=1000)
		
		for page in results:
			html = pageslist.replace("{{name}}", page.name)
			html = html.replace("{{key}}", str(page.key()))
			pages += html
			
		values['pages'] = pages
		
		template_values = {
		'content' : template.render(os.path.join(os.path.dirname(__file__), 'admin/pages.html'),values),
		'pages' : 'class="active"'
		}
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))


class HomePage(webapp.RequestHandler):
	def get(self):
		AuthenticateAdmin(self)
	
		template_values = {
		'content' : template.render(os.path.join(os.path.dirname(__file__), 'admin/welcome.html'),{}),
		'home' : 'class="active"'
		}
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))
		
class UserPage(webapp.RequestHandler):
	def get(self):
		AuthenticateAdmin(self)
		
		users = ""
		
		query = User.all()
		results = query.fetch(limit=1000)
		
		odd = False
		for user in results:
			html = userlist.replace("NAME", user.name)
			html = html.replace("USERN", user.username)
			html = html.replace("EMAIL", user.email)
			html = html.replace("DATE", str(user.registerdate))
			html = html.replace("{{KEY}}", str(user.key()))
			
			users += html
		
		values = {
			'userlist' : users
		}
		content = template.render(os.path.join(os.path.dirname(__file__), 'admin/users.html'),values)
	
		template_values = {
		'content' : content,
		'user' : 'class="active"'
		}
		
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))
		
class ViewUser(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		
		key = self.request.get('key')
		type = self.request.get('type')
		
		user = User.get(Key(key))
		
		if type == 'personal':
			user.name = self.request.get('name')
			user.username = self.request.get('username')
			user.email = self.request.get('email')
			
		if type == 'able':
			user.permissions = self.request.get('perms')
			user.tags = self.request.get('tags')
			
		user.put()
		
		self.render()
		
	def get(self):
		AuthenticateAdmin(self)
		self.render()
		
	def render(self):
		key = self.request.get('key')
		user = User.get(Key(key))
		
		values = {}
		
		values['name'] = user.name
		values['username'] = user.username
		values['email'] = user.email
		
		values['perms'] = user.permissions
		values['tags'] = user.tags
		
		values['pass'] = user.password
		values['resetlink'] = "resetpassword?key=" + values['username']
		
		values['key'] = key
		
		
		query = Meeting.gql("WHERE students = :1", key)
		results = query.fetch(limit=1000)
		
		absences = []
		attendences = []
		
		for meeting in results:
			index = meeting.students.index(key)
			if meeting.data[index]:
				attendences.append(meeting)
			else:
				absences.append(meeting)
				
		numattend = len(attendences)
		numabs = len(absences)
		
		if (numattend + numabs) > 0:
		
			values['rate'] = float(numattend)*100/(float(numattend) + float(numabs))
			values['numattend'] = numattend
			values['numabs'] = numabs
		
			meetinghtml = '''
			&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Date: <a href="editmeeting?key={{key}}">{{date}}</a>&nbsp;&nbsp;&nbsp;&nbsp;Type: {{type}}<br>
			'''
		
			abs = ""
		
			for meeting in absences:
				html = meetinghtml.replace("{{date}}", str(meeting.date.date()))
				html = html.replace("{{type}}", meeting.tags)
				html = html.replace("{{key}}", str(meeting.key()))
				abs += html
			
			values['abs'] = abs
		
			attend = ""
		
			for meeting in attendences:
				html = meetinghtml.replace("{{date}}", str(meeting.date.date()))
				html = html.replace("{{type}}", meeting.tags)
				html = html.replace("{{key}}", str(meeting.key()))
				attend += html
			
			values['attend'] = attend
		
		content = template.render(os.path.join(os.path.dirname(__file__), 'admin/user.html'), values)
	
		template_values = {
		'content' : content,
		'user' : 'class="active"'
		}
		
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))
		
class ResetPassword(webapp.RequestHandler):
	def get(self):
		AuthenticateAdmin(self)
		
		key = self.request.get('key')
		user = User.get(Key(key))
		
		user.password = "TEMP"
		
		user.put()
		
		self.redirect('viewuser?key=' + key)
		
class AdminPassword(webapp.RequestHandler):
	def post(self):
		
		p1 = self.request.get('p1')
		
		errors = ""
		
		query = Password.all()
		results = query.fetch(limit=1)
		
		result = 0
		
		if len(results) > 0:
			
			
			p = sha.new()
			p.update(p1)
			pval = p.hexdigest()
			
			if results[0].password == pval:
				result = 2
			else:
				result = 0
				errors += Error("Incorrect Password")
			
		else:
			result = 1
			

		
		if result == 0:
			self.render(errors)
		if result == 1:
			session = get_current_session()
			session.regenerate_id()
			session['admin'] = True
			self.redirect("setpassword")
		if result == 2:
			session = get_current_session()
			session.regenerate_id()
			session['admin'] = True
			self.redirect("home")
		
	def get(self):
		self.render("")
		
	def render(self,error):
	
		results = PageCode.gql("WHERE name = :1", "images").fetch(limit=1)
		if len(results) > 0:
			images = results[0].html.split()
			img = images[random.randint(0,len(images)-1)]
		else:
			img = ""
	
		'''
		images = [
		"http://icanhascheezburger.files.wordpress.com/2008/04/funny-pictures-password-lolspeakeasy.jpg",
		"http://icanhascheezburger.files.wordpress.com/2011/05/funny-pictures-today-password-iz-back-rub.jpg",
		"http://icanhascheezburger.files.wordpress.com/2008/09/funny-pictures-cat-is-suspicious-of-your-intentions.jpg",
		"http://images.cheezburger.com/completestore/2009/9/18/128977704323210964.jpg"
		]
		'''
		
		
		
		
		values = {}
		
		values['img'] = img
		values['errors'] = error
		
		path = os.path.join(os.path.dirname(__file__), 'admin/password.html')
		self.response.out.write(template.render(path, values))
		
class ForumPage(webapp.RequestHandler):
	
	def get(self):
		AuthenticateAdmin(self)
		
		template_values = {
		'content' : template.render(os.path.join(os.path.dirname(__file__), 'admin/welcome.html'),{}),
		'forum' : 'class="active"'
		}
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))
		

		
class Register(webapp.RequestHandler):


	def post(self):
		AuthenticateAdmin(self)
		
		name = self.request.get('name')
		username = self.request.get('username')
		email = self.request.get('email')
		perms = self.request.get('perms')
		tags = self.request.get('tags')
		
		values = {
		'name' : name,
		'username' : username,
		'email' : email,
		'perms' : perms,
		'tags' : tags
		}
		
		error = False
		values['error'] = ""
		
		if len(username) < 4:
			values['error'] += Error("The Username Must Be Greater Than 3 Characters")
			error = True
		if validateEmail(email) == False:
			values['error'] += Error("Please Enter a Valid Email")
			error = True
		if validateUsername(username) == False:
			values['error'] += Error("The Username May Only Contain Letters, Numbers, Or Underscores")
			error = True
		
		query = User.gql("WHERE username = :1",username)
		if len(query.fetch(limit=1)) > 0:
			values['error'] += Error("This Username Is Already In Use")
			error = True
		
		if error == False:
			newuser = User()
			
			newuser.name = name
			newuser.username = username
			newuser.email = email
			
			newuser.password = "TEMP"
			newuser.registerdate = datetime.datetime.now().date()
			
			newuser.permissions = perms
			newuser.tags = tags
			
			newuser.put()
			
			self.redirect("/admin/user")
		else:
			content = template.render(os.path.join(os.path.dirname(__file__), 'admin/register.html'), values)
			template_values = {
			'content' : content,
			'user' : 'class="active"'
			}
			path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
			self.response.out.write(template.render(path, template_values))
			
class AdminLogout(webapp.RequestHandler):
	def get(self):
		session = get_current_session()
		session.terminate()
		
		self.redirect('home')
		
class AdminHomePage(webapp.RequestHandler):
	def get(self):
		self.redirect('admin/home')

bindings = [
('/admin', AdminHomePage),
('/admin/', HomePage),
('/admin/home', HomePage),


('/admin/user', UserPage),
('/admin/newuser', Register),
('/admin/viewuser', ViewUser),


('/admin/attend', AttendPage),
('/admin/newmeeting', NewMeeting),
('/admin/editmeeting', EditMeeting),
('/admin/addstudent', AddStudent),
('/admin/deletestudent', DeleteStudent),
('/admin/resetpassword', ResetPassword),

('/admin/grading', GradingPage),
('/admin/newassignment', NewAssignment),
('/admin/editassignment', EditAssignment),
('/admin/addstudent2', AddStudent2),
('/admin/deletestudent2', DeleteStudent2),


('/admin/forum', ForumPage),


('/admin/password', AdminPassword),
('/admin/setpassword', SetAdminPassword),
('/admin/logout', AdminLogout),


('/admin/pages', PagesPage),
('/admin/newpage', NewPage),
('/admin/editpage', EditPage)
]

def main():
	application = webapp.WSGIApplication(bindings, debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
