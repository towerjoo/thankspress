from config import ALLOWED_EXTENSIONS
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
    def is_allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS