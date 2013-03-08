from app import db
from app.follow.choices import FollowStatusChoices

from datetime import datetime

class Follow(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)

    def __init__(self, follower_id, followed_id, status = FollowStatusChoices.FOLLOWING):
        self.follower_id = follower_id
        self.followed_id = followed_id
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<Follow %r>' % (self.id)

    def is_following(self):
        return self.status == FollowStatusChoices.FOLLOWING

    def make_following(self):
        self.status = FollowStatusChoices.FOLLOWING
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == FollowStatusChoices.DELETED

    def make_deleted(self):
        self.status = FollowStatusChoices.DELETED
        return self

    @staticmethod
    def get_follow(id):
        try:
            return Follow.query.get(int(id))
        except:
            return None

    @staticmethod
    def is_following_by_follower_and_followed(follower_id, followed_id):
        return Follow.query.filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id, Follow.status == FollowStatusChoices.FOLLOWING).first() != None

    @staticmethod
    def get_follow_by_follower_and_followed(follower_id, followed_id):
        return Follow.query.filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id, Follow.status == FollowStatusChoices.FOLLOWING).first()

    @staticmethod
    def get_deleted_follows_by_follower_and_followed(follower_id, followed_id):
        return Follow.query.filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id, Follow.status == FollowStatusChoices.DELETED).all()