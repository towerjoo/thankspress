from app import db
from app import functions
from app.public_page.choices import PublicPageStatusChoices

from app.email.models import Email
from app.email.choices import EmailStatusChoices
from app.follow.choices import FollowStatusChoices
from app.thank.choices import (ThankCommentStatusChoices, ThankStatusChoices,
    ThankReceivedByEmailStatusChoices, ThankReceivedByUserStatusChoices)
from app.user.choices import UserStatusChoices

from config import FORBIDDEN_USERNAMES
from datetime import datetime, timedelta
from hashlib import sha1

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    date_registered = db.Column(db.DateTime, nullable = False)
    language = db.Column(db.String(5), nullable = False)
    password = db.Column(db.String(40), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    username = db.Column(db.String(40), nullable = False)

    date_last_logged_in = db.Column(db.DateTime)
    date_last_seen = db.Column(db.DateTime)
    password_reset_key = db.Column(db.String(40))
    password_reset_key_expiration_date = db.Column(db.DateTime)

    # Email
    emails = db.relationship("Email", 
        primaryjoin = "and_(Email.user_id == User.id, \
                            Email.status != %d)" % EmailStatusChoices.DELETED, 
        lazy = "dynamic")

    primary_email = db.relationship("Email", 
        primaryjoin = "and_(Email.user_id == User.id, \
                            Email.is_primary == True, Email.status != %d)" % EmailStatusChoices.DELETED,
        uselist = False)

    # Follow
    following = db.relationship('User',
        secondary = 'follow', 
        primaryjoin = "and_(User.id == Follow.follower_id, \
                            User.status != %d)" % UserStatusChoices.DELETED, 
        secondaryjoin = "and_(  Follow.followed_id == User.id, \
                                Follow.status == %d)" % FollowStatusChoices.FOLLOWING, 
        backref = db.backref('followers', 
            lazy = 'dynamic'), 
        lazy = 'dynamic')

    # Profile
    profile = db.relationship('UserProfile', uselist = False)

    # PublicPage
    public_pages = db.relationship("PublicPage", 
        primaryjoin = "and_(PublicPage.creator_id == User.id, \
                            PublicPage.status != %d)" % PublicPageStatusChoices.DELETED, 
        lazy = "dynamic")

    # Thank
    thanks_given = db.relationship("Thank", 
        primaryjoin="and_(  Thank.giver_id == User.id, \
                            Thank.status != %d)" % ThankStatusChoices.DELETED, 
        lazy = "dynamic")

    thanks_received = db.relationship('Thank',
        secondary = 'thank_received_by_user', 
        primaryjoin = "and_(ThankReceivedByUser.receiver_id == User.id, \
                            ThankReceivedByUser.status != %d)" % ThankReceivedByUserStatusChoices.DELETED, 
        secondaryjoin = "and_(  Thank.id == ThankReceivedByUser.thank_id, \
                                Thank.status != %d)" % ThankStatusChoices.DELETED, 
        lazy = 'dynamic')

    thanks_received_unread = db.relationship('Thank',
        secondary = 'thank_received_by_user',
        primaryjoin = "and_(ThankReceivedByUser.receiver_id == User.id, \
                            ThankReceivedByUser.status == %d)" % ThankReceivedByUserStatusChoices.UNREAD, 
        secondaryjoin = "and_(  Thank.id == ThankReceivedByUser.thank_id, \
                                Thank.status != %d)" % ThankStatusChoices.DELETED, 
        lazy = 'dynamic')

    # ThankComment
    thank_comments = db.relationship("ThankComment", 
        primaryjoin = "and_(ThankComment.commenter_id == User.id, \
                            ThankComment.status != %d)" % ThankCommentStatusChoices.DELETED, 
        lazy = "dynamic")

    def __init__(self, password, username, language = 'en', status = UserStatusChoices.NEW):
        self.date_registered = datetime.utcnow()
        self.language = language
        self.password = sha1(password).hexdigest()
        self.username = username
        self.status = status

    def __repr__(self):
        return "<User %r - %s>" % (self.id, self.profile.name)

    ########### Flask-Login ############

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.is_not_deleted()

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    ####################################

    def is_new(self):
        return self.status == UserStatusChoices.NEW

    def make_new(self):
        self.status = UserStatusChoices.NEW
        return self

    def is_activated(self):
        return self.status == UserStatusChoices.ACTIVE

    def make_activated(self):
        self.status = UserStatusChoices.ACTIVE
        return self

    def is_deactivated(self):
        return self.status == UserStatusChoices.INACTIVE

    def make_deactivated(self):
        self.status = UserStatusChoices.INACTIVE
        return self

    def is_reported(self):
        return self.status == UserStatusChoices.REPORTED

    def make_reported(self):
        self.status = UserStatusChoices.REPORTED
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == UserStatusChoices.DELETED

    def make_deleted(self):
        self.status = UserStatusChoices.DELETED
        return self

    def match_password(self, password):
        return self.password == sha1(password).hexdigest()

    def change_password(self, new_password):
        self.password = sha1(new_password).hexdigest()
        self.date_changed_password = datetime.utcnow()
        return self

    def set_password_reset_key(self):
        self.password_reset_key = functions.generate_key(email)
        self.password_reset_key_expiration_date = datetime.utcnow() + timedelta(days=1)
        return self

    def can_reset_password(self, password_reset_key):
        return self.password_reset_key != None \
            and self.password_reset_key_expiration_date != None \
            and self.password_reset_key == password_reset_key \
            and self.password_reset_key_expiration_date > datetime.utcnow()

    def reset_password(self, new_password):
        self.change_password(new_password)
        self.password_reset_key = None
        self.password_reset_key_expiration_date = None
        return self

    def total_following(self):
        return len(self.following.all())-1 #Exclude user's self following

    def total_followers(self):
        return len(self.followers.all())-1 #Exclude user's self following

    @staticmethod
    def get_user(id):
        try:
            return User.query.get(int(id))
        except:
            return None

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter(   User.username == username, 
                                    User.status != UserStatusChoices.DELETED)\
                            .first()

    @staticmethod
    def get_user_by_email(email):
        user = getattr(Email.get_email_by_email(email), 'user', None)
        if user != None and user.is_not_deleted():
            return user
        return None

    @staticmethod
    def login_by_email(email, password):
        user = User.get_user_by_email(email)
        if user != None and user.password == sha1(password).hexdigest():
            return user
        return None

    @staticmethod
    def login_by_username(username, password):
        return User.query.filter(   User.username == username, 
                                    User.password == sha1(password).hexdigest(), 
                                    User.status != UserStatusChoices.DELETED)\
                            .first()

    @staticmethod
    def is_free_username(username):
        return username not in FORBIDDEN_USERNAMES and User.get_user_by_username(username) == None

    @staticmethod
    def make_free_username(username):
        if User.is_free_username(username): 
            return username
        count = 2
        username += str(count) 
        while User.is_free_username(username) != True:
            count += 1
            username = username[:-1] + str(count)
        return username


class UserProfile(db.Model):

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    name = db.Column(db.String(40), nullable = False)
    picture_id = db.Column(db.Integer, db.ForeignKey("media.id"), nullable = False)

    bio = db.Column(db.String(500))
    website = db.Column(db.String(500))

    def __init__(self, user_id, name, picture_id = 1):
        self.user_id = user_id
        self.name = name
        self.picture_id = picture_id

    def __repr__(self):
        return "<UserProfile %r - %s>" % (self.user_id, self.name)