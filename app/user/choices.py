#coding: utf-8

from app.choices import Choices

class EmailStatusChoices(Choices):
    NOT_VERIFIED = 0
    VERIFIED = 1
    REPORTED = 2
    DELETED = 3

class FollowStatusChoices(Choices):
    FOLLOWING = 1
    DELETED = 2
    
class UserStatusChoices(Choices):
    NEW = 0
    ACTIVE = 1
    INACTIVE = 2
    REPORTED = 3
    DELETED = 4