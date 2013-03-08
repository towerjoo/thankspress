from config import IMAGE_TYPES
from random import random
from hashlib import md5

def is_email(email):
    return '@' in email and '.' in email and len(email) >= 5

def is_image_type(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in IMAGE_TYPES

def generate_key(val):
    return md5(str(random()) + str(val)).hexdigest()

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_integer_with_pound_key(s):
    if s[0] == '#' and is_integer(s[1:]):
        return True
    return False