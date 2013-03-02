from config import IMAGE_TYPES
from random import random
from hashlib import md5

class Functions(object):
    @staticmethod
    def is_email(email):
        return '@' in email and '.' in email and len(email) >= 5

    @staticmethod
    def generate_key(val):
        return md5(str(random()) + str(val)).hexdigest()

    @staticmethod
    def is_image_type(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in IMAGE_TYPES