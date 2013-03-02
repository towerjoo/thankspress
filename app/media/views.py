from app import app
from config import UPLOAD_FOLDER
from flask import send_from_directory, abort
from app.media.models import Media

@app.route('/media/<id>')
def media(id):
    media = Media.get_media(id)
    if media != None:
        return send_from_directory(UPLOAD_FOLDER, media.path)
    abort(404)