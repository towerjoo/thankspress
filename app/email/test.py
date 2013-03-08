import os
import unittest

from app import app, db
from app.email.models import Email
from app.user.models import User, UserProfile
from app.thank.models import Media, Thank, ThankReceivedByEmail, ThankReceivedByPublicPage, ThankReceivedByUser
from app.test import BaseTestCase

from config import BASEDIR
from hashlib import md5
from sqlalchemy import or_, desc

class TestCase(BaseTestCase):

    def test(self):
        u1_name = 'john'
        u2_name = 'susan'
        u3_name = 'mary'
        u4_name = 'david'

        u1_username = 'john'
        u2_username = 'susan'
        u3_username = 'mary'
        u4_username = 'david'

        u1_email = 'john@example.com'
        u2_email = 'susan@example.com'
        u3_email = 'mary@example.com'
        u4_email = 'david@example.com'
        
        u1_password = 'john123'
        u2_password = 'susan123'
        u3_password = 'mary123'
        u4_password = 'david123'

        # make four users
        u1 = User(password = u1_password, username = u1_username)
        u2 = User(password = u2_password, username = u2_username)
        u3 = User(password = u3_password, username = u3_username)
        u4 = User(password = u4_password, username = u4_username)    

        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()

        up1 = UserProfile(user_id = u1.id, name = u1_name)
        up2 = UserProfile(user_id = u2.id, name = u2_name)
        up3 = UserProfile(user_id = u3.id, name = u3_name)
        up4 = UserProfile(user_id = u4.id, name = u4_name)

        db.session.add(up1)
        db.session.add(up2)
        db.session.add(up3)
        db.session.add(up4)
        db.session.commit()

        # make four emails for four users
        e1 = Email(email = u1_email, user_id = u1.id, is_primary = True)
        e2 = Email(email = u2_email, user_id = u2.id, is_primary = True)
        e3 = Email(email = u3_email, user_id = u3.id, is_primary = True)
        e4 = Email(email = u4_email, user_id = u4.id, is_primary = True)

        db.session.add(e1)
        db.session.add(e2)
        db.session.add(e3)
        db.session.add(e4)
        db.session.commit()

        assert u1.primary_email.email == e1.email
        assert u2.primary_email.email == e2.email
        assert u3.primary_email.email == e3.email
        assert u4.primary_email.email == e4.email

        # make additional emails for three users
        e5 = Email(email = u1.profile.name + '@example2.com', user_id = u1.id)
        e6 = Email(email = u1.profile.name + '@example3.com', user_id= u1.id)
        e7 = Email(email = u1.profile.name + '@example4.com', user_id= u1.id)
        e8 = Email(email = u2.profile.name + '@example2.com', user_id= u2.id)
        e9 = Email(email = u2.profile.name + '@example3.com', user_id = u2.id)
        e10 = Email(email = u3.profile.name + '@example2.com', user_id= u3.id)

        db.session.add(e5)
        db.session.add(e6)
        db.session.add(e7)
        db.session.add(e8)
        db.session.add(e9)
        db.session.add(e10)
        db.session.commit()

        emails = u1.emails.order_by(Email.date_registered).all()

        assert emails[0] is e1
        assert emails[1] is e5
        assert emails[2] is e6
        assert emails[3] is e7

        emails = u2.emails.order_by(Email.date_registered.desc()).all()

        assert emails[2] is e2
        assert emails[1] is e8
        assert emails[0] is e9

        emails = u3.emails.order_by(Email.date_registered).all()

        assert emails[0] is e3
        assert emails[1] is e10

        assert u4.emails.first() is e4

        # change user statuses

        u2.make_deactivated()
        u3.make_deleted()

        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()

        assert u2.is_deactivated() == True
        assert u2.is_activated() == False
        assert u2.is_active() == True
        assert u3.is_deleted() == True
        assert u3.is_not_deleted() == False

if __name__ == '__main__':
    unittest.main()
