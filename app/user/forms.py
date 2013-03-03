from app import functions
from app.user.models import Email as EmailModel, User as UserModel
from config import IMAGE_TYPES

from flask.ext.wtf import BooleanField, Email, EqualTo, FileField, HiddenField, \
    Form, Length, PasswordField, Required, TextField

# Account -----------------------------------------
class SettingsAccountPickUsernameForm(Form):
    username = TextField("Username", 
        validators = [  Required(),
                        Length( max = 32, 
                                message = "Username must be maximum 320 characters.")])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if UserModel.is_unique_username(self.username.data):
            return True
        self.username.errors.append('Username is not available.')
        return False


class SettingsAccountForm(Form):
    username = TextField("Username", 
        validators = [  Required(),
                        Length( max = 32, 
                                message = "Username must be maximum 320 characters.")])

    def __init__(self, user, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.user.username == self.username.data or UserModel.is_unique_username(self.username.data):
            return True
        self.username.errors.append('Username is not available.')
        return False

# Emails -----------------------------------------
class SettingsEmailsForm(Form):
    email = TextField("Email",
        validators = [  Required(),
                        Length( max = 320, 
                                message = "Email must be maximum 320 characters."),
                        Email()])

# Profile ----------------------------------------
class SettingsProfileForm(Form):
    name = TextField("Name", 
        validators = [  Required(), 
                        Length( max = 32, 
                                message="Name must be maximum 32 characters.")])
    bio = TextField("Bio", 
        validators = [  Length( max = 500, 
                                message="Bio must be maximum 500 characters.")])
    website = TextField("Website", 
        validators = [  Length( max = 500, 
                                message="Website must be maximum 500 characters.")])

class SettingsProfilePictureForm(Form):
    picture = FileField("Profile Picture",
        validators = [  Required( message = "Select a picture to upload.")])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.picture.data != None and functions.is_image_type(self.picture.data.filename):
            return True
        self.picture.errors.append('Image files only.')
        return False

# Registration -----------------------------------
class SignInForm(Form):
    email = TextField("Email", 
        validators = [  Required()])
    password = PasswordField("Password", 
        validators = [  Required()])
    remember_me = BooleanField("Remember Me", 
        default = False)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None
        self.validation_errors = []

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if functions.is_email(self.email.data):
            user = UserModel.sign_in_by_email(self.email.data, self.password.data)
        else:
            user = UserModel.sign_in_by_username(self.email.data, self.password.data)

        if user == None:
            self.validation_errors.append('Email and password did not match.')
            return False

        self.user = user
        return True

class SettingsEmailsEmailVerifyForm(SignInForm):
    email_to_be_verified = HiddenField()
    email_verification_key = HiddenField()

class SignUpForm(Form):
    name = TextField("Name", 
        validators = [  Required(), 
                        Length( max = 32,    
                                message="Name must be maximum 32 characters.")])
    email = TextField("Email", 
        validators = [  Required(), 
                        Email(), 
                        Length( max = 320, 
                                message="Email must be maximum 320 characters.")])
    password = PasswordField("Password", 
        validators = [  Required(),
                        Length( min = 8, 
                                max = 32, 
                                message="Password must be minimum 8 maximum 32 characters.")])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if EmailModel.is_unique_email(self.email.data):
            return True
        self.email.errors.append('Email is already registered.')
        return False


# Security --------------------------------------
class SettingsPasswordChangeForm(Form):
    current_password = PasswordField("Current Password", 
        validators = [  Required()])
    new_password = PasswordField("New Password", 
        validators = [  Required(),
                        Length( min = 8, 
                                max = 32, 
                                message="New Password must be minimum 8 maximum 32 characters."),
                        EqualTo('new_password_again', 
                                message = "New Password did not match New Password Again.")])
    new_password_again = PasswordField("New Password Again", 
        validators = [  Required()])

    def __init__(self, user, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.user.match_password(self.current_password.data):
            return True
        self.current_password.errors.append('Current Password field did not match with our records.')
        return False
