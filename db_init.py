#!venv/bin/python

from app import db
from app.media.models import Media
from app.media.choices import MediaTypeChoices

if Media.query.all() == []:
    profile_pic = Media(type = MediaTypeChoices.PROFILE_PICTURE, path = 'PROFILE_PICTURE/default.png')
    db.session.add(profile_pic)
    db.session.commit()