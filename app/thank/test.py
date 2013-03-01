#!/usr/bin/env python
import os
import unittest
from hashlib import md5
from sqlalchemy import or_, desc

from config import BASEDIR
from app import app, db
from app.user.models import Email, Follow, User, UserProfile
from app.publicpage.models import Media
from app.thank.models import Thank, ThankReceivedByEmail, ThankReceivedByPublicPage, ThankReceivedByUser
from app.test import BaseTestCase

class TestCase(BaseTestCase):

    def test(self):
        u1_name = 'john'
        u2_name = 'susan'
        u3_name = 'mary'
        u4_name = 'david'

        u1_email = 'john@example.com'
        u2_email = 'susan@example.com'
        u3_email = 'mary@example.com'
        u4_email = 'david@example.com'
        
        u1_password = 'john123'
        u2_password = 'susan123'
        u3_password = 'mary123'
        u4_password = 'david123'

        # make four users
        u1 = User(password = u1_password)
        u2 = User(password = u2_password)
        u3 = User(password = u3_password)
        u4 = User(password = u4_password)        

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

        assert u1.get_primary_email().email == e1.email
        assert u2.get_primary_email().email == e2.email
        assert u3.get_primary_email().email == e3.email
        assert u4.get_primary_email().email == e4.email

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

        # make four thanks

        t1 = Thank(u1.id)
        t2 = Thank(u2.id)
        t3 = Thank(u3.id)
        t4 = Thank(u4.id)

        db.session.add(t1)
        db.session.add(t2)
        db.session.add(t3)
        db.session.add(t4)
        db.session.commit()

        assert len(u1.thanks_given.all()) == 1
        assert len(u2.thanks_given.all()) == 1
        assert len(u3.thanks_given.all()) == 1
        assert len(u4.thanks_given.all()) == 1

        # thank to users

        t1u1 = ThankReceivedByUser(t1.id, u1.id)
        t1u2 = ThankReceivedByUser(t1.id, u2.id)
        t1u3 = ThankReceivedByUser(t1.id, u3.id)
        t1u4 = ThankReceivedByUser(t1.id, u4.id)

        t2u1 = ThankReceivedByUser(t2.id, u1.id)
        t2u2 = ThankReceivedByUser(t2.id, u2.id)
        t2u3 = ThankReceivedByUser(t2.id, u3.id)

        t3u1 = ThankReceivedByUser(t3.id, u1.id)
        t3u2 = ThankReceivedByUser(t3.id, u2.id)

        t4u1 = ThankReceivedByUser(t4.id, u1.id)

        db.session.add(t1u1)
        db.session.add(t1u2)
        db.session.add(t1u3)
        db.session.add(t1u4)
        db.session.add(t2u1)
        db.session.add(t2u2)
        db.session.add(t2u3)
        db.session.add(t3u1)
        db.session.add(t3u2)
        db.session.add(t4u1)
        db.session.commit()

        assert len(u1.thanks_received.all()) == 4
        assert len(u2.thanks_received.all()) == 3
        assert len(u3.thanks_received.all()) == 2
        assert len(u4.thanks_received.all()) == 1

        # delete thank

        t1.make_deleted()
        db.session.add(t1)
        db.session.commit()

        assert len(u1.thanks_received.all()) == 3
        assert len(u2.thanks_received.all()) == 2
        assert len(u3.thanks_received.all()) == 1
        assert len(u4.thanks_received.all()) == 0

        # delete thank to user

        t2u1.make_deleted()
        db.session.add(t2u1)
        db.session.commit()

        assert len(u1.thanks_received.all()) == 2
        assert len(u2.thanks_received.all()) == 2
        assert len(u3.thanks_received.all()) == 1
        assert len(u4.thanks_received.all()) == 0

        # follow users

        u1u1 = Follow(u1.id, u1.id)
        u1u2 = Follow(u1.id, u2.id)
        u1u3 = Follow(u1.id, u3.id)
        u1u4 = Follow(u1.id, u4.id)

        u2u1 = Follow(u2.id, u1.id)
        u2u2 = Follow(u2.id, u2.id)
        u2u3 = Follow(u2.id, u3.id)

        u3u1 = Follow(u3.id, u1.id)
        u3u2 = Follow(u3.id, u2.id)

        u4u1 = Follow(u4.id, u1.id)

        db.session.add(u1u1)
        db.session.add(u1u2)
        db.session.add(u1u3)
        db.session.add(u1u4)
        db.session.add(u2u1)
        db.session.add(u2u2)
        db.session.add(u2u3)
        db.session.add(u3u1)
        db.session.add(u3u2)
        db.session.add(u4u1)
        db.session.commit()

        assert len(u1.following.all()) == 4
        assert len(u2.following.all()) == 3
        assert len(u3.following.all()) == 2
        assert len(u4.following.all()) == 1

        # unfollow users

        u1u1.make_deleted()
        u2u2.make_deleted()

        db.session.add(u1u1)
        db.session.add(u2u2)
        db.session.commit()

        assert len(u1.following.all()) == 3
        assert len(u2.following.all()) == 2
        assert len(u3.following.all()) == 2
        assert len(u4.following.all()) == 1

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

        assert u2 in u1.following.all()
        assert u3 not in u1.following.all()

        assert len(u1.following.all()) == 2
        assert len(u2.following.all()) == 1
        assert len(u3.following.all()) == 2
        assert len(u4.following.all()) == 1

if __name__ == '__main__':
    unittest.main()
