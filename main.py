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

import sys

from attendancemodel import *

from gaesessions import *

from pagemodel import *

from google.appengine.api import urlfetch

from xml.dom.minidom import *

from login import *

from forum import *

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
	
class EventsPage(webapp.RequestHandler):
	def get(self):
		type = self.request.get("event")
		if type == "":
			type = "pfd"
			
		cval = {}
			
		results = PageCode.gql("WHERE name = :1", type).fetch(limit=1)
		if len(results) > 0:
			cval['page'] = results[0].html
		
		cval[type] = 'style="background-color:#E0F2F7;"'
		
		content = template.render(os.path.join(os.path.dirname(__file__), 'main/events.html'),cval)
			
		template_values = {
		'content' : content,
		'events' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))
	
class PhotosPage(webapp.RequestHandler):
	def get(self):
	
		content = ""
		
		results = PageCode.gql("WHERE name = :1", "photos").fetch(limit=1)
		if len(results) > 0:
			content += results[0].html
			
		template_values = {
		'content' : content,
		'photos' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))
		
class DocsPage(webapp.RequestHandler):
	def get(self):
	
		content = ""
		
		results = PageCode.gql("WHERE name = :1", "docs").fetch(limit=1)
		if len(results) > 0:
			content += results[0].html
			
		template_values = {
		'content' : content,
		'docs' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))
	
class AboutPage(webapp.RequestHandler):
	def get(self):
	
		content = ""
		
		results = PageCode.gql("WHERE name = :1", "about").fetch(limit=1)
		if len(results) > 0:
			content += results[0].html
			
		template_values = {
		'content' : content,
		'aboutus' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))
		
class ContactPage(webapp.RequestHandler):
	def get(self):
	
		content = ""
		
		results = PageCode.gql("WHERE name = :1", "contact").fetch(limit=1)
		if len(results) > 0:
			content += results[0].html
			
		template_values = {
		'content' : content,
		'contact' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))

class CalendarPage(webapp.RequestHandler):
	def get(self):
	
		template_values = {
		'content' : template.render(os.path.join(os.path.dirname(__file__), 'main/calendar.html'),{}),
		'calendar' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))



class HomePage(webapp.RequestHandler):
	def get(self):
	
		header = ""
		content = ""
		
		results = PageCode.gql("WHERE name = :1", "slider").fetch(limit=1)

		if len(results) > 0:
			header += results[0].html
			
			
		results = PageCode.gql("WHERE name = :1", "events").fetch(limit=1)

		if len(results) > 0:
			content += results[0].html
		
			
		cval = {}
		c1 = "<h2>Recent News <img src='icons/feed.png'></img></h2><hr>"
		c2 = "<h2>Upcoming Events <img src='icons/calendar.png'></img></h2><hr>"
		
		eventhtml = '''
		<p>
		<h3 style="display: inline;">Event Name: {{NAME}}</h3> <br>
		<strong>Date:</strong> {{DATE}}<br>
		<strong>Description:</strong><br>{{DESC}}<br>
		<strong>Location:</strong> {{WHERE}}
		</p>
		'''
		try:
		
			calendarurl = "http://www.google.com/calendar/ical/hamiltonforensics.net_8iq75b8enqrro2pd1nkej04unc%40group.calendar.google.com/private-50f411f82971bce5a7c43106b4e0f37d/basic.ics"
			
			calendardata = urlfetch.fetch(calendarurl)
			if calendardata.status_code == 200:
				lines = calendardata.content.splitlines()
				
				x = 0
				
				events = 0
				
				eventlist = []
				
				while x < len(lines):
					if lines[x] == "BEGIN:VEVENT":
						name = ""
						desc = ""
						date = datetime.datetime.now().date()
						loc = ""
						old = False
						
						while lines[x] != "END:VEVENT":
							line = lines[x]
							
							if "SUMMARY:" in line:
								name = line[line.index(":") + 1 :]
							if "LOCATION:" in line:
								loc = line[line.index(":") + 1 :]
							if "DTEND;VALUE=DATE:" in line:
								raw = line[line.index(":") + 1 :]
								date = datetime.date(int(raw[0:4]),int(raw[4:6]),int(raw[6:8]))
								if date < datetime.datetime.now().date():
									old = True
									break
							if "DESCRIPTION:" in line:

								while "LAST-MODIFIED:" not in lines[x]:
									desc += lines[x]
									x+=1
									
								desc = desc[desc.index(":") + 1 :]
								desc = desc.replace("\\n", "<br>")
								desc = desc.replace("\\ n", "<br>")
							x+= 1
						
						if old == False:
							html = eventhtml.replace("{{NAME}}",name)
							html = html.replace("{{DATE}}", str(date))
							html = html.replace("{{DESC}}", desc)
							html = html.replace("{{WHERE}}", loc)
						
							#c2 += html
							eventlist.append( html)
							
							events += 1
					x += 1
						
			events = 0
			
			
			eventlist.reverse()
			
			for event in eventlist:
				c2 += event
				
				events += 1
				
				if events >= 5:
					break
					
		except:
			pass
				
		c2 += '<p><a href="calendar" class="more">See Calendar</a></p>'
		
		entryhtml = '''
		<br>
		<h2>{{TITLE}}</h2>
		&nbsp;&nbsp;&nbsp; by <strong>{{AUTHOR}}</strong> on <strong>{{DATE}}</strong><br>
		<br>
		{{CONTENT}}
		<div align="right"><a href="{{COMMLINK}}"><img src='icons/balloon.png'></img> {{COMM}}</a></div>
		'''
		
		
		
		try:
			blogurl = "http://news.hamiltonforensics.net/feeds/posts/default"
			blogdata = urlfetch.fetch(blogurl)
			
			if blogdata.status_code == 200:
				dom = parseString(blogdata.content)
				
				entries = dom.getElementsByTagName("entry")
				
				posts = 0
				
				
				for entry in entries:
					title = getText(entry.getElementsByTagName("title")[0].childNodes)
					postcontent = getText(entry.getElementsByTagName("content")[0].childNodes)
					author = getText(entry.getElementsByTagName("author")[0].getElementsByTagName("name")[0].childNodes)
					date = getText(entry.getElementsByTagName("published")[0].childNodes).split("T")[0]
					
					comm = entry.getElementsByTagName("link")[1].getAttribute('title')
					
					commlink = entry.getElementsByTagName("link")[1].getAttribute('href')
					
					html = entryhtml.replace("{{TITLE}}", title)
					html = html.replace("{{CONTENT}}", postcontent)
					html = html.replace("{{AUTHOR}}", author)
					html = html.replace("{{DATE}}", date)
					html = html.replace("{{COMM}}", comm)
					html = html.replace("{{COMMLINK}}", commlink)
					
					c1 += html
					
					posts += 1
					
					if posts >= 2:
						break
		except:
			pass
		
		
		c1 += '<br><p><a href="http://news.hamiltonforensics.net" class="more">See More Posts</a></p>'
		
		text = c1
		newtext = ""
		
		for i in text:
			if ord(i) > 127:
				newtext = newtext + ""
			else:
				newtext = newtext + i
		
		
		cval['c1'] = newtext
		cval['c2'] = str(c2)
		content += template.render(os.path.join(os.path.dirname(__file__), 'main/twocolumn.html'),cval)
			
		
		template_values = {
		'content' : content,
		'header' : header,
		'home' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))
		
class ViewProfile(webapp.RequestHandler):
	def get(self):
		content = '''<br><br>
		<center><h1>You must be signed in to view a profile.</h1></center>
		<br><br><br>
		'''
		
		session = get_current_session()
		
		if session.get('user'):
			key = ""
			
			if self.request.get("user"):
				key = self.request.get("user")
			else:
				key = session.get('user')
				
			isSelf = (key == session.get('user'))
			
			cval = {}
			
			user = User.get(Key(key))
			
			cval['name'] = user.name
			cval['emailhash'] = hashlib.md5(user.email.lower()).hexdigest()
			
			
			
			if isSelf:
				query = Meeting.gql("WHERE students = :1", key)
				results = query.fetch(limit=1000)
				
				cval['email'] = user.email
				cval['tags'] = user.tags
				
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
				
					cval['rate'] = float(numattend)*100/(float(numattend) + float(numabs))
					cval['numattend'] = numattend
					cval['numabs'] = numabs
				
					meetinghtml = '''
					&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Date: {{date}}&nbsp;&nbsp;&nbsp;&nbsp;Type: {{type}}<br>
					'''
				
					abs = ""
				
					for meeting in absences:
						html = meetinghtml.replace("{{date}}", str(meeting.date.date()))
						html = html.replace("{{type}}", meeting.tags)
						html = html.replace("{{key}}", str(meeting.key()))
						abs += html
					
					cval['abs'] = abs
				
					attend = ""
				
					for meeting in attendences:
						html = meetinghtml.replace("{{date}}", str(meeting.date.date()))
						html = html.replace("{{type}}", meeting.tags)
						html = html.replace("{{key}}", str(meeting.key()))
						attend += html
					
					cval['attend'] = attend
		
			content = template.render(os.path.join(os.path.dirname(__file__), 'main/profile.html'),cval)
				
		template_values = {
		'content' : content,
		'profile' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))

bindings = [
('/', HomePage),
('/calendar', CalendarPage),
('/aboutus', AboutPage),
('/contact', ContactPage),
('/photos', PhotosPage),

('/docs', DocsPage),

('/events', EventsPage),
('/login', LoginPage),
('/logout', LogoutPage),
('/setpassword', SetPassword),
('/forum', ForumPage),
('/viewforum', ViewForum),
('/newtopic', NewTopic),
('/viewtopic', ViewTopic),
('/postreply', PostReply),
('/profile', ViewProfile)
]

def main():
	application = webapp.WSGIApplication(bindings, debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
