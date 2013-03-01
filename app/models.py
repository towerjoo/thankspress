from app import db
from hashlib import md5
from datetime import datetime, timedelta
from sqlalchemy import desc, or_
from config import FORBIDDEN_USERNAMES
from functions import AF
from choices import CommentStatusChoices


class Comment(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    comment = db.Column(db.String(5000), nullable = False)
    thank_id = db.Column(db.Integer, db.ForeignKey("thank.id"), nullable = False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) 
    date_registered = db.Column(db.DateTime, nullable = False)
    
    comment_language = db.Column(db.String(5))
    date_status_updated = db.Column(db.DateTime)

    def __init__(self, comment, thank_id, commenter_id, comment_language = None, 
                            status = CommentStatusChoices.VISIBLE):
        self.comment = comment
        self.thank_id = thank_id
        self.commenter_id = commenter_id
        self.status = status
        self.date_registered = datetime.utcnow()
        self.comment_language = comment_language

    def __repr__(self):
        return "<Comment %r>" % (self.id)

    def is_visible(self):
        return self.status == CommentStatusChoices.VISIBLE

    def make_visible(self):
        self.status = CommentStatusChoices.VISIBLE
        self.date_status_updated = datetime.utcnow()
        return self

    def is_reported(self):
        return self.status == CommentStatusChoices.REPORTED

    def make_reported(self):
        self.status = CommentStatusChoices.REPORTED
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == CommentStatusChoices.DELETED

    def make_deleted(self):
        self.status = CommentStatusChoices.DELETED
        self.date_status_updated = datetime.utcnow()
        return self

    @staticmethod
    def get_comment(id):
        # add exceptions handling, possible exceptions incl:
        # 1. id is from user's input and not a number, then int(id) will raise an exception
        # 2. Model.query.get may raise some exceptions
        try:
            comment = Comment.query.get(int(id))
            return comment
        except:
            return None


class Email(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(320), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    is_primary = db.Column(db.Boolean, nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) # 0- Not Verified 1- Verified 2- Reported 3- Deleted
    date_registered = db.Column(db.DateTime, nullable = False)

    verification_key = db.Column(db.String(32))
    date_status_updated = db.Column(db.DateTime)

    thanks_received = db.relationship('Thank',
        secondary = 'thank_received_by_email', 
        primaryjoin = "and_(ThankReceivedByEmail.receiver_id == Email.id, ThankReceivedByEmail.status != 3)", 
        secondaryjoin = "and_(Thank.id == ThankReceivedByEmail.thank_id, Thank.status != 4)", 
        backref = db.backref('receiver_emails', lazy = 'dynamic'), 
        lazy = 'dynamic')

    def __init__(self, email, user_id, is_primary = False, status = 0):
        self.email = email
        self.user_id = user_id
        self.verification_key = AF.generate_key(email)
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
        return self.status == 0

    def make_not_verified(self):
        self.status = 0
        self.date_status_updated = datetime.utcnow()
        self.verification_key = AF.generate_key(self.mail)
        return self

    def is_verified(self):
        return self.status == 1

    def make_verified(self):
        self.status = 1
        self.date_status_updated = datetime.utcnow()
        self.verification_key = None
        return self

    def is_reported(self):
        return self.status == 2

    def make_reported(self):
        self.status = 2
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == 3

    def make_deleted(self):
        self.status = 3
        self.is_primary = False
        self.date_status_updated = datetime.utcnow()
        return self

    @staticmethod
    def get_email(id):
        return Email.query.get(int(id))

    @staticmethod
    def get_email_by_email(email):
        return Email.query.filter(Email.email == email, Email.status != 3).first()

    @staticmethod
    def get_primary_email_by_email(email):
        return Email.query.filter(Email.email == email, Email.is_primary == True).first()

    @staticmethod
    def get_primary_email_by_user_id(user_id):
        return Email.query.filter(Email.user_id == user_id, Email.is_primary == True).first()

    @staticmethod
    def is_unique_email(email):
        return Email.query.filter(Email.email == email, Email.status != 3).first() == None

class Follow(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    date_registered = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) # 1- Following 2- Deleted

    date_status_updated = db.Column(db.DateTime)

    def __init__(self, follower_id, followed_id, status = 1):
        self.follower_id = follower_id
        self.followed_id = followed_id
        self.date_registered = datetime.utcnow()
        self.status = status

    def __repr__(self):
        return '<Follow %r>' % (self.id)

    def is_following(self):
        return self.status == 1

    def make_following(self):
        self.status = 1
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == 2

    def make_deleted(self):
        self.status = 2
        self.date_status_updated = datetime.utcnow()
        return self

    @staticmethod
    def get_follow(id):
        return Follow.query.get(int(id))

    @staticmethod
    def is_following_by_follower_and_followed(follower_id, followed_id):
        return Follow.query.filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id, Follow.status == 1).first() != None

    @staticmethod
    def get_follow_by_follower_and_followed(follower_id, followed_id):
        return Follow.query.filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id, Follow.status == 1).first()

    @staticmethod
    def get_deleted_follows_by_follower_and_followed(follower_id, followed_id):
        return Follow.query.filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id, Follow.status == 2).all()


class Media(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.SmallInteger, nullable = False) # 1- Image 2- Video 3- YouTube Video
    path = db.Column(db.String(500), nullable = False)
    date_registered = db.Column(db.DateTime, nullable = False)

    thank = db.relationship("Thank", 
        primaryjoin="and_(Thank.media_id == Media.id, Thank.status != 4)", 
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
        return Media.query.get(int(id))


class PublicPage(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) # 0- Not Verified 1- Verified 2- Reported 3- Deleted
    date_registered = db.Column(db.DateTime, nullable = False)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    
    date_status_updated = db.Column(db.DateTime)

    thanks_received = db.relationship('Thank',
        secondary = 'thank_received_by_public_page', 
        primaryjoin = "and_(ThankReceivedByPublicPage.receiver_id == PublicPage.id, ThankReceivedByPublicPage.status != 3)", 
        secondaryjoin = "and_(Thank.id == ThankReceivedByPublicPage.thank_id, Thank.status != 4)", 
        backref = db.backref('receiver_public_pages', lazy = 'dynamic'), 
        lazy = 'dynamic')

    def __init__(self, name, creator_id, status = 0):
        self.name = name
        self.creator_id = creator_id
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<PublicPage %r>' % (self.id)

    def is_not_verified(self):
        return self.status == 0

    def make_not_verified(self):
        self.status = 0
        self.date_status_updated = datetime.utcnow()
        return self

    def is_verified(self):
        return self.status == 1

    def make_verified(self):
        self.status = 1
        self.date_status_updated = datetime.utcnow()
        return self

    def is_reported(self):
        return self.status == 2

    def make_reported(self):
        self.status = 2
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == 3

    def make_deleted(self):
        self.status = 3
        self.date_status_updated = datetime.utcnow()
        return self

    @staticmethod
    def get_public_page(id):
        return Email.query.get(int(id))


class Thank(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    giver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) # 1- Public 2- Private 3- Reported 4- Deleted
    date_registered = db.Column(db.DateTime, nullable = False)

    message = db.Column(db.String(5000))
    message_language = db.Column(db.String(5))
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"))
    date_status_updated = db.Column(db.DateTime)

    comments = db.relationship("Comment", 
        primaryjoin = "and_(Comment.thank_id == Thank.id, Comment.status != 3)",
        backref = "thank", 
        lazy = "dynamic")

    def __init__(self, giver_id, message = None, message_language = None, media_id = None, status = 1):
        self.giver_id = giver_id
        self.status = status
        self.date_registered = datetime.utcnow()
        self.message = message
        self.message_language = message_language
        self.media_id = media_id

    def __repr__(self):
        return "<Thank %r>" % (self.id)

    def is_public(self):
        return self.status == 1

    def make_public(self):
        self.status = 1
        self.date_status_updated = datetime.utcnow()
        return self

    def is_private(self):
        return self.status == 2

    def make_private(self):
        self.status = 2
        self.date_status_updated = datetime.utcnow()
        return self

    def is_reported(self):
        return self.status == 3

    def make_reported(self):
        self.status = 3
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == 4

    def make_deleted(self):
        self.status = 4
        self.date_status_updated = datetime.utcnow()
        return self

    @staticmethod
    def get_thank(id):
        return Thank.query.get(int(id))


class ThankReceivedByEmail(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    thank_id = db.Column(db.Integer, db.ForeignKey("thank.id"), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("email.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) # 0- User Not Found 1- Migrated 2- Reported 3- Deleted
    date_registered = db.Column(db.DateTime, nullable = False)

    date_status_updated = db.Column(db.DateTime)

    def __init__(self, thank_id, receiver_id, status = 0):
        self.thank_id = thank_id
        self.receiver_id = receiver_id
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<ThankReceivedByEmail %r>' % (self.id)

    def is_user_not_found(self):
        return self.status == 0

    def make_user_not_found(self):
        self.status = 0
        self.date_status_updated = datetime.utcnow()
        return self

    def is_migrated(self):
        return self.status == 1

    def make_migrated(self):
        self.status = 1
        self.date_status_updated = datetime.utcnow()
        return self

    def is_reported(self):
        return self.status == 2

    def make_reported(self):
        self.status = 2
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == 3

    def make_deleted(self):
        self.status = 3
        self.date_status_updated = datetime.utcnow()
        return self


class ThankReceivedByPublicPage(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    thank_id = db.Column(db.Integer, db.ForeignKey("thank.id"), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("public_page.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) # 1- Visible 2- Reported 3- Deleted
    date_registered = db.Column(db.DateTime, nullable = False)

    date_status_updated = db.Column(db.DateTime)

    def __init__(self, thank_id, receiver_id, status = 1):
        self.thank_id = thank_id
        self.receiver_id = receiver_id
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<ThankReceivedByPublicPage %r>' % (self.id)

    def is_visible(self):
        return self.status == 1

    def make_visible(self):
        self.status = 1
        self.date_status_updated = datetime.utcnow()
        return self

    def is_reported(self):
        return self.status == 2

    def make_reported(self):
        self.status = 2
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == 3

    def make_deleted(self):
        self.status = 3
        self.date_status_updated = datetime.utcnow()
        return self


class ThankReceivedByUser(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    thank_id = db.Column(db.Integer, db.ForeignKey("thank.id"), nullable = False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) # 0- Unread 1- Visible 2- Hidden 3- Reported 4- Deleted
    date_registered = db.Column(db.DateTime, nullable = False)
    
    date_status_updated = db.Column(db.DateTime)

    def __init__(self, thank_id, receiver_id, status = 0):
        self.thank_id = thank_id
        self.receiver_id = receiver_id
        self.status = status
        self.date_registered = datetime.utcnow()

    def __repr__(self):
        return '<ThankReceivedByUser %r>' % (self.id)

    def is_unread(self):
        return self.status == 0

    def make_unread(self):
        self.status = 0
        self.date_status_updated = datetime.utcnow()
        return self

    def is_visible(self):
        return self.status == 1

    def make_visible(self):
        self.status = 1
        self.date_status_updated = datetime.utcnow()
        return self

    def is_hidden(self):
        return self.status == 2

    def make_hidden(self):
        self.status = 2
        self.date_status_updated = datetime.utcnow()
        return self

    def is_reported(self):
        return self.status == 3

    def make_reported(self):
        self.status = 3
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == 4

    def make_deleted(self):
        self.status = 4
        self.date_status_updated = datetime.utcnow()
        return self


class User(db.Model):

    #account
    id = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.String(32), nullable = False)
    status = db.Column(db.SmallInteger, nullable = False) # 0- New 1- Active 2- Deactivated 3- Reported 4- Deleted
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
        primaryjoin = "and_(Comment.commenter_id == User.id, Comment.status != 3)", 
        backref = "commenter", 
        lazy = "dynamic")

    #contributions
    public_pages = db.relationship("PublicPage", 
        primaryjoin = "and_(PublicPage.creator_id == User.id, PublicPage.status != 3)", 
        backref = "creator", 
        lazy = "dynamic")

    #emails
    emails = db.relationship("Email", 
        primaryjoin = "and_(Email.user_id == User.id, Email.status != 3)", 
        backref = "user", 
        lazy = "dynamic")

    #follows
    following = db.relationship('User',
        secondary = 'follow', 
        primaryjoin = "and_(User.id == Follow.follower_id, User.status != 4)", 
        secondaryjoin = "and_(Follow.followed_id == User.id, Follow.status == 1)", 
        backref = db.backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')

    #profile
    profile = db.relationship('UserProfile', uselist = False)

    #thanks
    thanks_given = db.relationship("Thank", 
        primaryjoin="and_(Thank.giver_id == User.id, Thank.status != 4)", 
        backref = "giver", 
        lazy = "dynamic")

    thanks_received = db.relationship('Thank',
        secondary = 'thank_received_by_user', 
        primaryjoin = "and_(ThankReceivedByUser.receiver_id == User.id, ThankReceivedByUser.status != 4)", 
        secondaryjoin = "and_(Thank.id == ThankReceivedByUser.thank_id, Thank.status != 4)", 
        backref = db.backref('receiver_users', lazy = 'dynamic'), 
        lazy = 'dynamic')

    def __init__(self, password, status = 0, language = 'en'):
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
        return self.status == 0

    def make_new(self):
        self.status = 0
        self.date_status_updated = datetime.utcnow()
        return self

    def is_activated(self):
        return self.status == 1

    def make_activated(self):
        self.status = 1
        self.date_status_updated = datetime.utcnow()
        return self

    def is_deactivated(self):
        return self.status == 2

    def make_deactivated(self):
        self.status = 2
        self.date_status_updated = datetime.utcnow()
        return self

    def is_reported(self):
        return self.status == 3

    def make_reported(self):
        self.status = 3
        self.date_status_updated = datetime.utcnow()
        return self

    def is_not_deleted(self):
        return not self.is_deleted()

    def is_deleted(self):
        return self.status == 4

    def make_deleted(self):
        self.status = 4
        self.date_status_updated = datetime.utcnow()
        return self

    def match_password(self, password):
        return self.password == md5(password).hexdigest()

    def change_password(self, new_password):
        self.password = md5(new_password).hexdigest()
        self.date_changed_password = datetime.utcnow()
        return self

    def set_reset_password_key(self):
        self.reset_password_key = AF.generate_key(email)
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
        return User.query.get(int(id))

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
        return User.query.filter(User.username == username, User.password == md5(password).hexdigest(), User.status != 4).first()

    @staticmethod
    def is_unique_username(username):
        return username not in FORBIDDEN_USERNAMES and User.query.filter(User.username == username, User.status != 4).first() == None

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
