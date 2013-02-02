from flask import Blueprint, render_template, redirect, request, session
from flask.ext.security import current_user, login_required
from confessionsplus.models import Post

posts = Blueprint('posts', __name__, template_folder="templates")
profile = Blueprint('profile', __name__, template_folder="templates")

@posts.route('/posts', subdomain="<group>")
def list(group=None):
  posts = Post.objects(group=group)
  return render_template('posts/list.html', posts=posts, group=group)

@posts.route('/posts/<slug>', subdomain="<group>")
def detail(slug, group):
  post = Post.objects(group=group, slug=slug)
  return render_template('posts/detail.html', post=post, group=group)

@profile.route('/login', subdomain="<group>")
def login(group):
  if current_user.is_authenticated():
    return redirect(request.referrer or '/posts')
  return render_template('login.html', group=group)

@profile.route('/register', methods=['GET', 'POST'], subdomain="<group>")
@profile.route('/register/<provider_id>', methods=['GET', 'POST'], subdomain="<group>")
def register(group, provider_id=None):
  if current_user.is_authenticated():
    return redirect(request.referrer or '/posts')

  if provider_id:
    provider = get_provider_or_404(provider_id)
    connection_values = session.get('failed_login_connection', None)
  else:
    provider = None
    connection_values = None

  print provider_id, provider, connection_values
  return redirect('/posts')


@profile.route('/me', subdomain="<group>")
@login_required
def me(group):
  posts = Post.objects(group=group, creator=current_user)
  return render_template('me.html', posts=posts, group=group)

