from app import app, db
from app import emails
from app.follow.models import Follow
from app.user.models import User

from flask import g, redirect, url_for
from flask.ext.login import login_required

@app.route('/settings/follows/<int:followed_id>/follow')
@login_required
def follows_followed_follow(followed_id):
    user = User.get_user(followed_id)
    if user != None and not user.is_deleted():
        if not Follow.is_following_by_follower_and_followed(g.user.id, user.id):
            follow = Follow(g.user.id, user.id)
            db.session.add(follow)
            db.session.commit()
            emails.follower_notification(g.user, user)
        return redirect(url_for('user_thanks', username = user.username))
    abort(404)

@app.route('/settings/follows/<int:followed_id>/unfollow')
@login_required
def follows_followed_unfollow(followed_id):
    user = User.get_user(followed_id)
    if user != None and not user.is_deleted():
        follow = Follow.get_follow_by_follower_and_followed(g.user.id, user.id)
        if follow != None:
            follow.make_deleted()
            db.session.add(follow)
            db.session.commit()
        return redirect(url_for('user_thanks', username = user.username))
    abort(404)