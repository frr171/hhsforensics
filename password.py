from google.appengine.ext import db

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from google.appengine.ext.webapp import template

import os

import datetime

import re
import sha
import string

from gaesessions import get_current_session

def AuthenticateAdmin(handle):
	session = get_current_session()
	
	if session.get('admin') == True:
		return True
	else:
		handle.redirect('password')
		return False

error='''
		<!-- Message Error -->
		<div class="msg msg-error">
			<p><strong>ERRORMSG</strong></p>
			<a href="#" class="close">close</a>
		</div>
		<!-- End Message Error -->
'''

def Error(msg):
	return error.replace("ERRORMSG",msg)

class Password(db.Model):
	password = db.StringProperty()
	
class SetAdminPassword(webapp.RequestHandler):
	def post(self):
		AuthenticateAdmin(self)
		
		p1 = self.request.get('pass1')
		p2 = self.request.get('pass2')
		
		error = False
		errors = ""
		
		if p1 != p2:
			error = True
			errors += Error("Passwords did not match")
		else:
			p = sha.new()
			p.update(p1)
			pval = p.hexdigest()
			
			query = Password.all()
			results = query.fetch(limit=1)
			if len(results) > 0:
				password = results[0]
				password.password = pval
				password.put()
			else:
				password = Password()
				password.password = pval
				password.put()

		
		values = {}
		values['errors'] = errors
		
		if error == True:
			self.render(values)
		else:
			self.redirect("password")
			
	def get(self):
		AuthenticateAdmin(self)
		self.render({})
		
	def render(self, values):
		
		content = template.render(os.path.join(os.path.dirname(__file__), 'admin/setpassword.html'),values)
		
		template_values = {
		'content' : content
		}
		
		path = os.path.join(os.path.dirname(__file__), 'admin/template.html')
		self.response.out.write(template.render(path, template_values))