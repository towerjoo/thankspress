#coding: utf-8
<<<<<<< HEAD

class Choices(object):
    @classmethod
    def to_string(cls, val):
        for s, v in vars(cls).iteritems():
            if v == val:
                return s

    @classmethod
    def from_string(cls, str):
        return getattr(cls, str.upper(), None)
=======
class Choices:
    @classmethod
    def get_value(cls, key):
        # get the string display if need to show
        for k, v in cls.CHOICES:
            if k == key:
                return v
        return ""

class CommentStatusChoices(Choices):
    VISIBLE = 1
    REPORTED = 2
    DELETED = 3

    CHOICES = (
        (VISIBLE, "VISIBLE"),
        (REPORTED, "REPORTED"),
        (DELETED, "DELETED"),
    )

>>>>>>> d5d7f110b65dfe96b3b227dd9cb4ba74b3d0acfd
