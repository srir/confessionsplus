import datetime
from flask import url_for
from confessionsplus import app, db
from flask.ext.security import Security, MongoEngineUserDatastore
from flask.ext.security import UserMixin, RoleMixin
from flask.ext.social import Social
from flask.ext.social.datastore import MongoEngineConnectionDatastore

class Role(db.Document, RoleMixin):
  name = db.StringField(max_length=80, unique=True)
  description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
  email = db.StringField(max_length=255)
  password = db.StringField(max_length=255)
  active = db.BooleanField(default=True)
  roles = db.ListField(db.ReferenceField(Role, dbref=False), default=[])

class Connection(db.Document):
  user = db.ReferenceField(User, required=True, dbref=False)
  provider_id = db.StringField(max_length=255)
  provider_user_id = db.StringField(max_length=255)
  access_token = db.StringField(max_length=255)
  secret = db.StringField(max_length=255)
  display_name = db.StringField(max_length=255)
  profile_url = db.StringField(max_length=512)
  image_url = db.StringField(max_length=512)
  rank = db.IntField()

class Post(db.Document):
  created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
  creator = db.ReferenceField(User, dbref=False, required=True)
  slug = db.StringField(max_length=255, required=True)
  body = db.StringField(required=True)
  group = db.StringField(required=True)
  comments = db.ListField(db.EmbeddedDocumentField('Comment'))

  def get_absolute_url(self):
    return url_for('posts.detail', kwargs={"slug": self.slug})

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
  anonymous = db.BooleanField(default=False, required=True)
  author = db.ReferenceField(User, dbref=False)

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)
social = Social(app, MongoEngineConnectionDatastore(db, Connection))
