from random import random
from hashlib import md5

class Functions(object):
    @staticmethod
    def is_email(email):
        return '@' in email and '.' in email and len(email) >= 5

    @staticmethod
    def generate_key(val):
        return md5(str(random()) + str(val)).hexdigest()