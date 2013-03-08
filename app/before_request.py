from app import app, db
from datetime import datetime

from flask import g, request, redirect, flash, render_template, url_for
from flask.ext.login import current_user

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.date_last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        if  g.user.is_activated() or request.endpoint in ('logout', 'settings_emails_email_verify', 'settings_emails_email_send_key'):
            pass
        elif g.user.is_new():
            if g.user.primary_email.is_verified():
                g.user.make_activated()
                db.session.add(g.user)
                db.session.commit()
                return redirect(url_for('user_thanks', username = g.user.username))
            return render_template('users/new_user.html',
                title = 'Email Verification')
        elif g.user.is_deactivated():
            g.user.make_activated()
            db.session.add(g.user)
            db.session.commit()
            flash('Great to see you back!')
        elif g.user.is_deleted():
            flash("Your account is deleted.")
            return redirect(url_for('logout'))