from app import app

from app.thank.choices import ThankReceivedByUserStatusChoices
from app.thank.models import Thank, ThankReceivedByUser

from flask import render_template, g
from flask.ext.login import login_required

from sqlalchemy import desc

@app.route('/notifications/')
@login_required
def notifications():
    return render_template('notifications/notifications.html',
        title = 'Notifications',
        message = '/notifications')

@app.route('/notifications/thanks-received/')
@login_required
def notifications_thanks_received():
    return render_template('notifications/notifications_thanks_received.html',
        thanks = g.user.thanks_received\
            .filter(ThankReceivedByUser.status == ThankReceivedByUserStatusChoices.UNREAD)\
            .order_by(desc(Thank.date_registered))\
            .all(),
        title = 'Notifications for Thanks-Received')