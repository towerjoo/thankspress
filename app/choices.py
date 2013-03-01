#coding: utf-8

class Choices(object):
    @classmethod
    def to_string(cls, val):
        for s, v in vars(cls).iteritems():
            if v == val:
                return s

    @classmethod
    def from_string(cls, str):
        return getattr(cls, str.upper(), None)