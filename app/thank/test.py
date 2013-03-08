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

        # delete thank to user
            # number of thanks_received decreases

        t2u1.make_deleted()
        db.session.add(t2u1)
        db.session.commit()

        assert len(u1.thanks_received.all()) == 3
        assert len(u2.thanks_received.all()) == 3
        assert len(u3.thanks_received.all()) == 2
        assert len(u4.thanks_received.all()) == 1

        # make four emails

        e5 = Email(email = 'fight@fight.com')
        e6 = Email(email = 'go@go.com')
        e7 = Email(email = 'further@further.com')
        e8 = Email(email = 'win@win.com')

        db.session.add(e5)
        db.session.add(e6)
        db.session.add(e7)
        db.session.add(e8)
        db.session.commit()

        # thank to emails

        t1e5 = ThankReceivedByEmail(t1.id, e5.id)
        t1e6 = ThankReceivedByEmail(t1.id, e6.id)
        t1e7 = ThankReceivedByEmail(t1.id, e7.id)
        t1e8 = ThankReceivedByEmail(t1.id, e8.id)

        t2e5 = ThankReceivedByEmail(t2.id, e5.id)
        t2e6 = ThankReceivedByEmail(t2.id, e6.id)
        t2e7 = ThankReceivedByEmail(t2.id, e7.id)

        t3e5 = ThankReceivedByEmail(t3.id, e5.id)
        t3e6 = ThankReceivedByEmail(t3.id, e6.id)

        t4e5 = ThankReceivedByEmail(t4.id, e5.id)

        db.session.add(t1e5)
        db.session.add(t1e6)
        db.session.add(t1e7)
        db.session.add(t1e8)
        db.session.add(t2e5)
        db.session.add(t2e6)
        db.session.add(t2e7)
        db.session.add(t3e5)
        db.session.add(t3e6)
        db.session.add(t4e5)
        db.session.commit()

        assert len(e5.thanks_received.all()) == 4
        assert len(e6.thanks_received.all()) == 3
        assert len(e7.thanks_received.all()) == 2
        assert len(e8.thanks_received.all()) == 1

        # email added to a user's account

        e5.user_id = u1.id
        db.session.add(e5)
        for thank in e5.thanks_received.all():
            if thank not in e5.user.thanks_received.all():
                thank_received_by_user = ThankReceivedByUser(thank_id = thank.id, receiver_id = e5.user_id)
                db.session.add(thank_received_by_user)
                db.session.commit()
            thank_received_by_email = ThankReceivedByEmail.get_thank_received_by_email_by_thank_and_receiver(thank.id, e5.id)
            thank_received_by_email.make_migrated(e5.user_id)
            db.session.add(thank_received_by_email)
            db.session.commit()

        assert len(e5.thanks_received.all()) == 0
        assert len(u1.thanks_received.all()) == 4
        print u1.thanks_received.order_by(Thank.date_registered).all()

        # delete thank to email
            # number of thanks_received decreases

        t2e5.make_deleted()
        db.session.add(t2e5)
        db.session.commit()

        assert len(e5.thanks_received.all()) == 0
        assert len(e6.thanks_received.all()) == 3
        assert len(e7.thanks_received.all()) == 2
        assert len(e8.thanks_received.all()) == 1

        # delete thank
            # number of thanks_received decreases

        t1.make_deleted()
        db.session.add(t1)
        db.session.commit()

        assert len(u1.thanks_received.all()) == 3
        assert len(u2.thanks_received.all()) == 2
        assert len(u3.thanks_received.all()) == 1
        assert len(u4.thanks_received.all()) == 0

        assert len(e5.thanks_received.all()) == 0
        assert len(e6.thanks_received.all()) == 2
        assert len(e7.thanks_received.all()) == 1
        assert len(e8.thanks_received.all()) == 0

        assert all(email in t1.receiver_emails.all() for email in [e6,e7,e8])


if __name__ == '__main__':
    unittest.main()
