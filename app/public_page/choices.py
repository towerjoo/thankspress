#coding: utf-8
from app.choices import Choices
class PublicPageStatusChoices(Choices):
    NOT_VERIFIED = 0
    VERIFIED = 1
    REPORTED = 2
    DELETED = 3

    CHOICES = (
        (NOT_VERIFIED, "NOT_VERIFIED"),
        (VERIFIED, "VERIFIED"),
        (REPORTED, "REPORTED"),
        (DELETED, "DELETED"),
    )

class MediaTypeChoices(Choices):
    IMAGE = 1
    VIDEO = 2
    YOUTUBE_VIDEO = 3

    CHOICES = (
        (IMAGE, "IMAGE"),
        (VIDEO, "VIDEO"),
        (YOUTUBE_VIDEO, "YOUTUBE_VIDEO"),
    )


