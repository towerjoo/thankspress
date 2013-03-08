from flask.ext.wtf import BooleanField, Form, Length, Required, TextField, TextAreaField, FileField
from app import functions
from app import db
from app.email.models import Email as EmailModel
from app.user.models import User as UserModel
from app.public_page.models import PublicPage as PublicPageModel

class ThanksGiveForm(Form):
    receivers = TextField("To", 
        validators = [  Required()])
    message = TextAreaField("Message", 
        validators = [  Length( max = 5000, 
                                message="Message must be maximum 5000 characters.")])
    media = FileField("Media")
    private = BooleanField("Private", 
        default = False)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        all_receivers = []
        for x in self.receivers.data.split(','):
            for y in x.split(' '):
                all_receivers.append(y.lower())

        all_receivers = list(set(all_receivers))
        all_receivers = filter(None, all_receivers)

        valid_receivers = {'emails':[],'users':[],'public_pages':[]}
        for receiver in all_receivers:
            if functions.is_email(receiver):
                email = EmailModel.get_email_by_email(receiver)
                if email == None:
                    email = EmailModel(email = receiver)
                    db.session.add(email)
                    db.session.commit()
                valid_receivers['emails'].append(email)

            elif receiver[:1] == 'u' and functions.is_integer(receiver[1:]):
                user = UserModel.get_user(int(receiver[1:]))
                if user != None:
                    valid_receivers['users'].append(user)

            elif receiver[:2] == 'pp' and functions.is_integer(receiver[2:]):
                public_page = PublicPageModel.get_public_page(int(receiver[2:]))
                if public_page != None:
                    valid_receivers['public_pages'].append(public_page)

        for key in valid_receivers:
            if valid_receivers[key] != []:
                self.receivers.data = valid_receivers
                return True

        self.receivers.errors.append('No valid receivers were entered.')
        return False

    #     if self.media.data != None and functions.is_image_type(self.media.data.filename):
    #         return True
    #     self.media.errors.append('Image files only.')
    #     return False