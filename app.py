from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.csrf import csrf
from flask_oauth import OAuth

app = Flask(__name__, static_folder="static")
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'not-secret'

app.config["MONGODB_DB"] = 'confessionsplus'
app.config["MONGODB_HOST"] = 'localhost'
app.config["MONGODB_PORT"] = 27017

app.config["FACEBOOK_APP_ID"] = "328075160635846"
app.config["FACEBOOK_APP_SECRET"] = "36a95cf8babf110ae8b6f7d49c127725"

app.config["SECURITY_REGISTERABLE"] = True

app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
app.config["SECURITY_PASSWORD_SALT"] = "salty"
app.config["SECURITY_POST_LOGIN"] = "/"
app.config["SECURITY_POST_LOGOUT"] = "/"

oauth = OAuth()
db = MongoEngine(app)
csrf(app)

def register_blueprints(app):
  from views import posts, profile, main, admin
  app.register_blueprint(main)
  app.register_blueprint(posts)
  app.register_blueprint(profile)
  app.register_blueprint(admin)

register_blueprints(app)

if __name__ == "__main__":
  app.run()
