import os

from app import app, db, lm
from app import emails, functions

from app.email.models import Email
from app.follow.models import Follow

from app.media.models import Media
from app.media.choices import MediaTypeChoices

from app.thank.models import Thank, ThankReceivedByUser
from app.thank.choices import ThankReceivedByUserStatusChoices, ThankStatusChoices

from app.user.forms import (LoginForm, RegisterForm, SettingsUserPasswordChangeForm, SettingsUserProfileForm, 
    SettingsUserProfilePictureForm, SettingsUserForm)
from app.user.models import User, UserProfile

from flask import abort, render_template, flash, redirect, url_for, g, session, request
from flask.ext.login import current_user, login_user, login_required, logout_user

from config import UPLOAD_FOLDER
from datetime import datetime
from sqlalchemy import desc, or_
from werkzeug import secure_filename

# Registration -------------------------------------

@lm.user_loader
def load_user(id):
    return User.get_user(int(id))

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if g.user.is_authenticated():
        flash("You are already registered.")
        return redirect(url_for('user_thanks', username = g.user.username))
    form = LoginForm()
    if form.validate_on_submit():
            login_user(form.user, remember = form.remember_me.data)
            g.user.date_last_logged_in = datetime.utcnow()
            db.session.add(g.user)
            db.session.commit()
            return redirect(request.args.get("next") or url_for('thanks'))
    return render_template('users/login.html',
        form = form,
        title = 'Login')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('thanks'))

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    if g.user.is_authenticated():
        flash("You are already registered.")
        return redirect(url_for('user_thanks', username = g.user.username))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(password = form.new_password.data, username = form.username.data)
        db.session.add(user)
        db.session.commit()

        profile = UserProfile(user_id = user.id, name = form.name.data)
        db.session.add(profile)

        email = form.registered_email
        if email != None:
            email.is_primary = True
            email.user_id = user.id
        else:
            email = Email(email = form.email.data, is_primary = True, user_id = user.id)
        db.session.add(email)

        follow = Follow(user.id, user.id)
        db.session.add(follow)
        db.session.commit()
        
        login_user(user)
        emails.register(email)
        return redirect(url_for('user_thanks', username = g.user.username))
    return render_template('users/register.html',
        form = form,
        title = 'Register')

# Settings ---------------------------------------

@app.route('/settings/', methods = ['GET', 'POST'])
@app.route('/settings/user/', methods = ['GET', 'POST'])
@login_required
def settings_user():
    form = SettingsUserForm(g.user)
    if form.validate_on_submit():
        g.user.username = form.username.data
        db.session.add(g.user)
        db.session.commit()
        flash('Changes have been saved.')
        return redirect(url_for('settings_user'))
    else:
        form.username.data = g.user.username
    return render_template('users/settings_user.html',
        form = form,
        title = 'Account Settings for' + g.user.username)

@app.route('/settings/user/deactivate/', methods = ['GET','POST'])
@login_required
def settings_user_deactivate():
    form = LoginForm()
    if form.validate_on_submit():
        form.user.make_deactivated()
        db.session.add(form.user)
        db.session.commit()
        return logout()
    return render_template('users/settings_user_deactivate.html',
        form = form,
        title = 'Deactivate Account')

@app.route('/settings/user/password/change', methods = ['GET', 'POST'])
@login_required
def settings_user_password_change():
    form = SettingsUserPasswordChangeForm(g.user)
    if form.validate_on_submit():
        g.user.change_password(form.new_password.data)
        db.session.add(g.user)
        db.session.commit()
        flash('You have successfully changed your password.')
    return render_template("users/settings_user_password_change.html",
        form = form,
        title = "Change Password")

@app.route('/settings/user/profile/', methods = ['GET', 'POST'])
@login_required
def settings_user_profile():
    form = SettingsUserProfileForm()
    if form.validate_on_submit():
        g.user.profile.name = form.name.data
        g.user.profile.bio = form.bio.data
        g.user.profile.website = form.website.data
        db.session.add(g.user.profile)
        db.session.commit()
        flash('Changes have been saved.')
        return redirect(url_for('settings_user_profile'))
    else:
        form.name.data = g.user.profile.name
        form.bio.data = g.user.profile.bio
        form.website.data = g.user.profile.website
    return render_template('users/settings_user_profile.html',
        form = form,
        title = 'Account Settings for' + g.user.username)

@app.route('/settings/user/profile/picture/', methods = ['GET', 'POST'])
@login_required
def settings_user_profile_picture():
    form = SettingsUserProfilePictureForm()
    if form.validate_on_submit():
        # Generate new filename with path then save picture
        path = 'PROFILE_PICTURE/' + str(g.user.id) + '.' + str(datetime.utcnow()) + '.png'
        form.picture.data.save(os.path.join(UPLOAD_FOLDER, path))
        # Create Media
        media = Media(type = MediaTypeChoices.PROFILE_PICTURE, path = path)
        db.session.add(media)
        db.session.commit()
        # Upload User Profile Picture
        g.user.profile.picture_id = media.id
        db.session.add(g.user.profile)
        db.session.commit()
        # Redirect to Profile Picture Page
        return redirect(url_for('settings_user_profile_picture_redirect'))
    return render_template('users/settings_user_profile_picture.html',
        form = form,
        title = 'Profile Picture Settings')

@app.route('/settings/user/profile/picture/redirect/')
def settings_user_profile_picture_redirect():
    return redirect(url_for('settings_user_profile_picture'))

# User Pages -----------------------------------------------

@app.route('/<username>/')
@app.route('/<username>/thanks/')
def user_thanks(username = None):
    user = User.get_user_by_username(username)
    if user != None and user.is_active():
        thanks = Thank.query.join(ThankReceivedByUser)\
                            .filter(Thank.status != ThankStatusChoices.DELETED,
                                    ThankReceivedByUser.status != ThankReceivedByUserStatusChoices.DELETED,
                                    ThankReceivedByUser.status != ThankReceivedByUserStatusChoices.HIDDEN)\
                            .filter(or_(Thank.giver_id == user.id,
                                        ThankReceivedByUser.receiver_id == user.id))\
                            .order_by(desc(Thank.date_registered))\
                            .all()
        return render_template('users/user_thanks.html',
            thanks = thanks,
            user = user,
            title = user.profile.name + "'s Thanks")
    abort(404)

@app.route('/<username>/thanks-given/')
def user_thanks_given(username = None):
    user = User.get_user_by_username(username)
    if user != None and user.is_active():
        return render_template('users/user_thanks_given.html',
            Follow = Follow,
            user = user,
            thanks = user.thanks_given.order_by(desc(Thank.date_registered)).all(),
            title = 'Thanks Given by ' + user.profile.name)
    abort(404)

@app.route('/<username>/thanks-received/')
def user_thanks_received(username = None):
    user = User.get_user_by_username(username)
    if user != None and user.is_active():
        return render_template('users/user_thanks_received.html',
            Follow = Follow,
            ThankReceivedByUser = ThankReceivedByUser,
            user = user,
            thanks = user.thanks_received\
                .filter(ThankReceivedByUser.status == ThankReceivedByUserStatusChoices.VISIBLE)\
                .order_by(desc(Thank.date_registered)).all(),
            title = 'Thanks Received by ' + user.profile.name)
    abort(404)

@app.route('/<username>/following/')
def user_following(username = None):
    user = User.get_user_by_username(username)
    if user != None and user.is_active():
        return render_template('users/user_following.html',
            Follow = Follow,
            user = user,
            title = user.profile.name + " is following these pages.")
    abort(404)

@app.route('/<username>/followers/')
def user_followers(username = None):
    user = User.get_user_by_username(username)
    if user != None and user.is_active():
        return render_template('users/user_followers.html',
            Follow = Follow,
            user = user,
            title = user.profile.name + "'s Followers")
    abort(404)

# User ID Redirects ------------------------------------------

@app.route('/users/<int:user_id>/')
@app.route('/users/<int:user_id>/timeline/')
def users_user_thanks(user_id = None):
    try:
        return redirect(url_for('user_thanks', username = User.get_user(user_id).username))
    except:
        abort(404)

@app.route('/users/<int:user_id>/followers/')
def users_user_followers(user_id = None):
    try:
        return redirect(url_for('user_followers', username = User.get_user(user_id).username))
    except:
        abort(404)

@app.route('/users/<int:user_id>/following/')
def users_user_following(user_id = None):
    try:
        return redirect(url_for('user_following', username = User.get_user(user_id).username))
    except:
        abort(404)

@app.route('/users/<int:user_id>/thanks-given/')
def users_user_thanks_given(user_id = None):
    try:
        return redirect(url_for('user_thanks_given', username = User.get_user(user_id).username))
    except:
        abort(404)

@app.route('/users/<int:user_id>/thanks-received/')
def users_user_thanks_received(user_id = None):
    try:
        return redirect(url_for('user_thanks_received', username = User.get_user(user_id).username))
    except:
        abort(404)