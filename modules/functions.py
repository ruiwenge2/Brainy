from flask import session
import os, requests, json

def is_human(captcha_response):
  secret = os.getenv("captcha_secret")
  payload = {'response':captcha_response, 'secret':secret}
  response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
  response_text = json.loads(response.text)
  return response_text['success']

def loggedIn():
  if "username" in session:
    return True
  return False

def getUser():
  return session["username"]
  
def Dict(obj):
  data = {}
  for i in obj:
    data[i] = dict(obj[i])
  return data