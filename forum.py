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

from login import *

import os
from google.appengine.ext.webapp import template

from google.appengine.ext import db

class Topic(db.Model):
	author = db.StringProperty()
	title = db.StringProperty()
	posts = db.StringListProperty()
	creationtime = db.DateTimeProperty()
	forum = db.StringProperty()
	lastposttime = db.DateTimeProperty()

class Post(db.Model):
	user = db.StringProperty()
	time = db.DateTimeProperty()
	forum = db.StringProperty()
	topic = db.StringProperty()
	content = db.TextProperty()

forumhtml = '''

			<tr> 
				<td class="row1" width="50" align="center"><img src="milkyway/imageset/forum_read.gif" width="31" height="31" alt="No unread posts" title="No unread posts" /></td> 
				<td class="row1" width="100%"> 
					
					<a class="forumlink" href="viewforum?id={{ID}}">{{NAME}}</a> 
					<p class="forumdesc">{{DESC}}</p> 
					
				</td> 
				<td class="row2" align="center"><p class="topicdetails">{{TOPICS}}</p></td> 
				<td class="row2" align="center"><p class="topicdetails">{{POSTS}}</p></td> 
				<td class="row2" align="center" nowrap="nowrap"> 
					
						<p class="topicdetails">{{LASTPOSTTIME}}</p> 
						<p class="topicdetails"><a href="profile?user={{LASTPOSTERKEY}}">{{LASTPOSTER}}</a> 
							<a href="viewtopic?key={{LASTPOST}}"><img src="milkyway/imageset/icon_topic_latest.gif" width="18" height="9" alt="View the latest post" title="View the latest post" /></a> 
						</p> 
					
				</td> 
			</tr> 
			
'''

forumslist = [
("General Discussions", "General questions and posts about Speech and Debate and tournaments as a whole.", "general"),
("PFD Forum", "Discussions about Public Forum Debate, resolutions, and evidence.", "pfd"),
("LD Forum", "Discussions about Lincoln-Douglas Debate, and how to approach the resolutions.", "ld"),
("Policy Forum", "Forum for sharing and discussion cards, as well as evidence.", "policy"),
("Congress", "Discussions about dockets and other information.", "congress"),
("Speech Events", "Discussions over the various Speech Events.", "speech")
]

class ForumPage(webapp.RequestHandler):
	def get(self):
		content = '''<br><br>
		<center><h1>You must be signed in to view the forum.</h1></center>
		<br><br><br>
		'''
		
		session = get_current_session()
		
		if session.get('user'):
			cval = {}
			
			forums = ""
			for forum in forumslist:
				html = forumhtml.replace("{{NAME}}", forum[0])
				html = html.replace("{{DESC}}", forum[1])
				html = html.replace("{{ID}}", forum[2])
				
				id = forum[2]
				
				topics = Topic.gql("WHERE forum = :1", id).fetch(limit=1000)
				
				
				
				html = html.replace("{{TOPICS}}", str(len(topics)))
				
				postsquery = Post.all().filter('forum = ', id).order("-time")
				
				posts = postsquery.fetch(limit=1000)
				
				html = html.replace("{{POSTS}}", str(len(posts)))
				
				if len(posts) > 0:
					html = html.replace("{{LASTPOSTTIME}}", str(posts[0].time))
					
					lastposter = User.get(Key(posts[0].user))
					
					html = html.replace("{{LASTPOSTER}}", lastposter.name)
					html = html.replace("{{LASTPOSTERKEY}}", posts[0].user)
					
					html = html.replace("{{LASTPOST}}", str(posts[0].topic))
					
				else:
					html = html.replace("{{LASTPOSTTIME}}", "")
					
					html = html.replace("{{LASTPOSTER}}", "")
					html = html.replace("{{LASTPOSTERKEY}}", "")
					
					html = html.replace("{{LASTPOST}}", "")
				
				forums += html
				
			cval['forums'] = forums
		
			content = template.render(os.path.join(os.path.dirname(__file__), 'forum/main.html'),cval)
				
		template_values = {
		'content' : content,
		'forum' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))
		
		
topichtml = '''
			<tr> 
				<td class="row1" width="25" align="center"><img src="milkyway/imageset/topic_read.gif" width="17" height="17" alt="No unread posts" title="No unread posts" /></td> 
				
					<td class="row1" width="25" align="center">&nbsp;</td> 
				
				<td class="row1"> 
					
					 <a title="Posted: {{FIRSTPOSTDATE}}" href="viewtopic?key={{ID}}" class="topictitle">{{NAME}}</a> 
					
				</td> 
				<td class="row2" width="130" align="center"><p class="topicauthor"><a href="profile?user={{AUTHORKEY}}">{{AUTHORNAME}}</a></p></td> 
				<td class="row1" width="50" align="center"><p class="topicdetails">{{REPLIES}}</p></td> 

				<td class="row1" width="140" align="center"> 
					<p class="topicdetails" style="white-space: nowrap;">{{LASTPOSTDATE}}</p> 
					<p class="topicdetails"><a href="profile?user={{LASTPOSTERKEY}}">{{LASTPOSTERNAME}}</a> 
						<a href="viewtopic?key={{ID}}"><img src="milkyway/imageset/icon_topic_latest.gif" width="18" height="9" alt="View the latest post" title="View the latest post" /></a> 
					</p> 
				</td> 
			</tr> 
			'''
class ViewForum(webapp.RequestHandler):
	def get(self):
		content = '''<br><br>
		<center><h1>You must be signed in to view the forum.</h1></center>
		<br><br><br>
		'''
		
		session = get_current_session()
		
		if session.get('user'):
			id = self.request.get('id')
			name = None
			
			for f in forumslist:
				if id == f[2]:
					name = f[0]
					break
			
			cval = {}
			cval['id'] = id
			cval['name'] = name
			
			topics = Topic.gql("WHERE forum = :1", id).fetch(limit=1000)
			topics.reverse()
			
			cval['numtopics'] = len(topics)
			
			topicslist = ""
			
			for topic in topics:
				html = topichtml.replace("{{NAME}}", topic.title)
				html = html.replace("{{ID}}", str(topic.key()))
				html = html.replace("{{FIRSTPOSTDATE}}", str(topic.creationtime))
				
				author = User.get(Key(topic.author))
				html = html.replace("{{AUTHORKEY}}", topic.author)
				html = html.replace("{{AUTHORNAME}}", author.name)
				
				html = html.replace("{{REPLIES}}", str(len(topic.posts)-1))
				
				lastpost = Post.get(Key(topic.posts[len(topic.posts)-1]))
				html = html.replace("{{LASTPOSTDATE}}", str(lastpost.time))
				
				lastposter = User.get(Key(lastpost.user))
				html = html.replace("{{LASTPOSTERNAME}}", lastposter.name)
				html = html.replace("{{LASTPOSTERKEY}}", lastpost.user)
				
				topicslist += html
			
			cval['topics'] = topicslist
		
			content = template.render(os.path.join(os.path.dirname(__file__), 'forum/forum.html'),cval)
				
		template_values = {
		'content' : content,
		'forum' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))
		
class NewTopic(webapp.RequestHandler):
	def post(self):
		
		session = get_current_session()
		
		user = session.get('user')
		id = self.request.get('id')
		title = self.request.get('title')
		content = self.request.get('editor1')
		
		topic = Topic()
		topic.author = user
		topic.title = title
		topic.posts = []
		topic.creationtime = datetime.datetime.now()
		topic.forum = id
		topic.lastposttime = datetime.datetime.now()
		
		topic.put()
		
		post = Post()
		post.user = user
		post.time = datetime.datetime.now()
		post.forum = id
		post.topic = str(topic.key())
		post.content = content
		post.put()
		
		topic.posts.append(str(post.key()))
		topic.put()
		
		self.redirect("viewtopic?key=" + str(topic.key()))
		
	def get(self):
		content = '''<br><br>
		<center><h1>You must be signed in to view the forum.</h1></center>
		<br><br><br>
		'''
		
		session = get_current_session()
		
		if session.get('user'):
			id = self.request.get('id')
			name = None
			
			for f in forumslist:
				if id == f[2]:
					name = f[0]
					break
			
			cval = {}
			cval['id'] = id
			cval['name'] = name
			
			topicslist = ""
		
			content = template.render(os.path.join(os.path.dirname(__file__), 'forum/newtopic.html'),cval)
				
		template_values = {
		'content' : content,
		'forum' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))
		
posttemplate = '''
	<tr> 
	
		<td class="row-post-top" align="center" valign="middle"> 
			<a name="p1"></a> 
			<b class="postauthor">{{POSTAUTHOR}}</b> 
		</td> 
		<td class="row-post-top" width="100%"> 
			<table width="100%" cellspacing="0"> 
			<tr> 
			
				<td class="gensmall" width="100%"><div style="float:left;">&nbsp;<b>Post subject:</b> {{TOPICNAME}}</div><div style="float:right;">&nbsp;<b>Posted:</b> {{POSTTIME}}&nbsp;</div></td> 
			</tr> 
			</table> 
		</td> 
	</tr> 
 
	<tr> 
		<td class="row-post-body" valign="top"> 
			
			<table cellspacing="4" width="150"> 
			
			<tr>
			<td style="float:center;">
			<center>
			<img src="http://www.gravatar.com/avatar/{{AUTHOREMAILHASH}}?d=mm" />
			</center>
			</td>
			</tr> 
			
			<tr>
			<td class="postdetails">
			<center>
			{{POSTAUTHOR}}
			</center>
			</td>
			</tr> 
			
			</table> 
		</td> 
		<td class="row-post-body" valign="top"> 
			<table width="100%" cellspacing="5"> 
			<tr> 
				<td> 
				
 
					<div class="postbody">
					
					{{POSTCONTENT}}
					
					</div> 
 
				<br clear="all" /><br /> 
 
					<table width="100%" cellspacing="0"> 
					<tr valign="middle"> 
						<td class="gensmall" align="right"> 
						
						</td> 
					</tr> 
					</table> 
				</td> 
			</tr> 
			</table> 
		</td> 
	</tr> 
 
	<tr> 
		<td class="row-post-bottom" align="center"></td> 
		<td class="row-post-bottom"><div class="gensmall" style="float:left;">&nbsp;<a href="profile?user={{AUTHORKEY}}"><img src="milkyway/imageset/en/icon_user_profile.gif" alt="Profile" title="Profile" /></a> &nbsp;</div> <div class="gensmall" style="float: right;">&nbsp;</div></td> 
	
	</tr> 
'''
		
class ViewTopic(webapp.RequestHandler):
	def get(self):
		content = '''<br><br>
		<center><h1>You must be signed in to view the forum.</h1></center>
		<br><br><br>
		'''
		
		session = get_current_session()
		
		if session.get('user'):
			key = self.request.get('key')
			cval = {}
			
			posts = ""
			
			topic = Topic.get(Key(key))
			topic.posts
			
			forumid = topic.forum
			forumname = ""
			
			for f in forumslist:
				if forumid == f[2]:
					forumname = f[0]
					break
			
			for postkey in topic.posts:
				post = Post.get(Key(postkey))
				author = User.get(Key(post.user))
				
				html = posttemplate.replace("{{POSTCONTENT}}",post.content)
				html = html.replace("{{POSTAUTHOR}}",author.name)
				
				html = html.replace("{{AUTHORKEY}}",post.user)
				html = html.replace("{{TOPICNAME}}",topic.title)
				html = html.replace("{{POSTTIME}}",str(post.time))
				
				html = html.replace("{{AUTHOREMAILHASH}}",hashlib.md5(author.email.lower()).hexdigest())
				
				posts += html
				
			cval['posts'] = posts
			cval['forumname'] = forumname
			cval['forumid'] = forumid
			cval['name'] = topic.title
			cval['key'] = key
			cval['numposts'] = len(topic.posts)
		
			content = template.render(os.path.join(os.path.dirname(__file__), 'forum/topic.html'),cval)
				
		template_values = {
		'content' : content,
		'forum' : "class='active'"
		}
		
		template_values.update(getSignInText(self.request))
		
		path = os.path.join(os.path.dirname(__file__), 'main/template.html')
		self.response.out.write(template.render(path, template_values))
		
class PostReply(webapp.RequestHandler):
	def post(self):
		session = get_current_session()
		key = self.request.get('topic')
		
		if session.get('user'):
			topic = Topic.get(Key(key))
			
			post = Post()
			post.user = session.get('user')
			post.time = datetime.datetime.now()
			post.forum = topic.forum
			post.topic = key
			post.content = self.request.get('editor1')
			post.put()
			
			topic.posts.append(str(post.key()))
			topic.put()
			
		self.redirect("viewtopic?key=" + key)