from flask import Flask, url_for
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__, static_folder="static")
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'not-secret'

app.config["MONGODB_DB"] = 'confessionsplus'
app.config["MONGODB_HOST"] = 'localhost'
app.config["MONGODB_PORT"] = 27017

app.config["SERVER_NAME"] = "confessionsplus.dev:5000"

app.config["SOCIAL_FACEBOOK"] = {
  'consumer_key': "328075160635846",
  'consumer_secret': "36a95cf8babf110ae8b6f7d49c127725"
}

app.config["SECURITY_POST_LOGIN"] = "/posts"

db = MongoEngine(app)

def register_blueprints(app):
  from confessionsplus.views import posts, profile
  app.register_blueprint(posts)
  app.register_blueprint(profile)

register_blueprints(app)

@app.context_processor
def util():
  def url_static(filename):
    if app.debug:
        return url_for('.static', filename=filename)
    else:
        return app.config['STATIC_URI'] + filename
  return dict(url_static=url_static)

if __name__ == "__main__":
  app.run()
