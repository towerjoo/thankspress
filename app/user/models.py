from app import db
from app.functions import Functions
from app.public_page.choices import PublicPageStatusChoices
from app.thank.choices import ThankCommentStatusChoices, ThankStatusChoices, \
    ThankReceivedByEmailStatusChoices, ThankReceivedByUserStatusChoices
from app.user.choices import EmailStatusChoices, FollowStatusChoices, UserStatusChoices

from config import FORBIDDEN_USERNAMES
from datetime import datetime, timedelta
from hashlib import md5

class Email(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(320), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    is_primary = db.Column(db.Boolean, nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)
    verification_key = db.Column(db.String(32)) # To be deleted once verified

    thanks_received = db.relationship('Thank',
        secondary = 'thank_received_by_email', 
        primaryjoin = "and_(ThankReceivedByEmail.receiver_id == Email.id, ThankReceivedByEmail.status != %d)" % ThankReceivedByEmailStatusChoices.DELETED, 
        secondaryjoin = "and_(Thank.id == ThankReceivedByEmail.thank_id, Thank.status != %d)" % ThankStatusChoices.DELETED, 
        backref = db.backref('receiver_emails', lazy = 'dynamic'), 
        lazy = 'dynamic')

    def __init__(self, email, user_id, is_primary = False, status = EmailStatusChoices.NOT_VERIFIED):
        self.email = email
        self.user_id = user_id
        self.is_primary = is_primary
        self.status = status
        self.date_registered = datetime.utcnow()
        self.verification_key = Functions.generate_key(email)

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
        self.verification_key = Functions.generate_key(self.mail)
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


class Profile(db.Model):

    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    name = db.Column(db.String(32), nullable = False)
    
    picture_id = db.Column(db.Integer, db.ForeignKey("media.id"))
    bio = db.Column(db.String(500))
    website = db.Column(db.String(500))

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return "<UserProfile %r - %s>" % (self.id, self.name)


class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.String(32), nullable = False)
    language = db.Column(db.String(5), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)

    date_last_signed_in = db.Column(db.DateTime)
    date_last_acted = db.Column(db.DateTime)
    username = db.Column(db.String(32))
    password_reset_key = db.Column(db.String(32))
    password_reset_key_expiration_date = db.Column(db.DateTime)

    # Email
    emails = db.relationship("Email", 
        primaryjoin = "and_(Email.user_id == User.id, Email.status != %d)" % EmailStatusChoices.DELETED, 
        backref = "user", 
        lazy = "dynamic")

    # Follow
    following = db.relationship('User',
        secondary = 'follow', 
        primaryjoin = "and_(User.id == Follow.follower_id, User.status != %d)" % UserStatusChoices.DELETED, 
        secondaryjoin = "and_(Follow.followed_id == User.id, Follow.status == %d)" % FollowStatusChoices.FOLLOWING, 
        backref = db.backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')

    # Profile
    profile = db.relationship('Profile', uselist = False)

    # PublicPage
    public_pages = db.relationship("PublicPage", 
        primaryjoin = "and_(PublicPage.creator_id == User.id, PublicPage.status != %d)" % PublicPageStatusChoices.DELETED, 
        backref = "creator", 
        lazy = "dynamic")

    # Thank
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

    # ThankComment
    comments = db.relationship("ThankComment", 
        primaryjoin = "and_(ThankComment.commenter_id == User.id, ThankComment.status != %d)" % ThankCommentStatusChoices.DELETED, 
        backref = "commenter", 
        lazy = "dynamic")

    def __init__(self, password, status = UserStatusChoices.NEW, language = 'en'):
        self.password = md5(password).hexdigest()
        self.status = status
        self.date_registered = datetime.utcnow()
        self.language = language

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
        return self.password == md5(password).hexdigest()

    def change_password(self, new_password):
        self.password = md5(new_password).hexdigest()
        self.date_changed_password = datetime.utcnow()
        return self

    def set_password_reset_key(self):
        self.password_reset_key = Functions.generate_key(email)
        self.password_reset_key_expiration_date = datetime.utcnow() + timedelta(days=1)
        return self

    def can_reset_password(self, password_reset_key):
        return self.password_reset_key != None and self.password_reset_key == password_reset_key and self.password_reset_key_expiration_date > datetime.utcnow()

    def reset_password(self, new_password):
        self.change_password(new_password)
        self.password_reset_key = None
        self.password_reset_key_expiration_date = None
        return self
 
    def get_primary_email(self):
        return Email.get_primary_email_by_user_id(self.id)

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