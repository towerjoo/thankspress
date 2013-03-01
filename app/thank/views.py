from app import app
from app.thank.forms import GiveThanksForm
from app.thank.models import Thank, ThankComment, ThankReceivedByEmail, \
    ThankReceivedByPublicPage, ThankReceivedByUser
from app.user.models import User

from flask import render_template
from flask.ext.login import login_required

@app.route('/give-thanks', methods = ['GET', 'POST'])
@app.route('/give-thanks/', methods = ['GET', 'POST'])
@login_required
def give_thanks():
    form = GiveThanksForm()
    if form.validate_on_submit():
        return 'Success!'
    return render_template('thank/give-thanks.html', 
        title = 'Give Thanks',
        message = '/give-thanks')


@app.route('/<username>/thanks-given')
@app.route('/<username>/thanks-given/')
def user_thanks_given(username = None):
    if username != None:
        user = User.get_user_by_username(username)
        if user != None and user.is_active():
            return render_template('thank/user_thanks_given.html', 
                title = 'Thanks Given by' + user.username,
                message = '/' + user.username + '/thanks-given')
    return render_template('404.html'), 404

@app.route('/<username>/thanks-received')
@app.route('/<username>/thanks-received/')
def user_thanks_received(username = None):
    if username != None:
        user = User.get_user_by_username(username)
        if user != None and user.is_active():
            return render_template('thank/user_thanks_received.html', 
                title = 'Thanks Received by' + user.username,
                message = '/' + user.username + '/thanks-received')
    return render_template('404.html'), 404

