#coding: utf-8

from app.choices import Choices

class ThankCommentStatusChoices(Choices):
    VISIBLE = 1
    REPORTED = 2
    DELETED = 3

class ThankStatusChoices(Choices):
    PUBLIC = 1
    PRIVATE = 2
    REPORTED = 3
    DELETED = 4

class ThankReceivedByEmailStatusChoices(Choices):
    USER_NOT_FOUND = 0
    MIGRATED = 1
    REPORTED = 2
    DELETED = 3

class ThankReceivedByPublicPageStatusChoices(Choices):
    VISIBLE = 1
    REPORTED = 2
    DELETED = 3

class ThankReceivedByUserStatusChoices(Choices):
    UNREAD = 0
    VISIBLE = 1
    HIDDEN = 2
    REPORTED = 3
    DELETED = 4