from app.user.forms import LoginForm
from flask.ext.wtf import Form, TextField, Required, Length, Email

class SettingsEmailsForm(Form):
    email = TextField("Email",
        validators = [  Required(),
                        Length( max = 320, 
                                message = "Email must be maximum 320 characters."),
                        Email()])