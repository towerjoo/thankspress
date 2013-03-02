from app import app
from app.thank.forms import ThankGiveForm

from flask import render_template
from flask.ext.login import login_required

@app.route('/thanks', methods = ['GET', 'POST'])
@app.route('/thanks/', methods = ['GET', 'POST'])
@app.route('/thanks/give', methods = ['GET', 'POST'])
@app.route('/thanks/give/', methods = ['GET', 'POST'])
@login_required
def thanks_give():
    form = ThankGiveForm()
    if form.validate_on_submit():
        return 'Success!'
    return render_template('thank/thank_give.html', 
        title = 'Give Thanks')


@app.route('/thanks/<int:thank_id>', methods = ['GET', 'POST'])
@app.route('/thanks/<int:thank_id>/', methods = ['GET', 'POST'])
def thanks_thank(thank_id = None):
    form = ThankGiveForm()
    if form.validate_on_submit():
        return 'Success!'
    return render_template('thank/thank_give.html', 
        title = 'Give Thanks')