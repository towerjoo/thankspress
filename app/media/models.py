from app import db
from app.media.choices import MediaStatusChoices

from datetime import datetime

class Media(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.SmallInteger, nullable = False)
    path = db.Column(db.String(500), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False)
    date_registered = db.Column(db.DateTime, nullable = False)

    profile = db.relationship('Profile', 
        primaryjoin='and_(Profile.picture_id == Media.id)',
        backref = 'picture', 
        lazy = 'dynamic')

    thank = db.relationship('Thank', 
        primaryjoin='and_(Thank.media_id == Media.id)', 
        backref = 'media', 
        lazy = 'dynamic')

    def __init__(self, type, path, status = MediaStatusChoices.VISIBLE):
        self.type = type
        self.path = path
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<Media %r>' % (self.id)

    def is_visible(self):
        return self.status == MediaStatusChoices.VISIBLE

    def make_visible(self):
        self.status = MediaStatusChoices.VISIBLE
        return self

    def is_reported(self):
        return self.status == MediaStatusChoices.REPORTED

    def make_reported(self):
        self.status = MediaStatusChoices.REPORTED
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == MediaStatusChoices.DELETED

    def make_deleted(self):
        self.status = MediaStatusChoices.DELETED
        return self

    @staticmethod
    def get_media(id):
        try:
            return Media.query.get(int(id))
        except:
            return None