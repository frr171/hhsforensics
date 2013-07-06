from google.appengine.ext.db import Key
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from usermodel import *
import re
import string
import datetime
import sha
import hashlib
import urllib

from gaesessions import *

import os
from google.appengine.ext.webapp import template

error='''
		<!-- Message Error -->
		<div class="msg msg-error">
			<p><strong>ERRORMSG</strong></p>
		</div>
		<!-- End Message Error -->
'''

def Error(msg):
	return error.replace("ERRORMSG",msg)

def getSignInText(request):
	session = get_current_session()
	
	values = {}
	values['signin'] = """You are not signed in.<br><a href="javascript: $( '#dialog-form' ).dialog( 'open' ); void(0);">Click here</a> to sign in."""
	
	
	if session.get('user'):
		user = User.get(Key(session.get('user')))
		
		url = urllib.urlencode({'url' : request.url})
		
		values['signin'] = "You are currently signed<br>in as <a href='profile'>" + user.name + "</a>.<br><a href='logout?" + url + "'>Click here</a> to sign out."
		values['emailhash'] = hashlib.md5(user.email.lower()).hexdigest()
		
	values['url'] = urllib.urlencode({'url' : request.url})
	
	return values
	
class LoginPage(webapp.RequestHandler):
	def post(self):
		name = self.request.get('name')
		password = self.request.get('password')
		url = self.request.get('url')
		
		p = sha.new()
		p.update(password)
		pval = p.hexdigest()
		
		session = get_current_session()
		
		results = User.gql("WHERE username = :1", name).fetch(limit=1)
		
		if len(results) > 0:
			if pval == results[0].password:
				session.regenerate_id()
				session['user'] = str(results[0].key())
				self.redirect(url)
			else:
				if results[0].password == "TEMP":
					session.regenerate_id()
					session['user'] = str(results[0].key())
					self.redirect("/setpassword")
				else:
					self.redirect(url)
		else:
			self.redirect(url)
				
class LogoutPage(webapp.RequestHandler):
	def get(self):
		url = self.request.get('url')
		
		
		session = get_current_session()
		session.terminate()
		
		self.redirect(url)
		
class SetPassword(webapp.RequestHandler):
	def post(self):
		p1 = self.request.get('p1')
		p2 = self.request.get('p2')
		
		error = False
		errors = ""
		
		if p1 != p2:
			error = True
			errors += Error("Passwords did not match")
			
			self.render(errors)
		else:
			p = sha.new()
			p.update(p1)
			pval = p.hexdigest()
			
			session = get_current_session()
			user = User.get(Key(session.get('user')))
			
			user.password = pval
			user.put()
			
			self.redirect("/")
			
	def get(self):
		self.render("")
		
	def render(self, errors):
		cval = {}
		
		cval['errors'] = errors
		
		template_values = {
		'content' : template.render(os.path.join(os.path.dirname(__file__), 'main/setpassword.html'),cval)
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))