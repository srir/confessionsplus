from flask import Blueprint, render_template, request, redirect, abort, url_for, session
from flask.ext.security import current_user, login_required
from flask.ext.login import login_user
import cgi

main = Blueprint('main', __name__, template_folder="templates")
posts = Blueprint('posts', __name__, template_folder="templates")
profile = Blueprint('profile', __name__, template_folder="templates")
admin = Blueprint('admin', __name__, template_folder="templates")

from models import Comment, Post, User, facebook

@main.route('/')
def index():
  groups = Post.objects.item_frequencies('group', normalize=True)
  return render_template('index.html', groups=groups)

@main.route('/security/fblogin')
def fblogin():
  return facebook.authorize(callback=url_for('main.fblogin_authorized',
    next=request.args.get('next') or request.referrer or None,
    _external=True))

@main.route('/security/fblogin_authorized')
@facebook.authorized_handler
def fblogin_authorized(resp):
  if resp is None:
    abort(500)

  oauth_token = resp['access_token']
  session['oauth_token'] = (oauth_token, '')
  me = facebook.get('/me')
  name = me.data['name']
  email = me.data['email']
  maybe_user = User.objects(email=email)
  user = None
  if maybe_user:
    user = maybe_user.get()
    user.oauth_token = oauth_token
  else:
    user = User(name=name, email=email, oauth_token=oauth_token)
  user.save()

  login_user(user)
  return redirect(request.args.get('next') or url_for('main.index'))

@facebook.tokengetter
def get_facebook_oauth_token():
  if current_user and current_user.is_authenticated():
    return current_user.oauth_token

  return session['oauth_token']

@main.route('/group_create', methods=["GET", "POST"])
def group_create():
  if request.method == "POST":
    if request.form['group'] != "":
      user = User.objects(id=current_user.id).get_or_404()
      group = cgi.escape(request.form["group"])
      if group not in user.moderating:
        user.moderating.append(group)
        user.save()

    return redirect(url_for('posts.list', group=group))

  return render_template('group_create.html')


@posts.route('/<group>/')
def postindex(group):
  return redirect(url_for('posts.list', group=group))

@posts.route('/<group>/posts/')
def list(group):
  posts = Post.objects(group=group, archived=False, approved=True)
  return render_template('posts/list.html', posts=posts, group=group)

@posts.route('/<group>/posts/<slug>')
def detail(group, slug):
  post = Post.objects(archived=False, group=group, slug=slug).get_or_404()
  return render_template('posts/detail.html', post=post, group=group)

@posts.route('/<group>/posts/<slug>/comment', methods=["POST"])
def comment(group, slug):
  if request.form['comment'] != "":
    user = User.objects(id=current_user.id).get()
    comment_body = cgi.escape(request.form["comment"])
    post = Post.objects(slug=slug).get()
    author = user
    if "anonymous" in request.form:
      author = None
    comment = Comment(body=comment_body, author=author)
    post.comments.append(comment)
    post.save()
    return redirect(url_for('posts.detail', group=group, slug=slug))
  abort(404)

@posts.route('/<group>/posts/create', methods=['GET', 'POST'])
@login_required
def create(group):
  if request.method == "POST":
    if request.form['post'] != "":
      user = User.objects(id=current_user.id).get()
      body = cgi.escape(request.form["post"])
      post = Post(creator=user, body=body, group=group)
      post.save()
      return redirect(url_for('posts.list', group=group))

  return render_template('posts/create.html', group=group)

@profile.route('/me')
@login_required
def me():
  posts = Post.objects(creator=current_user.id)
  return render_template('me.html', posts=posts)

@admin.route('/admin/')
def admin_index():
  user = User.objects(id=current_user.id).get()
  moderating = user.moderating
  return render_template('admin/index.html', groups=moderating)

@admin.route('/admin/<group>/')
def admin_list(group):
  user = User.objects(id=current_user.id).get()
  if group not in user.moderating:
    abort(404)

  unapproved_posts = Post.objects(archived=False, approved=False, group=group)
  approved_posts = Post.objects(archived=False, approved=True, group=group)

  return render_template('admin/list.html',
    group=group,
    unapproved_posts=unapproved_posts,
    approved_posts=approved_posts)

@admin.route('/admin/<group>/settings')
def admin_settings(group):
  pass

@admin.route('/admin/<group>/posts/<slug>/approve')
def approve(group, slug):
  user = User.objects(id=current_user.id).get()
  if group not in user.moderating:
    abort(404)

  post = Post.objects(group=group, slug=slug).get_or_404()
  post.approved = True
  post.save()

  return redirect(url_for('admin.admin_list', group=group))

@admin.route('/admin/<group>/posts/<slug>/deny')
def deny(group, slug):
  user = User.objects(id=current_user.id).get()
  if group not in user.moderating:
    abort(404)

  post = Post.objects(group=group, slug=slug).get_or_404()
  post.archived = True
  post.save()

  return redirect(url_for('admin.admin_list', group=group))

