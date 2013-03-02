from flask.ext.wtf import BooleanField, Form, Length, Required, TextField

class ThankGiveForm(Form):
    receivers = TextField("To", 
        validators = [  Required()])
    message = TextField("Message", 
        validators = [  Length( max = 5000, 
                                message="Message must be maximum 5000 characters.")])
    media = TextField("Media") #Integrate Flask-Uploads
    private = BooleanField("Private", 
        default = False)