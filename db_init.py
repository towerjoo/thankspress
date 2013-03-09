#!venv/bin/python
from app import db
from app.media.models import Media
from app.media.choices import MediaTypeChoices
from app.follow.models import Follow
from app.user.models import User, UserProfile
from app.email.models import Email
from app.thank.models import Thank, ThankReceivedByUser, ThankReceivedByEmail

if Media.query.all() == []:
    profile_pic = Media(type = MediaTypeChoices.PROFILE_PICTURE, path = 'PROFILE_PICTURE/default.png')
    db.session.add(profile_pic)
    db.session.commit()

    # For test purposes

    u1_name = 'Dogukan Tufekci' # follows every registered user # thanks everyone #deleted
    u2_name = 'Batikan Tufekci' # follows none but himself # thanks none
    u3_name = 'Mustafa Demirkent' # follows all # thanks none # all thanks hidden (3)
    u4_name = 'Ali Ozdengiz' # follows dogukan and mustafa and himself # thanks dogukan and mustafa privately
    u5_name = 'Sukran Hoca' # follows every registered user # thanks everyone but mustafa and ali # deleted
    u6_name = 'Salih Yilmaz' # follows dogukan mustafa ali and himself # thanks dogukan mustafa ali
    # u7_name = 'Ali Yilmaz' # received thanks but not registered yet

    u1_username = 'dogukan'
    u2_username = 'batikan'
    u3_username = 'mustafa'
    u4_username = 'ali'
    u5_username = 'sukran'
    u6_username = 'salih'
    # u7 didn't registester yet

    u1_email = 'dogukan@creco.co'
    u2_email = 'batikan@creco.co'
    u3_email = 'mustafa@creco.co'
    u4_email = 'ali@creco.co'
    u5_email = 'sukran@creco.co'
    u6_email = 'salih@creco.co'

    u1_password = 'dogukan'
    u2_password = 'batikan'
    u3_password = 'mustafa'
    u4_password = 'ali'
    u5_password = 'sukran'
    u6_password = 'salih'

    # make 6 users
    u1 = User(password = u1_password, username = u1_username)
    u2 = User(password = u2_password, username = u2_username)
    u3 = User(password = u3_password, username = u3_username)
    u4 = User(password = u4_password, username = u4_username)        
    u5 = User(password = u5_password, username = u5_username) 
    u6 = User(password = u6_password, username = u6_username) 

    db.session.add(u1)
    db.session.add(u2)
    db.session.add(u3)
    db.session.add(u4)
    db.session.add(u5)
    db.session.add(u6)
    db.session.commit()

    up1 = UserProfile(user_id = u1.id, name = u1_name, picture_id = 1)
    up2 = UserProfile(user_id = u2.id, name = u2_name, picture_id = 1)
    up3 = UserProfile(user_id = u3.id, name = u3_name, picture_id = 1)
    up4 = UserProfile(user_id = u4.id, name = u4_name, picture_id = 1)
    up5 = UserProfile(user_id = u5.id, name = u5_name, picture_id = 1)
    up6 = UserProfile(user_id = u6.id, name = u6_name, picture_id = 1)

    db.session.add(up1)
    db.session.add(up2)
    db.session.add(up3)
    db.session.add(up4)
    db.session.add(up5)
    db.session.add(up6)
    db.session.commit()

    # make 6 emails for 6 users
    e1 = Email(email = u1_email, user_id = u1.id, is_primary = True, status = 1)
    e2 = Email(email = u2_email, user_id = u2.id, is_primary = True, status = 1)
    e3 = Email(email = u3_email, user_id = u3.id, is_primary = True, status = 1)
    e4 = Email(email = u4_email, user_id = u4.id, is_primary = True, status = 1)
    e5 = Email(email = u5_email, user_id = u5.id, is_primary = True, status = 1)
    e6 = Email(email = u6_email, user_id = u6.id, is_primary = True, status = 1)

    db.session.add(e1)
    db.session.add(e2)
    db.session.add(e3)
    db.session.add(e4)
    db.session.add(e5)
    db.session.add(e6)
    db.session.commit()

    # make four thanks

    t1 = Thank(giver_id = u1.id, message = 'Thanks everyone!', message_language = 'en')
    t4 = Thank(giver_id = u4.id, status = 2, message = 'Tesekkur ederim!', message_language = 'tr')
    t5 = Thank(giver_id = u5.id, message = 'Herseyi size borcluyum!', message_language = 'tr')
    t6 = Thank(giver_id = u6.id, message = 'Cheers brafs!')

    db.session.add(t1)
    db.session.add(t4)
    db.session.add(t5)
    db.session.add(t6)
    db.session.commit()

    # thank to users

    t1u1 = ThankReceivedByUser(t1.id, u1.id, status = 1)
    t1u2 = ThankReceivedByUser(t1.id, u2.id, status = 1)
    t1u3 = ThankReceivedByUser(t1.id, u3.id, status = 2)
    t1u4 = ThankReceivedByUser(t1.id, u4.id, status = 1)
    t1u5 = ThankReceivedByUser(t1.id, u5.id, status = 1)
    t1u6 = ThankReceivedByUser(t1.id, u6.id, status = 1)

    t4u1 = ThankReceivedByUser(t4.id, u1.id)
    t4u3 = ThankReceivedByUser(t4.id, u3.id, status = 2)

    t5u1 = ThankReceivedByUser(t5.id, u1.id, status = 1)
    t5u2 = ThankReceivedByUser(t5.id, u2.id, status = 1)
    t5u5 = ThankReceivedByUser(t5.id, u5.id, status = 1)
    t5u6 = ThankReceivedByUser(t5.id, u6.id, status = 1)

    t6u1 = ThankReceivedByUser(t6.id, u1.id, status = 1)
    t6u3 = ThankReceivedByUser(t6.id, u3.id, status = 2)
    t6u4 = ThankReceivedByUser(t6.id, u4.id, status = 1)

    db.session.add(t1u1)
    db.session.add(t1u2)
    db.session.add(t1u3)
    db.session.add(t1u4)
    db.session.add(t1u5)
    db.session.add(t1u6)
    db.session.add(t4u1)
    db.session.add(t4u3)
    db.session.add(t5u1)
    db.session.add(t5u2)
    db.session.add(t5u5)
    db.session.add(t5u6)
    db.session.add(t6u1)
    db.session.add(t6u3)
    db.session.add(t6u4)
    db.session.commit()

    u1u1 = Follow(u1.id, u1.id)
    u1u2 = Follow(u1.id, u2.id)
    u1u3 = Follow(u1.id, u3.id)
    u1u4 = Follow(u1.id, u4.id)
    u1u5 = Follow(u1.id, u5.id)
    u1u6 = Follow(u1.id, u6.id)
    u2u2 = Follow(u2.id, u2.id)
    u3u1 = Follow(u3.id, u1.id)
    u3u2 = Follow(u3.id, u2.id)
    u3u3 = Follow(u3.id, u3.id)
    u3u4 = Follow(u3.id, u4.id)
    u3u5 = Follow(u3.id, u5.id)
    u3u6 = Follow(u3.id, u6.id)
    u4u1 = Follow(u4.id, u1.id)
    u4u3 = Follow(u4.id, u3.id)
    u4u4 = Follow(u4.id, u4.id)
    u5u1 = Follow(u5.id, u1.id)
    u5u2 = Follow(u5.id, u2.id)
    u5u5 = Follow(u5.id, u5.id)
    u5u6 = Follow(u5.id, u6.id)
    u6u1 = Follow(u6.id, u1.id)
    u6u4 = Follow(u6.id, u4.id)
    u6u6 = Follow(u6.id, u6.id)

    db.session.add(u1u1)
    db.session.add(u1u2)
    db.session.add(u1u3)
    db.session.add(u1u4)
    db.session.add(u1u5)
    db.session.add(u1u6)
    db.session.add(u2u2)
    db.session.add(u3u1)
    db.session.add(u3u2)
    db.session.add(u3u3)
    db.session.add(u3u4)
    db.session.add(u3u5)
    db.session.add(u3u6)
    db.session.add(u4u1)
    db.session.add(u4u3)
    db.session.add(u4u4)
    db.session.add(u5u1)
    db.session.add(u5u2)
    db.session.add(u5u5)
    db.session.add(u5u6)
    db.session.add(u6u1)
    db.session.add(u6u4)
    db.session.add(u6u6)
    db.session.commit()

    u5.make_deleted()
    db.session.add(u5)

    t1.make_deleted()
    db.session.add(t1)

    t5u4.make_deleted()
    t5u6.make_deleted()
    db.session.add(t5u4)
    db.session.add(t5u6)

    u6u1.make_deleted()
    db.session.add(u6u1)
    db.session.commit()

    # # delete thank to user
    #     # number of thanks_received decreases

    # t2u1.make_deleted()
    # db.session.add(t2u1)
    # db.session.commit()


    # # make four emails

    # e5 = Email(email = 'fight@fight.com')
    # e6 = Email(email = 'go@go.com')
    # e7 = Email(email = 'further@further.com')
    # e8 = Email(email = 'win@win.com')

    # db.session.add(e5)
    # db.session.add(e6)
    # db.session.add(e7)
    # db.session.add(e8)
    # db.session.commit()

    # # thank to emails

    # t1e5 = ThankReceivedByEmail(t1.id, e5.id)
    # t1e6 = ThankReceivedByEmail(t1.id, e6.id)
    # t1e7 = ThankReceivedByEmail(t1.id, e7.id)
    # t1e8 = ThankReceivedByEmail(t1.id, e8.id)

    # t2e5 = ThankReceivedByEmail(t2.id, e5.id)
    # t2e6 = ThankReceivedByEmail(t2.id, e6.id)
    # t2e7 = ThankReceivedByEmail(t2.id, e7.id)

    # t3e5 = ThankReceivedByEmail(t3.id, e5.id)
    # t3e6 = ThankReceivedByEmail(t3.id, e6.id)

    # t4e5 = ThankReceivedByEmail(t4.id, e5.id)

    # db.session.add(t1e5)
    # db.session.add(t1e6)
    # db.session.add(t1e7)
    # db.session.add(t1e8)
    # db.session.add(t2e5)
    # db.session.add(t2e6)
    # db.session.add(t2e7)
    # db.session.add(t3e5)
    # db.session.add(t3e6)
    # db.session.add(t4e5)
    # db.session.commit()