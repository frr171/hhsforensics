from gaesessions import SessionMiddleware
import os.path

def webapp_add_wsgi_middleware(app):
	key = open(os.path.dirname(__file__) + '/cookiekey.txt').read()
	
	app = SessionMiddleware(app, cookie_key = key)
	return app