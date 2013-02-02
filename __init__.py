from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine
from flask.ext.security import Security, MongoEngineUserDatastore, login_required
from flask.ext.security import UserMixin, RoleMixin

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'not-secret'

app.config["MONGODB_DB"] = 'confessionsplus'
app.config["MONGODB_HOST"] = 'localhost'
app.config["MONGODB_PORT"] = 27017

db = MongoEngine(app)

class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.before_first_request
def create_user():
    user_datastore.create_user(email='srikrish@andrew.cmu.edu', password='password')

@app.route('/')
@login_required
def home():
  return render_template('index.html')

if __name__ == "__main__":
  app.run()
