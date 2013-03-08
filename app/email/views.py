from app import app, lm, db
from app import functions, emails

from app.email.models import Email
from app.email.forms import SettingsEmailsForm

from app.thank.models import Thank
from app.user.forms import LoginForm

from datetime import datetime

from flask import flash, redirect, render_template, request, g, url_for
from flask.ext.login import login_required, login_user

@app.route('/settings/emails/', methods = ['GET', 'POST'])
@login_required
def settings_emails():
    form = SettingsEmailsForm()
    if form.validate_on_submit():
        return redirect(url_for('settings_emails_email_add', email = form.email.data))
    return render_template('users/settings_emails.html',
        form = form, 
        title = 'Manage Emails')

@app.route('/settings/emails/<email>/add/')
@login_required
def settings_emails_email_add(email):
    if functions.is_email(email):
        email_object = Email.get_email_by_email(email)
        if email_object == None or email_object.user_id == None:
            email = Email(email = email, user_id = g.user.id)
            db.session.add(email)
            db.session.commit()
            emails.settings_emails_email_add(email)
            flash('%s has been successfully added.' % (email.email)) 
        else:
            if email_object.user == g.user:
                flash('%s is already added.' % (email_object.email)) 
            else:
                flash('%s registered by another user.' % (email_object.email)) 
    return redirect(url_for('settings_emails'))

@app.route('/settings/emails/<email>/delete/')
@login_required
def settings_emails_email_delete(email):
    if functions.is_email(email):
        email = Email.get_email_by_email(email)
        if email == None:
            flash('Unregistered email cannot be deleted.')
        elif email not in g.user.emails:
            flash('%s is not your email. You cannot delete it.' % (email.email)) 
        elif email.is_primary:
            flash('%s is your primary email. It cannot be deleted.' % (email.email))
        else:
            email.make_deleted()
            db.session.add(email)
            db.session.commit()
            flash('%s has been successfully deleted.' % (email.email))
    return redirect(url_for('settings_emails'))

@app.route('/settings/emails/<email>/make-primary/')
@login_required
def settings_emails_email_make_primary(email):
    if functions.is_email(email):
        email = Email.get_email_by_email(email)
        if email == None:
            flash('Unregistered email cannot be primary email.')
        elif email not in g.user.emails:
            flash('%s is not registered by your account.' % (email.email))
        elif email.is_primary:
            flash('%s is already your primary email.' % (email.email))
        elif email.is_not_verified():
            flash('%s is not a verified email. Please verify to make primary.' % (email.email))
        else:
            current_primary_email = g.user.get_primary_email()
            current_primary_email.is_primary = False
            db.session.add(current_primary_email)
            email.make_primary()
            db.session.add(email)
            db.session.commit()
            flash('%s has been successfully made your primary email.' % (email.email))
    return redirect(url_for('settings_emails'))

@app.route('/settings/emails/<email>/send-key/')
@login_required
def settings_emails_email_send_key(email):
    if not functions.is_email(email):
        pass
    else:
        email = Email.get_email_by_email(email)
        if email == None:
            pass
        elif email not in g.user.emails:
            pass
        elif email.is_not_verified():
            emails.settings_emails_email_send_key(email)
            flash('We sent your email verification to %s. Please check your inbox for verification instructions.' % (email.email))
        elif email.is_verified():
            flash('%s is already verified.' % (email.email))
        elif email.is_reported():
            flash('%s is reported. It cannot be verified until case is resolved.' % (email.email))
    return redirect(url_for('settings_emails'))

@app.route('/settings/emails/<email>/verify/', methods = ['GET', 'POST'])
def settings_emails_email_verify(email = None):
    if g.user.is_anonymous():
        form = LoginForm()
        if form.validate_on_submit():
            login_user(form.user, remember = form.remember_me.data)
            g.user.date_last_signed_in = datetime.utcnow()
            db.session.add(g.user)
            db.session.commit()
        else:
            return render_template('users/settings_emails_email_verify.html',
                form = form,
                title = 'Sign In')

    if not functions.is_email(email):
        return request.path
    elif request.args.get("key") == None or len(request.args.get("key")) != 32:
        flash('Verification key could not be detected. You may have a broken link.')
    else:
        email = Email.get_email_by_email(email)
        if email == None:
            flash('Unregistered email cannot be verified.')
        elif email not in g.user.emails:
            flash('%s is not your email. If you own this email, please send an email to \'emails@thankspress.com\'' % (email.email)) 
        elif email.is_verified():
            flash('%s is already verified.' % (email.email))
        elif email.is_reported():
            flash('%s is reported. It cannot be verified until case is resolved.' % (email.email))
        else:
            if email.verification_key == request.args.get("key"):
                email.make_verified()
                db.session.add(email)
                db.session.commit()
                Thank.migrate_thanks_received_by_email_to_user(email)
                flash('%s has been successfully verified.' % (email.email))
            else:
                flash('Verification key is not valid. Please request a new verification key and try again.')
    return redirect(url_for('settings_emails'))