from app import db
from app.functions import Functions
from app.public_page.choices import PublicPageStatusChoices
from app.thank.choices import ThankCommentStatusChoices, ThankStatusChoices, \
    ThankReceivedByEmailStatusChoices, ThankReceivedByUserStatusChoices
from app.user.choices import EmailStatusChoices, FollowStatusChoices, UserStatusChoices

from config import FORBIDDEN_USERNAMES
from datetime import datetime, timedelta
from hashlib import md5
from sqlalchemy import desc, or_

class Email(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(320), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    is_primary = db.Column(db.Boolean, nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)

    verification_key = db.Column(db.String(32))
    date_status_updated = db.Column(db.DateTime)

    thanks_received = db.relationship('Thank',
        secondary = 'thank_received_by_email', 
        primaryjoin = "and_(ThankReceivedByEmail.receiver_id == Email.id, ThankReceivedByEmail.status != %d)" % ThankReceivedByEmailStatusChoices.DELETED, 
        secondaryjoin = "and_(Thank.id == ThankReceivedByEmail.thank_id, Thank.status != %d)" % ThankStatusChoices.DELETED, 
        backref = db.backref('receiver_emails', lazy = 'dynamic'), 
        lazy = 'dynamic')

    def __init__(self, email, user_id, is_primary = False, status = EmailStatusChoices.NOT_VERIFIED):
        self.email = email
        self.user_id = user_id
        self.verification_key = Functions.generate_key(email)
        self.is_primary = is_primary
        self.status = status
        self.date_registered = datetime.utcnow()

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
        self.date_status_updated = datetime.utcnow()
        self.verification_key = Functions.generate_key(self.mail)
        return self

    def is_verified(self):
        return self.status == EmailStatusChoices.VERIFIED

    def make_verified(self):
        self.status = EmailStatusChoices.VERIFIED
        self.date_status_updated = datetime.utcnow()
        self.verification_key = None
        return self

    def is_reported(self):
        return self.status == EmailStatusChoices.REPORTED

    def make_reported(self):
        self.status = EmailStatusChoices.REPORTED
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == EmailStatusChoices.DELETED

    def make_deleted(self):
        self.status = EmailStatusChoices.DELETED
        self.is_primary = False
        self.date_status_updated = datetime.utcnow()
        return self

    @staticmethod
    def get_email(id):
        try:
            return Email.query.get(int(id))
        except:
            return None

    @staticmethod
    def get_email_by_email(email):
        return Email.query.filter(Email.email == email, Email.status != EmailStatusChoices.DELETED).first()

    @staticmethod
    def get_primary_email_by_email(email):
        return Email.query.filter(Email.email == email, Email.is_primary == True).first()

    @staticmethod
    def get_primary_email_by_user_id(user_id):
        return Email.query.filter(Email.user_id == user_id, Email.is_primary == True).first()

    @staticmethod
    def is_unique_email(email):
        return Email.query.filter(Email.email == email, Email.status != EmailStatusChoices.DELETED).first() == None

class Follow(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    date_registered = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 

    date_status_updated = db.Column(db.DateTime)

    def __init__(self, follower_id, followed_id, status = FollowStatusChoices.FOLLOWING):
        self.follower_id = follower_id
        self.followed_id = followed_id
        self.date_registered = datetime.utcnow()
        self.status = status

    def __repr__(self):
        return '<Follow %r>' % (self.id)

    def is_following(self):
        return self.status == FollowStatusChoices.FOLLOWING

    def make_following(self):
        self.status = FollowStatusChoices.FOLLOWING
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == FollowStatusChoices.DELETED

    def make_deleted(self):
        self.status = FollowStatusChoices.DELETED
        self.date_status_updated = datetime.utcnow()
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


class User(db.Model):

    #account
    id = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.String(32), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    language = db.Column(db.String(5), nullable = False)
    date_registered = db.Column(db.DateTime, nullable = False)

    username = db.Column(db.String(32))
    reset_password_key = db.Column(db.String(32))
    date_status_updated = db.Column(db.DateTime)
    date_last_acted = db.Column(db.DateTime)
    date_changed_password = db.Column(db.DateTime)
    date_set_reset_password_key = db.Column(db.DateTime)

    #comments
    comments = db.relationship("Comment", 
        primaryjoin = "and_(Comment.commenter_id == User.id, Comment.status != %d)" % ThankCommentStatusChoices.DELETED, 
        backref = "commenter", 
        lazy = "dynamic")

    #contributions
    public_pages = db.relationship("PublicPage", 
        primaryjoin = "and_(PublicPage.creator_id == User.id, PublicPage.status != %d)" % PublicPageStatusChoices.DELETED, 
        backref = "creator", 
        lazy = "dynamic")

    #emails
    emails = db.relationship("Email", 
        primaryjoin = "and_(Email.user_id == User.id, Email.status != %d)" % EmailStatusChoices.DELETED, 
        backref = "user", 
        lazy = "dynamic")

    #follows
    following = db.relationship('User',
        secondary = 'follow', 
        primaryjoin = "and_(User.id == Follow.follower_id, User.status != %d)" % UserStatusChoices.DELETED, 
        secondaryjoin = "and_(Follow.followed_id == User.id, Follow.status == %d)" % FollowStatusChoices.FOLLOWING, 
        backref = db.backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')

    #profile
    profile = db.relationship('UserProfile', uselist = False)

    #thanks
    thanks_given = db.relationship("Thank", 
        primaryjoin="and_(Thank.giver_id == User.id, Thank.status != %d)" % ThankStatusChoices.DELETED, 
        backref = "giver", 
        lazy = "dynamic")

    thanks_received = db.relationship('Thank',
        secondary = 'thank_received_by_user', 
        primaryjoin = "and_(ThankReceivedByUser.receiver_id == User.id, ThankReceivedByUser.status != %d)" % ThankReceivedByUserStatusChoices.DELETED, 
        secondaryjoin = "and_(Thank.id == ThankReceivedByUser.thank_id, Thank.status != %d)" % ThankStatusChoices.DELETED, 
        backref = db.backref('receiver_users', lazy = 'dynamic'), 
        lazy = 'dynamic')

    def __init__(self, password, status = UserStatusChoices.NEW, language = 'en'):
        self.password = md5(password).hexdigest()
        self.status = status
        self.language = language
        self.date_registered = self.date_status_updated = self.date_last_acted = datetime.utcnow()

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
        self.date_status_updated = datetime.utcnow()
        return self

    def is_activated(self):
        return self.status == UserStatusChoices.ACTIVE

    def make_activated(self):
        self.status = UserStatusChoices.ACTIVE
        self.date_status_updated = datetime.utcnow()
        return self

    def is_deactivated(self):
        return self.status == UserStatusChoices.INACTIVE

    def make_deactivated(self):
        self.status = UserStatusChoices.INACTIVE
        self.date_status_updated = datetime.utcnow()
        return self

    def is_reported(self):
        return self.status == UserStatusChoices.REPORTED

    def make_reported(self):
        self.status = UserStatusChoices.REPORTED
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == UserStatusChoices.DELETED

    def make_deleted(self):
        self.status = UserStatusChoices.DELETED
        self.date_status_updated = datetime.utcnow()
        return self

    def match_password(self, password):
        return self.password == md5(password).hexdigest()

    def change_password(self, new_password):
        self.password = md5(new_password).hexdigest()
        self.date_changed_password = datetime.utcnow()
        return self

    def set_reset_password_key(self):
        self.reset_password_key = Functions.generate_key(email)
        self.date_set_reset_password_key = datetime.utcnow()
        return self

    def can_reset_password(self, reset_password_key):
        return self.reset_password_key != None and self.reset_password_key == reset_password_key and datetime.utcnow() < self.date_set_reset_password_key + timedelta(days=1)

    def reset_password(self, new_password):
        self.change_password(new_password)
        self.reset_password_key = None
        self.date_set_reset_password_key = None
        return self
 
    def get_primary_email(self):
        return Email.get_primary_email_by_user_id(self.id)

    def update_date_last_acted(self):
        self.date_last_acted = datetime.utcnow()
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
        return User.query.filter(User.username == username, User.status != 4).first()

    @staticmethod
    def get_user_by_email(email):
        user = getattr(Email.get_email_by_email(email), 'user', None)
        if user != None and user.is_not_deleted():
            return user
        return None

    @staticmethod
    def sign_in_by_email(email, password):
        user = User.get_user_by_email(email)
        if user != None and user.password == md5(password).hexdigest():
            return user
        return None

    @staticmethod
    def sign_in_by_username(username, password):
        return User.query.filter(User.username == username, User.password == md5(password).hexdigest(), User.status != UserStatusChoices.DELETED).first()

    @staticmethod
    def is_unique_username(username):
        return username not in FORBIDDEN_USERNAMES and User.query.filter(User.username == username, User.status != UserStatusChoices.DELETED).first() == None

    @staticmethod
    def make_unique_username(username):
        if User.is_unique_username(username): 
            return username
        count = 2
        username += str(count) 
        while User.is_unique_username(username) != True:
            count += 1
            username = username[:-1] + str(count)
        return username


class UserProfile(db.Model):

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    name = db.Column(db.String(32), nullable = False)

    avatar = db.Column(db.String(32))
    bio = db.Column(db.String(500))
    facebook_username = db.Column(db.String(32))
    is_facebook_visible = db.Column(db.Boolean)
    twitter_username = db.Column(db.String(32))
    is_twitter_visible = db.Column(db.Boolean)
    website = db.Column(db.String(500))

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    def __repr__(self):
        return "<UserProfile %r - %s>" % (self.user_id, self.name)