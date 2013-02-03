import datetime
import shortuuid
from confessionsplus import app, db, oauth
from flask.ext.security import Security, MongoEngineUserDatastore
from flask.ext.security import UserMixin, RoleMixin

class Role(db.Document, RoleMixin):
  name = db.StringField(max_length=80, unique=True)
  description = db.StringField(max_length=80)

class User(db.Document, UserMixin):
  name = db.StringField(max_length=255)
  email = db.StringField(max_length=255)
  password = db.StringField(max_length=255)
  oauth_token = db.StringField(max_length=512)
  active = db.BooleanField(default=True)
  roles = db.ListField(db.ReferenceField(Role, dbref=False), default=[])
  moderating = db.ListField(db.StringField())
  subscribed = db.ListField(db.StringField())

def create_slug():
  return shortuuid.uuid()[:8]

class Post(db.Document):
  created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
  creator = db.ReferenceField(User, dbref=False, required=True)
  slug = db.StringField(default=create_slug, max_length=255, required=True)
  body = db.StringField(required=True)
  group = db.StringField(required=True)
  comments = db.ListField(db.EmbeddedDocumentField('Comment'))
  approved = db.BooleanField(default=False)
  archived = db.BooleanField(default=False)

  def __unicode__(self):
    return self.body

  meta = {
    'allow_inheritance': True,
    'indexes': ['-created_at', 'slug'],
    'ordering': ['-created_at']
  }

class Comment(db.EmbeddedDocument):
  created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
  body = db.StringField(verbose_name="Comment", required=True)
  author = db.ReferenceField(User, dbref=False, required=False)

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=app.config["FACEBOOK_APP_ID"],
    consumer_secret=app.config["FACEBOOK_APP_SECRET"],
    request_token_params={'scope': 'email'}
)

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)
app.extensions['security']._send_mail_task = lambda x: True
