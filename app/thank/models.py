from app import db
from datetime import datetime
from app.media.models import Media
from app.thank.choices import ThankCommentStatusChoices, ThankStatusChoices, \
    ThankReceivedByEmailStatusChoices, ThankReceivedByUserStatusChoices, \
    ThankReceivedByPublicPageStatusChoices

class Thank(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    giver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)

    message = db.Column(db.String(5000))
    message_language = db.Column(db.String(5))
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"))

    comments = db.relationship("ThankComment", 
        primaryjoin = "and_(ThankComment.thank_id == Thank.id, ThankComment.status != 3)",
        backref = "thank", 
        lazy = "dynamic")

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


class ThankComment(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    comment = db.Column(db.String(5000), nullable = False)
    thank_id = db.Column(db.Integer, db.ForeignKey("thank.id"), nullable = False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)
    
    comment_language = db.Column(db.String(5))

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

    def make_migrated(self):
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

