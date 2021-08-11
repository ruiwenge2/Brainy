from flask import Flask, session, request, render_template, redirect, make_response
from flask_cors import CORS, cross_origin
from replit import db
from shortuuid import ShortUUID
from modules import *
import os

app = Flask("app", static_url_path="")
cors = CORS(app, resources={r"/*/*/json": {"origins": "*"}})
app.config["SECRET_KEY"] = os.getenv("secretkey")

@app.route("/")
def index():
  if loggedIn():
    recent = list(db[getUser()]["surveys"].keys())
    recent.reverse()
    recentlength = len(recent)
    if recentlength > 3:
      recent = [recent[0], recent[1], recent[2]]
    return render_template("index.html", loggedIn=True, username=getUser(), recent=recent, recentlength=recentlength)
  return render_template("index.html", loggedIn=False)

@app.route("/login")
def login():
  return redirect("/") if loggedIn() else render_template("login.html", error=False)

@app.route("/login", methods=["GET", "POST"])
def loginsubmit():
  if loggedIn():
    return redirect("/")
  if request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]
    if username not in db.keys() or db[username]["password"] != password:
      return render_template("login.html", error="Invalid username and/or password.")
    session["username"] = username
    return redirect("/")

@app.route("/signup")
def signup():
  return redirect("/") if loggedIn() else render_template("signup.html", error=False)

@app.route("/signup", methods=["GET", "POST"])
def createaccount():
  if loggedIn():
    return redirect("/")
  if request.method == "POST":
    newusername = request.form["newusername"]
    newpassword = request.form["newpassword"]
    captcha_response = request.form["g-recaptcha-response"]
    print(newusername)
    for i in newusername:
      if i not in allchars:
        return render_template("signup.html", error="Username can only contain alphanumeric characters and underscores.")
    if newusername in db.keys():
      return render_template("signup.html", error="Username taken.")
    if newusername == "" or newpassword == "":
      return render_template("signup.html", error="All fields are required.")
    if is_human(captcha_response):
      db[newusername] = {
        "password":newpassword,
        "surveys":{}
      }
      session["username"] = newusername
      print("new account created")
      return redirect("/")
    else:
      print("not verified")
      return render_template("signup.html", error="No bots allowed!")

@app.route("/surveys")
def surveys():
  if not loggedIn():
    return redirect("/login")
  allsurveys = list(db[getUser()]["surveys"].keys())
  allsurveys.reverse()
  return render_template("survey/surveys.html", surveys=allsurveys, username=getUser(), loggedIn=True)

@app.route("/newsurvey", methods=["GET", "POST"])
def newsurvey():
  if not loggedIn():
    return redirect("/")
  if request.method == "POST":
    name = request.json["name"]
    if len(db[getUser()]["surveys"]) >= max_surveys:
      print("sss")
      return "You have reached the limit for the number of surveys you can create."
    for i in name:
      if i not in allchars + ["-"]:
        return "The name can only contain alphanumeric characters, dashes, and underscores."
    if name in db[getUser()]["surveys"]:
      return "This survey already exists."
    if len(name) > max_survey_length:
      return "The name cannot have more than 20 characters."
    db[getUser()]["surveys"][name] = {
      "public":True,
      "ended":False,
      "inputfields":[],
      "apikey":ShortUUID().random(),
      "data":{}
    }
    return "Success"

@app.route("/<username>/<survey>/dashboard")
def dashboard(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  if not loggedIn():
    return redirect("/login")
  if getUser() != username:
    return render_template("404.html", loggedIn=loggedIn()), 404
  info = db[username]["surveys"][survey]
  return render_template("survey/dashboard.html", data=dict(info["data"]), ended=info["ended"], public=info["public"], inputfields=list(info["inputfields"]), loggedIn=True, length=len(info["inputfields"]), survey=survey)

@app.route("/<username>/<survey>/json")
@cross_origin()
def json(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  info = db[username]["surveys"][survey]
  if not info["public"]:
    if not loggedIn():
      return redirect("/login")
    if getUser() != username:
      return render_template("404.html", loggedIn=loggedIn()), 404
  resp = make_response(Dict(info["data"]))
  resp.mimetype = "application/json"
  return resp

@app.route("/<username>/<survey>/downloadjson")
def downloadjson(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  info = db[username]["surveys"][survey]
  if not info["public"]:
    if not loggedIn():
      return redirect("/login")
    if getUser() != username:
      return render_template("404.html", loggedIn=loggedIn()), 404
  resp = make_response(Dict(info["data"]))
  resp.mimetype = "application/json"
  resp.headers['Content-Disposition'] = f"attachment; filename={survey}.json"
  return resp

@app.route("/<username>/<survey>/csv")
def csv(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  info = db[username]["surveys"][survey]
  if not loggedIn():
    return redirect("/login")
  if getUser() != username:
    return render_template("404.html", loggedIn=loggedIn()), 404
  lines = []
  fields = list(info["inputfields"])
  fields = ["#"] + fields
  fields = ", ".join(fields)
  lines.append(fields)
  for i in info["data"]:
    line = list(dict(info["data"][i]).values())
    line = [i] + line
    line = ", ".join(line)
    lines.append(line)
  total = "\n".join(lines)
  resp = make_response(total)
  resp.mimetype = "text/csv"
  resp.headers['Content-Disposition'] = f"attachment; filename={survey}.csv"
  return resp

@app.route("/<username>/<survey>/rename", methods=["GET", "POST"])
def rename(username, survey):
  if request.method == "POST":
    if username not in db.keys() or survey not in db[username]["surveys"]:
      return render_template("404.html", loggedIn=loggedIn()), 404
    if not loggedIn() or getUser() != username:
      return render_template("404.html", loggedIn=loggedIn()), 404
    name = request.json["name"]
    for i in name:
      if i not in allchars + ["-"]:
        return "The name can only contain alphanumeric characters, dashes, and underscores."
    if name in db[getUser()]["surveys"]:
      return "This survey already exists."
    if len(name) > 20:
      return "The name cannot have more than 20 characters."
    info = db[username]["surveys"][survey]
    del db[username]["surveys"][survey]
    db[username]["surveys"][name] = info
    return "Success"

@app.route("/<username>/<survey>/delete", methods=["GET", "POST"])
def delete(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  if not loggedIn() or getUser() != username:
    return render_template("404.html", loggedIn=loggedIn()), 404
  if request.method == "POST":
    del db[username]["surveys"][survey]
    return "Success"

@app.route("/<username>/<survey>/script")
def script(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  resp = make_response(render_template("survey/script.js", apikey=db[username]["surveys"][survey]["apikey"]))
  resp.mimetype = "text/javascript"
  return resp

@app.route("/<username>/<survey>/submit", methods=["GET", "POST"])
def submit(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  if request.method == "POST":
    info = db[username]["surveys"][survey]
    form = dict(request.form)
    if info["ended"]:
      print("survey already ended")
      return {"success":"false", "error":"Survey has already been ended."}
    if "apikey" not in form or form["apikey"] != info["apikey"]:
      print("invalid api key")
      return {"success":"false", "error":"Invalid API key."}
    redirectvar = False
    if "redirecturl" in form:
      redirecturl = form["redirecturl"]
      del form["redirecturl"]
      redirectvar = True
    for i in form.copy():
      if i not in info["inputfields"]:
        del form[i]
    for i in info["inputfields"]:
      if i not in form:
        print("missing input fields")
        return {"success":"false", "error":"Missing input fields"}
    number = len(info["data"]) + 1
    db[username]["surveys"][survey]["data"][number] = form
    db[username]["surveys"][survey]["apikey"] = ShortUUID().random()
    if redirectvar:
      return redirect(redirecturl)
    return {"success":"true"}
  return render_template("404.html", loggedIn=loggedIn()), 404

@app.route("/<username>/<survey>/inputfields", methods=["PUT", "PATCH", "DELETE"])
def update(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  if not loggedIn() or getUser() != username:
    return render_template("404.html", loggedIn=loggedIn()), 404
  info = db[username]["surveys"][survey]
  if request.method == "PUT":
    name = request.json["name"]
    if name in info["inputfields"]:
      return "This input field already exists."
    if name == "apikey" or name == "redirecturl":
      return "That cannot be the name."
    if len(name) > max_input_length:
      return "The name cannot have more than 20 characters."
    db[username]["surveys"][survey]["inputfields"].append(name)
    for i in db[username]["surveys"][survey]["data"]:
      db[username]["surveys"][survey]["data"][i][name] = "None"
    return "Success"
  elif request.method == "PATCH":
    name = request.json["name"]
    newname = request.json["newname"]
    if name not in info["inputfields"]:
      return "That input field doesn't exist."
    if newname in info["inputfields"]:
      return "The new input field already exists."
    if newname == "apikey" or newname == "redirecturl":
      return "That cannot be the name."
    if len(newname) > max_input_length:
      return "The name cannot have more than 20 characters."
    db[username]["surveys"][survey]["inputfields"].remove(name)
    db[username]["surveys"][survey]["inputfields"].append(newname)
    for i in db[username]["surveys"][survey]["data"]:
      value = db[username]["surveys"][survey]["data"][i][name]
      del db[username]["surveys"][survey]["data"][i][name]
      db[username]["surveys"][survey]["data"][i][newname] = value
    return "Success"
  elif request.method == "DELETE":
    name = request.json["name"]
    if name not in info["inputfields"]:
      return "That input field doesn't exist."
    db[username]["surveys"][survey]["inputfields"].remove(name)
    for i in db[username]["surveys"][survey]["data"]:
      del db[username]["surveys"][survey]["data"][i][name]
    return "Success"

@app.route("/<username>/<survey>/change", methods=["PATCH", "PUT"])
def changesettings(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  if not loggedIn() or getUser() != username:
    return render_template("404.html", loggedIn=loggedIn()), 404
  info = db[username]["surveys"][survey]
  if request.method == "PATCH":
    if info["public"]:
      db[username]["surveys"][survey]["public"] = False
    else:
      db[username]["surveys"][survey]["public"] = True
    return "Success"
  elif request.method == "PUT":
    db[username]["surveys"][survey]["ended"] = True
    return "Success"

@app.route("/<username>/<survey>/code")
def code(username, survey):
  if username not in db.keys() or survey not in db[username]["surveys"]:
    return render_template("404.html", loggedIn=loggedIn()), 404
  info = db[username]["surveys"][survey]
  if not loggedIn():
    return redirect("/login")
  if getUser() != username:
    return render_template("404.html", loggedIn=loggedIn()), 404
  return render_template("help/code.html", survey=survey, username=username, inputfields=info["inputfields"], loggedIn=loggedIn())

@app.route("/docs")
def docs():
  return render_template("help/docs.html", loggedIn=loggedIn())

@app.route("/logout")
def logout():
  del session["username"]
  return redirect("/")

@app.route(os.getenv("path"))
def path():
  resp = make_response(str(dict(db)))
  resp.mimetype = "application/json"
  return resp

@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html", loggedIn=loggedIn()), 404

app.run(host="0.0.0.0", port=8080)