from hashlib import md5
from flask.ext.wtf import BooleanField, Email, Form, Length, Required, TextField

class GiveThanksForm(Form):
    receivers = TextField("To", 
        validators = [  Required()])
    message = TextField("Message", 
        validators = [  Length( max = 5000, 
                                message="Message must be maximum 5000 characters.")])
    media = TextField("Media") #Integrate Flask-Uploads
    private = BooleanField("Private", 
        default = False)