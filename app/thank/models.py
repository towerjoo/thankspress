from app import db
from app.email.choices import EmailStatusChoices
from app.media.models import Media
from app.thank.choices import (ThankCommentStatusChoices, ThankStatusChoices,
    ThankReceivedByEmailStatusChoices, ThankReceivedByUserStatusChoices,
    ThankReceivedByPublicPageStatusChoices)
from app.user.choices import UserStatusChoices
from app.public_page.choices import PublicPageStatusChoices

from flask import g
from datetime import datetime

class Thank(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    giver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)

    message = db.Column(db.String(5000))
    message_language = db.Column(db.String(5))
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"))

    giver = db.relationship('User', primaryjoin = 'User.id == Thank.giver_id')
    media = db.relationship('Media', primaryjoin = 'Media.id == Thank.media_id')


    comments = db.relationship("ThankComment", 
        primaryjoin = "and_(ThankComment.thank_id == Thank.id, ThankComment.status != %d)" % ThankCommentStatusChoices.DELETED,
        lazy = "dynamic")

    receiver_users = db.relationship('User',
        secondary = 'thank_received_by_user',
        primaryjoin = "and_(  ThankReceivedByUser.thank_id == Thank.id, \
                                ThankReceivedByUser.status != %d)" % ThankReceivedByUserStatusChoices.DELETED, 
        secondaryjoin = "and_(User.id == ThankReceivedByUser.receiver_id)",
        lazy = 'dynamic')

    receiver_emails = db.relationship('Email',
        secondary = 'thank_received_by_email', 
        primaryjoin = "and_(  ThankReceivedByEmail.thank_id == Thank.id, \
                                ThankReceivedByEmail.status != %d, \
                                ThankReceivedByEmail.status != %d)" % ( ThankReceivedByEmailStatusChoices.MIGRATED,
                                                                        ThankReceivedByEmailStatusChoices.DELETED),
        secondaryjoin = "and_(Email.id == ThankReceivedByEmail.receiver_id)",
        lazy = 'dynamic')

    receiver_public_pages = db.relationship('PublicPage',
        secondary = 'thank_received_by_public_page',
        primaryjoin = "and_(ThankReceivedByPublicPage.thank_id == Thank.id, \
                            ThankReceivedByPublicPage.status != %d)" % ThankReceivedByPublicPageStatusChoices.DELETED,
        secondaryjoin = "and_(PublicPage.id == ThankReceivedByPublicPage.receiver_id)",
        lazy = 'dynamic')

    def __init__(self, giver_id, message = None, message_language = None, media_id = None, status = ThankStatusChoices.PUBLIC):
        self.giver_id = giver_id
        self.status = status
        self.date_registered = datetime.utcnow()
        self.message = message
        self.message_language = message_language
        self.media_id = media_id

    def __repr__(self):
        return "<Thank %r>" % (self.id)

    def is_public(self):
        return self.status == ThankStatusChoices.PUBLIC

    def make_public(self):
        self.status = ThankStatusChoices.PUBLIC
        return self

    def is_private(self):
        return self.status == ThankStatusChoices.PRIVATE

    def make_private(self):
        self.status = ThankStatusChoices.PRIVATE
        return self

    def is_reported(self):
        return self.status == ThankStatusChoices.REPORTED

    def make_reported(self):
        self.status = ThankStatusChoices.REPORTED
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == ThankStatusChoices.DELETED

    def make_deleted(self):
        self.status = ThankStatusChoices.DELETED
        return self

    @staticmethod
    def get_thank(id):
        try:
            return Thank.query.get(int(id))
        except:
            return None

    @staticmethod
    def migrate_thanks_received_by_email_to_user(email):
        if email.user != None:
            for thank in email.thanks_received.all():
                if thank.giver != g.user and thank not in email.user.thanks_received.all():
                    thank_received_by_user = ThankReceivedByUser(thank_id = thank.id, receiver_id = email.user_id)
                    db.session.add(thank_received_by_user)
                    db.session.commit()
                thank_received_by_email = ThankReceivedByEmail.get_thank_received_by_email_by_thank_and_receiver(thank.id, email.id)
                thank_received_by_email.make_migrated(email.user_id)
                db.session.add(thank_received_by_email)
            db.session.commit()
            return email
        return None

class ThankComment(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    comment = db.Column(db.String(5000), nullable = False)
    thank_id = db.Column(db.Integer, db.ForeignKey("thank.id"), nullable = False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)
    
    comment_language = db.Column(db.String(5))

    thank = db.relationship("Thank", 
        primaryjoin = "and_(Thank.id == ThankComment.thank_id, \
                            Thank.status != %d)" % ThankStatusChoices.DELETED)
    commenter = db.relationship("User", 
        primaryjoin = "and_(User.id == ThankComment.commenter_id, \
                            User.status != %d)" % UserStatusChoices.DELETED)

    def __init__(self, comment, thank_id, commenter_id, comment_language = None, status = ThankCommentStatusChoices.VISIBLE):
        self.comment = comment
        self.thank_id = thank_id
        self.commenter_id = commenter_id
        self.status = status
        self.date_registered = datetime.utcnow()
        self.comment_language = comment_language

    def __repr__(self):
        return "<Comment %r>" % (self.id)

    def is_visible(self):
        return self.status == ThankCommentStatusChoices.VISIBLE

    def make_visible(self):
        self.status = ThankCommentStatusChoices.VISIBLE
        return self

    def is_reported(self):
        return self.status == ThankCommentStatusChoices.REPORTED

    def make_reported(self):
        self.status = ThankCommentStatusChoices.REPORTED
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == ThankCommentStatusChoices.DELETED

    def make_deleted(self):
        self.status = ThankCommentStatusChoices.DELETED
        return self

    @staticmethod
    def get_comment(id):
        try:
            return Comment.query.get(int(id))
        except:
            return None

class ThankReceivedByEmail(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    thank_id = db.Column(db.Integer, db.ForeignKey("thank.id"), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("email.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)

    migrated_to = db.Column(db.Integer, db.ForeignKey("thank_received_by_user.id"))

    def __init__(self, thank_id, receiver_id, status = ThankReceivedByEmailStatusChoices.USER_NOT_FOUND):
        self.thank_id = thank_id
        self.receiver_id = receiver_id
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<ThankReceivedByEmail %r>' % (self.id)

    def is_user_not_found(self):
        return self.status == ThankReceivedByEmailStatusChoices.USER_NOT_FOUND

    def make_user_not_found(self):
        self.status = ThankReceivedByEmailStatusChoices.USER_NOT_FOUND
        return self

    def is_migrated(self):
        return self.status == ThankReceivedByEmailStatusChoices.MIGRATED

    def make_migrated(self, migrated_to):
        self.migrated_to = migrated_to
        self.status = ThankReceivedByEmailStatusChoices.MIGRATED
        return self

    def is_reported(self):
        return self.status == ThankReceivedByEmailStatusChoices.REPORTED

    def make_reported(self):
        self.status = ThankReceivedByEmailStatusChoices.REPORTED
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == ThankReceivedByEmailStatusChoices.DELETED

    def make_deleted(self):
        self.status = ThankReceivedByEmailStatusChoices.DELETED
        return self

    @staticmethod
    def get_thank_received_by_email(id):
        try:
            return ThankReceivedByEmail.query.get(int(id))
        except:
            None

    @staticmethod
    def get_thank_received_by_email_by_thank_and_receiver(thank_id, receiver_id):
        return ThankReceivedByEmail.query \
            .filter(ThankReceivedByEmail.thank_id == thank_id,
                    ThankReceivedByEmail.receiver_id == receiver_id,
                    ThankReceivedByEmail.status != ThankReceivedByEmailStatusChoices.DELETED) \
            .first()

class ThankReceivedByPublicPage(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    thank_id = db.Column(db.Integer, db.ForeignKey("thank.id"), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("public_page.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)

    def __init__(self, thank_id, receiver_id, status = ThankReceivedByPublicPageStatusChoices.VISIBLE):
        self.thank_id = thank_id
        self.receiver_id = receiver_id
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<ThankReceivedByPublicPage %r>' % (self.id)

    def is_visible(self):
        return self.status == ThankReceivedByPublicPageStatusChoices.VISIBLE

    def make_visible(self):
        self.status = ThankReceivedByPublicPageStatusChoices.VISIBLE
        return self

    def is_reported(self):
        return self.status == ThankReceivedByPublicPageStatusChoices.REPORTED

    def make_reported(self):
        self.status = ThankReceivedByPublicPageStatusChoices.REPORTED
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == ThankReceivedByPublicPageStatusChoices.DELETED

    def make_deleted(self):
        self.status = ThankReceivedByPublicPageStatusChoices.DELETED
        return self


class ThankReceivedByUser(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    thank_id = db.Column(db.Integer, db.ForeignKey("thank.id"), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)

    migrated_from = db.relationship("ThankReceivedByEmail", 
        primaryjoin = "and_(ThankReceivedByEmail.migrated_to == ThankReceivedByUser.id, \
                            ThankReceivedByEmail.status == %d)" % ThankReceivedByEmailStatusChoices.MIGRATED)

    def __init__(self, thank_id, receiver_id, status = ThankReceivedByUserStatusChoices.UNREAD):
        self.thank_id = thank_id
        self.receiver_id = receiver_id
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<ThankReceivedByUser %r>' % (self.id)

    def is_unread(self):
        return self.status == ThankReceivedByUserStatusChoices.UNREAD

    def make_unread(self):
        self.status = ThankReceivedByUserStatusChoices.UNREAD
        return self

    def is_visible(self):
        return self.status == ThankReceivedByUserStatusChoices.VISIBLE

    def make_visible(self):
        self.status = ThankReceivedByUserStatusChoices.VISIBLE
        return self

    def is_hidden(self):
        return self.status == ThankReceivedByUserStatusChoices.HIDDEN

    def make_hidden(self):
        self.status = ThankReceivedByUserStatusChoices.HIDDEN
        return self

    def is_reported(self):
        return self.status == ThankReceivedByUserStatusChoices.REPORTED

    def make_reported(self):
        self.status = ThankReceivedByUserStatusChoices.REPORTED
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == ThankReceivedByUserStatusChoices.DELETED

    def make_deleted(self):
        self.status = ThankReceivedByUserStatusChoices.DELETED
        return self

    @staticmethod
    def get_thank_received_by_user_by_thank_and_receiver(thank_id, receiver_id):
        return ThankReceivedByUser.query \
            .filter(ThankReceivedByUser.thank_id == thank_id,
                    ThankReceivedByUser.receiver_id == receiver_id,
                    ThankReceivedByUser.status != ThankReceivedByUserStatusChoices.DELETED) \
            .first()
