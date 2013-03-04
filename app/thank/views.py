from app import app
from app.thank.forms import ThankGiveForm
from app.thank.models import Thank

from flask import render_template, abort
from flask.ext.login import login_required

@app.route('/thanks/', methods = ['GET', 'POST'])
@app.route('/thanks/give/', methods = ['GET', 'POST'])
@login_required
def thanks_give():
    form = ThankGiveForm()
    if form.validate_on_submit():
        return 'Success!'
    return render_template('thank/thank_give.html', 
        title = 'Give Thanks')


@app.route('/thanks/<int:id>/', methods = ['GET', 'POST'])
def thanks_thank(id = None):
    thank = Thank.get_thank(id)
    if thank != None:
        return render_template('thanks/thank.html',
            thank = thank,
            title = 'Thank by ' + thank.giver.profile.name)
    abort(404)