from app import db
from app import functions
from app.email.choices import EmailStatusChoices
from app.thank.choices import ThankReceivedByEmailStatusChoices, ThankStatusChoices
from app.user.choices import UserStatusChoices

from datetime import datetime

class Email(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    date_registered = db.Column(db.DateTime, nullable = False)
    email = db.Column(db.String(320), nullable = False)
    is_primary = db.Column(db.Boolean, nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    verification_key = db.Column(db.String(32))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Relationships ----------------------------------------

    user = db.relationship("User", primaryjoin = "User.id == Email.user_id")

    thanks_received = db.relationship('Thank',
        secondary = 'thank_received_by_email', 
        primaryjoin = "and_(ThankReceivedByEmail.receiver_id == Email.id, \
                            ThankReceivedByEmail.status != %d)" % ThankReceivedByEmailStatusChoices.DELETED,
        secondaryjoin = "and_(Thank.id == ThankReceivedByEmail.thank_id, Thank.status != %d)" % ThankStatusChoices.DELETED, 
        lazy = 'dynamic')

    thank_received_by_emails = db.relationship("ThankReceivedByEmail", 
        primaryjoin = "and_(ThankReceivedByEmail.receiver_id == Email.id, \
                            ThankReceivedByEmail.status != %d)" % ThankReceivedByEmailStatusChoices.DELETED, 
        lazy = "dynamic")

    # Methods -----------------------------------------------

    def __init__(self, email, is_primary = False, status = EmailStatusChoices.NOT_VERIFIED, user_id = None):
        self.date_registered = datetime.utcnow()
        self.email = email
        self.is_primary = is_primary
        self.status = status
        self.verification_key = functions.generate_key(email)

        self.user_id = user_id

    def __repr__(self):
        return '<Email %r>' % (self.id)

    def is_not_primary(self):
        return not self.is_primary

    def make_not_primary(self):
        self.is_primary = False
        return self

    def make_primary(self):
        self.is_primary = True
        return self

    def is_not_verified(self):
        return self.status == EmailStatusChoices.NOT_VERIFIED

    def make_not_verified(self):
        self.status = EmailStatusChoices.NOT_VERIFIED
        self.verification_key = functions.generate_key(self.mail)
        return self

    def is_verified(self):
        return self.status == EmailStatusChoices.VERIFIED

    def make_verified(self):
        self.status = EmailStatusChoices.VERIFIED
        self.verification_key = None
        return self

    def is_reported(self):
        return self.status == EmailStatusChoices.REPORTED

    def make_reported(self):
        self.status = EmailStatusChoices.REPORTED
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == EmailStatusChoices.DELETED

    def make_deleted(self):
        self.status = EmailStatusChoices.DELETED
        self.is_primary = False
        return self

    @staticmethod
    def get_email(id):
        try:
            return Email.query.get(int(id))
        except:
            return None

    @staticmethod
    def get_email_by_email(email):
        return Email.query.filter(  Email.email == email, 
                                    Email.status != EmailStatusChoices.DELETED)\
                            .first()

    @staticmethod
    def get_primary_email_by_email(email):
        return Email.query.filter(  Email.email == email, 
                                    Email.is_primary == True, 
                                    Email.status != EmailStatusChoices.DELETED)\
                            .first()

    @staticmethod
    def get_primary_email_by_user_id(user_id):
        return Email.query.filter(  Email.user_id == user_id,
                                    Email.is_primary == True,
                                    Email.status != EmailStatusChoices.DELETED)\
                            .first()

    @staticmethod
    def is_free_email(email):
        return Email.query.filter(  Email.email == email,
                                    Email.status != EmailStatusChoices.DELETED)\
                            .first() == None