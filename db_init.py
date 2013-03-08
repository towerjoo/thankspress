#!venv/bin/python
from app import db
from app.media.models import Media
from app.media.choices import MediaTypeChoices
from app.user.models import User, UserProfile
from app.email.models import Email
from app.thank.models import Thank, ThankReceivedByUser, ThankReceivedByEmail

if Media.query.all() == []:
    profile_pic = Media(type = MediaTypeChoices.PROFILE_PICTURE, path = 'PROFILE_PICTURE/default.png')
    db.session.add(profile_pic)
    db.session.commit()

    # For test purposes

    u1_name = 'john'
    u2_name = 'susan'
    u3_name = 'mary'
    u4_name = 'david'

    u1_username = 'john'
    u2_username = 'susan'
    u3_username = 'mary'
    u4_username = 'david'

    u1_email = 'john@creco.co'
    u2_email = 'susan@creco.co'
    u3_email = 'mary@creco.co'
    u4_email = 'david@creco.co'
    
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

    # thank to users

    t1u2 = ThankReceivedByUser(t1.id, u2.id)
    t1u3 = ThankReceivedByUser(t1.id, u3.id)
    t1u4 = ThankReceivedByUser(t1.id, u4.id)

    t2u1 = ThankReceivedByUser(t2.id, u1.id)
    t2u3 = ThankReceivedByUser(t2.id, u3.id)

    t3u1 = ThankReceivedByUser(t3.id, u1.id)
    t3u2 = ThankReceivedByUser(t3.id, u2.id)

    t4u1 = ThankReceivedByUser(t4.id, u1.id)

    db.session.add(t1u2)
    db.session.add(t1u3)
    db.session.add(t1u4)
    db.session.add(t2u1)
    db.session.add(t2u3)
    db.session.add(t3u1)
    db.session.add(t3u2)
    db.session.add(t4u1)
    db.session.commit()


    # delete thank to user
        # number of thanks_received decreases

    t2u1.make_deleted()
    db.session.add(t2u1)
    db.session.commit()


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