import os
import random
import hashlib
import logging

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = False)  

class BaseHandler(webapp2.RequestHandler):
    ""
    def render(self, template, **kw):
        """Handlers method which renders jinja template with
        a set of template values(kw)"""
        t = jinja_env.get_template(template) 
        self.response.out.write(t.render(kw))

class User(db.Model):
    ""
    name = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Client(BaseHandler):
    def get(self):
        template_values = {'nonce' : random.randint(1000000, 9999999)}
        self.render('login.html', **template_values)

    def post(self):
        template_values = {}
        username = self.request.get('username')
        received_hash = self.request.get('hash')
        nonce = self.request.get('nonce')
        user = User.all().filter('name =', username).get()
        if user:
            hash = hashlib.sha1(user.password + nonce).hexdigest()
        else:
            self.redirect('/')
            return
        if hash == received_hash:
            template_values['username'] = username
            self.render('loginsuccess.html', **template_values)
            return
        else:
            self.redirect('/')

class Server(BaseHandler):
    def get(self):
        template_values = {}
        self.render('server.html', **template_values)

    def post(self):
        template_values = {}
        username = self.request.get('username')
        password = self.request.get('password')
        if username and password:
            user = User(name = username, password = password)
            user.put()
            template_values['username'] = username            
        else:
            self.redirect('/server')
            return
        self.render('registrationsuccess.html', **template_values)

application = webapp2.WSGIApplication([
    ('/', Client),
    ('/server', Server),
], debug=True)