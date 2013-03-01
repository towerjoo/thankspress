from app import db
from app.public_page.choices import PublicPageStatusChoices, MediaTypeChoices
from app.thank.choices import ThankStatusChoices, ThankReceivedByPublicPageStatusChoices

from datetime import datetime

class Media(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.SmallInteger, nullable = False)
    path = db.Column(db.String(500), nullable = False)
    date_registered = db.Column(db.DateTime, nullable = False)

    thank = db.relationship("Thank", 
        primaryjoin="and_(Thank.media_id == Media.id, Thank.status != %d)" % ThankStatusChoices.DELETED, 
        backref = "media", 
        lazy = "dynamic")

    def __init__(self, type, path, status = 1):
        self.type = type
        self.path = path
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return "<Media %r>" % (self.id)

    @staticmethod
    def get_media(id):
        try:
            return Media.query.get(int(id))
        except:
            return None

class PublicPage(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False)
    date_registered = db.Column(db.DateTime, nullable = False)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    
    date_status_updated = db.Column(db.DateTime)

    thanks_received = db.relationship('Thank',
        secondary = 'thank_received_by_public_page', 
        primaryjoin = "and_(ThankReceivedByPublicPage.receiver_id == PublicPage.id, ThankReceivedByPublicPage.status != %d)" % ThankReceivedByPublicPageStatusChoices.DELETED, 
        secondaryjoin = "and_(Thank.id == ThankReceivedByPublicPage.thank_id, Thank.status != %d)" % ThankStatusChoices.DELETED, 
        backref = db.backref('receiver_public_pages', lazy = 'dynamic'), 
        lazy = 'dynamic')

    def __init__(self, name, creator_id, status = PublicPageStatusChoices.NOT_VERIFIED):
        self.name = name
        self.creator_id = creator_id
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<PublicPage %r>' % (self.id)

    def is_not_verified(self):
        return self.status == PublicPageStatusChoices.NOT_VERIFIED

    def make_not_verified(self):
        self.status = PublicPageStatusChoices.NOT_VERIFIED
        self.date_status_updated = datetime.utcnow()
        return self

    def is_verified(self):
        return self.status == PublicPageStatusChoices.VERIFIED

    def make_verified(self):
        self.status = PublicPageStatusChoices.VERIFIED
        self.date_status_updated = datetime.utcnow()
        return self

    def is_reported(self):
        return self.status == PublicPageStatusChoices.VERIFIED

    def make_reported(self):
        self.status = PublicPageStatusChoices.REPORTED
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == PublicPageStatusChoices.DELETED

    def make_deleted(self):
        self.status = PublicPageStatusChoices.DELETED
        self.date_status_updated = datetime.utcnow()
        return self

    @staticmethod
    def get_public_page(id):
        try:
            return PublicPage.query.get(int(id))
        except:
            return None

