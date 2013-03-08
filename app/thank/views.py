from app import app, db
from app.email.models import Email

from app.follow.choices import FollowStatusChoices
from app.follow.models import Follow

from app.thank.forms import ThanksGiveForm
from app.thank.models import Thank, ThankReceivedByEmail, \
    ThankReceivedByUser, ThankReceivedByPublicPage
from app.thank.choices import ThankStatusChoices, ThankReceivedByUserStatusChoices, ThankReceivedByEmailStatusChoices

from flask import render_template, abort, redirect, url_for, g, request, flash
from flask.ext.login import login_required

from sqlalchemy import desc, or_

@app.route('/')
@app.route('/thanks/')
def thanks():
    suggested_users = None
    if g.user.is_anonymous():
        thanks = Thank.query.filter(Thank.status == ThankStatusChoices.PUBLIC)\
                                .order_by(desc(Thank.date_registered))\
                                .all()
    else:
        thanks = Thank.query.outerjoin(ThankReceivedByUser,
                                    (ThankReceivedByUser.thank_id == Thank.id))\
                            .outerjoin(ThankReceivedByEmail,
                                    (ThankReceivedByEmail.thank_id == Thank.id))\
                            .outerjoin(Follow, 
                                    (Follow.followed_id == ThankReceivedByUser.receiver_id))\
                            .filter(Thank.status != ThankStatusChoices.DELETED,
                                    ThankReceivedByUser.status != ThankReceivedByUserStatusChoices.DELETED,
                                    ThankReceivedByUser.status != ThankReceivedByUserStatusChoices.HIDDEN,
                                    ThankReceivedByEmail.status != ThankReceivedByEmailStatusChoices.DELETED,
                                    ThankReceivedByEmail.status != ThankReceivedByEmailStatusChoices.MIGRATED,
                                    Follow.status != FollowStatusChoices.DELETED)\
                            .filter(or_(Thank.giver_id == g.user.id,
                                        Follow.follower_id == g.user.id))\
                            .all()
    return render_template('thanks/thanks.html',
        suggested_users = suggested_users,
        thanks = thanks,
        title = 'Thanks')


@app.route('/thanks/give/', methods = ['GET', 'POST'])
@login_required
def thanks_give():
    form = ThanksGiveForm()
    if form.validate_on_submit():
        # Register Thank
        media = None
        message_language = None
        status = ThankStatusChoices.PUBLIC
        if form.private.data == True:
            status = ThankStatusChoices.PRIVATE
        thank = Thank(  giver_id = g.user.id, 
                        message = form.message.data,
                        message_language = message_language,
                        media_id = media,
                        status = status  )
        db.session.add(thank)
        db.session.commit()
        # Register Thank Receivers
        for email in form.receivers.data['emails']:
            if email not in g.user.emails or email.is_not_verified():
                trbe = ThankReceivedByEmail(thank_id = thank.id, receiver_id = email.id)
                db.session.add(trbe)
                db.session.commit()
                if email.user != None and email.is_verified():
                    trbu = ThankReceivedByUser( thank_id = thank.id, 
                                                receiver_id = email.user_id)
                    db.session.add(trbu)
                    db.session.commit()

                    trbe.make_migrated(trbu.id)
                    db.session.add(trbe)
                    db.session.commit()
        for public_page in form.receivers.data['public_pages']:
            trbpp = ThankReceivedByPublicPage(thank_id = thank.id, receiver_id = public_page.id)
            db.session.add(trbpp)
            db.session.commit()
        for user in form.receivers.data['users']:
            if user != g.user:
                trbu = ThankReceivedByUser(thank_id = thank.id, receiver_id = user.id)
                db.session.add(trbu)
                db.session.commit()
        return redirect(url_for('thanks_thank', id = thank.id))
    return render_template('thanks/thanks_give.html',
        form = form,
        title = 'Give Thanks')


@app.route('/thanks/<int:id>/', methods = ['GET', 'POST'])
def thanks_thank(id = None):
    thank = Thank.get_thank(id)
    if thank != None and thank.is_public() or g.user in thank.receiver_users.all() or g.user == thank.giver:
        return render_template('thanks/thank.html',
            thank = thank,
            ThankReceivedByUser = ThankReceivedByUser,
            title = 'Thank by ' + thank.giver.profile.name)
    abort(404)

@app.route('/thanks/<int:id>/make-visible/')
@login_required
def thanks_thank_make_visible(id = None):
    thank = Thank.get_thank(id)
    if thank != None:
        thank_received_by_user = ThankReceivedByUser\
            .get_thank_received_by_user_by_thank_and_receiver(
                thank_id = thank.id,
                receiver_id = g.user.id)
        if thank_received_by_user != None:
            thank_received_by_user.make_visible()
            db.session.add(thank_received_by_user)
            db.session.commit()
        return redirect(request.args.get("next") or url_for('thanks_thank', id = thank.id))
    abort(404)

@app.route('/thanks/<int:id>/make-hidden/')
@login_required
def thanks_thank_make_hidden(id = None):
    thank = Thank.get_thank(id)
    if thank != None:
        thank_received_by_user = ThankReceivedByUser\
            .get_thank_received_by_user_by_thank_and_receiver(
                thank_id = thank.id,
                receiver_id = g.user.id)
        if thank_received_by_user != None:
            thank_received_by_user.make_hidden()
            db.session.add(thank_received_by_user)
            db.session.commit()
        return redirect(request.args.get("next") or url_for('thanks_thank', id = thank.id))
    abort(404)

@app.route('/thanks/<int:id>/delete/')
@login_required
def thanks_thank_delete(id = None):
    thank = Thank.get_thank(id)
    if thank != None and thank.giver == g.user:
        thank.make_deleted()
        db.session.add(thank)
        db.session.commit()
        flash('Thank deleted.')
        return redirect(request.args.get("next") or url_for('user_thanks_given', username = g.user.username))
    abort(404)