#!/usr/bin/env python

import webapp2
import urllib
import os
import jinja2
from google.appengine.api import urlfetch
from local_settings import credentials

from os import environ
from recaptcha.client import captcha

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render())
    
    def post(self):
        message = self.request.get('message')
        tags = self.request.get('tags')

        challenge = self.request.get('recaptcha_challenge_field')
        response  = self.request.get('recaptcha_response_field')
        remoteip  = environ['REMOTE_ADDR']

        cResponse = captcha.submit(
                         challenge,
                         response,
                         credentials['recaptcha_private_key'],
                         remoteip)

        if not cResponse.is_valid:
            self.response.out.write(cResponse.error_code)
            self.redirect('/')
        
        url = 'https://graph.facebook.com/%s/feed'%(credentials['page_id'])
        data = {
        'access_token' : credentials['access_token'],
         'message' : message }
        
        response=urlfetch.fetch(url,payload=urllib.urlencode(data), method=urlfetch.POST)
        if response.status_code == 200:
            msg= response.content
            id= msg.split('_')[-1]
            template = jinja_environment.get_template('templates/result.html')
            self.response.out.write(template.render(msg=msg,id=id))
        else:
            msg= response.content
            template = jinja_environment.get_template('templates/result.html')
            self.response.out.write(template.render(msg=msg))
    
app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
